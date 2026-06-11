# Architectural Review: Whiz Voice-to-Text Application

**Review Date:** February 8, 2026  
**Reviewer Role:** Senior Software Architect  
**Codebase Version:** v2.x  
**Review Scope:** Architecture, structure, design quality, modularity, and long-term maintainability

---

## Architectural Overview

### What This System Does

Whiz is a **cross-platform voice-to-text application** that enables users to transcribe speech using global hotkeys. The application:

- Captures audio from system microphones via global hotkey triggers (hold or toggle mode)
- Processes audio through OpenAI Whisper or faster-whisper models
- Provides real-time visual feedback (waveform visualization, recording indicators)
- Offers comprehensive settings management with persistence across platforms
- Supports Windows, macOS, and Linux with platform-specific optimizations

**Primary Use Case:** Accessibility tool for hands-free voice transcription with auto-paste capabilities

### Responsibility Distribution

The system follows a **3-layer architecture** with clear separation:

```
┌─────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (ui/)                           │
│  - MainWindow, RecordTab, TranscriptsTab            │
│  - Custom widgets, themes, visual indicators        │
│  - PyQt5-based UI components                        │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  ORCHESTRATION LAYER (root level)                   │
│  - SpeechApp (speech_ui.py) - UI coordination       │
│  - SpeechController (speech_controller.py) - Logic  │
│  - Main.py - Application bootstrap                  │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  CORE SERVICES LAYER (core/)                        │
│  - HotkeyManager, AudioManager, SettingsManager     │
│  - Platform abstraction, logging, cleanup           │
│  - Cross-platform utilities and validation          │
└─────────────────────────────────────────────────────┘
```

**Key Responsibilities:**
- **UI Layer:** Pure presentation - rendering, user interaction, visual feedback
- **Orchestration Layer:** Coordinates UI and services, manages application lifecycle
- **Core Layer:** Platform-agnostic business logic and infrastructure services

### Implicit Architectural Style

**Hybrid: Layered + Service-Oriented**

- **Layered:** Clear top-down dependency flow (UI → Orchestration → Core)
- **Service-Oriented:** Core layer provides standalone services (singleton managers)
- **Event-Driven:** PyQt signals/slots for async communication
- **Cross-Platform Abstraction:** Platform-specific logic isolated in `core/platform_*` modules

---

## Structural Strengths

### 1. **Excellent Core Service Abstraction**

**Location:** `core/` directory

The core layer demonstrates professional-grade abstraction:

```python
# Clean, focused responsibility per module
core/hotkey_manager.py      # Global hotkey registration
core/audio_manager.py        # Cross-platform audio I/O
core/settings_manager.py     # Persistence layer
core/cleanup_manager.py      # Resource lifecycle
core/platform_utils.py       # OS abstraction
```

**Why This Works:**
- Each manager has a **single, clear responsibility**
- Services are **self-contained** with minimal coupling
- Platform differences isolated behind unified interfaces
- All managers use **lazy initialization** for fast startup
- Comprehensive error handling with custom exception hierarchy

### 2. **Robust Resource Management**

**Location:** `core/cleanup_manager.py`

The `CleanupManager` is an architectural highlight:

- **Phased cleanup** (UI → Audio → Hotkeys → Models → Files → System)
- **Timeout protection** prevents hanging during shutdown
- **Verification hooks** to confirm cleanup success
- **Rollback capabilities** for failed cleanup
- **Dependency tracking** ensures proper cleanup order

**Impact:** This prevents common issues like memory leaks, hanging processes, and resource contention.

### 3. **Strong Settings Architecture**

**Location:** `core/settings_manager.py` + `core/settings_schema.py`

Settings management is well-designed:

- **Schema-based validation** prevents invalid states
- **QSettings integration** for platform-native persistence
- **JSON import/export** for configuration sharing
- **Cache layer** for performance optimization
- **Type coercion** handles platform differences (Registry vs. plist)

**Pattern Used:** Repository pattern with validation layer

### 4. **Comprehensive Test Coverage**

**Location:** `tests/` directory

The test structure shows maturity:

