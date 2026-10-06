<script setup lang="ts">
import { computed, ref } from "vue";
import type { ProgrammeSource } from "@domain/models";
import { buildShareCard } from "@domain/shareCard";
import { useShareCard } from "@app/useShareCard";
import { CARD_HEIGHT, CARD_WIDTH } from "@infra/canvas/renderShareCard";
import BaseButton from "./BaseButton.vue";

const props = defineProps<{
  question: string;
  answer: string;
  sources: ProgrammeSource[];
}>();

const card = computed(() => buildShareCard(props.question, props.answer, props.sources));

const {
  previewUrl,
  rendering,
  status,
  fallbackLink,
  replyTo,
  replyId,
  shareOnX,
  copyImageToClipboard,
  copyText,
} = useShareCard(card);

const dialog = ref<HTMLDialogElement | null>(null);

function open() {
  dialog.value?.showModal();
}

function close() {
  dialog.value?.close();
}

// Clic sur le fond (hors de la fenêtre) : fermeture
function onDialogClick(e: MouseEvent) {
  if (e.target === dialog.value) close();
}
</script>

<template>
  <div class="share">
    <BaseButton variant="navy" @click="open">
      <svg aria-hidden="true" viewBox="0 0 24 24" width="16" height="16">
        <path
          d="M12 3v12M12 3l-4.5 4.5M12 3l4.5 4.5M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      Partager
    </BaseButton>

    <dialog ref="dialog" class="dialog" aria-labelledby="share-title" @click="onDialogClick">
      <div class="body">
        <header>
          <h3 id="share-title">Partager la réponse</h3>
          <button type="button" class="close" aria-label="Fermer" @click="close">×</button>
        </header>

        <img
          v-if="previewUrl"
          class="preview"
          :src="previewUrl"
          :width="CARD_WIDTH"
          :height="CARD_HEIGHT"
          :alt="`Visuel à partager : ${card.headline}`"
        />
        <div v-else class="preview placeholder">
          {{ rendering ? "Création du visuel…" : "Visuel indisponible" }}
        </div>

        <label for="reply-to">Répondre à un post X <span>(facultatif)</span></label>
        <input
          id="reply-to"
          v-model="replyTo"
          type="url"
          inputmode="url"
          placeholder="Collez le lien du post"
        />

        <BaseButton class="primary" variant="navy" :disabled="!previewUrl" @click="shareOnX">
          {{ replyId ? "Répondre sur X" : "Partager sur X" }}
        </BaseButton>
        <div class="secondary">
          <BaseButton variant="outline" :disabled="!previewUrl" @click="copyImageToClipboard">
            Copier l’image
          </BaseButton>
          <BaseButton variant="outline" @click="copyText">Copier le texte</BaseButton>
        </div>

        <p class="status" aria-live="polite">
          <template v-if="status">{{ status }}</template>
          <a v-if="fallbackLink" :href="fallbackLink" target="_blank" rel="noopener">Ouvrir X →</a>
        </p>
      </div>
    </dialog>
  </div>
</template>

<style scoped>
.share {
  margin-top: 1rem;
}

.dialog {
  width: min(56rem, calc(100% - 2rem));
  max-height: calc(100% - 2rem);
  padding: 0;
  border: 0;
  border-radius: var(--radius);
  background: var(--card);
  color: var(--ink);
  box-shadow: 0 24px 60px rgba(20, 28, 79, 0.35);
}

.dialog[open] {
  animation: pop 0.18s ease-out;
}

.dialog::backdrop {
  background: rgba(20, 28, 79, 0.55);
}

.body {
  padding: 1.1rem 1.2rem 1.2rem;
  display: grid;
  gap: 0.6rem;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

h3 {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--navy);
}

.close {
  width: 2rem;
  height: 2rem;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--muted);
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
}

.close:hover {
  background: var(--bg);
  color: var(--navy);
}

.preview {
  width: 100%;
  height: auto;
  aspect-ratio: 16 / 9;
  border-radius: 8px;
  display: block;
}

.placeholder {
  display: grid;
  place-items: center;
  background: var(--navy);
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  font-weight: 600;
}

label {
  margin-top: 0.3rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--navy);
}

label span {
  color: var(--muted);
  font-weight: 500;
}

input {
  width: 100%;
  border: 1.5px solid var(--line);
  border-radius: 0.75rem;
  background: #fafbfe;
  color: var(--ink);
  padding: 0.65rem 0.9rem;
}

input:focus-visible {
  outline: 2px solid var(--gold);
  outline-offset: 2px;
}

.primary {
  margin-top: 0.4rem;
  width: 100%;
}

.secondary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
  gap: 0.6rem;
}

.secondary :deep(.btn) {
  padding-inline: 0.6rem;
}

.status {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--navy);
}

.status:empty {
  display: none;
}

.status a {
  margin-left: 0.4rem;
  color: var(--navy);
}

@keyframes pop {
  from {
    opacity: 0;
    transform: scale(0.97);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
</style>
