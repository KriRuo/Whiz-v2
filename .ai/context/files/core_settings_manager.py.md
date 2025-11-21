## File: `core/settings_manager.py`

### Purpose
- Central entry point for **persistent application settings**:
  - Wraps `QSettings` for cross-platform storage.
  - Applies schema-driven defaults, validation, and migration via `SETTINGS_SCHEMA`.
  - Exposes a cache-aware API for reading and writing configuration.
  - Manages window geometry/state and JSON import/export of settings.

### Key Responsibilities & Behavior
- **Initialization & Caching**
  - Configured with an organization/app name (default `Whiz` / `VoiceToText`).
  - Immediately calls `load_all()` to:
    - Pull existing `QSettings` keys, validate with `SETTINGS_SCHEMA`, and merge with defaults.
    - Apply migration logic to produce a consistent final settings dict.
    - Populate `_settings_cache` and `_loaded_settings`, marking the cache as valid.
- **Core API**
  - `get(key, default=None)`:
    - Reads from `_loaded_settings` first, then falls back to `QSettings` with schema defaults.
    - Validates values using `SETTINGS_SCHEMA.validate_setting`, logging and reverting to defaults on errors.
  - `set(key, value, _use_default_on_error=False)`:
    - Validates the value (if the key is in the schema), writes to `QSettings`, syncs to disk, and updates `_loaded_settings`.
    - On validation error, attempts to fall back to the schema default (without infinite recursion) and raises if that also fails.
    - Invalidates the cached map via `_invalidate_cache()`.
  - `load_all(force_reload=False)`:
    - Returns a copy of the cached settings when `cache_valid` is `True` and not forcing reload.
    - Otherwise reloads from `QSettings`, applies validation + migration, and refreshes the cache.
  - `get_cache_status()` exposes cache validity and age for diagnostics.
- **Window State**
  - `save_window(main_window)` and `restore_window(main_window)`:
    - Save/restore `window/geometry` and `window/state` using `saveGeometry()` / `saveState()` and `restoreGeometry()` / `restoreState()`.
    - Store blobs as `QByteArray` values in `QSettings`.
- **Settings Application**
  - `apply_all(main_window)`:
    - Reloads settings (respecting cache) and delegates to:
      - `_apply_theme()`: calls `main_window.apply_theme(theme)` when available.
      - `_apply_behavior_settings()`: updates `SpeechController` (auto-paste, toggle mode, hotkey, visual indicator) and main window behavior (minimize to tray, indicator widget, hotkey instruction).
      - `_apply_audio_settings()` + `_apply_audio_device_settings()`: set sound effects, tone paths, and selected audio device on the controller.
      - `_apply_whisper_settings()`: adjust model, temperature, and speed mode on the controller.
- **Import/Export & Maintenance**
  - `export_json(path)`:
    - Writes all non-binary settings (excluding window geometry/state) to a JSON file, converting values to JSON-serializable representations.
  - `import_json(path, merge=True, overwrite=False)`:
    - Reads settings from a JSON file, validates each via `SETTINGS_SCHEMA`, and applies them using `set()`.
    - Returns a summary dict with `applied`, `invalid`, and `unknown` keys.
  - `restore_defaults()`:
    - Writes schema defaults for all settings keys, syncs, invalidates the cache, and reloads.
  - `clear_all()`:
    - Clears `QSettings`, syncs, and repopulates `_loaded_settings` via `load_all()`.

### Dependencies & Interactions
- Depends on:
  - `core.settings_schema.SETTINGS_SCHEMA` for defaults, validation, and migrations.
  - Qt (`QSettings`, `QByteArray`, `QMainWindow`) for storage and window management.
  - Logging via the standard `logging` module.
- Interacts with:
  - `MainWindow` (UI) for theme, window layout, minimize-to-tray, sound effects, and footer behavior.
  - `SpeechController` for behavior, audio, and Whisper settings.

### Notes / Gotchas
- Any new setting key should be added to `SETTINGS_SCHEMA` before using `get()`/`set()` here, otherwise it will be treated as an untyped value.
- Cache invalidation is **explicit**: always use `set()` (not direct `QSettings` writes) so that `_settings_cache` stays consistent.
- Geometry/state values must remain `QByteArray` instances when restoring; type checks in `restore_window()` guard against invalid or missing values.


