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
from core.audio_manager import AudioManager
from core.platform_features import PlatformFeatures, FeatureStatus
from core.logging_config import get_logger
from core.performance_monitor import get_performance_monitor
from core.path_validation import get_sandbox, create_safe_temp_file
from core.transcription_exceptions import (
    TranscriptionException, ModelLoadingError, AudioProcessingError, 
    WhisperError, FileIOError, TranscriptionTimeoutError,
    with_retry, classify_exception, get_retry_manager
)
from core.cleanup_manager import (
    CleanupManager, CleanupPhase, register_cleanup_task, get_cleanup_manager
)
from core.config import TIMEOUT_CONFIG, WHISPER_CONFIG, AUDIO_CONFIG, MEMORY_CONFIG
from core.transcription_service import TranscriptionService

logger = get_logger(__name__)

# Whisper engine availability flags (set lazily when needed)
WHISPER_AVAILABLE = False
FASTER_WHISPER_AVAILABLE = False
CUDA_AVAILABLE = False

class SpeechController:
    def __init__(self, hotkey: str = "alt gr", model_size: str = "tiny", auto_paste: bool = True, 
                 language: str = None, temperature: float = 0.5, engine: str = None):
        self.model_size = model_size
        self.auto_paste = auto_paste
        self.language = language if language is not None else "auto"
        self.temperature = temperature
        self.engine = (engine or WHISPER_CONFIG.DEFAULT_ENGINE).lower()  # Use config default if None
        self.speed_mode = True  # Enable speed optimizations by default
        self.toggle_mode = False  # Default to hold mode
        self.listening = False
        self.listen_thread = None
        self.recording_frames = []
        self.transcript_log: List[Dict] = []
        self.transcript_callback: Optional[Callable] = None
        self.recording_stream = None
        
        # Audio recording parameters
        self.CHUNK = 2048  # Match tests' expected chunk size
        self.CHANNELS = 1
        self.RATE = 16000  # Whisper's optimal sample rate
        
        # Initialize performance monitoring
        self.performance_monitor = get_performance_monitor()
        
        # Initialize platform features detection (needed before hotkey registration)
        self.platform_features = PlatformFeatures()
        self.features = self.platform_features.detect_all_features()

        # Initialize managers
        self.hotkey_manager = HotkeyManager()
        self.audio_manager = AudioManager(
            sample_rate=self.RATE,
            channels=self.CHANNELS,
            chunk_size=self.CHUNK
        )
        self.hotkey = hotkey  # Store original hotkey for compatibility
        
        # Visual indicator settings
        self.visual_indicator_enabled = True
        self.visual_indicator_position = "Bottom Center"
        
        # Status callback for UI updates
        self.status_callback: Optional[Callable[[str], None]] = None
        # Recording state callback (bool)
        self.recording_state_callback: Optional[Callable[[bool], None]] = None

        # Create temporary directory and audio file path using sandbox
        sandbox = get_sandbox()
        self.temp_dir = str(sandbox.temp_dir)
        self.audio_path = str(create_safe_temp_file(suffix='.wav'))
        logger.info(f"Using temporary directory: {self.temp_dir}")
        logger.info(f"Using sandboxed audio path: {self.audio_path}")

        # Whisper model - lazy loading for faster startup
        self.model_size = model_size
        self.model = None  # Will be loaded on first use
        self.transcription_service: Optional[TranscriptionService] = None
        self.model_loading = False
        self.model_loaded = False
        self.model_load_error = None
        
        # Thread safety for model loading
        self._model_lock = threading.Lock()
        self._model_condition = threading.Condition(self._model_lock)
        self._pending_transcriptions = []  # Queue for pending transcription requests
        
        logger.info(f"Whisper {model_size} model ({self.engine} engine) will be loaded on first recording.")

        # Set up audio manager
        self._setup_audio_manager()
        
        # Set up hotkey manager
        self._setup_hotkey_manager()
        
        # Register initial hotkey
        self.register_hotkeys()
        
        # Initialize cleanup manager and register cleanup tasks
        self.cleanup_manager = get_cleanup_manager()
        self._register_cleanup_tasks()
        
        logger.info("SpeechController initialized successfully")
    
    def _register_cleanup_tasks(self):
        """Register cleanup tasks with the cleanup manager"""
        # Audio resources cleanup
        register_cleanup_task(
            "audio_manager_cleanup",
            CleanupPhase.AUDIO_RESOURCES,
            self._cleanup_audio_manager,
            self._verify_audio_cleanup,
            timeout=5.0,
            critical=True
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
        
        # Model resources cleanup
        register_cleanup_task(
            "model_cleanup",
            CleanupPhase.MODEL_RESOURCES,
            self._cleanup_model,
            self._verify_model_cleanup,
            timeout=10.0,
            critical=False
        )
        
        # File resources cleanup
        register_cleanup_task(
            "file_cleanup",
            CleanupPhase.FILE_RESOURCES,
            self._cleanup_files,
            self._verify_file_cleanup,
            timeout=5.0,
            critical=False
        )
        
        logger.info("Cleanup tasks registered successfully")
    
    def _setup_audio_manager(self):
        """Set up the audio manager with callbacks"""
        if not self.audio_manager.is_available():
            logger.warning("Audio functionality not available on this platform")
            return
        
        # Use default device selection (will be overridden by settings if available)
        self.audio_manager.select_device(None)
        logger.info("Using default audio device (will be updated by settings if available)")
        
        # Set up callbacks
        self.audio_manager.set_callbacks(
            on_audio_level=self._on_audio_level
        )
        
        logger.info("Audio manager initialized successfully")
    
    def set_audio_device(self, device_index: Optional[int] = None) -> bool:
        """
        Set the audio input device.
        
        Args:
            device_index: Device index to select, or None for system default
            
        Returns:
            True if device was set successfully, False otherwise
        """
        if not self.audio_manager.is_available():
            logger.error("Audio functionality not available")
            return False
        
        try:
            # Use smart device selection with fallback
            success = self._smart_select_device(device_index)
            
            if success:
                device_name = "System Default"
                if device_index is not None:
                    devices = self.audio_manager.get_devices()
                    if device_index < len(devices):
                        device_name = devices[device_index]['name']
                logger.info(f"Audio device set to: {device_name}")
            else:
                logger.warning("Failed to set audio device, using default")
            
            return success
            
        except Exception as e:
            logger.error(f"Error setting audio device: {e}")
            return False
    
    def _smart_select_device(self, target_index: Optional[int] = None) -> bool:
        """
        Smart device selection with fallback strategies.
        
        Args:
            target_index: Target device index, or None for system default
            
        Returns:
            True if device was selected successfully, False otherwise
        """
        if target_index is None:
            # Use system default
            return self.audio_manager.select_device(None)
        
        try:
            devices = self.audio_manager.get_devices()
            if not devices:
                logger.warning("No audio devices available")
                return self.audio_manager.select_device(None)
            
            # Try exact index match first (fast path)
            if 0 <= target_index < len(devices):
                if self.audio_manager.select_device(target_index):
                    return True
                else:
                    logger.warning(f"Device at index {target_index} failed, trying fallback")
            
            # Fallback to system default
            logger.info("Falling back to system default device")
            return self.audio_manager.select_device(None)
            
        except Exception as e:
            logger.error(f"Error in smart device selection: {e}")
            return self.audio_manager.select_device(None)
    
    def _on_audio_level(self, level: float):
        """Handle audio level updates for visualization"""
        if hasattr(self, 'audio_level_callback') and self.audio_level_callback:
            self.audio_level_callback(level)
    
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

    def _ensure_model_loaded(self, timeout_seconds: int = None) -> bool:
        """
        Ensure Whisper model is loaded, loading it if necessary.
        
        Args:
            timeout_seconds: Maximum time to wait for model loading (uses config default if None)
            
        Returns:
            True if model is ready, False if timeout or error
        """
        if timeout_seconds is None:
            timeout_seconds = TIMEOUT_CONFIG.MODEL_LOADING_TIMEOUT
        
        self._model_condition.acquire()
        lock_released = False  # Track if lock has been released
        try:
            # If model is already loaded, return immediately
            if self.model_loaded:
                return True
            
            # If there's a previous load error, don't try again
            if self.model_load_error:
                logger.warning(f"Model load previously failed: {self.model_load_error}")
                return False
            
            # If model is currently loading, wait for it
            if self.model_loading:
                logger.info("Model is loading, waiting for completion...")
                self._update_status("Model loading, please wait...")
                
                # Wait for model loading to complete with timeout
                if not self._model_condition.wait(timeout_seconds):
                    logger.error(f"Model loading timeout after {timeout_seconds} seconds")
                    self._update_status("Model loading timeout")
                    return False
                
                # Check if loading completed successfully
                if self.model_loaded:
                    logger.info("Model loading completed successfully")
                    return True
                elif self.model_load_error:
                    logger.error(f"Model loading failed: {self.model_load_error}")
                    return False
                else:
                    logger.error("Model loading completed but state is inconsistent")
                    return False
            
            # Model is not loading, start loading it
            logger.info("Starting model loading...")
            self.model_loading = True
            self._update_status(f"Loading {self.engine} Whisper model...")
            
            # Release the lock while loading (this is safe because we check model_loading)
            self._model_condition.release()
            lock_released = True  # Mark that we've released the lock
            
        except Exception:
            # If any error occurs in the locked section, release before re-raising
            if not lock_released:
                self._model_condition.release()
                lock_released = True
            raise
        finally:
            # Ensure lock is released on all code paths (early returns, exceptions, etc.)
            if not lock_released:
                self._model_condition.release()
        
        # Now we're outside the lock, load the model
        try:
            # Load the model with comprehensive error handling
            success = self._load_model_implementation()
            
            # Re-acquire lock to update state
            self._model_condition.acquire()
            try:
                if success:
                    self.model_loaded = True
                    self.model_load_error = None
                    logger.info(f"{self.engine.title()} model loaded successfully!")
                    self._update_status(f"{self.engine.title()} model loaded successfully!")
                else:
                    self.model_load_error = "Model loading failed"
                    logger.error("Model loading failed")
                    self._update_status("Model loading failed")
                
                self.model_loading = False
                
                # Notify all waiting threads
                self._model_condition.notify_all()
                
                return success
            finally:
                self._model_condition.release()
                
        except Exception as e:
            # Re-acquire lock to update state
            self._model_condition.acquire()
            try:
                self.model_loading = False
                self.model_load_error = f"Unexpected error: {e}"
                logger.error(f"Unexpected error loading Whisper model: {e}")
                self._update_status(f"Error loading model: {e}")
                
                # Notify all waiting threads
                self._model_condition.notify_all()
                
                return False
            finally:
                self._model_condition.release()
    
    @with_retry("model_loading")
    def _load_model_implementation(self) -> bool:
        """
        Internal method to load the Whisper model with retry logic.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading {self.engine} Whisper {self.model_size} model... this may take a moment.")
            
            # Lazy import Whisper libraries to avoid startup delays
            global WHISPER_AVAILABLE, FASTER_WHISPER_AVAILABLE, CUDA_AVAILABLE
            
            # Import whisper (OpenAI)
            try:
                import whisper
                WHISPER_AVAILABLE = True
                logger.debug("OpenAI Whisper imported successfully")
            except ImportError as e:
                logger.error(f"Failed to import OpenAI Whisper: {e}")
                WHISPER_AVAILABLE = False
            
            # Import faster-whisper with fallback
            try:
                from faster_whisper import WhisperModel as FasterWhisperModel
                FASTER_WHISPER_AVAILABLE = True
                logger.debug("faster-whisper imported successfully")
            except ImportError as e:
                logger.debug(f"faster-whisper not available: {e}")
                FASTER_WHISPER_AVAILABLE = False
            
            # Check for CUDA availability
            try:
                import torch
                CUDA_AVAILABLE = torch.cuda.is_available()
                if CUDA_AVAILABLE:
                    logger.info(f"CUDA available with {torch.cuda.device_count()} GPU(s)")
                else:
                    logger.info("CUDA not available, using CPU")
            except ImportError as e:
                logger.warning(f"PyTorch not available: {e}")
                CUDA_AVAILABLE = False
            except Exception as e:
                logger.warning(f"PyTorch initialization failed: {e}")
                CUDA_AVAILABLE = False
            
            # Validate engine choice now that we know what's available
            if self.engine == "faster" and not FASTER_WHISPER_AVAILABLE:
                logger.warning("faster-whisper not available, falling back to openai-whisper")
                self.engine = "openai"
            
            if self.engine == "openai" and not WHISPER_AVAILABLE:
                raise ModelLoadingError("Neither faster-whisper nor OpenAI Whisper is available")
            
            # Check available memory before loading model
            from core.path_validation import check_available_memory
            try:
                check_available_memory(MEMORY_CONFIG.MIN_AVAILABLE_MEMORY_MB)
            except MemoryError as e:
                logger.error(f"Cannot load model: {e}")
                raise ModelLoadingError(str(e), e)
            
            # Time model loading for performance monitoring
            with self.performance_monitor.time_operation("model_loading"):
                # Validate model size
                valid_models = ["tiny", "base", "small", "medium", "large"]
                if self.model_size not in valid_models:
                    raise ModelLoadingError(f"Invalid model size: {self.model_size}. Valid options: {valid_models}")
                
                # Load model based on engine with performance optimizations
                if self.engine == "faster":
                    # Determine device and compute type based on availability
                    try:
                        if CUDA_AVAILABLE:
                            device = "cuda"
                            compute_type = "float16"  # Use float16 for GPU
                            logger.info("Using GPU acceleration for faster-whisper")
                        else:
                            device = "cpu"
                            compute_type = "int8"  # Use int8 for CPU
                            logger.info("Using CPU with int8 optimization for faster-whisper")
                    except Exception as e:
                        logger.warning(f"CUDA detection failed, falling back to CPU: {e}")
                        device = "cpu"
                        compute_type = "int8"
                        logger.info("Using CPU with int8 optimization for faster-whisper (fallback)")

                    # Use process-based faster-whisper to isolate ONNX runtime from PyQt process
                    try:
                        if self.transcription_service:
                            self.transcription_service.stop()

                        self.transcription_service = TranscriptionService(
                            model_name=self.model_size,
                            device=device,
                            compute_type=compute_type,
                        )

                        logger.info(
                            f"Starting transcription worker with device={device}, compute_type={compute_type}"
                        )
                        if not self.transcription_service.start(timeout_seconds=TIMEOUT_CONFIG.MODEL_LOADING_TIMEOUT):
                            raise ModelLoadingError("Failed to start transcription worker")

                        self.model = None
                        logger.info("Transcription worker started successfully")
                    except Exception as e:
                        import traceback
                        logger.error(f"Failed to start faster-whisper worker: {e}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        logger.info("Falling back to OpenAI Whisper...")

                        if self.transcription_service:
                            self.transcription_service.stop()
                            self.transcription_service = None

                        if not WHISPER_AVAILABLE:
                            raise ModelLoadingError("Failed to start worker and OpenAI Whisper is unavailable")

                        # Fallback to OpenAI Whisper
                        self.engine = "openai"
                        self.model = whisper.load_model(
                            self.model_size,
                            device="cpu"  # Force CPU for stability
                        )
                else:
                    # Use original openai-whisper with error handling
                    self.model = whisper.load_model(
                        self.model_size,
                        device="cpu",
                        download_root=None  # Use default cache
                    )
                
                # Validate model was loaded (only needed for non-service paths)
                if self.engine != "faster" and self.model is None:
                    raise ModelLoadingError("Model loaded but is None")
                
                return True
                
        except ImportError as e:
            raise ModelLoadingError(f"Import error: {e}", e)
        except ValueError as e:
            raise ModelLoadingError(f"Configuration error: {e}", e)
        except RuntimeError as e:
            raise ModelLoadingError(f"Runtime error: {e}", e)
        except Exception as e:
            transcription_exception = classify_exception(e)
            if isinstance(transcription_exception, ModelLoadingError):
                raise transcription_exception
            else:
                raise ModelLoadingError(f"Unexpected error: {e}", e)
    
    def is_model_ready(self):
        """Check if the Whisper model is ready for use"""
        return self.model_loaded and (self.model is not None or self.transcription_service is not None)
    
    def get_model_status(self):
        """Get current model loading status"""
        if self.model_loaded:
            return "loaded"
        elif self.model_loading:
            return "loading"
        elif self.model_load_error:
            return f"error: {self.model_load_error}"
        else:
            return "not_loaded"
    
    def preload_model(self):
        """Preload the Whisper model in a background thread"""
        with self._model_condition:
            if not self.model_loaded and not self.model_loading and not self.model_load_error:
                # Start loading in a separate thread to avoid blocking
                # Use daemon thread so it doesn't prevent app shutdown
                load_thread = threading.Thread(target=self._background_load_model, daemon=True)
                load_thread.start()
                
                # Update state
                self.model_loading = True
                self._update_status(f"Loading {self.engine} Whisper model...")
                
                logger.info("Started background model loading...")
                return True
        return False
    
    def _background_load_model(self):
        """Background model loading thread function"""
        try:
            logger.info("Starting _load_model_implementation in background thread...")
            success = self._load_model_implementation()
            logger.info(f"_load_model_implementation returned: {success}")
            
            with self._model_condition:
                if success:
                    self.model_loaded = True
                    self.model_load_error = None
                    logger.info(f"{self.engine.title()} model loaded successfully!")
                    self._update_status(f"{self.engine.title()} model loaded successfully!")
                else:
                    self.model_load_error = "Model loading failed"
                    logger.error("Background model loading failed")
                    self._update_status("Model loading failed")
                
                self.model_loading = False
                
                # Notify all waiting threads
                self._model_condition.notify_all()
                
        except Exception as e:
            import traceback
            with self._model_condition:
                self.model_loading = False
                self.model_load_error = f"Unexpected error: {e}"
                logger.error(f"Unexpected error in background model loading: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                self._update_status(f"Error loading model: {e}")
                
                # Notify all waiting threads
                self._model_condition.notify_all()
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set a callback function to update UI status"""
        self.status_callback = callback

    def set_recording_state_callback(self, callback: Callable[[bool], None]):
        """Set callback invoked when recording starts/stops."""
        self.recording_state_callback = callback

    def set_transcript_callback(self, callback: Callable[[], None]):
        """Set callback function for transcript updates"""
        self.transcript_callback = callback

    def set_audio_level_callback(self, callback: Callable[[float], None]):
        """Set a callback function to update audio level for waveform visualization"""
        self.audio_level_callback = callback

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
        
        self.listening = True
        self.recording_frames = []
        self._update_status("Recording...")
        if self.recording_state_callback:
            try:
                self.recording_state_callback(True)
            except Exception:
                pass
        
        # Start audio recording
        if self.audio_manager.start_recording():
            logger.info("Audio recording started successfully")
        else:
            logger.error("Failed to start audio recording")
            self.listening = False
            self._update_status("Recording failed")

    def stop_recording(self):
        """Stop recording and process audio"""
        if not self.listening:
            return
        
        self.listening = False
        self._update_status("Processing...")
        if self.recording_state_callback:
            try:
                self.recording_state_callback(False)
            except Exception:
                pass
        
        # Stop audio recording and get frames
        self.recording_frames = self.audio_manager.stop_recording()
        
        if self.recording_frames:
            self.process_recorded_audio()
        else:
            logger.warning("No audio recorded")
            self._update_status("Idle")

    def toggle_recording(self):
        """Toggle between recording and idle states"""
        if self.listening:
            self.stop_recording()
        else:
            self.start_recording()


    def save_audio_to_file(self, frames, filename):
        """Save recorded audio frames to a WAV file"""
        return self.audio_manager.save_audio_to_file(frames, filename)

    def process_recorded_audio(self):
        """Process recorded audio through Whisper and optionally paste text"""
        try:
            if not self.recording_frames:
                logger.warning("No audio frames to process")
                self._update_status("No audio recorded")
                return

            # Validate audio frames
            if not isinstance(self.recording_frames, list) or len(self.recording_frames) == 0:
                logger.error("Invalid audio frames")
                self._update_status("Invalid audio data")
                return

            # Save audio file with error handling
            try:
                if not self.save_audio_to_file(self.recording_frames, self.audio_path):
                    logger.error("Failed to save audio file")
                    self._update_status("Failed to save audio")
                    return
            except Exception as e:
                logger.error(f"Error saving audio file: {e}")
                self._update_status(f"Audio save error: {e}")
                return

            logger.info(f"Audio saved to {self.audio_path}")
            time.sleep(0.05)  # ensure FS flush on some systems

            # Validate saved file
            try:
                if not os.path.exists(self.audio_path):
                    logger.error(f"Audio file not created: {self.audio_path}")
                    self._update_status("Audio file not created")
                    return
                
                file_size = os.path.getsize(self.audio_path)
                if file_size == 0:
                    logger.error(f"Audio file is empty: {self.audio_path}")
                    self._update_status("Audio file is empty")
                    return
                
                # Check for reasonable file size (not too small, not too large)
                if file_size < 1000:  # Less than 1KB is probably too small
                    logger.warning(f"Audio file seems too small: {file_size} bytes")
                elif file_size > 50 * 1024 * 1024:  # More than 50MB is probably too large
                    logger.warning(f"Audio file seems too large: {file_size} bytes")
                    
            except OSError as e:
                logger.error(f"Error checking audio file: {e}")
                self._update_status(f"File system error: {e}")
                return

            try:
                # Ensure model is loaded before transcription (with timeout)
                if not self._ensure_model_loaded(timeout_seconds=TIMEOUT_CONFIG.MODEL_LOADING_TIMEOUT):
                    logger.error("Model loading failed or timed out, cannot transcribe")
                    self._update_status("Transcription failed: Model not ready")
                    return
                
                # Transcribe using the selected engine with performance monitoring
                logger.info(f"Using transcription engine: {self.engine}")
                with self.performance_monitor.time_operation("transcription"):
                    try:
                        if self.engine == "faster":
                            if self.transcription_service:
                                logger.info(f"Transcribing audio via worker: {self.audio_path}")
                                result = self.transcription_service.transcribe(
                                    audio_path=self.audio_path,
                                    language=self.language,
                                    temperature=self.temperature,
                                    speed_mode=self.speed_mode,
                                    timeout_seconds=TIMEOUT_CONFIG.TRANSCRIPTION_TIMEOUT,
                                )

                                if result is None:
                                    logger.error("Transcription worker request failed")
                                    self._update_status("Transcription failed")
                                    text = ""
                                else:
                                    text = (result.get("text") or "").strip()
                            else:
                                logger.error("faster engine selected but transcription worker is unavailable")
                                self._update_status("Transcription engine unavailable")
                                text = ""
                        else:
                            # Use original openai-whisper API
                            if self.speed_mode:
                                transcribe_params = {
                                    "fp16": True,
                                    "temperature": self.temperature,
                                    "compression_ratio_threshold": 2.4,
                                    "no_speech_threshold": 0.6,
                                    "condition_on_previous_text": False,
                                    "initial_prompt": None,
                                    "word_timestamps": False,
                                    "prepend_punctuations": "",
                                    "append_punctuations": ""
                                }
                            else:
                                # Standard parameters for better accuracy
                                transcribe_params = {
                                    "fp16": False,
                                    "temperature": self.temperature,
                                    "condition_on_previous_text": True,
                                    "word_timestamps": False
                                }
                            # Only set language if it's not auto-detection
                            if self.language and self.language != "auto":
                                transcribe_params["language"] = self.language
                            
                            logger.debug(f"Calling openai-whisper with params: {transcribe_params}")
                            logger.info(f"Transcribing audio file: {self.audio_path}")
                            logger.info(f"File exists before transcription: {os.path.exists(self.audio_path)}")
                            result = self.model.transcribe(self.audio_path, **transcribe_params)
                            logger.debug(f"openai-whisper returned result: {type(result)}")
                            
                            # Handle case where result might be None or missing text
                            if result is None:
                                logger.warning("openai-whisper returned None result")
                                text = ""
                            else:
                                text = (result.get("text") or "").strip()
                                if not text:
                                    logger.debug("openai-whisper returned empty text")
                    except Exception as e:
                        # Log full traceback for debugging
                        import traceback
                        logger.error(f"Transcription exception: {e}")
                        logger.error(f"Exception type: {type(e).__name__}")
                        logger.error(f"Full traceback:\n{traceback.format_exc()}")
                        
                        # Classify the exception and provide specific error handling
                        transcription_exception = classify_exception(e)
                        
                        if isinstance(transcription_exception, WhisperError):
                            logger.error(f"Whisper transcription error: {e}")
                            self._update_status(f"Transcription failed: {e}")
                        elif isinstance(transcription_exception, FileIOError):
                            logger.error(f"File I/O error during transcription: {e}")
                            self._update_status(f"File error: {e}")
                        elif isinstance(transcription_exception, MemoryError):
                            logger.error(f"Memory error during transcription: {e}")
                            self._update_status(f"Memory error: {e}")
                        else:
                            logger.error(f"Unexpected transcription error: {e}")
                            logger.error(f"Error type: {type(e)}")
                            self._update_status(f"Transcription error: {e}")
                        
                        text = ""
                if text:
                    logger.info(f"Recognized: {text}")
                    
                    # Add to transcript history
                    timestamp = datetime.now().strftime("%m/%d %H:%M")
                    transcript_entry = {
                        "timestamp": timestamp,
                        "text": text
                    }
                    self.transcript_log.insert(0, transcript_entry)  # Newest at top
                    
                    # Notify UI of new transcript
                    if self.transcript_callback:
                        self.transcript_callback()
                    
                    if self.auto_paste:
                        try:
                            pyautogui.write(text + " ")
                        except Exception as paste_error:
                            logger.warning(f"Auto-paste failed: {paste_error}")
                            # Continue without crashing the app
                else:
                    logger.info("No speech detected")
            except Exception as e:
                logger.error(f"Error transcribing audio: {e}")
        except Exception as e:
            logger.error(f"Error processing recorded audio: {e}")
        finally:
            self.recording_frames = []
            self._update_status("Idle")

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
        self.language = lang_code
        logger.info(f"Language set to: {lang_code}")

    def set_temperature(self, temperature: float):
        """Set the temperature for transcription (0.0 = deterministic, higher = more random)"""
        self.temperature = max(0.0, min(1.0, temperature))  # Clamp between 0.0 and 1.0
        logger.info(f"Temperature set to: {self.temperature}")
    
    def set_model(self, model_size: str):
        """Change the Whisper model dynamically"""
        if model_size != self.model_size:
            logger.info(f"Changing model from {self.model_size} to {model_size}...")
            self.model_size = model_size
            self.model = whisper.load_model(model_size)
            logger.info(f"Model changed to {model_size} successfully!")
    
    def set_speed_mode(self, enabled: bool):
        """Enable or disable speed optimizations"""
        self.speed_mode = enabled
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
    
    def _cleanup_audio_manager(self) -> bool:
        """Clean up audio manager resources"""
        try:
            if hasattr(self, 'audio_manager') and self.audio_manager:
                self.audio_manager.cleanup()
                logger.debug("Audio manager cleaned up")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up audio manager: {e}")
            return False
    
    def _verify_audio_cleanup(self) -> bool:
        """Verify audio manager cleanup"""
        try:
            # Check if audio manager is properly cleaned up
            if hasattr(self, 'audio_manager') and self.audio_manager:
                return not self.audio_manager.is_recording
            return True
        except Exception as e:
            logger.error(f"Error verifying audio cleanup: {e}")
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
    
    def _cleanup_model(self) -> bool:
        """Clean up Whisper model resources"""
        try:
            if hasattr(self, 'transcription_service') and self.transcription_service:
                self.transcription_service.stop()
                self.transcription_service = None

            if hasattr(self, 'model') and self.model:
                # Clear model reference to free memory
                self.model = None
                logger.debug("Whisper model cleaned up")
            
            # Reset model state
            self.model_loaded = False
            self.model_loading = False
            self.model_load_error = None
            
            return True
        except Exception as e:
            logger.error(f"Error cleaning up model: {e}")
            return False
    
    def _verify_model_cleanup(self) -> bool:
        """Verify model cleanup"""
        try:
            worker_stopped = not getattr(self, 'transcription_service', None)
            return not self.model_loaded and not self.model_loading and worker_stopped
        except Exception as e:
            logger.error(f"Error verifying model cleanup: {e}")
            return False
    
    def _cleanup_files(self) -> bool:
        """Clean up temporary files"""
        try:
            # Clean up temporary audio file
            if hasattr(self, 'audio_path') and self.audio_path and os.path.exists(self.audio_path):
                os.remove(self.audio_path)
                logger.debug(f"Temporary audio file removed: {self.audio_path}")
            
            # Clean up temporary directory if empty
            if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    os.rmdir(self.temp_dir)
                    logger.debug(f"Temporary directory removed: {self.temp_dir}")
                except OSError:
                    # Directory not empty, that's okay
                    pass
            
            return True
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
            return False
    
    def _verify_file_cleanup(self) -> bool:
        """Verify file cleanup"""
        try:
            # Check if temporary files are cleaned up
            audio_file_cleaned = not (hasattr(self, 'audio_path') and self.audio_path and os.path.exists(self.audio_path))
            return audio_file_cleaned
        except Exception as e:
            logger.error(f"Error verifying file cleanup: {e}")
            return False
