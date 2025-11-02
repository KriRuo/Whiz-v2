# Whiz v1.0.0 - Cross-Platform Voice-to-Text Application

## 🎉 First Official Release

Whiz is now available for Windows, macOS, and Linux! This is the first official release of our AI-powered voice-to-text application.

## 📦 Downloads

### Windows
- [Installer](Whiz-v1.0.0-Windows-Installer.zip) - Recommended for most users
- [Standalone Executable](Whiz-v1.0.0-Windows-Standalone.exe) - No installation required

### macOS
- [DMG Installer](Whiz-v1.0.0-macOS.dmg) - Drag to Applications folder

### Linux
- [AppImage](Whiz-v1.0.0-Linux.AppImage) - Universal Linux package

## ✨ Features

- **AI-powered voice transcription** using OpenAI Whisper
- **Global hotkey support** (hold or toggle mode)
- **Auto-paste transcribed text** to any application
- **Multiple Whisper models** (tiny to large)
- **Cross-platform settings persistence**
- **Modern UI with splash screen**
- **Real-time audio visualization**
- **Transcript history**
- **Comprehensive settings management**

## 🔒 Security

Verify downloads using [SHA256 checksums](SHA256-checksums.txt)

## 📋 System Requirements

- **Windows**: Windows 10 (1903+) or Windows 11
- **macOS**: macOS 10.15 (Catalina) or later
- **Linux**: Ubuntu 20.04+ or equivalent
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Audio**: Microphone (built-in or external)

## 🐛 Known Issues

- macOS requires microphone and accessibility permissions
- Linux may require additional audio dependencies
- First run may take longer due to model download

## 📖 Documentation

- [Installation Guide](INSTALLATION_GUIDE.md)
- [Release Notes](RELEASE_NOTES.md)
- [Platform Support](PLATFORM_SUPPORT.md)

## 🚀 Quick Start

1. **Download** the appropriate file for your platform
2. **Install/Run** the application
3. **Grant** microphone permissions when prompted
4. **Press** Alt+Gr (Windows) or Cmd+R (macOS) to start recording
5. **Speak** clearly into your microphone
6. **Release** the hotkey to transcribe and auto-paste

## 🎯 What's New in v1.0.0

### Cross-Platform Support
- ✅ **Windows**: Full support with custom titlebar
- ✅ **macOS**: Native app bundle with proper permissions
- ✅ **Linux**: AppImage for universal compatibility

### Technical Improvements
- **PyAudio → SoundDevice**: Better cross-platform audio support
- **Keyboard → PyNput**: Improved hotkey handling
- **Comprehensive logging**: Better debugging and error tracking
- **Graceful degradation**: App works even with missing dependencies

### User Experience
- **Modern UI**: Wispr Flow inspired design
- **Splash screen**: Professional loading experience
- **Responsive design**: Works on different screen sizes
- **High DPI support**: Crisp display on Retina screens

## 🔧 For Developers

### Building from Source
```bash
# Clone repository
git clone https://github.com/KriRuo/Whiz.git
cd Whiz

# Create virtual environment
python -m venv whiz_env
whiz_env\Scripts\activate  # Windows
# source whiz_env/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Testing
```bash
# Run test suite
python -m pytest tests/ -v

# Run specific tests
python -m pytest tests/test_cross_platform_compatibility.py -v
```

## 📞 Support

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and get help
- **Documentation**: Check README.md and other guides

### Log Files
If you encounter issues, please include these log files:
- **Windows**: `%APPDATA%\Whiz\logs\whiz.log`
- **macOS**: `~/Library/Logs/Whiz/whiz.log`
- **Linux**: `~/.local/share/Whiz/logs/whiz.log`

## 🎯 Roadmap

### v1.1.0 (Planned)
- **Performance improvements**
- **Additional language models**
- **Cloud transcription options**
- **Team collaboration features**

### v1.2.0 (Future)
- **Advanced audio processing**
- **Plugin system**
- **Mobile companion app**
- **Enterprise features**

## 🙏 Acknowledgments

- **OpenAI** for the Whisper AI model
- **PyQt5** team for the GUI framework
- **SoundDevice** contributors for audio support
- **PyNput** developers for input handling
- **All contributors** and testers

---

**Thank you for using Whiz!** 🎤✨

Your feedback helps us create a better voice-to-text experience for everyone.

## 📊 Release Statistics

- **Total Downloads**: [Will be updated after release]
- **Platform Distribution**: [Will be updated after release]
- **User Feedback**: [Will be updated after release]

## 🔄 Update Instructions

### Windows
1. Download the new installer
2. Run the installer (it will update automatically)
3. Restart the application

### macOS
1. Download the new DMG
2. Replace the old app in Applications
3. Restart the application

### Linux
1. Download the new AppImage
2. Replace the old AppImage
3. Restart the application

## 📝 Changelog

### v1.0.0 (2025-01-10)
- **Initial release** for Windows, macOS, and Linux
- **Cross-platform architecture** with platform-specific optimizations
- **Comprehensive logging** and error handling
- **Modern UI** with responsive design
- **Extensive testing** and documentation
- **Professional packaging** with installers and checksums