- **60+ test files** covering unit, integration, and functional scenarios
- **Organized by concern:** `tests/unit/`, `tests/integration/`, `tests/verification/`
- **Platform-specific tests:** DPI scaling, Windows audio, cross-platform compatibility
- **Real-world scenarios:** Audio workflow tests, full integration tests

### 5. **Platform Abstraction Done Right**

**Location:** `core/platform_utils.py`, `core/platform_features.py`

Platform differences are isolated effectively:

```python
# Feature detection pattern
platform_features = PlatformFeatures()
features = platform_features.detect_all_features()

if features['single_instance'] == FeatureStatus.AVAILABLE:
    # Use platform-specific implementation
```

**Benefits:**
- No `if sys.platform == 'win32'` scattered throughout codebase
- Graceful degradation when features unavailable
- Easy to add new platform-specific features

### 6. **Responsive UI Design System**

**Location:** `ui/layout_system.py`

A comprehensive design system with:

- **Design tokens** (spacing, colors, typography)
- **DPI scaling helpers** for high-resolution displays
- **Responsive breakpoints** based on screen size
- **Adaptive components** that scale automatically

**Impact:** Professional UI that works across screen resolutions and DPI settings

---

## Key Issues & Architectural Smells

### 1. **God Object: SpeechController**

**Severity:** High  
**Affected Areas:** `speech_controller.py` (786 lines)

**Description:**

`SpeechController` violates Single Responsibility Principle by handling:

1. Hotkey listening (threading)
2. Audio recording coordination
3. Whisper model management (lazy loading)
4. Transcript generation
5. File I/O (temporary audio files)
6. Settings propagation
7. Callback management for UI updates
8. Engine selection (openai vs faster-whisper)
9. Performance monitoring integration

**Why This Matters Long-Term:**

- **Hard to test:** Unit testing requires mocking 5+ dependencies
- **Fragile:** Changes to transcription logic can break audio recording
- **Difficult to extend:** Adding new features requires editing a monolithic class
- **Poor reusability:** Can't use parts of functionality independently
- **High cognitive load:** Understanding one feature requires understanding all features

**Suggested Improvement:**

Split into focused services:

```python
# Proposed structure
core/transcription/
    transcription_engine.py     # Abstract base + factory
    whisper_engine.py           # OpenAI Whisper implementation
    faster_whisper_engine.py    # faster-whisper implementation
    model_manager.py            # Model loading/caching

core/recording/
    recording_coordinator.py    # Orchestrates recording workflow
    audio_file_handler.py       # Temp file management
    
controllers/
    speech_controller.py        # Slim facade coordinating services
```

**Migration Strategy:**
1. Extract model management first (lowest risk)
2. Extract engine abstraction
3. Extract recording coordination
4. Refactor remaining controller to thin facade

---

### 2. **Tight Coupling: Orchestration ↔ UI**

**Severity:** High  
**Affected Areas:** `speech_ui.py`, `ui/main_window.py`, `ui/record_tab.py`

**Description:**

`SpeechApp` (in `speech_ui.py`) extends `MainWindow` and directly manages:

- Tab widgets (`RecordTab`, `TranscriptsTab`)
- Preferences dialog lifecycle
- Waveform widget
- Visual indicator widget
- Theme management
- Settings synchronization
- Controller callbacks

This creates **bidirectional dependencies:**

```
SpeechApp → MainWindow
SpeechApp → RecordTab → SpeechApp (circular via parent_app)
SpeechApp → SpeechController → SpeechApp (callbacks)
```

**Why This Matters Long-Term:**

- **Cannot test UI without controller** and vice versa
- **Circular dependencies** make reasoning about code flow difficult
- **Hard to reuse components:** RecordTab expects full SpeechApp context
- **Fragile refactoring:** Changes ripple across multiple classes

**Suggested Improvement:**

Introduce **Mediator pattern** to break circular dependencies:

