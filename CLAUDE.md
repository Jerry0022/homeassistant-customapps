# ha-customapps

Shared Python/JS framework for Home Assistant custom integrations, add-ons, and dashboard panels.

## Architecture

- `src/ha_customapps/` — pip-installable Python library (hatchling build)
- `frontend/` — Web Components for HA sidebar panels
- `templates/` — Scaffolding for addon, integration, CI workflows

## Key Patterns

- Version must stay aligned: `pyproject.toml`, `src/ha_customapps/__init__.py`
- Published to PyPI via OIDC trusted publishing (tag `v*` triggers)
- Used by HA integrations via `manifest.json` requirements: `"ha-customapps>=0.x.y"`

## Commands

```bash
python -m build          # Build package
pip install -e .         # Dev install
```
