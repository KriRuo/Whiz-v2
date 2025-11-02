# macOS Testing Guide for Whiz v1.0.0

## 🍎 Testing Instructions for macOS Users

This guide will help you test Whiz on macOS and provide feedback for the upcoming v1.1.0 release.

## 📋 Prerequisites

### System Requirements
- **macOS**: 10.15 (Catalina) or later
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Audio**: Built-in microphone or external microphone
- **Network**: Internet connection for initial setup

### Required Software
- **Python 3.8+**: Download from [python.org](https://python.org) or use Homebrew
- **Git**: For cloning the repository

## 🚀 Setup Instructions

### Step 1: Install Python (if not already installed)

**Option A: Official Python**
```bash
# Download from python.org and install
# Or use the installer from the website
```

**Option B: Homebrew (recommended)**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

### Step 2: Clone the Repository
```bash
# Clone the Whiz repository
git clone https://github.com/yourusername/whiz.git
cd whiz
```

### Step 3: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv whiz_env

# Activate virtual environment
source whiz_env/bin/activate
```

### Step 4: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Step 5: Test the Application
```bash
# Test with splash screen (recommended)
python main_with_splash.py

# Or test direct launch
python main.py
```

## 🧪 Testing Checklist

### Basic Functionality
- [ ] **Application launches** without errors
- [ ] **Splash screen appears** and shows progress
- [ ] **Main window opens** after initialization
- [ ] **Microphone permissions** are requested and granted
- [ ] **Audio device detection** works correctly

### Core Features
- [ ] **Voice recording** starts when hotkey is pressed
- [ ] **Audio waveform** displays during recording
- [ ] **Transcription** works accurately
- [ ] **Auto-paste** pastes text to current application
- [ ] **Settings dialog** opens and functions properly
- [ ] **Hotkey configuration** can be changed

### UI/UX Testing
- [ ] **High DPI scaling** works on Retina displays
- [ ] **Window resizing** works smoothly
- [ ] **Dark/light themes** switch correctly
- [ ] **Splash screen** fades out smoothly
- [ ] **Error handling** shows user-friendly messages

### Performance Testing
- [ ] **Startup time** is reasonable (< 10 seconds)
- [ ] **Memory usage** is acceptable (< 500MB)
- [ ] **CPU usage** is low when idle
- [ ] **Transcription speed** is acceptable
- [ ] **Audio quality** is good

## 🐛 Common Issues & Solutions

### Issue: "Python not found"
**Solution**: Install Python 3.8+ from python.org or use Homebrew

### Issue: "Permission denied" for microphone
**Solution**: 
1. Go to System Preferences > Security & Privacy > Privacy
2. Select "Microphone" from the left sidebar
3. Check the box next to Terminal (or your Python app)
4. Restart the application

### Issue: "Module not found" errors
**Solution**: 
```bash
# Make sure virtual environment is activated
source whiz_env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Audio device not found"
**Solution**:
1. Check microphone is connected and working
2. Go to System Preferences > Sound > Input
3. Select correct microphone
4. Test with Voice Memos app first

### Issue: "Hotkey not working"
**Solution**:
1. Try running as Administrator (if possible)
2. Change hotkey in Settings to avoid conflicts
3. Check if other apps are using the same key combination

## 📊 Performance Benchmarks

### Expected Performance
- **Startup time**: 5-10 seconds
- **Memory usage**: 200-400MB
- **CPU usage**: <5% when idle, 20-40% during transcription
- **Transcription accuracy**: >90% for clear speech
- **Transcription speed**: 2-5x real-time

### Test Scenarios
1. **Short phrases** (1-3 words)
2. **Medium sentences** (10-20 words)
3. **Long paragraphs** (50+ words)
4. **Background noise** (music, TV, etc.)
5. **Different languages** (if applicable)

## 📝 Feedback Form

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

### Performance
- **Startup time**: ___________
- **Memory usage**: ___________
- **Transcription accuracy**: ___________
- **Overall performance**: ___________

### Issues Found
1. **Issue**: ___________
   **Steps to reproduce**: ___________
   **Expected behavior**: ___________
   **Actual behavior**: ___________

2. **Issue**: ___________
   **Steps to reproduce**: ___________
   **Expected behavior**: ___________
   **Actual behavior**: ___________

### Suggestions
- **UI improvements**: ___________
- **Feature requests**: ___________
- **Performance optimizations**: ___________
- **Other feedback**: ___________

## 🔧 Advanced Testing

### Build from Source (Optional)
```bash
# Install PyInstaller
pip install PyInstaller

# Build macOS application
chmod +x build-macos.sh
./build-macos.sh

# Create DMG installer
chmod +x create-dmg-macos.sh
./create-dmg-macos.sh
```

### Test with Different Audio Devices
1. **Built-in microphone**
2. **External USB microphone**
3. **Bluetooth headset**
4. **Audio interface**

### Test with Different Applications
1. **TextEdit** (simple text editor)
2. **Pages** (word processor)
3. **Mail** (email client)
4. **Messages** (chat application)
5. **Terminal** (command line)

## 📞 Support

### Getting Help
- **GitHub Issues**: Report bugs and issues
- **GitHub Discussions**: Ask questions and get help
- **Email**: Contact the development team

### Log Files
If you encounter issues, please include these log files:
- `~/Library/Logs/whiz/whiz.log`
- `~/Library/Logs/whiz/whiz_errors.log`

### Debug Mode
To enable debug logging:
```bash
# Set environment variable
export WHIZ_LOG_LEVEL=DEBUG

# Run application
python main_with_splash.py
```

## 🎯 Testing Goals

### Primary Goals
1. **Verify basic functionality** works on macOS
2. **Identify platform-specific issues**
3. **Test performance** on different hardware
4. **Validate user experience** on macOS

### Secondary Goals
1. **Test edge cases** and error conditions
2. **Verify compatibility** with different macOS versions
3. **Test with various audio devices**
4. **Validate installer** (if built)

## 📋 Next Steps

After testing:
1. **Fill out the feedback form** above
2. **Report any issues** via GitHub Issues
3. **Share performance results** with the team
4. **Suggest improvements** for v1.1.0

---

**Thank you for testing Whiz on macOS!** 🍎✨

Your feedback will help us create a better cross-platform experience for all users.
