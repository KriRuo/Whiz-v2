"""
Base UI Components for Whiz Voice-to-Text Application
Reusable components with consistent styling and behavior.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QDialog, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from ui.layout_system import LayoutBuilder, LayoutTokens, ColorTokens


class BaseTab(QWidget):
    """Base class for all tabs with consistent layout and styling."""
    
    def __init__(self, parent_app=None):
        super().__init__()
        self.parent_app = parent_app
        self.init_base_layout()
        self.init_content()
    
    def init_base_layout(self):
        """Initialize the base layout structure."""
        self.main_layout = LayoutBuilder.create_main_layout(
            self, 
            spacing=LayoutTokens.SPACING_MD,
            margins=(LayoutTokens.MARGIN_MD, LayoutTokens.MARGIN_MD, 
                    LayoutTokens.MARGIN_MD, LayoutTokens.MARGIN_MD)
        )
    
    def init_content(self):
        """Override in subclasses to add specific content."""
        pass


class BaseDialog(QDialog):
    """Base class for dialogs with consistent layout and styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_base_layout()
        self.init_content()
    
    def init_base_layout(self):
        """Initialize the base layout structure."""
        self.main_layout = LayoutBuilder.create_main_layout(
            self,
            spacing=LayoutTokens.SPACING_LG,
            margins=(LayoutTokens.MARGIN_XL, LayoutTokens.MARGIN_XL,
                    LayoutTokens.MARGIN_XL, LayoutTokens.MARGIN_XL)
        )
    
    def init_content(self):
        """Override in subclasses to add specific content."""
        pass


