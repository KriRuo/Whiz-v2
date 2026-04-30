# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

**Whiz** is a PyQt5 desktop voice-to-text application. It captures audio via global hotkey, transcribes using OpenAI Whisper (faster-whisper by default), and optionally auto-pastes the result. Targets Windows, macOS, and Linux.

## Commands

```bash
# Setup
pip install -r requirements.txt
install_ffmpeg.bat                          # Windows: FFmpeg codec support
python scripts/tools/verify_setup.py       # Verify environment

# Run
python main.py                             # Direct launch
python main_with_splash.py                 # With splash screen

# Tests
python -m pytest tests/ -v                 # Full suite
python -m pytest tests/unit/test_settings_manager.py -v   # Single file
python -m pytest tests/integration/ -v    # Integration only
```

## Architecture

Three layers — UI, Core, Platform:

```
UI Layer      ui/, speech_ui.py, waveform_widget.py
Core Layer    core/, speech_controller.py
Platform      core/platform_*, scripts/
```

**`speech_controller.py`** is the central orchestrator (~50KB). It wires together audio, hotkeys, transcription, settings, and UI signals. Most non-trivial features touch this file.

### Key flows

**Startup:** `main.py` → single-instance check → init logging/settings/SpeechController → create UI → background Whisper model load

**Recording → Transcription:** hotkey/UI → `HotkeyManager` → `SpeechController` → `AudioManager` starts stream → frames queued → on stop: audio written to sandboxed temp file → Whisper transcribes → result emitted via Qt signals → UI update + optional auto-paste

**Settings:** all settings defined in `core/settings_schema.py`, accessed via `core/settings_manager.py` (`SettingsManager`). Schema enforces types, ranges, defaults, and migrations. `QSettings` persists to registry (Windows) or config files (Linux/macOS).

**Shutdown:** `CleanupManager` runs ordered phases: UI → audio → hotkeys → model → temp files.

### Threading

Long-running work (model loading, audio processing) runs in worker threads. UI updates always go through Qt signals — never call UI methods directly from a thread.

## Conventions

**Settings:** Add new keys to `core/settings_schema.py` first, then consume them. Never use raw `QSettings` calls outside `SettingsManager`.

**Logging:** Always use `core.logging_config.get_logger(__name__)`.

**UI layer boundaries:** UI code must not directly call `sounddevice`, `pynput`, or Whisper. Route through `SpeechController` and core managers.

**New UI:** Use `LayoutBuilder`/`LayoutTokens`/`ResponsiveSizing` from `ui/layout_system.py` instead of raw layout math. Styles go in `ui/styles/main_styles.py` or `theme_dark.qss`/`theme_light.qss`.

**Tests:** Unit tests under `tests/unit/`, integration under `tests/integration/`. Use `tests/conftest.py` fixtures.

## Existing Context

The project maintains a structured AI knowledge base under `.ai/context/`. Load relevant files before any non-trivial task:

- `.ai/context/architecture.md` — layer diagram and key flows
- `.ai/context/conventions.md` — full coding conventions
- `.ai/context/domains/` — domain-specific knowledge (audio, UI, settings, transcription)
- `.ai/context/files/` — per-file summaries

If stored context conflicts with actual code, the code wins. Flag the discrepancy rather than silently trusting the context file.
