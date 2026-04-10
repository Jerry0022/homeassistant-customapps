/**
 * ha-chat-panel.js — Base chat panel Web Component for HA integrations.
 *
 * Provides a reusable chat interface with:
 * - Message list (user, assistant, system, error types)
 * - Input bar with send button
 * - Loading state with animated dots
 * - Auto-scroll to latest message
 * - HTML escaping for XSS protection
 *
 * Usage:
 *   import { HaChatPanel, CHAT_CSS } from "./ha-chat-panel.js";
 *
 *   class MyPanel extends HaChatPanel {
 *     static get tag() { return "my-panel"; }
 *     get domain() { return "my_domain"; }
 *
 *     async onSubmit(text) {
 *       const response = await this._hass.callApi("POST", `${this.domain}/process`, { text });
 *       return { text: response.summary, actions: response.results };
 *     }
 *
 *     renderHeaderContent() {
 *       return `<div class="brand-title">My App</div>`;
 *     }
 *   }
 *
 *   MyPanel.register();
 */

// ── HTML escape ──────────────────────────────────────────────────────────────

export function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// ── SVG icons ────────────────────────────────────────────────────────────────

export const SEND_SVG = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>`;

export const SPINNER_SVG = `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true" class="spin-icon"><circle cx="12" cy="12" r="9" stroke-opacity="0.25"/><path d="M12 3a9 9 0 0 1 9 9" /></svg>`;

export const ERROR_SVG = `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>`;

// ── Chat CSS ─────────────────────────────────────────────────────────────────

export const CHAT_CSS = `
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :host {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
    padding: 16px;
    background: var(--primary-background-color, #111318);
    color: var(--primary-text-color, #e1e2e8);
  }

  .panel-wrap {
    width: 100%;
    max-width: 800px;
    display: flex;
    flex-direction: column;
    gap: 0;
    height: calc(100vh - 32px);
  }

  .header-card {
    background: var(--card-background-color, #1c1e26);
    border-radius: 20px 20px 0 0;
    padding: 18px 20px 14px;
    border-bottom: 1px solid var(--divider-color, rgba(255,255,255,0.08));
  }

  .warning-container { padding: 0 20px; }

  .chat-card {
    background: var(--card-background-color, #1c1e26);
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .chat-body {
    flex: 1;
    overflow-y: auto;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    scroll-behavior: smooth;
  }
  .chat-body::-webkit-scrollbar { width: 6px; }
  .chat-body::-webkit-scrollbar-thumb {
    background: var(--divider-color, rgba(255,255,255,0.1));
    border-radius: 3px;
  }
  .chat-empty {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--secondary-text-color, #9e9e9e);
    font-size: 14px;
    text-align: center;
    padding: 32px;
    opacity: 0.7;
  }

  .msg { animation: msg-in 0.2s ease-out; margin-bottom: 4px; }
  @keyframes msg-in {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .msg-right { display: flex; flex-direction: column; align-items: flex-end; }
  .msg-left  { display: flex; flex-direction: column; align-items: flex-start; }

  .bubble {
    max-width: min(80%, 560px);
    padding: 10px 14px;
    border-radius: 16px;
    font-size: 14px;
    line-height: 1.5;
    word-break: break-word;
  }
  .bubble-user {
    background: var(--primary-color, #6750a4);
    color: white;
    border-bottom-right-radius: 4px;
  }
  .bubble-assistant {
    background: var(--secondary-background-color, #23252f);
    color: var(--primary-text-color, #e1e2e8);
    border-bottom-left-radius: 4px;
    display: flex;
    gap: 8px;
    align-items: flex-start;
  }
  .bubble-error {
    background: color-mix(in srgb, var(--error-color, #f44336) 14%, var(--secondary-background-color, #23252f));
    color: var(--error-color, #f44336);
    border: 1px solid color-mix(in srgb, var(--error-color, #f44336) 30%, transparent);
    border-bottom-left-radius: 4px;
    display: flex;
    gap: 8px;
    align-items: flex-start;
  }
  .error-icon { flex-shrink: 0; margin-top: 2px; display: flex; }
  .bubble-system {
    background: transparent;
    color: var(--secondary-text-color, #9e9e9e);
    font-size: 12px;
    padding: 4px 0;
    font-style: italic;
  }
  .bubble-text { display: block; }

  .msg-time {
    font-size: 10px;
    color: var(--secondary-text-color, #9e9e9e);
    opacity: 0.6;
    margin-top: 3px;
    padding: 0 2px;
  }
  .msg-time--right { text-align: right; }

  .msg-loading .bubble-assistant { min-width: 64px; }
  .loading-dots {
    display: flex;
    gap: 5px;
    align-items: center;
    padding: 4px 2px;
  }
  .loading-dots span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--secondary-text-color, #9e9e9e);
    animation: dot-bounce 1.2s ease-in-out infinite;
  }
  .loading-dots span:nth-child(1) { animation-delay: 0s; }
  .loading-dots span:nth-child(2) { animation-delay: 0.2s; }
  .loading-dots span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes dot-bounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
    40% { transform: translateY(-5px); opacity: 1; }
  }

  .input-card {
    background: var(--card-background-color, #1c1e26);
    border-radius: 0 0 20px 20px;
    padding: 14px 20px;
    border-top: 1px solid var(--divider-color, rgba(255,255,255,0.08));
  }
  .input-row {
    display: flex;
    gap: 10px;
    align-items: center;
  }
  .prompt-input {
    flex: 1;
    padding: 12px 16px;
    border-radius: 24px;
    border: 1.5px solid var(--divider-color, rgba(255,255,255,0.12));
    background: var(--secondary-background-color, #23252f);
    color: var(--primary-text-color, #e1e2e8);
    font-size: 15px;
    transition: border-color 0.2s;
    outline: none;
  }
  .prompt-input:focus {
    border-color: var(--primary-color, #6750a4);
  }
  .prompt-input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .send-btn {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    border: none;
    background: var(--primary-color, #6750a4);
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: opacity 0.2s, transform 0.1s;
  }
  .send-btn:hover:not(:disabled) { opacity: 0.9; transform: scale(1.05); }
  .send-btn:active:not(:disabled) { transform: scale(0.97); }
  .send-btn:disabled { opacity: 0.45; cursor: not-allowed; transform: none; }
  .send-btn--loading { opacity: 0.8; }
  .spin-icon { animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  @media (max-width: 480px) {
    :host { padding: 8px; }
    .panel-wrap { height: calc(100vh - 16px); }
    .bubble { max-width: 92%; }
    .header-card, .input-card { padding: 12px 14px; }
    .chat-body { padding: 12px 14px; }
  }
`;

