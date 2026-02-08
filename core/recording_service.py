#!/usr/bin/env python3
"""
core/recording_service.py
------------------------
Standalone audio recording service for voice-to-text applications.

This service handles:
- Audio device enumeration and selection
- Recording lifecycle management (start, stop, pause)
- Real-time audio level monitoring
- Thread-safe recording operations
- Audio buffer management and file output
- Recording state machine

Features:
    - Cross-platform audio recording (via AudioManager)
    - Device validation and fallback
    - Real-time audio level callbacks
    - Safe temporary file handling
    - Configurable sample rates and quality
    - Robust error handling
    - State-based recording control

Example:
    Basic usage:
        from core.recording_service import RecordingService, RecordingConfig
        
        config = RecordingConfig(
            sample_rate=16000,
            channels=1,
            chunk_size=1024
        )
        
        service = RecordingService(config)
        
        # Set up callbacks
        service.set_audio_level_callback(lambda level: print(f"Level: {level}"))
        service.set_status_callback(lambda status: print(f"Status: {status}"))
        
        # Start recording
        success = service.start_recording()
        if success:
            # ... wait for speech ...
            audio_path = service.stop_recording()
            print(f"Audio saved to: {audio_path}")

Author: Whiz Development Team
Version: 2.0.0
"""

import os
import time
import threading
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any, List
from enum import Enum
from pathlib import Path

from .logging_config import get_logger
from .audio_manager import AudioManager
from .path_validation import get_sandbox, create_safe_temp_file

logger = get_logger(__name__)


class RecordingState(Enum):
    """States of the recording service"""
    IDLE = "idle"
    RECORDING = "recording"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class RecordingConfig:
    """Configuration for recording service"""
    sample_rate: int = 16000  # Hz - Whisper's optimal rate
    channels: int = 1  # Mono audio
    chunk_size: int = 1024  # Samples per chunk
    device_index: Optional[int] = None  # Audio device, None = default
    max_duration: Optional[float] = None  # Max recording duration in seconds
    
    def __post_init__(self):
        """Validate configuration"""
        if self.sample_rate <= 0:
            raise ValueError(f"Invalid sample_rate: {self.sample_rate}. Must be positive")
        
        if self.channels not in [1, 2]:
            raise ValueError(f"Invalid channels: {self.channels}. Must be 1 (mono) or 2 (stereo)")
        
        if self.chunk_size <= 0:
            raise ValueError(f"Invalid chunk_size: {self.chunk_size}. Must be positive")
        
        if self.max_duration is not None and self.max_duration <= 0:
            raise ValueError(f"Invalid max_duration: {self.max_duration}. Must be positive")


@dataclass
class RecordingResult:
    """Result of a recording operation"""
    success: bool
    audio_path: Optional[str] = None
    duration_seconds: float = 0.0
    error: Optional[str] = None
    error_type: Optional[str] = None
    samples_recorded: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "audio_path": self.audio_path,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
            "error_type": self.error_type,
            "samples_recorded": self.samples_recorded
        }


