"""Entity serialization utilities for Home Assistant integrations.

Provides helpers for resolving entity areas and serializing entity
state to plain dictionaries.

Usage::

    from ha_customapps.entity_utils import resolve_area_name, serialize_entity_base

    area = resolve_area_name(entity_reg, area_reg, entity_id)
    base = serialize_entity_base(state, entity_reg, area_reg)
"""

from __future__ import annotations

from typing import Any

from homeassistant.core import State
from homeassistant.helpers import area_registry as ar, entity_registry as er


def resolve_area_name(
    entity_reg: er.EntityRegistry,
    area_reg: ar.AreaRegistry,
    entity_id: str,
    *,
    default: str = "unknown",
) -> str:
    """Resolve the area name for an entity.

    Parameters
    ----------
    entity_reg : EntityRegistry
        The entity registry.
    area_reg : AreaRegistry
        The area registry.
    entity_id : str
        The entity ID to look up.
    default : str
        Fallback name if no area is assigned (default "unknown").

    Returns
    -------
    str
        The area name or default.
    """
    entry = entity_reg.async_get(entity_id)
    if entry and entry.area_id:
        area_entry = area_reg.async_get_area(entry.area_id)
        if area_entry:
            return area_entry.name
    return default


def serialize_entity_base(
    state: State,
    entity_reg: er.EntityRegistry,
    area_reg: ar.AreaRegistry,
) -> dict[str, Any]:
    """Serialize core entity fields common to all domains.

    Returns a dict with ``entity_id``, ``name``, ``area``, and
    ``state``. Consumers should extend this with domain-specific
    attributes.

    Parameters
    ----------
    state : State
        The entity state object.
    entity_reg : EntityRegistry
        The entity registry.
    area_reg : AreaRegistry
        The area registry.

    Returns
    -------
    dict
        Base entity data.
    """
    attrs = state.attributes
    return {
        "entity_id": state.entity_id,
        "name": attrs.get("friendly_name", state.name),
        "area": resolve_area_name(entity_reg, area_reg, state.entity_id),
        "state": state.state,
    }