class StatusDisplay(QWidget):
    """Consistent status display component."""
    
    def __init__(self, initial_text: str = "Idle"):
        super().__init__()
        self.init_ui(initial_text)
    
    def init_ui(self, initial_text: str):
        """Initialize the status display UI."""
        layout = LayoutBuilder.create_horizontal_layout()
        
        self.status_label = QLabel(initial_text)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Inter", LayoutTokens.FONT_LG, QFont.Bold))
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorTokens.TEXT_PRIMARY};
                font-weight: 600;
                font-size: 15px;
                padding: 8px;
                background-color: {ColorTokens.BG_SECONDARY};
                border-radius: 8px;
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
            }}
        """)
        
        layout.addWidget(self.status_label)
        self.setLayout(layout)
    
    def update_status(self, text: str):
        """Update the status text."""
        self.status_label.setText(text)


class ActionButton(QPushButton):
    """Consistent action button component with dark theme variants."""
    
    def __init__(self, text: str, button_type: str = "primary"):
        super().__init__(text)
        self.button_type = button_type
        self.init_styling()
        
        # Force smaller button size
        self.setMaximumHeight(35)  # Reduced from default ~44px
        self.setMinimumHeight(30)  # Reduced from default ~44px
    
    def init_styling(self):
        """Apply consistent styling based on button type."""
        if self.button_type == "primary":
            # Cyan start button with subtle glowing border
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(45, 49, 57, 0.9), stop:0.3 rgba(35, 39, 47, 0.95), 
                        stop:0.7 rgba(29, 33, 41, 1.0), stop:1 rgba(25, 29, 37, 1.0));
                    color: {ColorTokens.TEXT_PRIMARY};
                    border: 1px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 212, 255, 0.4), stop:0.3 rgba(0, 232, 255, 0.5), 
                        stop:0.7 rgba(0, 212, 255, 0.5), stop:1 rgba(0, 192, 235, 0.4));
                    padding: 8px 16px !important;
                    border-radius: 12px;
                    font-weight: 500;
                    font-size: 16px;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(55, 59, 67, 0.9), stop:0.3 rgba(45, 49, 57, 0.95), 
                        stop:0.7 rgba(35, 39, 47, 1.0), stop:1 rgba(29, 33, 41, 1.0));
                    border: 1px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 232, 255, 0.6), stop:0.3 rgba(0, 252, 255, 0.7), 
                        stop:0.7 rgba(0, 232, 255, 0.7), stop:1 rgba(0, 212, 255, 0.6));
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(0, 180, 230, 0.9), stop:0.3 rgba(0, 160, 210, 0.95), 
                        stop:0.7 rgba(0, 140, 190, 1.0), stop:1 rgba(0, 120, 170, 1.0));
                    color: {ColorTokens.BG_PRIMARY};
                    border-color: rgba(0, 212, 255, 0.8);
                }}
            """)
        elif self.button_type == "secondary":
            # Dark gray stop button with subtle styling
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(60, 66, 72, 0.9), stop:0.3 rgba(50, 56, 62, 0.95), 
                        stop:0.7 rgba(40, 46, 52, 1.0), stop:1 rgba(30, 36, 42, 1.0));
                    color: {ColorTokens.TEXT_SECONDARY};
                    border: 1px solid rgba(40, 46, 52, 0.8);
                    padding: 8px 16px !important;
                    border-radius: 12px;
                    font-weight: 500;
                    font-size: 16px;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(70, 76, 82, 0.9), stop:0.3 rgba(60, 66, 72, 0.95), 
                        stop:0.7 rgba(50, 56, 62, 1.0), stop:1 rgba(40, 46, 52, 1.0));
                    border-color: rgba(50, 56, 62, 0.9);
                    color: {ColorTokens.TEXT_PRIMARY};
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(30, 36, 42, 1.0), stop:0.3 rgba(25, 31, 37, 1.0), 
                        stop:0.7 rgba(20, 26, 32, 1.0), stop:1 rgba(15, 21, 27, 1.0));
                    color: {ColorTokens.TEXT_SECONDARY};
                }}
                QPushButton:disabled {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(30, 36, 42, 0.6), stop:0.3 rgba(25, 31, 37, 0.7), 
                        stop:0.7 rgba(20, 26, 32, 0.8), stop:1 rgba(15, 21, 27, 0.9));
                    color: rgba(155, 163, 175, 0.5);
                    border-color: rgba(30, 36, 42, 0.4);
                }}
            """)
        else:
            # Default button styling
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(60, 66, 72, 0.9), stop:0.3 rgba(50, 56, 62, 0.95), 
                        stop:0.7 rgba(40, 46, 52, 1.0), stop:1 rgba(30, 36, 42, 1.0));
                    color: {ColorTokens.TEXT_PRIMARY};
                    border: 2px solid {ColorTokens.BORDER_SUBTLE};
                    padding: 8px 16px !important;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 16px;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(70, 76, 82, 0.9), stop:0.3 rgba(60, 66, 72, 0.95), 
                        stop:0.7 rgba(50, 56, 62, 1.0), stop:1 rgba(40, 46, 52, 1.0));
                    border-color: {ColorTokens.ACCENT_PRIMARY};
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(0, 180, 230, 0.9), stop:0.3 rgba(0, 160, 210, 0.95), 
                        stop:0.7 rgba(0, 140, 190, 1.0), stop:1 rgba(0, 120, 170, 1.0));
                    color: {ColorTokens.BG_PRIMARY};
                }}
            """)


