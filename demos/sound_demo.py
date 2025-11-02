#!/usr/bin/env python3
"""
Test script to preview the new modern sound effects
"""

import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSoundEffect

class SoundTestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_sounds()
        
    def init_ui(self):
        self.setWindowTitle("Sound Effects Test")
        self.setGeometry(300, 300, 300, 200)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Modern Sound Effects Test")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Click buttons to test the new modern, lower-pitched sound effects")
        desc.setStyleSheet("margin: 10px; color: #666;")
        layout.addWidget(desc)
        
        # Start sound button
        self.start_btn = QPushButton("Test Start Sound (Ascending)")
        self.start_btn.clicked.connect(self.play_start_sound)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.start_btn)
        
        # End sound button
        self.end_btn = QPushButton("Test End Sound (Descending)")
        self.end_btn.clicked.connect(self.play_end_sound)
        self.end_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        layout.addWidget(self.end_btn)
        
        # Info
        info = QLabel("""
        New Sound Characteristics:
        • Start: Gentle ascending tone (300Hz → 400Hz)
        • End: Gentle descending tone (400Hz → 300Hz)
        • Smooth fade in/out for professional feel
        • Lower frequencies for modern, subtle tone
        """)
        info.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info)
        
    def init_sounds(self):
        # Initialize sound effects
        self.sound_start = QSoundEffect()
        self.sound_start.setSource(QUrl.fromLocalFile("../assets/sound_start.wav"))
        self.sound_start.setVolume(0.35)
        
        self.sound_end = QSoundEffect()
        self.sound_end.setSource(QUrl.fromLocalFile("../assets/sound_end.wav"))
        self.sound_end.setVolume(0.35)
        
    def play_start_sound(self):
        if self.sound_start.isLoaded():
            self.sound_start.play()
            print("Playing start sound (ascending tone)")
        else:
            print("Error: Start sound not loaded")
            
    def play_end_sound(self):
        if self.sound_end.isLoaded():
            self.sound_end.play()
            print("Playing end sound (descending tone)")
        else:
            print("Error: End sound not loaded")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SoundTestWidget()
    widget.show()
    sys.exit(app.exec_())