```python
# Proposed structure
class ApplicationMediator:
    """Coordinates between UI and business logic"""
    
    def __init__(self, controller: SpeechController):
        self.controller = controller
        self._ui_callbacks = {}
    
    def register_ui_callback(self, event: str, callback: Callable):
        self._ui_callbacks[event] = callback
    
    def handle_start_recording(self):
        self.controller.start_recording()
        self._notify_ui('recording_started')
    
    def handle_transcription_complete(self, text: str):
        self._notify_ui('transcript_available', text)

# UI becomes passive
class RecordTab(BaseTab):
    def __init__(self, mediator: ApplicationMediator):
        self.mediator = mediator
        
    def _on_start(self):
        self.mediator.handle_start_recording()
```

**Benefits:**
- **Testable in isolation:** Mock mediator for UI tests
- **No circular dependencies:** One-way dependency flow
- **Clear contracts:** Mediator defines all interactions

---

### 3. **Mixed Responsibilities: Root-Level Files**

**Severity:** Medium  
**Affected Areas:** `speech_controller.py`, `speech_ui.py`, `waveform_widget.py`, `main.py`

**Description:**

The project has **9 Python files at root level** mixing different concerns:

```
speech_controller.py      # Core business logic (786 lines)
speech_ui.py             # UI coordination (1200+ lines)
waveform_widget.py       # Specialized UI component
main.py                  # Bootstrap
main_with_splash.py      # Alternative bootstrap
splash_screen.py         # UI component
create_sounds.py         # Utility script
fix_windows_audio.py     # Platform-specific script
diagnose_windows_audio.py # Diagnostic script
```

**Why This Matters Long-Term:**

