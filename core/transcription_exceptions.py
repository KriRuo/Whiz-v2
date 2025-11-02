#!/usr/bin/env python3
"""
core/transcription_exceptions.py
--------------------------------
Specific exception types and retry logic for transcription operations.

This module provides specific exception types for different transcription
failure scenarios and implements retry logic with exponential backoff.

Features:
    - Specific exception types for different failure modes
    - Retry logic with exponential backoff
    - Circuit breaker pattern for repeated failures
    - Detailed error reporting and recovery suggestions

Author: Whiz Development Team
Last Updated: December 2024
"""

import time
import logging
from typing import Optional, Callable, Any, Dict, List
from enum import Enum
from dataclasses import dataclass

from .logging_config import get_logger

logger = get_logger(__name__)

class TranscriptionErrorType(Enum):
    """Types of transcription errors"""
    MODEL_LOADING = "model_loading"
    AUDIO_PROCESSING = "audio_processing"
    WHISPER_ERROR = "whisper_error"
    FILE_IO = "file_io"
    MEMORY_ERROR = "memory_error"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    PERMISSION_ERROR = "permission_error"
    UNKNOWN = "unknown"

@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True

class TranscriptionException(Exception):
    """Base exception for transcription errors"""
    
    def __init__(self, message: str, error_type: TranscriptionErrorType = TranscriptionErrorType.UNKNOWN,
                 original_exception: Optional[Exception] = None, retryable: bool = True):
        super().__init__(message)
        self.error_type = error_type
        self.original_exception = original_exception
        self.retryable = retryable
        self.timestamp = time.time()

class ModelLoadingError(TranscriptionException):
    """Exception raised when model loading fails"""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(
            f"Model loading failed: {message}",
            TranscriptionErrorType.MODEL_LOADING,
            original_exception,
            retryable=True
        )

class AudioProcessingError(TranscriptionException):
    """Exception raised when audio processing fails"""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(
            f"Audio processing failed: {message}",
            TranscriptionErrorType.AUDIO_PROCESSING,
            original_exception,
            retryable=True
        )

class WhisperError(TranscriptionException):
    """Exception raised when Whisper transcription fails"""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(
            f"Whisper transcription failed: {message}",
            TranscriptionErrorType.WHISPER_ERROR,
            original_exception,
            retryable=True
        )

class FileIOError(TranscriptionException):
    """Exception raised when file I/O operations fail"""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(
            f"File I/O error: {message}",
            TranscriptionErrorType.FILE_IO,
            original_exception,
            retryable=True
        )

class MemoryError(TranscriptionException):
    """Exception raised when memory operations fail"""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(
            f"Memory error: {message}",
            TranscriptionErrorType.MEMORY_ERROR,
            original_exception,
            retryable=False  # Memory errors are usually not retryable
        )

class TranscriptionTimeoutError(TranscriptionException):
    """Exception raised when transcription times out"""
    
    def __init__(self, message: str, timeout_seconds: float, original_exception: Optional[Exception] = None):
        super().__init__(
            f"Transcription timeout after {timeout_seconds}s: {message}",
            TranscriptionErrorType.TIMEOUT,
            original_exception,
            retryable=True
        )

class NetworkError(TranscriptionException):
    """Exception raised when network operations fail"""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(
            f"Network error: {message}",
            TranscriptionErrorType.NETWORK_ERROR,
            original_exception,
            retryable=True
        )

class PermissionError(TranscriptionException):
    """Exception raised when permission operations fail"""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(
            f"Permission error: {message}",
            TranscriptionErrorType.PERMISSION_ERROR,
            original_exception,
            retryable=False  # Permission errors usually require user intervention
        )

