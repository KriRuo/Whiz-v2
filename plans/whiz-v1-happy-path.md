# Plan: Whiz v1 — Fast, Accurate English Voice-to-Text on Windows

> Source PRD: https://github.com/KriRuo/Whiz-v2/issues/9

## Architectural decisions

- **Engine**: faster-whisper only. No openai-whisper fallback.
- **Model resolution rule**: `(model_size, language=en)` → `{model_size}.en` at load time. Exception: `large` has no `.en` variant, stays `large`. All other sizes (tiny, base, small, medium) support `.en`.
- **Device selection rule**: `auto` → `cuda + float16` if `torch.cuda.is_available()`, else `cpu + int8`. Determined once at model load time, not per-transcription.
- **Preload contract**: Model loading begins immediately when `SpeechController` initialises — not on first hotkey press, not behind a timer.
- **Hotkey-while-loading**: A single recording may be queued (depth 1, last wins) while the model loads. It is transcribed automatically once the model is ready.
- **Windows autostart**: Implemented via `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` registry key. Uses a `--tray` CLI flag to distinguish silent-launch from normal launch.
- **Settings keys** (new): `behavior/run_at_startup` (bool, default False).
- **Platform scope**: Windows 10+ only for this plan. No macOS or Linux changes.

---

## Phase 1: UI — Fix button overlap and simplify record tab

**User stories**: 2, 13, 15

### What to build

The Record tab currently shows Start Recording and Stop Recording side-by-side in a fixed horizontal layout, causing them to overlap at the window's natural width. Replace the two-button layout with a single contextual button that changes label and state: shows "Start Recording" when idle and "Stop Recording" when actively recording. This removes the overlap entirely and simplifies the visual hierarchy.

Also audit the record tab for any other padding, spacing, or widget-sizing issues visible at the default window size. The waveform circle and status line at the bottom should have clear vertical breathing room.

### Acceptance criteria

- [ ] Only one button is visible at a time in the Record tab — no overlap at any window size.
- [ ] Button reads "Start Recording" when idle/model-loading; reads "Stop Recording" when actively recording.
- [ ] Button is disabled (greyed out) while the model is loading — not hidden, so the user sees something to wait for.
- [ ] Status line at the bottom (`Idle | Model: Loading...`) is fully visible and not clipped.
- [ ] No regression in hotkey-triggered recording (button state still tracks correctly when hotkey is used instead of the button).

---

## Phase 2: English-only model variant resolution

**User stories**: 7, 8, 11, 22

### What to build

`TranscriptionService` resolves the actual model identifier at load time from `(model_size, language)`. When language is `en`, it appends `.en` to the model name (e.g. `tiny` → `tiny.en`, `base` → `base.en`). `large` stays `large` since no English-only variant exists. For any other language or `auto`, the multilingual model is used unchanged.

The resolved model name is surfaced in the UI footer and in the Preferences dialog so the user can see exactly which model is loaded. The `TranscriptionConfig` exposes a computed `resolved_model_name` property — not a stored field, so it always reflects the current `(model_size, language)` combination.

### Acceptance criteria

