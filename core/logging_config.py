#!/usr/bin/env python3
"""
core/logging_config.py
---------------------
Centralized logging framework for Whiz Voice-to-Text Application.

This module provides a comprehensive logging system with file rotation,
platform-specific paths, and structured output. It supports multiple
log levels and both console and file output.

Features:
    - Centralized logging configuration
    - File rotation with size limits
    - Platform-specific log directories
    - Multiple log files (main, error, debug)
    - Structured log format with timestamps
    - Thread-safe logging operations

Dependencies:
    - logging: Python's built-in logging module
    - pathlib: Cross-platform path handling
    - tempfile: Temporary directory creation

Example:
    Basic usage:
        from core.logging_config import initialize_logging, get_logger
        
        initialize_logging(log_level='INFO', log_to_file=True)
        logger = get_logger(__name__)
        logger.info("Application started")

Author: Whiz Development Team
Last Updated: October 10, 2025
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

class LogLevel:
    """Log level constants"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LoggingConfig:
    """Centralized logging configuration"""
    
    def __init__(self, 
                 log_level: str = LogLevel.INFO,
                 log_to_file: bool = True,
                 log_to_console: bool = True,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 log_dir: Optional[Path] = None):
        """
        Initialize logging configuration.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file
            log_to_console: Whether to log to console
            max_file_size: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
            log_dir: Custom log directory (uses platform default if None)
        """
        self.log_level = log_level.upper()
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Use provided log_dir or create a default one
        if log_dir is None:
            # Create a simple default log directory to avoid circular import
            import tempfile
            temp_base = Path(tempfile.gettempdir())
            self.log_dir = temp_base / 'whiz' / 'logs'
        else:
            self.log_dir = log_dir
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file paths
        self.main_log_file = self.log_dir / "whiz.log"
        self.error_log_file = self.log_dir / "whiz_errors.log"
        self.debug_log_file = self.log_dir / "whiz_debug.log"
        
        # Initialize logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Set up the logging configuration"""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set root logger level
        root_logger.setLevel(getattr(logging, self.log_level))
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler
        if self.log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(simple_formatter)
            root_logger.addHandler(console_handler)
        
        # File handlers
        if self.log_to_file:
            # Main log file (rotating)
            main_handler = logging.handlers.RotatingFileHandler(
                self.main_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            main_handler.setLevel(logging.DEBUG)
            main_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(main_handler)
            
            # Error log file (errors and above)
            error_handler = logging.handlers.RotatingFileHandler(
                self.error_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(error_handler)
            
            # Debug log file (debug only, if debug level)
            if self.log_level == LogLevel.DEBUG:
                debug_handler = logging.handlers.RotatingFileHandler(
                    self.debug_log_file,
                    maxBytes=self.max_file_size,
                    backupCount=self.backup_count,
                    encoding='utf-8'
                )
                debug_handler.setLevel(logging.DEBUG)
                debug_handler.setFormatter(detailed_formatter)
                root_logger.addHandler(debug_handler)
        
        # Log startup information
        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info("Whiz Logging System Initialized")
        logger.info(f"Log Level: {self.log_level}")
        logger.info(f"Log Directory: {self.log_dir}")
        logger.info(f"Main Log File: {self.main_log_file}")
        logger.info(f"Error Log File: {self.error_log_file}")
        if self.log_level == LogLevel.DEBUG:
            logger.info(f"Debug Log File: {self.debug_log_file}")
        logger.info("=" * 60)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)
    
    def set_level(self, level: str) -> None:
        """
        Change the logging level at runtime.
        
        Args:
            level: New logging level
        """
        self.log_level = level.upper()
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level))
        
        logger = logging.getLogger(__name__)
        logger.info(f"Log level changed to: {self.log_level}")
    
    def enable_debug(self) -> None:
        """Enable debug logging"""
        self.set_level(LogLevel.DEBUG)
    
    def disable_debug(self) -> None:
        """Disable debug logging (set to INFO)"""
        self.set_level(LogLevel.INFO)
    
    def get_log_files(self) -> Dict[str, Path]:
        """
        Get paths to all log files.
        
        Returns:
            Dictionary mapping log type to file path
        """
        files = {
            "main": self.main_log_file,
            "errors": self.error_log_file
        }
        
        if self.log_level == LogLevel.DEBUG:
            files["debug"] = self.debug_log_file
        
        return files
    
    def get_log_info(self) -> Dict[str, Any]:
        """
        Get information about the current logging configuration.
        
        Returns:
            Dictionary with logging information
        """
        log_files = self.get_log_files()
        file_sizes = {}
        
        for log_type, log_file in log_files.items():
            if log_file.exists():
                file_sizes[log_type] = log_file.stat().st_size
            else:
                file_sizes[log_type] = 0
        
        return {
            "log_level": self.log_level,
            "log_dir": str(self.log_dir),
            "log_files": {k: str(v) for k, v in log_files.items()},
            "file_sizes": file_sizes,
            "max_file_size": self.max_file_size,
            "backup_count": self.backup_count,
            "log_to_file": self.log_to_file,
            "log_to_console": self.log_to_console
        }
    
    def cleanup_old_logs(self, days_to_keep: int = 30) -> None:
        """
        Clean up old log files.
        
        Args:
            days_to_keep: Number of days of logs to keep
        """
        import time
        
        logger = logging.getLogger(__name__)
        current_time = time.time()
        cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
        
        cleaned_count = 0
        
        for log_file in self.log_dir.glob("whiz*.log*"):
            try:
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    cleaned_count += 1
                    logger.info(f"Cleaned up old log file: {log_file}")
            except Exception as e:
                logger.warning(f"Error cleaning up log file {log_file}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old log files")
    
    def log_system_info(self) -> None:
        """Log system information for debugging"""
        logger = logging.getLogger(__name__)
        
        try:
            import platform
            import psutil
            
            logger.info("System Information:")
            logger.info(f"  Platform: {platform.platform()}")
            logger.info(f"  Python: {platform.python_version()}")
            logger.info(f"  CPU Count: {psutil.cpu_count()}")
            logger.info(f"  Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
            logger.info(f"  Disk Space: {psutil.disk_usage('/').free / (1024**3):.1f} GB free")
            
        except ImportError:
            logger.warning("psutil not available for system info")
        except Exception as e:
            logger.warning(f"Error getting system info: {e}")

# Global logging configuration instance
_logging_config: Optional[LoggingConfig] = None

def initialize_logging(log_level: str = LogLevel.INFO,
                      log_to_file: bool = True,
                      log_to_console: bool = True,
                      max_file_size: int = 10 * 1024 * 1024,
                      backup_count: int = 5,
                      log_dir: Optional[Path] = None) -> LoggingConfig:
    """
    Initialize the global logging configuration.
    
    Args:
        log_level: Logging level
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        log_dir: Custom log directory
        
    Returns:
        LoggingConfig instance
    """
    global _logging_config
    _logging_config = LoggingConfig(
        log_level=log_level,
        log_to_file=log_to_file,
        log_to_console=log_to_console,
        max_file_size=max_file_size,
        backup_count=backup_count,
        log_dir=log_dir
    )
    return _logging_config

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    if _logging_config is None:
        # Fallback to basic logging if not initialized
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)
    
    return _logging_config.get_logger(name)

def get_logging_config() -> Optional[LoggingConfig]:
    """
    Get the current logging configuration.
    
    Returns:
        LoggingConfig instance or None if not initialized
    """
    return _logging_config

def set_log_level(level: str) -> None:
    """
    Change the global logging level.
    
    Args:
        level: New logging level
    """
    if _logging_config:
        _logging_config.set_level(level)

def enable_debug_logging() -> None:
    """Enable debug logging globally"""
    if _logging_config:
        _logging_config.enable_debug()

def disable_debug_logging() -> None:
    """Disable debug logging globally"""
    if _logging_config:
        _logging_config.disable_debug()

def cleanup_logs(days_to_keep: int = 30) -> None:
    """
    Clean up old log files.
    
    Args:
        days_to_keep: Number of days of logs to keep
    """
    if _logging_config:
        _logging_config.cleanup_old_logs(days_to_keep)

def log_system_info() -> None:
    """Log system information for debugging"""
    if _logging_config:
        _logging_config.log_system_info()
