"""Restart notification framework for companion add-on updates.

Implements the marker-file + HA Repairs pattern:
1. Companion add-on writes a JSON marker after copying new files.
2. Integration polls for marker, creates a Repairs issue.
3. User clicks Fix → HA restarts → new code loads.

Usage::

    from ha_customapps.restart import RestartNotifier

    # In async_setup_entry:
    notifier = RestartNotifier(hass, "my_domain")
    await notifier.async_setup(entry)

    # In async_unload_entry:
    # (cleanup is automatic via entry.async_on_unload)
"""

from __future__ import annotations

import json
import logging
from datetime import timedelta
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)

_DEFAULT_POLL_SECONDS = 60
_ISSUE_ID = "restart_required"


class RestartNotifier:
    """Manage restart-required notifications via HA Repairs.

    Parameters
    ----------
    hass : HomeAssistant
        The HA instance.
    domain : str
        Integration domain (e.g. ``"finance_dashboard"``).
    poll_seconds : int
        How often to check for the marker file (default 60).
    marker_filename : str | None
        Override the marker filename. Default: ``{domain}_restart_needed.json``.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        *,
        poll_seconds: int = _DEFAULT_POLL_SECONDS,
        marker_filename: str | None = None,
    ) -> None:
        self._hass = hass
        self._domain = domain
        self._poll_seconds = poll_seconds
        self._marker_filename = (
            marker_filename or f"{domain}_restart_needed.json"
        )

    @property
    def marker_path(self) -> Path:
        """Absolute path to the restart marker file."""
        return Path(
            self._hass.config.path(f".storage/{self._marker_filename}")
        )

    async def async_setup(self, entry: ConfigEntry) -> None:
        """Register polling and clean up stale issues.

        Call this during ``async_setup_entry``. The poll timer is
        automatically cancelled when the config entry is unloaded.
        """
        # Clean up stale issues if no marker is pending
        if not await self._hass.async_add_executor_job(
            self.marker_path.exists
        ):
            ir.async_delete_issue(self._hass, self._domain, _ISSUE_ID)

        # Register periodic poll
        entry.async_on_unload(
            async_track_time_interval(
                self._hass,
                self._poll_restart_marker,
                timedelta(seconds=self._poll_seconds),
            )
        )

        # Fire first poll immediately
        await self._poll_restart_marker(None)

    async def _poll_restart_marker(self, _now: Any) -> None:
        """Check for marker file, create Repairs issue if found."""
        data = await self._hass.async_add_executor_job(
            self._read_and_delete_marker
        )
        if data is None:
            return

        version = data.get("version", "unknown")
        ir.async_create_issue(
            self._hass,
            self._domain,
            _ISSUE_ID,
            is_fixable=True,
            is_persistent=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key=_ISSUE_ID,
            translation_placeholders={"version": version},
        )
        _LOGGER.info(
            "Restart required for %s v%s — Repairs issue created",
            self._domain,
            version,
        )

    def _read_and_delete_marker(self) -> dict | None:
        """Read and atomically delete the marker (runs in executor)."""
        marker = self.marker_path
        if not marker.exists():
            return None
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
            marker.unlink()
            return data
        except Exception:
            _LOGGER.exception("Failed to read restart marker at %s", marker)
            return None
