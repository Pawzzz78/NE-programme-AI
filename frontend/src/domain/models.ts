/** Entités du domaine — indépendantes du framework UI / HTTP. */

export type RetrievalMode = "hybrid" | "semantic" | "lexical";

export type QueryMode = "ask" | "search";

export interface ProgrammeSource {
  pageTitle: string;
  section: string;
  paragraph: number;
  url: string;
  excerpt: string;
  score: number;
  scoreLexical: number | null;
  scoreSemantic: number | null;
  retrieval: RetrievalMode | null;
  /** Lien court du site vers la page source (ex. /s/a3f9c2). */
  shortPath: string | null;
}

export interface EmbeddingsHealth {
  ready: boolean;
  chunkCount: number;
  model: string | null;
  dim?: number;
  createdAt?: string;
}

export interface CorpusHealth {
  ok: boolean;
  error?: string;
  chunks?: number;
  pages?: number;
  scrapedAt?: string;
  model?: string;
  embedModel?: string;
  hasApiKey: boolean;
  embeddings: EmbeddingsHealth;
}

export interface ChatResult {
  answer: string;
  sources: ProgrammeSource[];
  model: string;
  found: boolean;
  retrieval: RetrievalMode | null;
}

/** Carte partageable d'une réponse (visuel + texte du post). */
export interface ShareCard {
  question: string;
  headline: string;
  sourceTitle: string;
  sourceUrl: string;
  sourceShortPath: string | null;
}

export interface SearchResult {
  results: ProgrammeSource[];
  retrieval: RetrievalMode;
  count: number;
}
