# Windows 11 Audio & Transcription System Review

**Date:** November 22, 2024 (Review Update)  
**System:** Windows 11  
**Status:** 🟡 Partially Working (with known limitations)

---

## Executive Summary

The Whiz app does **not** have "speech adapters" as a separate architectural component. Instead, it uses:

1. **AudioManager** (`core/audio_manager.py`) - Handles microphone input via `sounddevice`
2. **SpeechController** (`speech_controller.py`) - Orchestrates recording and transcription
3. **Whisper Engines** - Two implementations with different trade-offs

The system has **4 critical issues** on Windows 11 that impact reliability.

---

## Architecture Components

### 1. AudioManager (Audio Recording Layer)

**Location:** `core/audio_manager.py`  
**Purpose:** Cross-platform audio capture using `sounddevice` library

**Key Features:**
- Device enumeration and consolidation (Windows exposes duplicates)
- Real-time audio level monitoring for UI feedback
- Thread-safe recording with queues
- Automatic fallback to working devices (when enabled)

**Windows-Specific Issues:**

#### ❌ Issue A: Device Validation Disabled
```python
# Line 108 in audio_manager.py
self.device_validation_enabled = False  # Temporarily disable to debug audio issues
```

**Impact:**
- No validation that microphone is connected
- No fallback when device fails
- Recording errors fail silently
- Harder to diagnose actual problems

**Why Disabled:** Comment suggests this was disabled during debugging and never re-enabled.

#### ⚠️ Issue B: Audio Format Inconsistency
```python
# Line 628: Recording uses float32
self.stream = sd.InputStream(
    dtype='float32',  # Try float32 instead of int16
    ...
)

# Lines 860-871: Conversion to int16 for WAV files
audio_data = np.frombuffer(b''.join(frames), dtype=np.float32)
audio_int16 = (audio_data * 32767).astype(np.int16)
```

**Impact:**
- Extra conversion step
- Potential precision loss
- More complex error surface
- Documented concerns about empty frames

#### 📊 Issue C: Empty Frame Detection
The code has extensive logging for empty audio frames, suggesting this is a known problem:

```python
# Lines 720-727
if total_bytes == 0:
    logger.warning("No audio data captured - all frames are empty")
elif total_bytes < 1000:
    logger.warning(f"Very little audio data captured: {total_bytes} bytes")
```

**Root Causes:**
1. Windows microphone privacy settings blocking access
2. Microphone in use by another application
3. Wrong device selected (system default may not be the microphone)
4. Device validation disabled, masking real issues

---

### 2. SpeechController (Orchestration Layer)

**Location:** `speech_controller.py`  
**Purpose:** Coordinates audio recording, model management, and transcription

**Flow:**
1. User triggers hotkey (Alt+Gr by default)
2. `start_recording()` → AudioManager starts capturing
3. Audio frames queued + visual feedback
4. User releases hotkey
5. `stop_recording()` → AudioManager stops, returns frames
6. `process_recorded_audio()` → Save WAV file, transcribe, paste

**Key Methods:**

```python
def process_recorded_audio(self):  # Line 717
    """Process recorded audio through Whisper and optionally paste text"""
    # 1. Validate frames exist
    # 2. Save to WAV file
    # 3. Validate file size
    # 4. Ensure model loaded
    # 5. Transcribe with selected engine
    # 6. Handle errors
    # 7. Update UI and paste text
```

**Windows Issues:**

#### ⚠️ Issue D: File Validation Suggests Reliability Problems
```python
# Lines 752-762: Extensive validation of audio file
file_size = os.path.getsize(self.audio_path)
if file_size == 0:
    logger.error(f"Audio file is empty: {self.audio_path}")
    return

if file_size < 1000:  # Less than 1KB
    logger.warning(f"Audio file seems too small: {file_size} bytes")
```

This suggests the system **has experienced** issues with:
- Empty audio files being created
- Incomplete audio captures
- File system timing issues

