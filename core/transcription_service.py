#!/usr/bin/env python3
"""
core/transcription_service.py
----------------------------
Standalone transcription service for Whisper-based speech-to-text.

This service handles:
- Whisper model loading and management (faster-whisper and openai-whisper engines)
- Transcription request processing with retry logic
- Async transcription queue management
- Comprehensive error handling and classification
- Thread-safe model access

Features:
    - Lazy model loading for fast startup
    - Support for multiple Whisper engines (faster-whisper, openai-whisper)
    - Configurable model size, language, and temperature
    - Thread-safe transcription operations
    - Structured error responses
    - Retry logic for transient failures
    - Model caching to avoid reloading

Example:
    Basic usage:
        from core.transcription_service import TranscriptionService, TranscriptionConfig
        
        config = TranscriptionConfig(
            model_size="tiny",
            engine="faster",
            language="auto",
            temperature=0.0
        )
        
        service = TranscriptionService(config)
        result = service.transcribe("path/to/audio.wav")
        
        if result.success:
            print(f"Transcript: {result.text}")
        else:
            print(f"Error: {result.error}")

Author: Whiz Development Team
Version: 2.0.0
"""

import os
import threading
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable
from enum import Enum
from pathlib import Path

from .logging_config import get_logger
from .transcription_exceptions import (
    TranscriptionException, ModelLoadingError, AudioProcessingError,
    WhisperError, FileIOError, TranscriptionTimeoutError,
    with_retry, classify_exception
)
from .config import TIMEOUT_CONFIG, WHISPER_CONFIG, MEMORY_CONFIG

# Try importing whisper engines (they may not be installed)
try:
    import faster_whisper
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    faster_whisper = None
    FASTER_WHISPER_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    whisper = None
    WHISPER_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

logger = get_logger(__name__)


class TranscriptionEngine(Enum):
    """Supported Whisper engines"""
    FASTER_WHISPER = "faster"
    OPENAI_WHISPER = "openai"


