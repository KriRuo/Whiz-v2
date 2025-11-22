# Whiz Platform Testing Checklist
**Date:** November 22, 2024  
**Status:** ✅ Initial test PASSED

---

## ✅ **Already Verified**

### Test 1: Basic Recording & Transcription
- [x] App launches without crashing
- [x] Audio recording captures data (138 frames, 1.13 MB)
- [x] OpenAI Whisper engine loads successfully
- [x] Transcription completes in ~1 second
- [x] Text recognized: "Make sense to move the faster whisper into a single isolated process."
- [x] Status updates work (Idle → Processing → Idle)

**Result:** ✅ **PASS** - Core functionality working!

---

## 🔄 **Additional Tests to Run**

### Test 2: Short Recording
**Purpose:** Test minimum recording duration handling

**Steps:**
1. Press Alt+Gr
2. Say one word: "Test"
3. Release immediately

**Expected:**
- Recording captures at least 0.5 seconds
- Transcription returns the word
- No errors in logs

**Status:** [ ] Not tested yet

---

### Test 3: Long Recording
**Purpose:** Test extended recording (30+ seconds)

**Steps:**
1. Press and hold Alt+Gr
2. Speak continuously for 30-45 seconds
3. Release Alt+Gr

**Expected:**
- Audio continues capturing throughout
- File size is reasonable (not excessive)
- Transcription completes without timeout
- Full text is captured

**Status:** [ ] Not tested yet

---

### Test 4: No Speech (Silence)
**Purpose:** Test handling of silent recording

**Steps:**
1. Press Alt+Gr
2. Stay silent for 2-3 seconds
3. Release Alt+Gr

**Expected:**
- Recording captures silence
- Transcription may return empty string or "[BLANK_AUDIO]"
- No crash or error
- Status returns to Idle

**Status:** [ ] Not tested yet

---

### Test 5: Background Noise
**Purpose:** Test noise rejection

**Steps:**
1. Play music or have background noise
2. Press Alt+Gr
3. Speak clearly: "This is a test with background noise"
4. Release Alt+Gr

**Expected:**
- Whisper filters out most background noise
- Speech is transcribed accurately
- Background sounds are mostly ignored

**Status:** [ ] Not tested yet

---

### Test 6: Multiple Rapid Recordings
**Purpose:** Test system stability with repeated use

**Steps:**
1. Record 5 short phrases in quick succession:
   - "Test one"
   - "Test two"
   - "Test three"
   - "Test four"
   - "Test five"
2. Wait ~1 second between each

**Expected:**
- All recordings complete successfully
- No memory leaks or slowdowns
- Transcripts appear in order
- System remains stable

**Status:** [ ] Not tested yet

---

### Test 7: Auto-Paste Functionality
**Purpose:** Verify clipboard integration

**Steps:**
1. Open Notepad or any text editor
2. Click in text area to focus
3. Press Alt+Gr, say: "Testing auto paste"
4. Release Alt+Gr

**Expected:**
- Text appears in the focused window
- Cursor advances after paste
- No clipboard conflicts

**Status:** [ ] Not tested yet

---

### Test 8: Different Microphones
**Purpose:** Test device switching

**Steps:**
1. Open Settings in Whiz app
2. Go to Audio tab
3. Select different microphone (e.g., webcam vs. headset)
4. Save and test recording

**Expected:**
- Device switches successfully
- Audio still captures
- Transcription still works
- Setting persists across restarts

**Status:** [ ] Not tested yet

---

### Test 9: Hotkey Change
**Purpose:** Verify hotkey configuration

**Steps:**
1. Open Settings
2. Change hotkey from "Alt+Gr" to "Ctrl+Shift+Space"
3. Save
4. Test with new hotkey

**Expected:**
- New hotkey triggers recording
- Old hotkey no longer works
- Setting persists

**Status:** [ ] Not tested yet

---

### Test 10: Different Languages
**Purpose:** Test multi-language support

**Steps:**
1. Open Settings
2. Change language from "auto" to specific language (e.g., Spanish)
3. Speak in that language
4. Test transcription

