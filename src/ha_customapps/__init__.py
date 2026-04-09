"""ha-customapps — Shared framework for Home Assistant custom apps.

Provides reusable building blocks for custom integrations, companion
add-ons, and sidebar dashboard panels. Designed to be listed in
manifest.json ``requirements`` so HA auto-installs it.

Usage in a custom integration::

    # manifest.json — install from GitHub release archive
    { "requirements": ["ha-customapps @ https://github.com/Jerry0022/homeassistant-customapps/archive/refs/tags/v0.2.0.zip"] }

    # __init__.py
    from ha_customapps.restart import RestartNotifier
    from ha_customapps.panel import PanelRegistrar
    from ha_customapps.credential_store import CredentialStore
"""

__version__ = "0.2.0"
