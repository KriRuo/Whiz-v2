#!/usr/bin/env python3
"""
core/path_validation.py
-----------------------
Path validation and sandboxing utilities for Whiz Voice-to-Text Application.

This module provides secure file operations with path validation, sandboxing,
and security checks to prevent path traversal attacks and unauthorized file access.

Features:
    - Path validation and sanitization
    - Sandboxed file operations
    - Security checks for file access
    - Safe temporary file handling
    - File size limits and validation

Author: Whiz Development Team
Last Updated: December 2024
"""

import os
import tempfile
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
from contextlib import contextmanager
import logging

from .logging_config import get_logger

logger = get_logger(__name__)

class PathValidationError(Exception):
    """Exception raised for path validation errors"""
    pass

class SandboxError(Exception):
    """Exception raised for sandboxing errors"""
    pass

class PathValidator:
    """Path validation and sanitization utilities"""
    
    # Allowed file extensions for different operations
    ALLOWED_AUDIO_EXTENSIONS = {'.wav', '.mp3', '.ogg', '.flac', '.m4a'}
    ALLOWED_CONFIG_EXTENSIONS = {'.json', '.txt', '.cfg', '.ini'}
    ALLOWED_LOG_EXTENSIONS = {'.log', '.txt'}
    
    # Maximum file sizes (in bytes)
    MAX_AUDIO_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_CONFIG_FILE_SIZE = 10 * 1024 * 1024   # 10MB
    MAX_LOG_FILE_SIZE = 50 * 1024 * 1024     # 50MB
    
    # Dangerous path patterns
    DANGEROUS_PATTERNS = [
        '..',  # Path traversal
        '~',   # Home directory
        '//',  # UNC paths
        '\\\\', # Windows UNC paths
        ':',   # Drive letters (Windows)
        '|',   # Pipe characters
        '<',   # Redirection
        '>',   # Redirection
        '*',   # Wildcards
        '?',   # Wildcards
        '"',   # Quotes
        "'",   # Quotes
        '\n',  # Newlines
        '\r',  # Carriage returns
        '\t',  # Tabs
    ]
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize path validator.
        
        Args:
            base_path: Base path for relative path resolution
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.allowed_paths: List[Path] = []
        self._add_safe_paths()
    
    def _add_safe_paths(self):
        """Add system-safe paths to allowed list"""
        safe_paths = [
            self.base_path,
            Path(tempfile.gettempdir()),
            Path.home() / '.whiz',  # User config directory
        ]
        
        for path in safe_paths:
            if path.exists():
                self.allowed_paths.append(path.resolve())
    
    def validate_path(self, path: Union[str, Path], 
                     allowed_extensions: Optional[set] = None,
                     max_size: Optional[int] = None,
                     must_exist: bool = False) -> Path:
        """
        Validate and sanitize a file path.
        
        Args:
            path: Path to validate
            allowed_extensions: Set of allowed file extensions
            max_size: Maximum file size in bytes
            must_exist: Whether the path must exist
            
        Returns:
            Validated and sanitized Path object
            
        Raises:
            PathValidationError: If validation fails
        """
        try:
            # Convert to Path object
            path_obj = Path(path)
            
            # Check for dangerous patterns
            path_str = str(path_obj)
            for pattern in self.DANGEROUS_PATTERNS:
                if pattern in path_str:
                    raise PathValidationError(f"Dangerous pattern '{pattern}' found in path: {path_str}")
            
            # Resolve path
            if path_obj.is_absolute():
                resolved_path = path_obj.resolve()
            else:
                resolved_path = (self.base_path / path_obj).resolve()
            
            # Check if path is within allowed directories
            if not self._is_path_allowed(resolved_path):
                raise PathValidationError(f"Path outside allowed directories: {resolved_path}")
            
            # Check file extension if specified
            if allowed_extensions and resolved_path.suffix.lower() not in allowed_extensions:
                raise PathValidationError(f"File extension '{resolved_path.suffix}' not allowed. Allowed: {allowed_extensions}")
            
            # Check if file exists if required
            if must_exist and not resolved_path.exists():
                raise PathValidationError(f"Required file does not exist: {resolved_path}")
            
            # Check file size if specified and file exists
            if max_size and resolved_path.exists() and resolved_path.is_file():
                file_size = resolved_path.stat().st_size
                if file_size > max_size:
                    raise PathValidationError(f"File too large: {file_size} bytes (max: {max_size})")
            
            return resolved_path
            
        except Exception as e:
            if isinstance(e, PathValidationError):
                raise
            raise PathValidationError(f"Path validation failed: {e}")
    
    def _is_path_allowed(self, path: Path) -> bool:
        """Check if path is within allowed directories"""
        for allowed_path in self.allowed_paths:
            try:
                path.relative_to(allowed_path)
                return True
            except ValueError:
                continue
        return False
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename by removing dangerous characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove dangerous characters
        sanitized = filename
        for char in self.DANGEROUS_PATTERNS:
            sanitized = sanitized.replace(char, '_')
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Ensure filename is not empty
        if not sanitized:
            sanitized = 'unnamed_file'
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
        
        return sanitized

