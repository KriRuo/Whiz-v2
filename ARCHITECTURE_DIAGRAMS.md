# Architecture Diagrams

This document provides visual representations of the Whiz application architecture.

---

## Current Architecture

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  MainWindow  │  │  RecordTab   │  │ TranscriptsTab  │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘   │
│         │                 │                    │             │
│         └─────────────────┴────────────────────┘             │
│                           │                                  │
│         ┌─────────────────▼──────────────────┐              │
│         │   Custom Widgets & Components      │              │
│         │   - WaveformWidget                 │              │
│         │   - VisualIndicator                │              │
│         │   - GradientTabs                   │              │
│         │   - PreferencesDialog              │              │
│         └────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              SpeechApp (speech_ui.py)                 │  │
│  │  - Coordinates UI and Controller                      │  │
│  │  - Manages lifecycle and callbacks                    │  │
│  │  - Handles settings synchronization                   │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                       │
│  ┌───────────────────▼───────────────────────────────────┐  │
│  │         SpeechController (speech_controller.py)       │  │
│  │  ⚠️ GOD OBJECT - TOO MANY RESPONSIBILITIES:           │  │
│  │  - Hotkey listening                                   │  │
│  │  - Audio recording coordination                       │  │
│  │  - Whisper model management                           │  │
│  │  - Transcription processing                           │  │
│  │  - File I/O (temp audio files)                        │  │
│  │  - Callback management                                │  │
│  │  - Engine selection                                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CORE SERVICES LAYER                       │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ HotkeyManager │  │ AudioManager │  │SettingsManager  │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │CleanupManager │  │ PlatformUtils│  │LoggingConfig    │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │PerformanceMonitor│ PathValidation│ │ Configuration   │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  EXTERNAL DEPENDENCIES                       │
│  PyQt5 | Whisper | sounddevice | numpy | pynput | torch    │
└─────────────────────────────────────────────────────────────┘
```

---

## Problem: Circular Dependencies

```
┌─────────────┐
│  SpeechApp  │────┐
└──────┬──────┘    │
       │           │ Creates & holds reference
       │           ▼
       │      ┌──────────────────┐
       │      │ SpeechController │
       │      └────────┬─────────┘
       │               │
       │               │ Callbacks for UI updates
       └───────────────┘
       
⚠️ This creates a cycle that makes testing difficult
```

### Also:

```
┌─────────────┐
│  SpeechApp  │────┐
└──────┬──────┘    │
       │           │ Creates
       │           ▼
       │      ┌──────────┐
       │      │RecordTab │
       │      └────┬─────┘
       │           │
       │           │ parent_app reference
       └───────────┘

⚠️ RecordTab cannot be reused outside SpeechApp
```

---

## Proposed: Mediator Pattern (Breaks Cycles)

```
┌─────────────┐                    ┌──────────────────┐
│  SpeechApp  │───────────────────▶│ApplicationMediator│
└─────────────┘   Uses mediator    └────────┬─────────┘
                                            │
                                            │ Coordinates
                                            │
                  ┌─────────────────────────┴───────┐
                  │                                 │
                  ▼                                 ▼
         ┌──────────────┐                 ┌──────────────────┐
         │  RecordTab   │                 │ SpeechController │
         └──────────────┘                 └──────────────────┘
         
✅ No circular dependencies
✅ UI and Controller decoupled
✅ Testable in isolation
```

---

## Proposed: Decomposed SpeechController

### Before (Current):

```
┌────────────────────────────────────────────────┐
│         SpeechController (786 lines)           │
│  ⚠️ God Object                                 │
│  - Hotkey listening                            │
│  - Audio recording                             │
│  - Model management                            │
│  - Transcription                               │
│  - File I/O                                    │
│  - Callbacks                                   │
└────────────────────────────────────────────────┘
```

### After (Proposed):

```
┌────────────────────────────────────────────────┐
│      SpeechController (Slim Facade)            │
│  ✅ Coordinates services                       │
│  - Delegates to specialized services           │
│  - Thin orchestration layer                    │
└───────────┬───────────────────────────────────┘
            │
            │ Uses
            │
    ┌───────┴────────┬─────────────┬───────────────┐
    │                │             │               │
    ▼                ▼             ▼               ▼