class InfoPanel(QFrame):
    """Consistent info panel component."""
    
    def __init__(self, title: str, content: str):
        super().__init__()
        self.init_ui(title, content)
    
    def init_ui(self, title: str, content: str):
        """Initialize the info panel UI."""
        layout = LayoutBuilder.create_container_layout(
            self,
            spacing=LayoutTokens.SPACING_SM,
            margins=(LayoutTokens.MARGIN_MD, LayoutTokens.MARGIN_MD,
                    LayoutTokens.MARGIN_MD, LayoutTokens.MARGIN_MD)
        )
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Inter", LayoutTokens.FONT_MD, QFont.Bold))
        title_label.setStyleSheet("color: #2D1B69; font-weight: 600;")
        layout.addWidget(title_label)
        
        # Content
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setFont(QFont("Inter", LayoutTokens.FONT_SM))
        content_label.setStyleSheet("""
            color: #666;
            padding: 8px;
            background-color: #f0f0f0;
            border-radius: 6px;
            line-height: 1.4;
        """)
        layout.addWidget(content_label)
        
        # Panel styling
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(255, 182, 193, 0.3);
                border-radius: 12px;
                margin: 4px 0;
            }
        """)


class ButtonGroup(QWidget):
    """Consistent button group component."""
    
    def __init__(self, buttons: list, spacing: int = LayoutTokens.SPACING_MD):
        super().__init__()
        self.buttons = buttons
        self.init_ui(spacing)
    
    def init_ui(self, spacing: int):
        """Initialize the button group UI."""
        layout = LayoutBuilder.create_horizontal_layout(spacing)
        
        for button in self.buttons:
            layout.addWidget(button)
        
        self.setLayout(layout)


class SettingsSection(QGroupBox):
    """
    Reusable settings section component with consistent styling.
    
    Provides a QGroupBox with standardized styling for preferences dialogs.
    Can contain form layouts, vertical layouts, or horizontal layouts.
    
    Usage:
        section = SettingsSection("User Interface", layout_type="form")
        section.layout().addRow("Theme:", theme_combo)
    """
    
    def __init__(self, title: str, layout_type: str = "form"):
        """
        Initialize the settings section.
        
        Args:
            title: The section title to display
            layout_type: Layout type - "form", "vertical", or "horizontal"
        """
        super().__init__(title)
        self.init_layout(layout_type)
        self.apply_styling()
    
    def init_layout(self, layout_type: str):
        """Initialize the section layout."""
        if layout_type == "form":
            layout = QFormLayout(self)
            layout.setSpacing(LayoutTokens.SPACING_MD)
        elif layout_type == "vertical":
            layout = QVBoxLayout(self)
            layout.setSpacing(LayoutTokens.SPACING_MD)
        elif layout_type == "horizontal":
            layout = QHBoxLayout(self)
            layout.setSpacing(LayoutTokens.SPACING_MD)
        else:
            raise ValueError(f"Unknown layout type: {layout_type}")
    
    def apply_styling(self):
        """Apply consistent styling to the section."""
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                color: {ColorTokens.TEXT_PRIMARY} !important;
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: {LayoutTokens.RADIUS_MD}px;
                margin-top: 20px;
                padding-top: 20px;
                background-color: {ColorTokens.BG_PRIMARY};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {LayoutTokens.SPACING_LG}px;
                padding: 0 {LayoutTokens.SPACING_MD}px 0 {LayoutTokens.SPACING_MD}px;
                color: {ColorTokens.TEXT_PRIMARY} !important;
                font-weight: 700;
                font-size: {LayoutTokens.FONT_XL}px;
            }}
        """)


class InfoLabel(QLabel):
    """
    Reusable info/help text label with consistent styling.
    
    Displays secondary text with proper styling for help/info messages
    in settings dialogs. Automatically handles word wrapping.
    
    Usage:
        info = InfoLabel("This is a helpful message about the setting.")
        layout.addRow(info)
    """
    
    def __init__(self, text: str, font_size: int = 12):
        """
        Initialize the info label.
        
        Args:
            text: The info text to display
            font_size: Font size in pixels (default: 12)
        """
        super().__init__(text)
        self.setWordWrap(True)
        self.apply_styling(font_size)
    
    def apply_styling(self, font_size: int):
        """Apply consistent styling to the info label."""
        self.setStyleSheet(f"""
            QLabel {{
                color: {ColorTokens.TEXT_SECONDARY};
                font-size: {font_size}px;
                padding: 12px;
                background-color: transparent;
                border-radius: 6px;
                line-height: 1.4;
            }}
        """)
