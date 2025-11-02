#!/usr/bin/env python3
"""
Test script for the new WaveformWidget with neon glow effects
"""

import sys
import time
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer

# Add parent directory to path to import waveform_widget
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from waveform_widget import WaveformWidget  # Import from dedicated file

class WaveformTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_state = "idle"
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Waveform Widget Test - Neon Glow Effects")
        self.setGeometry(100, 100, 600, 200)
        
        layout = QVBoxLayout(self)
        
        # Create waveform widget
        self.waveform = WaveformWidget()
        layout.addWidget(self.waveform)
        
        # Create control buttons
        button_layout = QHBoxLayout()
        
        self.idle_btn = QPushButton("Idle")
        self.idle_btn.clicked.connect(lambda: self.change_state("idle"))
        button_layout.addWidget(self.idle_btn)
        
        self.recording_btn = QPushButton("Recording")
        self.recording_btn.clicked.connect(lambda: self.change_state("recording"))
        button_layout.addWidget(self.recording_btn)
        
        self.transcribing_btn = QPushButton("Transcribing")
        self.transcribing_btn.clicked.connect(lambda: self.change_state("transcribing"))
        button_layout.addWidget(self.transcribing_btn)
        
        layout.addLayout(button_layout)
        
        # Add a timer to simulate audio levels
        self.audio_timer = QTimer()
        self.audio_timer.timeout.connect(self.simulate_audio)
        self.audio_timer.start(100)  # Update every 100ms
        
        self.audio_level = 0.0
        self.audio_direction = 0.1
        
    def change_state(self, state):
        self.current_state = state
        self.waveform.set_state(state)
        print(f"Changed to {state} state")
        
    def simulate_audio(self):
        # Simulate varying audio levels
        if self.current_state == "recording":
            self.audio_level += self.audio_direction
            if self.audio_level >= 1.0:
                self.audio_direction = -0.1
            elif self.audio_level <= 0.0:
                self.audio_direction = 0.1
        else:
            self.audio_level = 0.0
            
        self.waveform.update_level(self.audio_level)

def main():
    app = QApplication(sys.argv)
    
    # Test different neon tints
    test_window = WaveformTestApp()
    test_window.show()
    
    print("Waveform Widget Test")
    print("====================")
    print("1. Click 'Idle' to see light, translucent bars")
    print("2. Click 'Recording' to see neon cyan/blue bars with glow")
    print("3. Click 'Transcribing' to see muted blue-grey bars")
    print("4. Watch the smooth animations and neon glow effects")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
