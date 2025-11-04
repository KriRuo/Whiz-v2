# Platform Support Guide

This document provides detailed information about Whiz's cross-platform compatibility, including installation instructions, known limitations, and troubleshooting tips for each supported platform.

## Supported Platforms

| Platform | Status | Audio | Hotkeys | Auto-paste | Notes |
|----------|--------|-------|---------|------------|-------|
| **Windows 10/11** | ✅ v1.0.0 Released | ✅ | ✅ | ✅ | Full support, standalone executable |
| **macOS 10.15+** | ✅ v1.0.0 Released | ✅ | ✅* | ✅* | Requires accessibility permissions |
| **Linux (Ubuntu/Debian)** | ✅ v1.0.0 Released | ✅ | ✅ | ✅ | AppImage available |
| **Linux (Fedora/RHEL)** | ✅ v1.0.0 Released | ✅ | ✅ | ✅ | Package manager support |
| **Linux (Arch/Manjaro)** | ✅ v1.0.0 Released | ✅ | ✅ | ✅ | AUR packages available |

*Requires user permission setup

## Installation Methods

### Method 1: Developer Installation (Recommended for Friends)

Your friend can clone the repository and install dependencies:

#### Windows
```cmd
# Clone the repository
git clone <repository-url>
cd Whiz

# Run the installer
scripts\tools\install-dependencies.ps1

# Launch the application
scripts\launch\launch-whiz.bat
```

#### macOS
```bash
# Clone the repository
git clone <repository-url>
cd Whiz

# Run the installer and launch
./scripts/tools/install-and-run-macos.sh
```

#### Linux
```bash
# Clone the repository
git clone <repository-url>
cd Whiz

# Run the installer and launch
./scripts/tools/install-and-run-linux.sh
```

### Method 2: Standalone Executable

For end users who don't want to install Python:

#### Windows
- Download the `.exe` file from releases
- Double-click to run (no installation required)

#### macOS
- Download the `.app` bundle from releases
- Drag to Applications folder
- Double-click to run

#### Linux
- Download the `.AppImage` file from releases
- Make executable: `chmod +x Whiz.AppImage`
- Run: `./Whiz.AppImage`

## Platform-Specific Setup

### Windows

#### Requirements
- Windows 10 or later
- Python 3.7+ (if installing from source)
- Microphone access

#### Installation
1. **Python Method**: Run `scripts\launch\launch-whiz.bat`
2. **Executable Method**: Download and run `.exe` file

#### Features
- ✅ Full audio recording support
- ✅ Global hotkeys (no special permissions needed)
- ✅ Auto-paste functionality
- ✅ Custom titlebar with Windows integration
- ✅ System tray support
- ✅ Windows notifications

#### Troubleshooting
- **"Python not found"**: Install Python from python.org, check "Add to PATH"
- **Audio not working**: Check Windows audio settings, microphone permissions
- **Hotkeys not working**: Run as administrator if needed

### macOS

#### Requirements
- macOS 10.15 (Catalina) or later
- Python 3.7+ (if installing from source)
- Microphone access
- Accessibility permissions (for hotkeys)

#### Installation
1. **Python Method**: Run `./scripts/tools/install-and-run-macos.sh`
2. **App Bundle Method**: Download and run `.app` file

#### Permission Setup
**Required for Hotkeys:**
1. Open System Preferences > Security & Privacy > Privacy
2. Select "Accessibility" from the left sidebar
3. Click the lock to make changes
4. Add "Terminal" or "Python" to the list
5. Check the box to enable it

**Required for Microphone:**
1. Open System Preferences > Security & Privacy > Privacy
2. Select "Microphone" from the left sidebar
3. Add "Terminal" or "Python" to the list
4. Check the box to enable it

#### Features
- ✅ Full audio recording support
- ✅ Global hotkeys (with permissions)
- ✅ Auto-paste functionality (with permissions)
- ✅ Native macOS integration
- ✅ Dark mode support
- ✅ Menu bar integration

#### Troubleshooting
- **"Permission denied"**: Enable accessibility permissions
- **Audio not working**: Check microphone permissions in System Preferences
- **Hotkeys not working**: Ensure accessibility permissions are granted

### Linux

#### Requirements
- Python 3.7+
- PortAudio development libraries
- X11 or Wayland display server
- Microphone access

