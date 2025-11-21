## Project: Whiz Voice-to-Text

### Goal
- Provide a cross-platform, desktop voice-to-text application with a **modern PyQt5 UI**, **global hotkeys**, and **fast, reliable transcription** powered by Whisper (with Faster-Whisper as the default engine).

### High-Level Description
- **Whiz** is a GUI application that:
  - Listens to the microphone on demand (via hotkey or UI controls).
  - Records and buffers audio safely, with real-time waveform visualization and status indicators.
  - Transcribes recordings using Whisper / Faster-Whisper with performance optimizations (caching, quantization, GPU when available).
  - Optionally auto-pastes the transcribed text into the active application.
  - Persists user settings (UI, audio, behavior, Whisper, window state) across sessions using `QSettings`.
  - Runs as a **single-instance** app with proper resource cleanup on shutdown.

### Platforms & Distribution
- **Supported platforms**
  - Windows 10+ and Windows 11
  - macOS 10.15+
  - Linux (AppImage; Ubuntu 20.04+ and equivalents)
- **Distribution**
  - Native installers / bundles per platform (Windows installer, macOS DMG, Linux AppImage).
  - Standalone Windows executable and scripted launchers for development.

### Core Capabilities
- **Recording & Transcription**
  - Hotkey-based start/stop (hold or toggle modes).
  - Device validation and fallback for audio input.
  - Sandboxed temp-file handling for audio recordings.
  - Configurable Whisper engine, model size, language, temperature, and speed mode.
- **User Interface**
  - Custom, frameless titlebar on Windows with system tray integration.
  - Tabbed interface (`Record`, `Transcripts`, settings access).
  - Real-time waveform & visual recording indicator.
  - Preferences dialog with live validation and device testing.
- **Settings System**
  - Central `SettingsManager` backed by `QSettings`.
  - `SettingsSchema` provides defaults, validation, and migration.
  - JSON import/export for sharing settings.
- **Reliability & Safety**
  - Single-instance enforcement with PID-based lock file.
  - Structured cleanup phases for UI, audio, hotkeys, model, and files.
  - Path sandboxing and validation for file operations.
  - Exception classification for transcription, model loading, audio, file I/O, and timeouts.

### Key Entry Points
- `main.py`: standard GUI entry point with single-instance check and core initialization.
- `main_with_splash.py`: entry point with splash screen and background model loading.
- `speech_controller.py`: central orchestrator for audio recording, transcription, and error handling.
- `speech_ui.py` / `ui/main_window.py`: main UI shell and layout.

### Testing & Quality
- Uses **pytest** for unit, integration, and verification tests under `tests/`.
- Core areas under test:
  - Settings persistence and migration.
  - UI layout, DPI scaling, and visual components.
  - Audio behavior and waveform rendering.
  - Single-instance behavior and platform-specific features.
- Recommended commands:
  - `python scripts/tools/run_tests.py`
  - `python -m pytest tests/ -v`


