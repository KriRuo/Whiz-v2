# Speech-to-Text Tool (PyQt GUI)

A modern PyQt-based GUI for the hotkey-driven speech-to-text application using OpenAI Whisper and PyAudio.

## Features

- **Global Hotkey Support**: Press and hold any configured hotkey to record, release to transcribe
- **PyQt GUI**: Clean, modern interface with real-time status updates
- **Whisper Integration**: Uses OpenAI Whisper for high-quality speech recognition
- **Auto-Paste**: Automatically pastes transcribed text to the active application
- **Dynamic Hotkey Configuration**: Change hotkeys without restarting the application
- **Multiple Whisper Models**: Choose from tiny, base, small, medium, or large models

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

## Usage

### Basic Operation
1. Launch the application
2. Press and hold your configured hotkey (default: AltGr)
3. Speak clearly into your microphone
4. Release the hotkey to transcribe and paste

### GUI Controls

- **Start/Stop Recording**: Manual control buttons for recording
- **Whisper Model**: Select model size (tiny = fastest, large = most accurate)
- **Auto-Paste Toggle**: Enable/disable automatic text pasting
- **Hotkey Configuration**: Set custom hotkeys (e.g., "F8", "ctrl+shift+R")

### Hotkey Examples
- `F8` - Function key
- `alt gr` - AltGr key (default)
- `ctrl+shift+r` - Combination keys
- `space` - Spacebar (not recommended)

## File Structure

```
├── main.py              # Application entry point
├── speech_controller.py  # Core speech processing logic
├── speech_ui.py         # PyQt GUI implementation
├── requirements.txt     # Python dependencies
└── README_PyQt.md       # This file
```

## Troubleshooting

### Audio Issues
- Ensure your microphone is properly connected and set as default
- Check that PyAudio is correctly installed
- On Windows, you may need to install Visual C++ Build Tools

### Hotkey Issues
- Some hotkeys may conflict with system shortcuts
- Try different hotkeys if one doesn't work
- Ensure the application has focus when testing hotkeys

### Performance
- Use "tiny" model for fastest processing
- Use "large" model for best accuracy
- Processing time increases with model size

## Dependencies

- **PyQt5**: GUI framework
- **openai-whisper**: Speech recognition
- **pyaudio**: Audio recording
- **keyboard**: Global hotkey detection
- **pyautogui**: Text pasting

## License

This project is open source. Feel free to modify and distribute.
