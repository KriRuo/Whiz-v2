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
        
        # Animated circle (now responsive) - wrapped in container for proper centering
        self.animation_circle = AnimationCircleWidget()
        
        # Create a container widget to ensure proper horizontal centering
        circle_container = QWidget()
        circle_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        circle_layout = QHBoxLayout(circle_container)
        circle_layout.setContentsMargins(0, 0, 0, 0)
        circle_layout.setSpacing(0)
        circle_layout.addStretch(1)  # Equal stretch before
        circle_layout.addWidget(self.animation_circle, alignment=Qt.AlignCenter)
        circle_layout.addStretch(1)  # Equal stretch after
        
        self.main_layout.addWidget(circle_container, 0, Qt.AlignHCenter)
        
        # Add spacing between animation circle and buttons using a fixed-height widget
        spacer_widget = QWidget()
        spacer_widget.setMinimumHeight(button_spacing)
        spacer_widget.setMaximumHeight(button_spacing)
        spacer_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        spacer_widget.setStyleSheet("background-color: transparent;")
        self.main_layout.addWidget(spacer_widget)
        
        # Action buttons using new components with dark theme styling
        self.start_button = ActionButton("Start Recording", "primary")
        self.start_button.setObjectName("StartButton")
        self.stop_button = ActionButton("Stop Recording", "secondary")
        self.stop_button.setObjectName("StopButton")
        self.stop_button.setEnabled(False)
        
        # Button group with responsive spacing - wrapped in container for centering
        responsive_button_spacing = AdaptiveSpacing.get_spacing(LayoutTokens.SPACING_MD)
        button_group = ButtonGroup([self.start_button, self.stop_button], responsive_button_spacing)
        
        # Create a container widget to ensure proper horizontal centering of buttons
        button_container = QWidget()
        button_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        button_container_layout = QHBoxLayout(button_container)
        button_container_layout.setContentsMargins(0, 0, 0, 0)
        button_container_layout.setSpacing(0)
        button_container_layout.addStretch(1)  # Equal stretch before
        button_container_layout.addWidget(button_group, alignment=Qt.AlignCenter)
        button_container_layout.addStretch(1)  # Equal stretch after
        
        self.main_layout.addWidget(button_container, 0, Qt.AlignHCenter)
        
        # Wire button events
        self.start_button.clicked.connect(self._on_start)
        self.stop_button.clicked.connect(self._on_stop)
        
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
    
    def update_feature_availability(self):
        """Update UI elements based on feature availability"""
        if not hasattr(self.parent_app, 'controller'):
            return
        
        feature_status = self.parent_app.controller.get_feature_status()
        
        # Update recording button availability
        if not feature_status.get("audio_recording", False):
            self.start_button.setEnabled(False)
            self.start_button.setToolTip("Audio recording not available on this platform")
        else:
            self.start_button.setEnabled(True)
            self.start_button.setToolTip("Start recording audio")

    def _on_start(self):
        """Handle start recording button click."""
        self.parent_app.start_recording()
        self.animation_circle.set_recording(True)  # Start pulse animation
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def _on_stop(self):
        """Handle stop recording button click."""
        self.parent_app.stop_recording()
        self.animation_circle.set_recording(False)  # Stop pulse animation
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
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
