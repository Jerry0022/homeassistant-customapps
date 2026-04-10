"""Shared constants for Home Assistant custom integrations.

Provides common config key names and a provider model registry
used across multiple integrations.

Usage::

    from ha_customapps.const import CONF_PROVIDER, CONF_MODEL, PROVIDER_MODELS

    provider = config.get(CONF_PROVIDER, DEFAULT_PROVIDER)
    models = PROVIDER_MODELS.get(provider, [])
"""

from __future__ import annotations

# ── Common config keys ────────────────────────────────────────────────────────

CONF_PROVIDER = "provider"
CONF_API_KEY = "api_key"
CONF_MODEL = "model"
CONF_BASE_URL = "base_url"
CONF_LLM_SOURCE = "llm_source"

# ── Default LLM settings ─────────────────────────────────────────────────────

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_BASE_URL = "https://api.openai.com/v1"

LLM_SOURCE_HA_CONVERSATION = "ha_conversation"

# ── Provider model registry ───────────────────────────────────────────────────
# Integrations can extend this at runtime if needed.

PROVIDER_MODELS: dict[str, list[str]] = {
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"],
    "anthropic": ["claude-3-5-haiku-latest", "claude-3-5-sonnet-latest"],
    "google": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
}

# ── Common conversation agent domains ────────────────────────────────────────

OPENAI_AGENT_DOMAINS = ("openai_conversation", "openai")