---

### 3. Whisper Engines (Transcription Layer)

The app supports **two different Whisper implementations** with vastly different characteristics:

#### Option 1: faster-whisper (ONNX-based)

**Advantages:**
- 5-10x faster transcription
- Lower memory usage
- Better for real-time use

**Critical Issue: PyQt5 Incompatibility** 🚨

```
Status: CRASHES on Windows with PyQt5
Cause:  ONNX Runtime threading conflicts with Qt event loop
Result: Silent segmentation fault (no Python exception)
```

**Evidence from WHISPER_MODEL_CRASH_TROUBLESHOOTING.md:**
```
✅ Works in standalone Python scripts
❌ Crashes in PyQt applications
❌ Crash occurs during FasterWhisperModel() instantiation
❌ No Python exception raised (C-level crash)
```

**Attempted Solutions (All Failed):**
1. ❌ Lazy loading (crashes on first use)
2. ❌ Main thread loading with processEvents()
3. ❌ Background thread loading
4. 🔄 QThread approach (untested)
5. 🔄 Separate process with IPC (untested)

#### Option 2: openai-whisper (PyTorch-based)

**Advantages:**
- ✅ Stable with PyQt5
- ✅ No crashes
- ✅ Well-tested

**Disadvantages:**
- ⏱️ 3-5 seconds per transcription (vs <1 second)
- 📈 Higher memory usage

**Current Recommendation:** Use `openai` engine on Windows

---

## Critical Issue Matrix

| Issue | Severity | Impact | Status | Fix Available |
|-------|----------|--------|--------|---------------|
| faster-whisper crashes | 🔴 HIGH | Can't use fast engine | Known | ✅ Use openai |
| Device validation off | 🟡 MEDIUM | Silent failures | Known | ⚠️ Needs code change |
| Empty audio frames | 🟡 MEDIUM | No transcription | Known | ⚠️ Check permissions |
| Audio format conversion | 🟢 LOW | Complexity | Documented | ✅ Working |

---

## Root Cause Analysis

### Why It's Not Working on Your Windows 11

Based on the code review and documentation, here are the most likely causes:

#### 1. You're Using faster-whisper Engine (Most Likely)
```powershell
# Check current setting
python -c "from core.settings_manager import SettingsManager; print(SettingsManager().get('whisper/engine'))"
```

If this prints `"faster"`, that's your problem. The app will crash when loading the model.

**Fix:**
```powershell
python -c "from core.settings_manager import SettingsManager; sm = SettingsManager(); sm.set('whisper/engine', 'openai')"
```

#### 2. Windows Microphone Privacy Settings
Windows 11 has strict privacy controls that can block microphone access without obvious errors.

**Check:**
1. Settings → Privacy & Security → Microphone
2. Enable "Let apps access your microphone"
3. Enable "Let desktop apps access your microphone"

#### 3. Wrong Audio Device Selected
With device validation disabled, the system may be using the wrong input device.

**Check:**
```python
from core.audio_manager import AudioManager
audio = AudioManager()
devices = audio.get_devices()
for i, d in enumerate(devices):
    print(f"{i}: {d['name']} - {d['channels']} channels")
```

#### 4. Audio Frames Are Empty
Even if recording "works", the frames might contain no actual audio data.

**Symptoms:**
- Recording indicator shows
- Processing happens
- But transcription returns nothing
- Logs show "No audio data captured"

