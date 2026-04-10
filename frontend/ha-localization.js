/**
 * ha-localization.js — Language resolution utility for HA panels.
 *
 * Provides a mixin/utility for resolving the user's language from
 * the HA hass object and looking up translations with fallback.
 *
 * Usage:
 *   import { resolveLanguage, createTranslator } from "./ha-localization.js";
 *
 *   const lang = resolveLanguage(hass.language, UI_TEXT);
 *   const t = createTranslator(UI_TEXT, lang);
 *   console.log(t.placeholder); // Resolved string
 */

/**
 * Resolve the best matching language key from a translations object.
 *
 * Resolution order:
 * 1. Exact match (e.g. "pt-BR")
 * 2. Base language (e.g. "pt" from "pt-BR")
 * 3. Fallback to "en"
 *
 * @param {string|undefined} language - The HA language string (e.g. "de", "pt-BR").
 * @param {Object} translations - Object keyed by language codes.
 * @returns {string} The resolved language key.
 */
export function resolveLanguage(language, translations) {
  if (!language) return "en";
  if (translations[language]) return language;
  const base = language.split("-")[0];
  if (translations[base]) return base;
  return "en";
}

/**
 * Create a translation accessor that merges the resolved language
 * with the English fallback.
 *
 * @param {Object} translations - Object keyed by language codes.
 * @param {string} lang - Resolved language key.
 * @returns {Object} Merged translation object (resolved lang over "en").
 */
export function createTranslator(translations, lang) {
  return { ...(translations.en || {}), ...(translations[lang] || {}) };
}
