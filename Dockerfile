# Image unique : front Vue compilé + API FastAPI.
# Le build re-scrape le site officiel et recalcule les embeddings Mistral.

# --- 1. Front (Vue) -----------------------------------------------------------
FROM node:22-alpine AS front
WORKDIR /front
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# --- 2. Corpus : scrape + embeddings ------------------------------------------
FROM python:3.13-slim AS corpus
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY scripts/ scripts/
# Corpus versionné : repli si le scrape échoue
COPY data/programme.json data/
# Les sitemaps invalident le cache Docker dès que le site change :
# le scrape (et donc l'embedding) n'est rejoué que si le contenu a bougé.
ADD https://www.unenouvelleenergie.fr/pages-sitemap.xml /tmp/sitemaps/pages.xml
ADD https://www.unenouvelleenergie.fr/questions-sitemap.xml /tmp/sitemaps/questions.xml
RUN python scripts/scrape_programme.py \
    || echo "AVERTISSEMENT : scrape échoué, corpus versionné conservé"
# Variables Railway passées au build. Sans clé, le build échoue
# (plutôt que de déployer une app sans recherche sémantique).
ARG MISTRAL_API_KEY
ARG MISTRAL_EMBED_MODEL=mistral-embed
RUN python scripts/embed_programme.py

# --- 3. Runtime ---------------------------------------------------------------
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
COPY --from=corpus /app/data/ data/
COPY --from=front /front/dist/ frontend/dist/
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
