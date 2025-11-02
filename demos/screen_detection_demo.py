#!/usr/bin/env python3
"""
Test script to verify screen detection logic for the floating icon
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor

class TestScreenDetection(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Screen Detection Test")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout(self)
        
        # Test button
        test_btn = QPushButton("Test Screen Detection")
        test_btn.clicked.connect(self.test_screen_detection)
        layout.addWidget(test_btn)
        
        # Results label
        self.results_label = QLabel("Click the button to test screen detection")
        self.results_label.setWordWrap(True)
        layout.addWidget(self.results_label)
        
    def test_screen_detection(self):
        """Test the screen detection logic"""
        results = []
        
        # Test 1: Get cursor position
        cursor_pos = QCursor.pos()
        results.append(f"Cursor position: {cursor_pos.x()}, {cursor_pos.y()}")
        
        # Test 2: Get screen at cursor position
        screen_at_cursor = QApplication.screenAt(cursor_pos)
        if screen_at_cursor:
            geometry = screen_at_cursor.geometry()
            results.append(f"Screen at cursor: {screen_at_cursor.name()} - Geometry: {geometry.x()}, {geometry.y()}, {geometry.width()}x{geometry.height()}")
        else:
            results.append("Screen at cursor: None")
        
        # Test 3: Get primary screen
        primary_screen = QApplication.primaryScreen()
        if primary_screen:
            geometry = primary_screen.geometry()
            results.append(f"Primary screen: {primary_screen.name()} - Geometry: {geometry.x()}, {geometry.y()}, {geometry.width()}x{geometry.height()}")
        else:
            results.append("Primary screen: None")
        
        # Test 4: List all screens
        screens = QApplication.screens()
        results.append(f"Total screens: {len(screens)}")
        for i, screen in enumerate(screens):
            geometry = screen.geometry()
            results.append(f"  Screen {i}: {screen.name()} - Geometry: {geometry.x()}, {geometry.y()}, {geometry.width()}x{geometry.height()}")
        
        # Test 5: Calculate positions for different settings
        if screen_at_cursor:
            screen_geometry = screen_at_cursor.geometry()
            positions = [
                ("Top Left", (screen_geometry.x() + 20, screen_geometry.y() + 20)),
                ("Top Right", (screen_geometry.x() + screen_geometry.width() - 100, screen_geometry.y() + 20)),
                ("Bottom Right", (screen_geometry.x() + screen_geometry.width() - 100, screen_geometry.y() + screen_geometry.height() - 100)),
                ("Bottom Left", (screen_geometry.x() + 20, screen_geometry.y() + screen_geometry.height() - 100)),
                ("Top Center", (screen_geometry.x() + (screen_geometry.width() - 80) // 2, screen_geometry.y() + 20)),
                ("Middle Center", (screen_geometry.x() + (screen_geometry.width() - 80) // 2, screen_geometry.y() + (screen_geometry.height() - 80) // 2)),
                ("Bottom Center", (screen_geometry.x() + (screen_geometry.width() - 80) // 2, screen_geometry.y() + screen_geometry.height() - 100))
            ]
            
            results.append("\nCalculated positions:")
            for pos_name, (x, y) in positions:
                results.append(f"  {pos_name}: ({x}, {y})")
        
        self.results_label.setText("\n".join(results))

def main():
    app = QApplication(sys.argv)
    window = TestScreenDetection()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
