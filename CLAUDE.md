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

## Workflow

Before any non-trivial task, follow this order:

1. **Load context** — read relevant files from `.ai/context/` (architecture, conventions, domain files, per-file summaries)
2. **Plan** — produce a brief impact analysis and proposed steps; pause if assumptions are unclear
3. **Execute** — follow the validated plan; keep changes minimal and targeted
4. **Test** — run `pytest` and verify behavior matches expectations
5. **Update context** — after completing a task, update the relevant `.ai/context/` files (file summaries, domain notes, architecture if meaningfully changed). Never store guesses — only factual, code-verified changes.

For small, isolated changes (single-file bug fixes, styling, utility additions), steps 1 and 5 can be abbreviated but not skipped entirely.

If stored context conflicts with actual code: **the code wins**. Flag the discrepancy rather than silently trusting the context file.

## Architecture

Three layers — UI, Core, Platform:

```
UI Layer      ui/, speech_ui.py (legacy), waveform_widget.py
Core Layer    core/, speech_controller.py
Platform      core/platform_*, scripts/
```

**`speech_controller.py`** is the central orchestrator. It wires together audio, hotkeys, transcription, settings, and UI signals. Most non-trivial features touch this file.

`speech_ui.py` is legacy and being replaced by the modular `ui/` components. Prefer `ui/` for any new UI work.

### Key flows

**Startup:** `main.py` → single-instance check → init logging/settings/SpeechController → create UI → background Whisper model load

**Recording → Transcription:** hotkey/UI → `HotkeyManager` → `SpeechController` → `AudioManager` starts stream → frames queued → on stop: audio written to sandboxed temp file → Whisper transcribes → result emitted via Qt signals → UI update + optional auto-paste

**Settings:** all settings defined in `core/settings_schema.py`, accessed via `core/settings_manager.py` (`SettingsManager`). Schema enforces types, ranges, defaults, and migrations. `QSettings` persists to registry (Windows) or config files (Linux/macOS).

**Shutdown:** `CleanupManager` runs ordered phases: UI → audio → hotkeys → model → temp files.

### Threading

Long-running work (model loading, audio processing) runs in worker threads. UI updates always go through Qt signals — never call UI methods directly from a thread. Audio frames are passed through a thread-safe `queue.Queue`.

### Platform notes

Windows gets a custom frameless titlebar (`ui/custom_titlebar.py`) and startup registry integration (`core/windows_startup.py`). Platform detection lives in `core/platform_utils.py`. Platform-specific code is isolated under `core/platform_*` — keep it there.

## Conventions

**Settings:** Add new keys to `core/settings_schema.py` first, then consume them. Never use raw `QSettings` calls outside `SettingsManager`.

**Logging:** Always use `core.logging_config.get_logger(__name__)`.

**UI layer boundaries:** UI code must not directly call `sounddevice`, `pynput`, or Whisper. Route through `SpeechController` and core managers.

**New UI:** Use `LayoutBuilder`/`LayoutTokens`/`ResponsiveSizing` from `ui/layout_system.py` instead of raw layout math. Styles go in `ui/styles/main_styles.py` or `theme_dark.qss`/`theme_light.qss`.

**Path safety:** All temp file I/O must go through `core/path_validation.py` sandboxing — never write to arbitrary paths.

**Tests:** Unit tests under `tests/unit/`, integration under `tests/integration/`. Use `tests/conftest.py` fixtures.

## AI Context Files

The project maintains a structured knowledge base under `.ai/context/`. Load relevant files before any non-trivial task:

- `.ai/context/architecture.md` — layer diagram and key flows
- `.ai/context/conventions.md` — full coding conventions
- `.ai/context/domains/` — domain-specific knowledge (audio, UI, settings, transcription)
- `.ai/context/files/` — per-file summaries
