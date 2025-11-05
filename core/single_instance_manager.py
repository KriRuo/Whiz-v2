#!/usr/bin/env python3
"""
core/single_instance_manager.py
------------------------------
Single instance management for Whiz Voice-to-Text Application.

This module prevents multiple instances of the application from running
simultaneously using a hybrid approach:
- Primary lock: Qt's QSharedMemory + QSystemSemaphore for atomic, cross-platform locking
- Secondary lock: File-based lock for PID tracking and window activation

Features:
    - Cross-platform single instance enforcement (Windows, Linux, macOS)
    - Atomic operations preventing race conditions
    - Window activation via platform-specific IPC
    - Automatic cleanup via OS (shared memory)
    - Manual cleanup via CleanupManager integration
    - Force-start option for recovery

Author: Whiz Development Team
Last Updated: December 2024
"""

import os
import sys
import time
import tempfile
import psutil
import atexit
import signal
from typing import Optional, Tuple
from pathlib import Path

try:
    from PyQt5.QtCore import QSharedMemory, QSystemSemaphore
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    QSharedMemory = None
    QSystemSemaphore = None

from .logging_config import get_logger
logger = get_logger(__name__)

class SingleInstanceManager:
    """
    Manages single instance enforcement using hybrid approach:
    - Primary: Qt's QSharedMemory + QSystemSemaphore (atomic, cross-platform)
    - Secondary: File-based lock (PID tracking, window activation)
    
    Includes platform-specific window activation and cleanup integration.
    """
    
    def __init__(self, app_name: str = "whiz", timeout_minutes: int = 5):
        """
        Initialize single instance manager.
        
        Args:
            app_name: Application name for lock identifiers
            timeout_minutes: Lock file timeout in minutes (for stale lock detection)
        """
        self.app_name = app_name
        self.timeout_seconds = timeout_minutes * 60
        self.pid = os.getpid()
        self.lock_acquired = False
        
        # Qt-based primary lock (atomic, cross-platform)
        self.shared_memory = None
        self.semaphore = None
        self._qt_lock_key = f"{app_name}_single_instance"
        self._qt_semaphore_key = f"{app_name}_single_instance_sem"
        
        # File-based secondary lock (PID tracking, window activation)
        self.lock_file_path = Path(tempfile.gettempdir()) / f"{app_name}_app.lock"
        
        # Register cleanup handlers
        self._register_cleanup_handlers()
        
        logger.info(f"SingleInstanceManager initialized for PID {self.pid}")
    
    def try_acquire_lock(self) -> Tuple[bool, Optional[str]]:
        """
        Try to acquire the single instance lock using Qt's atomic primitives.
        
        Returns:
            Tuple of (success, message)
            - success: True if lock acquired or existing instance found
            - message: Error message if failed, None if successful, or activation message
        """
        try:
            # Try Qt-based atomic lock first (primary mechanism)
            if QT_AVAILABLE:
                qt_result = self._try_acquire_qt_lock()
                if qt_result is not None:
                    return qt_result
            
            # Fallback to file-based lock if Qt is not available
            logger.warning("Qt not available, falling back to file-based lock")
            return self._try_acquire_file_lock()
                
        except Exception as e:
            logger.error(f"Error acquiring single instance lock: {e}")
            return False, f"Failed to acquire lock: {e}"
    
    def _try_acquire_qt_lock(self) -> Optional[Tuple[bool, Optional[str]]]:
        """Try to acquire lock using Qt's QSharedMemory + QSystemSemaphore."""
        try:
            # Check if QApplication exists (required for QSharedMemory on some platforms)
            from PyQt5.QtWidgets import QApplication
            app_instance = QApplication.instance()
            if app_instance is None:
                # QApplication not created yet - this is OK, QSharedMemory can work without it
                # but we'll log it for debugging
                logger.debug("QApplication not yet created, but proceeding with QSharedMemory")
            
            # Initialize Qt primitives
            self.shared_memory = QSharedMemory(self._qt_lock_key)
            self.semaphore = QSystemSemaphore(self._qt_semaphore_key, 1)
            
            # Acquire semaphore to ensure atomic operation
            if not self.semaphore.acquire():
                logger.error("Failed to acquire semaphore for single instance check")
                return False, "Failed to acquire semaphore"
            
            try:
                # Try to create shared memory (atomic operation)
                if self.shared_memory.create(512):  # Create 512 bytes
                    # Success: We're the first instance!
                    logger.info("Single instance lock acquired (Qt) - first instance")
                    self.lock_acquired = True
                    
                    # Create file-based lock for PID tracking
                    self._create_lock_file()
                    
                    return True, None
                else:
                    # Shared memory already exists - another instance is running
                    error = self.shared_memory.error()
                    
                    if error == QSharedMemory.AlreadyExists:
                        # Another instance exists - try to activate it
                        logger.info("Existing instance found (Qt shared memory), attempting activation")
                        
                        # Try to attach to shared memory to verify it exists
                        if self.shared_memory.attach():
                            self.shared_memory.detach()
                        
                        # Get PID from file lock for window activation
                        existing_pid, _ = self._read_lock_file()
                        
                        if existing_pid and self._is_process_running(existing_pid):
                            if self._activate_existing_window():
                                logger.info("Successfully activated existing window")
                                return True, "Existing instance activated"
                            else:
                                logger.warning("Failed to activate existing window")
                                return False, "Existing instance found but could not be activated"
                        else:
                            # Stale lock - clean up and try again
                            logger.warning("Stale Qt lock detected, cleaning up")
                            self._cleanup_qt_lock()
                            # Retry once
                            if self.shared_memory.create(512):
                                self.lock_acquired = True
                                self._create_lock_file()
                                return True, None
                            else:
                                return False, "Failed to acquire lock after cleanup"
                    else:
                        logger.error(f"QSharedMemory error: {error}")
                        return False, f"Shared memory error: {error}"
            finally:
                self.semaphore.release()
                
        except Exception as e:
            logger.error(f"Error in Qt lock acquisition: {e}")
            if self.semaphore:
                try:
                    self.semaphore.release()
                except:
                    pass
            return None  # Indicate fallback should be used
    
    def _try_acquire_file_lock(self) -> Tuple[bool, Optional[str]]:
        """Fallback file-based lock acquisition."""
        try:
            # Check if lock file exists
            if not self.lock_file_path.exists():
                # No existing instance, create lock file
                self._create_lock_file()
                self.lock_acquired = True
                logger.info("Single instance lock acquired (file) - first instance")
                return True, None
            
            # Lock file exists, check if it's valid
            existing_pid, lock_time = self._read_lock_file()
            
            if existing_pid is None:
                # Invalid lock file, remove it and create new one
                logger.warning("Invalid lock file found, removing and creating new one")
                self.lock_file_path.unlink(missing_ok=True)
                self._create_lock_file()
                self.lock_acquired = True
                return True, None
            
            # Check if existing process is still running
            if self._is_process_running(existing_pid):
                # Check if lock is stale (older than timeout)
                if time.time() - lock_time > self.timeout_seconds:
                    logger.warning(f"Stale lock file found (PID {existing_pid}), removing")
                    self.lock_file_path.unlink(missing_ok=True)
                    self._create_lock_file()
                    self.lock_acquired = True
                    return True, None
                else:
                    # Valid existing instance, try to activate it
                    logger.info(f"Existing instance found (PID {existing_pid}), attempting activation")
                    if self._activate_existing_window():
                        logger.info("Successfully activated existing window")
                        return True, "Existing instance activated"
                    else:
                        logger.warning("Failed to activate existing window")
                        return False, "Existing instance found but could not be activated"
            else:
                # Process not running, remove stale lock
                logger.info(f"Stale lock file found (PID {existing_pid} not running), removing")
                self.lock_file_path.unlink(missing_ok=True)
                self._create_lock_file()
                self.lock_acquired = True
                return True, None
                
        except Exception as e:
            logger.error(f"Error in file lock acquisition: {e}")
            return False, f"Failed to acquire file lock: {e}"
    
    def release_lock(self) -> bool:
        """
        Release the single instance lock.
        
        Returns:
            True if lock was released successfully, False otherwise
        """
        try:
            success = True
            
            # Release Qt-based lock
            if self.shared_memory:
                try:
                    if self.lock_acquired:
                        if self.semaphore:
                            if not self.semaphore.acquire():
                                logger.warning("Failed to acquire semaphore for cleanup")
                            else:
                                try:
                                    self.shared_memory.detach()
                                    if self.shared_memory.isAttached():
                                        logger.warning("Shared memory still attached after detach")
                                    else:
                                        logger.debug("Qt shared memory detached")
                                finally:
                                    self.semaphore.release()
                        
                        # Clean up shared memory segment
                        self._cleanup_qt_lock()
                except Exception as e:
                    logger.error(f"Error releasing Qt lock: {e}")
                    success = False
            
            # Release file-based lock
            if self.lock_acquired and self.lock_file_path.exists():
                try:
                    # Verify this is our lock file before removing
                    existing_pid, _ = self._read_lock_file()
                    if existing_pid == self.pid:
                        self.lock_file_path.unlink(missing_ok=True)
                        logger.info("Single instance lock released")
                    else:
                        logger.warning("Lock file PID mismatch, not removing")
                except Exception as e:
                    logger.error(f"Error releasing file lock: {e}")
                    success = False
            
            self.lock_acquired = False
            return success
            
        except Exception as e:
            logger.error(f"Error releasing single instance lock: {e}")
            return False
    
    def _cleanup_qt_lock(self) -> None:
        """Clean up Qt shared memory and semaphore."""
        try:
            if self.shared_memory:
                if self.shared_memory.isAttached():
                    self.shared_memory.detach()
                
                # On Unix systems, we need to explicitly remove the shared memory segment
                if sys.platform != "win32":
                    try:
                        self.shared_memory.detach()
                        # The shared memory will be automatically cleaned up by the OS
                        # when no processes are attached, but we can try to remove it
                        if hasattr(self.shared_memory, 'key') and self.shared_memory.key():
                            logger.debug("Qt shared memory cleaned up")
                    except Exception as e:
                        logger.debug(f"Error cleaning up Qt shared memory: {e}")
        except Exception as e:
            logger.warning(f"Error in Qt lock cleanup: {e}")
    
    def force_release_lock(self) -> None:
        """Force release all locks (for recovery purposes)."""
        try:
            # Force cleanup Qt locks
            if self.shared_memory:
                self._cleanup_qt_lock()
            
            # Force cleanup file lock
            if self.lock_file_path.exists():
                self.lock_file_path.unlink(missing_ok=True)
                logger.info("Single instance lock force-released")
            
            self.lock_acquired = False
        except Exception as e:
            logger.error(f"Error force-releasing single instance lock: {e}")
    
    def _register_cleanup_handlers(self) -> None:
        """Register cleanup handlers for signal and atexit."""
        # Register atexit handler
        atexit.register(self._cleanup_on_exit)
        
        # Register signal handlers (Unix)
        if sys.platform != "win32":
            try:
                signal.signal(signal.SIGTERM, self._signal_handler)
                signal.signal(signal.SIGINT, self._signal_handler)
            except Exception as e:
                logger.warning(f"Could not register signal handlers: {e}")
    
    def _cleanup_on_exit(self) -> None:
        """Cleanup handler called on normal exit."""
        if self.lock_acquired:
            logger.debug("Cleaning up single instance lock on exit")
            self.release_lock()
    
    def _signal_handler(self, signum, frame) -> None:
        """Signal handler for SIGTERM/SIGINT."""
        logger.info(f"Received signal {signum}, cleaning up single instance lock")
        if self.lock_acquired:
            self.release_lock()
        # Re-raise signal to allow normal termination
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
    
    def _create_lock_file(self) -> None:
        """Create lock file with current PID and timestamp."""
        try:
            lock_content = f"{self.pid}\n{time.time()}"
            self.lock_file_path.write_text(lock_content, encoding='utf-8')
            logger.debug(f"Lock file created: {self.lock_file_path}")
        except Exception as e:
            logger.error(f"Error creating lock file: {e}")
            raise
    
    def _read_lock_file(self) -> Tuple[Optional[int], Optional[float]]:
        """
        Read lock file and return PID and timestamp.
        
        Returns:
            Tuple of (pid, timestamp) or (None, None) if invalid
        """
        try:
            if not self.lock_file_path.exists():
                return None, None
            
            content = self.lock_file_path.read_text(encoding='utf-8').strip()
            lines = content.split('\n')
            
            if len(lines) != 2:
                logger.warning(f"Invalid lock file format: {content}")
                return None, None
            
            pid = int(lines[0])
            timestamp = float(lines[1])
            
            return pid, timestamp
            
        except (ValueError, FileNotFoundError) as e:
            logger.warning(f"Error reading lock file: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Unexpected error reading lock file: {e}")
            return None, None
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if process with given PID is still running."""
        try:
            return psutil.pid_exists(pid)
        except Exception as e:
            logger.warning(f"Error checking if process {pid} exists: {e}")
            return False
    
    def _activate_existing_window(self) -> bool:
        """
        Activate existing application window.
        
        Returns:
            True if window was activated successfully, False otherwise
        """
        try:
            if sys.platform == "win32":
                return self._activate_window_windows()
            elif sys.platform == "darwin":
                return self._activate_window_macos()
            elif sys.platform.startswith("linux"):
                return self._activate_window_linux()
            else:
                logger.warning(f"Window activation not supported on platform: {sys.platform}")
                return False
        except Exception as e:
            logger.error(f"Error activating existing window: {e}")
            return False
    
    def _activate_window_windows(self) -> bool:
        """Activate window on Windows using win32gui."""
        try:
            # Conditional import - only available on Windows
            try:
                import win32gui
                import win32con
            except ImportError:
                logger.warning("win32gui not available, cannot activate window on Windows")
                return False
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if "Whiz" in window_title:
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                hwnd = windows[0]  # Take the first matching window
                
                # Restore if minimized
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                
                # Bring to foreground
                win32gui.SetForegroundWindow(hwnd)
                logger.info("Windows window activated successfully")
                return True
            else:
                logger.warning("No Whiz window found on Windows")
                return False
                
        except Exception as e:
            logger.error(f"Error activating Windows window: {e}")
            return False
    
    def _activate_window_macos(self) -> bool:
        """Activate window on macOS using AppleScript."""
        try:
            import subprocess
            
            # Use AppleScript to activate Whiz application
            script = '''
            tell application "System Events"
                set whizProcesses to (every process whose name contains "Whiz")
                if (count of whizProcesses) > 0 then
                    set frontmost of item 1 of whizProcesses to true
                    return "activated"
                else
                    return "not_found"
                end if
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and "activated" in result.stdout:
                logger.info("macOS window activated successfully")
                return True
            else:
                logger.warning(f"Failed to activate macOS window: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.warning("AppleScript timeout when activating macOS window")
            return False
        except Exception as e:
            logger.error(f"Error activating macOS window: {e}")
            return False
    
    def _activate_window_linux(self) -> bool:
        """Activate window on Linux using wmctrl."""
        try:
            import subprocess
            
            # Try wmctrl first (most common)
            try:
                result = subprocess.run(
                    ["wmctrl", "-a", "Whiz"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info("Linux window activated successfully with wmctrl")
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Fallback to xdotool
            try:
                result = subprocess.run(
                    ["xdotool", "search", "--name", "Whiz", "windowactivate"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info("Linux window activated successfully with xdotool")
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            logger.warning("No window manager tool available for Linux activation")
            return False
            
        except Exception as e:
            logger.error(f"Error activating Linux window: {e}")
            return False
    
    def cleanup_for_manager(self) -> bool:
        """
        Cleanup method for CleanupManager integration.
        
        Returns:
            True if cleanup was successful, False otherwise
        """
        return self.release_lock()
    
    def get_status(self) -> dict:
        """Get current single instance status."""
        status = {
            "lock_acquired": self.lock_acquired,
            "lock_file_path": str(self.lock_file_path),
            "lock_file_exists": self.lock_file_path.exists(),
            "pid": self.pid,
            "timeout_seconds": self.timeout_seconds,
            "qt_available": QT_AVAILABLE
        }
        
        if self.shared_memory:
            status["qt_shared_memory_key"] = self._qt_lock_key
            status["qt_shared_memory_attached"] = self.shared_memory.isAttached() if self.shared_memory else False
        
        return status
