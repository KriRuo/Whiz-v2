"""
Custom Tab Widget with Gradient Accent Line
Provides sophisticated shading effects for tab accent lines
"""

from PyQt5.QtWidgets import QTabWidget, QTabBar, QWidget
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPainter, QPen, QLinearGradient, QColor, QFontMetrics


class GradientTabBar(QTabBar):
    """Custom tab bar with gradient accent line for selected tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDrawBase(False)  # Don't draw the base line
        self.setElideMode(Qt.ElideNone)  # Disable text elision to prevent truncation
        self.setUsesScrollButtons(True)  # Allow scrolling if tabs don't fit
    
    def tabSizeHint(self, index):
        """Override to ensure tabs have enough space for their content"""
        # Get the default size hint
        size = super().tabSizeHint(index)
        
        # Get the text for this tab
        text = self.tabText(index)
        if text:
            # Calculate the width needed for the text
            font_metrics = QFontMetrics(self.font())
            text_width = font_metrics.horizontalAdvance(text)
            
            # Add padding (left + right padding from CSS: 20px + 20px = 40px)
            # Plus extra margin for safety and better visual spacing
            required_width = text_width + 70
            
            # Use the larger of default width or required width
            size.setWidth(max(size.width(), required_width))
        
        return size
        
    def paintEvent(self, event):
        """Custom paint event to draw gradient accent line"""
        super().paintEvent(event)
        
        # Get the selected tab index
        selected_index = self.currentIndex()
        if selected_index >= 0:
            # Get the selected tab rectangle
            tab_rect = self.tabRect(selected_index)
            
            # Create painter for gradient accent line
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create horizontal gradient for accent line
            gradient = QLinearGradient(tab_rect.left(), tab_rect.bottom(), 
                                     tab_rect.right(), tab_rect.bottom())
            
            # Gradient stops: fade from edges to center (wider center section)
            gradient.setColorAt(0.0, QColor(0, 212, 255, 30))    # Left edge - very transparent
            gradient.setColorAt(0.15, QColor(0, 212, 255, 100))  # 15% - more visible
            gradient.setColorAt(0.3, QColor(0, 212, 255, 255))   # 30% - full opacity starts
            gradient.setColorAt(0.7, QColor(0, 212, 255, 255))   # 70% - full opacity ends
            gradient.setColorAt(0.85, QColor(0, 212, 255, 100))  # 85% - more visible
            gradient.setColorAt(1.0, QColor(0, 212, 255, 30))    # Right edge - very transparent
            
            # Draw the gradient accent line - extend fully across the tab
            # Use the full tab width to extend to both edges
            accent_rect = QRect(tab_rect.left(), tab_rect.bottom() - 2, 
                               tab_rect.width(), 3)
            painter.fillRect(accent_rect, gradient)
            
            painter.end()


class GradientTabWidget(QTabWidget):
    """Custom tab widget with gradient accent line support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(GradientTabBar(self))
