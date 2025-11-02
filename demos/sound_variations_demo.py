#!/usr/bin/env python3
"""
Comprehensive test script to preview all sound effect variations
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QGroupBox, QScrollArea, QGridLayout)
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSoundEffect

class SoundVariationTestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.sounds = {}
        self.init_ui()
        self.init_sounds()
        
    def init_ui(self):
        self.setWindowTitle("Sound Effect Variations Test")
        self.setGeometry(300, 300, 900, 700)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Sound Effect Variations Review")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #004E92;")
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel("Click buttons to test different sound effect variations. Choose your favorite!")
        desc.setStyleSheet("margin: 10px; color: #666; font-size: 12px;")
        main_layout.addWidget(desc)
        
        # Create scrollable area for all variations
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: #FAFAFA;
            }
        """)
        
        # Container widget for all variations
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setSpacing(15)
        
        # Original sounds
        original_group = self.create_sound_group(
            "Original (Current)", 
            "sound_start.wav", "sound_end.wav",
            "Gentle ascending/descending tones (300-400Hz)",
            "#4CAF50"
        )
        container_layout.addWidget(original_group)
        
        # Variation 1: Deep Bass
        v1_group = self.create_sound_group(
            "Variation 1: Deep Bass", 
            "sound_start_v1.wav", "sound_end_v1.wav",
            "Deep bass tones (150-200Hz) - Longer duration",
            "#2196F3"
        )
        container_layout.addWidget(v1_group)
        
        # Variation 2: Mid-Range Extended
        v2_group = self.create_sound_group(
            "Variation 2: Mid-Range Extended", 
            "sound_start_v2.wav", "sound_end_v2.wav",
            "Mid-range tones (400-600Hz) - Extended duration",
            "#FF9800"
        )
        container_layout.addWidget(v2_group)
        
        # Variation 3: High-Pitched Quick
        v3_group = self.create_sound_group(
            "Variation 3: High-Pitched Quick", 
            "sound_start_v3.wav", "sound_end_v3.wav",
            "High-pitched tones (800-1000Hz) - Quick fade",
            "#9C27B0"
        )
        container_layout.addWidget(v3_group)
        
        # Variation 4: Bell-Like
        v4_group = self.create_sound_group(
            "Variation 4: Bell-Like", 
            "sound_start_v4.wav", "sound_end_v4.wav",
            "Bell-like tones (500-700Hz) - Rich harmonics",
            "#795548"
        )
        container_layout.addWidget(v4_group)
        
        # Variation 5: Electronic Beep
        v5_group = self.create_sound_group(
            "Variation 5: Electronic Beep", 
            "sound_start_v5.wav", "sound_end_v5.wav",
            "Electronic beep tones (600-800Hz) - Quick attack/release",
            "#607D8B"
        )
        container_layout.addWidget(v5_group)
        
        # NEW BASS VARIATIONS
        
        # Variation 6: Ultra Deep Bass
        v6_group = self.create_sound_group(
            "Variation 6: Ultra Deep Bass", 
            "sound_start_v6.wav", "sound_end_v6.wav",
            "Ultra deep bass tones (80-120Hz) - Very short duration",
            "#3F51B5"
        )
        container_layout.addWidget(v6_group)
        
        # Variation 7: Warm Bass
        v7_group = self.create_sound_group(
            "Variation 7: Warm Bass", 
            "sound_start_v7.wav", "sound_end_v7.wav",
            "Warm bass tones (180-250Hz) - Rich harmonics",
            "#E91E63"
        )
        container_layout.addWidget(v7_group)
        
        # Variation 8: Punchy Bass
        v8_group = self.create_sound_group(
            "Variation 8: Punchy Bass", 
            "sound_start_v8.wav", "sound_end_v8.wav",
            "Punchy bass tones (200-280Hz) - Quick attack",
            "#00BCD4"
        )
        container_layout.addWidget(v8_group)
        
        # Variation 9: Sub Bass
        v9_group = self.create_sound_group(
            "Variation 9: Sub Bass", 
            "sound_start_v9.wav", "sound_end_v9.wav",
            "Sub bass tones (60-100Hz) - Very low frequency",
            "#8BC34A"
        )
        container_layout.addWidget(v9_group)
        
        # Variation 10: Bass Click
        v10_group = self.create_sound_group(
            "Variation 10: Bass Click", 
            "sound_start_v10.wav", "sound_end_v10.wav",
            "Bass click tones (150-200Hz) - Click-like character",
            "#FF5722"
        )
        container_layout.addWidget(v10_group)
        
        # Instructions
        instructions = QLabel("""
        <b>Instructions:</b><br>
        • Click "Start" buttons to hear ascending tones (recording begins)<br>
        • Click "End" buttons to hear descending tones (recording stops)<br>
        • Each variation has different frequency ranges and characteristics<br>
        • Bass variations (6-10) focus on lower frequencies with short durations<br>
        • Choose the variation that sounds most professional and pleasant to you
        """)
        instructions.setStyleSheet("""
            margin: 20px; 
            padding: 15px; 
            background-color: #E3F2FD; 
            border-radius: 8px; 
            border: 1px solid #BBDEFB;
            font-size: 11px;
        """)
        container_layout.addWidget(instructions)
        
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area)
        
    def create_sound_group(self, title, start_file, end_file, description, color):
        """Create a group for testing a sound variation"""
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {color};
                border: 2px solid {color};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {color};
                font-weight: bold;
            }}
        """)
        
        layout = QVBoxLayout(group)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #666; font-size: 11px; margin: 5px; font-style: italic;")
        layout.addWidget(desc_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Start button
        start_btn = QPushButton("Test Start Sound")
        start_btn.clicked.connect(lambda: self.play_sound(start_file))
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
            }}
            QPushButton:pressed {{
                background-color: {color}AA;
            }}
        """)
        button_layout.addWidget(start_btn)
        
        # End button
        end_btn = QPushButton("Test End Sound")
        end_btn.clicked.connect(lambda: self.play_sound(end_file))
        end_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #f44336DD;
            }}
            QPushButton:pressed {{
                background-color: #f44336AA;
            }}
        """)
        button_layout.addWidget(end_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return group
        
    def init_sounds(self):
        """Initialize all sound effects"""
        sound_files = [
            "sound_start.wav", "sound_end.wav",
            "sound_start_v1.wav", "sound_end_v1.wav",
            "sound_start_v2.wav", "sound_end_v2.wav",
            "sound_start_v3.wav", "sound_end_v3.wav",
            "sound_start_v4.wav", "sound_end_v4.wav",
            "sound_start_v5.wav", "sound_end_v5.wav",
            "sound_start_v6.wav", "sound_end_v6.wav",
            "sound_start_v7.wav", "sound_end_v7.wav",
            "sound_start_v8.wav", "sound_end_v8.wav",
            "sound_start_v9.wav", "sound_end_v9.wav",
            "sound_start_v10.wav", "sound_end_v10.wav"
        ]
        
        for sound_file in sound_files:
            file_path = os.path.join("../assets", sound_file)
            if os.path.exists(file_path):
                sound = QSoundEffect()
                sound.setSource(QUrl.fromLocalFile(file_path))
                sound.setVolume(0.35)
                self.sounds[sound_file] = sound
                print(f"Loaded: {sound_file}")
            else:
                print(f"Warning: {sound_file} not found")
        
    def play_sound(self, sound_file):
        """Play a specific sound file"""
        if sound_file in self.sounds:
            sound = self.sounds[sound_file]
            if sound.isLoaded():
                sound.play()
                print(f"Playing: {sound_file}")
            else:
                print(f"Error: {sound_file} not loaded")
        else:
            print(f"Error: {sound_file} not found")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SoundVariationTestWidget()
    widget.show()
    sys.exit(app.exec_())
