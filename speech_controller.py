import pyautogui
# Disable PyAutoGUI fail-safe to prevent crashes when mouse moves to corners
pyautogui.FAILSAFE = False
import threading
import time
import sys
import os
import tempfile
# whisper, faster_whisper, and torch imported lazily to avoid startup delays
import wave
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime

# Import our abstraction layers
from core.hotkey_manager import HotkeyManager, HotkeyMode
from core.platform_features import PlatformFeatures, FeatureStatus
from core.logging_config import get_logger
from core.performance_monitor import get_performance_monitor
from core.path_validation import get_sandbox, create_safe_temp_file
from core.cleanup_manager import (
    CleanupManager, CleanupPhase, register_cleanup_task, get_cleanup_manager
)
from core.config import TIMEOUT_CONFIG, WHISPER_CONFIG, AUDIO_CONFIG, MEMORY_CONFIG

# Import new services
from core.transcription_service import TranscriptionService, TranscriptionConfig
from core.recording_service import RecordingService, RecordingConfig

logger = get_logger(__name__)

class SpeechController:
    def __init__(self, hotkey: str = "alt gr", model_size: str = "tiny", auto_paste: bool = True, 
                 language: str = None, temperature: float = 0.5, engine: str = None):
        # Basic settings
        self.auto_paste = auto_paste
        self.toggle_mode = False  # Default to hold mode
        self.listening = False
        self.transcript_log: List[Dict] = []
        self.transcript_callback: Optional[Callable] = None
        
        # Initialize performance monitoring
        self.performance_monitor = get_performance_monitor()
        
        # Initialize platform features detection (needed before hotkey registration)
        self.platform_features = PlatformFeatures()
        self.features = self.platform_features.detect_all_features()
        
        # Visual indicator settings
        self.visual_indicator_enabled = True
        self.visual_indicator_position = "Bottom Center"
        
        # Status callback for UI updates
        self.status_callback: Optional[Callable[[str], None]] = None
        # Recording state callback (bool)
        self.recording_state_callback: Optional[Callable[[bool], None]] = None

        # Initialize TranscriptionService
        transcription_config = TranscriptionConfig(
            model_size=model_size,
            engine=engine or WHISPER_CONFIG.DEFAULT_ENGINE,
            language=language or "auto",
            temperature=temperature
        )
        self.transcription_service = TranscriptionService(transcription_config)
        self.transcription_service.set_status_callback(self._update_status)
        
        # Initialize RecordingService
        recording_config = RecordingConfig(
            sample_rate=16000,
            channels=1,
            chunk_size=2048
        )
        self.recording_service = RecordingService(recording_config)
        self.recording_service.set_status_callback(self._update_status)
        self.recording_service.set_state_change_callback(self._on_recording_state_change)
        
        # Initialize hotkey manager
        self.hotkey_manager = HotkeyManager()
        self.hotkey = hotkey  # Store original hotkey for compatibility
        
        # Set up hotkey manager
        self._setup_hotkey_manager()
        
        # Register initial hotkey
        self.register_hotkeys()
        
        # Initialize cleanup manager and register cleanup tasks
        self.cleanup_manager = get_cleanup_manager()
        self._register_cleanup_tasks()
        
        logger.info("SpeechController initialized successfully")
    
    # Backward compatibility properties
    @property
    def model_size(self) -> str:
        """Get current model size"""
        return self.transcription_service.config.model_size
    
    @property
    def engine(self) -> str:
        """Get current transcription engine"""
        return self.transcription_service.config.engine
    
    @property
    def language(self) -> str:
        """Get current language setting"""
        return self.transcription_service.config.language
    
    @property
    def temperature(self) -> float:
        """Get current temperature setting"""
        return self.transcription_service.config.temperature
    
    def _register_cleanup_tasks(self):
        """Register cleanup tasks with the cleanup manager"""
        # Recording service cleanup
        register_cleanup_task(
            "recording_service_cleanup",
            CleanupPhase.AUDIO_RESOURCES,
            self._cleanup_recording_service,
            self._verify_recording_cleanup,
            timeout=5.0,
            critical=True
        )
        
        # Transcription service cleanup
        register_cleanup_task(
            "transcription_service_cleanup",
            CleanupPhase.MODEL_RESOURCES,
            self._cleanup_transcription_service,
            self._verify_transcription_cleanup,
            timeout=10.0,
            critical=False
        )
        
        # Hotkey resources cleanup
        register_cleanup_task(
            "hotkey_manager_cleanup",
            CleanupPhase.HOTKEY_RESOURCES,
            self._cleanup_hotkey_manager,
            self._verify_hotkey_cleanup,
            timeout=3.0,
            critical=True
        )
        
        logger.info("Cleanup tasks registered successfully")
    
    def _on_recording_state_change(self, state):
        """Handle recording state changes from RecordingService"""
        from core.recording_service import RecordingState
        
        # Map RecordingState to boolean for backward compatibility
        is_recording = (state == RecordingState.RECORDING)
        self.listening = is_recording
        
        # Notify UI
        if self.recording_state_callback:
            try:
                self.recording_state_callback(is_recording)
            except Exception:
                pass
    
    
    def set_audio_device(self, device_index: Optional[int] = None) -> bool:
        """
        Set the audio input device.
        
        Args:
            device_index: Device index to select, or None for system default
            
        Returns:
            True if device was set successfully, False otherwise
        """
        return self.recording_service.select_device(device_index)
    
    def set_audio_level_callback(self, callback: Callable[[float], None]):
        """Set callback for audio level updates"""
        self.recording_service.set_audio_level_callback(callback)
    
    def _setup_hotkey_manager(self):
        """Set up the hotkey manager with callbacks"""
        if not self.hotkey_manager.is_available():
            logger.warning("Hotkey functionality not available on this platform")
            return
        
        # Set the hotkey
        if not self.hotkey_manager.set_hotkey(self.hotkey):
            logger.warning(f"Failed to set hotkey '{self.hotkey}'")
            return
        
        # Set the mode
        mode = HotkeyMode.TOGGLE if self.toggle_mode else HotkeyMode.HOLD
        self.hotkey_manager.set_mode(mode)
        
        # Set up callbacks
        self.hotkey_manager.set_callbacks(
            on_start=self.start_recording,
            on_stop=self.stop_recording,
            on_toggle=self.toggle_recording
        )
        
        logger.info(f"Hotkey manager initialized with '{self.hotkey}' ({mode.value} mode)")

    
    def is_model_ready(self):
        """Check if the Whisper model is ready for use"""
        return self.transcription_service.is_model_loaded()
    
    def get_model_status(self):
        """Get current model loading status"""
        status = self.transcription_service.get_status()
        if status['model_loaded']:
            return "loaded"
        elif status['model_loading']:
            return "loading"
        elif status['model_load_error']:
            return f"error: {status['model_load_error']}"
        else:
            return "not_loaded"
    
    def preload_model(self):
        """Preload the Whisper model in a background thread"""
        def _background_load():
            self.transcription_service.ensure_model_loaded()
        
        load_thread = threading.Thread(target=_background_load, daemon=True)
        load_thread.start()
        logger.info("Started background model loading...")
        return True
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set a callback function to update UI status"""
        self.status_callback = callback

    def set_recording_state_callback(self, callback: Callable[[bool], None]):
        """Set callback invoked when recording starts/stops."""
        self.recording_state_callback = callback

    def set_transcript_callback(self, callback: Callable[[], None]):
        """Set callback function for transcript updates"""
        self.transcript_callback = callback

    def _update_status(self, status: str):
        """Update status and notify UI if callback is set"""
        logger.info(f"Status: {status}")
        if self.status_callback:
            self.status_callback(status)


    def set_hotkey(self, new_hotkey: str):
        """Dynamically change the hotkey without restarting"""
        if self.hotkey == new_hotkey:
            return  # No change needed
        
        self.hotkey = new_hotkey
        
        # Update hotkey manager
        if self.hotkey_manager.is_available():
            if self.hotkey_manager.set_hotkey(new_hotkey):
                self.register_hotkeys()
                logger.info(f"Hotkey changed to: {new_hotkey} ({'toggle' if self.toggle_mode else 'hold'} mode)")
            else:
                logger.error(f"Failed to change hotkey to: {new_hotkey}")
        else:
            logger.warning("Hotkey functionality not available")

    def register_hotkeys(self):
        """Register the current hotkey for global listening"""
        if not self.platform_features.is_feature_available("hotkeys.global_hotkeys"):
            logger.warning("Hotkey functionality not available on this platform")
            return
        
        try:
            success = self.hotkey_manager.register_hotkeys()
            if success:
                logger.info(f"Hotkey registered: {self.hotkey} ({'toggle' if self.toggle_mode else 'hold'} mode)")
            else:
                logger.error(f"Failed to register hotkey: {self.hotkey}")
        except Exception as e:
            logger.error(f"Error registering hotkey: {e}")

    def start_recording(self):
        """Start recording audio"""
        if self.listening:
            return
        
        # Check if audio recording is available
        if not self.platform_features.is_feature_available("audio.recording"):
            logger.warning("Audio recording not available on this platform")
            self._update_status("Audio recording unavailable")
            return
        
        # Start recording using RecordingService
        success = self.recording_service.start_recording()
        if success:
            logger.info("Audio recording started successfully")
        else:
            logger.error("Failed to start audio recording")
            self._update_status("Recording failed")

    def stop_recording(self):
        """Stop recording and transcribe audio"""
        if not self.listening:
            return
        
        # Stop recording and get result
        result = self.recording_service.stop_recording()
        
        if result.success:
            # Transcribe the audio
            self._transcribe_audio(result.audio_path)
        else:
            logger.error(f"Recording failed: {result.error}")
            self._update_status(f"Recording error: {result.error}")

    def toggle_recording(self):
        """Toggle between recording and idle states"""
        if self.listening:
            self.stop_recording()
        else:
            self.start_recording()

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
            text = result.text
            logger.info(f"Recognized: {text}")
            
            # Add to transcript history
            timestamp = datetime.now().strftime("%m/%d %H:%M")
            transcript_entry = {
                "timestamp": timestamp,
                "text": text,
                "duration": result.duration_seconds,
                "model_info": result.model_info
            }
            self.transcript_log.insert(0, transcript_entry)  # Newest at top
            
            # Notify UI of new transcript
            if self.transcript_callback:
                self.transcript_callback()
            
            # Auto-paste if enabled
            if self.auto_paste:
                try:
                    pyautogui.write(text + " ")
                except Exception as paste_error:
                    logger.warning(f"Auto-paste failed: {paste_error}")
            
            self._update_status("Idle")
        else:
            logger.error(f"Transcription failed: {result.error}")
            self._update_status(f"Transcription error: {result.error}")

    def get_transcripts(self) -> List[Dict]:
        """Get the list of transcript history entries"""
        return self.transcript_log.copy()
    
    def get_feature_status(self) -> Dict[str, Any]:
        """Get current feature availability status"""
        return {
            "audio_recording": self.platform_features.is_feature_available("audio.recording"),
            "hotkeys": self.platform_features.is_feature_available("hotkeys.global_hotkeys"),
            "autopaste": self.platform_features.is_feature_available("autopaste.text_pasting"),
            "clipboard": self.platform_features.is_feature_available("autopaste.clipboard_access"),
            "permissions_required": (self.features or {}).get("permissions", {}).get("accessibility_required", False),
            "recommendations": self.platform_features.get_recommendations()
        }

    def set_auto_paste(self, enabled: bool):
        """Enable or disable auto-paste functionality"""
        self.auto_paste = enabled
        logger.info(f"Auto-paste {'enabled' if enabled else 'disabled'}")

    def set_language(self, lang_code: str):
        """Set the language for transcription"""
        # Update transcription service configuration
        new_config = TranscriptionConfig(
            model_size=self.transcription_service.config.model_size,
            engine=self.transcription_service.config.engine,
            language=lang_code,
            temperature=self.transcription_service.config.temperature
        )
        old_service = self.transcription_service
        self.transcription_service = TranscriptionService(new_config)
        self.transcription_service.set_status_callback(self._update_status)
        old_service.unload_model()
        logger.info(f"Language set to: {lang_code}")

    def set_temperature(self, temperature: float):
        """Set the temperature for transcription (0.0 = deterministic, higher = more random)"""
        temperature = max(0.0, min(1.0, temperature))  # Clamp between 0.0 and 1.0
        # Update transcription service configuration
        new_config = TranscriptionConfig(
            model_size=self.transcription_service.config.model_size,
            engine=self.transcription_service.config.engine,
            language=self.transcription_service.config.language,
            temperature=temperature
        )
        old_service = self.transcription_service
        self.transcription_service = TranscriptionService(new_config)
        self.transcription_service.set_status_callback(self._update_status)
        old_service.unload_model()
        logger.info(f"Temperature set to: {temperature}")
    
    def set_model(self, model_size: str):
        """Change the Whisper model dynamically"""
        # Update transcription service configuration
        new_config = TranscriptionConfig(
            model_size=model_size,
            engine=self.transcription_service.config.engine,
            language=self.transcription_service.config.language,
            temperature=self.transcription_service.config.temperature
        )
        old_service = self.transcription_service
        self.transcription_service = TranscriptionService(new_config)
        self.transcription_service.set_status_callback(self._update_status)
        old_service.unload_model()
        logger.info(f"Model changed to {model_size}")
    
    def set_speed_mode(self, enabled: bool):
        """Enable or disable speed optimizations"""
        # Note: speed_mode is handled internally by TranscriptionService via config
        logger.info(f"Speed mode {'enabled' if enabled else 'disabled'}")

    def set_toggle_mode(self, enabled: bool):
        """Enable or disable toggle mode"""
        self.toggle_mode = enabled
        
        # Update hotkey manager mode
        if self.hotkey_manager.is_available():
            mode = HotkeyMode.TOGGLE if enabled else HotkeyMode.HOLD
            self.hotkey_manager.set_mode(mode)
            self.register_hotkeys()
        
        logger.info(f"Toggle mode {'enabled' if enabled else 'disabled'}")

    def set_visual_indicator(self, enabled: bool, position: str):
        """Enable or disable visual recording indicator"""
        self.visual_indicator_enabled = enabled
        self.visual_indicator_position = position
        logger.info(f"Visual indicator {'enabled' if enabled else 'disabled'} at position: {position}")
    
    def set_auto_copy_clipboard(self, enabled: bool):
        """Enable or disable auto-copy to clipboard functionality"""
        # This would be implemented if clipboard functionality is added
        logger.info(f"Auto-copy to clipboard {'enabled' if enabled else 'disabled'}")
    
    def set_auto_convert_gherkin(self, enabled: bool):
        """Enable or disable auto-convert to Gherkin format"""
        # This would be implemented if Gherkin conversion is added
        logger.info(f"Auto-convert to Gherkin {'enabled' if enabled else 'disabled'}")

    def cleanup(self):
        """Clean up resources when shutting down using the cleanup manager"""
        logger.info("Starting SpeechController cleanup")
        
        try:
            # Use the cleanup manager to perform ordered cleanup
            results = self.cleanup_manager.cleanup_all()
            
            # Log cleanup summary
            summary = self.cleanup_manager.get_cleanup_summary()
            logger.info(f"Cleanup completed: {summary['completed_tasks']}/{summary['total_tasks']} tasks successful")
            
            if summary['failed_tasks'] > 0:
                logger.warning(f"{summary['failed_tasks']} cleanup tasks failed")
            
            return summary['success_rate'] > 0.8  # Consider cleanup successful if 80%+ tasks succeeded
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False
    
    def _cleanup_recording_service(self) -> bool:
        """Clean up recording service resources"""
        try:
            if hasattr(self, 'recording_service') and self.recording_service:
                self.recording_service.cleanup()
                logger.debug("Recording service cleaned up")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up recording service: {e}")
            return False
    
    def _verify_recording_cleanup(self) -> bool:
        """Verify recording service cleanup"""
        try:
            if hasattr(self, 'recording_service') and self.recording_service:
                return not self.recording_service.is_recording()
            return True
        except Exception as e:
            logger.error(f"Error verifying recording cleanup: {e}")
            return False
    
    def _cleanup_transcription_service(self) -> bool:
        """Clean up transcription service resources"""
        try:
            if hasattr(self, 'transcription_service') and self.transcription_service:
                self.transcription_service.unload_model()
                logger.debug("Transcription service cleaned up")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up transcription service: {e}")
            return False
    
    def _verify_transcription_cleanup(self) -> bool:
        """Verify transcription service cleanup"""
        try:
            if hasattr(self, 'transcription_service') and self.transcription_service:
                return not self.transcription_service.is_model_loaded()
            return True
        except Exception as e:
            logger.error(f"Error verifying transcription cleanup: {e}")
            return False
    
    
    def _cleanup_hotkey_manager(self) -> bool:
        """Clean up hotkey manager resources"""
        try:
            if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
                self.hotkey_manager.cleanup()
                logger.debug("Hotkey manager cleaned up")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up hotkey manager: {e}")
            return False
    
    def _verify_hotkey_cleanup(self) -> bool:
        """Verify hotkey manager cleanup"""
        try:
            # Check if hotkey manager is properly cleaned up
            if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
                return not hasattr(self.hotkey_manager, 'is_active') or not self.hotkey_manager.is_active
            return True
        except Exception as e:
            logger.error(f"Error verifying hotkey cleanup: {e}")
            return False
