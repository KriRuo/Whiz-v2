from PyQt5.QtCore import Qt, QEasingCurve, QPropertyAnimation
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolButton, QPlainTextEdit


class TranscriptExpander(QWidget):
    """Collapsible transcript preview with smooth height animation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TranscriptExpander")

        self._collapsed = True
        self._collapsed_height = 80
        self._expanded_height = 240

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(8)

        header = QHBoxLayout()
        self.title = QLabel("Latest Transcript")
        self.title.setObjectName("TranscriptTitle")
        self.toggle = QToolButton()
        self.toggle.setText("›")
        self.toggle.setCheckable(True)
        self.toggle.setChecked(False)
        self.toggle.clicked.connect(self.toggle_expanded)
        header.addWidget(self.title)
        header.addStretch(1)
        header.addWidget(self.toggle)
        root.addLayout(header)

        self.preview = QPlainTextEdit()
        self.preview.setObjectName("TranscriptPreview")
        self.preview.setReadOnly(True)
        self.preview.setFrameShape(QPlainTextEdit.NoFrame)
        self.preview.setPlaceholderText("Transcripts will appear here…")
        root.addWidget(self.preview)

        self.setMaximumHeight(self._collapsed_height)

        self._anim = QPropertyAnimation(self, b"maximumHeight", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    # API
    def set_text(self, text: str):
        self.preview.setPlainText(text or "")

    def toggle_expanded(self):
        self.set_expanded(not self._collapsed)

    def set_expanded(self, expanded: bool):
        self._collapsed = not expanded
        self.toggle.setChecked(expanded)
        self.toggle.setText("⌄" if expanded else "›")
        start = self.maximumHeight()
        end = self._expanded_height if expanded else self._collapsed_height
        if start == end:
            return
        self._anim.stop()
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()


