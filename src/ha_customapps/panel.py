"""Sidebar panel registration for custom dashboard integrations.

Abstracts the boilerplate of registering a sidebar panel with icon,
static file paths, and optional Lovelace card components.

Usage::

    from ha_customapps.panel import PanelRegistrar

    registrar = PanelRegistrar(
        hass=hass,
        domain="my_app",
        panel_component="my-app-panel",
        panel_title="My App",
        panel_icon="mdi:application",
        panel_url_path="my-app",
        module_url="/api/my_app/static/my-app-panel.js",
        lovelace_urls=[
            "/api/my_app/static/my-card.js",
        ],
    )
    await registrar.async_register()
"""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import panel_custom
from homeassistant.components.frontend import (
    add_extra_js_url,
)
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class PanelRegistrar:
    """Register a sidebar panel with static file serving.

    Parameters
    ----------
    hass : HomeAssistant
        The HA instance.
    domain : str
        Integration domain.
    panel_component : str
        Web Component tag name (e.g. ``"my-app-panel"``).
    panel_title : str
        Sidebar display title.
    panel_icon : str
        MDI icon string (e.g. ``"mdi:application"``).
    panel_url_path : str
        URL slug for the panel route.
    module_url : str
        URL to the main JS module (served by HA static).
    frontend_dir : str | Path | None
        Local path to the frontend directory. If provided, a static
        path is registered automatically at ``/api/{domain}/static``.
    lovelace_urls : list[str] | None
        Additional JS URLs to register as Lovelace resources.
    require_admin : bool
        Restrict panel to admin users (default False).
    config : dict | None
        Extra config passed to the panel Web Component.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        *,
        panel_component: str,
        panel_title: str,
        panel_icon: str,
        panel_url_path: str,
        module_url: str,
        frontend_dir: str | Path | None = None,
        lovelace_urls: list[str] | None = None,
        require_admin: bool = False,
        config: dict | None = None,
    ) -> None:
        self._hass = hass
        self._domain = domain
        self._panel_component = panel_component
        self._panel_title = panel_title
        self._panel_icon = panel_icon
        self._panel_url_path = panel_url_path
        self._module_url = module_url
        self._frontend_dir = Path(frontend_dir) if frontend_dir else None
        self._lovelace_urls = lovelace_urls or []
        self._require_admin = require_admin
        self._config = config or {"domain": domain}

    async def async_register(self) -> None:
        """Register static paths, sidebar panel, and Lovelace resources."""
        # 1. Register static file serving
        if self._frontend_dir and self._frontend_dir.is_dir():
            static_base = f"/api/{self._domain}/static"
            await self._hass.http.async_register_static_paths(
                [
                    StaticPathConfig(
                        static_base,
                        str(self._frontend_dir),
                        True,  # cache-busting via version in URL
                    )
                ]
            )
            _LOGGER.debug("Registered static path: %s", static_base)

        # 2. Register the sidebar panel
        await panel_custom.async_register_panel(
            self._hass,
            webcomponent_name=self._panel_component,
            frontend_url_path=self._panel_url_path,
            module_url=self._module_url,
            sidebar_title=self._panel_title,
            sidebar_icon=self._panel_icon,
            require_admin=self._require_admin,
            config=self._config,
        )
        _LOGGER.debug("Registered sidebar panel: %s", self._panel_title)

        # 3. Register Lovelace card JS resources
        for url in self._lovelace_urls:
            add_extra_js_url(self._hass, url)
            _LOGGER.debug("Registered Lovelace resource: %s", url)
