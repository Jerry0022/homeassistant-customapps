"""Config entry helpers for Home Assistant custom integrations.

Provides reusable patterns for accessing config entries, merging
options with data, and building UI selectors.

Usage::

    from ha_customapps.config_helpers import (
        get_primary_entry,
        get_merged_config,
        model_selector,
    )

    entry = get_primary_entry(hass, DOMAIN)
    config = get_merged_config(entry, defaults={"model": "gpt-4o-mini"})
    selector = model_selector(["gpt-4o-mini", "gpt-4o"])
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector


def get_primary_entry(hass: HomeAssistant, domain: str) -> ConfigEntry:
    """Return the first config entry for the given domain.

    Parameters
    ----------
    hass : HomeAssistant
        The HA instance.
    domain : str
        Integration domain.

    Returns
    -------
    ConfigEntry
        The first config entry.

    Raises
    ------
    ValueError
        If no config entry exists for the domain.
    """
    entries = list(hass.config_entries.async_entries(domain))
    if not entries:
        raise ValueError(f"No configuration found for {domain}")
    return entries[0]


def get_merged_config(
    entry: ConfigEntry,
    defaults: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge config entry data and options with optional defaults.

    Options take precedence over data, which takes precedence over
    defaults.

    Parameters
    ----------
    entry : ConfigEntry
        The config entry.
    defaults : dict, optional
        Default values for missing keys.

    Returns
    -------
    dict
        The merged configuration.
    """
    result = dict(defaults or {})
    result.update(entry.data)
    result.update(entry.options)
    return result


def model_selector(
    models: list[str],
    *,
    custom_value: bool = True,
    mode: str = "dropdown",
) -> selector.SelectSelector:
    """Build a Home Assistant model selector for config flows.

    Parameters
    ----------
    models : list of str
        Available model identifiers.
    custom_value : bool
        Allow users to enter custom model names (default True).
    mode : str
        Selector display mode (default "dropdown").

    Returns
    -------
    selector.SelectSelector
        A selector ready for use in a config flow schema.
    """
    mode_enum = getattr(
        selector.SelectSelectorMode,
        mode.upper(),
        selector.SelectSelectorMode.DROPDOWN,
    )
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=models,
            custom_value=custom_value,
            mode=mode_enum,
        )
    )
