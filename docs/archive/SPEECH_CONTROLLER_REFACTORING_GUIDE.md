# Speech Processing Engine Refactoring - Slice 3 Guide

## Overview

This document describes how to refactor `speech_controller.py` to use the new `TranscriptionService` and `RecordingService` as an orchestrator pattern.

## Architecture

### Before Refactoring
```
SpeechController (1108 lines)
├── Model loading logic
├── Transcription logic
├── Audio recording logic  
├── Hotkey management
├── State management
├── Error handling
└── UI callbacks
```

### After Refactoring
```
SpeechController (Orchestrator)
├── TranscriptionService ✅
├── RecordingService ✅
├── HotkeyManager (existing)
└── Event coordination
```

## Refactoring Steps

### Step 1: Add Service Initialization

Replace direct AudioManager and model initialization with services:

```python
class SpeechController:
    def __init__(self, hotkey: str = "alt gr", model_size: str = "tiny", 
                 auto_paste: bool = True, language: str = None, 
                 temperature: float = 0.5, engine: str = None):
        
        # Initialize services
        from core.transcription_service import TranscriptionService, TranscriptionConfig
        from core.recording_service import RecordingService, RecordingConfig
        
        # Create transcription service
        transcription_config = TranscriptionConfig(
            model_size=model_size,
            engine=engine or "faster",
            language=language or "auto",
            temperature=temperature
        )
        self.transcription_service = TranscriptionService(transcription_config)
        self.transcription_service.set_status_callback(self._update_status)
        
        # Create recording service
        recording_config = RecordingConfig(
            sample_rate=16000,
            channels=1,
            chunk_size=2048
        )
        self.recording_service = RecordingService(recording_config)
        self.recording_service.set_status_callback(self._update_status)
        self.recording_service.set_audio_level_callback(self._on_audio_level)
        self.recording_service.set_state_change_callback(self._on_recording_state_change)
        
        # Keep existing hotkey manager initialization
        self.hotkey_manager = HotkeyManager()
        # ... rest of initialization
```

### Step 2: Simplify Recording Methods

Replace direct audio_manager calls with recording_service:

```python
def start_recording(self):
    """Start recording using RecordingService"""
    if not self.recording_service.is_recording():
        success = self.recording_service.start_recording()
        if success:
            self._notify_recording_started()
        return success
    return False

def stop_recording(self):
    """Stop recording and transcribe"""
    if self.recording_service.is_recording():
        # Stop recording and get audio file
        result = self.recording_service.stop_recording()
        
        if result.success:
            self._notify_recording_stopped()
            # Transcribe the audio
            self._transcribe_audio(result.audio_path)
        else:
            logger.error(f"Recording failed: {result.error}")
            self._update_status(f"Recording error: {result.error}")
```

### Step 3: Simplify Transcription Methods

Replace direct model management with transcription_service:

```python
def _transcribe_audio(self, audio_path: str):
    """Transcribe audio file using TranscriptionService"""
    # Transcribe asynchronously to avoid blocking
    threading.Thread(
        target=self._do_transcription,
        args=(audio_path,),
        daemon=True
    ).start()

def _do_transcription(self, audio_path: str):
    """Perform transcription in background thread"""
    result = self.transcription_service.transcribe(audio_path)
    
    if result.success:
        # Add to transcript log
        transcript_entry = {
            "text": result.text,
            "timestamp": datetime.now().isoformat(),
            "duration": result.duration_seconds,
            "model_info": result.model_info
        }
        self.transcript_log.append(transcript_entry)
        
        # Notify UI
        if self.transcript_callback:
            self.transcript_callback(transcript_entry)
        
        # Auto-paste if enabled
        if self.auto_paste:
            self._auto_paste_text(result.text)
    else:
        logger.error(f"Transcription failed: {result.error}")
        self._update_status(f"Transcription error: {result.error}")
```

### Step 4: Remove Redundant Code

Delete or deprecate these methods (now handled by services):
- `_ensure_model_loaded()` → Use `transcription_service.ensure_model_loaded()`
- `_load_model_implementation()` → Internal to TranscriptionService
- `_load_faster_whisper()` → Internal to TranscriptionService  
- `_load_openai_whisper()` → Internal to TranscriptionService
- `_transcribe_faster_whisper()` → Internal to TranscriptionService
- `_transcribe_openai_whisper()` → Internal to TranscriptionService
- Direct AudioManager manipulation → Use RecordingService

### Step 5: Update Settings Management

Modify settings to update services:

