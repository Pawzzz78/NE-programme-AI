<script setup lang="ts">
import { computed } from "vue";
import type { ProgrammeSource, QueryMode, RetrievalMode } from "@domain/models";
import { renderMarkdown } from "../markdown";
import SourceCard from "./SourceCard.vue";

const props = defineProps<{
  mode: QueryMode;
  answer: string | null;
  sources: ProgrammeSource[];
  retrieval: RetrievalMode | null;
  error: string | null;
}>();

const answerHtml = computed(() => (props.answer ? renderMarkdown(props.answer) : ""));
</script>

<template>
  <section class="result" aria-live="polite">
    <h2>{{ mode === "ask" ? "Réponse" : "Résultats" }}</h2>

    <p v-if="error" class="error">{{ error }}</p>
    <div v-else-if="answer" class="answer" v-html="answerHtml" />

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
  line-height: 1.6;
  overflow-wrap: anywhere;
}

.answer :deep(> :first-child) {
  margin-top: 0;
}

.answer :deep(> :last-child) {
  margin-bottom: 0;
}

.answer :deep(p),
.answer :deep(ul),
.answer :deep(ol),
.answer :deep(blockquote) {
  margin: 0 0 0.75rem;
}

.answer :deep(ul),
.answer :deep(ol) {
  padding-left: 1.3rem;
}

.answer :deep(li + li) {
  margin-top: 0.45rem;
}

.answer :deep(h1),
.answer :deep(h2),
.answer :deep(h3),
.answer :deep(h4) {
  margin: 1rem 0 0.5rem;
  font-size: 1rem;
  color: var(--navy);
}

.answer :deep(strong) {
  color: var(--navy);
}

.answer :deep(blockquote) {
  padding: 0.1rem 0 0.1rem 0.8rem;
  border-left: 3px solid var(--gold);
  color: var(--muted);
  font-style: italic;
}

.answer :deep(a) {
  color: var(--navy);
  text-decoration: underline;
  text-underline-offset: 2px;
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
