"""
core/windows_startup.py
-----------------------
Manages Windows run-at-startup via the HKCU Run registry key.
"""

import winreg
from .logging_config import get_logger

logger = get_logger(__name__)


class WindowsStartupManager:
    APP_NAME = "Whiz"
    RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def enable(self, exe_path: str) -> None:
        """Register Whiz to start with Windows, appending --tray flag."""
        value = f"{exe_path} --tray"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, self.APP_NAME, 0, winreg.REG_SZ, value)
        logger.info(f"Startup registered: {value}")

    def disable(self) -> None:
        """Remove Whiz from the Windows Run key; no-op if not present."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, self.APP_NAME)
            logger.info("Startup entry removed")
        except FileNotFoundError:
            pass

    def is_enabled(self) -> bool:
        """Return True if a Run entry for Whiz exists."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.RUN_KEY, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, self.APP_NAME)
            return True
        except FileNotFoundError:
            return False
