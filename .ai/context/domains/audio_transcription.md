## Domain: Audio & Transcription

### Responsibilities
- Manage **microphone audio capture**, device enumeration/selection, and real-time level monitoring.
- Persist audio safely to sandboxed temp files and feed recordings into the Whisper transcription pipeline.
- Handle **transcription execution**, error classification, retries, and result delivery to the UI and clipboard (auto-paste).

### Key Modules
- `core/audio_manager.py`
  - Cross-platform audio recording using `sounddevice`.
  - Device discovery, consolidation (especially for Windows), and selection.
  - Real-time audio level callbacks for waveform/visual indicators.
  - Thread-safe recording using queues and locks.
  - Sandboxed temp file handling for audio output.
- `speech_controller.py`
  - Owns `AudioManager` and orchestrates recording lifecycle.
  - Coordinates hotkeys, audio, and Whisper model usage.
  - Manages eager model preload on init (QThread), depth-1 audio queue during model load, and background work.
  - Applies error classification and retry policies via `core.transcription_exceptions`.
- `core/transcription_exceptions.py`
  - Defines domain-specific exception types (model loading, audio processing, file I/O, Whisper failures, timeouts).
  - Provides helpers for classification, retry management, and backoff.
- `core/path_validation.py`
  - Provides sandbox and safe temp file helpers used by audio and transcription flows.

### Typical Flow
1. User presses or toggles the global hotkey (or clicks UI controls).
2. `SpeechController` asks `AudioManager` to start recording:
   - Audio stream dispatches frames to a queue.
   - Audio levels are sent to UI callbacks for waveform and indicators.
3. On stop:
   - `AudioManager` stops and flushes frames to a sandboxed WAV file.
   - `SpeechController` checks if the model is ready. If still loading, audio path is queued (depth-1, last wins) and processed when the model finishes.
   - Transcription is executed (Faster-Whisper by default). Device resolved at load time: CUDA → `float16`, CPU → `int8`.
   - Exceptions are classified; retries are applied where appropriate.
   - On success, the transcript is logged, the UI is updated, and auto-paste is performed if enabled.

### Constraints & Notes
- Audio capture must be **non-blocking** and **thread-safe**, keeping the UI responsive.
- Device enumeration and selection should be **robust** against missing/invalid devices, with sensible fallbacks.
- All file paths for audio recording must go through sandbox/path validation helpers.
- Whisper model is preloaded eagerly at startup (QThread), not lazily. The UI is non-blocking because preload runs in a background thread — but the model will be ready sooner than on-demand loading.
- If a recording completes before the model is ready, the audio path is held in a depth-1 slot; a second recording discards the first (last-wins).
- Auto-paste is optional and should respect platform capabilities and user configuration.


