# ha-customapps

Shared framework for building Home Assistant custom integrations, companion add-ons, and sidebar dashboard panels.

Eliminates boilerplate by providing production-ready building blocks for the patterns every HA custom app needs: update notifications, encrypted credential storage, sidebar panels, version management, and CI/CD workflows.

## How it works

`ha-customapps` is a **Python package** that HA auto-installs when listed in your integration's `manifest.json`:

```json
{
  "domain": "my_app",
  "requirements": ["ha-customapps>=0.1.0"]
}
```

Your integration then imports the modules it needs:

```python
from ha_customapps.restart import RestartNotifier
from ha_customapps.panel import PanelRegistrar
from ha_customapps.credential_store import CredentialStore
```

## Architecture

```
ha-customapps/
├── src/ha_customapps/          # Python library (pip installable)
│   ├── restart.py              # Restart marker + HA Repairs notification
│   ├── repairs.py              # Generic repair flow (restart on confirm)
│   ├── panel.py                # Sidebar panel registration
│   ├── credential_store.py     # Fernet-encrypted credential storage + audit
│   └── version.py              # Semantic version management across files
├── frontend/                   # JS utilities (copy into your frontend/)
│   ├── ha-panel-shell.js       # Base Web Component for sidebar panels
│   ├── ha-data-provider.js     # Base data provider with HA state subscription
│   └── ha-shared-utils.js      # Formatters, XSS escape, shared CSS
└── templates/                  # Scaffolding templates (copy + customize)
    ├── addon/                  # Companion add-on (Dockerfile, run.sh, config)
    ├── integration/            # Integration boilerplate (strings.json, repairs.py)
    └── ci/                     # GitHub Actions (validate.yml, release.yml)
```

## Modules

### RestartNotifier

Implements the marker-file + HA Repairs pattern for companion add-on updates:

1. Add-on copies new files and writes a JSON marker to `.storage/`
2. Integration polls for marker, creates a Repairs issue with version info
3. User clicks Fix in Settings > System > Repairs, HA restarts

```python
# __init__.py
from ha_customapps.restart import RestartNotifier

async def async_setup_entry(hass, entry):
    notifier = RestartNotifier(hass, DOMAIN)
    await notifier.async_setup(entry)  # polls + auto-cleanup
```

The matching `repairs.py` is a one-liner:

```python
# repairs.py
from ha_customapps.repairs import async_create_fix_flow  # noqa: F401
```

Add the `restart_required` issue strings to your `strings.json` (see `templates/integration/strings.json` for the full template).

### PanelRegistrar

Registers a sidebar panel with static file serving and optional Lovelace card resources:

```python
from ha_customapps.panel import PanelRegistrar

registrar = PanelRegistrar(
    hass=hass,
    domain="my_app",
    panel_component="my-app-panel",
    panel_title="My App",
    panel_icon="mdi:application",
    panel_url_path="my-app",
    module_url=f"/api/my_app/static/my-app-panel.js?v={VERSION}",
    frontend_dir=hass.config.path("custom_components", "my_app", "frontend"),
    lovelace_urls=["/api/my_app/static/my-card.js"],
)
await registrar.async_register()
```

### CredentialStore

Fernet-encrypted credential storage with audit logging:

```python
from ha_customapps.credential_store import CredentialStore

store = CredentialStore(hass, DOMAIN)
await store.async_initialize()

# Store (encrypted at rest in .storage/)
await store.async_store("api_key", "secret-value")
await store.async_store_batch({"client_id": "abc", "client_secret": "xyz"})

# Retrieve (decrypted on read)
api_key = await store.async_get("api_key")

# Audit trail (timestamps + event types only, never values)
log = await store.async_get_audit_log(limit=20)
```

### VersionManager

Keeps versions aligned across the standard HA custom app file trio:

```python
from pathlib import Path
from ha_customapps.version import VersionManager

mgr = VersionManager("my_app", repo_root=Path("."))

# Check alignment
aligned, versions = mgr.check_alignment()
# versions = {"manifest": "1.2.3", "addon": "1.2.3", "const": "1.2.3"}

# Bump all files atomically
new_version = mgr.bump("patch")  # "1.2.4"
```

## Frontend Utilities

Copy the files from `frontend/` into your integration's frontend directory.

### ha-panel-shell.js

Base class for sidebar dashboard panels:

```javascript
import { HaPanelShell } from "./ha-panel-shell.js";

class MyAppPanel extends HaPanelShell {
  static get tag() { return "my-app-panel"; }

  renderContent() {
    return `<div class="card"><h2>Dashboard</h2></div>`;
  }

  onData(data) {
    // Update UI with fresh data
  }
}

MyAppPanel.register();
```

### ha-data-provider.js

Base class for HA entity state subscription with debounced updates:

```javascript
import { HaDataProvider } from "./ha-data-provider.js";

class MyDataProvider extends HaDataProvider {
  static get tag() { return "my-data-provider"; }
  get domain() { return "my_app"; }
  get entityPrefix() { return "sensor.my_app_"; }

  transformData(entities) {
    return { status: entities["sensor.my_app_status"]?.state };
  }
}

MyDataProvider.register();
```

### ha-shared-utils.js

Formatters, XSS escape, and shared CSS custom properties:

```javascript
import { formatCurrency, escapeHtml, BASE_CSS } from "./ha-shared-utils.js";

formatCurrency(42.5);         // "42,50 €"
formatCurrency(42.5, "USD", "en-US"); // "$42.50"
escapeHtml("<script>alert(1)</script>");  // safe string
```

## Templates

The `templates/` directory contains ready-to-use scaffolding. Copy and replace the `__PLACEHOLDERS__`:

| Placeholder | Example |
|---|---|
| `__DOMAIN__` | `my_app` |
| `__ADDON_NAME__` | `My App` |
| `__ADDON_SLUG__` | `my_app_companion` |
| `__DESCRIPTION__` | `Companion add-on for My App integration` |
| `__REPO_URL__` | `https://github.com/user/repo` |
| `__REPO_NAME__` | `My App Add-ons` |
| `__MAINTAINER__` | `Your Name <you@example.com>` |

### Add-on Repository Structure

For HA Supervisor to recognize a GitHub repo as an add-on repository, it needs:

1. `repository.yaml` at the repo root (use the template in `templates/addon/`)
2. At least one subdirectory containing a `config.yaml` (the add-on)

Minimal repo structure:

```
repository.yaml              # Required — repo metadata for HA Supervisor
my_addon/                    # Add-on directory (one per add-on)
├── config.yaml              # Required — add-on metadata
├── Dockerfile               # Required — build instructions
├── build.yaml               # Multi-arch base images
└── run.sh                   # Entry point
custom_components/my_app/    # Optional — custom integration (for HACS)
├── manifest.json
└── ...
```

The `repository.yaml` template uses three placeholders: `__REPO_NAME__`, `__REPO_URL__`, and `__MAINTAINER__`.

### Companion Add-on

```
templates/addon/
├── Dockerfile      # Alpine + bash + curl
├── run.sh          # Smart installer (version compare, marker, notification)
├── config.yaml     # HA add-on metadata
└── build.yaml      # Multi-arch base images
```

### CI/CD

```
templates/ci/
├── validate.yml    # Python/JS syntax, YAML/JSON, version alignment
└── release.yml     # Tag-triggered GitHub Release with changelog extraction
```

## Integration into existing projects

### Option A: pip dependency (recommended)

Add to `manifest.json`:

```json
{ "requirements": ["ha-customapps>=0.1.0"] }
```

HA installs it automatically. Import and use the Python modules directly.

### Option B: Copy what you need

For projects that can't use pip dependencies, copy individual files:
- Python modules from `src/ha_customapps/` into your integration
- Frontend utilities from `frontend/` into your frontend directory
- Templates from `templates/` as scaffolding

### Option C: Git submodule

```bash
git submodule add https://github.com/Jerry0022/homeassistant-customapps.git lib/ha-customapps
```

## Icon handling

HA custom apps need icons in multiple places:

| File | Purpose | Location |
|---|---|---|
| `icon.png` | Add-on store icon | `{addon}/icon.png` |
| `logo.png` | Add-on store logo | `{addon}/logo.png` |
| `dark_icon.png` | Dark theme variant | `{addon}/dark_icon.png` |
| `dark_logo.png` | Dark theme variant | `{addon}/dark_logo.png` |
| `brand/icon.png` | Integration brand icon | `custom_components/{domain}/brand/icon.png` |
| `brand/logo.png` | Integration brand logo | `custom_components/{domain}/brand/logo.png` |
| Sidebar icon | MDI icon string | Set in `PanelRegistrar(panel_icon="mdi:...")` |
| Entity icons | MDI icon strings | Set in entity `_attr_icon` or via `const.py` mapping |

Recommended sizes: `icon.png` 256x256, `logo.png` 256x256. Provide both light and dark variants.

## HA update recognition

For HA to properly detect and display updates:

1. **Version in `manifest.json`** — HA reads this to display the current version
2. **GitHub Releases with `v*` tags** — HACS and manual update checkers use these
3. **`hacs.json`** (if using HACS) — configure rendering and content type
4. **Companion add-on `config.yaml` version** — HA Supervisor reads this for add-on updates
5. **Restart marker** — `RestartNotifier` creates the Repairs issue after file copy

The `VersionManager` ensures all version files stay in sync.

## License

MIT
