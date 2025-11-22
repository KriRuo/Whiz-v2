"""
Theme Manager for Whiz Voice-to-Text Application
Manages theme switching and generates theme-specific stylesheets.
"""

from PyQt5.QtCore import QObject, pyqtSignal
from ui.layout_system import ColorTokens


class ThemeManager(QObject):
    """Manages application themes and generates appropriate stylesheets."""
    
    # Signal emitted when theme changes
    theme_changed = pyqtSignal(str)
    
    def __init__(self, settings_manager=None):
        super().__init__()
        self.settings_manager = settings_manager
        self.current_theme = "dark"  # Default to dark theme
        
    def get_current_theme(self) -> str:
        """Get the current theme name."""
        return self.current_theme
        
    def set_theme(self, theme: str):
        """Set the current theme and save to settings."""
        if theme not in ["dark", "light"]:
            raise ValueError(f"Invalid theme: {theme}. Must be 'dark' or 'light'.")
            
        self.current_theme = theme
        
        # Save to settings if manager is available
        if self.settings_manager:
            self.settings_manager.save_setting("ui/theme", theme)
            
        # Emit signal for UI updates
        self.theme_changed.emit(theme)
        
    def get_dark_stylesheet(self) -> str:
        """Get the dark theme stylesheet."""
        return f"""
            /* Main Window - Dark charcoal background */
            QMainWindow {{
                background-color: {ColorTokens.BG_PRIMARY};
            }}
            
            /* Central Widget - Transparent to show background */
            QWidget#centralWidget {{
                background: transparent;
            }}
            
            /* Content Widget - Dark background */
            QWidget#Content {{
                background-color: {ColorTokens.BG_PRIMARY};
                border-bottom-left-radius: 16px;
                border-bottom-right-radius: 16px;
                border-top: 1px solid {ColorTokens.BORDER_SUBTLE};
            }}
            
            /* Tab Widget Styling - Dark theme */
            QTabWidget::pane {{
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: 16px;
                background-color: {ColorTokens.BG_SECONDARY};
                margin-top: 12px;
                padding: 4px;
            }}
            
            QTabBar::tab {{
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_SECONDARY};
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                font-size: 13px;
                min-height: 28px;
                min-width: 100px;
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
            }}
            
            QTabBar::tab:selected {{
                background-color: {ColorTokens.BG_SECONDARY};
                color: {ColorTokens.TEXT_PRIMARY};
                border-bottom: 3px solid {ColorTokens.ACCENT_PRIMARY};
                font-weight: 600;
                font-size: 13px;
            }}
            
            QTabBar::tab:hover {{
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_PRIMARY};
            }}
            
            /* Group Box Styling - Dark theme */
            QGroupBox {{
                font-weight: 600;
                font-size: 12px;
                color: {ColorTokens.TEXT_PRIMARY};
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: 16px;
                margin-top: 20px;
                padding-top: 20px;
                background-color: {ColorTokens.BG_SECONDARY};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 12px 0 12px;
                color: {ColorTokens.TEXT_PRIMARY};
                font-weight: 600;
            }}
            
            /* Input Fields Styling - Dark theme */
            QLineEdit {{
                padding: 8px 12px;
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: 6px;
                font-size: 13px;
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_PRIMARY};
                selection-background-color: {ColorTokens.ACCENT_PRIMARY};
                min-height: 18px;
            }}
            
            QLineEdit:focus {{
                border-color: {ColorTokens.ACCENT_PRIMARY};
                background-color: {ColorTokens.BG_SECONDARY};
            }}
            
            QComboBox {{
                padding: 8px 12px;
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: 6px;
                font-size: 13px;
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_PRIMARY};
                min-height: 18px;
            }}
            
            QComboBox:focus {{
                border-color: {ColorTokens.ACCENT_PRIMARY};
                background-color: {ColorTokens.BG_SECONDARY};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {ColorTokens.TEXT_SECONDARY};
                margin-right: 5px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {ColorTokens.BG_SECONDARY};
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                color: {ColorTokens.TEXT_PRIMARY} !important;
                selection-background-color: {ColorTokens.ACCENT_PRIMARY};
                selection-color: {ColorTokens.TEXT_PRIMARY} !important;
                padding: 4px;
            }}
            
            QComboBox::item {{
                color: {ColorTokens.TEXT_PRIMARY} !important;
                background-color: transparent;
                padding: 6px 12px;
                min-height: 24px;
            }}
            
            QComboBox::item:selected {{
                background-color: {ColorTokens.ACCENT_PRIMARY};
                color: {ColorTokens.TEXT_PRIMARY} !important;
            }}
            
            QComboBox::item:hover {{
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_PRIMARY} !important;
            }}
            
            /* Button Styling - Dark theme */
            QPushButton {{
                background-color: {ColorTokens.BUTTON_SECONDARY};
                color: {ColorTokens.TEXT_PRIMARY};
                border: 2px solid {ColorTokens.BORDER_SUBTLE};
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                min-height: 18px;
            }}
            
            QPushButton:hover {{
                background-color: {ColorTokens.BUTTON_HOVER};
                border-color: {ColorTokens.ACCENT_PRIMARY};
            }}
            
            QPushButton:pressed {{
                background-color: {ColorTokens.ACCENT_PRIMARY};
                color: {ColorTokens.BG_PRIMARY};
            }}
            
            QPushButton:disabled {{
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_TERTIARY};
                border-color: {ColorTokens.BORDER_SUBTLE};
            }}
            
            /* Start Button - Cyan with glow */
            QPushButton#StartButton {{
                background-color: {ColorTokens.BUTTON_PRIMARY};
                color: {ColorTokens.BG_PRIMARY};
                border: 2px solid {ColorTokens.ACCENT_PRIMARY};
                font-weight: 700;
            }}
            
            QPushButton#StartButton:hover {{
                background-color: {ColorTokens.BUTTON_HOVER};
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            }}
            
            /* Stop Button - Dark gray */
            QPushButton#StopButton {{
                background-color: {ColorTokens.BUTTON_SECONDARY};
                color: {ColorTokens.TEXT_PRIMARY};
                border: 2px solid {ColorTokens.BORDER_SUBTLE};
            }}
            
            QPushButton#StopButton:hover {{
                background-color: #5a6066;
                border-color: #6a7076;
            }}
            
            /* Label Styling - Dark theme */
            QLabel {{
                font-size: 13px;
                color: {ColorTokens.TEXT_PRIMARY} !important;
                line-height: 1.4;
                background: transparent;
            }}
            
            /* Force all labels in form layouts to use correct color */
            QFormLayout QLabel {{
                color: {ColorTokens.TEXT_PRIMARY} !important;
            }}
            
            /* Checkbox Styling - Dark theme */
            QCheckBox {{
                font-size: 13px;
                color: {ColorTokens.TEXT_PRIMARY};
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: 6px;
                background-color: {ColorTokens.BG_TERTIARY};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {ColorTokens.ACCENT_PRIMARY};
                border-color: {ColorTokens.ACCENT_PRIMARY};
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {ColorTokens.ACCENT_PRIMARY};
            }}
            
            /* Scroll Area Styling - Dark theme */
            QScrollArea {{
                background-color: {ColorTokens.BG_SECONDARY};
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: 8px;
            }}
            
            QScrollBar:vertical {{
                background-color: {ColorTokens.BG_TERTIARY};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {ColorTokens.BORDER_SUBTLE};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {ColorTokens.ACCENT_PRIMARY};
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """
        
    def get_light_stylesheet(self) -> str:
        """Get the light theme stylesheet (placeholder for future implementation)."""
        # For now, return dark theme as we're focusing on dark mode
        return self.get_dark_stylesheet()
        
    def get_current_stylesheet(self) -> str:
        """Get the stylesheet for the current theme."""
        if self.current_theme == "dark":
            return self.get_dark_stylesheet()
        elif self.current_theme == "light":
            return self.get_light_stylesheet()
        else:
            return self.get_dark_stylesheet()  # Fallback