class RecordingService:
    """
    Standalone service for audio recording.
    
    This service manages the complete audio recording lifecycle with
    proper state management and error handling.
    """
    
    def __init__(self, config: RecordingConfig):
        """
        Initialize recording service.
        
        Args:
            config: RecordingConfig instance with audio settings
        """
        self.config = config
        self.state = RecordingState.IDLE
        
        # Audio manager
        self.audio_manager = AudioManager(
            sample_rate=config.sample_rate,
            channels=config.channels,
            chunk_size=config.chunk_size
        )
        
        # Recording state
        self.recording_start_time: Optional[float] = None
        self.current_audio_path: Optional[str] = None
        
        # Thread safety
        self._state_lock = threading.Lock()
        
        # Callbacks
        self.audio_level_callback: Optional[Callable[[float], None]] = None
        self.status_callback: Optional[Callable[[str], None]] = None
        self.state_change_callback: Optional[Callable[[RecordingState], None]] = None
        
        # Validate audio availability
        if not self.audio_manager.is_available():
            logger.error("Audio system not available!")
            self._set_state(RecordingState.ERROR)
        else:
            # Set up audio callbacks
            self.audio_manager.set_callbacks(on_audio_level=self._on_audio_level)
            
            # Select audio device
            if config.device_index is not None:
                self.select_device(config.device_index)
            
            logger.info(f"RecordingService initialized (rate={config.sample_rate}, channels={config.channels})")
    
    def set_audio_level_callback(self, callback: Callable[[float], None]):
        """Set callback for audio level updates"""
        self.audio_level_callback = callback
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback for status messages"""
        self.status_callback = callback
    
    def set_state_change_callback(self, callback: Callable[[RecordingState], None]):
        """Set callback for state changes"""
        self.state_change_callback = callback
    
    def _update_status(self, message: str):
        """Update status via callback if available"""
        if self.status_callback:
            try:
                self.status_callback(message)
            except Exception as e:
                logger.warning(f"Status callback failed: {e}")
    
    def _on_audio_level(self, level: float):
        """Internal callback for audio level updates"""
        if self.audio_level_callback:
            try:
                self.audio_level_callback(level)
            except Exception as e:
                logger.warning(f"Audio level callback failed: {e}")
    
    def _set_state(self, new_state: RecordingState):
        """Update recording state with callback notification"""
        with self._state_lock:
            old_state = self.state
            self.state = new_state
            
            if old_state != new_state:
                logger.info(f"Recording state: {old_state.value} -> {new_state.value}")
                
                if self.state_change_callback:
                    try:
                        self.state_change_callback(new_state)
                    except Exception as e:
                        logger.warning(f"State change callback failed: {e}")
    
    def get_state(self) -> RecordingState:
        """Get current recording state"""
        with self._state_lock:
            return self.state
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.get_state() == RecordingState.RECORDING
    
    def get_available_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of available audio input devices.
        
        Returns:
            List of device dictionaries with name, index, and info
        """
        if not self.audio_manager.is_available():
            return []
        
        return self.audio_manager.get_devices()
    
    def select_device(self, device_index: Optional[int] = None) -> bool:
        """
        Select audio input device.
        
        Args:
            device_index: Device index, or None for system default
            
        Returns:
            True if device was selected successfully
        """
        if not self.audio_manager.is_available():
            logger.error("Audio system not available")
            return False
        
        try:
            success = self.audio_manager.select_device(device_index)
            
            if success:
                device_name = "System Default"
                if device_index is not None:
                    devices = self.get_available_devices()
                    if device_index < len(devices):
                        device_name = devices[device_index]['name']
                
                logger.info(f"Audio device selected: {device_name}")
                self._update_status(f"Using device: {device_name}")
            else:
                logger.warning("Failed to select audio device")
                self._update_status("Device selection failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error selecting device: {e}")
            return False
    
    def start_recording(self) -> bool:
        """
        Start audio recording.
        
        Returns:
            True if recording started successfully, False otherwise
        """
        if not self.audio_manager.is_available():
            logger.error("Cannot start recording: audio not available")
            self._set_state(RecordingState.ERROR)
            return False
        
        current_state = self.get_state()
        if current_state == RecordingState.RECORDING:
            logger.warning("Already recording")
            return False
        
        if current_state == RecordingState.ERROR:
            logger.error("Cannot start recording: service in error state")
            return False
        
        try:
            # Create safe temporary file for audio
            self.current_audio_path = str(create_safe_temp_file(suffix='.wav'))
            
            # Start audio recording
            success = self.audio_manager.start_recording()
            
            if success:
                self.recording_start_time = time.time()
                self._set_state(RecordingState.RECORDING)
                self._update_status("Recording started")
                logger.info(f"Recording started, saving to: {self.current_audio_path}")
                return True
            else:
                logger.error("Failed to start audio recording")
                self._set_state(RecordingState.ERROR)
                self._update_status("Failed to start recording")
                return False
                
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            self._set_state(RecordingState.ERROR)
            self._update_status(f"Recording error: {e}")
            return False
    
    def stop_recording(self) -> RecordingResult:
        """
        Stop audio recording and save to file.
        
        Returns:
            RecordingResult with audio file path or error information
        """
        current_state = self.get_state()
        
        if current_state != RecordingState.RECORDING:
            logger.warning(f"Cannot stop recording: not in recording state (current: {current_state.value})")
            return RecordingResult(
                success=False,
                error=f"Not recording (state: {current_state.value})",
                error_type="InvalidState"
            )
        
        try:
            self._set_state(RecordingState.STOPPING)
            self._update_status("Stopping recording...")
            
            # Stop audio recording and get file path
            audio_path = self.audio_manager.stop_recording(self.current_audio_path)
            
            # Calculate duration
            duration = 0.0
            if self.recording_start_time:
                duration = time.time() - self.recording_start_time
            
            if audio_path and Path(audio_path).exists():
                self._set_state(RecordingState.IDLE)
                self._update_status("Recording complete")
                
                logger.info(f"Recording stopped, duration: {duration:.2f}s, saved to: {audio_path}")
                
                return RecordingResult(
                    success=True,
                    audio_path=audio_path,
                    duration_seconds=duration
                )
            else:
                logger.error("Failed to save recording")
                self._set_state(RecordingState.ERROR)
                self._update_status("Failed to save recording")
                
                return RecordingResult(
                    success=False,
                    error="Failed to save audio file",
                    error_type="FileIOError",
                    duration_seconds=duration
                )
                
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            self._set_state(RecordingState.ERROR)
            self._update_status(f"Stop error: {e}")
            
            return RecordingResult(
                success=False,
                error=str(e),
                error_type=type(e).__name__
            )
        finally:
            self.recording_start_time = None
            self.current_audio_path = None
    
    def cancel_recording(self):
        """Cancel current recording without saving"""
        if self.get_state() == RecordingState.RECORDING:
            try:
                self.audio_manager.stop_recording(None)  # Don't save
                self._set_state(RecordingState.IDLE)
                self._update_status("Recording cancelled")
                logger.info("Recording cancelled")
            except Exception as e:
                logger.error(f"Error cancelling recording: {e}")
                self._set_state(RecordingState.ERROR)
    
    def get_recording_duration(self) -> float:
        """Get duration of current recording in seconds"""
        if self.recording_start_time and self.get_state() == RecordingState.RECORDING:
            return time.time() - self.recording_start_time
        return 0.0
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.is_recording():
                self.cancel_recording()
            
            logger.info("RecordingService cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return {
            "state": self.get_state().value,
            "is_recording": self.is_recording(),
            "recording_duration": self.get_recording_duration(),
            "audio_available": self.audio_manager.is_available(),
            "sample_rate": self.config.sample_rate,
            "channels": self.config.channels
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the recording service.
        
        Returns:
            Dictionary with health status information
        """
        from .service_health import HealthStatus, HealthCheckResult
        
        # Check if audio is available
        if not self.audio_manager.is_available():
            result = HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                service_name="RecordingService",
                message="Audio system is not available",
                details={"audio_available": False}
            )
        elif self.state == RecordingState.ERROR:
            result = HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                service_name="RecordingService",
                message="Service is in error state",
                details={"state": self.state.value}
            )
        elif self.state == RecordingState.RECORDING:
            result = HealthCheckResult(
                status=HealthStatus.HEALTHY,
                service_name="RecordingService",
                message="Recording in progress",
                details={
                    "state": self.state.value,
                    "duration": self.get_recording_duration()
                }
            )
        else:
            result = HealthCheckResult(
                status=HealthStatus.HEALTHY,
                service_name="RecordingService",
                message="Service is healthy and ready",
                details={"state": self.state.value}
            )
        
        return result.to_dict()
    
    def readiness_check(self) -> Dict[str, Any]:
        """
        Check if service is ready to accept requests.
        
        Returns:
            Dictionary with readiness status
        """
        from .service_health import ReadinessStatus, ReadinessCheckResult
        
        # Check if audio system is available
        if not self.audio_manager.is_available():
            result = ReadinessCheckResult(
                status=ReadinessStatus.NOT_READY,
                service_name="RecordingService",
                message="Audio system is not available",
                dependencies_ready=False
            )
        elif self.state == RecordingState.ERROR:
            result = ReadinessCheckResult(
                status=ReadinessStatus.NOT_READY,
                service_name="RecordingService",
                message="Service is in error state",
                dependencies_ready=True
            )
        elif self.state == RecordingState.STOPPING:
            result = ReadinessCheckResult(
                status=ReadinessStatus.INITIALIZING,
                service_name="RecordingService",
                message="Recording is being stopped",
                dependencies_ready=True
            )
        else:
            result = ReadinessCheckResult(
                status=ReadinessStatus.READY,
                service_name="RecordingService",
                message="Service is ready to accept requests",
                dependencies_ready=True
            )
        
        return result.to_dict()
