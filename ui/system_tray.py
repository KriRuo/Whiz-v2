"""
System tray icon implementation for Whiz Voice-to-Text application.
Provides cross-platform system tray functionality with context menu and window control.
"""

import os
import sys
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap

from core.platform_utils import PlatformUtils


class SystemTrayIcon(QSystemTrayIcon):
    """
    System tray icon for Whiz application.
    
    Provides a system tray icon with context menu for:
    - Show/Hide main window
    - Quit application
    
    Works on Windows, Linux, and macOS platforms where system tray is available.
    """
    
    # Signals emitted by the tray icon
    show_window = pyqtSignal()
    hide_window = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self, parent=None, icon_path=None):
        """
        Initialize the system tray icon.
        
        Args:
            parent: Parent widget
            icon_path: Path to icon file (defaults to app icon)
        """
        super().__init__(parent)
        
        # Check if system tray is available on this platform
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        # Set up icon
        if icon_path is None:
            icon_path_obj = PlatformUtils.get_resource_path("assets/images/icons/app_icon_transparent.ico")
            icon_path = str(icon_path_obj)

        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            # Fallback to a simple icon if file not found
            pixmap = QPixmap(16, 16)
            pixmap.fill()
            self.setIcon(QIcon(pixmap))
        
        # Set tooltip
        self.setToolTip("Whiz Voice-to-Text")
        
        # Create context menu
        self.create_context_menu()
        
        # Connect signals
        self.activated.connect(self.on_tray_activated)
        
        # Show the tray icon
        self.show()
    
    def create_context_menu(self):
        """Create the right-click context menu for the tray icon."""
        self.context_menu = QMenu()
        
        # Show/Hide action
        self.show_hide_action = QAction("Show Window", self)
        self.show_hide_action.triggered.connect(self.toggle_window_visibility)
        self.context_menu.addAction(self.show_hide_action)
        
        # Separator
        self.context_menu.addSeparator()
        
        # Settings action
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.settings_requested.emit)
        self.context_menu.addAction(self.settings_action)
        
        # Separator
        self.context_menu.addSeparator()
        
        # Quit action
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.quit_requested.emit)
        self.context_menu.addAction(self.quit_action)
        
        # Set the context menu
        self.setContextMenu(self.context_menu)
    
    def on_tray_activated(self, reason):
        """
        Handle tray icon activation (click).
        
        Args:
            reason: Activation reason (QSystemTrayIcon.ActivationReason)
        """
        if reason == QSystemTrayIcon.DoubleClick:
            # Double-click shows/hides the window
            self.toggle_window_visibility()
        elif reason == QSystemTrayIcon.Trigger:
            # Single click also shows/hides the window
            self.toggle_window_visibility()
    
    def toggle_window_visibility(self):
        """Toggle main window visibility."""
        # Emit signal to let parent handle the actual show/hide logic
        self.show_window.emit()
    
    def update_show_hide_text(self, is_visible):
        """
        Update the Show/Hide menu text based on window visibility.
        
        Args:
            is_visible: Whether the main window is currently visible
        """
        if hasattr(self, 'show_hide_action'):
            if is_visible:
                self.show_hide_action.setText("Hide Window")
            else:
                self.show_hide_action.setText("Show Window")
    
    def show_message(self, title, message, icon=QSystemTrayIcon.Information, timeout=3000):
        """
        Show a balloon message from the tray icon.
        
        Args:
            title: Message title
            message: Message text
            icon: Message icon type
            timeout: Display timeout in milliseconds
        """
        # System tray messages work on all platforms where tray is available
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.showMessage(title, message, icon, timeout)
    
    def cleanup(self):
        """Clean up the tray icon."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.hide()
            self.deleteLater()