```python
def update_model_settings(self, model_size: str = None, engine: str = None, 
                          language: str = None, temperature: float = None):
    """Update transcription settings"""
    # Create new config with updated settings
    new_config = TranscriptionConfig(
        model_size=model_size or self.transcription_service.config.model_size,
        engine=engine or self.transcription_service.config.engine,
        language=language or self.transcription_service.config.language,
        temperature=temperature if temperature is not None else self.transcription_service.config.temperature
    )
    
    # Replace service with new configuration
    old_service = self.transcription_service
    self.transcription_service = TranscriptionService(new_config)
    self.transcription_service.set_status_callback(self._update_status)
    
    # Clean up old service
    old_service.unload_model()

def set_audio_device(self, device_index: Optional[int] = None) -> bool:
    """Set audio input device"""
    return self.recording_service.select_device(device_index)
```

### Step 6: Add Service Cleanup

Update cleanup to use services:

```python
def cleanup(self):
    """Clean up all services and resources"""
    logger.info("Starting SpeechController cleanup...")
    
    try:
        # Clean up recording service
        if hasattr(self, 'recording_service'):
            self.recording_service.cleanup()
        
        # Clean up transcription service
        if hasattr(self, 'transcription_service'):
            self.transcription_service.unload_model()
        
        # Clean up hotkey manager (existing)
        if hasattr(self, 'hotkey_manager'):
            self.hotkey_manager.stop()
        
        logger.info("SpeechController cleanup complete")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
```

## Benefits of Refactoring

### 1. Separation of Concerns
- **Before**: SpeechController does everything
- **After**: Clear delegation to specialized services

### 2. Testability
- **Before**: Hard to test model loading without actual models
- **After**: Can mock TranscriptionService and RecordingService

### 3. Maintainability
- **Before**: 1108 lines of mixed concerns
- **After**: ~400 lines of orchestration logic

### 4. Reusability
- **Before**: Tightly coupled to SpeechController
- **After**: Services can be used in other contexts (CLI tools, API servers, etc.)

### 5. Error Handling
- **Before**: Mixed error handling throughout
- **After**: Services handle their own errors with structured responses

## Migration Strategy

### Phase 1: Add Services (Non-Breaking)
1. Add TranscriptionService and RecordingService initialization
2. Keep existing methods working
3. Add tests for new code paths

### Phase 2: Delegate to Services (Breaking Changes Controlled)
1. Update internal methods to use services
2. Keep public API unchanged
3. Run full test suite

### Phase 3: Clean Up (Optimization)
1. Remove redundant code
2. Simplify SpeechController
3. Update documentation

## Testing Strategy

### Unit Tests
```python
def test_speech_controller_with_services(self):
    """Test that SpeechController correctly uses services"""
    mock_transcription = Mock(spec=TranscriptionService)
    mock_recording = Mock(spec=RecordingService)
    
    controller = SpeechController()
    controller.transcription_service = mock_transcription
    controller.recording_service = mock_recording
    
    # Test recording workflow
    controller.start_recording()
    mock_recording.start_recording.assert_called_once()
    
    controller.stop_recording()
    mock_recording.stop_recording.assert_called_once()
```

### Integration Tests
```python
def test_end_to_end_with_services(self):
    """Test complete workflow with real services"""
    controller = SpeechController(
        model_size="tiny",
        engine="faster"
    )
    
    # Ensure services are initialized
    assert controller.transcription_service is not None
    assert controller.recording_service is not None
    
    # Test that services are properly configured
    assert controller.transcription_service.config.model_size == "tiny"
    assert controller.recording_service.config.sample_rate == 16000
```

## Backward Compatibility

To maintain backward compatibility during migration:

1. **Keep existing public API**:
   ```python
   def set_model_size(self, model_size: str):
       """Legacy method - delegates to service"""
       self.update_model_settings(model_size=model_size)
   ```

2. **Preserve property accessors**:
   ```python
   @property
   def model_size(self) -> str:
       return self.transcription_service.config.model_size
   
   @property
   def listening(self) -> bool:
       return self.recording_service.is_recording()
   ```

3. **Keep callback signatures**:
   - Existing callbacks should continue to work
   - New services use same callback patterns

## Next Steps

After completing Slice 3:
1. Run existing test suite to ensure no regressions
2. Update integration tests to validate new architecture
3. Measure performance to ensure no degradation
4. Update documentation
5. Proceed to Slice 4 (Observability & Configuration)

## Conclusion

This refactoring transforms SpeechController from a monolithic "do-everything" class into a clean orchestrator that coordinates specialized services. Each service has a single responsibility, is independently testable, and can be reused in different contexts. The result is more maintainable, testable, and scalable code that follows backend engineering best practices.
