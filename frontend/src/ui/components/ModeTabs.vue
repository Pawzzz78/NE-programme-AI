<script setup lang="ts">
import type { QueryMode } from "@domain/models";

defineProps<{
  mode: QueryMode;
}>();

const emit = defineEmits<{
  change: [mode: QueryMode];
}>();
</script>

<template>
  <div class="tabs" role="tablist" aria-label="Mode">
    <button
      type="button"
      role="tab"
      class="tab"
      :class="{ active: mode === 'ask' }"
      :aria-selected="mode === 'ask'"
      @click="emit('change', 'ask')"
    >
      Demander
    </button>
    <button
      type="button"
      role="tab"
      class="tab"
      :class="{ active: mode === 'search' }"
      :aria-selected="mode === 'search'"
      @click="emit('change', 'search')"
    >
      Chercher
    </button>
  </div>
</template>

<style scoped>
.tabs {
  display: inline-flex;
  gap: 0.35rem;
  padding: 0.3rem;
  background: var(--white);
  border: 1px solid var(--line);
  border-radius: var(--radius-pill);
}

.tab {
  border: 0;
  background: transparent;
  color: var(--muted);
  padding: 0.55rem 1.15rem;
  border-radius: var(--radius-pill);
  font-weight: 700;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  cursor: pointer;
}

.tab.active {
  background: var(--navy);
  color: var(--white);
}
</style>
