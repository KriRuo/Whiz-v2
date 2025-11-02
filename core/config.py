#!/usr/bin/env python3
"""
core/config.py
--------------
Central configuration constants for Whiz Voice-to-Text Application.

This module provides centralized configuration values to eliminate magic numbers
and make the application easier to maintain and tune.

Author: Whiz Development Team
Last Updated: January 2025
"""

from dataclasses import dataclass
from typing import Final

@dataclass(frozen=True)
class AudioConfig:
    """Audio recording and processing configuration"""
    SAMPLE_RATE: Final[int] = 16000  # Whisper's optimal sample rate
    CHANNELS: Final[int] = 1  # Mono audio
    CHUNK_SIZE: Final[int] = 2048  # Audio buffer chunk size
    MAX_RECORDING_DURATION_SECONDS: Final[int] = 600  # 10 minutes max
    MIN_RECORDING_DURATION_SECONDS: Final[float] = 0.5  # Minimum recording length
    SILENCE_THRESHOLD: Final[float] = 0.01  # Audio level threshold for silence detection

@dataclass(frozen=True)
class TimeoutConfig:
    """Timeout values for various operations"""
    MODEL_LOADING_TIMEOUT: Final[float] = 30.0  # Model loading timeout
    MODEL_IDLE_TIMEOUT: Final[float] = 300.0  # 5 minutes before unloading idle model
    TRANSCRIPTION_TIMEOUT: Final[float] = 60.0  # Transcription operation timeout
    CLEANUP_TASK_TIMEOUT: Final[float] = 10.0  # Individual cleanup task timeout
    GLOBAL_CLEANUP_TIMEOUT: Final[float] = 60.0  # Overall cleanup timeout

@dataclass(frozen=True)
class MemoryConfig:
    """Memory management configuration"""
    MIN_AVAILABLE_MEMORY_MB: Final[int] = 500  # Minimum MB required
    MIN_DISK_SPACE_MB: Final[int] = 100  # Minimum disk space MB required
    MAX_TRANSCRIPT_HISTORY: Final[int] = 100  # Maximum transcripts to keep in memory

@dataclass(frozen=True)
class WhisperConfig:
    """Whisper model configuration"""
    DEFAULT_ENGINE: Final[str] = "faster"  # Default to faster-whisper
    AVAILABLE_ENGINES: Final[tuple] = ("openai", "faster")
    AVAILABLE_MODELS: Final[tuple] = ("tiny", "base", "small", "medium", "large")
    DEFAULT_MODEL: Final[str] = "tiny"
    DEFAULT_TEMPERATURE: Final[float] = 0.0  # Most deterministic
    DEFAULT_LANGUAGE: Final[str] = "auto"  # Auto-detect language
    
    # faster-whisper specific settings
    BEAM_SIZE: Final[int] = 5  # Beam search size
    VAD_FILTER: Final[bool] = True  # Voice activity detection
    COMPUTE_TYPE_CPU: Final[str] = "int8"  # CPU inference type
    COMPUTE_TYPE_GPU: Final[str] = "float16"  # GPU inference type

# Singleton instances for easy access
AUDIO_CONFIG = AudioConfig()
TIMEOUT_CONFIG = TimeoutConfig()
MEMORY_CONFIG = MemoryConfig()
WHISPER_CONFIG = WhisperConfig()

# Convenience function for logging configuration
def log_config():
    """Log current configuration for debugging"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Audio Config: {AUDIO_CONFIG}")
    logger.info(f"Timeout Config: {TIMEOUT_CONFIG}")
    logger.info(f"Memory Config: {MEMORY_CONFIG}")
    logger.info(f"Whisper Config: {WHISPER_CONFIG}")
