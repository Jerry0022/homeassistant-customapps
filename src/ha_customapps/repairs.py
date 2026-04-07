"""Generic Repairs flow for restart-required issues.

Provides a ready-to-use ``async_create_fix_flow`` that any integration
can wire up by adding a thin ``repairs.py`` in its own package::

    # my_integration/repairs.py
    from ha_customapps.repairs import async_create_fix_flow  # noqa: F401

Or, if custom repair flows are needed alongside the restart flow::

    from ha_customapps.repairs import RestartRepairFlow

    async def async_create_fix_flow(hass, issue_id, data):
        if issue_id == "restart_required":
            return RestartRepairFlow()
        if issue_id == "my_custom_issue":
            return MyCustomFlow()
        return None
"""

from __future__ import annotations

from homeassistant import data_entry_flow
from homeassistant.components.repairs import RepairsFlow
from homeassistant.core import HomeAssistant


class RestartRepairFlow(RepairsFlow):
    """Repair flow that restarts Home Assistant when the user confirms."""

    async def async_step_init(
        self, user_input: dict | None = None
    ) -> data_entry_flow.FlowResult:
        """Show confirmation form, then restart HA."""
        if user_input is not None:
            await self.hass.services.async_call("homeassistant", "restart")
            return self.async_create_entry(data={}, title="")
        return self.async_show_form(step_id="init")


async def async_create_fix_flow(
    hass: HomeAssistant, issue_id: str, data: dict | None
) -> RepairsFlow | None:
    """Default fix-flow factory — handles ``restart_required`` only."""
    if issue_id == "restart_required":
        return RestartRepairFlow()
    return None
