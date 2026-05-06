"""
Record Tab using new layout system and base components.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseTab, StatusDisplay, ActionButton, ButtonGroup, InfoPanel, AnimationCircleWidget
from ui.layout_system import (LayoutBuilder, LayoutTokens, ColorTokens, 
                             ResponsiveFontSize, AdaptiveSpacing, DPIScalingHelper)
from ui.styles.main_styles import MainStyles


class RecordTab(BaseTab):
    """Record tab using new layout system and base components."""

    def __init__(self, parent_app):
        self.parent_app = parent_app
        super().__init__(parent_app)
        # Override the base layout with responsive spacing
        responsive_spacing = AdaptiveSpacing.get_spacing(LayoutTokens.SPACING_XS)
        self.main_layout.setSpacing(responsive_spacing)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def init_content(self):
        """Initialize the record tab content using responsive layout system."""
        from PyQt5.QtWidgets import QSpacerItem, QSizePolicy

        self._is_recording = False

        # Get responsive spacing values
        animation_spacing = AdaptiveSpacing.get_spacing(1)
        button_spacing = AdaptiveSpacing.get_spacing(20)

        # Expanding top spacer — pushes content to vertical center together with bottom spacer
        top_spacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addItem(top_spacer)
        
        # Animated circle (now responsive) - centered using horizontal layout
        self.animation_circle = AnimationCircleWidget()

        # Loading mascot shown while the Whisper model preloads
        from ui.widgets.loading_mascot_widget import LoadingMascotWidget
        self.mascot_widget = LoadingMascotWidget()

        # Stack: index 0 = mascot (startup), index 1 = circle (ready)
        self._circle_stack = QStackedWidget()
        self._circle_stack.addWidget(self.mascot_widget)
        self._circle_stack.addWidget(self.animation_circle)
        self._circle_stack.setCurrentIndex(0)

        # Create horizontal layout for proper centering
        circle_h_layout = QHBoxLayout()
        circle_h_layout.setSpacing(0)
        circle_h_layout.setContentsMargins(0, 0, 0, 0)
        circle_h_layout.addStretch()
        circle_h_layout.addWidget(self._circle_stack)
        circle_h_layout.addStretch()
        
        self.main_layout.addLayout(circle_h_layout)
        
        # Add spacing between animation circle and buttons using a fixed-height widget
        spacer_widget = QWidget()
        spacer_widget.setMinimumHeight(button_spacing)
        spacer_widget.setMaximumHeight(button_spacing)
        spacer_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        spacer_widget.setStyleSheet("background-color: transparent;")
        self.main_layout.addWidget(spacer_widget)
        
        # Single toggle button — label and style change with recording state
        self.record_button = ActionButton("Start", "primary")
        self.record_button.setObjectName("RecordButton")
        self.record_button.setFixedHeight(49)
        self.record_button.setMinimumWidth(180)

        # Button group - centered using horizontal layout
        responsive_button_spacing = AdaptiveSpacing.get_spacing(LayoutTokens.SPACING_MD)
        button_group = ButtonGroup([self.record_button], responsive_button_spacing)

        button_h_layout = QHBoxLayout()
        button_h_layout.addStretch()
        button_h_layout.addWidget(button_group)
        button_h_layout.addStretch()

        self.main_layout.addLayout(button_h_layout)

        # Wire toggle from button and from circle click
        self.record_button.clicked.connect(self._on_toggle_recording)
        self.animation_circle.clicked.connect(self._on_toggle_recording)
        
        # Add responsive spacer between buttons and status text
        buttons_to_status_spacer = QSpacerItem(20, animation_spacing, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.main_layout.addItem(buttons_to_status_spacer)
        
        # Status text below buttons with responsive font
        self.status_label = QLabel("Idle")
        self.status_label.setAlignment(Qt.AlignCenter)
        responsive_font_size = ResponsiveFontSize.get_font_size('lg')
        self.status_label.setStyleSheet(f"color: {ColorTokens.TEXT_SECONDARY}; font-family: \"Inter\",\"Segoe UI\",system-ui,-apple-system; font-size: {responsive_font_size}px; font-weight: 400;")
        self.main_layout.addWidget(self.status_label)
        
        # Add responsive spacer between status and hotkey instruction
        status_to_instruction_spacer = QSpacerItem(20, animation_spacing, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.main_layout.addItem(status_to_instruction_spacer)
        
        # Hotkey instruction with responsive font
        self.hotkey_instruction_label = QLabel("Press AltGr (or your configured hotkey) to start recording.")
        self.hotkey_instruction_label.setAlignment(Qt.AlignCenter)
        instruction_font_size = ResponsiveFontSize.get_font_size('md')
        self.hotkey_instruction_label.setFont(QFont("Inter", instruction_font_size))
        self.hotkey_instruction_label.setStyleSheet(f"color: {ColorTokens.TEXT_SECONDARY}; font-family: \"Inter\",\"Segoe UI\",system-ui,-apple-system; font-style: italic; font-size: {instruction_font_size}px; font-weight: 400;")
        self.main_layout.addWidget(self.hotkey_instruction_label)
        
        # Expanding bottom spacer — mirrors top spacer to vertically center all content
        bottom_spacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addItem(bottom_spacer)
        
    def set_loading_mode(self, loading: bool) -> None:
        """Switch between loading mascot (True) and the animation circle (False)."""
        if loading:
            self._circle_stack.setCurrentIndex(0)
        else:
            def _swap():
                self._circle_stack.setCurrentIndex(1)

            self.mascot_widget.finished.connect(_swap)
            self.mascot_widget.stop_and_hide()

    def update_status(self, status: str):
        """Update the status display and sync button/circle to external state changes."""
        self.status_label.setText(status)

        active = "Recording" in status and "failed" not in status.lower()

        if active:
            self.animation_circle.set_recording(True)
            if not self._is_recording:
                self._is_recording = True
                self._apply_recording_button_style()
        elif "Processing" in status:
            self.animation_circle.set_recording(False)
            self.animation_circle.set_processing(True)
        else:
            self.animation_circle.set_recording(False)
            self.animation_circle.set_processing(False)
            if self._is_recording:
                self._is_recording = False
                self._apply_idle_button_style()
    
    def update_feature_availability(self):
        """Update UI elements based on feature availability"""
        if not hasattr(self.parent_app, 'controller'):
            return

        feature_status = self.parent_app.controller.get_feature_status()

        if not feature_status.get("audio_recording", False):
            self.record_button.setEnabled(False)
            self.record_button.setToolTip("Audio recording not available on this platform")
        else:
            self.record_button.setEnabled(True)
            self.record_button.setToolTip("Click or press hotkey to start recording")

    def set_recording_active(self, active: bool, processing: bool = False):
        """Sync button and circle from external controller state changes."""
        self._is_recording = active
        if active:
            self.animation_circle.set_recording(True)
            self.animation_circle.set_processing(False)
            self._apply_recording_button_style()
            self.record_button.setEnabled(True)
        elif processing:
            self.animation_circle.set_recording(False)
            self.animation_circle.set_processing(True)
            self._apply_idle_button_style()
            self.record_button.setEnabled(False)
        else:
            self.animation_circle.set_recording(False)
            self.animation_circle.set_processing(False)
            self._apply_idle_button_style()
            self.record_button.setEnabled(True)

    def _on_toggle_recording(self):
        """Toggle recording on/off from button or circle click."""
        if self._is_recording:
            self._on_stop()
        else:
            self._on_start()

    def _on_start(self):
        self._is_recording = True
        self.parent_app.start_recording()
        self.animation_circle.set_recording(True)
        self._apply_recording_button_style()

    def _on_stop(self):
        self._is_recording = False
        self.parent_app.stop_recording()
        self.animation_circle.set_recording(False)
        self._apply_idle_button_style()

    def _apply_recording_button_style(self):
        self.record_button.setText("Stop")
        self.record_button.button_type = "recording"
        self.record_button.init_styling()

    def _apply_idle_button_style(self):
        self.record_button.setText("Start")
        self.record_button.button_type = "primary"
        self.record_button.init_styling()
    
    def show_feature_recommendations(self, recommendations):
        """Show recommendations for missing features"""
        # This could be expanded to show a notification or dialog
        # For now, just log the recommendations
        install_packages = recommendations.get("install_packages", [])
        enable_permissions = recommendations.get("enable_permissions", [])
        
        if install_packages:
            print(f"Missing packages: {', '.join(install_packages)}")
        if enable_permissions:
            for perm in enable_permissions:
                print(f"Permission required: {perm.get('description', 'Unknown')}")
