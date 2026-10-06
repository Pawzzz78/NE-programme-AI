const form = document.getElementById("form");
const q = document.getElementById("q");
const send = document.getElementById("send");
const result = document.getElementById("result");
const answer = document.getElementById("answer");
const sources = document.getElementById("sources");
const status = document.getElementById("status");
const qLabel = document.getElementById("q-label");
const resultTitle = document.getElementById("result-title");
const sourcesTitle = document.getElementById("sources-title");
const retrievalMeta = document.getElementById("retrieval-meta");
const tabs = document.querySelectorAll(".tab");

let mode = "ask"; // ask | search

function setMode(next) {
  mode = next;
  tabs.forEach((tab) => {
    const active = tab.dataset.mode === mode;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", active ? "true" : "false");
  });
  if (mode === "ask") {
    qLabel.textContent = "Votre question";
    q.placeholder = "Ex. Que propose-t-il sur la sécurité ? Sur l’immigration ? Sur l’école ?";
    send.textContent = "Demander";
    resultTitle.textContent = "Réponse";
    sourcesTitle.textContent = "Passages utilisés";
  } else {
    qLabel.textContent = "Recherche dans le programme";
    q.placeholder = "Ex. police municipale, capitalisation retraite, carte scolaire…";
    send.textContent = "Chercher";
    resultTitle.textContent = "Résultats";
    sourcesTitle.textContent = "Passages trouvés";
  }
  result.hidden = true;
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => setMode(tab.dataset.mode));
});

function renderSources(list) {
  sources.innerHTML = "";
  for (const s of list || []) {
    const li = document.createElement("li");
    const scores = [];
    if (s.score_semantic != null) scores.push(`sémantique ${s.score_semantic}`);
    if (s.score_lexical != null) scores.push(`lexical ${s.score_lexical}`);
    const scoreLine = scores.length ? `<div class="meta">${scores.join(" · ")}</div>` : "";
    li.innerHTML = `
      <div class="meta">${escapeHtml(s.page_title)} — ${escapeHtml(s.section)} — paragraphe ${s.paragraph}</div>
      ${scoreLine}
      <div class="excerpt">${escapeHtml(s.excerpt)}</div>
      <a href="${s.url}" target="_blank" rel="noopener">Voir sur le site officiel</a>
    `;
    sources.appendChild(li);
  }
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function refreshHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    if (!data.ok) {
      status.textContent = data.error || "Corpus indisponible.";
      status.className = "status err";
      return;
    }
    const key = data.has_api_key ? "clé Mistral OK" : "clé Mistral manquante (.env)";
    const emb = data.embeddings?.ready
      ? `embeddings OK (${data.embeddings.chunk_count})`
      : "embeddings absents (python scripts/embed_programme.py)";
    status.textContent = `Corpus : ${data.chunks} passages · ${data.pages} pages · ${emb} · ${key}`;
    status.className = data.has_api_key ? "status ok" : "status err";
  } catch {
    status.textContent = "Serveur injoignable.";
    status.className = "status err";
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = q.value.trim();
  if (question.length < 3) return;

  send.disabled = true;
  const previousLabel = send.textContent;
  send.textContent = mode === "ask" ? "Recherche…" : "Indexation…";
  result.hidden = true;
  sources.innerHTML = "";
  answer.textContent = "";
  retrievalMeta.hidden = true;

  try {
    const endpoint = mode === "ask" ? "/api/chat" : "/api/search";
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    if (!res.ok) {
      answer.textContent = data.detail || "Erreur serveur.";
      result.hidden = false;
      return;
    }

    if (mode === "ask") {
      answer.textContent = data.answer;
      answer.hidden = false;
      renderSources(data.sources);
      if (data.retrieval) {
        retrievalMeta.textContent = `Récupération : ${data.retrieval}`;
        retrievalMeta.hidden = false;
      }
    } else {
      answer.hidden = true;
      if (!data.results?.length) {
        answer.hidden = false;
        answer.textContent = "Aucun passage trouvé dans le programme officiel.";
      }
      renderSources(data.results);
      retrievalMeta.textContent = `Récupération : ${data.retrieval} · ${data.count} résultat(s)`;
      retrievalMeta.hidden = false;
    }
    result.hidden = false;
  } catch {
    answer.hidden = false;
    answer.textContent = "Impossible de joindre l’API.";
    result.hidden = false;
  } finally {
    send.disabled = false;
    send.textContent = previousLabel;
  }
});

setMode("ask");
refreshHealth();
