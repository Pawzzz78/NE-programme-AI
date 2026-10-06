import type { ChatResult, CorpusHealth, SearchResult } from "./models";

/** Port sortant : accès au programme (implémenté par l'infra HTTP). */
export interface ProgrammeRepository {
  getHealth(): Promise<CorpusHealth>;
  ask(question: string): Promise<ChatResult>;
  search(question: string): Promise<SearchResult>;
}
