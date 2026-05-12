"""Standalone splash screen shown while the Whisper model loads on startup."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QApplication
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtSignal, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QFont, QLinearGradient, QPen

from ui.widgets.loading_mascot_widget import LoadingMascotWidget


class SplashScreen(QWidget):
    """Frameless centered splash window; call dismiss() when the app is ready."""

    finished = pyqtSignal()

    def __init__(self):
        super().__init__(
            None,
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool,
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(420, 510)
        self._center_on_screen()
        self._setup_ui()

    # ── layout ───────────────────────────────────────────────────────────────
    def _center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            screen.left() + (screen.width()  - self.width())  // 2,
            screen.top()  + (screen.height() - self.height()) // 2,
        )

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 28, 20, 16)
        layout.setSpacing(2)

        title = QLabel("Whiz")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 30, QFont.Bold))
        title.setStyleSheet("color: #9670ff; background: transparent;")
        layout.addWidget(title)

        subtitle = QLabel("Voice-to-Text")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7a6ea8; background: transparent; margin-bottom: 6px;")
        layout.addWidget(subtitle)

        self.mascot = LoadingMascotWidget()
        self.mascot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.mascot)

    # ── show at full opacity immediately ─────────────────────────────────────
    # A fade-in animation here would never run: show() is called before
    # app.exec_(), so the event loop isn't pumping yet and no animation
    # frames would fire — the splash would sit at opacity 0 the entire time.
    def showEvent(self, event):
        super().showEvent(event)
        self.setWindowOpacity(1.0)

    # ── dismiss (called when model finishes loading) ─────────────────────────
    def dismiss(self):
        """Fade out the splash; emits finished and closes when done."""
        self.mascot.stop_and_hide()
        anim = QPropertyAnimation(self, b"windowOpacity", self)
        anim.setDuration(500)
        anim.setStartValue(self.windowOpacity())
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InCubic)
        anim.finished.connect(self.finished)
        anim.finished.connect(self.close)
        self._fadeout = anim
        anim.start()

    # ── rounded card background ──────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor(38, 34, 62))
        grad.setColorAt(1.0, QColor(22, 20, 36))

        painter.setBrush(grad)
        painter.setPen(QPen(QColor(90, 68, 160), 1))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 18, 18)
        painter.end()
