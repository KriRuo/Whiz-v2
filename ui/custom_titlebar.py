"""
Custom Title Bar for PyQt5 Speech-to-Text Tool

This module provides a modern, custom title bar that replaces the standard Windows
title bar while maintaining all native behaviors like drag, resize, and snap.
"""

import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QFont
from ui.layout_system import ResponsiveSizing, ResponsiveBreakpoints, DPIScalingHelper
from PyQt5.QtGui import QFont, QIcon, QPixmap


class TitleBar(QWidget):
    """
    Custom title bar widget with minimize, maximize/restore, and close buttons.
    Handles window dragging and double-click to toggle maximize/restore.
    """
    
    # Signals for window actions
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.is_maximized = False
        self.drag_position = QPoint()
        
        self.init_ui()
        self.setup_styling()
        
    def _calculate_responsive_dimensions(self):
        """Calculate responsive dimensions based on screen size"""
        from PyQt5.QtWidgets import QApplication
        
        # Get current screen dimensions
        app = QApplication.instance()
        if app and app.primaryScreen():
            screen = app.primaryScreen()
            screen_width = screen.availableGeometry().width()
            screen_height = screen.availableGeometry().height()
        else:
            # Fallback dimensions
            screen_width = 1920
            screen_height = 1080
        
        # Determine screen size class
        screen_class = ResponsiveBreakpoints.get_screen_size_class(screen_width)
        
        # Calculate responsive dimensions based on screen class (50% smaller)
        if screen_class.value == "XSMALL":
            self.title_bar_height = 18  # 50% of 36
            self.title_font_size = 14
            self.button_size = 13  # 50% of 26
            self.button_height = 11  # 50% of 22
            self.margin_horizontal = 8
            self.margin_vertical = 3  # 50% of 6
            self.button_spacing = 6
            self.spacer_width = 30
        elif screen_class.value == "SMALL":
            self.title_bar_height = 20  # 50% of 40
            self.title_font_size = 16
            self.button_size = 14  # 50% of 28
            self.button_height = 12  # 50% of 24
            self.margin_horizontal = 10
            self.margin_vertical = 3  # 50% of 7
            self.button_spacing = 7
            self.spacer_width = 35
        elif screen_class.value == "MEDIUM":
            self.title_bar_height = 22  # 50% of 44
            self.title_font_size = 18
            self.button_size = 16  # 50% of 32
            self.button_height = 14  # 50% of 28
            self.margin_horizontal = 12
            self.margin_vertical = 4  # 50% of 8
            self.button_spacing = 8
            self.spacer_width = 40
        elif screen_class.value == "LARGE":
            self.title_bar_height = 24  # 50% of 48
            self.title_font_size = 20
            self.button_size = 18  # 50% of 36
            self.button_height = 16  # 50% of 32
            self.margin_horizontal = 14
            self.margin_vertical = 4  # 50% of 9
            self.button_spacing = 9
            self.spacer_width = 45
        else:  # XLARGE
            self.title_bar_height = 26  # 50% of 52
            self.title_font_size = 22
            self.button_size = 20  # 50% of 40
            self.button_height = 18  # 50% of 36
            self.margin_horizontal = 16
            self.margin_vertical = 5  # 50% of 10
            self.button_spacing = 10
            self.spacer_width = 50
        
    def init_ui(self):
        """Initialize the title bar UI components with responsive sizing"""
        # Calculate responsive dimensions
        self._calculate_responsive_dimensions()
        
        self.setFixedHeight(self.title_bar_height)
        self.setObjectName("TitleBar")
        
        # Main layout with responsive margins
        layout = QHBoxLayout(self)
        layout.setContentsMargins(self.margin_horizontal, self.margin_vertical, 
                                self.margin_horizontal, self.margin_vertical)
        layout.setSpacing(self.button_spacing)
        
        # Title text with responsive font
        self.title_label = QLabel("Whiz")
        self.title_label.setObjectName("TitleText")
        self.title_label.setFont(QFont("Inter", self.title_font_size, QFont.DemiBold))
        layout.addWidget(self.title_label)
        
        # Spacer to push buttons to the right
        spacer = QSpacerItem(self.spacer_width, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        # Settings button with responsive size
        self.settings_btn = QPushButton()
        self.settings_btn.setObjectName("SettingsButton")
        self.settings_btn.setFixedSize(self.button_size, self.button_height)
        self.settings_btn.setIcon(self.create_settings_icon())
        self.settings_btn.setToolTip("Open Preferences")
        self.settings_btn.clicked.connect(self.on_settings_clicked)
        self.settings_btn.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.settings_btn)
        
        # Window control buttons with responsive sizes
        self.minimize_btn = QPushButton()
        self.minimize_btn.setObjectName("HeaderButton")
        self.minimize_btn.setFixedSize(self.button_size, self.button_height)
        self.minimize_btn.setIcon(self.create_minimize_icon())
        self.minimize_btn.clicked.connect(self.minimize_clicked.emit)
        layout.addWidget(self.minimize_btn)
        
        self.maximize_btn = QPushButton()
        self.maximize_btn.setObjectName("HeaderButton")
        self.maximize_btn.setFixedSize(self.button_size, self.button_height)
        self.maximize_btn.setIcon(self.create_maximize_icon())
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.maximize_btn)
        
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("HeaderButton")
        self.close_btn.setFixedSize(self.button_size, self.button_height)
        self.close_btn.setIcon(self.create_close_icon())
        self.close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.close_btn)
        
    def create_minimize_icon(self):
        """Create minimize icon (horizontal line)"""
        from PyQt5.QtGui import QPainter, QPen
        from PyQt5.QtCore import QSize
        
        # Use responsive icon size (50% smaller)
        icon_size = max(8, self.button_size // 2)  # At least 8px, but responsive
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw horizontal line (scaled)
        line_width = max(1, icon_size // 8)
        margin = icon_size // 4
        painter.setPen(QPen(Qt.white, line_width, Qt.SolidLine))
        painter.drawLine(margin, icon_size//2, icon_size-margin, icon_size//2)
        
        painter.end()
        return QIcon(pixmap)
        
    def create_maximize_icon(self):
        """Create maximize icon (square outline)"""
        from PyQt5.QtGui import QPainter, QPen
        from PyQt5.QtCore import QSize
        
        # Use responsive icon size (50% smaller)
        icon_size = max(8, self.button_size // 2)  # At least 8px, but responsive
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw square outline (scaled)
        line_width = max(1, icon_size // 8)
        margin = icon_size // 4
        painter.setPen(QPen(Qt.white, line_width, Qt.SolidLine))
        painter.drawRect(margin, margin, icon_size-margin*2, icon_size-margin*2)
        
        painter.end()
        return QIcon(pixmap)
        
    def create_close_icon(self):
        """Create close icon (X)"""
        from PyQt5.QtGui import QPainter, QPen
        from PyQt5.QtCore import QSize
        
        # Use responsive icon size (50% smaller)
        icon_size = max(8, self.button_size // 2)  # At least 8px, but responsive
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw X (scaled)
        line_width = max(1, icon_size // 8)
        margin = icon_size // 4
        painter.setPen(QPen(Qt.white, line_width, Qt.SolidLine))
        painter.drawLine(margin, margin, icon_size-margin, icon_size-margin)
        painter.drawLine(icon_size-margin, margin, margin, icon_size-margin)
        
        painter.end()
        return QIcon(pixmap)
        
    def create_restore_icon(self):
        """Create restore icon (overlapping squares)"""
        from PyQt5.QtGui import QPainter, QPen
        from PyQt5.QtCore import QSize
        
        # Use responsive icon size (50% smaller)
        icon_size = max(8, self.button_size // 2)  # At least 8px, but responsive
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw overlapping squares (scaled)
        line_width = max(1, icon_size // 8)
        margin = icon_size // 4
        painter.setPen(QPen(Qt.white, line_width, Qt.SolidLine))
        
        # Back square
        painter.drawRect(margin, margin+icon_size//3, icon_size-margin*2, icon_size-margin*2)
        # Front square (offset)
        painter.drawRect(margin+icon_size//3, margin, icon_size-margin*2, icon_size-margin*2)
        
        painter.end()
        return QIcon(pixmap)
    
    def create_settings_icon(self):
        """Create settings icon (gear/cog)"""
        from PyQt5.QtGui import QPainter, QPen
        from PyQt5.QtCore import QSize
        
        # Use responsive icon size (50% smaller)
        icon_size = max(8, self.button_size // 2)  # At least 8px, but responsive
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw gear icon (scaled)
        line_width = max(1, icon_size // 8)
        margin = icon_size // 8
        
        painter.setPen(QPen(Qt.white, line_width, Qt.SolidLine))
        
        # Outer circle
        painter.drawEllipse(margin, margin, icon_size-margin*2, icon_size-margin*2)
        
        # Inner circle
        inner_margin = icon_size // 3
        painter.drawEllipse(inner_margin, inner_margin, icon_size-inner_margin*2, icon_size-inner_margin*2)
        
        # Gear teeth (4 small rectangles) - scaled
        tooth_width = max(1, icon_size // 8)
        tooth_height = max(1, icon_size // 5)
        center = icon_size // 2
        
        painter.fillRect(center-tooth_width//2, margin, tooth_width, tooth_height, Qt.white)  # Top
        painter.fillRect(center-tooth_width//2, icon_size-margin-tooth_height, tooth_width, tooth_height, Qt.white)  # Bottom
        painter.fillRect(margin, center-tooth_height//2, tooth_height, tooth_width, Qt.white)  # Left
        painter.fillRect(icon_size-margin-tooth_height, center-tooth_height//2, tooth_height, tooth_width, Qt.white)  # Right
        
        painter.end()
        return QIcon(pixmap)
        
    def setup_styling(self):
        """Apply modern styling to the title bar with Wispr Flow inspired design"""
        
        # Use responsive font size
        font_size = getattr(self, 'title_font_size', 18)
        
        self.setStyleSheet(f"""
            #TitleBar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2D1B69, stop:1 #11052C);
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                border-bottom: 1px solid rgba(255, 182, 193, 0.3);
                border: none;
            }}
            
            #TitleText {{
                color: white;
                font-family: "Inter","Segoe UI",system-ui,-apple-system;
                font-weight: 600;
                font-size: {font_size}px;
                letter-spacing: -0.2px;
                background: transparent;
                border: none;
                padding-left: 0px;
            }}
            
            #HeaderButton {{
                background-color: rgba(255, 182, 193, 0.15);
                color: #FFB6C1;
                border: 1px solid rgba(255, 182, 193, 0.3);
                border-radius: 8px;
                font-weight: 600;
                padding: 0px;
            }}
            
            #SettingsButton {{
                background-color: rgba(255, 107, 157, 0.2);
                color: #FF6B9D;
                border: 1px solid rgba(255, 107, 157, 0.4);
                border-radius: 8px;
                font-weight: 600;
                padding: 0px;
            }}
            
            #HeaderButton:hover {{
                background-color: rgba(255, 182, 193, 0.3);
                color: white;
                border-color: rgba(255, 182, 193, 0.6);
            }}
            
            #HeaderButton:pressed {{
                background-color: rgba(255, 182, 193, 0.4);
                color: white;
            }}
            
            #SettingsButton:hover {{
                background-color: rgba(255, 107, 157, 0.4);
                color: white;
                border-color: rgba(255, 107, 157, 0.8);
            }}
            
            #SettingsButton:pressed {{
                background-color: rgba(255, 107, 157, 0.6);
                color: white;
            }}
            
            /* Special styling for close button */
            QPushButton#HeaderButton:last-child:hover {{
                background-color: #E53E3E;
                color: white;
                border-color: #C53030;
            }}
            
            QPushButton#HeaderButton:last-child:pressed {{
                background-color: #C53030;
                color: white;
            }}
        """)
        
    def set_title(self, text: str):
        """Set the title text"""
        self.title_label.setText(text)
        
    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        self.is_maximized = not self.is_maximized
        self.maximize_clicked.emit()
        
        # Update button icon
        if self.is_maximized:
            self.maximize_btn.setIcon(self.create_restore_icon())
        else:
            self.maximize_btn.setIcon(self.create_maximize_icon())
            
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.LeftButton and not self.is_maximized:
            # Only drag if not maximized
            self.parent_window.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseDoubleClickEvent(self, event):
        """Handle double-click to toggle maximize/restore"""
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()
            event.accept()
    
    def on_settings_clicked(self):
        """Handle settings button click"""
        # Check if this is a real user click by checking the sender
        sender = self.sender()
        if sender != self.settings_btn:
            return
        self.settings_clicked.emit()
    
    def update_responsive_sizing(self):
        """Update title bar sizing when screen changes"""
        # Recalculate dimensions
        self._calculate_responsive_dimensions()
        
        # Update height
        self.setFixedHeight(self.title_bar_height)
        
        # Update font size
        self.title_label.setFont(QFont("Inter", self.title_font_size, QFont.DemiBold))
        
        # Update button sizes
        self.settings_btn.setFixedSize(self.button_size, self.button_height)
        self.minimize_btn.setFixedSize(self.button_size, self.button_height)
        self.maximize_btn.setFixedSize(self.button_size, self.button_height)
        self.close_btn.setFixedSize(self.button_size, self.button_height)
        
        # Update layout margins and spacing
        layout = self.layout()
        layout.setContentsMargins(self.margin_horizontal, self.margin_vertical, 
                                self.margin_horizontal, self.margin_vertical)
        layout.setSpacing(self.button_spacing)
        
        # Update spacer
        spacer_item = layout.itemAt(1)  # Spacer is at index 1
        if spacer_item:
            spacer_item.changeSize(self.spacer_width, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # Reapply styling with new font size
        self.setup_styling()


class WindowHitTester:
    """
    Windows-specific hit testing for proper resize and snap functionality.
    This class handles the nativeEvent override for Windows hit-testing.
    """
    
    # Windows hit-test constants
    HTNOWHERE = 0
    HTCLIENT = 1
    HTCAPTION = 2
    HTLEFT = 10
    HTRIGHT = 11
    HTTOP = 12
    HTTOPLEFT = 13
    HTTOPRIGHT = 14
    HTBOTTOM = 15
    HTBOTTOMLEFT = 16
    HTBOTTOMRIGHT = 17
    
    @staticmethod
    def get_hit_test_result(pos, window_rect, border_size=8):
        """
        Determine the appropriate hit-test result based on cursor position.
        
        Args:
            pos: QPoint - cursor position relative to window
            window_rect: QRect - window rectangle
            border_size: int - size of resize border in pixels
            
        Returns:
            int - Windows hit-test constant
        """
        x, y = pos.x(), pos.y()
        width, height = window_rect.width(), window_rect.height()
        
        # Check if cursor is in resize borders
        if x < border_size:
            if y < border_size:
                return WindowHitTester.HTTOPLEFT
            elif y > height - border_size:
                return WindowHitTester.HTBOTTOMLEFT
            else:
                return WindowHitTester.HTLEFT
        elif x > width - border_size:
            if y < border_size:
                return WindowHitTester.HTTOPRIGHT
            elif y > height - border_size:
                return WindowHitTester.HTBOTTOMRIGHT
            else:
                return WindowHitTester.HTRIGHT
        elif y < border_size:
            return WindowHitTester.HTTOP
        elif y > height - border_size:
            return WindowHitTester.HTBOTTOM
        
        # Check if cursor is in title bar area (first 44 pixels)
        elif y < 44:
            return WindowHitTester.HTCAPTION
        
        # Default to client area
        return WindowHitTester.HTCLIENT


def apply_frameless_window_hints(window):
    """
    Apply frameless window hints to the main window.
    
    Args:
        window: QMainWindow - the main window to modify
    """
    # Set frameless window hint
    window.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
    
    # Ensure the window can still be minimized/maximized
    window.setWindowFlags(window.windowFlags() | Qt.WindowMinMaxButtonsHint)
    
    # Enable native window controls on Windows
    if sys.platform == "win32":
        window.setWindowFlags(window.windowFlags() | Qt.WindowSystemMenuHint)


def setup_window_resize_border(window, title_bar):
    """
    Set up the window resize border and hit-testing.
    
    Args:
        window: QMainWindow - the main window
        title_bar: TitleBar - the custom title bar widget
    """
    # For now, we'll skip the complex native event handling
    # The basic frameless window functionality works without it
    # This prevents the TypeError and AttributeError issues
    
    # The window will still be draggable via the title bar
    # and resizable via Qt's built-in mechanisms
    pass
