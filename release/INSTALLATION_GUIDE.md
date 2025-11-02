# Whiz Installation Guide

## Quick Start

### Windows Users (Recommended)

1. **Download**: Get `Whiz-v1.0.0-Windows-Installer.zip` from the releases page
2. **Extract**: Unzip the file to a folder (e.g., Desktop)
3. **Install**: Right-click `install-whiz.bat` → "Run as administrator"
4. **Launch**: Double-click the Whiz desktop shortcut

### Alternative: Standalone Version

1. **Download**: Get `Whiz-v1.0.0-Windows-Standalone.exe`
2. **Run**: Double-click the executable
3. **No installation required**

## Detailed Installation Steps

### Method 1: Full Installation (Recommended)

#### Step 1: Download and Extract
```
1. Download Whiz-v1.0.0-Windows-Installer.zip
2. Right-click the ZIP file → "Extract All"
3. Choose a location (e.g., C:\Users\[YourName]\Desktop\Whiz)
4. Click "Extract"
```

#### Step 2: Run Installation
```
1. Navigate to the extracted folder
2. Right-click "install-whiz.bat"
3. Select "Run as administrator"
4. Click "Yes" when Windows asks for permission
5. Wait for installation to complete
```

#### Step 3: Verify Installation
```
1. Look for "Whiz" desktop shortcut
2. Check Start menu for "Whiz" entry
3. Double-click desktop shortcut to launch
4. Grant microphone permissions when prompted
```

### Method 2: Standalone Executable

#### Step 1: Download
```
1. Download Whiz-v1.0.0-Windows-Standalone.exe
2. Save to desired location (e.g., Desktop)
```

#### Step 2: Run
```
1. Double-click Whiz-v1.0.0-Windows-Standalone.exe
2. Grant microphone permissions when prompted
3. Application starts immediately
```

## First-Time Setup

### 1. Microphone Permissions
When you first launch Whiz:
- Windows will ask for microphone permissions
- Click "Yes" or "Allow"
- This is required for voice recording

### 2. Initial Model Download
On first use:
- Whiz will download the Whisper AI model (~150MB)
- This requires an internet connection
- Download happens automatically in the background
- You'll see progress in the splash screen

### 3. Test Recording
To verify everything works:
1. Launch Whiz
2. Wait for "Ready!" status
3. Press **AltGr** key (or your configured hotkey)
4. Speak into your microphone
5. Release the key
6. Check if text appears in your current application

## Configuration

### Basic Settings
1. **Open Settings**: Click the gear icon in Whiz
2. **Audio Tab**: Select your microphone
3. **Hotkeys Tab**: Change recording hotkey if needed
4. **Whisper Tab**: Choose model size (tiny = faster, larger = more accurate)

### Advanced Settings
- **Language**: Set specific language or use auto-detection
- **Temperature**: Adjust transcription creativity (0.0 = most accurate)
- **Auto-paste**: Enable/disable automatic text pasting
- **Visual Indicator**: Show/hide recording indicator

## Troubleshooting

### Common Issues

#### "Microphone not detected"
**Solution**:
1. Check microphone is connected and working
2. Go to Settings > Audio
3. Select correct audio device
4. Test with Windows Sound settings

#### "Hotkey not working"
**Solution**:
1. Try running Whiz as Administrator
2. Go to Settings > Hotkeys
3. Change to a different key combination
4. Avoid keys used by other applications

#### "Installation failed"
**Solution**:
1. Ensure you're running as Administrator
2. Check Windows Defender isn't blocking the installer
3. Try the standalone executable instead
4. Disable antivirus temporarily during installation

#### "Transcription not working"
**Solution**:
1. Check internet connection (required for model download)
2. Speak clearly and reduce background noise
3. Try a different microphone
4. Increase recording duration (speak longer)

### Performance Issues

#### "Application is slow"
**Solution**:
1. Close other applications
2. Use smaller Whisper model (tiny instead of base)
3. Reduce background noise
4. Restart Whiz

#### "High CPU usage"
**Solution**:
1. Use smaller Whisper model
2. Reduce recording quality in Settings
3. Close other applications
4. Check for Windows updates

## Uninstallation

### Full Installation Removal
1. **Control Panel Method**:
   - Go to Control Panel > Programs > Programs and Features
   - Find "Whiz" in the list
   - Click "Uninstall"

2. **Batch Script Method**:
   - Navigate to installation folder
   - Run `uninstall-whiz.bat` as Administrator

3. **Manual Removal**:
   - Delete installation folder
   - Remove desktop shortcut
   - Remove Start menu entry

### Standalone Version Removal
- Simply delete the executable file
- No additional cleanup required

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 (version 1903) or Windows 11
- **Processor**: 64-bit processor
- **Memory**: 4 GB RAM
- **Storage**: 2 GB free disk space
- **Audio**: Microphone for voice input
- **Network**: Internet connection for initial setup

### Recommended Requirements
- **Operating System**: Windows 11
- **Processor**: Modern multi-core processor
- **Memory**: 8 GB RAM or more
- **Storage**: 5 GB free disk space
- **Audio**: High-quality USB or built-in microphone
- **Network**: Stable broadband internet connection

## Security Notes

### File Verification
- **SHA256 Checksums**: Verify downloaded files using `SHA256-checksums.txt`
- **Antivirus**: Some antivirus software may flag the executable
- **Windows Defender**: May require approval for first run

### Permissions
- **Microphone**: Required for voice recording
- **Administrator**: May be required for global hotkeys
- **Network**: Required for initial model download

## Support

### Getting Help
- **Documentation**: Check README.md for detailed information
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Community support and questions

### Contact Information
- **GitHub Repository**: [Link to repository]
- **Issues Page**: [Link to issues]
- **Discussions**: [Link to discussions]

---

**Need Help?** Check the troubleshooting section above or visit our GitHub repository for support.
