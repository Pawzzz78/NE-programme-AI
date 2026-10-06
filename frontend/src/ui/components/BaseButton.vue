<script setup lang="ts">
defineProps<{
  variant?: "gold" | "navy" | "ghost" | "outline";
  type?: "button" | "submit";
  disabled?: boolean;
}>();
</script>

<template>
  <button
    class="btn"
    :class="variant ?? 'gold'"
    :type="type ?? 'button'"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  border: 0;
  border-radius: var(--radius-pill);
  padding: 0.75rem 1.35rem;
  font-weight: 700;
  font-size: 0.82rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.15s ease;
}

.btn:disabled {
  opacity: 0.55;
  cursor: wait;
}

.gold {
  background: var(--gold);
  color: var(--gold-ink);
}

.gold:hover:not(:disabled) {
  background: var(--gold-hover);
}

.navy {
  background: var(--navy);
  color: var(--white);
}

.navy:hover:not(:disabled) {
  background: var(--navy-soft);
}

.ghost {
  background: transparent;
  color: var(--white);
  border: 1.5px solid rgba(255, 255, 255, 0.55);
}

.ghost:hover:not(:disabled) {
  border-color: var(--white);
  background: rgba(255, 255, 255, 0.06);
}

.outline {
  background: transparent;
  color: var(--navy);
  border: 1.5px solid var(--line);
}

.outline:hover:not(:disabled) {
  border-color: var(--navy);
}
</style>