class FileSandbox:
    """Sandboxed file operations with security checks"""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize file sandbox.
        
        Args:
            base_path: Base path for sandbox operations
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.validator = PathValidator(self.base_path)
        self.temp_dir = Path(tempfile.mkdtemp(prefix='whiz_sandbox_'))
        self.active_files: Dict[str, Any] = {}
        
        logger.info(f"File sandbox initialized at: {self.base_path}")
        logger.info(f"Temporary directory: {self.temp_dir}")
    
    def cleanup(self):
        """Clean up sandbox resources"""
        try:
            # Close all active files
            for file_handle in self.active_files.values():
                if hasattr(file_handle, 'close'):
                    file_handle.close()
            
            # Remove temporary directory
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                logger.info("Sandbox temporary directory cleaned up")
                
        except Exception as e:
            logger.error(f"Error cleaning up sandbox: {e}")
    
    @contextmanager
    def safe_open(self, path: Union[str, Path], mode: str = 'r',
                  allowed_extensions: Optional[set] = None,
                  max_size: Optional[int] = None,
                  encoding: str = 'utf-8'):
        """
        Safely open a file with validation and sandboxing.
        
        Args:
            path: File path
            mode: File open mode
            allowed_extensions: Set of allowed file extensions
            max_size: Maximum file size
            encoding: Text encoding for text files
            
        Yields:
            File handle
            
        Raises:
            SandboxError: If sandboxing fails
        """
        file_handle = None
        try:
            # Validate path
            validated_path = self.validator.validate_path(
                path, 
                allowed_extensions=allowed_extensions,
                max_size=max_size,
                must_exist=(mode in ['r', 'rb'])
            )
            
            # Open file
            if 'b' in mode:
                file_handle = open(validated_path, mode)
            else:
                file_handle = open(validated_path, mode, encoding=encoding)
            
            # Track active file
            file_id = str(id(file_handle))
            self.active_files[file_id] = file_handle
            
            logger.debug(f"Opened file safely: {validated_path}")
            yield file_handle
            
        except Exception as e:
            if file_handle:
                file_handle.close()
            raise SandboxError(f"Safe file operation failed: {e}")
        finally:
            if file_handle:
                file_id = str(id(file_handle))
                if file_id in self.active_files:
                    del self.active_files[file_id]
                file_handle.close()
    
    def safe_write(self, path: Union[str, Path], content: Union[str, bytes],
                   allowed_extensions: Optional[set] = None,
                   backup: bool = True) -> Path:
        """
        Safely write content to a file.
        
        Args:
            path: File path
            content: Content to write
            allowed_extensions: Set of allowed file extensions
            backup: Whether to create backup of existing file
            
        Returns:
            Path to written file
            
        Raises:
            SandboxError: If write operation fails
        """
        try:
            # Validate path
            validated_path = self.validator.validate_path(
                path,
                allowed_extensions=allowed_extensions,
                must_exist=False
            )
            
            # Create backup if file exists and backup requested
            if backup and validated_path.exists():
                backup_path = validated_path.with_suffix(validated_path.suffix + '.backup')
                shutil.copy2(validated_path, backup_path)
                logger.debug(f"Created backup: {backup_path}")
            
            # Ensure parent directory exists
            validated_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            if isinstance(content, str):
                with open(validated_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                with open(validated_path, 'wb') as f:
                    f.write(content)
            
            logger.debug(f"Wrote content to: {validated_path}")
            return validated_path
            
        except Exception as e:
            raise SandboxError(f"Safe write operation failed: {e}")
    
    def safe_read(self, path: Union[str, Path],
                  allowed_extensions: Optional[set] = None,
                  max_size: Optional[int] = None,
                  encoding: str = 'utf-8') -> Union[str, bytes]:
        """
        Safely read content from a file.
        
        Args:
            path: File path
            allowed_extensions: Set of allowed file extensions
            max_size: Maximum file size
            encoding: Text encoding for text files
            
        Returns:
            File content
            
        Raises:
            SandboxError: If read operation fails
        """
        try:
            # Validate path
            validated_path = self.validator.validate_path(
                path,
                allowed_extensions=allowed_extensions,
                max_size=max_size,
                must_exist=True
            )
            
            # Read content
            with open(validated_path, 'rb') as f:
                content = f.read()
            
            # Decode if text file
            if validated_path.suffix.lower() in {'.txt', '.json', '.cfg', '.ini', '.log'}:
                try:
                    content = content.decode(encoding)
                except UnicodeDecodeError:
                    # Fallback to latin-1 if utf-8 fails
                    content = content.decode('latin-1')
            
            logger.debug(f"Read content from: {validated_path}")
            return content
            
        except Exception as e:
            raise SandboxError(f"Safe read operation failed: {e}")
    
    def create_temp_file(self, suffix: str = '.tmp',
                        prefix: str = 'whiz_',
                        content: Optional[Union[str, bytes]] = None) -> Path:
        """
        Create a temporary file in the sandbox.
        
        Args:
            suffix: File suffix
            prefix: File prefix
            content: Initial content
            
        Returns:
            Path to temporary file
        """
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=suffix,
                prefix=prefix,
                dir=self.temp_dir,
                delete=False
            )
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            # Write initial content if provided
            if content is not None:
                if isinstance(content, str):
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    with open(temp_path, 'wb') as f:
                        f.write(content)
            
            logger.debug(f"Created temporary file: {temp_path}")
            return temp_path
            
        except Exception as e:
            raise SandboxError(f"Failed to create temporary file: {e}")
    
    def validate_file_integrity(self, path: Union[str, Path],
                               expected_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate file integrity and return metadata.
        
        Args:
            path: File path
            expected_hash: Expected file hash (optional)
            
        Returns:
            Dictionary with file metadata and integrity info
        """
        try:
            validated_path = self.validator.validate_path(path, must_exist=True)
            
            # Get file stats
            stat = validated_path.stat()
            
            # Calculate hash
            file_hash = hashlib.sha256()
            with open(validated_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
            
            hash_hex = file_hash.hexdigest()
            
            # Validate hash if expected
            hash_valid = True
            if expected_hash:
                hash_valid = hash_hex == expected_hash
            
            metadata = {
                'path': str(validated_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'hash': hash_hex,
                'hash_valid': hash_valid,
                'exists': True
            }
            
            logger.debug(f"File integrity validated: {validated_path}")
            return metadata
            
        except Exception as e:
            raise SandboxError(f"File integrity validation failed: {e}")

# Global sandbox instance
_global_sandbox: Optional[FileSandbox] = None

def get_sandbox() -> FileSandbox:
    """Get or create global file sandbox instance"""
    global _global_sandbox
    if _global_sandbox is None:
        _global_sandbox = FileSandbox()
    return _global_sandbox

def cleanup_sandbox():
    """Clean up global sandbox"""
    global _global_sandbox
    if _global_sandbox:
        _global_sandbox.cleanup()
        _global_sandbox = None

# Convenience functions for common operations
def safe_read_audio_file(path: Union[str, Path]) -> bytes:
    """Safely read an audio file"""
    sandbox = get_sandbox()
    return sandbox.safe_read(
        path,
        allowed_extensions=PathValidator.ALLOWED_AUDIO_EXTENSIONS,
        max_size=PathValidator.MAX_AUDIO_FILE_SIZE
    )

def safe_write_config_file(path: Union[str, Path], content: str) -> Path:
    """Safely write a configuration file"""
    sandbox = get_sandbox()
    return sandbox.safe_write(
        path,
        content,
        allowed_extensions=PathValidator.ALLOWED_CONFIG_EXTENSIONS
    )

def safe_read_config_file(path: Union[str, Path]) -> str:
    """Safely read a configuration file"""
    sandbox = get_sandbox()
    content = sandbox.safe_read(
        path,
        allowed_extensions=PathValidator.ALLOWED_CONFIG_EXTENSIONS,
        max_size=PathValidator.MAX_CONFIG_FILE_SIZE
    )
    return content if isinstance(content, str) else content.decode('utf-8')

def create_safe_temp_file(suffix: str = '.tmp', content: Optional[Union[str, bytes]] = None) -> Path:                                                      
    """Create a safe temporary file"""
    sandbox = get_sandbox()
    return sandbox.create_temp_file(suffix=suffix, content=content)        

def check_disk_space(path: str, required_mb: int = 100) -> bool:
    """
    Check if sufficient disk space is available.
    
    Args:
        path: Path to check disk space for
        required_mb: Required space in megabytes
        
    Returns:
        True if sufficient space available
        
    Raises:
        FileIOError: If insufficient disk space
    """
    import shutil
    try:
        stat = shutil.disk_usage(path)
        free_mb = stat.free / (1024 * 1024)
        
        if free_mb < required_mb:
            from core.transcription_exceptions import FileIOError
            raise FileIOError(
                f"Insufficient disk space: {free_mb:.1f}MB available, "
                f"{required_mb}MB required at {path}"
            )
        
        logger.debug(f"Disk space check passed: {free_mb:.1f}MB available")
        return True
        
    except FileIOError:
        raise  # Re-raise FileIOError
    except Exception as e:
        logger.warning(f"Could not check disk space: {e}")
        return True  # Don't fail if we can't check

def check_available_memory(required_mb: int = 500) -> bool:
    """
    Check if sufficient memory is available.
    
    Args:
        required_mb: Required memory in megabytes
        
    Returns:
        True if sufficient memory available
        
    Raises:
        MemoryError: If insufficient memory
    """
    try:
        import psutil
        mem = psutil.virtual_memory()
        available_mb = mem.available / (1024 * 1024)
        
        if available_mb < required_mb:
            raise MemoryError(
                f"Insufficient memory: {available_mb:.1f}MB available, "
                f"{required_mb}MB required"
            )
        
        logger.debug(f"Memory check passed: {available_mb:.1f}MB available")
        return True
        
    except ImportError:
        logger.warning("psutil not available, skipping memory check")
        return True
    except MemoryError:
        raise  # Re-raise MemoryError
    except Exception as e:
        logger.warning(f"Could not check memory: {e}")
        return True
