# Whiz - Voice-to-Text Application

A powerful PyQt-based voice-to-text application with Whisper integration, featuring robust settings persistence, comprehensive preferences UI, and cross-platform compatibility.

## Download & Install

### Windows
- [Download Whiz v1.0.0 Installer](https://github.com/KriRuo/Whiz/releases/download/v1.0.0/Whiz-v1.0.0-Windows-Installer.zip) - Recommended for most users
- [Download Whiz v1.0.0 Standalone](https://github.com/KriRuo/Whiz/releases/download/v1.0.0/Whiz-v1.0.0-Windows-Standalone.exe) - No installation required

### macOS
- [Download Whiz v1.0.0 DMG](https://github.com/KriRuo/Whiz/releases/download/v1.0.0/Whiz-v1.0.0-macOS.dmg) - Drag to Applications folder

### Linux
- [Download Whiz v1.0.0 AppImage](https://github.com/KriRuo/Whiz/releases/download/v1.0.0/Whiz-v1.0.0-Linux.AppImage) - Universal Linux package

### System Requirements
- **Windows**: Windows 10 (1903+) or Windows 11
- **macOS**: macOS 10.15 (Catalina) or later
- **Linux**: Ubuntu 20.04+ or equivalent
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Audio**: Microphone for voice input
- **Network**: Internet connection for initial setup
- **FFmpeg**: Required for audio processing (see installation instructions below)

### Current Status
- ✅ **Windows v1.0.0**: Released and ready for download
- ✅ **macOS v1.0.0**: Released and ready for download
- ✅ **Linux v1.0.0**: Released and ready for download
- ✅ **Cross-platform**: Full support for all major operating systems

---

## Development Setup

This section is for developers who want to run Whiz from source code, contribute to the project, or customize the application.

### Prerequisites

- **Python 3.9+** (Python 3.11 recommended for best performance)
  - Download from [python.org](https://python.org)
  - Verify: `python --version`
- **Git** (for cloning the repository)
- **FFmpeg** (required for audio processing)
  - Windows: Run `install_ffmpeg.bat` (included in project)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg` (Ubuntu/Debian) or equivalent

### Quick Start for Developers

#### 1. Clone the Repository

```bash
git clone https://github.com/KriRuo/Whiz.git
cd Whiz
```

#### 2. Create Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv whiz_env
.\whiz_env\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv whiz_env
source whiz_env/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Important for Windows Developers:**
The `requirements.txt` includes `pywin32>=306` which is **critical** for:
- Single instance management (window activation)
- System tray integration
- Windows-specific features

If you encounter issues with `pywin32`, install it manually:
```powershell
pip install pywin32>=306
```

#### 4. Install FFmpeg (Windows)

```bash
.\install_ffmpeg.bat
```

This installs FFmpeg to the `ffmpeg/` directory in your project.

#### 5. Verify Setup

Run the verification script to ensure everything is configured correctly:

```bash
python scripts/tools/verify_setup.py
```

This will check:
- ✓ Python version compatibility
- ✓ All required dependencies
- ✓ Platform-specific packages (e.g., `pywin32` on Windows)
- ✓ Audio system functionality
- ✓ FFmpeg availability
- ✓ Project file structure

#### 6. Run the Application

**Option A: With splash screen (recommended)**
```bash
python main_with_splash.py
```

**Option B: Direct launch**
```bash
python main.py
```

**Option C: One-click setup and run**
```bash
python scripts/tools/setup_and_run.py
```

This automatically installs dependencies and launches the app.

### Platform-Specific Notes

#### Windows
- **`pywin32` is required** for proper window management and system integration
- **FFmpeg**: Use `install_ffmpeg.bat` for automatic installation
- **Path setup**: Launch scripts automatically add FFmpeg to PATH
- **Virtual environment**: Use PowerShell or CMD, not Git Bash

#### macOS
- Install FFmpeg via Homebrew: `brew install ffmpeg`
- May require accessibility permissions for global hotkeys
- Use Python 3.9+ from python.org (not system Python)

#### Linux
- Install FFmpeg: `sudo apt install ffmpeg` (Ubuntu/Debian)
- Install PortAudio: `sudo apt install portaudio19-dev`
- May need to install Qt dependencies: `sudo apt install libxcb-xinerama0`
- Ensure Python development headers: `sudo apt install python3-dev`

### Troubleshooting Development Setup

#### "win32gui not available" Error (Windows)
**Cause**: `pywin32` package is not installed  
**Fix**: 
```powershell
pip install pywin32>=306
```

#### "Single instance check failed" Error
**Cause**: `pywin32` is missing or not properly installed on Windows  
**Fix**: Reinstall `pywin32` and restart your IDE:
```powershell
pip uninstall pywin32
pip install pywin32>=306
```

#### Import Errors or Missing Packages
**Fix**: Reinstall all dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

#### FFmpeg Not Found
**Windows**: Run `install_ffmpeg.bat`  
**macOS**: `brew install ffmpeg`  
**Linux**: `sudo apt install ffmpeg`

Verify installation:
```bash
ffmpeg -version
```

#### Audio Device Errors
- Check your microphone is connected and not in use by other applications
- On Linux, ensure your user is in the `audio` group
- Run `python scripts/tools/verify_setup.py` to diagnose audio issues

### Development Tools

#### Verify Setup
```bash
python scripts/tools/verify_setup.py
```

Comprehensive check of your development environment.

#### Run Tests
```bash
python -m pytest tests/
```

#### Build for Distribution
See `scripts/build/` for platform-specific build scripts.

---

## Core Files

- `main.py` - Direct application entry point
- `main_with_splash.py` - Application with splash screen and background initialization
- `main_with_splash_fixed.py` - Fixed version with improved error handling
- `speech_ui.py` - PyQt5 GUI interface with custom titlebar and modern styling
- `speech_controller.py` - Core speech processing logic with Whisper integration
- `waveform_widget.py` - Real-time audio waveform visualization with neon effects
- `ui/main_window.py` - Main window management with responsive design
- `ui/custom_titlebar.py` - Custom window titlebar implementation
- `ui/preferences_dialog.py` - Comprehensive settings management UI
- `ui/record_tab.py` - Recording interface with modern components
- `ui/transcripts_tab.py` - Transcript history display with copy confirmation
- `ui/styles/main_styles.py` - Modern Wispr Flow inspired styling
- `ui/components/` - Reusable UI components with consistent design

## Settings & Preferences

The application features a robust settings system with cross-platform persistence, JSON import/export, and comprehensive validation.

### Settings Storage

Settings are automatically stored using QSettings and persist across application restarts:

- **Windows**: Registry (`HKEY_CURRENT_USER\Software\Whiz\VoiceToText`)
- **Linux**: `~/.config/Whiz/VoiceToText.conf`
- **macOS**: `~/Library/Preferences/com.whiz.VoiceToText.plist`

### Available Settings

#### UI Settings
- `ui/theme`: Application theme ("system", "light", "dark")

#### Audio Settings
- `audio/effects_enabled`: Enable start/stop sound effects (true/false)
- `audio/start_tone`: Path to start recording tone file
- `audio/stop_tone`: Path to stop recording tone file
- `audio/input_device`: Audio input device index or None for system default
- `audio/input_device_name`: Device name for display purposes

#### Whisper Settings
- `whisper/model_name`: Whisper model size ("tiny", "base", "small", "medium", "large")
- `whisper/speed_mode`: Enable speed optimizations (true/false)
- `whisper/temperature`: Transcription temperature (0.0-1.0)
- `whisper/language`: Language code or "auto" for auto-detection
- `whisper/engine`: Whisper engine ("faster" [default], "openai")

#### Behavior Settings
- `behavior/auto_paste`: Enable automatic text pasting (true/false)
- `behavior/toggle_mode`: Use toggle mode instead of hold mode (true/false)
- `behavior/visual_indicator`: Show visual recording indicator (true/false)
- `behavior/indicator_position`: Position of visual indicator ("Bottom Center", etc.)
- `behavior/hotkey`: Global hotkey for recording ("alt gr", "F8", etc.)

#### Statistics Settings
- `stats/enabled`: Enable usage statistics (true/false)
- `stats/reset_on_start`: Reset stats on application start (true/false)

#### Window Settings (Automatic)
- `window/geometry`: Window position and size (binary data)
- `window/state`: Window state and layout (binary data)

### Settings Management

Settings are automatically saved when changed and persist across application restarts. The preferences dialog provides a clean interface for managing application settings without the need for manual file editing.

### Preferences UI

Access the preferences dialog through:
- **Settings Tab** → "Open Preferences..." button
- **Organized Tabs**: General, Behavior, Audio, Transcription, and Advanced
- **Live Updates**: Changes apply immediately without restart
- **Validation**: All settings are validated with fallback to defaults
- **Test Functions**: Test audio tones and microphone devices directly from preferences
- **Device Management**: Select microphone device, refresh device list, and test device functionality

**Note**: Behavior settings (auto-paste, clipboard, etc.), hotkey configuration, and transcription settings (language, temperature, Whisper model) are managed directly in the main Settings tab, not in the preferences dialog.

### Default Values

All settings have sensible defaults that ensure the application works out-of-the-box:

```python
DEFAULTS = {
    "ui/theme": "system",
    "audio/effects_enabled": True,
    "audio/start_tone": "assets/sound_start_v9.wav",
    "audio/stop_tone": "assets/sound_end_v9.wav",
    "whisper/model_name": "tiny",  # Fastest model for speed
    "whisper/speed_mode": True,
    "whisper/temperature": 0.0,  # Fastest temperature
    "whisper/language": "auto",  # Auto-detect language
    "whisper/engine": "faster"
}
```

**Note**: The application always starts on the **Record tab** - this is the main functionality and cannot be changed.

## Quick Start

### For New Users (Recommended)

1. **Install Python** (if not already installed)
   - Download from https://python.org
   - **Important**: Check "Add Python to PATH" during installation

2. **Run the Application**
   - Double-click `scripts/launch/launch-whiz.bat` (uses optimized splash screen for fast startup)
   - Or double-click `scripts/launch/launch-whiz-splash.bat` (with minimized console)
   - The setup will handle everything automatically

### For Developers

```bash
# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (Windows - run as administrator)
# Option 1: Use automated installer (recommended)
install_ffmpeg.bat

# Option 2: Manual installation
# Download from https://www.gyan.dev/ffmpeg/builds/
# Extract and add bin folder to system PATH

# Run the application
python main.py
```

### Alternative Launch Methods

- **Silent Launch**: Double-click `scripts/launch/launch-whiz.vbs` (no console window)
- **Splash Screen**: Run `python main_with_splash.py`
- **Manual Setup**: Run `python scripts/tools/setup_and_run.py`
- **Direct Launch**: Run `python main.py`

### Using the Application

1. **Start Recording**: Press the configured hotkey (default: AltGr) or click "Start Recording"
2. **Stop Recording**: Release the hotkey or click "Stop Recording"
3. **View Transcripts**: Switch to the "Transcripts" tab to see your recording history
4. **Copy Transcripts**: Click the copy icon in any transcript bubble to copy text to clipboard
5. **Configure Settings**: Use the "Settings" tab or click "Open Preferences..." for advanced options

### Hotkey Modes

- **Hold Mode** (default): Hold the hotkey while speaking, release to transcribe
- **Toggle Mode**: Press once to start recording, press again to stop

## Features

### Core Functionality
- **Real-time Speech Recognition**: Powered by OpenAI Whisper models
- **Global Hotkey Support**: Works across all applications
- **Live Audio Visualization**: Real-time waveform display
- **Transcript History**: View and manage your recording history
- **Multiple Recording Modes**: Hold-to-record or toggle mode

### Performance Features
- **faster-whisper Engine (Default)**: 5-10x faster transcription than OpenAI Whisper
- **INT8 Quantization**: 50% less memory usage on CPU
- **GPU Acceleration**: Automatic CUDA support when available
- **Intelligent Fallback**: Automatically uses OpenAI Whisper if faster-whisper unavailable
- **Optimized Settings**: Pre-configured for best performance vs. accuracy balance

### Advanced Features
- **Cross-platform Settings**: Persistent settings across Windows, Linux, and macOS
- **JSON Import/Export**: Share settings between machines
- **Theme Support**: Light, dark, and system themes
- **Custom Audio Tones**: Configure start/stop sounds
- **Microphone Device Selection**: Choose specific audio input device with live testing
- **Language Selection**: Support for multiple languages with auto-detection
- **Model Selection**: Choose Whisper model size (tiny to large)
- **Engine Selection**: Choose between OpenAI Whisper and Faster-Whisper engines
- **Temperature Control**: Fine-tune transcription accuracy vs. flexibility
- **Speed Mode**: Optimize for faster processing
- **Visual Indicators**: Optional recording status indicators
- **Toggle Mode**: Alternative to hold-to-record mode

### UI Features
- **Modern Interface**: Clean, professional PyQt5 interface with Wispr Flow inspired design
- **Custom Titlebar**: Frameless window with custom controls and Windows integration
- **Responsive Design**: Adapts to different screen sizes and DPI scaling
- **Neon Waveform**: Real-time audio visualization with neon glow effects
- **Tab-based Interface**: Organized Record and Transcripts tabs
- **Component System**: Reusable UI components with consistent styling
- **Comprehensive Preferences**: Detailed settings management with live updates
- **Copy Confirmation**: Visual feedback when copying transcript text to clipboard

## Requirements

### System Requirements
- **Python 3.9+** (Python 3.11+ recommended for 20-25% better performance)
- **PyQt5**: GUI framework
- **SoundDevice**: Cross-platform audio input/output
- **OpenAI Whisper**: Speech recognition
- **PyNput**: Cross-platform global hotkey support
- **pyautogui**: Auto-paste functionality
- **numpy**: Audio processing

### Installation

```bash
# Clone or download the repository
git clone <repository-url>
cd Whiz

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Dependencies

```txt
PyQt5==5.15.10
openai-whisper>=20231117
faster-whisper>=1.0.3  # Default engine for 5-10x faster transcription
sounddevice>=0.4.7
pynput>=1.7.7
pyautogui>=0.9.54
numpy>=1.24.0,<2.0  # Compatible with PyTorch
psutil>=5.9.8
torch>=2.0.0,<2.2.0  # CPU-only version for compatibility
```

## Testing

The application includes comprehensive unit tests for the settings system:

```bash
# Run all tests
python scripts/tools/run_tests.py

# Or use pytest directly
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/test_settings_manager.py -v
python -m pytest tests/integration/ -v
```

## Troubleshooting

### Common Issues

#### "Python not found"
- Install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation
- Restart your computer after installing Python

#### "Installation failed"
- Check your internet connection
- Try running as administrator
- Run `python scripts/tools/setup_and_run.py` manually

#### "FileNotFoundError: ffmpeg not found" or Transcription Fails
- This means FFmpeg is not installed or not in your system PATH
- **Solution**: Run `install_ffmpeg.bat` in the project root (Windows)
- **Alternative**: Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/ and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (RHEL/CentOS)
- After installation, restart the application

#### Audio Device Not Found
- Ensure your microphone is connected and working
- Check Windows audio settings
- Try running as administrator

#### Hotkey Not Working
- Some hotkeys may conflict with system shortcuts
- Try different hotkey combinations in Preferences
- Ensure the application has focus when testing

#### Whisper Model Download Issues
- Models are downloaded automatically on first use
- Ensure you have internet connectivity
- Check available disk space (models can be large)

#### Settings Not Persisting
- Check file permissions in the settings directory
- On Windows, ensure the application can write to the Registry
- Try running as administrator if needed

### Performance Tips

- **Model Selection**: Use "tiny" or "base" for faster processing, "large" for better accuracy
- **Temperature**: Lower values (0.0-0.3) for more accurate transcriptions
- **Audio Quality**: Use a good quality microphone for better results
- **Background Noise**: Minimize background noise for clearer transcriptions

## Development

### Project Structure

```
Whiz/
├── core/                    # Core functionality
│   ├── settings_manager.py  # Settings persistence
│   ├── settings_schema.py   # Settings validation
│   ├── audio_manager.py     # Audio handling
│   ├── hotkey_manager.py    # Global hotkey support
│   └── ...                  # Other core modules
├── ui/                      # User interface
│   ├── main_window.py       # Main window management
│   ├── record_tab.py        # Recording interface
│   ├── transcripts_tab.py   # Transcript history
│   ├── preferences_dialog.py # Settings UI
│   ├── custom_titlebar.py   # Custom window controls
│   ├── styles/              # Modern styling system
│   │   └── main_styles.py   # Wispr Flow inspired styles
│   └── components/          # Reusable UI components
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── verification/        # Verification scripts
├── scripts/                 # Utility scripts
│   ├── launch/              # Launch scripts (.bat, .ps1, .vbs, .sh)
│   ├── build/               # Build scripts
│   └── tools/               # Utility scripts (test runners, setup, etc.)
├── assets/                  # Resources
│   ├── images/              # Images and icons
│   │   └── icons/           # Application icons
│   └── sounds/              # Audio files
├── docs/                    # Documentation
│   ├── architecture/        # Architecture documentation
│   ├── guides/              # User guides
│   └── release/             # Release notes
├── main.py                  # Direct application entry point
├── main_with_splash.py      # Splash screen version
├── speech_ui.py            # Main GUI
├── speech_controller.py     # Core logic
└── waveform_widget.py      # Audio visualization with neon effects
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document functions and classes
- Write comprehensive tests
