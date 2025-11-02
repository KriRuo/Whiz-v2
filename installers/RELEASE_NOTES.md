# Whiz v1.0.0 Release Notes

## 🎉 First Official Release

Whiz is now available for Windows! This is the first official release of our AI-powered voice-to-text application.

## ✨ Features

### Core Functionality
- **AI-powered voice transcription** using OpenAI Whisper
- **Global hotkey support** (hold or toggle mode)
- **Auto-paste transcribed text** to any application
- **Multiple Whisper models** (tiny to large)
- **Cross-platform settings persistence**
- **Modern UI with splash screen**

### User Interface
- **Custom titlebar** (Windows only)
- **Responsive design** with high DPI support
- **Dark/light theme support**
- **Splash screen** with loading progress
- **Settings dialog** with comprehensive options

### Audio Features
- **Real-time audio recording**
- **Visual waveform display**
- **Audio effects** (start/stop sounds)
- **Multiple audio device support**
- **Background noise filtering**

## 🔧 Technical Details

### System Requirements
- **Windows**: Windows 10 (1903+) or Windows 11
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Audio**: Microphone (built-in or external)
- **Network**: Internet connection for initial setup

### Dependencies
- **PyQt5**: Modern GUI framework
- **OpenAI Whisper**: AI transcription engine
- **SoundDevice**: Cross-platform audio I/O
- **PyNput**: Cross-platform input handling
- **NumPy**: Numerical computing

## 🚀 Installation

### Windows
1. **Installer** (Recommended): Download `Whiz-v1.0.0-Windows-Installer.zip`
   - Extract to desired location
   - Run `Whiz.exe`
   - Grant microphone permissions

2. **Standalone**: Download `Whiz-v1.0.0-Windows-Standalone.exe`
   - No installation required
   - Double-click to run
   - Grant microphone permissions

### macOS (Coming Soon)
- Download `Whiz-v1.0.0-macOS.dmg`
- Mount DMG and drag to Applications
- Grant microphone and accessibility permissions

### Linux (Coming Soon)
- Download `Whiz-v1.0.0-Linux.AppImage`
- Make executable: `chmod +x Whiz-v1.0.0-Linux.AppImage`
- Run: `./Whiz-v1.0.0-Linux.AppImage`

## 🎯 Usage

### Basic Usage
1. **Launch Whiz** from desktop or start menu
2. **Grant permissions** when prompted
3. **Press Alt+Gr** (or configured hotkey) to start recording
4. **Speak clearly** into your microphone
5. **Release hotkey** to stop and transcribe
6. **Text appears** in your current application

### Advanced Features
- **Toggle Mode**: Press once to start, press again to stop
- **Visual Indicator**: Shows recording status on screen
- **Settings**: Configure hotkeys, models, and preferences
- **Transcript History**: View past transcriptions
- **Multiple Languages**: Support for 20+ languages

## 🐛 Known Issues

### Windows
- **Custom titlebar** may not work on some older Windows versions
- **High DPI scaling** requires Windows 10 1703+
- **Audio device switching** may require restart

### General
- **First run** may take longer due to model download
- **Background noise** can affect transcription accuracy
- **Network required** for initial Whisper model download

## 🔒 Security

### Verification
- **SHA256 checksums** provided for all downloads
- **Code signing** (planned for future releases)
- **Open source** code available on GitHub

### Privacy
- **Local processing** - audio stays on your device
- **No cloud storage** - transcriptions stored locally
- **No telemetry** - no usage data collected

## 📋 Changelog

### v1.0.0 (2025-01-10)
- **Initial release** for Windows
- **Cross-platform architecture** ready for macOS/Linux
- **Comprehensive logging** and error handling
- **Modern UI** with responsive design
- **Extensive testing** and documentation

## 🛠️ Development

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

### Contributing
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Pull Requests**: Submit improvements and fixes

## 📞 Support

### Getting Help
- **GitHub Issues**: https://github.com/KriRuo/Whiz/issues
- **GitHub Discussions**: https://github.com/KriRuo/Whiz/discussions
- **Documentation**: See README.md and QUICK_START.md

### Log Files
If you encounter issues, please include these log files:
- **Windows**: `%APPDATA%\Whiz\logs\whiz.log`
- **macOS**: `~/Library/Logs/Whiz/whiz.log`
- **Linux**: `~/.local/share/Whiz/logs/whiz.log`

## 🎯 Roadmap

### v1.1.0 (Planned)
- **macOS support** with native app bundle
- **Linux support** with AppImage
- **Code signing** for all platforms
- **Performance improvements**
- **Additional language models**

### v1.2.0 (Future)
- **Cloud transcription** options
- **Team collaboration** features
- **Advanced audio processing**
- **Plugin system**

## 🙏 Acknowledgments

- **OpenAI** for the Whisper AI model
- **PyQt5** team for the GUI framework
- **SoundDevice** contributors for audio support
- **PyNput** developers for input handling
- **All contributors** and testers

---

**Thank you for using Whiz!** 🎤✨

Your feedback helps us create a better voice-to-text experience for everyone.
