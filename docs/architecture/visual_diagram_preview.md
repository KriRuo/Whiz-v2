# Visual Representation of Whiz Application Diagrams

## 1. Application Architecture Overview (Text Art)

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   SpeechApp     │  │  Custom Title   │  │   Tab Widget    │ │
│  │ Main Window     │  │     Bar         │  │ Main Content    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                     │                     │         │
│           │                     │                     │         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Record Tab    │  │ Transcripts Tab │  │ Preferences    │ │
│  │ Recording UI    │  │ History Display │  │ Dialog          │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                     │                     │         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Waveform Widget │  │ Visual Indicator │  │ Mic Circle      │ │
│  │ Audio Viz       │  │ Floating Status │  │ Animation       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CORE APPLICATION LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │SpeechController │  │SettingsManager  │  │ HotkeyManager   │ │
│  │ Main Logic      │  │ Configuration   │  │ Global Hotkeys  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                     │                     │         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ AudioManager    │  │ CleanupManager  │  │SingleInstance   │ │
│  │ Audio Recording │  │ Resource Mgmt   │  │ Manager          │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SECURITY & VALIDATION                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   FileSandbox   │  │Transcription    │  │ PathValidator   │ │
│  │ Path Validation │  │Exceptions       │  │ Secure Ops      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EXTERNAL DEPENDENCIES                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Whisper Engine  │  │  SoundDevice    │  │   PyAutoGUI     │ │
│  │ Speech Recog    │  │ Audio Recording │  │ Text Pasting    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                     │                     │         │
│  ┌─────────────────┐  ┌─────────────────┐                     │
│  │    PyInput      │  │     PyQt5       │                     │
│  │ Hotkey Detect   │  │   GUI Framework │                     │
│  └─────────────────┘  └─────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Speech Processing Flow (Timeline)

```
User Action → Hotkey Detection → Audio Recording → Speech Recognition → Text Output

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    USER     │    │ HOTKEY     │    │ AUDIO      │    │ WHISPER    │    │   OUTPUT   │
│             │    │ MANAGER    │    │ MANAGER    │    │ ENGINE     │    │            │
├─────────────┤    ├─────────────┤    ├─────────────┤    ├─────────────┤    ├─────────────┤
│ Presses     │───▶│ Detects     │───▶│ Starts      │───▶│ Loads      │───▶│ Processes   │
│ Alt+Gr      │    │ Hotkey      │    │ Recording   │    │ Model      │    │ Text       │
│             │    │             │    │             │    │             │    │            │
│ Releases    │───▶│ Releases    │───▶│ Stops       │───▶│ Transcribes │───▶│ Displays   │
│ Alt+Gr      │    │ Hotkey      │    │ Recording   │    │ Audio      │    │ Result     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                   │                   │                   │                   │
      │                   │                   │                   │                   │
      ▼                   ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   UI        │    │   UI        │    │   UI        │    │   UI        │    │   UI        │
│ Updates     │    │ Updates     │    │ Updates     │    │ Updates     │    │ Updates     │
│ Status      │    │ Status      │    │ Waveform    │    │ Status      │    │ History     │
│ "Recording" │    │ "Transcrib" │    │ Animation   │    │ "Complete"  │    │ Auto-paste  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 3. Detailed Processing Pipeline (Flow Chart)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MICROPHONE    │───▶│ SOUNDDEVICE     │───▶│ AUDIO CHUNKS    │
│     INPUT       │    │    STREAM       │    │ Thread-Safe     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ AUDIO LEVEL     │◀───│ AUDIO FRAME     │───▶│ WAVEFORM        │
│ CALCULATION    │    │ STORAGE         │    │ WIDGET          │
│ RMS Analysis   │    │                 │    │ Visual Feedback │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ DEVICE          │───▶│ CONTINUE        │◀───│ FALLBACK        │
│ VALIDATION      │    │ RECORDING      │    │ DEVICE          │
│ Connection      │    │                │    │                 │
│ Check           │    │                │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ AUDIO FILE      │───▶│ MODEL LOADING   │───▶│ WHISPER MODEL   │
│ CREATION        │    │ CHECK           │    │ Background       │
│ Sandboxed WAV   │    │ Thread-Safe     │    │ Loading          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ SPEECH          │───▶│ EXCEPTION       │───▶│ TEXT            │
│ RECOGNITION     │    │ CLASSIFICATION  │    │ PROCESSING      │
│ With Retry      │    │ Error Handling  │    │ Cleanup &       │
│ Logic           │    │                 │    │ Validation      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ EXPONENTIAL     │    │ ERROR           │    │ TRANSCRIPT      │
│ BACKOFF         │    │ RECOVERY        │    │ STORAGE         │
│                 │    │                 │    │ Timestamp &     │
│                 │    │                 │    │ Text            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ UI UPDATE       │    │ PYAUTOGUI       │    │ PASTE TO        │
│ Safe Widget     │    │                 │    │ ACTIVE WINDOW   │
│ Access          │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 4. Application Startup Flow

```
┌─────────────────┐
│ USER LAUNCHES   │
│     APP         │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ SINGLE INSTANCE │
│     CHECK       │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐ ┌─────────┐
│ NEW     │ │EXISTING │
│INSTANCE │ │INSTANCE │
└─────────┘ └─────────┘
    │           │
    ▼           ▼
┌─────────┐ ┌─────────┐
│ACQUIRE  │ │ACTIVATE │
│ LOCK    │ │ WINDOW  │
└─────────┘ └─────────┘
    │           │
    ▼           ▼
┌─────────┐ ┌─────────┐
│CREATE   │ │ EXIT    │
│QAPP     │ │ CURRENT │
└─────────┘ └─────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                INITIALIZATION SEQUENCE                      │
├─────────────────────────────────────────────────────────────┤
│ Logging → Settings → SpeechController → CleanupManager      │
│    ↓         ↓           ↓              ↓                 │
│ Audio → Hotkey → PathSandbox → SpeechApp → WidgetLifecycle  │
│    ↓         ↓           ↓              ↓                 │
│ Styling → ShowWindow → BackgroundModel → App Ready         │
└─────────────────────────────────────────────────────────────┘
```

## How to View the Actual Mermaid Diagrams

To see the actual rendered Mermaid diagrams, you can:

1. **Copy the Mermaid code** from the `application_diagram.md` file
2. **Paste it into** any of these online Mermaid editors:
   - [Mermaid Live Editor](https://mermaid.live/)
   - [Mermaid Chart](https://www.mermaidchart.com/)
   - [Draw.io](https://app.diagrams.net/) (supports Mermaid)

3. **Or use** Mermaid-compatible tools:
   - GitHub (renders Mermaid in README files)
   - GitLab (supports Mermaid in markdown)
   - VS Code with Mermaid extensions
   - Notion, Obsidian, or other markdown editors with Mermaid support

The diagrams show:
- **Architecture**: How all components connect
- **Flow**: Step-by-step speech processing
- **Pipeline**: Technical processing details  
- **Startup**: Application initialization sequence

Each diagram uses different Mermaid chart types (graph, sequenceDiagram) to best represent the different aspects of the application.