┌─────────┐  ┌──────────────┐ ┌────────────┐ ┌────────────┐
│Recording│  │Transcription │ │   Model    │ │   Audio    │
│Coordinator│ │   Engine    │ │  Manager   │ │FileHandler │
└─────────┘  └──────────────┘ └────────────┘ └────────────┘
```

---

## Current File Organization

```
Whiz-v2/
├── speech_controller.py ← ⚠️ Core logic at root
├── speech_ui.py         ← ⚠️ Orchestration at root
├── waveform_widget.py   ← ⚠️ UI widget at root
├── main.py              ← ✅ Bootstrap at root (OK)
├── splash_screen.py     ← ⚠️ UI at root
├── create_sounds.py     ← ⚠️ Utility at root
├── fix_windows_audio.py ← ⚠️ Utility at root
├── diagnose_windows_audio.py ← ⚠️ Utility at root
├── core/                ← ✅ Well-organized
│   ├── audio_manager.py
│   ├── hotkey_manager.py
│   ├── settings_manager.py
│   └── ... (13 modules)
├── ui/                  ← ⚠️ Mixed organization
│   ├── main_window.py
│   ├── record_tab.py
│   ├── transcripts_tab.py
│   ├── preferences_dialog.py ← ⚠️ 1465 lines
│   ├── components/      ← Only 3 files
│   ├── widgets/         ← Only 4 files
│   └── ... (10+ files at root)
└── tests/               ← ✅ Well-organized
```

---

## Proposed File Organization

```
Whiz-v2/
├── app/                     ← ✅ New: Orchestration layer
│   ├── bootstrap/
│   │   ├── main.py
│   │   └── splash.py
│   └── controllers/
│       ├── speech_controller.py
│       ├── application_coordinator.py
│       └── application_mediator.py
├── core/                    ← ✅ Keep (already good)
│   ├── audio/
│   ├── transcription/       ← ✅ New: Domain logic
│   │   ├── engine.py
│   │   ├── whisper_engine.py
│   │   ├── faster_whisper_engine.py
│   │   └── model_manager.py
│   ├── recording/           ← ✅ New: Domain logic
│   │   ├── recording_coordinator.py
│   │   └── audio_file_handler.py
│   └── ... (other managers)
├── ui/                      ← ✅ Reorganized
│   ├── windows/
│   │   └── main_window.py
│   ├── tabs/
│   │   ├── record_tab.py
│   │   └── transcripts_tab.py
│   ├── dialogs/
│   │   └── preferences/
│   │       ├── preferences_dialog.py
│   │       ├── general_tab.py
│   │       ├── audio_tab.py
│   │       └── behavior_tab.py
│   ├── widgets/
│   │   ├── waveform_widget.py ← Moved from root
│   │   ├── titlebar_widget.py
│   │   └── ...
│   └── components/
│       └── ... (reusable components)
├── scripts/                 ← ✅ Keep
│   └── tools/
│       ├── create_sounds.py      ← Moved from root
│       ├── diagnose_audio.py     ← Moved from root
│       └── fix_audio.py          ← Moved from root
└── tests/                   ← ✅ Keep (already good)
```

---

## Data Flow (Current)

### Recording Flow

```
1. User Presses Hotkey
        │
        ▼
2. HotkeyManager detects (separate thread)
        │
        ▼
3. SpeechController.on_hotkey()
        │
        ▼
4. AudioManager.start_recording()
        │
        ▼
5. Audio frames collected ──────┐
        │                        │
        ├─────────────────┐      │
        │                 ▼      │
        │         WaveformWidget  │
        │         (visualization) │
        ▼                         │
6. User Releases Hotkey ◀────────┘
        │
        ▼
7. AudioManager.stop_recording()
        │
        ▼
8. Save to temp WAV file
        │
        ▼
9. Load Whisper model (lazy)
        │
        ▼
10. Transcribe audio
        │
        ▼
11. SpeechController.transcript_callback
        │
        ▼
12. SpeechApp.on_new_transcript()
        │
        ├──────────────┬─────────────┐
        │              │             │
        ▼              ▼             ▼
   Update UI    Auto-paste?    Add to history
                (pyautogui)   (TranscriptsTab)
```

---

## Coupling Diagram

### Legend
- `────▶` Strong coupling (direct reference)
- `····▶` Weak coupling (callback/signal)
- `⚠️` Circular dependency

### Current State

```
                         ⚠️ CIRCULAR
        ┌────────────────────────────────┐
        │                                │
        │                                │
SpeechApp ────▶ SpeechController ·······┘
   │
   ├────▶ MainWindow
   │
   ├────▶ RecordTab ⚠️ ──────┐
   │         │                │
   │         └────────────────┘ parent_app
   │
   ├────▶ TranscriptsTab
   │
   └────▶ PreferencesDialog


SpeechController ────▶ HotkeyManager
                 ────▶ AudioManager
                 ····▶ UI (callbacks)


MainWindow ────▶ SettingsManager
           ────▶ ThemeManager
           ────▶ SystemTray
```

### Proposed State (After Refactoring)

```
ApplicationMediator
   │
   ├────▶ SpeechController (slim)
   │         │
   │         ├────▶ RecordingCoordinator
   │         ├────▶ TranscriptionEngine
   │         └────▶ ModelManager
   │
   └─────▶ UI Components (via signals)
            - SpeechApp
            - MainWindow
            - RecordTab
            - TranscriptsTab

