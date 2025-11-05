"""
Icon management module for Whiz application.
Handles Windows-specific icon setting and provides centralized icon management.
"""

import os
import sys
from PyQt5.QtGui import QIcon
from core.platform_utils import PlatformUtils


class _IconPathDescriptor:
    """Descriptor for lazy-loading icon path"""
    def __get__(self, obj, cls):
        if cls._icon_path is None:
            icon_path_obj = PlatformUtils.get_resource_path("assets/images/icons/app_icon_transparent.ico")
            cls._icon_path = str(icon_path_obj)
        return cls._icon_path


class IconManager:
    """Manages application icons across different contexts"""
    
    _icon_path = None
    ICON_PATH = _IconPathDescriptor()
    
    @staticmethod
    def _get_icon_path() -> str:
        """Get the icon path using PlatformUtils for proper resource resolution."""
        return IconManager.ICON_PATH
    
    @staticmethod
    def set_windows_icon(icon_path: str) -> bool:
        """Set the application icon at Windows process level"""
        if sys.platform != "win32":
            return False
            
        try:
            import ctypes
            
            # Get absolute path to icon
            abs_icon_path = os.path.abspath(icon_path)
            
            if not os.path.exists(abs_icon_path):
                return False
            
            # Load Windows libraries
            user32 = ctypes.windll.user32
            
            # Load icon from file (returns HICON)
            LR_LOADFROMFILE = 0x00000010
            IMAGE_ICON = 1
            
            hicon = user32.LoadImageW(
                None,
                abs_icon_path,
                IMAGE_ICON,
                0, 0,  # Use default size
                LR_LOADFROMFILE
            )
            
            if not hicon:
                return False
            
            return True
            
        except Exception as e:
            print(f"Failed to set Windows icon: {e}")
            return False
    
    @staticmethod
    def get_app_icon() -> QIcon:
        """Get the application icon"""
        icon_path = IconManager._get_icon_path()
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            return QIcon()
