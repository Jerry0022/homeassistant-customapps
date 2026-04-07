/**
 * ha-data-provider.js — Generic data provider Web Component.
 *
 * Subscribes to HA entity state changes and dispatches events
 * to sibling components. Provides debounced updates and
 * API call helpers.
 *
 * Usage:
 *   import { HaDataProvider } from "./ha-data-provider.js";
 *
 *   class MyDataProvider extends HaDataProvider {
 *     static get tag() { return "my-data-provider"; }
 *     get domain() { return "my_domain"; }
 *     get entityPrefix() { return "sensor.my_"; }
 *
 *     transformData(entities) {
 *       return { value: entities["sensor.my_value"]?.state };
 *     }
 *   }
 *
 *   MyDataProvider.register();
 */

const DEFAULT_DEBOUNCE_MS = 250;

export class HaDataProvider extends HTMLElement {
  static get tag() {
    throw new Error("Subclass must define static get tag()");
  }

  /** Override: integration domain for API calls. */
  get domain() {
    throw new Error("Subclass must define get domain()");
  }

  /** Override: entity ID prefix for filtering state changes. */
  get entityPrefix() {
    return "";
  }

  /** Override: transform HA entities into your data shape. */
  transformData(_entities) {
    return {};
  }

  constructor() {
    super();
    this._hass = null;
    this._debounceTimer = null;
    this._debounceMs = DEFAULT_DEBOUNCE_MS;
    this._data = null;
  }

  set hass(hass) {
    this._hass = hass;
    clearTimeout(this._debounceTimer);
    this._debounceTimer = setTimeout(
      () => this._onHassChanged(),
      this._debounceMs
    );
  }

  get hass() {
    return this._hass;
  }

  get data() {
    return this._data;
  }

  /** Register custom element. */
  static register() {
    if (!customElements.get(this.tag)) {
      customElements.define(this.tag, this);
    }
  }

  /** Call an HA API endpoint. */
  async callApi(method, path) {
    if (!this._hass) throw new Error("hass not set");
    return this._hass.callApi(method, `${this.domain}/${path}`);
  }

  /** Call an HA service. */
  async callService(service, data = {}) {
    if (!this._hass) throw new Error("hass not set");
    return this._hass.callService(this.domain, service, data);
  }

  /** Dispatch a data-updated event to parent/sibling components. */
  _dispatch(detail) {
    this.dispatchEvent(
      new CustomEvent("data-updated", {
        detail,
        bubbles: true,
        composed: true,
      })
    );
  }

  /** Called after debounce when HA state changes. */
  _onHassChanged() {
    if (!this._hass) return;

    const prefix = this.entityPrefix;
    const entities = {};

    if (prefix) {
      for (const [id, state] of Object.entries(this._hass.states)) {
        if (id.startsWith(prefix)) {
          entities[id] = state;
        }
      }
    }

    try {
      this._data = this.transformData(entities);
      this._dispatch(this._data);
    } catch (err) {
      this._dispatch({ error: err.message });
    }
  }

  /** Trigger a manual refresh. */
  async refresh() {
    this._onHassChanged();
  }
}
