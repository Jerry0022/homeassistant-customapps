"""ha-customapps — Shared framework for Home Assistant custom apps.

Provides reusable building blocks for custom integrations, companion
add-ons, and sidebar dashboard panels. Designed to be listed in
manifest.json ``requirements`` so HA auto-installs it.

Usage in a custom integration::

    # manifest.json
    { "requirements": ["ha-customapps>=0.3.0"] }

    # __init__.py
    from ha_customapps.panel import PanelRegistrar
    from ha_customapps.credential_store import CredentialStore
    from ha_customapps.restart import RestartNotifier
    from ha_customapps.llm import extract_json, parse_llm_json, call_ha_conversation_agent
    from ha_customapps.config_helpers import get_primary_entry, get_merged_config, model_selector
    from ha_customapps.entity_utils import resolve_area_name, serialize_entity_base
    from ha_customapps.const import CONF_PROVIDER, CONF_MODEL, PROVIDER_MODELS
"""

__version__ = "0.3.0"
