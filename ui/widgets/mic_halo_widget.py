from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QConicalGradient
from PyQt5.QtWidgets import QWidget


class MicHaloWidget(QWidget):
    """Circular microphone halo with subtle idle pulse and recording animation.

    The widget exposes a boolean 'recording' property to drive animations.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._recording = False
        self._pulse = 0.0  # 0..1

        # Idle pulse timer
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._advance_pulse)
        self._pulse_timer.start(32)  # ~30 FPS

        # Rotation for recording state
        self._rotation = 0.0
        self._rotation_anim = QPropertyAnimation(self, b"rotation")
        self._rotation_anim.setDuration(6000)
        self._rotation_anim.setStartValue(0.0)
        self._rotation_anim.setEndValue(360.0)
        self._rotation_anim.setLoopCount(-1)
        self._rotation_anim.setEasingCurve(QEasingCurve.Linear)

        self.setMinimumSize(320, 320)  # Increased to match MicCircleWidget size
        self.setObjectName("MicHalo")

    # ----- animated properties -----
    def get_rotation(self) -> float:
        return self._rotation

    def set_rotation(self, value: float):
        self._rotation = value
        self.update()

    rotation = pyqtProperty(float, fget=get_rotation, fset=set_rotation)

    # ----- recording property -----
    def get_recording(self) -> bool:
        return self._recording

    def set_recording(self, value: bool):
        if self._recording == value:
            return
        self._recording = value
        if value:
            self._rotation_anim.start()
        else:
            self._rotation_anim.stop()
            self._rotation = 0.0
        self.update()

    recording = pyqtProperty(bool, fget=get_recording, fset=set_recording)

    # ----- helpers -----
    def _advance_pulse(self):
        # slow breathing 1.6s period
        step = 32.0 / 1600.0
        self._pulse = (self._pulse + step) % 1.0
        if not self._recording:
            self.update()

    # ----- paint -----
    def paintEvent(self, event):  # noqa: N802 (Qt signature)
        size = min(self.width(), self.height())
        radius = size / 2.0
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(center_x, center_y)

        # Background soft glow
        pulse_scale = 1.0 + (0.04 * (1.0 - abs(0.5 - self._pulse) * 2.0))
        painter.save()
        painter.scale(pulse_scale, pulse_scale)
        pen = QPen(Qt.NoPen)
        painter.setPen(pen)
        # Inner soft circle
        painter.setBrush(QColor(255, 255, 255, 18))
        painter.drawEllipse(-radius * 0.72, -radius * 0.72, radius * 1.44, radius * 1.44)
        painter.restore()

        # Rotating ring (active when recording)
        painter.save()
        painter.rotate(self._rotation)
        grad = QConicalGradient(0, 0, 0)
        grad.setColorAt(0.0, QColor(59, 130, 246))      # blue
        grad.setColorAt(0.5, QColor(34, 211, 238))      # cyan
        grad.setColorAt(1.0, QColor(217, 70, 239))      # pink

        ring_pen = QPen()
        ring_pen.setWidthF(radius * 0.14)
        ring_pen.setBrush(grad)
        ring_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(ring_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(int(-radius * 0.86), int(-radius * 0.86), int(radius * 1.72), int(radius * 1.72), 0, 360 * 16)
        painter.restore()

        # Inner dark disk
        painter.save()
        painter.setPen(QPen(QColor(255, 255, 255, 28), 1))
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.drawEllipse(int(-radius * 0.60), int(-radius * 0.60), int(radius * 1.20), int(radius * 1.20))
        painter.restore()

        # Mic glyph (simple bars)
        painter.save()
        painter.setPen(QPen(QColor(160, 200, 255, 220), 3, cap=Qt.RoundCap))
        for i, h in enumerate([18, 28, 36, 24]):
            x = (i - 1.5) * 10
            painter.drawLine(x, -h / 2.0, x, h / 2.0)
        painter.restore()


