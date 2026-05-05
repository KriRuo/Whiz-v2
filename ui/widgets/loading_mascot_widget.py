"""Microphone mascot widget shown during model preload."""

import math
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation, pyqtProperty,
                          pyqtSignal, QEasingCurve, QRect, QSize)
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont


_MESSAGES = [
    "Warming up vocal cords...",
    "Convincing AI to care...",
    "Bribing the GPU...",
    "Downloading patience...",
    "Teaching myself your accent...",
    "Still loading (it's a big brain)",
    "Please hold — AI is napping",
    "Installing common sense...",
]

_STATE_SEQUENCE = [
    ("jumping_jacks", 2.0),
    ("panting",       0.6),
    ("yawn",          1.4),
    ("idle",          0.5),
]
_CYCLE = sum(d for _, d in _STATE_SEQUENCE)  # 4.5 s

_BG = QColor(26, 29, 36)          # matches BG_PRIMARY (#1a1d24)
_BODY_FILL = QColor(72, 58, 108)   # visible medium-purple (not dark like bg)
_BODY_OUTLINE = QColor(150, 110, 255)  # bright purple, 3px
_EYE = QColor(220, 215, 255)
_ARM = QColor(150, 120, 240)
_STAND = QColor(100, 88, 140)
_MOUTH_DARK = QColor(30, 12, 12)
_MOUTH_LINE = QColor(220, 170, 170)
_TEXT = QColor(180, 158, 240)


class LoadingMascotWidget(QWidget):
    """Animated mic mascot that entertains while the Whisper model loads.

    Call stop_and_hide() when the model is ready; it fades out and emits
    the finished signal when the animation completes.
    """

    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Let QStackedLayout control our geometry — do NOT call setFixedSize.
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self._tick = 0
        self._opacity = 1.0
        self._msg_index = 0
        self._msg_ticks = 0
        self._msg_interval = int(2.5 * 30)  # change message every 2.5 s

        self._timer = QTimer(self)
        self._timer.setInterval(33)  # ~30 fps
        self._timer.timeout.connect(self._on_tick)
        self._timer.start()

    def sizeHint(self) -> QSize:
        return QSize(320, 320)

    # ── animated opacity property (required for QPropertyAnimation) ─────────
    def _get_opacity(self) -> float:
        return self._opacity

    def _set_opacity(self, value: float) -> None:
        self._opacity = max(0.0, min(1.0, value))
        self.update()

    opacity = pyqtProperty(float, fget=_get_opacity, fset=_set_opacity)

    # ── public API ───────────────────────────────────────────────────────────
    def stop_and_hide(self) -> None:
        """Stop the animation loop and fade out; emits finished when done."""
        self._timer.stop()
        anim = QPropertyAnimation(self, b"opacity", self)
        anim.setDuration(500)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.finished.connect(self.finished)
        anim.finished.connect(self.hide)
        self._fade_anim = anim  # keep reference so Qt doesn't GC it
        anim.start()

    # ── internal ─────────────────────────────────────────────────────────────
    def _on_tick(self) -> None:
        self._tick += 1
        self._msg_ticks += 1
        if self._msg_ticks >= self._msg_interval:
            self._msg_ticks = 0
            self._msg_index = (self._msg_index + 1) % len(_MESSAGES)
        self.update()

    def _current_state(self):
        t = (self._tick / 30.0) % _CYCLE
        elapsed = 0.0
        for name, dur in _STATE_SEQUENCE:
            if t < elapsed + dur:
                return name, (t - elapsed) / dur
            elapsed += dur
        return _STATE_SEQUENCE[-1][0], 1.0

    # ── painting ─────────────────────────────────────────────────────────────
    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        # Explicit background fill so the mascot is visible over any stylesheet.
        painter.setOpacity(1.0)
        painter.fillRect(self.rect(), _BG)

        painter.setOpacity(self._opacity)

        cx = w // 2
        cy = h // 2 - 20  # shift up to leave room for message text

        state, progress = self._current_state()

        # ── mic body ─────────────────────────────────────────────────────────
        body_w, body_h = 68, 100
        bx = cx - body_w // 2
        by = cy - body_h // 2

        painter.setBrush(QBrush(_BODY_FILL))
        painter.setPen(QPen(_BODY_OUTLINE, 3))
        painter.drawRoundedRect(bx, by, body_w, body_h, 34, 34)

        # ── eyes ─────────────────────────────────────────────────────────────
        eye_y = by + 30
        blink = (self._tick % 75) < 3
        if blink:
            painter.setPen(QPen(_EYE, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawLine(cx - 20, eye_y, cx - 9, eye_y)
            painter.drawLine(cx + 9,  eye_y, cx + 20, eye_y)
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(_EYE))
            painter.drawEllipse(cx - 20, eye_y - 6, 12, 12)
            painter.drawEllipse(cx + 8,  eye_y - 6, 12, 12)

        # ── mouth ─────────────────────────────────────────────────────────────
        mouth_y = by + 72
        if state == "panting":
            painter.setBrush(QBrush(_MOUTH_DARK))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx - 13, mouth_y - 6, 26, 16)
        elif state == "yawn":
            ow = int(10 + 26 * progress)
            oh = int(8 + 22 * progress)
            painter.setBrush(QBrush(_MOUTH_DARK))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx - ow // 2, mouth_y - oh // 2, ow, oh)
        else:
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(_MOUTH_LINE, 2))
            painter.drawArc(QRect(cx - 14, mouth_y - 6, 28, 14), 210 * 16, 120 * 16)

        # ── arms ──────────────────────────────────────────────────────────────
        arm_y = by + body_h // 2 + 10
        arm_len = 34

        if state == "jumping_jacks":
            angle_deg = 60.0 * math.sin(progress * 2 * math.pi * 2)
        elif state == "yawn":
            angle_deg = 70.0 * min(progress * 2, 1.0)
        elif state == "panting":
            angle_deg = 5.0
        else:
            angle_deg = 0.0

        outward = int(arm_len * math.cos(math.radians(12)))
        upward  = int(arm_len * math.sin(math.radians(abs(angle_deg))))
        if angle_deg < 0:
            upward = -upward

        painter.setPen(QPen(_ARM, 4, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(cx - body_w // 2, arm_y,
                         cx - body_w // 2 - outward, arm_y - upward)
        painter.drawLine(cx + body_w // 2, arm_y,
                         cx + body_w // 2 + outward, arm_y - upward)

        # ── stand ─────────────────────────────────────────────────────────────
        stand_top = by + body_h
        stand_bot = cy + body_h // 2 + 14
        painter.setPen(QPen(_STAND, 3))
        painter.drawLine(cx, stand_top, cx, stand_bot)
        painter.drawLine(cx - 24, stand_bot, cx + 24, stand_bot)

        # ── message text ──────────────────────────────────────────────────────
        painter.setPen(_TEXT)
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(QRect(10, h - 52, w - 20, 46),
                         Qt.AlignHCenter | Qt.AlignVCenter | Qt.TextWordWrap,
                         _MESSAGES[self._msg_index])

        painter.end()