- **No clear ownership:** Which files are "core" vs "UI" vs "utilities"?
- **Import confusion:** Should `speech_controller` import from `ui/`? (It doesn't, but location suggests it could)
- **Discovery difficulty:** New developers don't know where to find things
- **Merge conflicts:** Everyone works in root directory

**Suggested Improvement:**

Reorganize into clear module boundaries:

```
whiz/
├── app/                      # Application layer
│   ├── controllers/
│   │   └── speech_controller.py
│   ├── coordination/
│   │   └── application_coordinator.py
│   └── bootstrap/
│       ├── main.py
│       └── splash.py
├── core/                     # Already good
├── ui/                       # Already good
│   └── widgets/
│       └── waveform_widget.py  # Move here
├── scripts/                  # Already exists
│   └── tools/
│       ├── create_sounds.py    # Move here
│       └── diagnose_audio.py   # Move here
└── tests/                    # Already good
```

**Migration Path:**
1. Move utilities to `scripts/tools/` (lowest risk)
2. Move `waveform_widget.py` to `ui/widgets/`
3. Create `app/` package for orchestration layer
4. Update imports gradually with deprecation warnings

---

### 4. **Inconsistent Component Organization**

**Severity:** Medium  
**Affected Areas:** `ui/components/`, `ui/widgets/`, `ui/layouts/`

**Description:**

The UI layer has **inconsistent organization**:

```
ui/
├── components/               # 3 files (base_components.py, mic_circle.py, __init__.py)
├── widgets/                  # 4 files (gradient tabs, transcript expander, etc.)
├── layouts/                  # Layout configurations
├── custom_titlebar.py        # Why not in components/?
├── visual_indicator.py       # Why not in widgets/?
├── system_tray.py           # Why not in components/?
├── preferences_dialog.py     # 1465 lines - should be split
└── ... (10 more files at ui/ root)
```

**Why This Matters Long-Term:**

- **No clear rules:** Where do new components go?
- **Discoverability:** Hard to find related functionality
- **Growing root:** As project grows, `ui/` becomes cluttered
- **Inconsistent imports:** `from ui.components` vs `from ui.visual_indicator`

**Suggested Improvement:**

Establish clear rules:

```
ui/
├── components/          # Generic reusable components
│   ├── buttons.py
│   ├── inputs.py
│   ├── panels.py
│   └── indicators.py   # Move visual_indicator.py here
├── widgets/             # Domain-specific composed widgets
│   ├── waveform_widget.py
│   ├── titlebar_widget.py  # Move custom_titlebar.py here
│   ├── system_tray_widget.py
│   └── transcript_expander.py
├── dialogs/             # Full-screen dialogs
│   ├── preferences/    # Split 1465-line file
│   │   ├── preferences_dialog.py
│   │   ├── general_tab.py
│   │   ├── audio_tab.py
│   │   └── behavior_tab.py
│   └── about_dialog.py
├── tabs/                # Tab containers
│   ├── record_tab.py
│   └── transcripts_tab.py
├── windows/             # Window management
│   └── main_window.py
├── styles/              # Already good
└── layout_system.py     # Core layout utilities
```

**Rules:**
- **components/**: Small, reusable, no business logic
- **widgets/**: Composed components, domain-aware
- **dialogs/**: Full-screen views
- **tabs/**: Tab content containers

---

### 5. **Hidden Dependency: Global Singletons**

**Severity:** Medium  
**Affected Areas:** `core/cleanup_manager.py`, `core/performance_monitor.py`, `core/logging_config.py`

**Description:**

Several core modules use **global singleton access** via module-level functions:

```python
# From various modules
logger = get_logger(__name__)                      # Implicit global
monitor = get_performance_monitor()                # Implicit singleton
cleanup_mgr = get_cleanup_manager()               # Implicit singleton
sandbox = get_sandbox()                            # Implicit singleton
```

**Why This Matters Long-Term:**

- **Hidden dependencies:** Not visible in function signatures
- **Hard to test:** Can't inject mocks easily
- **State leakage:** Tests can interfere with each other
- **Initialization order issues:** Must be called in correct sequence
- **Difficult to parallelize:** Global state prevents concurrent testing

**Suggested Improvement:**

Make dependencies explicit:

```python
# Instead of
def process_audio():
    logger = get_logger(__name__)
    monitor = get_performance_monitor()
    logger.info("Processing...")

# Do this
def process_audio(logger: Logger, monitor: PerformanceMonitor):
    logger.info("Processing...")

# Or use context object
@dataclass
class AppContext:
    logger: Logger
    monitor: PerformanceMonitor
    cleanup: CleanupManager
    settings: SettingsManager

def process_audio(ctx: AppContext):
    ctx.logger.info("Processing...")
```

**Migration Path:**
1. Add optional parameters with defaults using global accessors
2. Update callers to pass dependencies explicitly
3. Deprecate global accessors
4. Remove global state

**Exception:** Logging can remain global as it's truly infrastructure-level

---

### 6. **Bloated Dialog: PreferencesDialog**

**Severity:** Low  
**Affected Areas:** `ui/preferences_dialog.py` (1465 lines)

**Description:**

`PreferencesDialog` is a **single 1465-line file** managing:

- 5 tabs (General, Behavior, Audio, Transcription, Advanced)
- Device enumeration and selection
- Audio testing functionality
- Theme switching
- Hotkey configuration
- Settings validation and persistence
- Help text management

**Why This Matters Long-Term:**

- **Merge conflicts:** Multiple developers can't work on different tabs
- **High cognitive load:** Understanding any feature requires reading 1465 lines
- **Difficult testing:** Hard to test individual tab logic
- **Slow compile times:** Large files slow down IDE performance

**Suggested Improvement:**

Split by tab:

```python
ui/dialogs/preferences/
├── __init__.py
├── preferences_dialog.py       # Main container (< 100 lines)
├── tabs/
│   ├── general_tab.py
│   ├── behavior_tab.py
│   ├── audio_tab.py           # Audio device + testing
│   ├── transcription_tab.py
│   └── advanced_tab.py
└── shared/
    ├── settings_validator.py
    └── help_texts.py
```

**Benefits:**
- **Parallel development:** Different developers work on different tabs
- **Easier testing:** Test tabs independently
- **Better code review:** Smaller, focused PRs
- **Clear ownership:** Each tab is self-contained

---

### 7. **Unclear Boundary: App vs. UI**

**Severity:** Low  
**Affected Areas:** `speech_ui.py` (SpeechApp)

**Description:**

`SpeechApp` extends `MainWindow`, creating confusion:

```python
class MainWindow(QMainWindow):  # UI/presentation concern
    # Window management, geometry, tray icon, theming
    ...

class SpeechApp(MainWindow):     # Application concern
    # Controller integration, lifecycle, callbacks
    ...
```

**Questions This Raises:**
- Is `SpeechApp` part of the UI layer or orchestration layer?
- Should new features go in `MainWindow` or `SpeechApp`?
- Why does UI class (`MainWindow`) know about `settings_manager`?

**Why This Matters Long-Term:**

- **Confusing boundaries:** Team disagrees on where features belong
- **Harder to test:** UI and app logic mixed together
- **Difficult to refactor:** Can't change window behavior without affecting app logic

**Suggested Improvement:**

**Option 1: Composition over Inheritance**

```python
class MainWindow(QMainWindow):
    """Pure UI concerns: geometry, chrome, theming"""
    def __init__(self):
        # No business logic dependencies
        ...

class SpeechApp:
    """Application orchestration"""
    def __init__(self, controller: SpeechController, settings: SettingsManager):
        self.window = MainWindow()
        self.controller = controller
        self.settings = settings
        self._wire_connections()
```

**Option 2: Clear Naming**

```python
class ApplicationWindow(QMainWindow):  # Clearly app-level
    ...

class MainUIWindow(QMainWindow):       # Clearly UI-level
    ...
```

---

## Dependency & Coupling Analysis

### Dependency Direction

**Current State: ✅ Clean**

Dependencies flow correctly:

```
UI → Orchestration → Core → External Libraries
✓  Never reverses
✓  Core never imports from UI
✓  Core never imports from orchestration
```

**Verification:**

```bash
$ grep -r "import.*ui\." core/
# (No results - confirmed clean)
```

### Tight Couplings

1. **SpeechApp ↔ SpeechController**
   - **Type:** Bidirectional (callbacks)
   - **Impact:** Cannot test independently
   - **Fix:** Introduce mediator/event bus

2. **RecordTab → parent_app (SpeechApp)**
   - **Type:** Parent dependency
   - **Impact:** RecordTab cannot be reused outside SpeechApp
   - **Fix:** Pass specific callbacks, not entire parent

3. **MainWindow → SettingsManager**
   - **Type:** Direct dependency
   - **Impact:** Window management coupled to persistence
   - **Fix:** Pass settings as data, not manager

### Circular Dependencies

**Found:** 1 circular dependency

```
SpeechApp → RecordTab
RecordTab.parent_app → SpeechApp
```

**Why Problematic:**
- Makes code hard to reason about
- Complicates testing (need full object graph)
- Prevents incremental loading

**Fix:** Use dependency inversion - RecordTab should depend on abstraction:

```python
class IRecordingHost(Protocol):
    def on_start_recording(self) -> None: ...
    def on_stop_recording(self) -> None: ...

class RecordTab(BaseTab):
    def __init__(self, host: IRecordingHost):
        self.host = host  # No longer knows about SpeechApp
```

### Opportunities for Clearer Boundaries

1. **Create `app/` Package**
   - Move `speech_ui.py`, `speech_controller.py` into `app/controllers/`
   - Clear separation from `core/` (infrastructure) and `ui/` (presentation)

2. **Extract Transcription Domain**
   - Create `core/transcription/` with engine abstraction
   - Reduces coupling between controller and specific Whisper implementations

3. **Formalize Event Contracts**
   - Define explicit event types (instead of callbacks)
   - Use PyQt signals throughout (already partially done)

---

## Modularity & Separation of Concerns

### Well-Separated Concerns ✅

1. **Platform Abstraction**
   - `core/platform_utils.py` isolates OS differences
   - Clean interface, no leakage

2. **Settings Management**
   - Schema-based validation separated from persistence
   - JSON import/export decoupled from QSettings

3. **Resource Cleanup**
   - Cleanup logic isolated in dedicated manager
   - No cleanup code scattered across modules

### Mixed Concerns ❌

1. **SpeechController**
   - Mixes: hotkey handling + audio + transcription + file I/O
   - **Should be:** Thin coordinator calling specialized services

2. **SpeechApp**
   - Mixes: UI lifecycle + settings management + controller coordination
   - **Should be:** Pure orchestration, no UI concerns

3. **MainWindow**
   - Mixes: Window chrome + system tray + sound effects + settings
   - **Should be:** Just window management

### Missing Boundaries

1. **No Transcription Domain**
   - Transcription logic embedded in `SpeechController`
   - Should have: `core/transcription/` package with engine abstraction

2. **No Recording Domain**
   - Recording workflow scattered across controller
   - Should have: `core/recording/` with coordinator + file handler

3. **No Event/Message Layer**
   - Callbacks used directly between layers
   - Should have: Typed events or message bus

---

## Scalability & Evolution Readiness

### Easy to Add ✅

1. **New Settings**
   - Schema-based system makes adding settings trivial
   - Just add to `SETTINGS_SCHEMA` with validation rules

2. **New Platform**
   - Platform abstraction makes adding OS support straightforward
   - Add handlers to `PlatformFeatures` and `PlatformUtils`

3. **New UI Themes**
   - Theme system well-designed with token-based approach
   - Add theme to `theme_manager.py` with color palette

4. **New Tests**
   - Clear test organization makes adding tests easy
   - Just follow existing patterns in `tests/unit/` or `tests/integration/`

### Hard to Add ❌

1. **New Transcription Engine**
   - Currently: Must modify `SpeechController` directly
   - **Should be:** Plugin-based architecture with engine registry

2. **Alternative Recording Mode**
   - Currently: Logic tightly coupled to hold/toggle in controller
   - **Should be:** Strategy pattern for recording modes

3. **Multiple Simultaneous Recordings**
   - Currently: Single global recording state
   - **Would require:** Major refactoring of `SpeechController`

4. **Background Transcription Queue**
   - Currently: Synchronous transcription blocks UI
   - **Would require:** Queue abstraction + worker pool

### Ripple Effect Zones

**High Ripple Risk:**

1. **Changing Transcription Engine**
   - Affects: `SpeechController`, `speech_ui.py`, settings, preferences
   - **Why:** Engine selection logic scattered across layers

2. **Changing Audio Format**
   - Affects: `AudioManager`, `SpeechController`, file handling
   - **Why:** Format assumptions embedded throughout

3. **Adding New Recording Trigger**
   - Affects: `HotkeyManager`, `SpeechController`, UI callbacks
   - **Why:** Hotkey logic tightly coupled to recording logic

**Low Ripple Risk:**

1. **Changing UI Layout**
   - Affects: Only UI layer due to good separation
   - **Why:** Layout system well-abstracted

2. **Adding Platform Support**
   - Affects: Only platform abstraction modules
   - **Why:** Platform differences isolated

3. **Changing Persistence Mechanism**
   - Affects: Only `SettingsManager`
   - **Why:** Repository pattern shields consumers

---

## Testing & Maintainability Impact

### Test Friendliness

**What Tests Well ✅**

1. **Core Services**
   - `SettingsManager`, `CleanupManager`, `AudioManager` have clear interfaces
   - Easy to mock and test in isolation
   - Good test coverage in `tests/unit/`

2. **Settings System**
   - Schema validation logic independently testable
   - Race condition tests exist (`test_settings_race.py`)

3. **Platform Abstraction**
   - Feature detection testable
   - Cross-platform compatibility tests exist

**What Tests Poorly ❌**

1. **SpeechController**
   - Requires mocking: audio, hotkeys, models, file system, callbacks
   - Tests become fragile and hard to maintain
   - Integration tests required for most scenarios

2. **SpeechApp**
   - Circular dependencies make unit testing impossible
   - Must construct entire object graph (MainWindow + Controller + Managers)
   - Tests are slow and integration-heavy

3. **UI Components with parent_app**
   - `RecordTab` requires full `SpeechApp` instance
   - Cannot test tab logic independently

### Maintainability Pain Points

1. **Large Files**
   - `PreferencesDialog` (1465 lines): Hard to navigate, slow to understand
   - `SpeechController` (786 lines): Difficult to modify without breaking things
   - `speech_ui.py` (1200+ lines): Mixed concerns make changes risky

2. **Implicit Dependencies**
   - Global singleton access hides dependencies
   - Makes understanding data flow difficult
   - Complicates testing

3. **Callback Hell**
   - Controller ↔ UI communication via callbacks
   - Hard to trace execution flow
   - Difficult to debug async issues

4. **Inconsistent Organization**
   - UI components scattered between `ui/`, `ui/components/`, `ui/widgets/`
   - No clear rules for where new code goes

### Onboarding Friction

**For New Developers:**

1. **Where do I start?**
   - ✅ Good: README provides clear project structure
   - ❌ Bad: Root-level files create confusion about entry points

2. **How do I add a feature?**
   - ✅ Good: Core services have clear boundaries
   - ❌ Bad: Unclear whether to modify controller, UI, or both

3. **How do I test my changes?**
   - ✅ Good: Test organization is clear
   - ❌ Bad: Integration tests required for most features due to tight coupling

4. **How does data flow?**
   - ✅ Good: Layers are clear (UI → Controller → Core)
   - ❌ Bad: Callbacks make flow hard to trace

---

## Recommended Next Steps

### Priority 1: Must Fix (High Leverage, Low Risk)

#### 1. Reorganize Root-Level Files
**Effort:** Small  
**Impact:** Reduces confusion, improves discoverability  
**Team Alignment:** Just move files, update imports

**Action:**
```bash
# Create app package
mkdir -p app/controllers app/bootstrap

# Move files
mv speech_controller.py app/controllers/
mv speech_ui.py app/controllers/
mv main.py app/bootstrap/
mv main_with_splash.py app/bootstrap/
mv splash_screen.py ui/widgets/

# Move utilities
mv create_sounds.py scripts/tools/
mv diagnose_windows_audio.py scripts/tools/
mv fix_windows_audio.py scripts/tools/
```

**Benefit:** Immediate clarity on code organization without changing any logic

---

#### 2. Split PreferencesDialog by Tab
**Effort:** Small  
**Impact:** Enables parallel development, easier testing  
**Team Alignment:** None required (internal refactor)

**Action:**
```python
# Create structure
ui/dialogs/preferences/
    preferences_dialog.py    # Main container
    general_tab.py
    audio_tab.py
    behavior_tab.py
    transcription_tab.py
    advanced_tab.py
```

**Migration:** Keep old file temporarily, deprecate gradually

---

### Priority 2: Improve When Scaling (Medium Leverage)

#### 3. Extract Transcription Engine Abstraction
**Effort:** Medium  
**Impact:** Makes adding engines easy, reduces controller complexity  
**Team Alignment:** Define engine interface contract

**Action:**
```python
# Create transcription domain
core/transcription/
    engine.py           # Abstract base + factory
    whisper_engine.py
    faster_whisper_engine.py
    model_manager.py

# Interface
class TranscriptionEngine(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str, **kwargs) -> str:
        pass
```

**Benefit:** Simplifies adding new engines (e.g., local models, cloud APIs)

---

#### 4. Break SpeechController God Object
**Effort:** Large  
**Impact:** Dramatically improves testability and maintainability  
**Team Alignment:** Requires architectural discussion

**Action:**
```python
# Split responsibilities
core/recording/
    recording_coordinator.py    # Orchestrates recording
    audio_file_handler.py       # Temp file management

app/controllers/
    speech_controller.py        # Slim facade
    
# Inject dependencies
class SpeechController:
    def __init__(
        self,
        engine: TranscriptionEngine,
        recorder: RecordingCoordinator,
        file_handler: AudioFileHandler,
        ...
    ):
        self.engine = engine
        self.recorder = recorder
        ...
```

**Migration:** 
1. Extract model management (week 1)
2. Extract engine abstraction (week 2)
3. Extract recording coordinator (week 3)
4. Refactor controller to facade (week 4)

---

#### 5. Introduce Mediator for UI ↔ Controller
**Effort:** Medium  
**Impact:** Breaks circular dependencies, improves testability  
**Team Alignment:** Requires architectural discussion

**Action:**
```python
class ApplicationMediator:
    """Coordinates between UI and business logic"""
    
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    transcription_complete = pyqtSignal(str)
    
    def start_recording(self):
        self.controller.start_recording()
        
    def stop_recording(self):
        self.controller.stop_recording()
```

**Benefit:** Testable in isolation, clear contracts, no circular deps

---

### Priority 3: Long-Term Evolution (Low Priority)

#### 6. Formalize Event Contracts
**Effort:** Large  
**Impact:** Makes event flow explicit and type-safe  
**Team Alignment:** Requires team discussion

Define event types:

```python
# app/events.py
class AppEvent:
    pass

class RecordingStarted(AppEvent):
    timestamp: datetime

class RecordingCompleted(AppEvent):
    audio_path: str
    duration: float

class TranscriptionCompleted(AppEvent):
    text: str
    confidence: float
```

---

#### 7. Replace Global Singletons with Dependency Injection
**Effort:** Large  
**Impact:** Improves testability, makes dependencies explicit  
**Team Alignment:** Requires team discussion

Introduce application context:

```python
@dataclass
class AppContext:
    logger: Logger
    settings: SettingsManager
    cleanup: CleanupManager
    monitor: PerformanceMonitor
    
    @classmethod
    def create_default(cls) -> 'AppContext':
        return cls(
            logger=get_logger("whiz"),
            settings=SettingsManager(),
            cleanup=CleanupManager(),
            monitor=PerformanceMonitor(),
        )
```

---

## Open Questions / Assumptions

### Unclear Design Intent

1. **Why are some UI components in `ui/` root vs. `ui/components/` vs. `ui/widgets/`?**
   - **Assumption:** Historical evolution, no consistent rule
   - **Need:** Establish clear organization principles

2. **Is `SpeechController` intended as a facade or a coordinator?**
   - **Observation:** Currently acts as both
   - **Need:** Clarify intended responsibility

3. **Why does `MainWindow` manage sound effects?**
   - **Assumption:** Convenience, but violates SRP
   - **Need:** Move to audio service or UI component

4. **Is the `app/` layer missing by design or oversight?**
   - **Assumption:** Oversight - orchestration layer not formalized
   - **Need:** Create explicit app layer

### Architecture Decisions That Need Documentation

1. **Why PyQt5 over PyQt6?**
   - **Assumption:** Stability, wider support
   - **Document:** In `docs/architecture/decisions.md`

2. **Why openai-whisper as default over faster-whisper?**
   - **Finding:** Code comments mention PyQt/ONNX conflicts
   - **Document:** Known issues and tradeoffs

3. **Why hold mode as default over toggle mode?**
   - **Assumption:** Better UX for voice transcription
   - **Document:** UX rationale

4. **Why global singletons for infrastructure services?**
   - **Assumption:** Convenience for logging/monitoring
   - **Evaluate:** Whether benefits outweigh testability costs

---

## Summary & Verdict

### Overall Assessment: **Good Foundation, Needs Refactoring**

**Strengths:**
- ✅ Clean layering (UI → Orchestration → Core)
- ✅ Excellent core services (settings, cleanup, platform abstraction)
- ✅ Comprehensive test coverage
- ✅ Strong resource management
- ✅ Cross-platform design done well

**Critical Issues:**
- ❌ God object (`SpeechController`) violates SRP
- ❌ Tight coupling between UI and controller
- ❌ Mixed responsibilities at root level
- ❌ Circular dependencies (UI ↔ Controller)

**Recommendation:**

The codebase is **maintainable today** but will become **difficult to evolve** without refactoring. The architecture is fundamentally sound, but tactical refactoring is needed to prevent technical debt accumulation.

**Immediate Actions:**
1. Reorganize root-level files (low risk, high clarity)
2. Split `PreferencesDialog` (enables parallel work)
3. Plan `SpeechController` decomposition (schedule over 4 weeks)

**Long-Term Vision:**
- Formalize orchestration layer (`app/` package)
- Extract domain logic (transcription, recording)
- Introduce mediator to break circular dependencies
- Make dependencies explicit (reduce global singletons)

**Timeline:**
- **Month 1:** Priority 1 items (reorganize, split dialog)
- **Month 2-3:** Priority 2 items (extract transcription, break god object)
- **Month 4+:** Priority 3 items (events, DI) - only if team grows or features require

**Risk Level:** Low to Medium
- Core services are solid
- Tests provide safety net
- Changes can be incremental
- No need for "big bang" rewrite

---

**Review Completed By:** Senior Software Architect  
**Review Date:** February 8, 2026  
**Next Review Recommended:** After Priority 1-2 refactoring (3-6 months)
