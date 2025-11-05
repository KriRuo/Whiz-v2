"""
Visual Indicator Widget for Whiz Voice-to-Text Application
A floating widget that shows recording status with customizable positioning.
"""

from ui.layout_system import DPIScalingHelper, ResponsiveBreakpoints, ScreenSizeClass
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QCursor
from core.platform_utils import PlatformUtils

class VisualIndicatorWidget(QWidget):
    """A floating widget that shows recording status"""
    
    def __init__(self, position: str = "Top Right"):
        super().__init__()
        self.position = position
        self.init_ui()
        self.position_widget()
        
    def init_ui(self):
        """Initialize the visual indicator UI"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Calculate responsive size based on screen class and DPI
        self._update_responsive_size()
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the indicator circle with responsive sizing
        self.indicator_label = QLabel()
        self.indicator_label.setAlignment(Qt.AlignCenter)
        
        # Load the Icon_Listening.png image with responsive scaling
        self._load_responsive_icon()
            
        layout.addWidget(self.indicator_label)
        # Add size policy for better layout behavior
        self.indicator_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def _update_responsive_size(self):
        """Update widget size based on screen class and DPI."""
        # Check if QApplication is available and initialized
        app = QApplication.instance()
        if app is None:
            # Fallback to fixed size if app not ready
            self.setMinimumSize(80, 80)
            self.setMaximumSize(120, 120)
            self.resize(80, 80)
            return
        
        try:
            screen_class = ResponsiveBreakpoints.get_current_screen_size_class()
            dpi_factor = DPIScalingHelper.get_device_pixel_ratio()
            
            # Calculate responsive base size
            size_multipliers = {
                ScreenSizeClass.XSMALL: 0.6,   # Smaller on small screens
                ScreenSizeClass.SMALL: 0.7,    # Slightly smaller
                ScreenSizeClass.MEDIUM: 1.0,   # Base size
                ScreenSizeClass.LARGE: 1.1,    # Slightly larger
                ScreenSizeClass.XLARGE: 1.2    # Larger on big screens
            }
            
            base_size = 80  # Base size for calculations
            multiplier = size_multipliers[screen_class]
            responsive_size = int(base_size * multiplier)
            
            # Apply DPI scaling
            final_size = DPIScalingHelper.scale_pixel_value(responsive_size, dpi_factor)
            
            # Set the size
            self.setMinimumSize(final_size, final_size)
            self.setMaximumSize(int(final_size * 1.5), int(final_size * 1.5))
            self.resize(final_size, final_size)
        except Exception:
            # Fallback to fixed size if any error occurs
            self.setMinimumSize(80, 80)
            self.setMaximumSize(120, 120)
            self.resize(80, 80)
    
    def _load_responsive_icon(self):
        """Load icon with responsive scaling."""
        try:
            icon_path_obj = PlatformUtils.get_resource_path("assets/images/Icon_Listening.png")
            icon_path = str(icon_path_obj)
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                # Calculate responsive icon size
                current_size = min(self.width(), self.height())
                icon_size = int(current_size * 0.75)  # 75% of widget size
                
                # Scale the image while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.indicator_label.setPixmap(scaled_pixmap)
            else:
                # Fallback to styled background if image fails to load
                self._set_fallback_style()
        except Exception as e:
            # Fallback to styled background if image loading fails
            print(f"Failed to load Icon_Listening.png: {e}")
            self._set_fallback_style()
    
    def _set_fallback_style(self):
        """Set fallback styled background."""
        current_size = min(self.width(), self.height())
        border_radius = current_size // 2
        border_width = max(2, int(current_size * 0.04))  # 4% of size
        
        self.indicator_label.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(244, 67, 54, 0.9);
                border-radius: {border_radius}px;
                color: white;
                border: {border_width}px solid rgba(255, 255, 255, 0.8);
            }}
        """)
        
    def position_widget(self):
        """Position the widget based on the specified position"""
        # Dynamically detect the correct screen at runtime
        # First try to get the screen under the mouse cursor
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)
        
        # If screenAt returns None, fallback to primary screen
        if screen is None:
            screen = QApplication.primaryScreen()
        
        # If both fail, use a safe fallback location
        if screen is None:
            x, y = 100, 100
            self.move(x, y)
            return
        
        # Get the screen's geometry
        screen_geometry = screen.geometry()
        x, y = 0, 0
        
        # Get current widget dimensions
        widget_width = self.width()
        widget_height = self.height()
        
        if self.position == "Top Left":
            x, y = screen_geometry.x() + 20, screen_geometry.y() + 20
        elif self.position == "Top Right":
            x, y = screen_geometry.x() + screen_geometry.width() - widget_width - 20, screen_geometry.y() + 20
        elif self.position == "Bottom Right":
            x, y = screen_geometry.x() + screen_geometry.width() - widget_width - 20, screen_geometry.y() + screen_geometry.height() - widget_height - 20
        elif self.position == "Bottom Left":
            x, y = screen_geometry.x() + 20, screen_geometry.y() + screen_geometry.height() - widget_height - 20
        elif self.position == "Top Center":
            x, y = screen_geometry.x() + (screen_geometry.width() - widget_width) // 2, screen_geometry.y() + 20
        elif self.position == "Middle Center":
            x, y = screen_geometry.x() + (screen_geometry.width() - widget_width) // 2, screen_geometry.y() + (screen_geometry.height() - widget_height) // 2
        elif self.position == "Bottom Center":
            x, y = screen_geometry.x() + (screen_geometry.width() - widget_width) // 2, screen_geometry.y() + screen_geometry.height() - widget_height - 20
        
        self.move(x, y)
        
    def show_recording(self):
        """Show the recording indicator"""
        # Reposition the widget before showing to ensure it appears on the correct screen
        self.position_widget()
        self.show()
        self.raise_()
        # Don't call activateWindow() to avoid stealing focus from main window
        
    def hide_recording(self):
        """Hide the recording indicator"""
        self.hide()
        
    def update_position(self, new_position: str):
        """Update the position setting and reposition the widget"""
        self.position = new_position
        self.position_widget()