class TranscriptionStatus(Enum):
    """Status of a transcription request"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TranscriptionConfig:
    """Configuration for transcription service"""
    model_size: str = "tiny"  # tiny, base, small, medium, large
    engine: str = "faster"  # faster or openai
    language: str = "auto"  # Language code or "auto"
    temperature: float = 0.0  # 0.0-1.0, lower = more accurate
    speed_mode: bool = True  # Enable speed optimizations
    device: str = "auto"  # cpu, cuda, or auto
    compute_type: str = "int8"  # For faster-whisper: int8, float16, float32
    num_workers: int = 1  # Number of worker threads for async processing
    
    def __post_init__(self):
        """Validate configuration"""
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if self.model_size not in valid_sizes:
            raise ValueError(f"Invalid model_size: {self.model_size}. Must be one of {valid_sizes}")
        
        valid_engines = ["faster", "openai"]
        if self.engine not in valid_engines:
            raise ValueError(f"Invalid engine: {self.engine}. Must be one of {valid_engines}")
        
        if not (0.0 <= self.temperature <= 1.0):
            raise ValueError(f"Invalid temperature: {self.temperature}. Must be between 0.0 and 1.0")


@dataclass
class TranscriptionResult:
    """Result of a transcription request"""
    success: bool
    text: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    duration_seconds: float = 0.0
    model_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "text": self.text,
            "error": self.error,
            "error_type": self.error_type,
            "duration_seconds": self.duration_seconds,
            "model_info": self.model_info
        }


class TranscriptionService:
    """
    Standalone service for Whisper-based transcription.
    
    This service manages Whisper model lifecycle and processes transcription
    requests with comprehensive error handling and retry logic.
    """
    
    def __init__(self, config: TranscriptionConfig):
        """
        Initialize transcription service.
        
        Args:
            config: TranscriptionConfig instance with model settings
        """
        self.config = config
        self.model = None
        self.model_loaded = False
        self.model_loading = False
        self.model_load_error: Optional[str] = None
        
        # Thread safety
        self._model_lock = threading.Lock()
        self._model_condition = threading.Condition(self._model_lock)
        
        # Engine availability (checked lazily)
        self._engines_checked = False
        self._faster_whisper_available = False
        self._openai_whisper_available = False
        self._cuda_available = False
        
        # Status callback for UI updates
        self.status_callback: Optional[Callable[[str], None]] = None
        
        logger.info(f"TranscriptionService initialized with engine={config.engine}, model={config.model_size}")
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def _update_status(self, message: str):
        """Update status via callback if available"""
        if self.status_callback:
            try:
                self.status_callback(message)
            except Exception as e:
                logger.warning(f"Status callback failed: {e}")
    
    def _check_engine_availability(self):
        """Check which Whisper engines are available"""
        if self._engines_checked:
            return
        
        # Check faster-whisper
        self._faster_whisper_available = FASTER_WHISPER_AVAILABLE
        if self._faster_whisper_available:
            logger.info("faster-whisper engine available")
        else:
            logger.warning("faster-whisper not available")
        
        # Check openai-whisper
        self._openai_whisper_available = WHISPER_AVAILABLE
        if self._openai_whisper_available:
            logger.info("openai-whisper engine available")
        else:
            logger.warning("openai-whisper not available")
        
        # Check CUDA availability
        if TORCH_AVAILABLE:
            self._cuda_available = torch.cuda.is_available()
            logger.info(f"CUDA available: {self._cuda_available}")
        else:
            logger.info("PyTorch not available, CUDA check skipped")
        
        self._engines_checked = True
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded and ready"""
        return self.model_loaded and self.model is not None
    
    def ensure_model_loaded(self, timeout_seconds: Optional[int] = None) -> bool:
        """
        Ensure Whisper model is loaded, loading it if necessary.
        
        Args:
            timeout_seconds: Maximum time to wait for model loading
            
        Returns:
            True if model is ready, False if timeout or error
        """
        if timeout_seconds is None:
            timeout_seconds = TIMEOUT_CONFIG.MODEL_LOADING_TIMEOUT
        
        with self._model_condition:
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
                
                if not self._model_condition.wait(timeout_seconds):
                    logger.error(f"Model loading timeout after {timeout_seconds} seconds")
                    self._update_status("Model loading timeout")
                    return False
                
                return self.model_loaded
            
            # Start loading the model
            logger.info("Starting model loading...")
            self.model_loading = True
            self._update_status(f"Loading {self.config.engine} Whisper model...")
        
        # Load model outside the lock
        try:
            success = self._load_model()
            
            with self._model_condition:
                if success:
                    self.model_loaded = True
                    self.model_load_error = None
                    logger.info(f"{self.config.engine.title()} model loaded successfully!")
                    self._update_status(f"{self.config.engine.title()} model loaded successfully!")
                else:
                    self.model_load_error = "Model loading failed"
                    logger.error("Model loading failed")
                    self._update_status("Model loading failed")
                
                self.model_loading = False
                self._model_condition.notify_all()
                
                return success
                
        except Exception as e:
            with self._model_condition:
                self.model_loading = False
                self.model_load_error = f"Unexpected error: {e}"
                logger.error(f"Unexpected error loading Whisper model: {e}")
                self._update_status(f"Error loading model: {e}")
                self._model_condition.notify_all()
                return False
    
    @with_retry("model_loading")
    def _load_model(self) -> bool:
        """
        Internal method to load the Whisper model with retry logic.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        self._check_engine_availability()
        
        # Determine which engine to use
        engine = self.config.engine.lower()
        
        # Try requested engine first
        if engine == "faster" and self._faster_whisper_available:
            return self._load_faster_whisper()
        elif engine == "openai" and self._openai_whisper_available:
            return self._load_openai_whisper()
        
        # Fallback to any available engine
        logger.warning(f"Requested engine '{engine}' not available, trying fallback...")
        
        if self._faster_whisper_available:
            logger.info("Falling back to faster-whisper")
            self.config.engine = "faster"
            return self._load_faster_whisper()
        elif self._openai_whisper_available:
            logger.info("Falling back to openai-whisper")
            self.config.engine = "openai"
            return self._load_openai_whisper()
        
        logger.error("No Whisper engines available!")
        raise ModelLoadingError("No Whisper engines available. Please install faster-whisper or openai-whisper.")
    
    def _load_faster_whisper(self) -> bool:
        """Load faster-whisper model"""
        try:
            if faster_whisper is None:
                raise ModelLoadingError("faster-whisper not available")
            
            # Determine device
            device = self.config.device
            if device == "auto":
                device = "cuda" if self._cuda_available else "cpu"
            
            logger.info(f"Loading faster-whisper model: {self.config.model_size} on {device}")
            
            self.model = faster_whisper.WhisperModel(
                self.config.model_size,
                device=device,
                compute_type=self.config.compute_type
            )
            
            logger.info("faster-whisper model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load faster-whisper model: {e}")
            raise ModelLoadingError(f"faster-whisper loading failed: {e}")
    
    def _load_openai_whisper(self) -> bool:
        """Load openai-whisper model"""
        try:
            if whisper is None:
                raise ModelLoadingError("openai-whisper not available")
            
            logger.info(f"Loading openai-whisper model: {self.config.model_size}")
            
            self.model = whisper.load_model(self.config.model_size)
            
            logger.info("openai-whisper model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load openai-whisper model: {e}")
            raise ModelLoadingError(f"openai-whisper loading failed: {e}")
    
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (WAV format)
            
        Returns:
            TranscriptionResult with text or error information
        """
        start_time = time.time()
        
        # Validate audio file exists
        if not Path(audio_path).exists():
            return TranscriptionResult(
                success=False,
                error=f"Audio file not found: {audio_path}",
                error_type="FileNotFound"
            )
        
        # Ensure model is loaded
        if not self.ensure_model_loaded():
            return TranscriptionResult(
                success=False,
                error="Failed to load Whisper model",
                error_type="ModelLoadingError",
                duration_seconds=time.time() - start_time
            )
        
        # Perform transcription
        try:
            self._update_status("Transcribing...")
            
            if self.config.engine == "faster":
                result = self._transcribe_faster_whisper(audio_path)
            else:
                result = self._transcribe_openai_whisper(audio_path)
            
            duration = time.time() - start_time
            result.duration_seconds = duration
            
            if result.success:
                logger.info(f"Transcription completed in {duration:.2f}s: {result.text[:50]}...")
                self._update_status("Transcription complete!")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_type = type(e).__name__
            logger.error(f"Transcription failed: {e}")
            
            return TranscriptionResult(
                success=False,
                error=str(e),
                error_type=error_type,
                duration_seconds=duration
            )
    
    @with_retry("transcription")
    def _transcribe_faster_whisper(self, audio_path: str) -> TranscriptionResult:
        """Transcribe using faster-whisper"""
        try:
            # Configure transcription parameters
            kwargs = {}
            if self.config.language != "auto":
                kwargs["language"] = self.config.language
            
            kwargs["temperature"] = self.config.temperature
            
            # Transcribe
            segments, info = self.model.transcribe(audio_path, **kwargs)
            
            # Collect segments
            text = " ".join([segment.text for segment in segments]).strip()
            
            model_info = {
                "engine": "faster-whisper",
                "model_size": self.config.model_size,
                "language": info.language if hasattr(info, 'language') else self.config.language,
                "duration": info.duration if hasattr(info, 'duration') else 0.0
            }
            
            return TranscriptionResult(
                success=True,
                text=text,
                model_info=model_info
            )
            
        except Exception as e:
            logger.error(f"faster-whisper transcription failed: {e}")
            raise WhisperError(f"faster-whisper transcription failed: {e}")
    
    @with_retry("transcription")
    def _transcribe_openai_whisper(self, audio_path: str) -> TranscriptionResult:
        """Transcribe using openai-whisper"""
        try:
            # Configure transcription parameters
            kwargs = {}
            if self.config.language != "auto":
                kwargs["language"] = self.config.language
            
            kwargs["temperature"] = self.config.temperature
            
            # Transcribe
            result = self.model.transcribe(audio_path, **kwargs)
            
            text = result.get("text", "").strip()
            
            model_info = {
                "engine": "openai-whisper",
                "model_size": self.config.model_size,
                "language": result.get("language", self.config.language)
            }
            
            return TranscriptionResult(
                success=True,
                text=text,
                model_info=model_info
            )
            
        except Exception as e:
            logger.error(f"openai-whisper transcription failed: {e}")
            raise WhisperError(f"openai-whisper transcription failed: {e}")
    
    def unload_model(self):
        """Unload the model to free memory"""
        with self._model_lock:
            if self.model is not None:
                logger.info("Unloading Whisper model...")
                self.model = None
                self.model_loaded = False
                logger.info("Model unloaded successfully")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return {
            "model_loaded": self.model_loaded,
            "model_loading": self.model_loading,
            "model_load_error": self.model_load_error,
            "engine": self.config.engine,
            "model_size": self.config.model_size,
            "language": self.config.language
        }
