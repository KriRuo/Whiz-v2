# Whiz Voice-to-Text System Architecture

## System Component Flow Diagram

```mermaid
graph TB
    %% User Interface Layer
    subgraph "UI Layer"
        MW[MainWindow]
        PD[PreferencesDialog]
        VI[VisualIndicator]
        MC[MicCircle]
        WT[WaveformWidget]
        ST[SplashScreen]
    end
    
    %% Core Application Layer
    subgraph "Core Layer"
        SC[SpeechController]
        SM[SettingsManager]
        HM[HotkeyManager]
        AM[AudioManager]
        SS[SettingsSchema]
    end
    
    %% External Dependencies
    subgraph "External Services"
        W[Whisper Engine]
        QS[QSettings Registry]
        SD[SoundDevice]
        PK[PyKeyboard]
    end
    
    %% Data Flow
    MW --> SC
    MW --> SM
    PD --> SM
    SC --> HM
    SC --> AM
    SC --> W
    SM --> SS
    SM --> QS
    AM --> SD
    HM --> PK
    
    %% UI Updates
    SC --> VI
    SC --> MC
    SC --> WT
    SM --> PD
    
    %% Settings Flow
    SS --> SM
    QS --> SM
    SM --> MW
    SM --> SC
    
    %% Audio Flow
    SD --> AM
    AM --> SC
    SC --> W
    W --> SC
    
    %% Hotkey Flow
    PK --> HM
    HM --> SC
    
    %% Styling
    classDef uiClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef coreClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef externalClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class MW,PD,VI,MC,WT,ST uiClass
    class SC,SM,HM,AM,SS coreClass
    class W,QS,SD,PK externalClass
```

## Settings Management Flow

```mermaid
sequenceDiagram
    participant U as User
    participant PD as PreferencesDialog
    participant SM as SettingsManager
    participant SS as SettingsSchema
    participant QS as QSettings
    participant SC as SpeechController
    
    U->>PD: Open Preferences
    PD->>SM: load_all() (cached)
    SM-->>PD: Return cached settings
    PD->>PD: Populate UI
    
    U->>PD: Change Setting
    PD->>SM: set(key, value)
    SM->>SS: validate_setting()
    SS-->>SM: Validated value
    SM->>QS: Store in registry
    SM->>SM: Invalidate cache
    SM-->>PD: Success
    
    PD->>SC: Emit settings_changed signal
    SC->>SC: Apply new settings
    
    Note over SM: Cache hit on subsequent loads
    Note over SS: Migration handles old settings
```

## Audio Processing Flow

```mermaid
sequenceDiagram
    participant U as User
    participant HM as HotkeyManager
    participant SC as SpeechController
    participant AM as AudioManager
    participant W as Whisper Engine
    participant MW as MainWindow
    
    U->>HM: Press Hotkey
    HM->>SC: hotkey_pressed()
    SC->>AM: start_recording()
    AM->>AM: Create audio stream
    SC->>MW: Update UI (recording)
    
    U->>HM: Release Hotkey
    HM->>SC: hotkey_released()
    SC->>AM: stop_recording()
    AM->>AM: Save audio file
    SC->>W: transcribe(audio_file)
    W-->>SC: Transcribed text
    SC->>MW: Update UI (idle)
    SC->>SC: Auto-paste text
```

## Performance Optimizations

```mermaid
graph LR
    subgraph "Before Optimization"
        A1[load_all()] --> A2[Validate All Settings]
        A2 --> A3[Apply Migration]
        A3 --> A4[Return Settings]
        A1 --> A5[load_all()] --> A2
    end
    
    subgraph "After Optimization"
        B1[load_all()] --> B2{Cache Valid?}
        B2 -->|Yes| B3[Return Cached Settings]
        B2 -->|No| B4[Validate & Migrate]
        B4 --> B5[Update Cache]
        B5 --> B6[Return Settings]
        B7[set()] --> B8[Invalidate Cache]
    end
    
    classDef beforeClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef afterClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    
    class A1,A2,A3,A4,A5 beforeClass
    class B1,B2,B3,B4,B5,B6,B7,B8 afterClass
```
