# Whiz v1.0.0 Installation Guide

## 📋 System Requirements

### Windows
- **Operating System**: Windows 10 (1903+) or Windows 11
- **Architecture**: x64 (64-bit)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Audio**: Microphone (built-in or external)
- **Network**: Internet connection for initial setup

### macOS (Coming Soon)
- **Operating System**: macOS 10.15 (Catalina) or later
- **Architecture**: x64 or Apple Silicon
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Audio**: Microphone (built-in or external)
- **Network**: Internet connection for initial setup

### Linux (Coming Soon)
- **Operating System**: Ubuntu 20.04+ or equivalent
- **Architecture**: x64 (64-bit)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Audio**: Microphone (built-in or external)
- **Network**: Internet connection for initial setup

## 🚀 Installation Methods

### Method 1: Installer Package (Recommended)

#### Windows
1. **Download** `Whiz-v1.0.0-Windows-Installer.zip`
2. **Extract** the ZIP file to a folder (e.g., `C:\Program Files\Whiz`)
3. **Run** `Whiz.exe` from the extracted folder
4. **Grant** microphone permissions when prompted
5. **Start** using Whiz!

#### macOS (Coming Soon)
1. **Download** `Whiz-v1.0.0-macOS.dmg`
2. **Mount** the DMG file by double-clicking
3. **Drag** Whiz.app to Applications folder
4. **Launch** from Applications or Spotlight
5. **Grant** microphone and accessibility permissions

#### Linux (Coming Soon)
1. **Download** `Whiz-v1.0.0-Linux.AppImage`
2. **Make executable**: `chmod +x Whiz-v1.0.0-Linux.AppImage`
3. **Run**: `./Whiz-v1.0.0-Linux.AppImage`
4. **Grant** microphone permissions when prompted

### Method 2: Standalone Executable

#### Windows
1. **Download** `Whiz-v1.0.0-Windows-Standalone.exe`
2. **Double-click** to run (no installation required)
3. **Grant** microphone permissions when prompted
4. **Start** using Whiz!

**Note**: Standalone executable is portable but doesn't create shortcuts or uninstaller.

## 🔧 First-Time Setup

### 1. Launch Application
- **Windows**: Double-click `Whiz.exe` or use Start Menu shortcut
- **macOS**: Launch from Applications folder or Spotlight
- **Linux**: Run AppImage or executable

### 2. Grant Permissions
- **Microphone**: Required for audio recording
- **Accessibility** (macOS): Required for global hotkeys
- **System Integration** (Linux): May be required for some features

### 3. Initial Configuration
- **Hotkey**: Default is Alt+Gr (Windows) or Cmd+R (macOS)
- **Language**: Auto-detection enabled by default
- **Model**: Tiny model selected for best performance
- **Audio Device**: System default microphone

### 4. Test Recording
1. **Press** the configured hotkey
2. **Speak** clearly into your microphone
3. **Release** the hotkey to stop recording
4. **Verify** transcription appears in your current application

## ⚙️ Configuration

### Settings Dialog
Access settings via:
- **Windows**: Gear icon in titlebar or Settings button
- **macOS**: Settings button in main window
- **Linux**: Settings button in main window

### Key Settings
- **Hotkey**: Change the recording hotkey
- **Language**: Select specific language or auto-detect
- **Model**: Choose Whisper model size (tiny to large)
- **Audio**: Configure input device and effects
- **UI**: Theme and visual preferences

### Advanced Settings
- **Temperature**: Control transcription randomness
- **Speed Mode**: Enable performance optimizations
- **Toggle Mode**: Switch between hold and toggle recording
- **Visual Indicator**: Show recording status overlay

## 🐛 Troubleshooting

### Common Issues

#### "Microphone not detected"
- **Check** microphone is connected and working
- **Verify** system audio settings
- **Restart** application after connecting microphone
- **Test** with system voice recorder first

#### "Permission denied"
- **Windows**: Check microphone privacy settings
- **macOS**: Grant permissions in System Preferences
- **Linux**: Check audio device permissions

#### "Hotkey not working"
- **Check** for conflicts with other applications
- **Try** different hotkey combination
- **Restart** application after changing hotkey
- **Run** as administrator (Windows) if needed

#### "Transcription not working"
- **Check** internet connection (required for model download)
- **Verify** microphone is working
- **Try** different Whisper model
- **Check** language settings

#### "Application crashes"
- **Check** system requirements
- **Update** graphics drivers
- **Disable** antivirus temporarily
- **Check** log files for error details

### Performance Issues

#### "Slow transcription"
- **Use** smaller Whisper model (tiny/base)
- **Enable** speed optimizations
- **Close** other applications
- **Check** available RAM

#### "High CPU usage"
- **Use** smaller Whisper model
- **Disable** visual effects
- **Close** unnecessary applications
- **Check** for background processes

#### "Memory issues"
- **Use** smaller Whisper model
- **Restart** application periodically
- **Check** available system memory
- **Close** other memory-intensive applications

## 🔒 Security Considerations

### File Verification
Always verify downloads using SHA256 checksums:
```bash
# Windows
certutil -hashfile filename SHA256

# macOS/Linux
sha256sum filename
```

### Safe Installation
- **Download** only from official GitHub releases
- **Verify** checksums before installation
- **Scan** with antivirus software
- **Install** in trusted locations

### Privacy
- **Local processing** - audio stays on your device
- **No cloud storage** - transcriptions stored locally
- **No telemetry** - no usage data collected
- **Open source** - code available for review

## 📞 Support

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and get help
- **Documentation**: Check README.md and other guides

### Log Files
Include these log files when reporting issues:
- **Windows**: `%APPDATA%\Whiz\logs\whiz.log`
- **macOS**: `~/Library/Logs/Whiz/whiz.log`
- **Linux**: `~/.local/share/Whiz/logs/whiz.log`

### Debug Mode
Enable debug logging for troubleshooting:
```bash
# Set environment variable
export WHIZ_LOG_LEVEL=DEBUG

# Run application
./Whiz
```

## 🎯 Next Steps

After successful installation:
1. **Read** the Quick Start guide
2. **Configure** your preferred settings
3. **Test** with different applications
4. **Explore** advanced features
5. **Join** the community discussions

---

**Welcome to Whiz!** 🎤✨

Enjoy your new voice-to-text experience!
