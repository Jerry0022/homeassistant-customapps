/**
 * ha-panel-shell.js — Generic sidebar panel Web Component shell.
 *
 * Extend this class for your custom dashboard panel. Provides:
 * - Shadow DOM setup
 * - HA hass object handling
 * - Loading/error state management
 * - Event wiring pattern
 *
 * Usage:
 *   import { HaPanelShell, BASE_CSS } from "./ha-panel-shell.js";
 *
 *   class MyAppPanel extends HaPanelShell {
 *     static get tag() { return "my-app-panel"; }
 *
 *     renderContent() {
 *       return `<h1>Hello from My App</h1>`;
 *     }
 *
 *     onData(data) {
 *       // Update child components with fresh data
 *     }
 *   }
 *
 *   MyAppPanel.register();
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
    --radius: 12px;
    --gap: 16px;
    display: block;
    font-family: var(--paper-font-body1_-_font-family, "Roboto", sans-serif);
    color: var(--tx);
    background: var(--bg);
    min-height: 100vh;
  }
  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;
    color: var(--tx2);
    font-size: 1.1em;
  }
  .error {
    padding: var(--gap);
    text-align: center;
    color: #ef4444;
  }
`;

export class HaPanelShell extends HTMLElement {
  /** Override in subclass — returns the custom element tag name. */
  static get tag() {
    throw new Error("Subclass must define static get tag()");
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._rendered = false;
  }

  /** HA sets this property whenever state changes. */
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

  /** Override to provide your panel's inner HTML. */
  renderContent() {
    return `<div class="loading">Loading...</div>`;
  }

  /** Override to provide additional CSS beyond BASE_CSS. */
  renderStyles() {
    return "";
  }

  /** Called every time HA pushes a state update. Override as needed. */
  onHassUpdate(_hass) {}

  /** Called when a data-updated event fires. Override to handle data. */
  onData(_data) {}

  /** Called when a refresh event fires. Override to trigger refresh. */
  onRefresh() {}

  /** Register this element with the custom elements registry. */
  static register() {
    if (!customElements.get(this.tag)) {
      customElements.define(this.tag, this);
    }
  }

  _render() {
    this.shadowRoot.innerHTML = `
      <style>${BASE_CSS}${this.renderStyles()}</style>
      <div id="shell">
        ${this.renderContent()}
      </div>
    `;

    // Wire up standard events
    this.shadowRoot.addEventListener("data-updated", (e) => {
      this.onData(e.detail);
    });
    this.shadowRoot.addEventListener("refresh-requested", () => {
      this.onRefresh();
    });
  }
}
