"""
Preferences dialog for Whiz Voice-to-Text application.
Provides a comprehensive UI for managing all application settings.
"""

import os
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QFormLayout,
    QComboBox, QCheckBox, QLineEdit, QPushButton, QLabel, QSlider, QSpinBox,
    QGroupBox, QFileDialog, QMessageBox, QScrollArea, QFrame, QSizePolicy,
    QApplication, QDesktopWidget, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QTimer
from PyQt5.QtGui import QFont, QPixmap, QCursor
from PyQt5.QtMultimedia import QSoundEffect

from core.settings_manager import SettingsManager
from core.settings_schema import SETTINGS_SCHEMA
from core.logging_config import get_logger
from ui.components import BaseDialog, SettingsSection, InfoLabel

logger = get_logger(__name__)
from ui.widgets.gradient_tab_widget import GradientTabWidget
from ui.layout_system import (LayoutBuilder, LayoutTokens, ResponsiveSizing, ColorTokens,
                             ResponsiveBreakpoints, DPIScalingHelper, ResponsiveFontSize, AdaptiveSpacing)

class PreferencesDialog(BaseDialog):
    """Comprehensive preferences dialog with tabbed interface."""
    
    # Signal emitted when settings change
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, settings_manager: SettingsManager, parent=None):
        """
        Initialize the preferences dialog.
        
        Args:
            settings_manager: The settings manager instance
            parent: Parent widget
        """
        # Store settings manager and load settings FIRST
        self.settings_manager = settings_manager
        self.current_settings = settings_manager.load_all()
        
        # Initialize base dialog (this will call init_content)
        super().__init__(parent)
        
        # Set dialog properties
        self.setWindowTitle("Preferences")
        self.setModal(True)
        
        # Load settings into UI and setup responsive geometry
        self.load_settings()
        try:
            self.setup_responsive_geometry()
        except Exception as e:
            # Continue with default size if responsive sizing fails
            logger.warning(f"Failed to setup responsive geometry: {e}")
            self.resize(800, 600)  # Default dialog size
    
    
    def init_content(self):
        """Initialize the dialog content using layout system."""
        # Create tab widget
        self.tab_widget = GradientTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_general_tab()
        self.create_behavior_tab()
        self.create_audio_tab()
        self.create_transcription_tab()
        self.create_advanced_tab()
        
        # Create button layout using layout system
        button_layout = self.create_horizontal_layout()
        button_layout.addStretch()
        
        # Action buttons
        self.restore_button = QPushButton("Restore Defaults")
        self.restore_button.clicked.connect(self.restore_defaults)
        button_layout.addWidget(self.restore_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(button_layout)
        
        # Apply styling using layout tokens
        self.setStyleSheet(self.get_dialog_stylesheet())
        
        # Force palette colors to ensure all text is white (fixes Qt Fusion style black text)
        from PyQt5.QtGui import QPalette, QColor
        palette = self.palette()
        palette.setColor(QPalette.WindowText, QColor(ColorTokens.TEXT_PRIMARY))
        palette.setColor(QPalette.Text, QColor(ColorTokens.TEXT_PRIMARY))
        palette.setColor(QPalette.ButtonText, QColor(ColorTokens.TEXT_PRIMARY))
        palette.setColor(QPalette.BrightText, QColor(ColorTokens.TEXT_PRIMARY))
        self.setPalette(palette)
        
        # Ensure tab elision is disabled AFTER stylesheet is applied
        if hasattr(self.tab_widget, 'tabBar'):
            self.tab_widget.tabBar().setElideMode(Qt.ElideNone)
    
    # Layout Helper Methods
    def create_tab_layout(self, tab):
        """Create a consistent main layout for tabs with responsive spacing."""
        layout = QVBoxLayout(tab)
        responsive_spacing = AdaptiveSpacing.get_spacing(LayoutTokens.SPACING_MD)
        responsive_margin = AdaptiveSpacing.get_spacing(LayoutTokens.MARGIN_MD)
        layout.setSpacing(responsive_spacing)
        layout.setContentsMargins(responsive_margin, responsive_margin, responsive_margin, responsive_margin)
        return layout
    
    def create_group_layout(self, group_box, layout_type="form"):
        """Create a consistent layout for group boxes."""
        if layout_type == "form":
            layout = QFormLayout(group_box)
            layout.setSpacing(LayoutTokens.SPACING_MD)
        elif layout_type == "vertical":
            layout = QVBoxLayout(group_box)
            layout.setSpacing(LayoutTokens.SPACING_MD)
        elif layout_type == "horizontal":
            layout = QHBoxLayout(group_box)
            layout.setSpacing(LayoutTokens.SPACING_MD)
        else:
            raise ValueError(f"Unknown layout type: {layout_type}")
        return layout
    
    def create_horizontal_layout(self, spacing=None):
        """Create a horizontal layout with consistent spacing."""
        layout = QHBoxLayout()
        layout.setSpacing(spacing or LayoutTokens.SPACING_MD)
        return layout
    
    def create_vertical_layout(self, spacing=None):
        """Create a vertical layout with consistent spacing."""
        layout = QVBoxLayout()
        layout.setSpacing(spacing or LayoutTokens.SPACING_MD)
        return layout
    
    def create_styled_combobox(self, items=None):
        """Create a QComboBox with proper palette for white text and visible selected value."""
        from PyQt5.QtGui import QPalette, QColor
        from PyQt5.QtWidgets import QListView
        
        combo = QComboBox()
        
        # Ensure the combobox is not editable
        combo.setEditable(False)
        
        # Create and configure a custom view for the dropdown
        view = QListView()
        combo.setView(view)
        
        # Add items if provided (do this after setting view)
        if items:
            combo.addItems(items)
        
        # Set comprehensive palette for the combo box
        combo_palette = combo.palette()
        # These roles control the text display when closed
        combo_palette.setColor(QPalette.Active, QPalette.ButtonText, QColor(ColorTokens.TEXT_PRIMARY))
        combo_palette.setColor(QPalette.Inactive, QPalette.ButtonText, QColor(ColorTokens.TEXT_PRIMARY))
        combo_palette.setColor(QPalette.Active, QPalette.WindowText, QColor(ColorTokens.TEXT_PRIMARY))
        combo_palette.setColor(QPalette.Inactive, QPalette.WindowText, QColor(ColorTokens.TEXT_PRIMARY))
        combo_palette.setColor(QPalette.Active, QPalette.Text, QColor(ColorTokens.TEXT_PRIMARY))
        combo_palette.setColor(QPalette.Inactive, QPalette.Text, QColor(ColorTokens.TEXT_PRIMARY))
        # Background colors
        combo_palette.setColor(QPalette.Active, QPalette.Base, QColor(ColorTokens.BG_PRIMARY))
        combo_palette.setColor(QPalette.Inactive, QPalette.Base, QColor(ColorTokens.BG_PRIMARY))
        combo_palette.setColor(QPalette.Active, QPalette.Button, QColor(ColorTokens.BG_PRIMARY))
        combo_palette.setColor(QPalette.Inactive, QPalette.Button, QColor(ColorTokens.BG_PRIMARY))
        combo.setPalette(combo_palette)
        
        # Set palette for the dropdown view
        view_palette = view.palette()
        view_palette.setColor(QPalette.Text, QColor(ColorTokens.TEXT_PRIMARY))
        view_palette.setColor(QPalette.WindowText, QColor(ColorTokens.TEXT_PRIMARY))
        view_palette.setColor(QPalette.Base, QColor(ColorTokens.BG_SECONDARY))
        view_palette.setColor(QPalette.Window, QColor(ColorTokens.BG_SECONDARY))
        view_palette.setColor(QPalette.Highlight, QColor(ColorTokens.ACCENT_PRIMARY))
        view_palette.setColor(QPalette.HighlightedText, QColor(ColorTokens.BG_PRIMARY))
        view.setPalette(view_palette)
        
        # Force update to apply palette
        combo.update()
        
        return combo
    
    def get_dialog_stylesheet(self):
        """Get the dialog stylesheet using ColorTokens for theme consistency."""
        from ui.layout_system import ColorTokens
        
        return f"""
            QDialog {{
                background-color: {ColorTokens.BG_PRIMARY};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: {LayoutTokens.RADIUS_MD}px;
                background-color: {ColorTokens.BG_SECONDARY};
            }}
            
            QTabBar::tab {{
                background-color: {ColorTokens.BG_SECONDARY};
                color: {ColorTokens.TEXT_SECONDARY};
                padding: 12px 24px;
                margin-right: {LayoutTokens.SPACING_XS}px;
                border-top-left-radius: {LayoutTokens.RADIUS_SM}px;
                border-top-right-radius: {LayoutTokens.RADIUS_SM}px;
                font-weight: 500;
                font-size: {LayoutTokens.FONT_LG}px;
                min-height: 28px;
                min-width: 90px;
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
            }}
            
            QTabBar::tab:selected {{
                background-color: {ColorTokens.BG_SECONDARY};
                color: {ColorTokens.TEXT_PRIMARY};
                border-bottom: 3px solid {ColorTokens.ACCENT_PRIMARY};
                font-weight: 600;
                font-size: {LayoutTokens.FONT_LG}px;
            }}
            
            QTabBar::tab:hover {{
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_PRIMARY};
            }}
            
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
            
            QPushButton {{
                background-color: {ColorTokens.BG_PRIMARY};
                color: {ColorTokens.TEXT_PRIMARY};
                border: 2px solid {ColorTokens.BORDER_SUBTLE};
                padding: {LayoutTokens.SPACING_SM}px {LayoutTokens.SPACING_LG}px;
                border-radius: {LayoutTokens.RADIUS_SM}px;
                font-weight: 600;
                font-size: {LayoutTokens.FONT_LG}px;
                min-height: 18px;
            }}
            
            QPushButton:hover {{
                background-color: {ColorTokens.BG_TERTIARY};
                border-color: {ColorTokens.ACCENT_PRIMARY};
            }}
            
            QPushButton:pressed {{
                background-color: {ColorTokens.ACCENT_PRIMARY};
                color: white;
            }}
            
            QLineEdit {{
                padding: {LayoutTokens.SPACING_SM}px {LayoutTokens.SPACING_MD}px;
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: {LayoutTokens.RADIUS_SM}px;
                font-size: {LayoutTokens.FONT_LG}px;
                background-color: {ColorTokens.BG_PRIMARY};
                color: {ColorTokens.TEXT_PRIMARY} !important;
                min-height: 18px;
            }}
            
            QComboBox {{
                padding: {LayoutTokens.SPACING_SM}px {LayoutTokens.SPACING_MD}px;
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: {LayoutTokens.RADIUS_SM}px;
                font-size: {LayoutTokens.FONT_LG}px;
                background-color: {ColorTokens.BG_PRIMARY};
                color: {ColorTokens.TEXT_PRIMARY} !important;
                min-height: 18px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                background-color: {ColorTokens.BG_PRIMARY};
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {ColorTokens.TEXT_PRIMARY};
                margin-right: 5px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {ColorTokens.BG_SECONDARY};
                color: {ColorTokens.TEXT_PRIMARY} !important;
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                selection-background-color: {ColorTokens.ACCENT_PRIMARY};
                selection-color: {ColorTokens.TEXT_PRIMARY} !important;
                outline: 0;
            }}
            
            QComboBox QListView {{
                background-color: {ColorTokens.BG_SECONDARY};
                color: {ColorTokens.TEXT_PRIMARY} !important;
                border: 1px solid {ColorTokens.BORDER_SUBTLE};
                padding: 4px;
                outline: 0;
            }}
            
            QComboBox::item {{
                color: {ColorTokens.TEXT_PRIMARY} !important;
                background-color: {ColorTokens.BG_SECONDARY};
                padding: 8px 12px;
                min-height: 28px;
                border: none;
            }}
            
            QComboBox::item:selected {{
                background-color: {ColorTokens.ACCENT_PRIMARY};
                color: {ColorTokens.BG_PRIMARY} !important;
            }}
            
            QComboBox::item:hover {{
                background-color: {ColorTokens.BG_TERTIARY};
                color: {ColorTokens.TEXT_PRIMARY} !important;
            }}
            
            QComboBox::item:!selected {{
                color: {ColorTokens.TEXT_PRIMARY} !important;
            }}
            
            QLineEdit:focus, QComboBox:focus {{
                border-color: {ColorTokens.ACCENT_PRIMARY};
                background-color: {ColorTokens.BG_SECONDARY};
            }}
            
            QLabel {{
                font-size: {LayoutTokens.FONT_LG}px;
                color: {ColorTokens.TEXT_PRIMARY} !important;
                line-height: 1.4;
                background: transparent;
            }}
            
            /* Force all labels in form layouts to use correct color */
            QFormLayout QLabel {{
                color: {ColorTokens.TEXT_PRIMARY} !important;
            }}
            
            QCheckBox {{
                font-size: {LayoutTokens.FONT_LG}px;
                color: {ColorTokens.TEXT_PRIMARY};
                spacing: {LayoutTokens.SPACING_SM}px;
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {ColorTokens.BORDER_SUBTLE};
                border-radius: {LayoutTokens.RADIUS_SM}px;
                background-color: {ColorTokens.BG_PRIMARY};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {ColorTokens.ACCENT_PRIMARY};
                border-color: {ColorTokens.ACCENT_PRIMARY};
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {ColorTokens.ACCENT_PRIMARY};
            }}
        """
    
    def create_general_tab(self):
        """Create the General tab using unified components."""
        tab = QWidget()
        layout = self.create_tab_layout(tab)
        
        # UI Settings Section
        ui_section = SettingsSection("User Interface", layout_type="form")
        
        # Theme selection
        self.theme_combo = self.create_styled_combobox(["system", "light", "dark"])
        ui_section.layout().addRow("Theme:", self.theme_combo)
        
        # Theme info
        theme_info = InfoLabel(
            "• system: Follow your system's dark/light mode setting\n"
            "• light: Always use light theme\n"
            "• dark: Always use dark theme"
        )
        ui_section.layout().addRow(theme_info)
        
        layout.addWidget(ui_section)
        
        # Language Settings Section
        language_section = SettingsSection("Language Settings", layout_type="form")
        
        # Language selection
        self.language_combo = self.create_styled_combobox([
            "auto", "en", "de", "es", "fr", "it", "pt", "ru", "ja", "ko", "zh", 
            "sv", "fi", "no", "da", "nl", "pl", "tr", "ar", "hi"
        ])
        language_section.layout().addRow("Language:", self.language_combo)
        
        # Language info
        language_info = InfoLabel(
            "• auto: Automatically detect language from speech\n"
            "• Specific languages: Force transcription in that language\n"
            "• Using a specific language can improve accuracy"
        )
        language_section.layout().addRow(language_info)
        
        layout.addWidget(language_section)
        
        # Engine Settings Section
        engine_section = SettingsSection("Transcription Engine", layout_type="form")
        
        # Engine selection
        self.engine_combo = self.create_styled_combobox(["faster", "openai"])  # faster first as it's the default
        engine_section.layout().addRow("Engine:", self.engine_combo)
        
        # Engine info
        engine_info = InfoLabel(
            "• faster: Faster-whisper implementation (5-10x faster, recommended, default)\n"
            "• openai: Original Whisper implementation (slower but very stable)\n\n"
            "Note: faster-whisper uses INT8 quantization for efficient CPU inference.\n"
            "Falls back to openai automatically if faster-whisper is unavailable."
        )
        engine_section.layout().addRow(engine_info)
        
        layout.addWidget(engine_section)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "General")
    
    def create_behavior_tab(self):
        """Create the Behavior tab using unified components."""
        tab = QWidget()
        layout = self.create_tab_layout(tab)
        
        # Recording Behavior Section
        recording_section = SettingsSection("Recording Behavior", layout_type="form")
        
        # Auto-paste setting
        self.auto_paste_checkbox = QCheckBox("Enable Auto-Paste")
        recording_section.layout().addRow(self.auto_paste_checkbox)
        
        # Toggle mode setting
        self.toggle_mode_checkbox = QCheckBox("Toggle Mode (press once to start/stop)")
        recording_section.layout().addRow(self.toggle_mode_checkbox)
        
        # Toggle mode info
        toggle_info = InfoLabel(
            "• Hold Mode: Hold the hotkey while speaking, release to transcribe\n"
            "• Toggle Mode: Press once to start recording, press again to stop"
        )
        recording_section.layout().addRow(toggle_info)
        
        # Minimize to tray setting
        self.minimize_to_tray_checkbox = QCheckBox("Keep app running in background on close")
        recording_section.layout().addRow(self.minimize_to_tray_checkbox)
        
        # Tray info
        tray_info = InfoLabel(
            "When enabled, closing the window will minimize it to the system tray instead of exiting.\n"
            "You can restore the window by clicking the tray icon or using the tray menu."
        )
        recording_section.layout().addRow(tray_info)
        
        layout.addWidget(recording_section)
        
        # Visual Indicator Section
        visual_section = SettingsSection("Visual Indicator", layout_type="form")
        
        # Visual indicator setting
        self.visual_indicator_checkbox = QCheckBox("Show visual indicator while recording")
        visual_section.layout().addRow(self.visual_indicator_checkbox)
        
        # Indicator position setting
        self.indicator_position_combo = self.create_styled_combobox([
            "Top Left", "Top Right", "Bottom Right", "Bottom Left",
            "Top Center", "Middle Center", "Bottom Center"
        ])
        visual_section.layout().addRow("Indicator Position:", self.indicator_position_combo)
        
        # Visual indicator info
        visual_info = InfoLabel(
            "The visual indicator shows a small overlay on screen while recording.\n"
            "This helps you see that the application is actively listening."
        )
        visual_section.layout().addRow(visual_info)
        
        layout.addWidget(visual_section)
        
        # Hotkey Settings Section
        hotkey_section = SettingsSection("Hotkey Settings", layout_type="form")
        
        # Hotkey selection
        self.hotkey_combo = self.create_styled_combobox([
            "F8", "F9", "ctrl+shift+R", "ctrl+alt+S", "alt gr", 
            "caps lock", "cmd+R", "shift+F12"
        ])
        hotkey_section.layout().addRow("Hotkey:", self.hotkey_combo)
        
        # Hotkey info
        hotkey_info = InfoLabel(
            "Choose the key combination to start/stop recording.\n"
            "The hotkey works in both Hold Mode and Toggle Mode."
        )
        hotkey_section.layout().addRow(hotkey_info)
        
        layout.addWidget(hotkey_section)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Behavior")
    
    def create_audio_tab(self):
        """Create the Audio tab using unified components."""
        tab = QWidget()
        layout = self.create_tab_layout(tab)
        
        # Audio Effects Section
        effects_section = SettingsSection("Audio Effects", layout_type="form")
        
        # Enable sound effects
        self.sound_effects_checkbox = QCheckBox("Enable start/stop sound effects")
        effects_section.layout().addRow(self.sound_effects_checkbox)
        
        layout.addWidget(effects_section)
        
        # Device Selection Section
        device_section = SettingsSection("Microphone Device", layout_type="form")
        
        # Device selection combo box with buttons
        device_selection_layout = self.create_horizontal_layout()
        self.device_combo = self.create_styled_combobox()
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        device_selection_layout.addWidget(self.device_combo)
        
        # Refresh devices button
        self.refresh_devices_button = QPushButton("Refresh")
        self.refresh_devices_button.clicked.connect(self.refresh_device_list)
        device_selection_layout.addWidget(self.refresh_devices_button)
        
        # Test device button
        self.test_device_button = QPushButton("Test")
        self.test_device_button.clicked.connect(self.test_selected_device)
        device_selection_layout.addWidget(self.test_device_button)
        
        device_section.layout().addRow("Device:", device_selection_layout)
        
        # No device warning (initially hidden) - using InfoLabel with custom warning styling
        self.no_device_warning = InfoLabel(
            "⚠️ No microphone detected. Please connect a microphone and click Refresh.\n"
            "Make sure your microphone is plugged in and enabled in system settings.",
            font_size=12
        )
        # Override styling for warning appearance
        self.no_device_warning.setStyleSheet(f"color: {ColorTokens.TEXT_PRIMARY}; font-size: 12px; padding: 12px; background-color: #ffebee; border: 1px solid #f44336; border-radius: 6px;")
        self.no_device_warning.hide()
        device_section.layout().addRow(self.no_device_warning)
        
        layout.addWidget(device_section)
        
        # Tone Files Section
        tones_section = SettingsSection("Tone Files", layout_type="form")
        
        # Start tone
        start_tone_layout = self.create_horizontal_layout()
        self.start_tone_edit = QLineEdit()
        start_tone_browse = QPushButton("Browse...")
        start_tone_browse.clicked.connect(lambda: self.browse_tone_file("start"))
        start_tone_test = QPushButton("Test")
        start_tone_test.clicked.connect(lambda: self.test_tone("start"))
        start_tone_layout.addWidget(self.start_tone_edit)
        start_tone_layout.addWidget(start_tone_browse)
        start_tone_layout.addWidget(start_tone_test)
        tones_section.layout().addRow("Start Tone:", start_tone_layout)
        
        # Stop tone
        stop_tone_layout = self.create_horizontal_layout()
        self.stop_tone_edit = QLineEdit()
        stop_tone_browse = QPushButton("Browse...")
        stop_tone_browse.clicked.connect(lambda: self.browse_tone_file("stop"))
        stop_tone_test = QPushButton("Test")
        stop_tone_test.clicked.connect(lambda: self.test_tone("stop"))
        stop_tone_layout.addWidget(self.stop_tone_edit)
        stop_tone_layout.addWidget(stop_tone_browse)
        stop_tone_layout.addWidget(stop_tone_test)
        tones_section.layout().addRow("Stop Tone:", stop_tone_layout)
        
        layout.addWidget(tones_section)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Audio")
    
    def create_transcription_tab(self):
        """Create the Transcription tab using unified components."""
        tab = QWidget()
        layout = self.create_tab_layout(tab)
        
        # Whisper Settings Section
        whisper_section = SettingsSection("Whisper Model Settings", layout_type="form")
        
        # Model selection
        self.model_combo = self.create_styled_combobox(["tiny", "base", "small", "medium", "large"])
        whisper_section.layout().addRow("Model Size:", self.model_combo)
        
        # Model info
        model_info = InfoLabel(
            "• tiny: Fastest, least accurate (~39 MB)\n"
            "• base: Fast, good accuracy (~74 MB)\n"
            "• small: Balanced speed/accuracy (~244 MB)\n"
            "• medium: Slower, better accuracy (~769 MB)\n"
            "• large: Slowest, most accurate (~1550 MB)"
        )
        whisper_section.layout().addRow(model_info)
        
        # Speed mode
        self.speed_mode_checkbox = QCheckBox("Enable speed optimizations")
        whisper_section.layout().addRow(self.speed_mode_checkbox)
        
        layout.addWidget(whisper_section)
        
        # Performance Settings Section (vertical layout)
        perf_section = SettingsSection("Performance Settings", layout_type="vertical")
        
        # Performance info
        perf_info = InfoLabel(
            "For best performance:\n"
            "• Use 'tiny' or 'base' models for real-time transcription\n"
            "• Set temperature to 0.0 for fastest results\n"
            "• Enable speed optimizations\n"
            "• Close other applications to free up memory"
        )
        perf_section.layout().addWidget(perf_info)
        
        layout.addWidget(perf_section)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Transcription")
    
    
    def create_advanced_tab(self):
        """Create the Advanced tab using unified components."""
        tab = QWidget()
        layout = self.create_tab_layout(tab)
        
        # Expert Settings Section
        expert_section = SettingsSection("Expert Settings", layout_type="form")
        
        # Expert mode toggle
        self.expert_mode_checkbox = QCheckBox("Enable Expert Mode")
        expert_section.layout().addRow(self.expert_mode_checkbox)
        
        # Expert mode info
        expert_info = InfoLabel(
            "Expert Mode reveals advanced settings that most users don't need to change.\n"
            "These settings can affect performance and accuracy but require technical knowledge.\n"
            "When disabled, advanced settings are reset to recommended values."
        )
        expert_section.layout().addRow(expert_info)
        
        # Reset to recommended button
        self.reset_recommended_button = QPushButton("Reset to Recommended")
        self.reset_recommended_button.clicked.connect(self.reset_to_recommended)
        self.reset_recommended_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ColorTokens.BUTTON_SECONDARY};
                color: {ColorTokens.TEXT_PRIMARY};
                border: 1px solid {ColorTokens.BORDER};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {ColorTokens.BUTTON_SECONDARY_HOVER};
            }}
        """)
        expert_section.layout().addRow("", self.reset_recommended_button)
        
        layout.addWidget(expert_section)
        
        # Temperature Settings Section (initially hidden - kept as QGroupBox for visibility control)
        self.temperature_group = SettingsSection("Transcription Temperature", layout_type="form")
        self.temperature_layout = self.temperature_group.layout()
        
        # Temperature setting
        temp_layout = self.create_horizontal_layout()
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 100)  # 0.0 to 1.0 as integers
        self.temperature_slider.setValue(0)  # Default to 0.0
        
        self.temperature_label = QLabel("0.0")
        self.temperature_label.setMinimumWidth(30)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_label)
        self.temperature_layout.addRow("Temperature:", temp_layout)
        
        # Temperature info
        temp_info = InfoLabel(
            "Controls randomness in transcription:\n"
            "• 0.0: Most deterministic, fastest (recommended)\n"
            "• 0.5: Balanced\n"
            "• 1.0: Most creative, slowest\n\n"
            "Most users should leave this at 0.0 for best performance."
        )
        self.temperature_layout.addRow(temp_info)
        
        layout.addWidget(self.temperature_group)
        self.temperature_group.hide()  # Initially hidden
        
        # Advanced Settings Section
        advanced_section = SettingsSection("Advanced Settings", layout_type="vertical")
        
        # Settings file info
        settings_info = InfoLabel(
            f"Settings are stored in:\n{self.settings_manager.get_settings_file_path()}\n\n"
            "You can manually edit this file if needed. Settings are automatically saved when changed."
        )
        advanced_section.layout().addWidget(settings_info)
        
        layout.addWidget(advanced_section)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Advanced")
    
    def load_settings(self):
        """Load current settings into the UI using cached settings for performance."""
        try:
            # Disconnect all signals to prevent triggering during load
            self._disconnect_signals()
            
            # Use cached settings for better performance (no validation overhead)
            self.current_settings = self.settings_manager.load_all()
            
            # General settings - use setCurrentIndex with findText for reliability
            theme_value = self.current_settings.get("ui/theme", "system")
            theme_index = self.theme_combo.findText(theme_value)
            if theme_index >= 0:
                self.theme_combo.setCurrentIndex(theme_index)
            
            language_value = self.current_settings.get("whisper/language", "auto")
            language_index = self.language_combo.findText(language_value)
            if language_index >= 0:
                self.language_combo.setCurrentIndex(language_index)
            
            engine_value = self.current_settings.get("whisper/engine", "faster")
            engine_index = self.engine_combo.findText(engine_value)
            if engine_index >= 0:
                self.engine_combo.setCurrentIndex(engine_index)
            
            # Behavior settings
            self.auto_paste_checkbox.setChecked(self.current_settings.get("behavior/auto_paste", True))
            self.toggle_mode_checkbox.setChecked(self.current_settings.get("behavior/toggle_mode", False))
            self.minimize_to_tray_checkbox.setChecked(self.current_settings.get("behavior/minimize_to_tray", False))
            self.visual_indicator_checkbox.setChecked(self.current_settings.get("behavior/visual_indicator", True))
            self.indicator_position_combo.setCurrentText(self.current_settings.get("behavior/indicator_position", "Bottom Center"))
            self.indicator_position_combo.setEnabled(self.visual_indicator_checkbox.isChecked())
            self.hotkey_combo.setCurrentText(self.current_settings.get("behavior/hotkey", "alt gr"))
            
            # Audio settings
            self.sound_effects_checkbox.setChecked(self.current_settings.get("audio/effects_enabled", True))
            self.start_tone_edit.setText(self.current_settings.get("audio/start_tone", "assets/sound_start_v9.wav"))
            self.stop_tone_edit.setText(self.current_settings.get("audio/stop_tone", "assets/sound_end_v9.wav"))
            
            # Initialize device list
            self.refresh_device_list(is_initial_load=True)
            
            # Transcription settings
            self.model_combo.setCurrentText(self.current_settings.get("whisper/model_name", "tiny"))
            self.speed_mode_checkbox.setChecked(self.current_settings.get("whisper/speed_mode", True))
            
            # Expert mode settings
            # Load expert mode setting (separate from temperature)
            expert_mode = self.current_settings.get("advanced/expert_mode", False)
            self.expert_mode_checkbox.setChecked(expert_mode)
            self.temperature_group.setVisible(expert_mode)
            
            # Load temperature setting
            temperature = self.current_settings.get("whisper/temperature", 0.0)
            self.temperature_slider.setValue(int(temperature * 100))
            self.temperature_label.setText(f"{temperature:.1f}")
            
            # Reconnect signals after loading is complete
            self._connect_signals()
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            # Ensure signals are reconnected even if loading fails
            self._connect_signals()
    
    def _disconnect_signals(self):
        """Disconnect all setting change signals to prevent triggering during load."""
        try:
            # Disconnect combo box signals
            self.theme_combo.currentTextChanged.disconnect()
            self.language_combo.currentTextChanged.disconnect()
            self.engine_combo.currentTextChanged.disconnect()
            self.indicator_position_combo.currentTextChanged.disconnect()
            self.hotkey_combo.currentTextChanged.disconnect()
            self.model_combo.currentTextChanged.disconnect()
            
            # Disconnect checkbox signals
            self.auto_paste_checkbox.stateChanged.disconnect()
            self.toggle_mode_checkbox.stateChanged.disconnect()
            self.minimize_to_tray_checkbox.stateChanged.disconnect()
            self.visual_indicator_checkbox.stateChanged.disconnect()
            self.sound_effects_checkbox.stateChanged.disconnect()
            self.speed_mode_checkbox.stateChanged.disconnect()
            self.expert_mode_checkbox.stateChanged.disconnect()
            
            # Disconnect line edit signals
            self.start_tone_edit.textChanged.disconnect()
            self.stop_tone_edit.textChanged.disconnect()
            
            # Disconnect slider signals
            self.temperature_slider.valueChanged.disconnect()
            
        except TypeError:
            # Signals were not connected, ignore
            pass
    
    def _connect_signals(self):
        """Reconnect all setting change signals after loading is complete."""
        # Connect combo box signals
        self.theme_combo.currentTextChanged.connect(self.on_setting_changed)
        self.language_combo.currentTextChanged.connect(self.on_setting_changed)
        self.engine_combo.currentTextChanged.connect(self.on_setting_changed)
        self.indicator_position_combo.currentTextChanged.connect(self.on_setting_changed)
        self.hotkey_combo.currentTextChanged.connect(self.on_setting_changed)
        self.model_combo.currentTextChanged.connect(self.on_setting_changed)
        
        # Connect checkbox signals
        self.auto_paste_checkbox.stateChanged.connect(self.on_setting_changed)
        self.toggle_mode_checkbox.stateChanged.connect(self.on_setting_changed)
        self.minimize_to_tray_checkbox.stateChanged.connect(self.on_setting_changed)
        self.visual_indicator_checkbox.stateChanged.connect(self.on_visual_indicator_changed)
        self.sound_effects_checkbox.stateChanged.connect(self.on_setting_changed)
        self.speed_mode_checkbox.stateChanged.connect(self.on_setting_changed)
        self.expert_mode_checkbox.stateChanged.connect(self.on_expert_mode_changed)
        
        # Connect line edit signals
        self.start_tone_edit.textChanged.connect(self.on_setting_changed)
        self.stop_tone_edit.textChanged.connect(self.on_setting_changed)
        
        # Connect slider signals
        self.temperature_slider.valueChanged.connect(self.on_temperature_changed)
    
    def reset_to_recommended(self):
        """Reset advanced settings to recommended values."""
        try:
            # Reset temperature to default
            self.temperature_slider.setValue(0)
            self.temperature_label.setText("0.0")
            self.settings_manager.set("whisper/temperature", 0.0)
            
            # Reset speed mode to default
            self.speed_mode_checkbox.setChecked(True)
            self.settings_manager.set("whisper/speed_mode", True)
            
            # Show confirmation
            QMessageBox.information(
                self,
                "Settings Reset",
                "Advanced settings have been reset to recommended values."
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Reset Error",
                f"Error resetting settings: {e}"
            )
    
    def on_setting_changed(self):
        """Handle setting changes and apply them immediately with validation."""
        try:
            # Get current values
            settings = {
                "ui/theme": self.theme_combo.currentText(),
                "whisper/language": self.language_combo.currentText(),
                "whisper/engine": self.engine_combo.currentText(),
                "behavior/auto_paste": self.auto_paste_checkbox.isChecked(),
                "behavior/toggle_mode": self.toggle_mode_checkbox.isChecked(),
                "behavior/minimize_to_tray": self.minimize_to_tray_checkbox.isChecked(),
                "behavior/visual_indicator": self.visual_indicator_checkbox.isChecked(),
                "behavior/indicator_position": self.indicator_position_combo.currentText(),
                "behavior/hotkey": self.hotkey_combo.currentText(),
                "audio/effects_enabled": self.sound_effects_checkbox.isChecked(),
                "audio/start_tone": self.start_tone_edit.text(),
                "audio/stop_tone": self.stop_tone_edit.text(),
                "whisper/model_name": self.model_combo.currentText(),
                "whisper/speed_mode": self.speed_mode_checkbox.isChecked(),
                "whisper/temperature": self.temperature_slider.value() / 100.0,
                "advanced/expert_mode": self.expert_mode_checkbox.isChecked(),
            }
            
            # Apply settings with validation
            failed_settings = []
            for key, value in settings.items():
                try:
                    self.settings_manager.set(key, value)
                except ValueError as e:
                    logger.error(f"Validation failed for setting '{key}' with value '{value}': {e}")
                    failed_settings.append((key, value, str(e)))
                except Exception as e:
                    logger.error(f"Unexpected error setting '{key}' to '{value}': {e}")
                    failed_settings.append((key, value, f"Unexpected error: {e}"))
            
            # Show error message if any settings failed validation
            if failed_settings:
                error_msg = "Some settings could not be saved due to validation errors:\n\n"
                for key, value, error in failed_settings:
                    error_msg += f"• {key}: {error}\n"
                error_msg += "\nThese settings have been reverted to their previous values."
                
                QMessageBox.warning(
                    self,
                    "Settings Validation Error",
                    error_msg
                )
            
            # Emit signal for live updates (only for successfully applied settings)
            if not failed_settings:
                self.settings_changed.emit(settings)
            
        except Exception as e:
            logger.error(f"Error applying setting change: {e}")
            QMessageBox.critical(
                self,
                "Settings Error",
                f"An unexpected error occurred while saving settings:\n{e}"
            )
    
    def on_temperature_changed(self):
        """Handle temperature slider changes."""
        temperature = self.temperature_slider.value() / 100.0
        self.temperature_label.setText(f"{temperature:.1f}")
        self.on_setting_changed()
    
    def on_expert_mode_changed(self):
        """Handle expert mode checkbox changes."""
        enabled = self.expert_mode_checkbox.isChecked()
        self.temperature_group.setVisible(enabled)
        
        # Save expert mode setting
        self.settings_manager.set("advanced/expert_mode", enabled)
        
        # If disabling expert mode, reset temperature to default
        if not enabled:
            self.temperature_slider.setValue(0)
            self.temperature_label.setText("0.0")
            self.settings_manager.set("whisper/temperature", 0.0)
    
    def on_visual_indicator_changed(self):
        """Handle visual indicator checkbox changes."""
        enabled = self.visual_indicator_checkbox.isChecked()
        self.indicator_position_combo.setEnabled(enabled)
        self.on_setting_changed()
    
    def browse_tone_file(self, tone_type: str):
        """Browse for tone file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {tone_type} tone file",
            "assets",
            "Audio Files (*.wav *.mp3 *.ogg);;All Files (*)"
        )
        
        if file_path:
            if tone_type == "start":
                self.start_tone_edit.setText(file_path)
            else:
                self.stop_tone_edit.setText(file_path)
            self.on_setting_changed()
    
    def test_tone(self, tone_type: str):
        """Test the selected tone file."""
        try:
            tone_path = self.start_tone_edit.text() if tone_type == "start" else self.stop_tone_edit.text()
            
            if not tone_path or not os.path.exists(tone_path):
                QMessageBox.warning(self, "File Not Found", f"The {tone_type} tone file was not found.")
                return
            
            # Create and play sound effect
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(tone_path))
            effect.setVolume(0.5)
            effect.play()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to play {tone_type} tone: {e}")
    
    def restore_defaults(self):
        """Restore all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to their default values?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.settings_manager.restore_defaults()
                self.current_settings = self.settings_manager.load_all()
                self.load_settings()
                
                QMessageBox.information(self, "Defaults Restored", "All settings have been restored to their default values.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to restore defaults: {e}")
    
    def refresh_device_list(self, is_initial_load=False):
        """
        Refresh the device list using consolidated devices and update UI.
        
        This method uses the AudioManager's consolidation feature to group
        duplicate Windows device configurations into clean, user-friendly
        device names while maintaining mapping to original device indices.
        
        Args:
            is_initial_load: If True, auto-selects the previously saved device
        """
        try:
            # Get consolidated devices from controller
            if hasattr(self.parent(), 'controller') and hasattr(self.parent().controller, 'audio_manager'):
                audio_manager = self.parent().controller.audio_manager
                consolidated_devices, display_to_original_map = audio_manager.get_consolidated_devices()
                
                # Store mapping for later use in device selection
                self.device_display_to_original_map = display_to_original_map
            else:
                consolidated_devices = []
                self.device_display_to_original_map = {}
            
            # Clear existing items
            self.device_combo.clear()
            
            if not consolidated_devices:
                # No devices available
                self.device_combo.addItem("No devices detected")
                self.device_combo.setEnabled(False)
                self.test_device_button.setEnabled(False)
                self.no_device_warning.show()
                return
            
            # Add devices to combo box
            current_device_index = self.current_settings.get("audio/input_device", None)
            current_device_name = self.current_settings.get("audio/input_device_name", "System Default")
            
            # Add system default option
            self.device_combo.addItem("System Default")
            
            # Add consolidated devices with clean display names
            for device in consolidated_devices:
                self.device_combo.addItem(device['display_name'])
            
            # Only auto-select on initial load, not on refresh
            if is_initial_load:
                if current_device_index is None:
                    # System default
                    self.device_combo.setCurrentIndex(0)
                else:
                    # Find matching device in consolidated list using original index
                    for i, device in enumerate(consolidated_devices):
                        if device['original_index'] == current_device_index:
                            self.device_combo.setCurrentIndex(i + 1)  # +1 because index 0 is "System Default"
                            break
                    else:
                        # Device not found, use system default
                        self.device_combo.setCurrentIndex(0)
            # On refresh, don't auto-select anything - let user choose manually
            
            # Update UI state
            self.device_combo.setEnabled(True)
            self.test_device_button.setEnabled(True)
            self.no_device_warning.hide()
            
            logger.info(f"Refreshed device list: {len(consolidated_devices)} consolidated devices")
            
        except Exception as e:
            logger.error(f"Error refreshing device list: {e}")
    
    
    def on_device_changed(self):
        """
        Handle device selection change using consolidated device mapping.
        
        This method maps the display index (from consolidated device list) to the
        original device index needed for actual audio operations.
        """
        try:
            selected_index = self.device_combo.currentIndex()
            
            if selected_index == 0:
                # System default selected
                device_index = None
                device_name = "System Default"
            else:
                # Specific device selected - map display index to original index
                display_device_index = selected_index - 1  # -1 because index 0 is "System Default"
                
                if hasattr(self, 'device_display_to_original_map') and self.device_display_to_original_map:
                    if display_device_index in self.device_display_to_original_map:
                        device_index = self.device_display_to_original_map[display_device_index]
                        device_name = self.device_combo.currentText()
                    else:
                        logger.warning(f"Display device index {display_device_index} not found in mapping")
                        return
                else:
                    logger.warning("Device mapping not available")
                    return
            
            # Save settings
            # Handle None device_index (System Default) properly
            if device_index is None:
                self.settings_manager.set("audio/input_device", None)
            else:
                self.settings_manager.set("audio/input_device", device_index)
            self.settings_manager.set("audio/input_device_name", device_name)
            
            # Apply to controller
            if hasattr(self.parent(), 'controller'):
                success = self.parent().controller.set_audio_device(device_index)
                if success:
                    logger.info(f"Successfully switched to device: {device_name} (index: {device_index})")
                else:
                    logger.warning(f"Failed to switch to device: {device_name}")
            
            # Update current settings
            self.current_settings["audio/input_device"] = device_index
            self.current_settings["audio/input_device_name"] = device_name
            
        except Exception as e:
            logger.error(f"Error changing device: {e}")
    
    def test_selected_device(self):
        """
        Test the selected audio device with real-time audio level feedback.
        
        Uses the consolidated device mapping to test the correct underlying
        device configuration.
        """
        try:
            selected_index = self.device_combo.currentIndex()
            
            if selected_index == 0:
                # System default
                device_index = None
                device_name = "System Default"
            else:
                # Specific device - map display index to original index
                display_device_index = selected_index - 1  # -1 because index 0 is "System Default"
                
                if hasattr(self, 'device_display_to_original_map') and self.device_display_to_original_map:
                    if display_device_index in self.device_display_to_original_map:
                        device_index = self.device_display_to_original_map[display_device_index]
                        device_name = self.device_combo.currentText()
                    else:
                        QMessageBox.warning(self, "Test Failed", "Selected device mapping not found.")
                        return
                else:
                    QMessageBox.warning(self, "Test Failed", "Device mapping not available.")
                    return
            
            # Show test dialog with real-time audio level feedback
            self._show_audio_test_dialog(device_index, device_name)
                
        except Exception as e:
            logger.error(f"Error testing device: {e}")
            QMessageBox.critical(self, "Test Error", f"Error testing device: {e}")
    
    def _show_audio_test_dialog(self, device_index, device_name):
        """Show a dialog for testing audio device with real-time level feedback."""
        
        # Create test dialog
        test_dialog = QDialog(self)
        test_dialog.setWindowTitle(f"Testing: {device_name}")
        test_dialog.setModal(True)
        test_dialog.setFixedSize(400, 200)
        
        layout = self.create_vertical_layout(15)
        layout.setContentsMargins(20, 20, 20, 20)
        test_dialog.setLayout(layout)
        
        # Title
        title_label = QLabel(f"Testing Microphone: {device_name}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Instructions
        instructions_label = QLabel("Speak into your microphone to test audio levels:")
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(instructions_label)
        
        # Audio level display
        level_layout = self.create_vertical_layout()
        
        level_label = QLabel("Audio Level:")
        level_label.setAlignment(Qt.AlignCenter)
        level_layout.addWidget(level_label)
        
        # Progress bar for audio level
        self.test_level_bar = QProgressBar()
        self.test_level_bar.setRange(0, 100)
        self.test_level_bar.setValue(0)
        self.test_level_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:0.7 #FFC107, stop:1 #F44336);
                border-radius: 6px;
            }
        """)
        level_layout.addWidget(self.test_level_bar)
        
        # Level value label
        self.test_level_value = QLabel("0%")
        self.test_level_value.setAlignment(Qt.AlignCenter)
        self.test_level_value.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        level_layout.addWidget(self.test_level_value)
        
        layout.addLayout(level_layout)
        
        # Status label
        self.test_status_label = QLabel("Click 'Start Test' to begin...")
        self.test_status_label.setAlignment(Qt.AlignCenter)
        self.test_status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.test_status_label)
        
        # Buttons
        button_layout = self.create_horizontal_layout()
        button_layout.addStretch()
        
        self.start_test_button = QPushButton("Start Test")
        self.start_test_button.clicked.connect(lambda: self._start_audio_test(test_dialog, device_index))
        button_layout.addWidget(self.start_test_button)
        
        self.stop_test_button = QPushButton("Stop Test")
        self.stop_test_button.clicked.connect(lambda: self._stop_audio_test(test_dialog))
        self.stop_test_button.setEnabled(False)
        button_layout.addWidget(self.stop_test_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(test_dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Store dialog reference for cleanup
        self.test_dialog = test_dialog
        self.test_timer = None
        self.test_audio_level_callback = None
        
        # Show dialog
        test_dialog.exec_()
    
    def _start_audio_test(self, dialog, device_index):
        """Start the audio test with real-time level monitoring."""
        try:
            # Get audio manager
            if not hasattr(self.parent(), 'controller') or not hasattr(self.parent().controller, 'audio_manager'):
                QMessageBox.warning(dialog, "Test Failed", "Audio controller not available.")
                return
            
            audio_manager = self.parent().controller.audio_manager
            
            # Set up audio level callback
            self.test_audio_level_callback = lambda level: self._update_test_level(level)
            audio_manager.set_callbacks(on_audio_level=self.test_audio_level_callback)
            
            # Start recording for level monitoring
            success = audio_manager.start_recording()
            if not success:
                QMessageBox.warning(dialog, "Test Failed", "Failed to start audio recording.")
                return
            
            # Update UI
            self.start_test_button.setEnabled(False)
            self.stop_test_button.setEnabled(True)
            self.test_status_label.setText("Listening... Speak into your microphone!")
            self.test_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            # Start timer for periodic updates
            self.test_timer = QTimer()
            self.test_timer.timeout.connect(lambda: self._update_test_status())
            self.test_timer.start(100)  # Update every 100ms
            
        except Exception as e:
            logger.error(f"Error starting audio test: {e}")
            QMessageBox.critical(dialog, "Test Error", f"Error starting test: {e}")
    
    def _stop_audio_test(self, dialog):
        """Stop the audio test."""
        try:
            # Stop timer
            if self.test_timer:
                self.test_timer.stop()
                self.test_timer = None
            
            # Stop recording
            if hasattr(self.parent(), 'controller') and hasattr(self.parent().controller, 'audio_manager'):
                audio_manager = self.parent().controller.audio_manager
                audio_manager.stop_recording()
                
                # Clear callbacks
                audio_manager.set_callbacks(on_audio_level=None)
            
            # Update UI
            self.start_test_button.setEnabled(True)
            self.stop_test_button.setEnabled(False)
            self.test_status_label.setText("Test stopped.")
            self.test_status_label.setStyleSheet("color: #666; font-style: italic;")
            
            # Reset level display
            self.test_level_bar.setValue(0)
            self.test_level_value.setText("0%")
            
        except Exception as e:
            logger.error(f"Error stopping audio test: {e}")
    
    def _update_test_level(self, level):
        """Update the audio level display during test."""
        try:
            # Convert level to percentage (level is typically 0.0 to 1.0)
            percentage = int(level * 100)
            percentage = max(0, min(100, percentage))  # Clamp to 0-100
            
            # Update progress bar
            self.test_level_bar.setValue(percentage)
            
            # Update value label
            self.test_level_value.setText(f"{percentage}%")
            
            # Update color based on level
            if percentage < 20:
                color = "#4CAF50"  # Green - low level
            elif percentage < 70:
                color = "#FFC107"  # Yellow - medium level
            else:
                color = "#F44336"  # Red - high level
            
            self.test_level_value.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {color};")
            
        except Exception as e:
            logger.error(f"Error updating test level: {e}")
    
    def _update_test_status(self):
        """Update test status during monitoring."""
        try:
            current_level = self.test_level_bar.value()
            
            if current_level > 0:
                if current_level < 10:
                    status = "Very quiet - try speaking louder"
                elif current_level < 30:
                    status = "Good level - microphone is working!"
                elif current_level < 70:
                    status = "Good level - microphone is working well!"
                else:
                    status = "Very loud - consider moving away from microphone"
                
                self.test_status_label.setText(status)
                
                # Update status color
                if current_level < 10:
                    self.test_status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
                elif current_level < 70:
                    self.test_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                else:
                    self.test_status_label.setStyleSheet("color: #F44336; font-weight: bold;")
            else:
                self.test_status_label.setText("No audio detected - check microphone connection")
                self.test_status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
                
        except Exception as e:
            logger.error(f"Error updating test status: {e}")
    
    def setup_responsive_geometry(self):
        """Set up responsive dialog geometry using centralized system."""
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
        
        # Calculate responsive dialog dimensions using new responsive system
        dialog_width, dialog_height = ResponsiveSizing.calculate_dialog_size(
            screen_width, screen_height
        )
        
        # Set minimum and maximum sizes for comfortable design
        min_width = max(600, int(screen_width * 0.40))
        min_height = max(500, int(screen_height * 0.40))
        max_width = min(1200, int(screen_width * 0.90))
        max_height = min(1000, int(screen_height * 0.90))
        
        self.setMinimumSize(min_width, min_height)
        self.setMaximumSize(max_width, max_height)
        
        # Center the dialog on the appropriate screen
        if screen is not None:
            screen_geometry = screen.availableGeometry()
            x = screen_geometry.x() + (screen_geometry.width() - dialog_width) // 2
            y = screen_geometry.y() + (screen_geometry.height() - dialog_height) // 2
        else:
            # Fallback centering
            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2
        
        # Ensure dialog stays within screen bounds
        x = max(screen_geometry.x() if screen else 0, x)
        y = max(screen_geometry.y() if screen else 0, y)
        
        self.setGeometry(x, y, dialog_width, dialog_height)
