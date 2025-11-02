"""
Icon management module for Whiz application.
Handles Windows-specific icon setting and provides centralized icon management.
"""

import os
import sys
from PyQt5.QtGui import QIcon


class IconManager:
    """Manages application icons across different contexts"""
    
    ICON_PATH = "app_icon_transparent.ico"
    
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
        if os.path.exists(IconManager.ICON_PATH):
            return QIcon(IconManager.ICON_PATH)
        else:
            return QIcon()
