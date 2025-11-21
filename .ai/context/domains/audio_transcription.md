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
  - Manages lazy model loading, pending transcription queue, and background work.
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
   - `SpeechController` ensures a Whisper model is loaded (lazily, in a background thread).
   - Transcription is executed (Faster-Whisper by default, with engine/model selection from settings).
   - Exceptions are classified; retries are applied where appropriate.
   - On success, the transcript is logged, the UI is updated, and auto-paste is performed if enabled.

### Constraints & Notes
- Audio capture must be **non-blocking** and **thread-safe**, keeping the UI responsive.
- Device enumeration and selection should be **robust** against missing/invalid devices, with sensible fallbacks.
- All file paths for audio recording must go through sandbox/path validation helpers.
- Whisper engines and models may be large and slow to load:
  - Prefer lazy, background initialization.
  - Avoid blocking the UI during model loading.
- Auto-paste is optional and should respect platform capabilities and user configuration.


