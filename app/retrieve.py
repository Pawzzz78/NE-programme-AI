"""Recherche hybride : lexical + embeddings Mistral (si disponibles)."""

from __future__ import annotations

import json
import os
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "programme.json"
EMBED_NPZ = ROOT / "data" / "embeddings.npz"
EMBED_META = ROOT / "data" / "embeddings_meta.json"

load_dotenv(ROOT / ".env", override=True)

STOPWORDS = {
    "le", "la", "les", "un", "une", "des", "de", "du", "au", "aux", "et", "ou",
    "en", "dans", "sur", "pour", "par", "avec", "sans", "que", "qui", "quoi",
    "dont", "est", "sont", "a", "à", "ce", "ces", "son", "sa", "ses", "leur",
    "leurs", "il", "elle", "ils", "elles", "nous", "vous", "je", "tu", "y",
    "ne", "pas", "plus", "moins", "très", "tres", "d", "l", "n", "s", "c",
    "se", "si", "comme", "être", "etre", "avoir", "fait", "faire", "peut",
    "quel", "quelle", "quels", "quelles", "comment", "pourquoi", "quand",
    "david", "lisnard",
}

RRF_K = 60


def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def tokenize(text: str) -> list[str]:
    text = strip_accents(text.lower())
    tokens = re.findall(r"[a-z0-9]{2,}", text)
    return [t for t in tokens if t not in STOPWORDS]


@lru_cache(maxsize=1)
def load_corpus() -> dict:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Corpus introuvable : {DATA_PATH}. Lancez d'abord "
            "`python scripts/scrape_programme.py`."
        )
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


_embeddings_cache: dict | None = None
_embeddings_mtime: float | None = None


def load_embeddings() -> dict | None:
    global _embeddings_cache, _embeddings_mtime
    if not EMBED_NPZ.exists():
        _embeddings_cache = None
        _embeddings_mtime = None
        return None
    mtime = EMBED_NPZ.stat().st_mtime
    if _embeddings_cache is not None and _embeddings_mtime == mtime:
        return _embeddings_cache
    data = np.load(EMBED_NPZ, allow_pickle=True)
    ids = [str(x) for x in data["ids"].tolist()]
    vectors = data["vectors"].astype(np.float32)
    meta = {}
    if EMBED_META.exists():
        meta = json.loads(EMBED_META.read_text(encoding="utf-8"))
    _embeddings_cache = {
        "ids": ids,
        "vectors": vectors,
        "meta": meta,
        "id_to_row": {i: n for n, i in enumerate(ids)},
    }
    _embeddings_mtime = mtime
    return _embeddings_cache


def embeddings_status() -> dict:
    emb = load_embeddings()
    if not emb:
        return {"ready": False, "chunk_count": 0, "model": None}
    return {
        "ready": True,
        "chunk_count": len(emb["ids"]),
        "model": emb["meta"].get("model", "mistral-embed"),
        "dim": emb["meta"].get("dim"),
        "created_at": emb["meta"].get("created_at"),
    }


