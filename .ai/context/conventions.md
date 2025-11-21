## Code & Architecture Conventions

### General
- **Language & Style**
  - Primary implementation language: **Python 3.9+** following **PEP 8**.
  - Use **type hints** where they add clarity, especially in core modules and public interfaces.
  - Prefer **clear, descriptive names** over abbreviations or clever one-liners.
  - Keep functions and methods focused on a single responsibility.
- **Structure**
  - `core/`: core logic, platform integration, settings, audio, hotkeys, cleanup, security.
  - `ui/`: PyQt5 UI components, layout system, widgets, styling.
  - `scripts/`: developer tooling, launchers, build helpers.
  - `docs/`: architecture, guides, and release documentation.

### Settings & Configuration
- Use `core.settings_manager.SettingsManager` as the **single entry point** for application settings.
- Define all settings in `core.settings_schema.SETTINGS_SCHEMA`:
  - Provide defaults, types, ranges/enums, and migration rules.
  - Add new settings to the schema first, then consume them in UI/core code.
- Access patterns:
  - Use `load_all()` when multiple settings are needed at once (benefits from caching).
  - Use `get(key, default)` / `set(key, value)` for individual values, allowing the schema to validate.
- Persist window geometry/state through `SettingsManager` instead of ad-hoc `QSettings` calls.

### UI & Layout
- Build new UI components under `ui/`:
  - Place reusable, generic widgets in `ui/components/` or `ui/widgets/`.
  - Keep page-level composition (tabs, dialogs, main window) in dedicated modules (e.g., `record_tab.py`, `transcripts_tab.py`, `preferences_dialog.py`).
- Styling:
  - Prefer centralized styles via `ui/styles/main_styles.py` and shared color/layout tokens.
  - Use `theme_dark.qss` / `theme_light.qss` for theme-specific overrides instead of duplicating inline styles.
- Layout & responsiveness:
  - Use the layout system (`LayoutBuilder`, `LayoutTokens`, `ResponsiveSizing`, `ResponsiveBreakpoints`, `DPIScalingHelper`) when arranging new UI instead of raw layout math.

### Audio, Hotkeys, and Transcription
- Use `core.audio_manager.AudioManager` for audio recording and device handling.
  - Do not open raw `sounddevice` streams directly from UI code.
- Use `core.hotkey_manager.HotkeyManager` for global hotkey registration and dispatch.
  - Route hotkey callbacks through `SpeechController`, not directly into UI.
- Implement new transcription-related behaviors in or through `SpeechController`:
  - Keep Whisper integration, retry logic, and error classification in the controller / core layer.
  - UI should respond to signals/events, not manipulate transcription internals directly.

### Error Handling & Logging
- Use `core.logging_config.get_logger(__name__)` for loggers.
- For expected failure modes (audio device issues, model loading, file I/O):
  - Prefer specific exception types from `core.transcription_exceptions` or related modules.
  - Log context-rich messages and, when applicable, surface a user-friendly message in the UI.
- Avoid bare `except:`; catch specific exceptions or log and re-raise where debugging is important.

### Testing
- Use **pytest** as the default test runner.
- Place tests under `tests/`:
  - `tests/unit/` for fine-grained, isolated tests of core and UI helpers.
  - `tests/integration/` for end-to-end flows (startup, recording, transcription, settings).
  - `tests/verification/` for targeted verification scripts and regression checks.
- When adding new core logic or a non-trivial UI component:
  - Add or extend tests that cover the new behavior.
  - Prefer testable, side-effect-light functions and methods over large, tightly coupled blocks.

### Tooling & Scripts
- Keep reusable automation scripts in `scripts/tools/` (Python preferred).
- Launch helpers:
  - Use `scripts/launch/` for platform-specific launchers (.bat, .ps1, .vbs, .sh).
  - For new automation on Windows, prefer **PowerShell** (`.ps1`) for maintainability and clarity.
- Build and packaging logic should live under `scripts/build/` or `docs/release/` as appropriate, not scattered in random modules.


