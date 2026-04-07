/**
 * ha-shared-utils.js — Generic utilities for HA custom dashboard panels.
 *
 * Copy this into your integration's frontend/ directory or import via
 * ES module from the shared static path.
 */

/**
 * Format a number as currency.
 * @param {number} value
 * @param {string} currency - ISO 4217 code (default "EUR")
 * @param {string} locale - BCP 47 locale (default "de-DE")
 * @returns {string}
 */
export function formatCurrency(value, currency = "EUR", locale = "de-DE") {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
  }).format(value || 0);
}

/**
 * Format a number as percentage.
 * @param {number} value - Value between 0 and 100.
 * @returns {string}
 */
export function formatPercent(value) {
  return `${Math.round(value || 0)}%`;
}

/**
 * Escape a string for safe HTML insertion (XSS protection).
 * @param {string} str
 * @returns {string}
 */
export function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Format a date string to localized display.
 * @param {string} isoDate - ISO 8601 date string.
 * @param {string} locale - BCP 47 locale (default "de-DE").
 * @param {Object} options - Intl.DateTimeFormat options.
 * @returns {string}
 */
export function formatDate(isoDate, locale = "de-DE", options = {}) {
  if (!isoDate) return "";
  const defaults = { year: "numeric", month: "2-digit", day: "2-digit" };
  return new Intl.DateTimeFormat(locale, { ...defaults, ...options }).format(
    new Date(isoDate)
  );
}

/**
 * Debounce a function call.
 * @param {Function} fn
 * @param {number} ms - Delay in milliseconds.
 * @returns {Function}
 */
export function debounce(fn, ms = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}

/**
 * Generic shared CSS custom properties for HA dark/light themes.
 * Use as a base and extend with your own properties.
 */
export const BASE_CSS = `
  :host {
    --bg: var(--primary-background-color, #0a0a0f);
    --bg2: var(--secondary-background-color, #111118);
    --card: var(--card-background-color, #16161e);
    --tx: var(--primary-text-color, #e0e0e0);
    --tx2: var(--secondary-text-color, #888);
    --brd: var(--divider-color, rgba(255,255,255,0.06));
    --ac: var(--accent-color, #4fc3f7);
    --pos: #22c55e;
    --neg: #ef4444;
    --radius: 12px;
    --gap: 16px;
    display: block;
    font-family: var(--paper-font-body1_-_font-family, "Roboto", sans-serif);
    color: var(--tx);
    background: var(--bg);
    min-height: 100vh;
  }

  .card {
    background: var(--card);
    border: 1px solid var(--brd);
    border-radius: var(--radius);
    padding: var(--gap);
  }

  .pos { color: var(--pos); }
  .neg { color: var(--neg); }
  .muted { color: var(--tx2); }

  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 200px;
    color: var(--tx2);
  }

  .error {
    padding: var(--gap);
    text-align: center;
    color: var(--neg);
  }
`;