- [ ] Setting language to `en` in Preferences causes `tiny.en` (or `base.en` etc.) to load — verifiable in the footer status.
- [ ] Setting language to `auto` loads the multilingual `tiny` model, not `tiny.en`.
- [ ] Selecting `large` model + `en` language loads `large` (not `large.en` which doesn't exist) — no crash.
- [ ] Changing language in Preferences triggers a background model reload; the UI shows "Model loading..." during the swap.
- [ ] Preferences dialog shows the resolved model name (e.g. "tiny.en") not just the size setting.
- [ ] Unit tests cover all resolution cases: `(tiny, en)→tiny.en`, `(large, en)→large`, `(tiny, auto)→tiny`, `(base, fr)→base`.

---

## Phase 3: Eager preload + hotkey-while-loading queue

**User stories**: 1, 2, 13

### What to build

Remove the 500ms `QTimer` delay before model loading. `SpeechController` triggers `TranscriptionService.ensure_model_loaded()` in a background thread immediately during initialisation.

The UI record button (from Phase 1) is disabled with label "Start Recording" while loading. The footer shows `Model: Loading...`. Once loaded, the button enables and the footer shows `Model: Ready`.

If the user presses the hotkey while the model is still loading, the recording is captured and held in a single-slot queue. The moment the model finishes loading, the queued audio is transcribed and auto-pasted as normal. If the user presses the hotkey a second time before the model is ready, the new recording replaces the queued one (depth-1, last wins).

### Acceptance criteria

- [ ] App window is fully interactive within 2 seconds of launch (before model finishes loading).
- [ ] Footer shows `Model: Loading...` immediately on launch, transitions to `Model: Ready` once loaded — no manual refresh needed.
- [ ] Hotkey press during model load starts recording immediately (audio capture begins); transcription queues and fires once ready.
- [ ] A second hotkey press while loading replaces the queued recording — no crash, no duplicate transcription.
- [ ] No regression: normal hotkey + auto-paste flow works identically when model is already loaded.
- [ ] Unit test: `SpeechController` queues a recording while model loads and transcribes it on model-ready signal.

---

## Phase 4: CUDA auto-select and CPU fallback

**User stories**: 9, 10, 12, 23

### What to build

`TranscriptionService` selects device and compute type at model load time based on `torch.cuda.is_available()`:
- CUDA available → `device=cuda`, `compute_type=float16`
- CUDA unavailable → `device=cpu`, `compute_type=int8`

If CUDA is detected but the model fails to load on GPU (e.g. driver mismatch, out-of-memory), the service catches the exception, logs a warning, and retries the load on CPU with `int8` — no crash, no user-visible error beyond a log line.

Active device and compute type are included in `TranscriptionService.get_status()` and shown in Preferences → Whisper section (e.g. "Device: CUDA (float16)" or "Device: CPU (int8)").

### Acceptance criteria

- [ ] On a machine with CUDA, the footer or Preferences shows "Device: CUDA".
- [ ] On a machine without CUDA (or with a broken CUDA install), the app loads on CPU without showing an error dialog.
- [ ] CUDA load failure is logged as a warning, not raised as an exception.
- [ ] Preferences → Whisper section shows active device and compute type.
- [ ] Unit test: mock `torch.cuda.is_available()=True` + `WhisperModel` raising on `cuda` → assert fallback to `cpu`, warning logged, model loaded.
- [ ] Unit test: mock `torch.cuda.is_available()=False` → assert `cpu+int8` selected directly, no fallback attempted.

---

## Phase 5: Windows autostart + silent tray launch

**User stories**: 3, 4, 5, 6, 21

### What to build

A new `WindowsStartupManager` module encapsulates all Windows registry interaction for run-at-startup. It reads/writes `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` to register or deregister Whiz. When registering, it writes the app executable path with a `--tray` flag appended.

`main.py` checks for the `--tray` CLI flag at launch. When present, it skips showing the main window and instead starts the app directly into the system tray, with the model preloading in the background (Phase 3 behaviour). The existing `SystemTrayIcon` is extended with:
- State-aware icon: grey (model loading), green (ready), red (recording).
- Right-click menu: Show Window, Preferences, Quit.

Preferences → Behaviour gains a "Start with Windows" toggle (bound to `behavior/run_at_startup`). Enabling it writes the registry key; disabling it removes it.

### Acceptance criteria

- [ ] Enabling "Start with Windows" in Preferences registers Whiz in the Windows Run key — verifiable in `regedit`.
- [ ] Disabling it removes the key cleanly.
- [ ] Launching with `--tray` shows no main window; tray icon appears with grey (loading) state.
- [ ] Tray icon turns green once model is ready.
- [ ] Tray icon turns red while recording, returns to green after transcription completes.
- [ ] Right-click tray menu: "Show" opens main window, "Preferences" opens preferences dialog, "Quit" exits cleanly.
- [ ] Double-clicking the tray icon shows/raises the main window.
- [ ] Unit test: `WindowsStartupManager.enable()` writes correct registry key (mock `winreg`).
- [ ] Unit test: `WindowsStartupManager.disable()` removes key without error even if key doesn't exist.
- [ ] Unit test: `WindowsStartupManager.is_enabled()` returns correct state from mocked registry.

---

## Phase 6: Windows installer

**User stories**: 16, 17, 18, 19, 20

### What to build

Update the existing Inno Setup `.iss` script to produce a single self-contained `.exe` installer that bundles a Python virtual environment with all dependencies pre-installed. The installer requires no internet connection after download.

The installer:
- Runs a bundled setup that creates the virtual environment and installs all pip dependencies silently.
- Creates a Start Menu shortcut and optionally a desktop shortcut (user choice during install).
- Registers an uninstaller in Windows Settings → Apps so Whiz appears as a normal installed application.
- Includes a `README-INSTALL.md` with plain-language numbered steps (no terminal required, NVIDIA GPU note included).

A GitHub release is created with the installer `.exe` attached and the README linked.

### Acceptance criteria

- [ ] Double-clicking the installer `.exe` installs Whiz with no terminal interaction required.
- [ ] Start Menu shortcut launches Whiz correctly after install.
- [ ] Whiz appears in Windows Settings → Apps and can be uninstalled cleanly (no orphaned files or registry entries beyond the user's `AppData` config).
- [ ] The installer works on a clean Windows 10 machine with no Python pre-installed.
- [ ] `README-INSTALL.md` is included in the installer directory and covers: download, install, first run, NVIDIA GPU note, and how to uninstall.
- [ ] GitHub release has the `.exe` and `README-INSTALL.md` attached.
