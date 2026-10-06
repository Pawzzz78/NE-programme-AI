<script setup lang="ts">
import type { ProgrammeSource, QueryMode, RetrievalMode } from "@domain/models";
import SourceCard from "./SourceCard.vue";

defineProps<{
  mode: QueryMode;
  answer: string | null;
  sources: ProgrammeSource[];
  retrieval: RetrievalMode | null;
  error: string | null;
}>();
</script>

<template>
  <section class="result" aria-live="polite">
    <h2>{{ mode === "ask" ? "Réponse" : "Résultats" }}</h2>

    <p v-if="error" class="error">{{ error }}</p>
    <div v-else-if="answer" class="answer">{{ answer }}</div>

    <p v-if="retrieval && !error" class="retrieval">
      Récupération : {{ retrieval }}
      <template v-if="mode === 'search'"> · {{ sources.length }} résultat(s)</template>
    </p>

    <template v-if="sources.length">
      <h3>{{ mode === "ask" ? "Passages utilisés" : "Passages trouvés" }}</h3>
      <ul class="sources">
        <SourceCard
          v-for="(source, i) in sources"
          :key="`${source.url}-${source.paragraph}-${i}`"
          :source="source"
        />
      </ul>
    </template>
  </section>
</template>

<style scoped>
.result {
  margin-top: 1.35rem;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 1.25rem 1.25rem 1.4rem;
  box-shadow: var(--shadow);
  animation: rise 0.35s ease both;
}

h2 {
  margin: 0 0 0.7rem;
  font-size: 0.95rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--navy);
}

h3 {
  margin: 1.3rem 0 0.55rem;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  font-weight: 700;
}

.answer {
  white-space: pre-wrap;
  line-height: 1.6;
}

.error {
  margin: 0;
  color: var(--warn);
  font-weight: 600;
}

.retrieval {
  margin: 0.9rem 0 0;
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 500;
}

.sources {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.9rem;
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
</style>