class TranscriptionRetryManager:
    """Manages retry logic for transcription operations"""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.failure_counts: Dict[str, int] = {}
        self.last_failure_times: Dict[str, float] = {}
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutes
    
    def should_retry(self, operation_id: str, exception: TranscriptionException) -> bool:
        """
        Determine if an operation should be retried.
        
        Args:
            operation_id: Unique identifier for the operation
            exception: The exception that occurred
            
        Returns:
            True if operation should be retried
        """
        # Don't retry if exception is not retryable
        if not exception.retryable:
            return False
        
        # Check circuit breaker
        if self._is_circuit_breaker_open(operation_id):
            return False
        
        # Check retry count
        failure_count = self.failure_counts.get(operation_id, 0)
        return failure_count < self.config.max_attempts
    
    def get_retry_delay(self, operation_id: str) -> float:
        """
        Calculate the delay before the next retry attempt.
        
        Args:
            operation_id: Unique identifier for the operation
            
        Returns:
            Delay in seconds
        """
        failure_count = self.failure_counts.get(operation_id, 0)
        
        # Calculate exponential backoff delay
        delay = self.config.base_delay * (self.config.exponential_base ** failure_count)
        
        # Apply maximum delay limit
        delay = min(delay, self.config.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.config.jitter:
            import random
            jitter_factor = random.uniform(0.5, 1.5)
            delay *= jitter_factor
        
        return delay
    
    def record_failure(self, operation_id: str, exception: TranscriptionException):
        """Record a failure for an operation"""
        self.failure_counts[operation_id] = self.failure_counts.get(operation_id, 0) + 1
        self.last_failure_times[operation_id] = time.time()
        
        logger.warning(f"Operation {operation_id} failed (attempt {self.failure_counts[operation_id]}): {exception}")
    
    def record_success(self, operation_id: str):
        """Record a success for an operation, resetting failure count"""
        if operation_id in self.failure_counts:
            del self.failure_counts[operation_id]
        if operation_id in self.last_failure_times:
            del self.last_failure_times[operation_id]
        
        logger.debug(f"Operation {operation_id} succeeded, resetting failure count")
    
    def _is_circuit_breaker_open(self, operation_id: str) -> bool:
        """Check if circuit breaker is open for an operation"""
        failure_count = self.failure_counts.get(operation_id, 0)
        last_failure_time = self.last_failure_times.get(operation_id, 0)
        
        if failure_count >= self.circuit_breaker_threshold:
            # Check if enough time has passed to reset circuit breaker
            if time.time() - last_failure_time > self.circuit_breaker_timeout:
                # Reset circuit breaker
                self.failure_counts[operation_id] = 0
                self.last_failure_times[operation_id] = 0
                logger.info(f"Circuit breaker reset for operation {operation_id}")
                return False
            else:
                logger.warning(f"Circuit breaker open for operation {operation_id}")
                return True
        
        return False
    
    def get_operation_stats(self, operation_id: str) -> Dict[str, Any]:
        """Get statistics for an operation"""
        return {
            'failure_count': self.failure_counts.get(operation_id, 0),
            'last_failure_time': self.last_failure_times.get(operation_id, 0),
            'circuit_breaker_open': self._is_circuit_breaker_open(operation_id)
        }

def with_retry(operation_id: str, retry_manager: Optional[TranscriptionRetryManager] = None,
               config: Optional[RetryConfig] = None):
    """
    Decorator to add retry logic to transcription operations.
    
    Args:
        operation_id: Unique identifier for the operation
        retry_manager: Retry manager instance (optional)
        config: Retry configuration (optional)
    """
    if retry_manager is None:
        retry_manager = TranscriptionRetryManager(config)
    
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            attempt = 0
            
            while True:
                try:
                    result = func(*args, **kwargs)
                    retry_manager.record_success(operation_id)
                    return result
                    
                except TranscriptionException as e:
                    attempt += 1
                    
                    if not retry_manager.should_retry(operation_id, e):
                        logger.error(f"Operation {operation_id} failed permanently after {attempt} attempts")
                        raise
                    
                    retry_manager.record_failure(operation_id, e)
                    
                    delay = retry_manager.get_retry_delay(operation_id)
                    logger.info(f"Retrying operation {operation_id} in {delay:.2f}s (attempt {attempt + 1})")
                    time.sleep(delay)
                    
                except Exception as e:
                    # Convert generic exceptions to TranscriptionException
                    transcription_exception = TranscriptionException(
                        f"Unexpected error in {operation_id}: {str(e)}",
                        TranscriptionErrorType.UNKNOWN,
                        e
                    )
                    
                    if not retry_manager.should_retry(operation_id, transcription_exception):
                        logger.error(f"Operation {operation_id} failed permanently after {attempt} attempts")
                        raise transcription_exception
                    
                    retry_manager.record_failure(operation_id, transcription_exception)
                    
                    delay = retry_manager.get_retry_delay(operation_id)
                    logger.info(f"Retrying operation {operation_id} in {delay:.2f}s (attempt {attempt + 1})")
                    time.sleep(delay)
            
        return wrapper
    return decorator

def classify_exception(exception: Exception) -> TranscriptionException:
    """
    Classify a generic exception into a specific TranscriptionException.
    
    Args:
        exception: The original exception
        
    Returns:
        Appropriate TranscriptionException
    """
    error_message = str(exception)
    error_type = type(exception)
    
    # Classify based on exception type and message
    if isinstance(exception, FileNotFoundError):
        return FileIOError(f"File not found: {error_message}", exception)
    elif isinstance(exception, PermissionError):
        return PermissionError(f"Permission denied: {error_message}", exception)
    elif isinstance(exception, MemoryError):
        return MemoryError(f"Insufficient memory: {error_message}", exception)
    elif isinstance(exception, TimeoutError):
        return TranscriptionTimeoutError(f"Operation timed out: {error_message}", 30.0, exception)
    elif isinstance(exception, ConnectionError):
        return NetworkError(f"Connection failed: {error_message}", exception)
    elif "whisper" in error_message.lower():
        return WhisperError(f"Whisper error: {error_message}", exception)
    elif "audio" in error_message.lower():
        return AudioProcessingError(f"Audio processing error: {error_message}", exception)
    elif "model" in error_message.lower():
        return ModelLoadingError(f"Model error: {error_message}", exception)
    else:
        return TranscriptionException(f"Unknown error: {error_message}", TranscriptionErrorType.UNKNOWN, exception)

# Global retry manager instance
_global_retry_manager: Optional[TranscriptionRetryManager] = None

def get_retry_manager() -> TranscriptionRetryManager:
    """Get or create global retry manager instance"""
    global _global_retry_manager
    if _global_retry_manager is None:
        _global_retry_manager = TranscriptionRetryManager()
    return _global_retry_manager