// ── Base Chat Panel Class ────────────────────────────────────────────────────

export class HaChatPanel extends HTMLElement {
  /** Override in subclass. */
  static get tag() {
    throw new Error("Subclass must define static get tag()");
  }

  /** Override: integration domain for API calls. */
  get domain() {
    throw new Error("Subclass must define get domain()");
  }

  /**
   * Override: handle user submission. Return an object with:
   * - text: string (assistant response text)
   * - actions: array (optional action results)
   * @param {string} text
   * @returns {Promise<{text: string, actions?: Array}>}
   */
  async onSubmit(_text) {
    throw new Error("Subclass must implement onSubmit()");
  }

  /** Override: return HTML for the header card content. */
  renderHeaderContent() {
    return "";
  }

  /** Override: return additional CSS. */
  renderExtraStyles() {
    return "";
  }

  /** Override: render action cards for assistant messages. */
  renderActions(_actions) {
    return "";
  }

  /** Override: return the empty-state placeholder text. */
  getEmptyText() {
    return "No messages yet.";
  }

  /** Override: return the input placeholder text. */
  getPlaceholder() {
    return "Type a message...";
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._text = "";
    this._loading = false;
    this._messages = [];
    this._rendered = false;
    this._msgIdCounter = 0;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._rendered) {
      this._render();
      this._rendered = true;
    }
    this.onHassUpdate(hass);
  }

  get hass() {
    return this._hass;
  }

  /** Called on every hass update. Override as needed. */
  onHassUpdate(_hass) {}

  /** Register this element. */
  static register() {
    if (!customElements.get(this.tag)) {
      customElements.define(this.tag, this);
    }
  }

  // ── Message management ───────────────────────────────────────────────────

  _nextId() {
    return ++this._msgIdCounter;
  }

  addMessage(msg) {
    const message = {
      id: this._nextId(),
      type: msg.type,
      text: msg.text,
      timestamp: new Date(),
      actions: msg.actions || [],
    };
    this._messages.push(message);

    const empty = this.shadowRoot?.querySelector(".chat-empty");
    if (empty) empty.remove();

    const chatBody = this.shadowRoot?.querySelector(".chat-body");
    if (chatBody) {
      chatBody.appendChild(this._createMessageEl(message));
      this._scrollToBottom();
    }
  }

  _showLoadingBubble(id) {
    const chatBody = this.shadowRoot?.querySelector(".chat-body");
    if (!chatBody) return;
    const el = document.createElement("div");
    el.className = "msg msg-assistant msg-loading";
    el.dataset.loadingId = id;
    el.innerHTML = `
      <div class="bubble bubble-assistant">
        <span class="loading-dots"><span></span><span></span><span></span></span>
      </div>`;
    chatBody.appendChild(el);
    this._scrollToBottom();
  }

  _removeLoadingBubble(id) {
    const el = this.shadowRoot?.querySelector(`[data-loading-id="${id}"]`);
    if (el) el.remove();
  }

  _scrollToBottom() {
    const chatBody = this.shadowRoot?.querySelector(".chat-body");
    if (chatBody) {
      requestAnimationFrame(() => {
        chatBody.scrollTop = chatBody.scrollHeight;
      });
    }
  }

  // ── Submit flow ──────────────────────────────────────────────────────────

  async _submit() {
    const text = this._text.trim();
    if (!text || this._loading) return;

    this.addMessage({ type: "user", text });
    this._text = "";
    this._loading = true;
    this._updateInput();

    const loadingId = this._nextId();
    this._showLoadingBubble(loadingId);

    try {
      const result = await this.onSubmit(text);
      this._removeLoadingBubble(loadingId);
      this.addMessage({
        type: "assistant",
        text: result.text || "",
        actions: result.actions || [],
      });
    } catch (err) {
      this._removeLoadingBubble(loadingId);
      this.addMessage({ type: "error", text: `Error: ${err.message}` });
    } finally {
      this._loading = false;
      this._updateInput();
      const input = this.shadowRoot?.querySelector("#prompt");
      if (input) setTimeout(() => input.focus(), 0);
    }
  }

  // ── DOM helpers ──────────────────────────────────────────────────────────

  _updateInput() {
    const input = this.shadowRoot?.querySelector("#prompt");
    const sendBtn = this.shadowRoot?.querySelector("#send");

    if (input) {
      input.disabled = this._loading;
      input.value = this._text;
    }
    if (sendBtn) {
      sendBtn.disabled = this._loading;
      sendBtn.className = `send-btn${this._loading ? " send-btn--loading" : ""}`;
      sendBtn.innerHTML = this._loading ? SPINNER_SVG : SEND_SVG;
    }
  }

  _createMessageEl(msg) {
    const wrap = document.createElement("div");
    const isUser = msg.type === "user";
    const isError = msg.type === "error";
    const isSystem = msg.type === "system";
    const isAssistant = msg.type === "assistant";

    wrap.className = `msg msg-${msg.type}`;
    wrap.dataset.msgId = msg.id;

    const time = msg.timestamp
      ? msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      : "";

    let bubbleContent = "";

    if (isError) {
      bubbleContent = `
        <div class="bubble bubble-error">
          <span class="error-icon" aria-hidden="true">${ERROR_SVG}</span>
          <span class="bubble-text">${escapeHtml(msg.text)}</span>
        </div>`;
    } else if (isSystem) {
      bubbleContent = `<div class="bubble bubble-system"><span class="bubble-text">${escapeHtml(msg.text)}</span></div>`;
    } else if (isUser) {
      bubbleContent = `<div class="bubble bubble-user"><span class="bubble-text">${escapeHtml(msg.text)}</span></div>`;
    } else if (isAssistant) {
      const actionsHtml = this.renderActions(msg.actions);
      bubbleContent = `
        <div class="bubble bubble-assistant">
          <div class="bubble-inner">
            <span class="bubble-text">${escapeHtml(msg.text)}</span>
            ${actionsHtml}
          </div>
        </div>`;
    }

    const alignClass = isUser ? "msg-right" : "msg-left";
    const timeHtml = time
      ? `<div class="msg-time ${isUser ? "msg-time--right" : ""}">${time}</div>`
      : "";

    wrap.innerHTML = `
      <div class="${alignClass}">
        ${bubbleContent}
        ${timeHtml}
      </div>`;

    return wrap;
  }

  // ── Render ───────────────────────────────────────────────────────────────

  _render() {
    if (!this.shadowRoot || this._rendered) return;

    this.shadowRoot.innerHTML = `
      <style>${CHAT_CSS}${this.renderExtraStyles()}</style>
      <div class="panel-wrap" role="main">
        <div class="header-card">${this.renderHeaderContent()}</div>
        <div class="warning-container"></div>
        <div class="chat-card">
          <div class="chat-body" role="log" aria-live="polite" aria-label="Chat messages">
            <div class="chat-empty">${escapeHtml(this.getEmptyText())}</div>
          </div>
        </div>
        <div class="input-card">
          <div class="input-row">
            <input
              id="prompt"
              class="prompt-input"
              type="text"
              placeholder="${escapeHtml(this.getPlaceholder())}"
              autocomplete="off"
              autocorrect="off"
              spellcheck="false"
            />
            <button id="send" class="send-btn" aria-label="Send">
              ${SEND_SVG}
            </button>
          </div>
        </div>
      </div>
    `;

    const input = this.shadowRoot.querySelector("#prompt");
    const sendBtn = this.shadowRoot.querySelector("#send");

    input?.addEventListener("input", (ev) => {
      this._text = ev.target.value;
    });
    input?.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        this._submit();
      }
    });
    sendBtn?.addEventListener("click", () => this._submit());

    setTimeout(() => input?.focus(), 0);
  }
}
