"""
Platform Utilities for Cross-Platform Compatibility

This module provides platform detection and utilities for handling
platform-specific behaviors and paths.
"""

import os
import sys
import platform
from typing import Optional, Dict, Any
from pathlib import Path

from .logging_config import get_logger
logger = get_logger(__name__)

class PlatformType:
    """Platform type enumeration"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"

class PlatformUtils:
    """Cross-platform utility functions"""
    
    @staticmethod
    def get_platform() -> str:
        """
        Get the current platform type.
        
        Returns:
            Platform type string (windows, linux, macos, unknown)
        """
        system = platform.system().lower()
        
        if system == "windows":
            return PlatformType.WINDOWS
        elif system == "linux":
            return PlatformType.LINUX
        elif system == "darwin":
            return PlatformType.MACOS
        else:
            return PlatformType.UNKNOWN
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows"""
        return PlatformUtils.get_platform() == PlatformType.WINDOWS
    
    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux"""
        return PlatformUtils.get_platform() == PlatformType.LINUX
    
    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS"""
        return PlatformUtils.get_platform() == PlatformType.MACOS
    
    @staticmethod
    def get_platform_info() -> Dict[str, Any]:
        """
        Get detailed platform information.
        
        Returns:
            Dictionary with platform information
        """
        return {
            "platform": PlatformUtils.get_platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation()
        }
    
    @staticmethod
    def get_config_dir() -> Path:
        """
        Get the platform-specific configuration directory.
        
        Returns:
            Path to configuration directory
        """
        platform_type = PlatformUtils.get_platform()
        
        if platform_type == PlatformType.WINDOWS:
            # Windows: %APPDATA%\\Whiz
            config_dir = Path(os.environ.get('APPDATA', '')) / 'Whiz'
        elif platform_type == PlatformType.MACOS:
            # macOS: ~/Library/Application Support/Whiz
            config_dir = Path.home() / 'Library' / 'Application Support' / 'Whiz'
        elif platform_type == PlatformType.LINUX:
            # Linux: ~/.config/Whiz
            config_dir = Path.home() / '.config' / 'Whiz'
        else:
            # Fallback: ~/.whiz
            config_dir = Path.home() / '.whiz'
        
        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    @staticmethod
    def get_temp_dir() -> Path:
        """
        Get the platform-specific temporary directory.
        
        Returns:
            Path to temporary directory
        """
        import tempfile
        
        # Use system temp directory with app-specific subdirectory
        temp_base = Path(tempfile.gettempdir())
        temp_dir = temp_base / 'whiz'
        
        # Create directory if it doesn't exist
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    @staticmethod
    def get_assets_dir() -> Path:
        """
        Get the assets directory path.
        
        Returns:
            Path to assets directory
        """
        # Get the directory containing this file
        current_dir = Path(__file__).parent.parent
        assets_dir = current_dir / 'assets'
        
        # If assets directory doesn't exist, try relative to main script
        if not assets_dir.exists():
            # Try to find the main script directory
            main_script = Path(sys.argv[0]).parent
            assets_dir = main_script / 'assets'
        
        return assets_dir
    
    @staticmethod
    def get_log_dir() -> Path:
        """
        Get the platform-specific log directory.
        
        Returns:
            Path to log directory
        """
        platform_type = PlatformUtils.get_platform()
        
        if platform_type == PlatformType.WINDOWS:
            # Windows: %APPDATA%\\Whiz\\logs
            log_dir = PlatformUtils.get_config_dir() / 'logs'
        elif platform_type == PlatformType.MACOS:
            # macOS: ~/Library/Logs/Whiz
            log_dir = Path.home() / 'Library' / 'Logs' / 'Whiz'
        elif platform_type == PlatformType.LINUX:
            # Linux: ~/.local/share/Whiz/logs
            log_dir = Path.home() / '.local' / 'share' / 'Whiz' / 'logs'
        else:
            # Fallback: config directory
            log_dir = PlatformUtils.get_config_dir() / 'logs'
        
        # Create directory if it doesn't exist
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    @staticmethod
    def get_executable_path() -> Optional[Path]:
        """
        Get the path to the current executable.
        
        Returns:
            Path to executable, or None if not available
        """
        if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
            # PyInstaller bundle
            return Path(sys.executable)
        else:
            # Running from source
            return Path(sys.argv[0])
    
    @staticmethod
    def get_resource_path(relative_path: str) -> Path:
        """
        Get the path to a resource file.
        
        Args:
            relative_path: Relative path to resource
            
        Returns:
            Absolute path to resource
        """
        if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
            # PyInstaller bundle
            base_path = Path(sys._MEIPASS)
        else:
            # Running from source
            base_path = Path(__file__).parent.parent
        
        return base_path / relative_path
    
    @staticmethod
    def get_user_documents_dir() -> Path:
        """
        Get the platform-specific user documents directory.
        
        Returns:
            Path to user documents directory
        """
        platform_type = PlatformUtils.get_platform()
        
        if platform_type == PlatformType.WINDOWS:
            # Windows: %USERPROFILE%\\Documents
            docs_dir = Path(os.environ.get('USERPROFILE', '')) / 'Documents'
        elif platform_type == PlatformType.MACOS:
            # macOS: ~/Documents
            docs_dir = Path.home() / 'Documents'
        elif platform_type == PlatformType.LINUX:
            # Linux: ~/Documents
            docs_dir = Path.home() / 'Documents'
        else:
            # Fallback: home directory
            docs_dir = Path.home()
        
        return docs_dir
    
    @staticmethod
    def get_desktop_dir() -> Path:
        """
        Get the platform-specific desktop directory.
        
        Returns:
            Path to desktop directory
        """
        platform_type = PlatformUtils.get_platform()
        
        if platform_type == PlatformType.WINDOWS:
            # Windows: %USERPROFILE%\\Desktop
            desktop_dir = Path(os.environ.get('USERPROFILE', '')) / 'Desktop'
        elif platform_type == PlatformType.MACOS:
            # macOS: ~/Desktop
            desktop_dir = Path.home() / 'Desktop'
        elif platform_type == PlatformType.LINUX:
            # Linux: ~/Desktop
            desktop_dir = Path.home() / 'Desktop'
        else:
            # Fallback: home directory
            desktop_dir = Path.home()
        
        return desktop_dir
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize a path for the current platform.
        
        Args:
            path: Path to normalize
            
        Returns:
            Normalized path string
        """
        return str(Path(path).resolve())
    
    @staticmethod
    def get_path_separator() -> str:
        """
        Get the path separator for the current platform.
        
        Returns:
            Path separator character
        """
        return os.sep
    
    @staticmethod
    def is_admin() -> bool:
        """
        Check if the current process is running with administrator/root privileges.
        
        Returns:
            True if running with elevated privileges, False otherwise
        """
        platform_type = PlatformUtils.get_platform()
        
        if platform_type == PlatformType.WINDOWS:
            try:
                import ctypes
                return bool(ctypes.windll.shell32.IsUserAnAdmin())
            except:
                return False
        elif platform_type == PlatformType.LINUX:
            return os.geteuid() == 0
        elif platform_type == PlatformType.MACOS:
            return os.geteuid() == 0
        else:
            return False
    
    @staticmethod
    def get_system_language() -> str:
        """
        Get the system language code.
        
        Returns:
            Language code (e.g., 'en', 'de', 'fr')
        """
        platform_type = PlatformUtils.get_platform()
        
        if platform_type == PlatformType.WINDOWS:
            try:
                import locale
                lang, _ = locale.getdefaultlocale()
                if lang:
                    return lang.split('_')[0]
            except:
                pass
        elif platform_type == PlatformType.MACOS:
            try:
                import locale
                lang, _ = locale.getdefaultlocale()
                if lang:
                    return lang.split('_')[0]
            except:
                pass
        elif platform_type == PlatformType.LINUX:
            try:
                lang = os.environ.get('LANG', '')
                if lang:
                    return lang.split('_')[0]
            except:
                pass
        
        return 'en'  # Default to English
    
    @staticmethod
    def get_display_info() -> Dict[str, Any]:
        """
        Get display information for the current platform.
        
        Returns:
            Dictionary with display information
        """
        info = {
            "platform": PlatformUtils.get_platform(),
            "dpi_aware": False,
            "high_dpi": False
        }
        
        try:
            if PlatformUtils.is_windows():
                # Windows DPI awareness
                try:
                    import ctypes
                    from ctypes import wintypes
                    
                    # Check DPI awareness
                    awareness = ctypes.c_int()
                    ctypes.windll.shcore.GetProcessDpiAwareness(
                        ctypes.windll.kernel32.GetCurrentProcess(),
                        ctypes.byref(awareness)
                    )
                    info["dpi_aware"] = awareness.value != 0
                    info["high_dpi"] = awareness.value >= 2
                except:
                    pass
            
            # Get screen resolution (basic)
            try:
                if PlatformUtils.is_windows():
                    import ctypes
                    user32 = ctypes.windll.user32
                    info["screen_width"] = user32.GetSystemMetrics(0)
                    info["screen_height"] = user32.GetSystemMetrics(1)
                else:
                    # Linux/macOS - would need additional libraries for accurate detection
                    info["screen_width"] = 1920  # Default
                    info["screen_height"] = 1080  # Default
            except:
                info["screen_width"] = 1920
                info["screen_height"] = 1080
        
        except Exception as e:
            logger.warning(f"Error getting display info: {e}")
        
        return info
