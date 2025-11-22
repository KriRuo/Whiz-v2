"""
Modern Styles Module for Whiz Voice-to-Text Application
Dark theme with neon cyan accents and modern design.
"""

from ui.layout_system import ColorTokens, ResponsiveFontSize, DPIScalingHelper, ResponsiveBreakpoints, ScreenSizeClass


class MainStyles:
    """Modern application styles with dark theme and neon accents."""
    
    @staticmethod
    def get_responsive_font_size(size_key: str) -> int:
        """Get responsive font size for given key."""
        return ResponsiveFontSize.get_font_size(size_key)
    
    @staticmethod
    def get_responsive_stylesheet():
        """Get responsive stylesheet with dynamic font sizes."""
        # Get responsive font sizes
        font_xs = MainStyles.get_responsive_font_size('xs')
        font_sm = MainStyles.get_responsive_font_size('sm')
        font_md = MainStyles.get_responsive_font_size('md')
        font_lg = MainStyles.get_responsive_font_size('lg')
        font_xl = MainStyles.get_responsive_font_size('xl')
        font_xxl = MainStyles.get_responsive_font_size('xxl')
        font_title = MainStyles.get_responsive_font_size('title')
        
        return f"""
            /* Main Window - Dark charcoal background */
            QMainWindow {{
                background-color: {ColorTokens.BG_PRIMARY};
            }}
            
            /* Content Widget */
            QWidget#Content {{
                background-color: {ColorTokens.BG_PRIMARY};
            }}
            
            /* Tab Widget - Modern gradient tabs */
            QTabWidget::pane {{
                border: none;
                background-color: {ColorTokens.BG_SECONDARY};
                border-radius: 8px;
            }}
            
            QTabBar::tab {{
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_SECONDARY};
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: {font_xl}px;
                font-weight: 500;
                min-width: 90px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {ColorTokens.BG_SECONDARY};
                color: {ColorTokens.TEXT_PRIMARY};
                font-weight: 600;
            }}
            
            QTabBar::tab:hover {{
                background-color: {ColorTokens.BG_SECONDARY};
                color: {ColorTokens.TEXT_PRIMARY};
            }}
            
            /* Settings Button */
            QPushButton#SettingsButton {{
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_SECONDARY};
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                padding: 6px 12px;
                border-radius: 6px;
                font-size: {font_md}px;
            }}
            
            QPushButton#SettingsButton:hover {{
                background-color: {ColorTokens.BG_SECONDARY};
                color: {ColorTokens.TEXT_PRIMARY};
            }}
            
            /* Labels */
            QLabel {{
                color: {ColorTokens.TEXT_PRIMARY} !important;
                font-size: {font_lg}px;
                background: transparent;
            }}
            
            /* Force all labels in form layouts to use correct color */
            QFormLayout QLabel {{
                color: {ColorTokens.TEXT_PRIMARY} !important;
            }}
            
            /* Status Labels */
            QLabel[class="status"] {{
                color: {ColorTokens.TEXT_SECONDARY};
                font-size: {font_lg}px;
                font-weight: 400;
            }}
            
            /* Instruction Labels */
            QLabel[class="instruction"] {{
                color: {ColorTokens.TEXT_SECONDARY};
                font-size: {font_md}px;
                font-style: italic;
            }}
        """
    
    @staticmethod
    def get_main_stylesheet():
        """Get the main application stylesheet with dark theme design."""
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
                border: none;
                border-radius: 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {ColorTokens.BG_SECONDARY}, stop:1 #15181f);
                margin-top: 0px;
                padding: 0px;
            }}
            
            QTabBar::tab {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 49, 57, 0.8), stop:0.3 rgba(35, 39, 47, 0.9), 
                    stop:0.7 rgba(29, 33, 41, 0.95), stop:1 rgba(25, 29, 37, 1.0));
                color: {ColorTokens.TEXT_SECONDARY};
                padding: 6px 8px;
                margin-left: 12px;
                margin-right: 0px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-family: "Inter","Segoe UI",system-ui,-apple-system;
                font-weight: 500;
                font-size: 16px;
                min-height: 24px;
                min-width: 80px;
                border: 1px solid rgba(58, 63, 71, 0.6);
                border-bottom: 1px solid rgba(58, 63, 71, 0.3);
            }}
            
            QTabBar::tab:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(55, 59, 67, 0.9), stop:0.2 rgba(45, 49, 57, 0.95), 
                    stop:0.6 rgba(35, 39, 47, 1.0), stop:1 rgba(29, 33, 41, 1.0));
                color: {ColorTokens.TEXT_PRIMARY};
                font-family: "Inter","Segoe UI",system-ui,-apple-system;
                font-weight: 500;
                font-size: 16px;
                border: 1px solid rgba(58, 63, 71, 0.8);
                margin-bottom: -1px;
            }}
            
            QTabBar::tab:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(50, 54, 62, 0.85), stop:0.3 rgba(40, 44, 52, 0.9), 
                    stop:0.7 rgba(32, 36, 44, 0.95), stop:1 rgba(28, 32, 40, 1.0));
                color: {ColorTokens.TEXT_PRIMARY};
                border: 1px solid rgba(58, 63, 71, 0.7);
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
            
            QLineEdit::placeholder {{
                color: {ColorTokens.TEXT_TERTIARY};
                font-style: italic;
            }}
            
            /* Combo Box Styling - Dark theme */
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
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 80, 86, 0.9), stop:0.3 rgba(64, 70, 76, 0.95), 
                    stop:0.7 rgba(54, 60, 66, 1.0), stop:1 rgba(44, 50, 56, 1.0));
                color: {ColorTokens.TEXT_PRIMARY};
                border: 1px solid rgba(58, 63, 71, 0.8);
                padding: 8px 16px !important;
                border-radius: 6px;
                font-family: "Inter","Segoe UI",system-ui,-apple-system;
                font-weight: 500;
                font-size: 16px;
                min-height: 20px;
            }}
            
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(84, 90, 96, 0.9), stop:0.3 rgba(74, 80, 86, 0.95), 
                    stop:0.7 rgba(64, 70, 76, 1.0), stop:1 rgba(54, 60, 66, 1.0));
                border-color: {ColorTokens.ACCENT_PRIMARY};
            }}
            
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 180, 230, 0.9), stop:0.3 rgba(0, 160, 210, 0.95), 
                    stop:0.7 rgba(0, 140, 190, 1.0), stop:1 rgba(0, 120, 170, 1.0));
                color: {ColorTokens.BG_PRIMARY};
                border-color: rgba(0, 212, 255, 0.8);
            }}
            
            QPushButton:disabled {{
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_TERTIARY};
                border-color: {ColorTokens.BORDER_SUBTLE};
            }}
            
            
            /* Label Styling - Dark theme */
            QLabel {{
                font-family: "Inter","Segoe UI",system-ui,-apple-system;
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
    
    @staticmethod
    def get_status_label_style():
        """Get styling for status label with dark theme."""
        return f"""
            QLabel {{
                color: {ColorTokens.TEXT_PRIMARY};
                font-family: "Inter","Segoe UI",system-ui,-apple-system;
                font-weight: 500;
                font-size: 13px;
            }}
        """
    
    @staticmethod
    def get_dark_theme_addition():
        """Provide additional dark theme styles for backward compatibility tests."""
        # Reuse main stylesheet additions that darken components
        return f"""
            /* Additional dark theme cues (legacy tests expect this API) */
            QMainWindow {{ background: {ColorTokens.BG_PRIMARY}; background-color: {ColorTokens.BG_PRIMARY}; }}
            QWidget {{ background: {ColorTokens.BG_PRIMARY}; background-color: {ColorTokens.BG_PRIMARY}; }}
            QLabel {{ color: {ColorTokens.TEXT_PRIMARY} !important; }}
        """

    @staticmethod
    def get_start_button_style():
        """Get styling for start button with cyan theme."""
        return f"""
            QPushButton {{
                background-color: {ColorTokens.BUTTON_PRIMARY};
                color: {ColorTokens.BG_PRIMARY};
                border: 2px solid {ColorTokens.ACCENT_PRIMARY};
                padding: 8px 16px !important;
                border-radius: 6px;
                font-weight: 700;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {ColorTokens.BUTTON_HOVER};
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            }}
            QPushButton:pressed {{
                background-color: {ColorTokens.ACCENT_PRIMARY};
                color: {ColorTokens.BG_PRIMARY};
            }}
        """
    
    @staticmethod
    def get_stop_button_style():
        """Get styling for stop button with dark theme."""
        return f"""
            QPushButton {{
                background-color: {ColorTokens.BUTTON_SECONDARY};
                color: {ColorTokens.TEXT_PRIMARY};
                border: 2px solid {ColorTokens.BORDER_SUBTLE};
                padding: 8px 16px !important;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #5a6066;
                border-color: #6a7076;
            }}
            QPushButton:pressed {{
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_PRIMARY};
            }}
        """
    
    @staticmethod
    def get_hotkey_instruction_style():
        """Get styling for hotkey instruction label with dark theme."""
        return f"""
            QLabel {{
                color: {ColorTokens.TEXT_SECONDARY};
                padding: 8px;
                font-family: "Inter","Segoe UI",system-ui,-apple-system;
                font-size: 12px;
                font-style: italic;
                font-weight: 500;
            }}
        """
    
    @staticmethod
    def get_header_line_style():
        """Get styling for header line with dark theme."""
        return f"QFrame {{ color: {ColorTokens.BORDER_SUBTLE}; }}"
    
    @staticmethod
    def get_tips_title_style():
        """Get styling for tips title with dark theme."""
        return f"""
            QLabel {{
                color: {ColorTokens.TEXT_PRIMARY};
                font-weight: 600;
                padding: 8px 16px !important;
                background-color: {ColorTokens.BG_SECONDARY};
                border-radius: 8px;
                margin: 2px 0;
                font-size: 12px;
            }}
            QLabel:hover {{
                background-color: {ColorTokens.BG_TERTIARY};
            }}
        """
    
    @staticmethod
    def get_tips_content_style():
        """Get styling for tips content with dark theme."""
        return f"""
            QLabel {{
                color: {ColorTokens.TEXT_SECONDARY};
                font-style: italic;
                padding: 16px;
                background-color: {ColorTokens.BG_SECONDARY};
                border-radius: 12px;
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                font-size: 11px;
                margin-top: 8px;
            }}
        """
    
    @staticmethod
    def get_transcript_scroll_area_style():
        """Get styling for transcript scroll area with dark theme."""
        return f"""
            QScrollArea {{
                border: none;
                border-radius: 16px;
                background-color: {ColorTokens.BG_PRIMARY};
            }}
            QScrollArea QWidget {{
                width: 100%;
            }}
            QScrollBar:vertical {{
                background-color: {ColorTokens.BG_TERTIARY};
                width: 8px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {ColorTokens.BORDER_SUBTLE};
                border-radius: 4px;
                min-height: 20px;
                margin: 1px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {ColorTokens.ACCENT_PRIMARY};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """
    
    @staticmethod
    def get_empty_transcript_style():
        """Get styling for empty transcript message with dark theme."""
        return f"""
            QLabel {{
                color: {ColorTokens.TEXT_SECONDARY};
                font-style: italic;
                padding: 20px 16px;
                margin: 6px 4px;
                background-color: {ColorTokens.BG_SECONDARY};
                border-radius: 16px;
                border: 2px dashed {ColorTokens.BORDER_SUBTLE};
                font-size: 14px;
            }}
        """
    
    @staticmethod
    def get_transcript_item_style():
        """Get styling for transcript item frame with chat bubble appearance."""
        return f"""
            QFrame {{
                background-color: {ColorTokens.BG_SECONDARY};
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: 16px;
                padding: 12px;
                margin: 6px 8px;
                min-width: 200px;
            }}
            QFrame:hover {{
                background-color: {ColorTokens.BG_TERTIARY};
                border-color: {ColorTokens.ACCENT_PRIMARY};
            }}
            QLabel {{
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }}
        """
    
    @staticmethod
    def get_timestamp_style():
        """Get styling for timestamp label with dark theme."""
        return f"""
            color: {ColorTokens.TEXT_TERTIARY}; 
            font-size: 11px; 
            font-weight: 400;
            font-family: "Inter","Segoe UI",system-ui,-apple-system;
            margin-bottom: 4px;
        """
    
    @staticmethod
    def get_transcript_text_style():
        """Get styling for transcript text with dark theme."""
        return f"""
            color: {ColorTokens.TEXT_PRIMARY}; 
            padding: 0px; 
            font-size: 14px;
            font-family: "Inter","Segoe UI",system-ui,-apple-system;
            font-weight: 400;
            line-height: 1.4;
        """