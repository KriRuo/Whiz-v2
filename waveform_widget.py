"""
Audio Waveform Visualization Widget

A custom PyQt5 widget that displays real-time audio levels as an animated
waveform. The widget adapts its appearance and animation based on the
current recording state (idle, recording, transcribing).

Features:
    - Real-time audio level visualization
    - State-based color schemes and animation speeds
    - Smooth transitions between states
    - Performance-optimized rendering
    - Responsive layout integration

States:
    - idle: Subtle blue animation, low amplitude
    - recording: Bright cyan animation, high amplitude
    - transcribing: Moderate animation, medium amplitude

Performance:
    - Uses coarse timers for efficiency
    - Adjustable FPS per state (24/60/30 fps)
    - Cached geometry calculations
"""

import math
import random
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QLinearGradient
from ui.layout_system import DPIScalingHelper, ResponsiveBreakpoints, ScreenSizeClass

class WaveformWidget(QWidget):
    """
    Animated waveform status panel showing recording state.
    
    This widget renders a series of animated bars that respond to audio input
    levels and change appearance based on the current recording state.
    
    Attributes:
        _state (str): Current state ("idle", "recording", "transcribing")
        _level (float): Current audio level (0.0 to 1.0)
        _bars (int): Number of waveform bars to display
        _bar_heights (list): Height values for each bar
        _phase (float): Animation phase for smooth transitions
        _amplitude (float): Current animation amplitude
        _target_amp (float): Target amplitude for smooth transitions
        _speed (float): Animation speed factor
        
    Style Constants:
        BAR_GAP: Spacing between bars (1px)
        BARS_MIN/MAX: Range for number of bars (96-192)
        BAR_MIN_W: Minimum bar width (1px)
        CORNER_R: Border radius (2px)
    """

    # style constants
    BAR_GAP   = 1
    BARS_MIN  = 96
    BARS_MAX  = 192
    BAR_MIN_W = 1
    CORNER_R  = 2

    PALETTE = {
        "idle":        {"core": (90, 140, 200, 120), "glow": (120, 170, 255, 60)},
        "recording":   {"core": (120, 210, 255, 230), "glow": (120, 210, 255, 110)},
        "transcribing":{"core": (120, 140, 165, 140), "glow": (120, 150, 190, 60)},
    }

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._state = "idle"
        self._level = 0.0
        self._bars = 96
        self._bar_heights = [0.1] * self._bars
        self._phase = 0.0
        self._amplitude = 0.20
        self._target_amp = 0.20
        self._speed = 0.014

        # perf: coarse timer + fps per state
        self.animation_timer = QTimer(self)
        self.animation_timer.setTimerType(Qt.CoarseTimer)
        self._fps_idle, self._fps_rec, self._fps_xcribe = 24, 60, 30
        self._set_fps(self._fps_idle)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start()

        # layout-friendly sizing
        self.setMinimumHeight(80)  # Smaller minimum
        self.setMaximumHeight(200)  # Add maximum height
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # cached geometry
        self._x = []
        self._bar_w = 1

        # keep the subtle card look local
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border: 2px solid rgba(176, 196, 222, 0.6);
                border-radius: 12px;
            }
        """)

    # ---------- public API ----------
    def set_state(self, state: str) -> None:
        self._state = state
        if state == "idle":
            self._target_amp, self._speed = 0.20, 0.014  # Increased amplitude
            self._set_fps(self._fps_idle)
        elif state == "recording":
            self._target_amp, self._speed = 0.75, 0.05  # Increased amplitude
            self._set_fps(self._fps_rec)
        else:  # transcribing
            self._target_amp, self._speed = 0.35, 0.02  # Increased amplitude
            self._set_fps(self._fps_xcribe)
        self.update()

    def update_level(self, level: float) -> None:
        self._level = max(0.0, min(1.0, level))

    def set_neon_tint(self, rgb_tuple: tuple[int, int, int]) -> None:
        r, g, b = rgb_tuple
        self.PALETTE["recording"]["core"] = (r, g, b, 230)
        self.PALETTE["recording"]["glow"] = (r, g, b, 110)
        self.update()

    # ---------- internals ----------
    def _set_fps(self, fps: int) -> None:
        self.animation_timer.setInterval(max(12, int(1000 / fps)))

    def _colors_for_state(self) -> tuple[QColor, QColor]:
        s = self._state if self._state in self.PALETTE else "idle"
        cr, cg, cb, ca = self.PALETTE[s]["core"]
        gr, gg, gb, ga = self.PALETTE[s]["glow"]
        return QColor(cr, cg, cb, ca), QColor(gr, gg, gb, ga)

    def showEvent(self, event) -> None:
        # resume when the tab shows
        if not self.animation_timer.isActive():
            self.animation_timer.start()

    def hideEvent(self, event) -> None:
        # pause when hidden (e.g., different tab)
        self.animation_timer.stop()

    def resizeEvent(self, event) -> None:
        w = self.width()
        gap = self.BAR_GAP
        bars = max(self.BARS_MIN, min(self.BARS_MAX, w // 8))
        usable = w - (bars - 1) * gap
        bar_w = max(self.BAR_MIN_W, usable // bars)
        start = (w - (bars * bar_w + (bars - 1) * gap)) // 2
        self._x = [start + i * (bar_w + gap) for i in range(bars)]
        self._bars = bars
        self._bar_w = bar_w
        if len(self._bar_heights) != self._bars:
            self._bar_heights = [0.1] * self._bars
        super().resizeEvent(event)

    def update_animation(self) -> None:
        # smooth amplitude → target
        if self._amplitude < self._target_amp:
            self._amplitude = min(self._target_amp, self._amplitude + self._speed)
        elif self._amplitude > self._target_amp:
            self._amplitude = max(self._target_amp, self._amplitude - self._speed)

        # Use real audio levels for bar heights (bars only grow upward)
        if self._state == "idle" or self._level < 0.01:
            # Uniform height for all bars when idle or no audio
            standard_height = 0.25  # Increased baseline height
            self._bar_heights = [standard_height] * self._bars
        else:
            # Dynamic waveform based on real audio levels (bars grow upward only)
            base_height = 0.25  # Increased baseline height
            audio_amplitude = self._level * self._amplitude
            
            for i in range(self._bars):
                # Create wave-like pattern with multiple frequencies for natural flow
                position_factor = (i / self._bars) * 2 * math.pi
                
                # Primary wave (main flow)
                primary_wave = math.sin(position_factor + self._phase * 0.8) * 1.5
                
                # Secondary wave (detail)
                secondary_wave = math.sin(position_factor * 2.3 + self._phase * 1.2) * 0.6
                
                # Tertiary wave (fine detail)
                tertiary_wave = math.sin(position_factor * 4.1 + self._phase * 0.6) * 0.3
                
                # Add some subtle randomness for natural variation
                random.seed(i + int(self._phase * 5))
                noise = random.uniform(-0.2, 0.2)
                
                # Combine waves for natural flowing pattern
                total_variation = primary_wave + secondary_wave + tertiary_wave + noise
                
                # Ensure all bars participate while maintaining wave pattern
                min_variation = 0.3  # Minimum movement for all bars
                # Use the wave pattern as the base, but ensure minimum participation
                if total_variation < -0.5:  # If wave would make bar too low
                    adjusted_variation = min_variation + (total_variation + 0.5) * 0.3  # Scale down the negative part
                else:
                    adjusted_variation = max(min_variation, total_variation)
                
                # Bars only grow upward from baseline
                height = base_height + (audio_amplitude * (0.8 + adjusted_variation))
                self._bar_heights[i] = min(0.95, max(base_height, height))  # Clamp between baseline and 0.95

        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        r = self.rect()
        h = r.height()

        core, glow = self._colors_for_state()
        glow_passes = 2 if self._state == "recording" else 1

        for i in range(self._bars):
            # Use the pre-calculated bar heights from update_animation
            bar_height_ratio = self._bar_heights[i] if i < len(self._bar_heights) else 0.15
            bar_h = max(6, int(h * bar_height_ratio))
            # Align bars to bottom to reduce white space
            y = r.bottom() - bar_h
            x = self._x[i] if i < len(self._x) else 0
            rect = QRectF(x, y, self._bar_w, bar_h)

            # glow (screen blend)
            for gp in range(glow_passes):
                p.save()
                p.setCompositionMode(QPainter.CompositionMode_Screen)
                p.setPen(Qt.NoPen)
                expand_x = 3 if (gp == 0 and self._state == "recording") else 2
                expand_y = 6 if (gp == 0 and self._state == "recording") else 4
                g = QColor(glow)
                if self._state != "recording" and gp == 0:
                    g.setAlpha(int(glow.alpha() * 0.7))
                p.setBrush(g)
                p.drawRoundedRect(rect.adjusted(-expand_x/2, -expand_y/2,
                                                expand_x/2,  expand_y/2),
                                  self.CORNER_R+1, self.CORNER_R+1)
                p.restore()

            # core bar gradient
            grad = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
            top = QColor(core); top.setAlpha(int(core.alpha()*0.95))
            bot = QColor(core); bot.setAlpha(int(core.alpha()*0.70))
            grad.setColorAt(0, top); grad.setColorAt(1, bot)
            p.setPen(Qt.NoPen)
            p.setBrush(grad)
            p.drawRoundedRect(rect, self.CORNER_R, self.CORNER_R)
