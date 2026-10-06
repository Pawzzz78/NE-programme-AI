import { HttpProgrammeRepository } from "@infra/http/programmeApi";
import type { ProgrammeRepository } from "@domain/ports";

/** Composition root — un seul point d'injection des adaptateurs. */
export const programmeRepository: ProgrammeRepository =
  new HttpProgrammeRepository();
