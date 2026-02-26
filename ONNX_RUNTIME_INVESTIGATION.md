# ONNX Runtime Compatibility Investigation

## Update (Feb 26, 2026) - Crash Pinpointed to Native DLL Conflict

### What was reproduced

- Full app startup (`main.py`) still fails to initialize faster-whisper worker.
- Worker timeout shows `exitcode=3221225477`, which decodes to `0xC0000005 (ACCESS_VIOLATION)`.
- Isolated worker startup via `TranscriptionService` often succeeds outside full UI context.

### New hard evidence collected

1. Worker stage log in `%TEMP%` (example: `whiz_worker_crash_65792.log`) shows:
   - `before_import_faster_whisper` ✅
   - `after_import_faster_whisper` ✅
   - `before_model_init` ✅
   - no `after_model_init` ❌

   This proves the process crashes inside native code during `WhisperModel(...)` construction.

2. Windows Event Viewer (`Application Error`, Event ID 1000) for the same worker PID (`0x10100` = `65792`) reports:
   - Faulting module: `MSVCP140.dll`
   - Faulting module path: `...\.venv\Lib\site-packages\PyQt5\Qt5\bin\MSVCP140.dll`
   - Exception code: `0xc0000005`

### Interpretation

- This is not a Python exception path.
- The failure is consistent with a native runtime/DLL conflict in the worker process.
- The faulting module path points at PyQt-bundled runtime DLLs being involved when faster-whisper/ctranslate2 initializes.

### Debugging direction (highest value)

1. Capture and inspect WER dump for the failing worker process (Report ID in Event Viewer).
2. Compare loaded DLL order between:
   - successful isolated worker launch
   - failing full app launch
3. Test worker startup with a sanitized `PATH` that excludes `PyQt5\Qt5\bin` entries before model init.

### Practical conclusion right now

- Current architecture already isolates transcription in a subprocess, but inherited native runtime state is still enough to trigger intermittent access violations.
- Root cause focus should move from ONNX version changes to Windows native dependency resolution / runtime DLL collisions.

**Date:** November 22, 2024  
**Finding:** Critical discovery about faster-whisper crashes

---

## Test Results

### Test 1: Standalone Script (No Qt Event Loop)
**ONNX Runtime:** 1.16.3  
**Result:** ✅ **SUCCESS** - Model loads without crash

```
[OK] onnxruntime version: 1.16.3
[OK] PyQt5 imported and QApplication created
[OK] faster-whisper imported successfully
[OK] MODEL LOADED SUCCESSFULLY!
```

### Test 2: Full Application (With Qt Event Loop Running)
**ONNX Runtime:** 1.16.3  
**Result:** ❌ **CRASH** - App still crashes

**Loading Sequence:**
1. App starts, Qt event loop begins (`app.exec_()`)
2. 500ms timer triggers model loading (`QTimer.singleShot`)
3. Model loads in background thread
4. **CRASH** - Silent segmentation fault

---

## Root Cause Analysis

### The Real Problem

**It's not just "ONNX Runtime + PyQt5"**  
**It's "ONNX Runtime + ACTIVE Qt Event Loop"**

| Scenario | Qt Event Loop | ONNX Runtime 1.16.3 | Result |
|----------|---------------|---------------------|--------|
| Standalone script | Not running | Model loads | ✅ Works |
| Full app with timer | Running | Model loads | ❌ Crashes |
| Background thread | Running | Model loads | ❌ Crashes |

### Why Downgrading Didn't Help

- **ONNX Runtime 1.23.2:** Crashes with running event loop ❌
- **ONNX Runtime 1.16.3:** STILL crashes with running event loop ❌

**Conclusion:** The Qt event loop conflict exists in BOTH versions. Version 1.23.2 might have made it worse, but the fundamental incompatibility was always there.

---

## How Did It Work a Month Ago?

### Possible Explanations:

1. **Model loading was disabled/commented out**
   - User may have been testing with lazy loading only
   - First recording would have crashed (or they didn't test it)

2. **Different loading strategy**
   - Model loaded BEFORE Qt event loop started?
   - Used a different isolation mechanism?

3. **Never actually worked in production**
   - Documentation was aspirational
   - Testing was with standalone scripts only

4. **Environment was different**
   - Different Python version?
   - Different PyQt5 version?
   - Running in a different way?

---

## Solutions That DON'T Work

| Attempt | Method | Result |
|---------|--------|--------|
| 1 | Lazy loading (load on first use) | ❌ Crashes on first recording |
| 2 | Main thread with processEvents() | ❌ Still crashes |
| 3 | Background threading.Thread | ❌ Still crashes |
| 4 | Downgrade ONNX Runtime to 1.16.3 | ❌ Still crashes with event loop |

---

## Solutions That MIGHT Work (Untested)

### Option 1: Load Model BEFORE Event Loop Starts ⭐

**Theory:** Load faster-whisper before calling `app.exec_()`

```python
# In main.py, BEFORE window.show() or app.exec_()
if settings.get("whisper/engine") == "faster":
    logger.info("Pre-loading faster-whisper before Qt event loop...")
    controller._load_model_implementation()
    logger.info("Model loaded successfully")

# Then start event loop
app.exec_()
```

**Risk:** Medium - UI will freeze during load, but may work
**Testing:** Easy to test

### Option 2: QThread Instead of threading.Thread

**Theory:** Qt's native threading may have better compatibility

```python
from PyQt5.QtCore import QThread

class ModelLoadingThread(QThread):
    def run(self):
        from faster_whisper import WhisperModel
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
```

**Risk:** Medium - May still crash
**Testing:** Moderate effort

### Option 3: Separate Process with IPC ⭐⭐

**Theory:** Complete isolation from Qt event loop

```python
import multiprocessing
from multiprocessing import Process, Queue

def load_model_in_process(queue):
    from faster_whisper import WhisperModel
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    queue.put("SUCCESS")

# In main app
queue = multiprocessing.Queue()
p = Process(target=load_model_in_process, args=(queue,))
p.start()
result = queue.get(timeout=30)
```

**Risk:** High complexity - Need to keep model in separate process for all transcriptions
**Testing:** High effort

### Option 4: Try Even Older ONNX Runtime

**Theory:** Maybe version 1.15.x or 1.14.x worked better

```bash
pip install onnxruntime==1.15.1
# or
pip install onnxruntime==1.14.1
```

**Risk:** Low - Easy to test
**Testing:** Very easy

---

## Current Recommendation

### Immediate: Revert to OpenAI Whisper ✅

```bash
pip install onnxruntime==1.23.2  # Restore original version
python -c "from core.settings_manager import SettingsManager; sm = SettingsManager(); sm.set('whisper/engine', 'openai')"
```

**Trade-off:** Slower transcription (3-5 seconds vs <1 second) but stable

### Short-term: Test Option 1 (Pre-load Before Event Loop)

This is the most promising solution and easiest to test.

### Long-term: Process Isolation (Option 3)

If performance is critical, implement separate process architecture for faster-whisper.

---

## Next Steps

1. ✅ Restore ONNX Runtime to 1.23.2
2. ✅ Switch engine back to openai
3. ⏭️ Test Option 1: Pre-load model before event loop
4. ⏭️ If Option 1 fails, try Option 4: Test older ONNX versions (1.15.x, 1.14.x)
5. ⏭️ Document final solution

---

**Status:** Investigation complete - Need to test pre-loading strategy

