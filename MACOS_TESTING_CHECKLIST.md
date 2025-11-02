# macOS Testing Checklist for Whiz v1.0.0

## 🍎 Pre-Testing Setup

### System Requirements Check
- [ ] macOS 10.15 (Catalina) or later
- [ ] 4GB RAM minimum (8GB recommended)
- [ ] 2GB free storage space
- [ ] Microphone available (built-in or external)
- [ ] Internet connection for initial setup

### Software Installation
- [ ] Python 3.8+ installed
- [ ] Git installed (for cloning repository)
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)

### Permissions Setup
- [ ] Microphone permissions granted
- [ ] Terminal/Python added to microphone access
- [ ] Accessibility permissions (if needed for hotkeys)

## 🧪 Automated Testing

### Run Test Suite
- [ ] Execute `python -m pytest tests/ -v`
- [ ] All tests pass (196/196)
- [ ] No import errors
- [ ] No deprecation warnings

### Run Testing Script
- [ ] Execute `chmod +x test-macos.sh && ./test-macos.sh`
- [ ] All automated checks pass
- [ ] Test report generated successfully
- [ ] No critical errors found

## 🚀 Manual Testing

### Application Launch
- [ ] **Splash Screen**: `python main_with_splash.py`
  - [ ] Splash screen appears immediately
  - [ ] Progress messages display correctly
  - [ ] Initialization completes successfully
  - [ ] Fade-out animation works smoothly
  - [ ] Main window appears after splash

- [ ] **Direct Launch**: `python main.py`
  - [ ] Application starts without splash
  - [ ] Main window appears directly
  - [ ] No errors during startup

### Core Functionality
- [ ] **Audio Recording**
  - [ ] Recording starts when hotkey pressed
  - [ ] Audio waveform displays during recording
  - [ ] Recording stops when hotkey released
  - [ ] Audio quality is good
  - [ ] No audio dropouts or glitches

- [ ] **Transcription**
  - [ ] Speech is transcribed accurately
  - [ ] Language detection works
  - [ ] Transcription speed is acceptable
  - [ ] No transcription errors or timeouts

- [ ] **Auto-paste**
  - [ ] Transcribed text appears in current application
  - [ ] Works with TextEdit
  - [ ] Works with Pages
  - [ ] Works with Mail
  - [ ] Works with Messages

### User Interface
- [ ] **Main Window**
  - [ ] Window opens and displays correctly
  - [ ] All UI elements are visible
  - [ ] High DPI scaling works on Retina displays
  - [ ] Window resizing works smoothly
  - [ ] Window positioning works correctly

- [ ] **Settings Dialog**
  - [ ] Settings dialog opens from gear icon
  - [ ] All tabs are accessible
  - [ ] Settings can be changed and saved
  - [ ] Changes persist after restart
  - [ ] Default values are correct

- [ ] **Hotkey Configuration**
  - [ ] Hotkey can be changed in settings
  - [ ] New hotkey works immediately
  - [ ] Hotkey conflicts are handled gracefully
  - [ ] Hold mode works correctly
  - [ ] Toggle mode works correctly

### Performance Testing
- [ ] **Startup Performance**
  - [ ] Application starts within 10 seconds
  - [ ] Splash screen shows progress
  - [ ] No hanging or freezing
  - [ ] Memory usage is reasonable (< 500MB)

- [ ] **Runtime Performance**
  - [ ] CPU usage is low when idle (< 5%)
  - [ ] CPU usage during transcription is acceptable (20-40%)
  - [ ] Memory usage remains stable
  - [ ] No memory leaks observed

- [ ] **Transcription Performance**
  - [ ] Short phrases (1-3 words) transcribe correctly
  - [ ] Medium sentences (10-20 words) transcribe correctly
  - [ ] Long paragraphs (50+ words) transcribe correctly
  - [ ] Transcription speed is 2-5x real-time
  - [ ] Accuracy is > 90% for clear speech

