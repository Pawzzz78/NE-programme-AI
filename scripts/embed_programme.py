"""Calcule les embeddings Mistral pour chaque passage du programme.

Prérequis : data/programme.json (scrape) + MISTRAL_API_KEY dans .env

Usage :
  python scripts/embed_programme.py
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from mistralai.client import Mistral

ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "data" / "programme.json"
OUT_NPZ = ROOT / "data" / "embeddings.npz"
OUT_META = ROOT / "data" / "embeddings_meta.json"
BATCH_SIZE = 32
MAX_ATTEMPTS = 6  # attentes : 2, 4, 8, 16, 32 s

load_dotenv(ROOT / ".env")


def chunk_text(chunk: dict) -> str:
    return (
        f"{chunk['page_title']}\n"
        f"{chunk['section']}\n"
        f"{chunk['text']}"
    )


def l2_normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return matrix / norms


def embed_batch(client: Mistral, model: str, batch: list[str]):
    """Appel embeddings avec nouvelles tentatives sur erreurs passagères (429, 5xx, réseau)."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return client.embeddings.create(model=model, inputs=batch)
        except Exception as exc:  # noqa: BLE001
            status = getattr(exc, "status_code", None)
            transient = status is None or status == 429 or status >= 500
            if not transient or attempt == MAX_ATTEMPTS:
                raise
            delay = 2**attempt
            print(f"  erreur {status or type(exc).__name__}, nouvelle tentative dans {delay} s "
                  f"({attempt}/{MAX_ATTEMPTS - 1})")
            time.sleep(delay)


def main() -> None:
    api_key = os.getenv("MISTRAL_API_KEY", "").strip()
    if not api_key or api_key.startswith("your_"):
        raise SystemExit("MISTRAL_API_KEY manquante dans .env")

    model = os.getenv("MISTRAL_EMBED_MODEL", "mistral-embed")
    if not CORPUS_PATH.exists():
        raise SystemExit(
            f"Corpus introuvable : {CORPUS_PATH}. "
            "Lancez d'abord python scripts/scrape_programme.py"
        )

    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    chunks = corpus["chunks"]
    texts = [chunk_text(c) for c in chunks]
    ids = [c["id"] for c in chunks]
    print(f"{len(texts)} passages -> embeddings ({model}), lots de {BATCH_SIZE}...")

    client = Mistral(api_key=api_key)
    vectors: list[list[float]] = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        resp = embed_batch(client, model, batch)
        # SDK may return data sorted by index
        ordered = sorted(resp.data, key=lambda d: d.index)
        vectors.extend([d.embedding for d in ordered])
        done = min(i + BATCH_SIZE, len(texts))
        print(f"  [{done}/{len(texts)}]")
        time.sleep(0.15)

    matrix = l2_normalize(np.asarray(vectors, dtype=np.float32))
    np.savez_compressed(OUT_NPZ, ids=np.asarray(ids), vectors=matrix)

    meta = {
        "model": model,
        "chunk_count": len(ids),
        "dim": int(matrix.shape[1]),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "corpus_scraped_at": corpus.get("scraped_at"),
        "path": str(OUT_NPZ.name),
    }
    OUT_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Écrit {OUT_NPZ} ({matrix.shape[0]} × {matrix.shape[1]})")
    print(f"Meta  {OUT_META}")


if __name__ == "__main__":
    main()
