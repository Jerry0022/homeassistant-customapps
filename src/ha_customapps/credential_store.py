"""Encrypted credential storage with audit logging.

Provides Fernet-based encryption on top of HA's ``.storage/`` system.
Credentials are encrypted at rest with a per-installation key.

Usage::

    from ha_customapps.credential_store import CredentialStore

    store = CredentialStore(hass, "my_domain")
    await store.async_initialize()

    await store.async_store("api_key", "secret-value-123")
    value = await store.async_get("api_key")

    log = await store.async_get_audit_log(limit=20)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from cryptography.fernet import Fernet

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)

_STORAGE_VERSION = 1
_MAX_AUDIT_ENTRIES = 200


class CredentialStore:
    """Encrypted credential storage with audit trail.

    Parameters
    ----------
    hass : HomeAssistant
        The HA instance.
    domain : str
        Integration domain — used as storage key prefix.
    storage_version : int
        Storage schema version (default 1).
    """

    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        *,
        storage_version: int = _STORAGE_VERSION,
    ) -> None:
        self._hass = hass
        self._domain = domain
        self._key_store = Store(
            hass, storage_version, f"{domain}.credentials"
        )
        self._data_store = Store(hass, storage_version, f"{domain}.tokens")
        self._audit_store = Store(hass, storage_version, f"{domain}.audit")
        self._fernet: Fernet | None = None

    @property
    def initialized(self) -> bool:
        """Return True if the store has been initialized."""
        return self._fernet is not None

    async def async_initialize(self) -> None:
        """Load or generate the encryption key."""
        key_data = await self._key_store.async_load()
        if key_data and "encryption_key" in key_data:
            encryption_key = key_data["encryption_key"].encode()
        else:
            encryption_key = Fernet.generate_key()
            await self._key_store.async_save(
                {"encryption_key": encryption_key.decode()}
            )
        self._fernet = Fernet(encryption_key)
        _LOGGER.debug("Credential store initialized for %s", self._domain)

    async def async_store(self, key: str, value: str) -> None:
        """Encrypt and store a credential value."""
        self._ensure_initialized()
        encrypted = self._fernet.encrypt(value.encode()).decode()  # type: ignore[union-attr]
        data = await self._data_store.async_load() or {}
        data[key] = encrypted
        await self._data_store.async_save(data)
        await self._audit("credential_stored", key=key)

    async def async_get(self, key: str) -> str | None:
        """Retrieve and decrypt a credential value."""
        self._ensure_initialized()
        data = await self._data_store.async_load() or {}
        encrypted = data.get(key)
        if encrypted is None:
            return None
        try:
            return self._fernet.decrypt(encrypted.encode()).decode()  # type: ignore[union-attr]
        except Exception:
            _LOGGER.warning("Failed to decrypt credential: %s", key)
            await self._audit("credential_decrypt_failed", key=key)
            return None

    async def async_delete(self, key: str) -> bool:
        """Remove a stored credential."""
        self._ensure_initialized()
        data = await self._data_store.async_load() or {}
        if key not in data:
            return False
        del data[key]
        await self._data_store.async_save(data)
        await self._audit("credential_deleted", key=key)
        return True

    async def async_store_batch(self, credentials: dict[str, str]) -> None:
        """Encrypt and store multiple credentials at once."""
        self._ensure_initialized()
        data = await self._data_store.async_load() or {}
        for key, value in credentials.items():
            data[key] = self._fernet.encrypt(value.encode()).decode()  # type: ignore[union-attr]
        await self._data_store.async_save(data)
        await self._audit(
            "credentials_batch_stored",
            keys=list(credentials.keys()),
        )

    async def async_get_audit_log(
        self, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Return recent audit log entries (newest first)."""
        log_data = await self._audit_store.async_load() or {}
        entries = log_data.get("entries", [])
        return entries[-limit:][::-1]

    async def _audit(self, event: str, **extra: Any) -> None:
        """Append an audit entry (timestamp + event type only, never values)."""
        log_data = await self._audit_store.async_load() or {}
        entries = log_data.get("entries", [])
        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
        }
        # Include metadata keys but never credential values
        if extra:
            entry["meta"] = {
                k: v for k, v in extra.items() if k != "value"
            }
        entries.append(entry)
        # Trim old entries
        if len(entries) > _MAX_AUDIT_ENTRIES:
            entries = entries[-_MAX_AUDIT_ENTRIES:]
        await self._audit_store.async_save({"entries": entries})

    def _ensure_initialized(self) -> None:
        """Raise if not initialized."""
        if self._fernet is None:
            raise RuntimeError(
                f"CredentialStore for {self._domain} not initialized. "
                "Call async_initialize() first."
            )