#### Installation by Distribution

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip portaudio19-dev python3-dev
pip3 install --user -r requirements.txt
python3 main.py
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install python3 python3-pip portaudio-devel python3-devel
pip3 install --user -r requirements.txt
python3 main.py
```

**Arch/Manjaro:**
```bash
sudo pacman -S python python-pip portaudio
pip install --user -r requirements.txt
python main.py
```

**openSUSE:**
```bash
sudo zypper install python3 python3-pip portaudio-devel python3-devel
pip3 install --user -r requirements.txt
python3 main.py
```

#### Features
- ✅ Full audio recording support
- ✅ Global hotkeys (X11/Wayland)
- ✅ Auto-paste functionality
- ✅ Desktop environment integration
- ✅ System notifications
- ✅ AppImage support

#### Troubleshooting
- **"No module named sounddevice"**: Install portaudio development libraries
- **"Permission denied"**: Add user to audio group: `sudo usermod -a -G audio $USER`
- **Hotkeys not working**: Ensure X11 or Wayland is running
- **Audio not working**: Check ALSA/PulseAudio configuration

## Feature Compatibility Matrix

### Audio Recording
| Platform | Status | Notes |
|----------|--------|-------|
| Windows | ✅ Full | DirectSound/WASAPI support |
| macOS | ✅ Full | Core Audio support |
| Linux | ✅ Full | ALSA/PulseAudio support |

### Global Hotkeys
| Platform | Status | Requirements |
|----------|--------|--------------|
| Windows | ✅ Full | None |
| macOS | ✅ Full | Accessibility permissions |
| Linux | ✅ Full | X11/Wayland display server |

### Auto-paste
| Platform | Status | Requirements |
|----------|--------|--------------|
| Windows | ✅ Full | None |
| macOS | ✅ Full | Accessibility permissions |
| Linux | ✅ Full | X11/Wayland display server |

### System Integration
| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| Notifications | ✅ | ✅ | ✅* |
| System Tray | ✅ | ⚠️ Menu Bar | ✅* |
| Startup Integration | ✅ | ✅ | ✅* |
| File Associations | ✅ | ✅ | ✅ |

*Depends on desktop environment

## Known Limitations

### Cross-Platform
- **Model Loading**: Whisper models are large (39MB-1.5GB) and require internet on first use
- **Audio Quality**: Depends on system audio drivers and microphone quality
- **Performance**: Transcription speed varies by hardware and model size

### Platform-Specific
- **Windows**: Custom titlebar only works on Windows 10+
- **macOS**: Requires user to grant accessibility permissions manually
- **Linux**: Desktop environment integration varies by distribution

## Troubleshooting

### Common Issues

#### "Module not found" Errors
**Solution**: Install missing dependencies
```bash
# Install system dependencies first
# Then install Python packages
pip install -r requirements.txt
```

#### Audio Not Working
**Windows**: Check Windows audio settings and microphone permissions
**macOS**: Check System Preferences > Security & Privacy > Microphone
**Linux**: Check ALSA/PulseAudio configuration and user permissions

#### Hotkeys Not Working
**Windows**: Try running as administrator
**macOS**: Enable accessibility permissions
**Linux**: Ensure X11/Wayland is running

#### Application Won't Start
**Check Python version**: `python --version` (requires 3.7+)
**Check dependencies**: `pip list` to see installed packages
**Check logs**: Look for error messages in console output

### Getting Help

1. **Check this guide** for platform-specific solutions
2. **Check console output** for error messages
3. **Verify permissions** (especially on macOS)
4. **Test with minimal setup** (disable optional features)
5. **Check system requirements** (Python version, audio drivers)

## Performance Tips

### Model Selection
- **tiny**: Fastest, least accurate (39MB)
- **base**: Good balance (74MB)
- **small**: Better accuracy (244MB)
- **medium**: High accuracy (769MB)
- **large**: Best accuracy (1.5GB)

### Audio Settings
- Use a good quality microphone
- Minimize background noise
- Position microphone close to your mouth
- Use 16kHz sample rate (optimal for Whisper)

### System Optimization
- Close unnecessary applications
- Use SSD storage for faster model loading
- Ensure adequate RAM (4GB+ recommended)
- Use CPU with good single-thread performance

## Contributing

If you encounter platform-specific issues or have improvements:

1. **Test on your platform** with the latest code
2. **Document the issue** with steps to reproduce
3. **Include system information** (OS version, Python version, etc.)
4. **Submit a pull request** with fixes or improvements

## Version History

- **v1.0**: Initial cross-platform release
  - Windows, macOS, Linux support
  - PyAudio → sounddevice migration
  - keyboard → pynput migration
  - Platform-specific UI adaptations
  - Comprehensive error handling
  - Graceful degradation for missing features
