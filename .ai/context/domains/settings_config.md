## Domain: Settings & Configuration

### Responsibilities
- Provide a **single, validated source of truth** for all application settings.
- Persist configuration across platforms via `QSettings` while supporting JSON import/export.
- Keep settings access fast (caching) and robust (schema-based validation and migration).

### Key Modules
- `core/settings_manager.py`
  - Wraps `QSettings` and exposes high-level APIs:
    - `get(key, default)`, `set(key, value)` for single values with validation.
    - `load_all(force_reload=False)` for full settings maps with caching.
  - Manages an internal cache of settings and invalidates it when data changes.
  - Handles window geometry/state persistence for main windows/dialogs.
- `core/settings_schema.py`
  - Defines `SETTINGS_SCHEMA` with:
    - Default values per key.
    - Type, range, and enum validation for settings.
    - Migration logic for renames, deprecations, and new defaults.
  - Provides helpers like `get_default_value`, `get_all_defaults`, `validate_setting`, and `migrate_settings`.
- UI Consumers
  - `ui/preferences_dialog.py`:
    - Loads all settings, populates controls, and writes back via `SettingsManager`.
    - Handles device selection/testing and validation errors with user-friendly messages.
  - `ui/main_window.py`, `ui/record_tab.py`, `ui/transcripts_tab.py`, `speech_controller.py`:
    - Read settings for behavior (theme, hotkey, audio device, whisper engine, auto-paste, visual indicator, etc.).

### Typical Flow
1. Application startup:
   - `SettingsManager` is created early and immediately calls `load_all()` to populate and cache settings.
   - `SettingsSchema` supplies defaults and migrates any legacy entries.
2. Settings usage:
   - UI and core components read settings via `load_all()` or `get()`.
   - When a setting changes (e.g., in preferences):
     - UI calls `set(key, value)`.
     - `SettingsManager` validates via `SettingsSchema`, writes to `QSettings`, updates `_loaded_settings`, and invalidates the cache.
3. Application runtime:
   - Components can re-read `load_all()` (cache-backed) cheaply for updated configuration.
   - Geometry/state helpers apply persistent window layout on show and save on close.

### Settings Categories (Examples)
- **UI**
  - Theme (`ui/theme`), startup behavior, expert mode, visual indicator options.
- **Audio**
  - Selected input device, effects enabled, start/stop tones.
- **Behavior**
  - Auto-paste, toggle vs hold mode, hotkey configuration, indicator position.
- **Whisper / Transcription**
  - Model name, engine, language, temperature, speed mode.
- **Window**
  - Geometry and state blobs stored by Qt (`window/geometry`, `window/state`).

### Constraints & Notes
- All new settings should be added to `SETTINGS_SCHEMA` before being used in code.
- Validation failures should:
  - Log a warning with context.
  - Fall back to defaults where possible, rather than silently ignoring.
- Avoid scattering raw `QSettings` usage; route through `SettingsManager` for consistency.


