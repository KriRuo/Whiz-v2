## File: `speech_controller.py`

### Purpose
- Central controller for **recording, transcription, and integrations**:
  - Owns `AudioManager` and `HotkeyManager`.
  - Manages Whisper / Faster-Whisper model lifecycle (eager preload on init via QThread, retries).
  - Coordinates UI callbacks (status, recording state, transcripts, audio levels).
  - Registers cleanup tasks for audio, hotkeys, models, and temp files.

### Key Responsibilities & Behavior
- **Initialization**
  - Configures hotkey, model size, auto-paste, language, temperature, and engine (default from `WHISPER_CONFIG`).
  - Detects platform features via `PlatformFeatures` to decide whether audio, hotkeys, and auto-paste are available.
  - Creates `AudioManager` with fixed sample rate/chunk size tuned for Whisper.
  - Allocates sandboxed temp dir + audio path via `get_sandbox` / `create_safe_temp_file`.
  - Registers ordered cleanup tasks with `CleanupManager`.
- **Hotkeys & Recording**
  - Uses `HotkeyManager` with HOLD/TOGGLE mode to call:
    - `start_recording()` → validates feature availability, starts `AudioManager`, updates status and callbacks.
    - `stop_recording()` → stops audio, collects frames, and calls `process_recorded_audio()`.
    - `toggle_recording()` → convenience wrapper used for toggle mode.
- **Model Management**
  - `preload_model()`:
    - Called eagerly in `__init__()`. Spawns a `QThread` (`_ModelLoadThread`) that calls `transcription_service.ensure_model_loaded()`.
    - After model is ready, flushes `_queued_audio_path` if an audio file was captured during load.
  - Audio queuing during load:
    - `_transcribe_audio()` checks `transcription_service.model_loading`; if true, stores the path in `_queued_audio_path` (depth-1 Optional[str] + lock — last recording wins, earlier ones discarded).
    - Once `_ModelLoadThread` finishes, queued path is consumed and transcribed.
- **Transcription**
  - `process_recorded_audio()`:
    - Validates frames and writes a WAV file through `AudioManager.save_audio_to_file`.
    - Ensures file exists, has non-zero size, and has a plausible size range.
    - Ensures the model is loaded, then:
      - Calls Faster-Whisper (`model.transcribe`) or OpenAI Whisper (`model.transcribe`) depending on `engine` and `speed_mode`.
      - Builds text from segments or result dict; handles empty/None cases.
      - Classifies and logs errors (`WhisperError`, `FileIOError`, `ModelLoadingError`, etc.), updating user-facing status.
    - On success:
      - Inserts a new transcript (timestamp + text) at the top of `transcript_log`.
      - Triggers `transcript_callback` if present.
      - Tries auto-paste via `pyautogui.write()` when enabled, swallowing failures.
- **Public Surface (Examples)**
  - `set_status_callback`, `set_recording_state_callback`, `set_transcript_callback`, `set_audio_level_callback`.
  - `set_hotkey`, `register_hotkeys`, `set_toggle_mode`.
  - `set_auto_paste`, `set_language`, `set_temperature`, `set_model`, `set_speed_mode`, `set_visual_indicator`.
  - `get_transcripts()`, `get_feature_status()`.
  - `cleanup()` for ordered resource shutdown.

### Dependencies & Interactions
- Depends heavily on:
  - `core.audio_manager.AudioManager`
  - `core.hotkey_manager.HotkeyManager`
  - `core.platform_features.PlatformFeatures`
  - `core.transcription_exceptions` (retry, classification, custom errors)
  - `core.cleanup_manager` (phased cleanup)
  - `core.config` (timeout, Whisper, audio, memory configs)
  - `core.path_validation` (sandbox + memory checks)
- UI code (e.g., `speech_ui.py`, `ui` components) should **only interact with this file via its public methods and callbacks**, not by calling Whisper/audio APIs directly.

### Notes / Gotchas
- Many operations are **multi-threaded** (audio callback, model loading threads). Always assume callbacks may fire off main thread and route UI updates via Qt-safe callbacks.
- `set_model` currently uses `whisper.load_model` directly, which assumes the OpenAI engine and CPU; keep this in mind if changing engine handling.
- Cleanup logic relies on `CleanupManager` and assumes that multiple cleanup attempts should not crash the app; failures are logged and surfaced via summary.


