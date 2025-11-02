import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame, QHBoxLayout, QPushButton, QSizePolicy, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QFont, QClipboard, QIcon, QPixmap, QPainter, QPen, QBrush, QColor
from ui.styles.main_styles import MainStyles
from ui.components import BaseTab
from ui.layout_system import LayoutBuilder, LayoutTokens, ColorTokens


class TranscriptsTab(BaseTab):
    """Transcripts tab component for displaying transcript history"""
    
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app  # Reference to the main application for callbacks
        
        # Connect to parent's transcript update signal
        if hasattr(parent_app, 'transcript_updated'):
            parent_app.transcript_updated.connect(self.refresh_transcript_log)
        
        # Initial load of transcripts
        self.refresh_transcript_log()
    
    def init_content(self):
        """Initialize the Transcripts tab content using new layout system."""
        # Scrollable transcript area with consistent styling
        self.transcript_scroll_area = QScrollArea()
        self.transcript_scroll_area.setWidgetResizable(True)
        self.transcript_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.transcript_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.transcript_scroll_area.setStyleSheet(MainStyles.get_transcript_scroll_area_style())
        
        # Transcript container widget using layout system
        self.transcript_container = QWidget()
        self.transcript_container.setStyleSheet(f"""
            QWidget {{
                background-color: {ColorTokens.BG_PRIMARY};
            }}
        """)
        self.transcript_layout = LayoutBuilder.create_container_layout(
            self.transcript_container,
            spacing=LayoutTokens.SPACING_MD,
            margins=(LayoutTokens.MARGIN_SM, LayoutTokens.MARGIN_SM,
                    LayoutTokens.MARGIN_SM, LayoutTokens.MARGIN_SM)  # Add some padding around the container
        )
        self.transcript_layout.addStretch()  # Push items to top
        
        self.transcript_scroll_area.setWidget(self.transcript_container)
        self.main_layout.addWidget(self.transcript_scroll_area)
    
    def refresh_transcript_log(self):
        """Refresh the transcript history display"""
        # Clear existing transcript widgets
        for i in reversed(range(self.transcript_layout.count() - 1)):  # Keep the stretch
            widget = self.transcript_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Get transcripts from controller
        transcripts = self.parent_app.controller.get_transcripts()
        
        if not transcripts:
            # Show empty state
            empty_label = QLabel("No transcripts yet.\nStart recording to see your transcript history here.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setWordWrap(True)  # Enable word wrap to prevent cutoff
            empty_label.setStyleSheet(MainStyles.get_empty_transcript_style())
            self.transcript_layout.insertWidget(0, empty_label)
            return
        
        # Add transcript entries (newest first)
        # Since we want newest at top, we need to reverse the order when inserting
        # because insertWidget(0, widget) puts the widget at the top
        for transcript in reversed(transcripts):
            transcript_widget = self.create_transcript_widget(transcript)
            self.transcript_layout.insertWidget(0, transcript_widget)
        
        # Scroll to top to show newest transcripts
        self.transcript_scroll_area.verticalScrollBar().setValue(0)
    
    def create_transcript_widget(self, transcript: dict) -> QWidget:
        """Create a widget for a single transcript entry using layout system."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.NoFrame)  # Remove default frame
        widget.setStyleSheet(MainStyles.get_transcript_item_style())
        
        # Main vertical layout for the entire transcript item
        main_layout = LayoutBuilder.create_container_layout(
            widget,
            spacing=2,  # Minimal spacing between timestamp and text
            margins=(0, 0, 0, 0)  # Let the CSS handle padding
        )
        
        # Top row with timestamp and copy button
        top_row_layout = QHBoxLayout()
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(8)
        
        # Timestamp - smaller and more subtle, no border
        timestamp_label = QLabel(transcript["timestamp"])
        timestamp_label.setFont(QFont("Inter", LayoutTokens.FONT_SM))
        timestamp_label.setStyleSheet(f"""
            color: {ColorTokens.TEXT_TERTIARY}; 
            font-size: 11px; 
            font-weight: 400;
            font-family: "Inter","Segoe UI",system-ui,-apple-system;
            padding: 0px;
            margin: 0px;
            background: transparent;
            border: none;
        """)
        top_row_layout.addWidget(timestamp_label)
        
        # Spacer to push copy button to the right
        top_row_layout.addStretch()
        
        # Copy button with programmatically created icon
        copy_icon = self.create_copy_icon(ColorTokens.TEXT_TERTIARY)
        copy_button = QPushButton()
        copy_button.setIcon(copy_icon)
        copy_button.setIconSize(QSize(20, 20))
        copy_button.setObjectName("CopyButton")
        copy_button.setFixedSize(28, 28)
        copy_button.setToolTip("Copy to clipboard")
        copy_button.setCursor(Qt.PointingHandCursor)
        copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 212, 255, 0.1);
                border-radius: 6px;
            }}
        """)
        
        # Store both icons on the button for easy access
        copy_button.copy_icon = copy_icon
        copy_button.checkmark_icon = self.create_checkmark_icon(ColorTokens.TEXT_TERTIARY)
        
        # Store button reference and text for the copy handler
        copy_button.transcript_text = transcript["text"]
        
        # Connect copy functionality with button reference
        copy_button.clicked.connect(self._on_copy_clicked)
        
        top_row_layout.addWidget(copy_button)
        main_layout.addLayout(top_row_layout)
        
        # Text content - more prominent, no border, with natural text flow
        text_label = QLabel(transcript["text"])
        # Enable word wrap to allow text to wrap within the bubble
        text_label.setWordWrap(True)
        text_label.setFont(QFont("Inter", LayoutTokens.FONT_LG))
        text_label.setStyleSheet(f"""
            color: {ColorTokens.TEXT_PRIMARY}; 
            padding: 0px; 
            font-size: 14px;
            font-family: "Inter","Segoe UI",system-ui,-apple-system;
            font-weight: 400;
            line-height: 1.4;
            margin: 0px;
            background: transparent;
            border: none;
        """)
        text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Set proper size policy for natural expansion
        text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        main_layout.addWidget(text_label)
        
        return widget
    
    def _on_copy_clicked(self):
        """Handle copy button click with visual feedback."""
        button = self.sender()  # Get the button that was clicked
        if button and hasattr(button, 'transcript_text'):
            self.copy_transcript_to_clipboard(button.transcript_text, button)
    
    def create_copy_icon(self, color: str) -> QIcon:
        """Create a copy icon programmatically with the specified color."""
        # Create a pixmap for the icon
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Convert color string to QColor
        icon_color = QColor(color)
        
        # Draw the copy icon (two overlapping rectangles)
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(icon_color))
        
        # First rectangle (top-left)
        painter.drawRect(2, 2, 8, 8)
        
        # Second rectangle (bottom-right, offset)
        painter.drawRect(6, 6, 8, 8)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def create_checkmark_icon(self, color: str) -> QIcon:
        """Create a checkmark icon programmatically with the specified color."""
        # Create a pixmap for the icon
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Convert color string to QColor
        icon_color = QColor(color)
        
        # Draw the checkmark icon
        painter.setPen(QPen(QBrush(icon_color), 2.5))
        painter.setBrush(Qt.NoBrush)
        
        # Draw checkmark path: bottom-left to middle, then middle to top-right
        painter.drawLine(5, 10, 8, 13)  # Bottom-left to middle
        painter.drawLine(8, 13, 15, 6)   # Middle to top-right
        
        painter.end()
        
        return QIcon(pixmap)
    
    def copy_transcript_to_clipboard(self, text: str, button: QPushButton = None):
        """Copy transcript text to the system clipboard with visual confirmation."""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Show visual feedback if button reference is provided
            if button and hasattr(button, 'checkmark_icon'):
                # Change icon to checkmark
                button.setIcon(button.checkmark_icon)
                
                # Schedule revert back to copy icon after 2 seconds
                QTimer.singleShot(2000, lambda: button.setIcon(button.copy_icon))
            
            print(f"Copied to clipboard: {text[:50]}{'...' if len(text) > 50 else ''}")
            
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
