"""
Record Tab using new layout system and base components.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
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
        
        # Get responsive spacing values
        top_spacing = AdaptiveSpacing.get_spacing(20)  # Fixed top spacing
        animation_spacing = AdaptiveSpacing.get_spacing(1)  # Small spacing (reduced from 2)
        button_spacing = AdaptiveSpacing.get_spacing(40)  # Visible spacing between mic and buttons
        bottom_spacing = AdaptiveSpacing.get_spacing(0)  # Minimal bottom spacing
        
        
        # Add responsive spacer at top - FIXED instead of Expanding to allow spacing to work
        top_spacer = QSpacerItem(20, top_spacing, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.main_layout.addItem(top_spacer)
        
        # Animated circle (now responsive) - centered using horizontal layout
        self.animation_circle = AnimationCircleWidget()
        
        # Create horizontal layout for proper centering
        circle_h_layout = QHBoxLayout()
        circle_h_layout.setSpacing(0)
        circle_h_layout.setContentsMargins(0, 0, 0, 0)
        circle_h_layout.addStretch()
        circle_h_layout.addWidget(self.animation_circle)
        circle_h_layout.addStretch()
        
        self.main_layout.addLayout(circle_h_layout)
        
        # Add spacing between animation circle and buttons using a fixed-height widget
        spacer_widget = QWidget()
        spacer_widget.setMinimumHeight(button_spacing)
        spacer_widget.setMaximumHeight(button_spacing)
        spacer_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        spacer_widget.setStyleSheet("background-color: transparent;")
        self.main_layout.addWidget(spacer_widget)
        
        # Single contextual record button — disabled until model is ready
        self.record_button = ActionButton("Start Recording", "primary")
        self.record_button.setObjectName("RecordButton")
        self.record_button.setEnabled(False)  # disabled while model loads
        self._recording = False

        # Centre the button
        button_h_layout = QHBoxLayout()
        button_h_layout.addStretch()
        button_h_layout.addWidget(self.record_button)
        button_h_layout.addStretch()

        self.main_layout.addLayout(button_h_layout)

        # Wire button event
        self.record_button.clicked.connect(self._on_record)
        
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
        
        # Add responsive bottom spacer with expanding height to balance the layout
        bottom_spacer = QSpacerItem(20, bottom_spacing, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addItem(bottom_spacer)
        
    def update_status(self, status: str):
        """Update the status display."""
        self.status_label.setText(status)
        
        # Update animation circle based on status
        if "Recording" in status:
            self.animation_circle.set_recording(True)
        elif "Processing" in status:
            self.animation_circle.set_recording(False)
            self.animation_circle.set_processing(True)
        else:
            self.animation_circle.set_recording(False)
            self.animation_circle.set_processing(False)
    
    def set_state(self, state: str) -> None:
        """Drive the single record button.

        state: 'loading' | 'idle' | 'recording'
        """
        if state == "recording":
            self._recording = True
            self.record_button.setText("Stop Recording")
            self.record_button.setEnabled(True)
            self.animation_circle.set_recording(True)
        elif state == "loading":
            self._recording = False
            self.record_button.setText("Start Recording")
            self.record_button.setEnabled(False)
            self.animation_circle.set_recording(False)
        else:  # idle / processing
            self._recording = False
            self.record_button.setText("Start Recording")
            self.record_button.setEnabled(True)
            self.animation_circle.set_recording(False)

    def update_feature_availability(self):
        """Update UI elements based on feature availability"""
        if not hasattr(self.parent_app, 'controller'):
            return
        feature_status = self.parent_app.controller.get_feature_status()
        if not feature_status.get("audio_recording", False):
            self.record_button.setEnabled(False)
            self.record_button.setToolTip("Audio recording not available on this platform")

    def _on_record(self):
        """Toggle recording on button click."""
        if self._recording:
            self.parent_app.stop_recording()
        else:
            self.parent_app.start_recording()
    
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