**Expected:**
- Transcription uses correct language model
- Accuracy is good for target language
- Setting persists

**Status:** [ ] Not tested yet

---

## 🐛 **Edge Cases to Test**

### Test 11: App While Recording
**Purpose:** Test interruption handling

**Steps:**
1. Start recording (press Alt+Gr)
2. While recording, try to close app window

**Expected:**
- App asks for confirmation OR
- Recording stops gracefully
- No data corruption

**Status:** [ ] Not tested yet

---

### Test 12: Device Disconnect During Recording
**Purpose:** Test hardware failure handling

**Steps:**
1. Start recording
2. Unplug microphone mid-recording
3. Release hotkey

**Expected:**
- Error message appears
- App doesn't crash
- Logs show "device failure"
- App recovers gracefully

**Status:** [ ] Not tested yet

---

### Test 13: Full Disk Scenario
**Purpose:** Test low disk space handling

**Steps:**
1. Check available disk space in temp folder
2. Record several long sessions
3. Monitor disk usage

**Expected:**
- Temp files are cleaned up
- No excessive disk usage
- Warning if disk is full

**Status:** [ ] Not tested yet

---

## 📊 **Performance Testing**

### Test 14: Memory Usage
**Purpose:** Check for memory leaks

**Steps:**
1. Note starting memory usage
2. Perform 20 recordings
3. Check memory again

**Expected:**
- Memory stays under 500 MB
- No significant growth over time
- Temp files are cleaned up

**Status:** [ ] Not tested yet

---

### Test 15: CPU Usage
**Purpose:** Verify efficient resource use

**Steps:**
1. Monitor CPU in Task Manager
2. Perform recordings
3. Note CPU % during idle, recording, and transcription

**Expected:**
- Idle: <5% CPU
- Recording: <10% CPU
- Transcription: 20-40% CPU (normal for Whisper)

**Status:** [ ] Not tested yet

---

## 🔒 **Security Testing**

### Test 16: File Permissions
**Purpose:** Verify sandboxed operation

**Steps:**
1. Check temp file location
2. Verify files are in sandboxed directory
3. Check file permissions

**Expected:**
- Files created in `%LOCALAPPDATA%\Temp\whiz_sandbox_*`
- Proper file permissions
- No files in sensitive locations

**Status:** [ ] Not tested yet

---

## 📝 **Logs and Diagnostics**

### Current Log Analysis
```powershell
# View full recent session
Get-Content "$env:LOCALAPPDATA\Temp\whiz\logs\whiz.log" -Tail 100

# Check for errors
Get-Content "$env:LOCALAPPDATA\Temp\whiz\logs\whiz_errors.log"

# Monitor live
Get-Content "$env:LOCALAPPDATA\Temp\whiz\logs\whiz.log" -Wait
```

---

## 🎯 **Summary**

### ✅ Working (Verified)
- Core recording functionality
- Audio capture (17+ seconds)
- OpenAI Whisper transcription
- WAV file creation and validation
- Status updates
- Single instance enforcement

### 🔄 To Be Tested
- Edge cases (silence, noise, etc.)
- Device switching
- Auto-paste
- Multi-language
- Performance under load
- Error recovery

### 🏆 **Overall Status**
**Primary Functionality:** ✅ **WORKING**  
**Confidence Level:** 🟢 **HIGH**

---

## 📞 **If Issues Occur**

1. **Check logs first:**
   ```powershell
   Get-Content "$env:LOCALAPPDATA\Temp\whiz\logs\whiz_errors.log" -Tail 20
   ```

2. **Verify engine setting:**
   ```powershell
   python -c "from core.settings_manager import SettingsManager; print(SettingsManager().get('whisper/engine'))"
   ```

3. **Re-run diagnostics:**
   ```powershell
   python diagnose_windows_audio.py
   ```

4. **Check Windows permissions:**
   - Settings → Privacy → Microphone → Enabled

---

**Next Steps:** Continue testing using the checklist above, focusing on your most common use cases.


