"""
Example: Refactored Preferences Dialog Tab using Unified Components

This file demonstrates how to refactor preferences dialog tabs using
the new SettingsSection and InfoLabel components.
"""

from PyQt5.QtWidgets import QWidget, QComboBox, QCheckBox
from ui.components import SettingsSection, InfoLabel
from ui.layout_system import LayoutTokens


class RefactoredGeneralTab:
    """
    Example of the General tab refactored to use unified components.
    
    Compare this with the original create_general_tab method in
    preferences_dialog.py (lines 376-446).
    """
    
    def create_general_tab_refactored(self):
        """
        Create the General tab using unified components.
        
        BENEFITS:
        - 30% less code
        - No repetitive styling
        - Better maintainability
        - Guaranteed consistency
        """
        tab = QWidget()
        layout = self.create_tab_layout(tab)
        
        # ===== UI Settings Section =====
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
        
        # ===== Language Settings Section =====
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
        
        # ===== Engine Settings Section =====
        engine_section = SettingsSection("Transcription Engine", layout_type="form")
        
        # Engine selection
        self.engine_combo = self.create_styled_combobox(["faster", "openai"])
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


class RefactoredBehaviorTab:
    """
    Example of the Behavior tab refactored to use unified components.
    
    Compare this with the original create_behavior_tab method in
    preferences_dialog.py (lines 448-538).
    """
    
    def create_behavior_tab_refactored(self):
        """
        Create the Behavior tab using unified components.
        
        BENEFITS:
        - Cleaner structure
        - Consistent visual hierarchy
        - Easier to scan and understand
        """
        tab = QWidget()
        layout = self.create_tab_layout(tab)
        
        # ===== Recording Behavior Section =====
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
        
        # ===== Visual Indicator Section =====
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
        
        # ===== Hotkey Settings Section =====
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


class RefactoredTranscriptionTab:
    """
    Example of the Transcription tab refactored to use unified components.
    
    Compare this with the original create_transcription_tab method in
    preferences_dialog.py (lines 622-672).
    """
    
    def create_transcription_tab_refactored(self):
        """
        Create the Transcription tab using unified components.
        
        BENEFITS:
        - Vertical layout example
        - Shows different layout types
        - Simpler structure
        """
        tab = QWidget()
        layout = self.create_tab_layout(tab)
        
        # ===== Whisper Settings Section =====
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
        
        # ===== Performance Settings Section (vertical layout example) =====
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


# ===== CODE COMPARISON =====

"""
BEFORE (Original Method):
- Lines of code: ~70 per tab (average)
- Repetitive QGroupBox() + create_group_layout() calls
- Inline stylesheets for every info label
- 6+ lines per info label

AFTER (Refactored with Unified Components):
- Lines of code: ~50 per tab (average)
- Clean SettingsSection() calls
- Single-line InfoLabel() creation
- 1 line per info label

REDUCTION: ~30% less code, 100% more maintainable
"""

# ===== STYLING CONSISTENCY =====

"""
BEFORE:
If you want to change info label styling, you need to:
1. Find all info labels across all tabs (13+ locations)
2. Update each inline stylesheet individually
3. Risk missing some and creating inconsistency

AFTER:
If you want to change info label styling, you need to:
1. Update InfoLabel.apply_styling() method once
2. All info labels automatically update
3. Zero risk of inconsistency
"""

# ===== READABILITY COMPARISON =====

"""
BEFORE:
    info = QLabel("Text")
    info.setWordWrap(True)
    info.setStyleSheet(f"color: {ColorTokens.TEXT_SECONDARY}; font-size: 12px; padding: 12px; background-color: transparent; border-radius: 6px;")
    
    # Hard to scan, lots of visual noise, purpose unclear at first glance

AFTER:
    info = InfoLabel("Text")
    
    # Immediately clear this is an info label
    # Semantic naming improves readability
    # Styling is implied and consistent
"""

