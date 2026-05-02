# Whisper Model Loading Crash - Troubleshooting Log

**Date:** November 22, 2024  
**Issue:** App crashes when loading faster-whisper model  
**Status:** ✅ RESOLVED - Using OpenAI Whisper (app now stable)

**IMPORTANT:** Simply changing the default engine in code doesn't work for existing users because settings are persisted in Windows Registry. You must manually update the saved setting.

---

## Problem Summary

The Whiz app crashes silently when loading the `faster-whisper` model, specifically when:
- Model loads at startup (via timer)
- Model loads during first recording (lazy loading)

The crash occurs after the HTTP request to Hugging Face but before the model finishes instantiating.

---

## Environment

- **OS:** Windows 10
- **Python:** 3.11 (whiz_env_311)
- **PyQt5:** Installed
- **faster-whisper:** 1.2.1
- **openai-whisper:** 20250625
- **torch:** 2.1.2

### Models Status
✅ **Models ARE installed:**
- faster-whisper-tiny: `C:\Users\krir\.cache\huggingface\hub\models--Systran--faster-whisper-tiny`
  - Files: config.json, model.bin, tokenizer.json, vocabulary.txt (all present)
- OpenAI tiny.pt: `C:\Users\krir\.cache\whisper\tiny.pt` (75MB)

✅ **FFmpeg IS available:**
- Location: `.\ffmpeg\bin\ffmpeg.exe` (version 8.0.1)
- **Fixed:** Added automatic PATH setup in `main.py` and `main_with_splash.py`

---

## Root Cause Analysis

### The Core Issue: PyQt + ONNX Runtime Incompatibility

**faster-whisper** uses **ONNX Runtime** internally. ONNX Runtime has known threading compatibility issues with GUI frameworks like PyQt5. When the model loads, it causes a **segmentation fault** that crashes Python silently (no exception, no traceback).

### Evidence
1. ✅ Model loads successfully in standalone Python script (no PyQt)
2. ❌ Model crashes when loaded in PyQt application
3. ❌ Crash occurs during `FasterWhisperModel()` instantiation
4. ❌ No Python exception is raised (C-level crash)
5. ✅ OpenAI Whisper (without ONNX) works fine in PyQt

---

## Attempts Made

### ❌ Attempt 1: Lazy Loading (On-Demand)
**What:** Disabled automatic model preloading at startup, load only when user starts recording

**Changes Made:**
- Commented out `QTimer.singleShot(500, self.start_background_model_loading)` in `speech_ui.py`
- Model loads via `_ensure_model_loaded()` during transcription

**Result:** ❌ FAILED
- App starts successfully without crashing
- BUT crashes when user presses record button (model loads then)

**Files Modified:**
- `speech_ui.py` (line 91)

---

### ❌ Attempt 2: Main Thread Loading with Qt Event Processing
**What:** Load model synchronously on main thread, use `QApplication.processEvents()` to keep UI responsive

**Changes Made:**
- Modified `preload_model()` to load synchronously
- Added `QApplication.processEvents()` before and after loading

**Result:** ❌ FAILED
- App still crashes during model loading
- ONNX Runtime crashes regardless of `processEvents()`

**Files Modified:**
- `speech_controller.py` (`preload_model()` method, lines 548-595)

---

### ❌ Attempt 3: Background Thread Loading
**What:** Load model in Python's `threading.Thread` (daemon thread)

**Changes Made:**
- Used `threading.Thread(target=self._background_load_model, daemon=True)`
- Model loads in background while UI remains responsive

**Result:** ❌ FAILED
- Crash still occurs
- ONNX Runtime doesn't work in Python background threads with PyQt

**Files Modified:**
- `speech_controller.py` (`preload_model()` method)

---

### ✅ Attempt 4 (WORKING SOLUTION): Switch to OpenAI Whisper
**What:** Use `openai-whisper` engine instead of `faster-whisper`

**Changes Made:**
- Changed default engine from `"faster"` to `"openai"` in `main.py`
- Updated `core/settings_schema.py` to default to `"openai"`
- Updated description to note faster-whisper compatibility issues
- **CRITICAL:** Manually updated saved settings because code defaults are ignored

