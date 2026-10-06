import type {
  ChatResult,
  CorpusHealth,
  ProgrammeSource,
  RetrievalMode,
  SearchResult,
} from "@domain/models";
import type { ProgrammeRepository } from "@domain/ports";
import { httpJson } from "./apiClient";

interface SourceDto {
  page_title: string;
  section: string;
  paragraph: number;
  url: string;
  score: number;
  excerpt: string;
  score_lexical?: number | null;
  score_semantic?: number | null;
  retrieval?: string | null;
  short_path?: string | null;
}

interface HealthDto {
  ok: boolean;
  error?: string;
  chunks?: number;
  pages?: number;
  scraped_at?: string;
  model?: string;
  embed_model?: string;
  has_api_key?: boolean;
  embeddings?: {
    ready: boolean;
    chunk_count: number;
    model: string | null;
    dim?: number;
    created_at?: string;
  };
}

interface ChatDto {
  answer: string;
  sources: SourceDto[];
  model: string;
  found: boolean;
  retrieval?: string | null;
}

interface SearchDto {
  results: SourceDto[];
  retrieval: string;
  count: number;
}

function mapSource(dto: SourceDto): ProgrammeSource {
  return {
    pageTitle: dto.page_title,
    section: dto.section,
    paragraph: dto.paragraph,
    url: dto.url,
    excerpt: dto.excerpt,
    score: dto.score,
    scoreLexical: dto.score_lexical ?? null,
    scoreSemantic: dto.score_semantic ?? null,
    retrieval: (dto.retrieval as RetrievalMode | null) ?? null,
    shortPath: dto.short_path ?? null,
  };
}

export class HttpProgrammeRepository implements ProgrammeRepository {
  async getHealth(): Promise<CorpusHealth> {
    const dto = await httpJson<HealthDto>("/api/health");
    const emb = dto.embeddings;
    return {
      ok: dto.ok,
      error: dto.error,
      chunks: dto.chunks,
      pages: dto.pages,
      scrapedAt: dto.scraped_at,
      model: dto.model,
      embedModel: dto.embed_model,
      hasApiKey: Boolean(dto.has_api_key),
      embeddings: {
        ready: Boolean(emb?.ready),
        chunkCount: emb?.chunk_count ?? 0,
        model: emb?.model ?? null,
        dim: emb?.dim,
        createdAt: emb?.created_at,
      },
    };
  }

  async ask(question: string): Promise<ChatResult> {
    const dto = await httpJson<ChatDto>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ question }),
    });
    return {
      answer: dto.answer,
      sources: (dto.sources ?? []).map(mapSource),
      model: dto.model,
      found: dto.found,
      retrieval: (dto.retrieval as RetrievalMode | null) ?? null,
    };
  }

  async search(question: string): Promise<SearchResult> {
    const dto = await httpJson<SearchDto>("/api/search", {
      method: "POST",
      body: JSON.stringify({ question }),
    });
    return {
      results: (dto.results ?? []).map(mapSource),
      retrieval: dto.retrieval as RetrievalMode,
      count: dto.count,
    };
  }
}
