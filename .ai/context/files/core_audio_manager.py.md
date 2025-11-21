## File: `core/audio_manager.py`

### Purpose
- Provide a **cross-platform, high-level audio recording interface** for Whiz using `sounddevice`:
  - Device discovery and consolidation (especially for noisy Windows device lists).
  - Safe recording lifecycle management with thread-safe queues and locks.
  - Real-time audio level computation for UI visualization.
  - Sandboxed WAV file writing for recorded audio.

### Key Responsibilities & Behavior
- **Initialization**
  - Configures sample rate, channels, chunk size (default 16kHz mono, 1024 samples).
  - Attempts to reuse a cached device (from a temp-file cache) for faster startup.
  - Discovers all input devices and stores them in `available_devices`.
- **Device Management**
  - `get_devices()` returns raw discovered devices.
  - `get_consolidated_devices()` groups Windows-style duplicate configs by base name:
    - `_extract_base_name()` strips sample-rate, channel, and driver noise from device names.
    - `_select_best_device_config()` / `_score_device_config()` pick the best config per physical device.
    - Returns a display list plus a map from display index to original index.
  - `select_device(device_index)` selects a device (or a heuristically chosen microphone/default when `None`).
  - Optional validation (`device_validation_enabled`) uses:
    - `validate_device_connection()`, `get_fallback_device()`, and `handle_device_failure()` to keep selection resilient.
- **Recording**
  - `start_recording()`:
    - Validates availability and current device (with optional validation/fallback).
    - Clears the recording queue and opens a `sounddevice.InputStream` with `_audio_callback`.
    - Starts the stream and marks `is_recording=True`.
  - `_audio_callback()`:
    - Runs on the audio thread; converts incoming frames to bytes and enqueues them in `recording_frames` (with overflow handling).
    - Computes RMS-based audio level and calls `on_audio_level(level)` when set.
    - Optionally calls `on_audio_data(bytes)` for consumers needing raw frames.
  - `stop_recording()`:
    - Stops/closes the stream, empties the queue into a list of frames, and logs total bytes.
    - Returns the list of byte frames to the caller (e.g., `SpeechController`).
- **Saving Audio**
  - `save_audio_to_file(frames, filename)`:
    - Uses `get_sandbox()` / `create_safe_temp_file()` and the path validator to enforce safe filenames.
    - Converts float32 samples in `frames` to int16 and writes a WAV file at the sandboxed temp path.
    - Copies the temp file to `filename` when possible, logging failures and falling back to the temp path.
- **Status & Utilities**
  - `set_callbacks(on_audio_data, on_audio_level)` to hook into the audio pipeline.
  - `set_device_validation(enabled)`, `get_device_status()`, and `get_status()` for diagnostics.
  - `_get_cached_device()` / `_cache_device()` store and retrieve the last working device across runs.
  - `cleanup()` stops and closes any active stream.

### Dependencies & Interactions
- Used primarily by `speech_controller.SpeechController` for all audio operations.
- Depends on:
  - `sounddevice` for actual audio I/O.
  - `numpy` and `wave` for audio processing and WAV handling.
  - `core.path_validation` sandbox utilities for safe file writes.
  - `core.logging_config.get_logger` for structured logging.

### Notes / Gotchas
- The callback runs in a non-UI thread; any UI updates must go through higher layers (`SpeechController` → Qt).
- Device consolidation and scoring are opinionated; changes can affect how devices appear to users across platforms.
- Recording operates in float32 internally but writes WAV in int16; any changes must maintain this contract or update consumers/tests accordingly.


