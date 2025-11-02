#!/usr/bin/env python3
"""
core/single_instance_manager.py
------------------------------
Single instance management for Whiz Voice-to-Text Application.

This module prevents multiple instances of the application from running
simultaneously by using a lock file mechanism with PID validation and
inter-process communication for window activation.

Features:
    - Cross-platform single instance enforcement
    - Lock file with PID validation and timeout
    - Window activation via platform-specific IPC
    - Stale lock cleanup (crashed instances)
    - Force-start option for recovery

Author: Whiz Development Team
Last Updated: December 2024
"""

import os
import sys
import time
import tempfile
import psutil
from typing import Optional, Tuple
from pathlib import Path

from .logging_config import get_logger
logger = get_logger(__name__)

class SingleInstanceManager:
    """
    Manages single instance enforcement using lock file mechanism.
    
    Uses a lock file containing PID and timestamp to prevent multiple
    instances. Includes platform-specific window activation.
    """
    
    def __init__(self, app_name: str = "whiz", timeout_minutes: int = 5):
        """
        Initialize single instance manager.
        
        Args:
            app_name: Application name for lock file
            timeout_minutes: Lock file timeout in minutes
        """
        self.app_name = app_name
        self.timeout_seconds = timeout_minutes * 60
        self.lock_file_path = Path(tempfile.gettempdir()) / f"{app_name}_app.lock"
        self.pid = os.getpid()
        self.lock_acquired = False
        
        logger.info(f"SingleInstanceManager initialized for PID {self.pid}")
    
    def try_acquire_lock(self) -> Tuple[bool, Optional[str]]:
        """
        Try to acquire the single instance lock.
        
        Returns:
            Tuple of (success, message)
            - success: True if lock acquired or existing instance found
            - message: Error message if failed, None if successful
        """
        try:
            # Check if lock file exists
            if not self.lock_file_path.exists():
                # No existing instance, create lock file
                self._create_lock_file()
                self.lock_acquired = True
                logger.info("Single instance lock acquired - first instance")
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
            logger.error(f"Error acquiring single instance lock: {e}")
            return False, f"Failed to acquire lock: {e}"
    
    def release_lock(self) -> None:
        """Release the single instance lock."""
        try:
            if self.lock_acquired and self.lock_file_path.exists():
                # Verify this is our lock file before removing
                existing_pid, _ = self._read_lock_file()
                if existing_pid == self.pid:
                    self.lock_file_path.unlink(missing_ok=True)
                    logger.info("Single instance lock released")
                else:
                    logger.warning("Lock file PID mismatch, not removing")
            self.lock_acquired = False
        except Exception as e:
            logger.error(f"Error releasing single instance lock: {e}")
    
    def force_release_lock(self) -> None:
        """Force release lock file (for recovery purposes)."""
        try:
            if self.lock_file_path.exists():
                self.lock_file_path.unlink(missing_ok=True)
                logger.info("Single instance lock force-released")
            self.lock_acquired = False
        except Exception as e:
            logger.error(f"Error force-releasing single instance lock: {e}")
    
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
            import win32gui
            import win32con
            
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
                
        except ImportError:
            logger.warning("win32gui not available, cannot activate window on Windows")
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
    
    def get_status(self) -> dict:
        """Get current single instance status."""
        return {
            "lock_acquired": self.lock_acquired,
            "lock_file_path": str(self.lock_file_path),
            "lock_file_exists": self.lock_file_path.exists(),
            "pid": self.pid,
            "timeout_seconds": self.timeout_seconds
        }
