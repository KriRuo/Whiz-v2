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
python main.py                             # Direct launch (no splash)
python main_with_splash.py                 # With animated splash + mascot

# Tests
python -m pytest tests/ -v                 # Full suite
python -m pytest tests/unit/test_settings_manager.py -v   # Single file
python -m pytest tests/integration/ -v    # Integration only
python -m pytest tests/test_splash_screen.py -v           # Splash screen
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

**Startup (direct):** `main.py` → single-instance check → init logging/settings/SpeechController → create UI → background Whisper model load

**Startup (splash):** `main_with_splash.py` → env vars + ctranslate2 import → single-instance check → show `SplashScreen` (with `LoadingMascotWidget`) → `SpeechController` starts background model load → 250 ms poll loop on `controller.get_model_status()` → on `"loaded"`: dismiss splash → show main window

**Recording → Transcription:** hotkey/UI → `HotkeyManager` → `SpeechController` → `AudioManager` starts stream → frames queued → on stop: audio written to sandboxed temp file → Whisper transcribes → result emitted via Qt signals → UI update + optional auto-paste

**Settings:** all settings defined in `core/settings_schema.py`, accessed via `core/settings_manager.py` (`SettingsManager`). Schema enforces types, ranges, defaults, and migrations. `QSettings` persists to registry (Windows) or config files (Linux/macOS).

**Shutdown:** `CleanupManager` runs ordered phases: UI → audio → hotkeys → model → temp files.

### Threading

Long-running work (model loading, audio processing) runs in worker threads. UI updates always go through Qt signals — never call UI methods directly from a thread. Audio frames are passed through a thread-safe `queue.Queue`.

### Platform notes

Windows gets a custom frameless titlebar (`ui/custom_titlebar.py`) and startup registry integration (`core/windows_startup.py`). Platform detection lives in `core/platform_utils.py`. Platform-specific code is isolated under `core/platform_*` — keep it there.

**Windows DLL import order (critical):** `main.py` sets `OMP_NUM_THREADS=1` and `KMP_DUPLICATE_LIB_OK=TRUE` then imports `ctranslate2` *before* any PyQt5 module. Both libraries ship an OpenMP runtime DLL on Windows; whichever loads first claims the shared allocator. If Qt loads first, `ctranslate2.WhisperModel()` silently segfaults at model-load time. Do not reorder these imports.

## Conventions

**Settings:** Add new keys to `core/settings_schema.py` first, then consume them. Never use raw `QSettings` calls outside `SettingsManager`.

**Logging:** Always use `core.logging_config.get_logger(__name__)`.

**UI layer boundaries:** UI code must not directly call `sounddevice`, `pynput`, or Whisper. Route through `SpeechController` and core managers.

**New UI:** Use `LayoutBuilder`/`LayoutTokens`/`ResponsiveSizing` from `ui/layout_system.py` instead of raw layout math. Styles go in `ui/styles/main_styles.py` or `theme_dark.qss`/`theme_light.qss`.

**Path safety:** All temp file I/O must go through `core/path_validation.py` sandboxing — never write to arbitrary paths.

**Device selection:** Transcription uses `device="auto"` in `TranscriptionConfig`, resolved at model-load time in `core/transcription_service.py`: CUDA → `float16`, CPU → `int8`. The `compute_type` field in the config is overridden by this logic. CUDA failures fall back to CPU silently (logged at WARNING).

**Tests:** Unit tests under `tests/unit/`, integration under `tests/integration/`. Use `tests/conftest.py` fixtures.

**Splash / loading mascot:** `SplashScreen` (`splash_screen.py`) embeds `LoadingMascotWidget` (`ui/widgets/loading_mascot_widget.py`). Stop the mascot by calling `splash.dismiss()` — it fades out and emits `finished`. In `main_with_splash.py` the dismiss is triggered when model load completes; in legacy mode the mascot placeholder is in `ui/record_tab.py` (disabled).

## AI Context Files

The project maintains a structured knowledge base under `.ai/context/`. Load relevant files before any non-trivial task:

- `.ai/context/architecture.md` — layer diagram and key flows
- `.ai/context/conventions.md` — full coding conventions
- `.ai/context/domains/` — domain-specific knowledge (audio, UI, settings, transcription)
- `.ai/context/files/` — per-file summaries