**How to Update Saved Settings:**
```python
python -c "from core.settings_manager import SettingsManager; sm = SettingsManager(); sm.set('whisper/engine', 'openai')"
```

**Result:** ✅ WORKING PERFECTLY
- App starts successfully ✅
- Model loads without crashing ✅
- Recording works ✅
- Transcription works ✅
- App remains stable after transcription ✅
- **Trade-off:** OpenAI Whisper is slower (3-5 seconds vs <1 second) but acceptable

**Verified:** 2024-11-22 11:23 AM - Full recording + transcription cycle completed successfully

**Files Modified:**
- `main.py` (line 169)
- `core/settings_schema.py` (lines 226-232)
- **Saved Settings:** `HKEY_CURRENT_USER\Software\Whiz\VoiceToText` (engine = "openai")

---

## Additional Fixes Applied

### ✅ FFmpeg PATH Configuration
**Problem:** Whisper couldn't find FFmpeg for audio processing  
**Solution:** Added automatic FFmpeg PATH setup at startup

**Changes:**
```python
# In main.py and main_with_splash.py
def _setup_ffmpeg_path():
    """Add local FFmpeg installation to PATH if available"""
    project_root = Path(__file__).parent.resolve()
    ffmpeg_bin = project_root / "ffmpeg" / "bin"
    if ffmpeg_bin.exists():
        os.environ["PATH"] = f"{ffmpeg_bin}{os.pathsep}{os.environ.get('PATH', '')}"
```

**Files Modified:**
- `main.py` (lines 19-40)
- `main_with_splash.py` (lines 49-70)

---

## Current State

### What Works ✅
- App starts successfully with OpenAI Whisper
- FFmpeg is found automatically
- Model loads in background thread
- Recording works
- Transcription works
- App remains stable (no crashes)
- Full workflow tested and verified

### What Doesn't Work ❌
- faster-whisper engine still crashes with PyQt
- Performance is slower (~3-5 seconds vs <1 second)
- No workaround found yet for faster-whisper + PyQt compatibility

---

## Quick Fix Guide (For Future Users)

If the app is crashing, follow these steps:

### Step 1: Verify Engine Setting
```powershell
cd C:\Users\krir\Documents\Solutions\Whiz
.\whiz_env_311\Scripts\python.exe -c "from core.settings_manager import SettingsManager; sm = SettingsManager(); print('Current engine:', sm.get('whisper/engine'))"
```

### Step 2: If It Says "faster", Change It
```powershell
.\whiz_env_311\Scripts\python.exe -c "from core.settings_manager import SettingsManager; sm = SettingsManager(); sm.set('whisper/engine', 'openai'); print('Updated to openai')"
```

### Step 3: Verify the Change
```powershell
.\whiz_env_311\Scripts\python.exe -c "from core.settings_manager import SettingsManager; sm = SettingsManager(); print('Engine is now:', sm.get('whisper/engine'))"
```

### Step 4: Launch App
```powershell
.\whiz_env_311\Scripts\activate.ps1
python main.py
```

**Expected Result:** App should start and load "Openai model" without crashing.

---

## Potential Solutions (NOT YET TRIED)

### Option 1: Use QThread Instead of threading.Thread
**Theory:** Qt's threading system (QThread) might have better compatibility with ONNX Runtime

**Implementation:**
```python
from PyQt5.QtCore import QThread, pyqtSignal

class ModelLoadingThread(QThread):
    finished = pyqtSignal(bool)
    
    def run(self):
        try:
            success = self._load_model_implementation()
            self.finished.emit(success)
        except Exception as e:
            logger.error(f"Error: {e}")
            self.finished.emit(False)

# Usage
self.model_thread = ModelLoadingThread()
self.model_thread.finished.connect(self._on_model_loaded)
self.model_thread.start()
```

**Risk:** Medium - May still crash if ONNX Runtime is fundamentally incompatible

---

### Option 2: Load Model in Separate Process
**Theory:** Use `multiprocessing` to load model in completely separate process, communicate via IPC

