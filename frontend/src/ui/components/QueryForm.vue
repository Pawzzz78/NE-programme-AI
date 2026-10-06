<script setup lang="ts">
import type { QueryMode } from "@domain/models";
import BaseButton from "./BaseButton.vue";

defineProps<{
  mode: QueryMode;
  modelValue: string;
  loading: boolean;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
  submit: [];
}>();

function onSubmit(e: Event) {
  e.preventDefault();
  emit("submit");
}
</script>

<template>
  <form class="form" @submit="onSubmit">
    <label for="q">
      {{ mode === "ask" ? "Votre question" : "Recherche dans le programme" }}
    </label>
    <div class="row">
      <textarea
        id="q"
        rows="3"
        maxlength="1000"
        required
        :value="modelValue"
        :placeholder="
          mode === 'ask'
            ? 'Ex. Que propose-t-il sur la sécurité ? Sur l’immigration ? Sur l’école ?'
            : 'Ex. police municipale, capitalisation retraite, carte scolaire…'
        "
        @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
      />
      <BaseButton
        type="submit"
        variant="gold"
        :disabled="loading || modelValue.trim().length < 3"
      >
        {{
          loading
            ? mode === "ask"
              ? "Recherche…"
              : "Indexation…"
            : mode === "ask"
              ? "Demander"
              : "Chercher"
        }}
      </BaseButton>
    </div>
  </form>
</template>

<style scoped>
.form {
  margin-top: 1.1rem;
  display: grid;
  gap: 0.65rem;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 1.2rem;
  box-shadow: var(--shadow);
}

label {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--navy);
}

.row {
  display: grid;
  gap: 0.85rem;
}

textarea {
  width: 100%;
  resize: vertical;
  border: 1.5px solid var(--line);
  border-radius: 1.25rem;
  background: #fafbfe;
  color: var(--ink);
  padding: 0.95rem 1.1rem;
  line-height: 1.45;
  min-height: 6.5rem;
}

textarea::placeholder {
  color: #8b93b0;
}

.row :deep(.btn) {
  justify-self: start;
}
</style>