✅ No circular dependencies
✅ Clear one-way flow
✅ Testable in isolation
```

---

## Testing Strategy

### Current Test Structure

```
tests/
├── unit/                    ← Small, focused tests
│   ├── test_tron_glow.py
│   ├── test_settings_race.py
│   └── test_button_animation.py
├── integration/             ← Multi-component tests
│   └── test_single_instance_runtime.py
├── verification/            ← Manual verification
│   ├── verify_dark_blue.py
│   └── verify_positioning.py
└── (root level tests)       ← Functional tests
    ├── test_settings_manager.py
    ├── test_speech_controller.py
    └── test_full_workflow_integration.py
```

### What Tests Well

```
✅ SettingsManager ────▶ Clear interface, easy to mock
✅ AudioManager    ────▶ Platform abstraction tested
✅ CleanupManager  ────▶ Phased cleanup verified
✅ PlatformUtils   ────▶ Feature detection checked
```

### What Tests Poorly

```
❌ SpeechController
   │
   └───▶ Requires mocking:
         - HotkeyManager
         - AudioManager  
         - Whisper models
         - File system
         - UI callbacks
         
   Result: Tests become integration tests (slow, fragile)

❌ SpeechApp
   │
   └───▶ Requires full object graph:
         - MainWindow
         - SpeechController (+ all its deps)
         - SettingsManager
         - Theme managers
         - All widgets
         
   Result: Cannot unit test, only integration test
```

---

## Design Patterns Used

### Currently Implemented

| Pattern | Location | Usage |
|---------|----------|-------|
| **Singleton** | CleanupManager, PerformanceMonitor | Global access via `get_*()` |
| **Observer** | Qt Signals/Slots | Event propagation |
| **Strategy** | Whisper engines | openai vs faster-whisper |
| **Factory** | IconManager, ComponentFactory | Object creation |
| **Repository** | SettingsManager | Persistence abstraction |
| **Facade** | PlatformUtils | OS abstraction |

### Recommended Additions

| Pattern | Where to Apply | Benefit |
|---------|---------------|---------|
| **Mediator** | UI ↔ Controller | Break circular dependencies |
| **Abstract Factory** | Transcription engines | Easy to add new engines |
| **Command** | Recording actions | Undo/redo, logging |
| **Dependency Injection** | Replace singletons | Explicit dependencies, testable |

---

## Complexity Metrics

### File Size Distribution

```
Large (>1000 lines) ⚠️
├── preferences_dialog.py: 1465 lines
└── speech_ui.py: 1200+ lines

Medium (500-1000 lines)
├── speech_controller.py: 786 lines
├── settings_manager.py: 556 lines
├── settings_schema.py: 608 lines
└── single_instance_manager.py: 566 lines

Small (<500 lines) ✅
└── Most other files (good!)
```

### Cyclomatic Complexity (Estimated)

```
High Complexity ⚠️
├── SpeechController.transcribe()
├── PreferencesDialog.init_ui()
└── MainWindow.init_window()

Medium Complexity
├── SettingsManager.validate()
└── CleanupManager.execute()

Low Complexity ✅
└── Most core service methods
```

---

## Evolution Paths

### Option 1: Incremental (Recommended)

```
Month 1: Organization
├── Reorganize root files
└── Split PreferencesDialog

Month 2: Extraction
├── Extract transcription domain
└── Create engine abstraction

Month 3: Decomposition
├── Split SpeechController (part 1)
└── Extract recording coordinator

Month 4: Decoupling
├── Split SpeechController (part 2)
└── Introduce mediator

Result: Clean architecture, no disruption
```

### Option 2: Big Bang (Not Recommended)

```
Week 1-2: Full rewrite
└── Rewrite entire orchestration layer

Risk: ⚠️
├── Breaking existing functionality
├── Long feature freeze
└── Difficult to review/test
```

---

## Summary Diagrams

### Current State
```
[UI Layer] ←──⚠️──→ [Orchestration] ←──→ [Core Services]
              Circular        Clean
              Dependencies    Boundaries
```

### Desired State
```
[UI Layer] ──→ [Mediator] ──→ [Controllers] ──→ [Core Services]
    Clean         Clean          Clean           Clean
    Deps          Deps           Deps            Deps
```

---

**For detailed recommendations, see:**
- [ARCHITECTURAL_REVIEW.md](ARCHITECTURAL_REVIEW.md) - Full analysis
- [ARCHITECTURAL_REVIEW_SUMMARY.md](ARCHITECTURAL_REVIEW_SUMMARY.md) - Executive summary