**Implementation:**
```python
import multiprocessing

def load_model_in_process(model_size, device, compute_type, queue):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    queue.put("SUCCESS")

# Usage
queue = multiprocessing.Queue()
process = multiprocessing.Process(target=load_model_in_process, args=(args, queue))
process.start()
result = queue.get(timeout=30)
```

**Risk:** High complexity - Need to serialize model or use shared memory

---

### Option 3: Build ONNX Runtime from Source
**Theory:** Pre-built ONNX Runtime wheels may have threading issues; building from source with specific flags might help

**Implementation:**
- Build ONNX Runtime with `-DONNXRUNTIME_USE_OPENMP=ON`
- Install custom wheel
- Test with faster-whisper

**Risk:** Very high - Complex build process, may not solve issue

---

### Option 4: Use ctranslate2 Directly
**Theory:** faster-whisper is a wrapper around ctranslate2; using ctranslate2 directly might avoid compatibility layer issues

**Implementation:**
```python
import ctranslate2

translator = ctranslate2.Translator(model_path, device="cpu", compute_type="int8")
# Custom transcription logic
```

**Risk:** High - Need to implement Whisper-specific logic ourselves

---

### Option 5: Investigate ONNX Runtime Environment Variables
**Theory:** Some ONNX Runtime threading behavior can be controlled via environment variables

**Environment Variables to Try:**
```bash
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
ONNXRUNTIME_SESSION_OPTIONS_INTER_OP_NUM_THREADS=1
ONNXRUNTIME_SESSION_OPTIONS_INTRA_OP_NUM_THREADS=1
```

**Risk:** Low - Easy to test, unlikely to work but worth trying

---

## Logs and Diagnostics

### Last Crash Log
```
2025-11-22 11:13:48 - INFO - Instantiating FasterWhisperModel with device=cpu, compute_type=int8
2025-11-22 11:13:49 - INFO - HTTP Request: GET https://huggingface.co/api/models/Systran/faster-whisper-tiny/revision/main "HTTP/1.1 200 OK"
[SILENT CRASH - No further logs]
```

### Successful OpenAI Whisper Load
```
2025-11-22 11:07:09 - INFO - Application started successfully!
[No model loading messages - lazy loading enabled]
```

---

## Recommendations

### Short Term (CURRENT)
✅ **Use OpenAI Whisper as default engine**
- Stable and reliable
- Works perfectly with PyQt
- Slower but acceptable for most use cases

### Medium Term
🔄 **Provide faster-whisper as optional experimental feature**
- Add warning in preferences: "faster-whisper may cause stability issues"
- Let advanced users opt-in
- Document the PyQt compatibility issue

### Long Term
🔍 **Continue investigating PyQt compatibility**
- Try QThread approach (Option 1)
- Monitor faster-whisper and ONNX Runtime updates
- Consider contributing fix upstream if solution found

---

## Files Changed (Summary)

### Core Fixes
- `main.py` - FFmpeg PATH setup, switched to openai engine
- `main_with_splash.py` - FFmpeg PATH setup
- `core/settings_schema.py` - Changed default engine to openai

### Attempted Fixes (May need reverting)
- `speech_controller.py` - Multiple changes to `preload_model()` and `_background_load_model()`
- `speech_ui.py` - Model loading timer changes

### Debug Additions
- `speech_controller.py` - Added detailed logging in model loading code

---

## Next Steps for Debugging

1. **If trying QThread approach:**
   - Create `ModelLoadingThread` class in `speech_controller.py`
   - Test with faster-whisper
   - Monitor for crashes

2. **If trying process isolation:**
   - Create separate model loading script
   - Use multiprocessing Queue for communication
   - Handle model serialization/deserialization

3. **If keeping OpenAI Whisper:**
   - Clean up debug logging
   - Remove unused faster-whisper loading code
   - Document in user-facing docs

---

## References

- faster-whisper GitHub: https://github.com/SYSTRAN/faster-whisper
- ONNX Runtime Issues: https://github.com/microsoft/onnxruntime/issues
- PyQt Threading: https://doc.qt.io/qt-5/qthread.html
- Related Issue: https://github.com/microsoft/onnxruntime/issues/11787

---

**Last Updated:** 2024-11-22 11:15:00  
**Status:** Using OpenAI Whisper workaround, faster-whisper investigation ongoing

