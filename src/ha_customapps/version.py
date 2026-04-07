"""Version management utilities.

Provides helpers for reading, comparing, and bumping semantic versions
across the standard HA custom app file trio:
  - ``custom_components/{domain}/manifest.json``
  - ``{domain}_companion/config.yaml``
  - ``custom_components/{domain}/const.py``

Usage::

    from ha_customapps.version import VersionManager

    mgr = VersionManager(
        domain="my_app",
        repo_root=Path("/path/to/repo"),
    )
    aligned, versions = mgr.check_alignment()
    new_version = mgr.bump("patch")
"""

from __future__ import annotations

import json
import re
from pathlib import Path


def bump_semver(current: str, part: str) -> str:
    """Bump a semantic version string.

    Parameters
    ----------
    current : str
        Current version (e.g. ``"1.2.3"``).
    part : str
        One of ``"major"``, ``"minor"``, ``"patch"``.

    Returns
    -------
    str
        The bumped version string.
    """
    major, minor, patch = map(int, current.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


class VersionManager:
    """Manage version alignment across HA custom app files.

    Parameters
    ----------
    domain : str
        Integration domain (e.g. ``"finance_dashboard"``).
    repo_root : Path
        Repository root directory.
    companion_slug : str | None
        Companion add-on directory name. Default: ``{domain}_companion``.
    const_variable : str
        Name of the version constant in ``const.py`` (default ``"VERSION"``).
    """

    def __init__(
        self,
        domain: str,
        repo_root: Path,
        *,
        companion_slug: str | None = None,
        const_variable: str = "VERSION",
    ) -> None:
        self.domain = domain
        self.root = repo_root
        self.companion_slug = companion_slug or f"{domain}_companion"
        self.const_variable = const_variable

        self.manifest_path = (
            repo_root / "custom_components" / domain / "manifest.json"
        )
        self.addon_config_path = (
            repo_root / self.companion_slug / "config.yaml"
        )
        self.const_path = (
            repo_root / "custom_components" / domain / "const.py"
        )

    def get_manifest_version(self) -> str | None:
        """Read version from manifest.json."""
        if not self.manifest_path.exists():
            return None
        data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        return data.get("version")

    def get_addon_version(self) -> str | None:
        """Read version from companion config.yaml."""
        if not self.addon_config_path.exists():
            return None
        text = self.addon_config_path.read_text(encoding="utf-8")
        match = re.search(
            r'^version:\s*"?(\d+\.\d+\.\d+)"?', text, re.MULTILINE
        )
        return match.group(1) if match else None

    def get_const_version(self) -> str | None:
        """Read VERSION constant from const.py."""
        if not self.const_path.exists():
            return None
        text = self.const_path.read_text(encoding="utf-8")
        match = re.search(
            rf'^{self.const_variable}\s*=\s*"(\d+\.\d+\.\d+)"',
            text,
            re.MULTILINE,
        )
        return match.group(1) if match else None

    def check_alignment(self) -> tuple[bool, dict[str, str | None]]:
        """Check if all version files are aligned.

        Returns
        -------
        tuple[bool, dict]
            ``(aligned, {"manifest": "x.y.z", "addon": ..., "const": ...})``
        """
        versions = {
            "manifest": self.get_manifest_version(),
            "addon": self.get_addon_version(),
            "const": self.get_const_version(),
        }
        present = [v for v in versions.values() if v is not None]
        aligned = len(set(present)) <= 1 and len(present) > 0
        return aligned, versions

    def set_version(self, new_version: str) -> list[str]:
        """Write the new version to all files. Returns list of updated files."""
        updated: list[str] = []

        # manifest.json
        if self.manifest_path.exists():
            data = json.loads(
                self.manifest_path.read_text(encoding="utf-8")
            )
            data["version"] = new_version
            self.manifest_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            updated.append(str(self.manifest_path))

        # config.yaml
        if self.addon_config_path.exists():
            text = self.addon_config_path.read_text(encoding="utf-8")
            text = re.sub(
                r'^(version:\s*)"?\d+\.\d+\.\d+"?',
                rf'\g<1>"{new_version}"',
                text,
                count=1,
                flags=re.MULTILINE,
            )
            self.addon_config_path.write_text(text, encoding="utf-8")
            updated.append(str(self.addon_config_path))

        # const.py
        if self.const_path.exists():
            text = self.const_path.read_text(encoding="utf-8")
            text = re.sub(
                rf'^({self.const_variable}\s*=\s*")[\d.]+"',
                rf"\g<1>{new_version}\"",
                text,
                count=1,
                flags=re.MULTILINE,
            )
            self.const_path.write_text(text, encoding="utf-8")
            updated.append(str(self.const_path))

        return updated

    def bump(self, part: str) -> str:
        """Bump version in all files. Returns the new version string."""
        current = self.get_manifest_version()
        if current is None:
            raise FileNotFoundError(
                f"Cannot read current version from {self.manifest_path}"
            )
        new_version = bump_semver(current, part)
        self.set_version(new_version)
        return new_version
