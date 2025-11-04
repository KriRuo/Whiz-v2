# Distribution Guide

This guide covers how to package and distribute Whiz Voice-to-Text Application across different platforms.

## Distribution Methods

### 1. Source Code Distribution (Developer-Friendly)

**Best for**: Developers, contributors, users who want to modify the code

**Pros**:
- Full source code access
- Easy to modify and extend
- No additional packaging overhead
- Works on any platform with Python

**Cons**:
- Requires Python installation
- Requires dependency management
- More complex setup for end users

**Files to include**:
- `main.py` - Application entry point
- `requirements.txt` - Python dependencies
- `core/` - Core application modules
- `ui/` - User interface components
- `assets/` - Application assets (sounds, icons)
- `scripts/tools/install-and-run-*.sh` - Platform-specific installers
- `scripts/launch/launch-whiz.bat` - Windows launcher
- `README.md` - Basic instructions
- `docs/release/PLATFORM_SUPPORT.md` - Detailed platform guide

### 2. Standalone Executable (End-User Friendly)

**Best for**: End users who don't want to install Python

**Pros**:
- No Python installation required
- Single file distribution
- Easy to run (double-click)
- Includes all dependencies

**Cons**:
- Larger file size
- Platform-specific builds required
- More complex build process

## Building Executables

### Current Status ✅
- **Windows Build**: SUCCESSFUL (303MB executable)
- **macOS Build**: Ready for testing (requires macOS system)
- **Linux Build**: Ready for testing (requires Linux system)
- **Executable Location**: `dist\Whiz.exe` (Windows), `dist\Whiz.app` (macOS), `dist\Whiz` (Linux)
- **Build Date**: January 10, 2025
- **Status**: Windows tested and working, macOS/Linux builds ready

### Prerequisites

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Install platform-specific dependencies**:
   - **Windows**: No additional requirements
   - **macOS**: Xcode command line tools
   - **Linux**: Build essentials, Python development headers

### Build Process

#### Automated Build (Recommended)

Use the provided build script:

```bash
python scripts/build/build-executable.py
```

This script will:
- Check for PyInstaller installation
- Clean previous builds
- Build the executable using `whiz.spec`
- Create platform-specific launchers
- Report build status and file sizes

#### Manual Build

1. **Windows**:
   ```cmd
   pyinstaller whiz.spec
   ```

2. **macOS**:
   ```bash
   pyinstaller whiz.spec
   ```

3. **Linux**:
   ```bash
   pyinstaller whiz.spec
   ```

### Build Configuration

The `whiz.spec` file contains PyInstaller configuration:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('ui', 'ui'),
        ('core', 'core'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
        'sounddevice',
        'pynput',
        'whisper',
        'pyautogui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Whiz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='speech_to_text_icon_transparent.ico'  # Windows only
)
```

### Platform-Specific Build Notes

#### Windows

**Output**: `dist/Whiz.exe`

**Features**:
- Single executable file
- Windows icon and version info
- No console window (GUI only)
- UPX compression enabled

**Requirements**:
- Windows 10 or later
- 64-bit architecture

**Testing**:
- Test on clean Windows VM
- Verify all features work
- Check antivirus compatibility

#### macOS

**Output**: `dist/Whiz.app`

**Features**:
- macOS application bundle
- Proper Info.plist configuration
- Code signing support (optional)

**Requirements**:
- macOS 10.15 or later
- Xcode command line tools

**Code Signing** (Optional):
```bash
# Sign the application
codesign --force --deep --sign "Developer ID Application: Your Name" dist/Whiz.app

# Verify signature
codesign --verify --verbose dist/Whiz.app
```

**Notarization** (Optional):
```bash
# Create DMG
hdiutil create -volname "Whiz" -srcfolder dist/Whiz.app -ov -format UDZO dist/Whiz.dmg

# Notarize DMG
xcrun notarytool submit dist/Whiz.dmg --keychain-profile "notarytool-profile" --wait
```

#### Linux

**Output**: `dist/whiz`

**Features**:
- Standalone executable
- AppImage support (optional)
- Desktop entry file

**Requirements**:
- Linux with glibc 2.17+
- X11 or Wayland

**AppImage Creation** (Optional):
```bash
# Download AppImageTool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Create AppImage
./appimagetool-x86_64.AppImage dist/Whiz.AppImage
```

## Distribution Channels

### 1. GitHub Releases

**Best for**: Open source projects, version control

**Steps**:
1. Create a release tag: `git tag v1.0.0`
2. Push tag: `git push origin v1.0.0`
3. Create GitHub release
4. Upload platform-specific files
5. Add release notes

**File naming convention**:
- `Whiz-v1.0.0-Windows.exe`
- `Whiz-v1.0.0-macOS.dmg`
- `Whiz-v1.0.0-Linux.AppImage`

### 2. Direct Download

**Best for**: Simple distribution, internal use

**Steps**:
1. Host files on web server
2. Provide download links
3. Include installation instructions
4. Monitor download statistics

### 3. Package Managers

#### Windows (Chocolatey)
```powershell
# Create package
choco pack whiz.nuspec

