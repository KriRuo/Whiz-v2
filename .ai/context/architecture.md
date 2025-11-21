## Architecture Overview

### Layers
- **UI Layer (`ui/`, `speech_ui.py`, `waveform_widget.py`)**
  - PyQt5-based interface with a custom main window, record/transcript tabs, preferences dialog, and visual components.
  - Custom titlebar and frameless window behavior on Windows, with system tray integration and DPI-aware layout system.
  - Reusable widgets (`mic` components, gradient tabs, transcript expanders) and centralized styling (`MainStyles`, QSS themes).
- **Core Layer (`core/`, `speech_controller.py`)**
  - `SpeechController` orchestrates hotkeys, audio recording, transcription, settings, and UI updates.
  - `SettingsManager` and `SettingsSchema` provide configuration persistence, validation, defaults, and migration.
  - `AudioManager`, `HotkeyManager`, `SingleInstanceManager`, `CleanupManager`, `PathValidation`/sandbox, logging, and performance monitoring.
- **System & Platform Integration (`core/platform_*`, `scripts/`, installers)**
  - Platform utilities (Windows/macOS/Linux feature detection and behavior).
  - Launch and build scripts, plus platform-specific installers and packaging.
- **External Dependencies**
  - Whisper / Faster-Whisper for transcription.
  - `sounddevice` for audio, `pynput`/keyboard hooks for hotkeys, `pyautogui` for auto-paste, `QSettings` for storage.

### Key Flows

#### Startup
- `main.py`:
  - Performs single-instance check via `core/single_instance_manager.py`.
  - Initializes logging, `SettingsManager`, `SpeechController`, cleanup management, and the main Qt application.
  - Creates the main UI (`SpeechApp`/`MainWindow`), wires signals, applies styles, and triggers background model loading.

#### Recording & Transcription
- **Trigger**: Global hotkey (hold or toggle) or UI control in the Record tab.
- **Flow**:
  - Hotkey → `HotkeyManager` → `SpeechController`.
  - `SpeechController` instructs `AudioManager` to start/stop recording.
  - Audio stream pushes frames into a thread-safe queue; levels are fed to `WaveformWidget` and indicators.
  - On stop: audio is written to a sandboxed temp file; Whisper model is loaded/ensured in the background.
  - Transcription runs (with retries and exception classification) and results are:
    - Stored as transcripts with timestamps.
    - Sent to UI (record tab + transcripts tab).
    - Optionally auto-pasted via `pyautogui`.

#### Settings Management
- `SettingsManager`:
  - Wraps `QSettings` for cross-platform persistence.
  - Uses `SettingsSchema` to provide defaults, validate, and migrate settings.
  - Caches the full settings map for performance and invalidates on changes.
- Flow:
  - UI components (e.g., `PreferencesDialog`, `MainWindow`, tabs) call `load_all()`, `get()`, or `set()`.
  - `SettingsSchema` enforces types, ranges, and enums per key.
  - Settings changes emit signals that `SpeechController` and UI consume to apply new configuration (e.g., hotkey, audio, behavior, Whisper options).

#### UI Composition
- `ui/main_window.py`:
  - Hosts the custom titlebar (Windows only), tab widget, and footer.
  - Manages responsive geometry (screen class, DPI factor), system tray, and settings entry points.
- Tabs:
  - **Record tab**: microphone controls, waveform, tips, visual indicators.
  - **Transcripts tab**: scrollable transcript list with copy actions and timestamps.
  - Preferences dialog: categorized settings, device testing, and live validation.
- Styling:
  - `ui/styles/main_styles.py` provides a central stylesheet with color and layout tokens.
  - Additional QSS files (`theme_dark.qss`, `theme_light.qss`) support alternate themes.

#### Cleanup & Shutdown
- `CleanupManager` coordinates an ordered shutdown:
  - UI/widget cleanup → audio stream tear-down → hotkey unregistration → model and file cleanup.
  - Each phase logs success/failure and attempts to proceed even if non-critical steps fail.
- Single-instance lock file is released, and temporary files are removed via the sandbox/validation layer.

### Cross-Cutting Concerns
- **Logging**
  - Centralized via `core/logging_config.get_logger`, used across core and UI.
- **Path & Security**
  - `core/path_validation.py` and associated sandboxing utilities ensure file operations stay within safe locations, prevent traversal, and sanitize names.
- **Performance**
  - Settings caching, model loading in background threads, and quantized Faster-Whisper models to reduce latency and memory.
  - `core/performance_monitor.py` is available for performance diagnostics.
- **Threading**
  - Long-running work (model loading, audio processing) is offloaded to worker threads.
  - UI updates are dispatched via Qt signals to keep the GUI responsive.