## 🔧 Advanced Testing

### Audio Device Testing
- [ ] **Built-in Microphone**
  - [ ] Detected correctly
  - [ ] Recording quality is good
  - [ ] No background noise issues

- [ ] **External USB Microphone**
  - [ ] Detected correctly
  - [ ] Recording quality is good
  - [ ] Device switching works

- [ ] **Bluetooth Headset**
  - [ ] Detected correctly
  - [ ] Recording quality is acceptable
  - [ ] Connection stability is good

### Application Integration
- [ ] **TextEdit Integration**
  - [ ] Auto-paste works correctly
  - [ ] Text formatting is preserved
  - [ ] No application conflicts

- [ ] **Pages Integration**
  - [ ] Auto-paste works correctly
  - [ ] Text formatting is preserved
  - [ ] No application conflicts

- [ ] **Mail Integration**
  - [ ] Auto-paste works correctly
  - [ ] Text appears in compose window
  - [ ] No application conflicts

- [ ] **Messages Integration**
  - [ ] Auto-paste works correctly
  - [ ] Text appears in message field
  - [ ] No application conflicts

### Error Handling
- [ ] **Network Issues**
  - [ ] Graceful handling of no internet
  - [ ] Clear error messages
  - [ ] Application doesn't crash

- [ ] **Audio Issues**
  - [ ] Graceful handling of no microphone
  - [ ] Clear error messages
  - [ ] Application doesn't crash

- [ ] **Permission Issues**
  - [ ] Clear permission requests
  - [ ] Graceful handling of denied permissions
  - [ ] Application doesn't crash

## 🐛 Issue Reporting

### Critical Issues
- [ ] Application crashes on launch
- [ ] Audio recording doesn't work
- [ ] Transcription doesn't work
- [ ] Auto-paste doesn't work
- [ ] Settings don't save

### Minor Issues
- [ ] UI elements misaligned
- [ ] Performance issues
- [ ] Minor transcription errors
- [ ] Cosmetic issues

### Enhancement Requests
- [ ] UI improvements
- [ ] Feature additions
- [ ] Performance optimizations
- [ ] Better error messages

## 📊 Test Results Summary

### System Information
- **macOS Version**: ___________
- **Python Version**: ___________
- **RAM**: ___________
- **Storage**: ___________
- **Microphone**: ___________

### Test Results
- **Launch**: ✅ Pass / ❌ Fail
- **Recording**: ✅ Pass / ❌ Fail
- **Transcription**: ✅ Pass / ❌ Fail
- **Auto-paste**: ✅ Pass / ❌ Fail
- **Settings**: ✅ Pass / ❌ Fail
- **Performance**: ✅ Pass / ❌ Fail

### Performance Metrics
- **Startup time**: ___________
- **Memory usage**: ___________
- **CPU usage (idle)**: ___________
- **CPU usage (recording)**: ___________
- **Transcription accuracy**: ___________
- **Transcription speed**: ___________

### Issues Found
1. **Issue**: ___________
   **Severity**: Critical / Minor / Enhancement
   **Steps to reproduce**: ___________
   **Expected behavior**: ___________
   **Actual behavior**: ___________

2. **Issue**: ___________
   **Severity**: Critical / Minor / Enhancement
   **Steps to reproduce**: ___________
   **Expected behavior**: ___________
   **Actual behavior**: ___________

### Overall Assessment
- **Overall rating**: ⭐⭐⭐⭐⭐ (1-5 stars)
- **Would recommend**: Yes / No
- **Ready for release**: Yes / No
- **Comments**: ___________

## 📝 Next Steps

After completing testing:
1. [ ] Fill out the test results summary above
2. [ ] Report critical issues immediately
3. [ ] Document all issues found
4. [ ] Provide performance feedback
5. [ ] Suggest improvements for v1.1.0

---

**Thank you for testing Whiz on macOS!** 🍎✨

Your feedback is invaluable for creating a better cross-platform experience.