# Install package
choco install whiz -s .
```

#### macOS (Homebrew)
```bash
# Create formula
brew create https://github.com/user/whiz/releases/download/v1.0.0/Whiz-v1.0.0-macOS.dmg

# Install package
brew install whiz
```

#### Linux (Snap)
```yaml
# snapcraft.yaml
name: whiz
version: '1.0.0'
summary: Voice-to-Text Application
description: |
  Whiz is a cross-platform voice-to-text application
  using Whisper AI for accurate transcription.

grade: stable
confinement: strict

parts:
  whiz:
    plugin: dump
    source: dist/
    stage:
      - whiz

apps:
  whiz:
    command: whiz
    plugs:
      - audio-playback
      - audio-record
      - desktop
```

### 4. App Stores

#### Microsoft Store (Windows)
- Package as MSIX
- Submit through Partner Center
- Automatic updates
- Windows integration

#### Mac App Store (macOS)
- Package as .app bundle
- Submit through App Store Connect
- Sandboxed environment
- Automatic updates

#### Snap Store (Linux)
- Package as Snap
- Submit through Snapcraft
- Automatic updates
- Cross-distribution support

## Quality Assurance

### Testing Checklist

#### Functionality Testing
- [ ] Audio recording works
- [ ] Transcription is accurate
- [ ] Hotkeys function properly
- [ ] Auto-paste works
- [ ] Settings can be changed
- [ ] Application starts and closes cleanly

#### Platform Testing
- [ ] Test on clean system (no Python installed)
- [ ] Test with different audio devices
- [ ] Test with different screen resolutions
- [ ] Test with different user permissions
- [ ] Test with antivirus software

#### Performance Testing
- [ ] Application startup time
- [ ] Memory usage during operation
- [ ] CPU usage during transcription
- [ ] File size of executable
- [ ] Installation time

### Automated Testing

#### CI/CD Pipeline
```yaml
# .github/workflows/build.yml
name: Build and Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: python scripts/build/build-executable.py
    
    - name: Test executable
      run: |
        # Platform-specific testing
        if [ "$RUNNER_OS" == "Windows" ]; then
          dist/Whiz.exe --version
        elif [ "$RUNNER_OS" == "macOS" ]; then
          dist/Whiz.app/Contents/MacOS/Whiz --version
        else
          dist/whiz --version
        fi
```

## Release Management

### Version Numbering

Use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Process

1. **Development**: Work on feature branch
2. **Testing**: Test on all platforms
3. **Documentation**: Update changelog and docs
4. **Tagging**: Create version tag
5. **Building**: Build executables for all platforms
6. **Publishing**: Upload to distribution channels
7. **Announcement**: Notify users of new release

### Changelog Format

```markdown
# Changelog

## [1.0.0] - 2024-01-01

### Added
- Cross-platform support for Windows, macOS, and Linux
- PyAudio → sounddevice migration for easier installation
- keyboard → pynput migration for better compatibility
- Platform-specific UI adaptations
- Comprehensive error handling and graceful degradation

### Changed
- Improved audio recording stability
- Better hotkey handling across platforms
- Enhanced error messages and user feedback

### Fixed
- Audio device selection issues
- Hotkey registration problems
- Memory leaks during long sessions

### Security
- Updated dependencies to latest versions
- Improved input validation
```

## Legal Considerations

### Licensing
- Ensure all dependencies are compatible with your license
- Include license files in distribution
- Document third-party components

### Privacy
- Document data collection practices
- Provide privacy policy
- Ensure compliance with local regulations

### Trademarks
- Check for trademark conflicts
- Register your own trademarks if needed
- Use proper attribution for third-party components

## Support and Maintenance

### User Support
- Provide clear installation instructions
- Create troubleshooting guides
- Maintain issue tracker
- Respond to user feedback

### Maintenance
- Regular dependency updates
- Security patch releases
- Bug fix releases
- Feature updates

### End-of-Life
- Plan for application lifecycle
- Provide migration paths
- Archive old versions
- Notify users of discontinuation

## Metrics and Analytics

### Distribution Metrics
- Download counts by platform
- Installation success rates
- User retention rates
- Feature usage statistics

### Performance Metrics
- Application startup times
- Memory usage patterns
- CPU usage during operation
- Error rates and types

### User Feedback
- User satisfaction surveys
- Feature request tracking
- Bug report analysis
- Community engagement metrics