**Causes:**
- Microphone muted in Windows
- Wrong input selected
- Privacy settings blocking
- Device validation disabled (can't detect and switch devices)

---

## Recommended Fixes

### Immediate Fixes (Run These Now)

#### 1. Run Diagnostics
```powershell
cd C:\Users\krir\Documents\Solutions\Whiz
.\whiz_env_311\Scripts\activate.ps1
python diagnose_windows_audio.py
```

This will check:
- Audio device availability
- Whisper engine installation
- FFmpeg configuration
- Current settings
- Microphone permissions
- Actual audio capture

#### 2. Apply Automated Fixes
```powershell
python fix_windows_audio.py
```

This will:
- ✅ Switch to openai-whisper engine
- ✅ Configure optimal settings
- ✅ Test microphone capture
- ✅ Verify FFmpeg
- ✅ Report any remaining issues

#### 3. Manual Verification
```powershell
# Check current engine
python -c "from core.settings_manager import SettingsManager; print('Engine:', SettingsManager().get('whisper/engine'))"

# Should print: Engine: openai
```

### Code-Level Fixes (For Development)

#### Fix 1: Enable Device Validation

**File:** `core/audio_manager.py`  
**Line:** 108

**Change:**
```python
# Before
self.device_validation_enabled = False  # Temporarily disable to debug audio issues

# After  
self.device_validation_enabled = True  # Enable validation for production
```

**Impact:**
- Better error messages
- Automatic fallback to working devices
- Earlier detection of device failures

**Testing Required:**
- Ensure fallback logic works
- No performance impact
- Proper error reporting

#### Fix 2: Use Consistent Audio Format

**File:** `core/audio_manager.py`  
**Line:** 628

**Change:**
```python
# Consider using int16 consistently
self.stream = sd.InputStream(
    samplerate=self.sample_rate,
    channels=self.channels,
    dtype='int16',  # Use int16 directly
    device=self.input_device,
    blocksize=self.chunk_size,
    callback=self._audio_callback
)
```

**Benefits:**
- No conversion needed
- Simpler code path
- Direct WAV file writing

**Risks:**
- May change audio level calculations
- Requires testing waveform visualization

#### Fix 3: Add Microphone Permission Check

**File:** `core/audio_manager.py`  
**New Method:**

```python
def check_microphone_permission(self) -> bool:
    """
    Test if microphone is accessible.
    Returns True if we can capture audio, False otherwise.
    """
    try:
        # Try a very short test recording
        test_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16',
            device=self.input_device,
            blocksize=self.chunk_size
        )
        test_stream.start()
        time.sleep(0.1)
        test_stream.stop()
        test_stream.close()
        return True
    except Exception as e:
        logger.error(f"Microphone permission check failed: {e}")
        return False
```

Call this during initialization to provide early feedback.

---

## Testing Checklist

### After Applying Fixes

- [ ] Run `diagnose_windows_audio.py` - all checks pass
- [ ] Run `fix_windows_audio.py` - all fixes succeed
- [ ] Launch Whiz app - no crashes on startup
- [ ] Wait for model load - status shows "Openai model loaded successfully"
- [ ] Press Alt+Gr - visual indicator appears
- [ ] Speak clearly - waveform shows activity
- [ ] Release Alt+Gr - "Processing..." appears
- [ ] Wait 3-5 seconds - transcription appears
- [ ] Check auto-paste - text appears in active window

### Common Test Failures

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| App crashes on startup | Using faster-whisper | Switch to openai engine |
| No audio captured | Permissions / wrong device | Check Windows settings |
| Transcription empty | Empty audio frames | Verify microphone working |
| Very slow | Wrong model size | Use "tiny" model |
| No auto-paste | PyAutoGUI issues | Check clipboard permissions |

---

## Performance Comparison

### faster-whisper (Not Usable on Windows)
```
Load time:  2-3 seconds
Transcription: <1 second
Memory: ~200 MB
Status: ❌ CRASHES
```

### openai-whisper (Current Workaround)
```
Load time: 10-15 seconds
Transcription: 3-5 seconds
Memory: ~400 MB
Status: ✅ STABLE
```

---

## Long-Term Solutions

### Option A: Fix ONNX Runtime Compatibility
**Effort:** High  
**Success Probability:** Low  
**Approach:**
1. Try QThread instead of threading.Thread
2. Use multiprocessing for model isolation
3. Build ONNX Runtime from source with different flags
4. Wait for upstream fixes

### Option B: Alternative Fast Engine
**Effort:** Medium  
**Success Probability:** Medium  
**Approach:**
1. Use ctranslate2 directly (bypasses faster-whisper wrapper)
2. Implement custom Whisper logic
3. Test PyQt5 compatibility

### Option C: Accept Trade-off
**Effort:** Low (Already Done)  
**Success Probability:** 100%  
**Approach:**
- Use openai-whisper as stable default
- Document performance difference
- Provide faster-whisper as experimental option
- **Current state** ✅

---

## Files Involved

### Core Components
```
core/
├── audio_manager.py          # Audio recording (988 lines)
│   ├── Device enumeration
│   ├── Recording management
│   └── Audio format handling
│
├── transcription_exceptions.py  # Error handling
│   ├── Exception classification
│   ├── Retry logic
│   └── Error recovery
│
└── settings_manager.py       # Persistent configuration
    └── Windows Registry storage

speech_controller.py          # Main orchestration (886 lines)
├── Model management
├── Recording lifecycle
├── Transcription coordination
└── UI callbacks

speech_ui.py                  # PyQt5 interface
└── Visual feedback
```

### Documentation
```
WHISPER_MODEL_CRASH_TROUBLESHOOTING.md  # Detailed crash investigation
CURRENT_STATE_SUMMARY.md                 # Current working state
WINDOWS_11_AUDIO_REVIEW.md               # This file
```

### Diagnostic Tools (New)
```
diagnose_windows_audio.py     # Comprehensive diagnostics
fix_windows_audio.py           # Automated fixes
```

---

## Quick Reference

### Check Current State
```powershell
# Check engine setting
python -c "from core.settings_manager import SettingsManager; print(SettingsManager().get('whisper/engine'))"

# List audio devices
python -c "from core.audio_manager import AudioManager; [print(f'{i}: {d[\"name\"]}') for i, d in enumerate(AudioManager().get_devices())]"

# Check model files
dir $env:USERPROFILE\.cache\whisper
dir $env:USERPROFILE\.cache\huggingface\hub
```

### View Logs
```powershell
# Main log
Get-Content "$env:LOCALAPPDATA\Temp\whiz\logs\whiz.log" -Tail 50

# Error log
Get-Content "$env:LOCALAPPDATA\Temp\whiz\logs\whiz_errors.log" -Tail 30

# Follow live
Get-Content "$env:LOCALAPPDATA\Temp\whiz\logs\whiz.log" -Wait
```

### Emergency Reset
```powershell
# Reset to known-good configuration
python -c "from core.settings_manager import SettingsManager; sm = SettingsManager(); sm.set('whisper/engine', 'openai'); sm.set('whisper/model_name', 'tiny'); sm.set('whisper/temperature', 0.0)"
```

---

## Conclusion

The Whiz app's audio and transcription system has a solid architecture, but Windows 11 introduces specific challenges:

### ✅ What Works
- Audio capture with sounddevice
- OpenAI Whisper transcription
- Device enumeration and selection
- Error handling and retry logic

### ❌ What Doesn't Work
- faster-whisper with PyQt5 (ONNX Runtime conflict)
- Device validation (currently disabled)
- Automatic device failure recovery

### 🔧 Immediate Actions
1. Run `diagnose_windows_audio.py` to identify issues
2. Run `fix_windows_audio.py` to apply automated fixes
3. Verify engine is set to "openai"
4. Check Windows microphone permissions
5. Test end-to-end recording and transcription

### 📋 Next Steps
1. Enable device validation after thorough testing
2. Consider QThread approach for faster-whisper
3. Add microphone permission check at startup
4. Document Windows-specific requirements
5. Create installer that sets optimal defaults

---

**Status:** 🟢 Ready for Testing  
**Recommendation:** Use openai-whisper engine, enable device validation, verify permissions


