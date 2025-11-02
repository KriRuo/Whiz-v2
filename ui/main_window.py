import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QMessageBox, QDialog, QDesktopWidget, QApplication,
                             QSystemTrayIcon, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QCursor
from PyQt5.QtMultimedia import QSoundEffect

from ui.custom_titlebar import TitleBar, apply_frameless_window_hints, setup_window_resize_border
from ui.styles.main_styles import MainStyles
from ui.preferences_dialog import PreferencesDialog
from ui.layout_system import (LayoutBuilder, LayoutTokens, ResponsiveSizing, 
                             ResponsiveBreakpoints, DPIScalingHelper, ScreenSizeClass, ColorTokens)
from ui.widgets.gradient_tab_widget import GradientTabWidget
from ui.system_tray import SystemTrayIcon
from core.platform_utils import PlatformUtils
from core.logging_config import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main window management class for Whiz application"""
    
    # Define signals for communication with SpeechApp
    preferences_opened = pyqtSignal()
    settings_changed = pyqtSignal(dict)
    window_state_changed = pyqtSignal()
    
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self._preferences_dialog_open = False
        
        # Initialize system tray
        self.system_tray = None
        self.minimize_to_tray_enabled = False
        
        # Initialize responsive properties
        self._current_screen_class = None
        self._current_dpi_factor = None
        self._last_screen_geometry = None
        
        # Set window icon using IconManager
        from ui.icon_manager import IconManager
        self.app_icon = IconManager.get_app_icon()
        self.setWindowIcon(self.app_icon)
        
        # Initialize sound effects
        self.sound_start = QSoundEffect()
        self.sound_start.setSource(QUrl.fromLocalFile("assets/sound_start_v9.wav"))
        self.sound_start.setVolume(0.385)
        
        self.sound_end = QSoundEffect()
        self.sound_end.setSource(QUrl.fromLocalFile("assets/sound_end_v9.wav"))
        self.sound_end.setVolume(0.385)
        
        # Sound effects enabled by default
        self.sound_enabled = True
        
        self.init_window()
    
    def init_window(self):
        """Initialize the main window UI"""
        self.setWindowTitle("Whiz")
        
        # Set responsive window size and position
        self.setup_responsive_geometry()
        
        # Apply platform-specific window setup
        self.use_custom_titlebar = PlatformUtils.is_windows()
        
        if self.use_custom_titlebar:
            # Apply frameless window hints for custom title bar (Windows only)
            apply_frameless_window_hints(self)
            
            # Create custom title bar
            self.title_bar = TitleBar(self)
            self.title_bar.minimize_clicked.connect(self.showMinimized)
            self.title_bar.maximize_clicked.connect(self.toggle_maximize)
            self.title_bar.close_clicked.connect(self.close)
            self.title_bar.settings_clicked.connect(self.open_preferences)
            
            # Set up Windows hit-testing for resize and snap
            setup_window_resize_border(self, self.title_bar)
        else:
            # Use native title bar on Linux/macOS
            self.title_bar = None
        
        # Create central widget and main layout using new layout system
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title bar at the top (Windows only)
        if self.title_bar:
            main_layout.addWidget(self.title_bar)
        
        # Create content container using layout system
        self.content_widget = QWidget()
        self.content_widget.setObjectName("Content")
        self.content_layout = LayoutBuilder.create_main_layout(
            self.content_widget,
            spacing=LayoutTokens.SPACING_LG,
            margins=(LayoutTokens.MARGIN_SM, LayoutTokens.MARGIN_XL, 
                    LayoutTokens.MARGIN_XL, LayoutTokens.MARGIN_SM)  # Reduced top and bottom margins from XL (20) to SM (8)
        )
        
        # Create tab widget
        self.tab_widget = GradientTabWidget()
        self.content_layout.addWidget(self.tab_widget)
        
        # Add content widget to main layout
        main_layout.addWidget(self.content_widget)
        
        # Create footer widget for model information
        self.footer_widget = QWidget()
        self.footer_widget.setObjectName("Footer")
        self.footer_widget.setFixedHeight(25)  # Reduced height from 30px to 25px
        footer_layout = QVBoxLayout(self.footer_widget)
        footer_layout.setContentsMargins(10, 3, 10, 3)  # Reduced top/bottom margins from 5px to 3px
        footer_layout.setSpacing(0)
        
        # Footer label for model information
        self.footer_label = QLabel("")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorTokens.TEXT_TERTIARY};
                font-size: 11px;
                font-family: "Inter","Segoe UI",system-ui,-apple-system;
                font-weight: 400;
                background: transparent;
                border: none;
                padding: 2px;
            }}
        """)
        footer_layout.addWidget(self.footer_label)
        
        # Add footer to main layout
        main_layout.addWidget(self.footer_widget)
        
        # Add settings button for non-Windows platforms
        if not self.use_custom_titlebar:
            self.add_native_settings_button()
        
        # Apply responsive styling
        self.setStyleSheet(MainStyles.get_responsive_stylesheet())
        
        # Ensure tab elision is disabled AFTER stylesheet is applied
        if hasattr(self.tab_widget, 'tabBar'):
            self.tab_widget.tabBar().setElideMode(Qt.ElideNone)
        
        # Initialize system tray if on Windows
        self.init_system_tray()
        
        # Connect screen change detection for multi-monitor setups
        self.connect_screen_change_detection()
    
    def setup_responsive_geometry(self):
        """Set up responsive window geometry based on screen size"""
        # Get the appropriate screen (prefer screen where cursor is located)
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)
        
        # Fallback to primary screen if cursor screen detection fails
        if screen is None:
            screen = QApplication.primaryScreen()
        
        # Fallback to desktop widget if all else fails
        if screen is None:
            desktop = QDesktopWidget()
            screen_geometry = desktop.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
        else:
            # Get available geometry (excludes taskbar/dock)
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
        
        # Store current screen properties for responsive updates
        self._current_screen_class = ResponsiveBreakpoints.get_screen_size_class(screen_width)
        self._current_dpi_factor = DPIScalingHelper.get_device_pixel_ratio()
        self._last_screen_geometry = screen_geometry
        
        # Calculate responsive window dimensions using new system
        window_width, window_height = ResponsiveSizing.calculate_window_size(
            screen_width, screen_height, self._current_screen_class
        )
        
        # Set minimum and maximum sizes using responsive system
        # Note: Qt's automatic DPI scaling handles the scaling, so we use logical pixels directly
        config = ResponsiveSizing.WINDOW_SIZING[self._current_screen_class]
        
        # Use logical pixel values directly (Qt handles DPI scaling automatically)
        min_width = config['min_width']
        min_height = config['min_height']
        max_width = config['max_width']
        max_height = config['max_height']
        
        self.setMinimumSize(min_width, min_height)
        self.setMaximumSize(max_width, max_height)
        
        # Center the window on the appropriate screen
        if screen is not None:
            screen_geometry = screen.availableGeometry()
            x = screen_geometry.x() + (screen_geometry.width() - window_width) // 2
            y = screen_geometry.y() + (screen_geometry.height() - window_height) // 2
        else:
            # Fallback centering
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
        
        # Ensure window stays within screen bounds
        x = max(screen_geometry.x() if screen else 0, x)
        y = max(screen_geometry.y() if screen else 0, y)
        
        self.setGeometry(x, y, window_width, window_height)
    
    def connect_screen_change_detection(self):
        """Connect to screen change signals for multi-monitor support."""
        # Connect to window's screenChanged signal
        if hasattr(self, 'windowHandle') and self.windowHandle():
            self.windowHandle().screenChanged.connect(self.handle_screen_change)
    
    def handle_screen_change(self, screen):
        """Handle window being moved to a different screen."""
        if screen:
            # Get new screen properties
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            # Check if screen properties have changed significantly
            new_screen_class = ResponsiveBreakpoints.get_screen_size_class(screen_width)
            new_dpi_factor = screen.devicePixelRatio()
            
            # Only update if there's a meaningful change
            if (new_screen_class != self._current_screen_class or 
                abs(new_dpi_factor - self._current_dpi_factor) > 0.1):
                
                # Update stored properties
                self._current_screen_class = new_screen_class
                self._current_dpi_factor = new_dpi_factor
                self._last_screen_geometry = screen_geometry
                
                # Recalculate window size for new screen
                self.update_window_for_screen_change(screen_width, screen_height)
    
    def update_window_for_screen_change(self, screen_width: int, screen_height: int):
        """Update window size and constraints when moved to different screen."""
        # Calculate new window dimensions
        window_width, window_height = ResponsiveSizing.calculate_window_size(
            screen_width, screen_height, self._current_screen_class
        )
        
        # Update size constraints
        # Note: Qt's automatic DPI scaling handles the scaling, so we use logical pixels directly
        config = ResponsiveSizing.WINDOW_SIZING[self._current_screen_class]
        
        # Use logical pixel values directly (Qt handles DPI scaling automatically)
        min_width = config['min_width']
        min_height = config['min_height']
        max_width = config['max_width']
        max_height = config['max_height']
        
        self.setMinimumSize(min_width, min_height)
        self.setMaximumSize(max_width, max_height)
        
        # Resize window if current size is outside new constraints
        current_width = self.width()
        current_height = self.height()
        
        if (current_width < min_width or current_width > max_width or
            current_height < min_height or current_height > max_height):
            self.resize(window_width, window_height)
        
        # Emit signal to update child components
        self.window_state_changed.emit()
        
        # Regenerate responsive stylesheet for new screen size
        self.setStyleSheet(MainStyles.get_responsive_stylesheet())
        
        # Update title bar responsive sizing if it exists
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.update_responsive_sizing()
    
    def resizeEvent(self, event):
        """Handle window resize events for responsive layout updates."""
        super().resizeEvent(event)
        
        # Emit signal for child components to update their layouts
        self.window_state_changed.emit()
    
    def add_native_settings_button(self):
        """Add a settings button for non-Windows platforms"""
        from PyQt5.QtWidgets import QPushButton, QHBoxLayout
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QIcon
        
        # Create a horizontal layout for the settings button
        settings_layout = QHBoxLayout()
        settings_layout.setContentsMargins(10, 5, 10, 5)
        
        # Create settings button
        settings_button = QPushButton("⚙️ Settings")
        settings_button.setObjectName("SettingsButton")
        settings_button.clicked.connect(self.open_preferences)
        settings_button.setMaximumWidth(120)
        
        # Add button to layout (right-aligned)
        settings_layout.addStretch()
        settings_layout.addWidget(settings_button)
        
        # Add layout to content widget
        self.content_layout.addLayout(settings_layout)
    
    def update_footer(self, text: str):
        """Update the footer text with model information."""
        self.footer_label.setText(text)
    
    def add_tab(self, widget, name):
        """Add a tab to the tab widget"""
        self.tab_widget.addTab(widget, name)
    
    def connect_tab_changed(self, callback):
        """Connect tab change signal to callback"""
        self.tab_widget.currentChanged.connect(callback)
    
    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.window_state_changed.emit()
    
    def open_preferences(self):
        """Open the preferences dialog"""
        # Prevent multiple dialogs from opening
        if self._preferences_dialog_open:
            return
            
        try:
            self._preferences_dialog_open = True
            self.preferences_opened.emit()
            
            dialog = PreferencesDialog(self.settings_manager, self)
            dialog.settings_changed.connect(self.on_settings_changed)
            
            if dialog.exec_() == QDialog.Accepted:
                # Settings were applied during the dialog interaction
                pass
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open preferences: {e}")
        finally:
            self._preferences_dialog_open = False
    
    def on_settings_changed(self, settings: dict):
        """Handle settings changes from preferences dialog"""
        try:
            # Apply the changed settings immediately
            self.settings_manager.apply_all(self)
            
            # Update sound settings
            if "audio/effects_enabled" in settings:
                self.sound_enabled = settings["audio/effects_enabled"]
            
            if "audio/start_tone" in settings:
                start_tone = settings["audio/start_tone"]
                if os.path.exists(start_tone):
                    self.sound_start.setSource(QUrl.fromLocalFile(start_tone))
            
            if "audio/stop_tone" in settings:
                stop_tone = settings["audio/stop_tone"]
                if os.path.exists(stop_tone):
                    self.sound_end.setSource(QUrl.fromLocalFile(stop_tone))
            
            # Emit signal for SpeechApp to handle other settings
            self.settings_changed.emit(settings)
            
        except Exception as e:
            print(f"Error applying settings changes: {e}")
    
    def apply_theme(self, theme: str):
        """Apply theme to the application"""
        try:
            if theme == "light":
                # Apply light theme (current default)
                pass
            elif theme == "dark":
                # Apply dark theme
                self.setStyleSheet(self.styleSheet() + MainStyles.get_dark_theme_addition())
            else:  # system theme
                # Use system theme (current default)
                pass
                
        except Exception as e:
            print(f"Error applying theme '{theme}': {e}")
    
    def play_start_sound(self):
        """Play start recording sound"""
        if self.sound_enabled and self.sound_start.isLoaded():
            self.sound_start.play()
    
    def play_stop_sound(self):
        """Play stop recording sound"""
        if self.sound_enabled and self.sound_end.isLoaded():
            self.sound_end.play()
    
    def init_system_tray(self):
        """Initialize the system tray icon (Windows only)."""
        if PlatformUtils.is_windows() and QSystemTrayIcon.isSystemTrayAvailable():
            try:
                self.system_tray = SystemTrayIcon(self)
                
                # Connect tray signals
                self.system_tray.show_window.connect(self.show_from_tray)
                self.system_tray.settings_requested.connect(self.show_settings)
                self.system_tray.quit_requested.connect(self.quit_application)
                
                # Update tray menu text based on current window state
                self.system_tray.update_show_hide_text(self.isVisible())
                
                print("System tray initialized successfully")
                
                # Set system tray availability in settings
                self.settings_manager.set("behavior/system_tray_available", True)
                
            except Exception as e:
                print(f"Failed to initialize system tray: {e}")
                self.system_tray = None
                # Set system tray availability to False
                self.settings_manager.set("behavior/system_tray_available", False)
        else:
            print("System tray not available - not on Windows or tray not supported")
            self.system_tray = None
            # Set system tray availability to False
            self.settings_manager.set("behavior/system_tray_available", False)
    
    def set_minimize_to_tray(self, enabled: bool):
        """
        Enable or disable minimize to tray functionality.
        
        Args:
            enabled: Whether to minimize to tray instead of closing
        """
        self.minimize_to_tray_enabled = enabled
        
        # Update tray menu text
        if self.system_tray:
            self.system_tray.update_show_hide_text(self.isVisible())
    
    def show_from_tray(self):
        """Show the window from system tray."""
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Update tray menu text
        if self.system_tray:
            self.system_tray.update_show_hide_text(True)
    
    def show_settings(self):
        """Show the settings dialog from system tray."""
        # First show the window if it's hidden
        if not self.isVisible():
            self.show_from_tray()
        
        # Then open the settings dialog
        # This will be implemented by the SpeechApp class
        if hasattr(self, 'show_preferences_dialog'):
            self.show_preferences_dialog()
    
    def hide_to_tray(self):
        """Hide the window to system tray."""
        self.hide()
        
        # Update tray menu text
        if self.system_tray:
            self.system_tray.update_show_hide_text(False)
    
    def quit_application(self):
        """Quit the application completely."""
        # Save window state before quitting
        try:
            self.settings_manager.save_window(self)
        except Exception as e:
            print(f"Error saving window state during quit: {e}")
        
        # Clean up controller if available (for SpeechApp)
        if hasattr(self, 'controller'):
            self.controller.cleanup()
        
        # Clean up system tray
        if self.system_tray:
            self.system_tray.cleanup()
        
        # Quit the application
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle application close"""
        try:
            print(f"closeEvent called - minimize_to_tray_enabled: {self.minimize_to_tray_enabled}, system_tray: {self.system_tray is not None}")
            
            # Check if minimize to tray is enabled AND system tray is available
            if self.minimize_to_tray_enabled and self.system_tray:
                print("Minimizing to tray...")
                # Hide to tray instead of closing
                self.hide_to_tray()
                event.ignore()  # Don't actually close the window
            else:
                print("Closing application normally...")
                # Normal close behavior
                # Save window geometry and state
                self.settings_manager.save_window(self)
                
                # Clean up system tray
                if self.system_tray:
                    self.system_tray.cleanup()
                
                event.accept()
            
        except Exception as e:
            print(f"Error during window close: {e}")
            event.accept()