def _lexical_ranked(query: str) -> list[tuple[str, float]]:
    corpus = load_corpus()
    q_tokens = tokenize(query)
    if not q_tokens:
        return []

    scored: list[tuple[str, float]] = []
    for chunk in corpus["chunks"]:
        hay = f"{chunk['page_title']} {chunk['section']} {chunk['text']}"
        tokens = tokenize(hay)
        if not tokens:
            continue
        tf: dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        score = 0.0
        for qt in q_tokens:
            if qt in tf:
                score += 1.0 + min(tf[qt], 5) * 0.25
            elif any(t.startswith(qt) or qt.startswith(t) for t in tf if len(qt) >= 4):
                score += 0.6
        title_tokens = set(tokenize(f"{chunk['page_title']} {chunk['section']}"))
        score += 1.2 * len(set(q_tokens) & title_tokens)
        if score > 0:
            scored.append((chunk["id"], score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def _embed_query(query: str) -> np.ndarray | None:
    emb = load_embeddings()
    if not emb:
        return None
    api_key = os.getenv("MISTRAL_API_KEY", "").strip()
    if not api_key or api_key.startswith("your_"):
        return None

    from mistralai.client import Mistral

    model = os.getenv("MISTRAL_EMBED_MODEL", emb["meta"].get("model", "mistral-embed"))
    client = Mistral(api_key=api_key)
    resp = client.embeddings.create(model=model, inputs=[query])
    vec = np.asarray(resp.data[0].embedding, dtype=np.float32)
    norm = float(np.linalg.norm(vec))
    if norm < 1e-12:
        return None
    return vec / norm


def _semantic_ranked(query: str) -> list[tuple[str, float]]:
    emb = load_embeddings()
    if not emb:
        return []
    qvec = _embed_query(query)
    if qvec is None:
        return []
    sims = emb["vectors"] @ qvec  # vectors are L2-normalized
    order = np.argsort(-sims)
    return [(emb["ids"][i], float(sims[i])) for i in order]


def _rrf(
    lexical: list[tuple[str, float]],
    semantic: list[tuple[str, float]],
    top_k: int,
) -> list[tuple[str, float, dict]]:
    """Reciprocal Rank Fusion — combine les classements lexical + sémantique."""
    scores: dict[str, float] = {}
    details: dict[str, dict] = {}

    for rank, (cid, raw) in enumerate(lexical):
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (RRF_K + rank + 1)
        details.setdefault(cid, {})["lexical"] = raw
        details[cid]["lex_rank"] = rank + 1

    for rank, (cid, raw) in enumerate(semantic):
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (RRF_K + rank + 1)
        details.setdefault(cid, {})["semantic"] = raw
        details[cid]["sem_rank"] = rank + 1

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(cid, score, details.get(cid, {})) for cid, score in ranked[:top_k]]


def _chunks_by_id() -> dict[str, dict]:
    corpus = load_corpus()
    return {c["id"]: c for c in corpus["chunks"]}


def search(
    query: str,
    top_k: int = 8,
    min_score: float = 0.0,
    min_semantic: float = 0.35,
) -> list[dict]:
    """Recherche hybride. Retombe sur lexical seul si pas d'embeddings / clé."""
    query = query.strip()
    if len(query) < 2:
        return []

    lexical = _lexical_ranked(query)
    semantic = _semantic_ranked(query)
    mode = "hybrid" if semantic and lexical else ("semantic" if semantic else "lexical")

    by_id = _chunks_by_id()
    results: list[dict] = []

    if mode == "hybrid":
        fused = _rrf(lexical, semantic, top_k=max(top_k * 3, 24))
        for cid, rrf_score, detail in fused:
            chunk = by_id.get(cid)
            if not chunk:
                continue
            sem = detail.get("semantic")
            # Filtre anti-bruit : si sémantique très faible et lexical absent, skip
            if sem is not None and sem < min_semantic and "lexical" not in detail:
                continue
            item = dict(chunk)
            item["score"] = round(rrf_score, 5)
            item["score_lexical"] = round(detail["lexical"], 3) if "lexical" in detail else None
            item["score_semantic"] = round(sem, 4) if sem is not None else None
            item["retrieval"] = mode
            results.append(item)
            if len(results) >= top_k:
                break
    elif mode == "semantic":
        for cid, sim in semantic[: top_k * 2]:
            if sim < min_semantic:
                continue
            chunk = by_id.get(cid)
            if not chunk:
                continue
            item = dict(chunk)
            item["score"] = round(sim, 4)
            item["score_lexical"] = None
            item["score_semantic"] = round(sim, 4)
            item["retrieval"] = mode
            results.append(item)
            if len(results) >= top_k:
                break
    else:
        # lexical seul (comportement MVP)
        for cid, score in lexical:
            if score < max(min_score, 1.5):
                continue
            chunk = by_id.get(cid)
            if not chunk:
                continue
            item = dict(chunk)
            item["score"] = round(score, 3)
            item["score_lexical"] = round(score, 3)
            item["score_semantic"] = None
            item["retrieval"] = mode
            results.append(item)
            if len(results) >= top_k:
                break

    return results
