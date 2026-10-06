import DOMPurify from "dompurify";
import { marked } from "marked";

// Liens des réponses (sources) : nouvel onglet, sans accès à window.opener
DOMPurify.addHook("afterSanitizeAttributes", (node) => {
  if (node.tagName === "A") {
    node.setAttribute("target", "_blank");
    node.setAttribute("rel", "noopener noreferrer");
  }
});

/** Markdown du LLM → HTML assaini (aucun script, aucun attribut dangereux). */
export function renderMarkdown(text: string): string {
  const html = marked.parse(text, { async: false, gfm: true, breaks: true });
  return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });
}
