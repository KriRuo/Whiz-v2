"""
Animated Circle Component for Whiz Voice-to-Text Application
Custom QWidget with soft neon glow aura and pulsing effects.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty, QRectF, QEasingCurve
from PyQt5.QtGui import QPainter, QPen, QBrush, QRadialGradient, QConicalGradient, QLinearGradient, QColor, QFont
from PyQt5.QtSvg import QSvgRenderer
from ui.layout_system import DPIScalingHelper, ResponsiveBreakpoints, ScreenSizeClass, AnimationTokens


class AnimationCircleWidget(QWidget):
    """Animated circle with soft neon glow aura and pulsing effects."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Animation properties
        self._pulse_opacity = 0.3
        self._idle_pulse_opacity = 0.2  # Updated to match new animation range (0.15-0.25)
        self._mystery_pulse_opacity = 0.15  # Updated to match new animation range (0.1-0.2)
        self._spinning_circles_angle = 0  # New spinning circles rotation
        self._spinning_circles_opacity = 0.1  # Updated to match new animation range (0.05-0.15)
        self._purple_aura_angle = 0  # New purple spinning aura rotation
        self._rotation_angle = 0
        self._inner_rotation_angle = 0  # New inner animation rotation
        self._color_variation_angle = 0  # Color variation rotation
        self._is_recording = False
        self._is_processing = False
        
        # Set responsive sizing instead of fixed size
        self._base_size = 240  # Base size for calculations
        self._glow_margin = 80  # Extra margin for glow effects
        
        # Set size policy for responsive behavior
        from PyQt5.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set initial size based on screen class (with safe fallback)
        try:
            self._update_responsive_size()
        except Exception:
            # Fallback to fixed size if responsive sizing fails during startup
            self.setFixedSize(320, 320)
        
        # Initialize animations
        self._init_animations()
        
        # Start rotation animations with reduced frequency for better performance
        self._rotation_timer = QTimer()
        self._rotation_timer.timeout.connect(self._update_rotation)
        self._rotation_timer.start(200)  # Reduced from 100ms to 200ms (5 FPS instead of 10 FPS)
        
        # Start inner rotation animation (faster than outer glow)
        self._inner_rotation_timer = QTimer()
        self._inner_rotation_timer.timeout.connect(self._update_inner_rotation)
        self._inner_rotation_timer.start(150)  # Reduced from 80ms to 150ms (6.7 FPS instead of 12.5 FPS)
        
        # Start color variation animation (slowest)
        self._color_variation_timer = QTimer()
        self._color_variation_timer.timeout.connect(self._update_color_variation)
        self._color_variation_timer.start(300)  # Reduced from 150ms to 300ms (3.3 FPS instead of 6.7 FPS)
        
        # Spinning circles rotation timer disabled
        # self._spinning_circles_timer = QTimer()
        # self._spinning_circles_timer.timeout.connect(self._update_spinning_circles)
        # self._spinning_circles_timer.start(150)  # Slower, smoother rotation
        
        # Start purple aura rotation timer
        self._purple_aura_timer = QTimer()
        self._purple_aura_timer.timeout.connect(self._update_purple_aura)
        self._purple_aura_timer.start(200)  # Moderate speed for subtle spinning
    
    def _update_responsive_size(self):
        """Update widget size based on screen class and DPI."""
        # Check if QApplication is available and initialized
        app = QApplication.instance()
        if app is None:
            # Fallback to fixed size if app not ready
            self.setFixedSize(320, 320)
            return
        
        try:
            screen_class = ResponsiveBreakpoints.get_current_screen_size_class()
            dpi_factor = DPIScalingHelper.get_device_pixel_ratio()
            
            # Calculate responsive base size
            size_multipliers = {
                ScreenSizeClass.XSMALL: 0.7,   # Smaller on small screens
                ScreenSizeClass.SMALL: 0.8,    # Slightly smaller
                ScreenSizeClass.MEDIUM: 1.0,   # Base size
                ScreenSizeClass.LARGE: 1.1,    # Slightly larger
                ScreenSizeClass.XLARGE: 1.2    # Larger on big screens
            }
            
            multiplier = size_multipliers[screen_class]
            responsive_size = int(self._base_size * multiplier)
            
            # Apply DPI scaling
            final_size = DPIScalingHelper.scale_pixel_value(responsive_size, dpi_factor)
            
            # Set the size with glow margin
            total_size = final_size + self._glow_margin
            self.resize(total_size, total_size)
        except Exception:
            # Fallback to fixed size if any error occurs
            self.setFixedSize(320, 320)
    
    def sizeHint(self):
        """Provide size hint for layout system."""
        try:
            screen_class = ResponsiveBreakpoints.get_current_screen_size_class()
            dpi_factor = DPIScalingHelper.get_device_pixel_ratio()
            
            size_multipliers = {
                ScreenSizeClass.XSMALL: 0.7,
                ScreenSizeClass.SMALL: 0.8,
                ScreenSizeClass.MEDIUM: 1.0,
                ScreenSizeClass.LARGE: 1.1,
                ScreenSizeClass.XLARGE: 1.2
            }
            
            multiplier = size_multipliers[screen_class]
            responsive_size = int(self._base_size * multiplier)
            final_size = DPIScalingHelper.scale_pixel_value(responsive_size, dpi_factor)
            total_size = final_size + self._glow_margin
            
            from PyQt5.QtCore import QSize
            return QSize(total_size, total_size)
        except Exception:
            # Fallback to fixed size if responsive sizing fails
            from PyQt5.QtCore import QSize
            return QSize(320, 320)
    
    def minimumSizeHint(self):
        """Provide minimum size hint for layout system."""
        try:
            # Minimum size should be smaller but still usable
            min_base_size = int(self._base_size * 0.6)
            dpi_factor = DPIScalingHelper.get_device_pixel_ratio()
            min_size = DPIScalingHelper.scale_pixel_value(min_base_size, dpi_factor)
            total_min_size = min_size + int(self._glow_margin * 0.5)
            
            from PyQt5.QtCore import QSize
            return QSize(total_min_size, total_min_size)
        except Exception:
            # Fallback to fixed minimum size if responsive sizing fails
            from PyQt5.QtCore import QSize
            return QSize(200, 200)
    
    def resizeEvent(self, event):
        """Handle resize events to maintain aspect ratio and update calculations."""
        super().resizeEvent(event)
        
        # Ensure square aspect ratio
        size = min(event.size().width(), event.size().height())
        if size != event.size().width() or size != event.size().height():
            self.resize(size, size)
        
    def _init_animations(self):
        """Initialize pulse animations."""
        # Recording pulse animation (faster, more dramatic)
        self._pulse_animation = QPropertyAnimation(self, b"pulseOpacity")
        self._pulse_animation.setDuration(AnimationTokens.DURATION_SLOW)
        self._pulse_animation.setLoopCount(-1)  # Infinite loop
        self._pulse_animation.setStartValue(0.2)
        self._pulse_animation.setEndValue(0.8)
        self._pulse_animation.setEasingCurve(QEasingCurve.InOutSine)
        
        # Idle pulse animation (slower and more seamless)
        self._idle_pulse_animation = QPropertyAnimation(self, b"idlePulseOpacity")
        self._idle_pulse_animation.setDuration(6000)  # Much slower for seamless transitions
        self._idle_pulse_animation.setLoopCount(-1)  # Infinite loop
        self._idle_pulse_animation.setStartValue(0.15)  # Keep subtle range
        self._idle_pulse_animation.setEndValue(0.25)   # Keep subtle range
        self._idle_pulse_animation.setEasingCurve(QEasingCurve.InOutCubic)  # Smoother easing for seamless transitions
        
        # Mysterious secondary pulse animation (slower and more seamless)
        self._mystery_pulse_animation = QPropertyAnimation(self, b"mysteryPulseOpacity")
        self._mystery_pulse_animation.setDuration(4500)  # Much slower for seamless transitions
        self._mystery_pulse_animation.setLoopCount(-1)  # Infinite loop
        self._mystery_pulse_animation.setStartValue(0.1)  # Keep subtle range
        self._mystery_pulse_animation.setEndValue(0.2)   # Keep subtle range
        self._mystery_pulse_animation.setEasingCurve(QEasingCurve.InOutCubic)  # Smoother easing for seamless transitions
        
        # Spinning circles animation (more subtle and smooth)
        self._spinning_circles_animation = QPropertyAnimation(self, b"spinningCirclesOpacity")
        self._spinning_circles_animation.setDuration(5000)  # Slower, more mysterious
        self._spinning_circles_animation.setLoopCount(-1)  # Infinite loop
        self._spinning_circles_animation.setStartValue(0.05)  # Very subtle - reduced by 75%
        self._spinning_circles_animation.setEndValue(0.15)   # Subtle peak - reduced by 75%
        self._spinning_circles_animation.setEasingCurve(QEasingCurve.InOutCubic)  # Smoother easing
        
        # Start idle pulse animation by default (since we start in idle state)
        self._idle_pulse_animation.start()
        self._mystery_pulse_animation.start()
        # Spinning circles animation disabled
        
    @pyqtProperty(float)
    def pulseOpacity(self):
        """Get current pulse opacity for animation."""
        return self._pulse_opacity
        
    @pulseOpacity.setter
    def pulseOpacity(self, value):
        """Set pulse opacity and trigger repaint."""
        self._pulse_opacity = value
        self.update()
        
    @pyqtProperty(float)
    def idlePulseOpacity(self):
        """Get current idle pulse opacity for animation."""
        return self._idle_pulse_opacity
        
    @idlePulseOpacity.setter
    def idlePulseOpacity(self, value):
        """Set idle pulse opacity and trigger repaint."""
        self._idle_pulse_opacity = value
        self.update()
        
    @pyqtProperty(float)
    def mysteryPulseOpacity(self):
        """Get current mystery pulse opacity for animation."""
        return self._mystery_pulse_opacity
        
    @mysteryPulseOpacity.setter
    def mysteryPulseOpacity(self, value):
        """Set mystery pulse opacity and trigger repaint."""
        self._mystery_pulse_opacity = value
        self.update()
        
    @pyqtProperty(float)
    def spinningCirclesOpacity(self):
        """Get current spinning circles opacity for animation."""
        return self._spinning_circles_opacity
        
    @spinningCirclesOpacity.setter
    def spinningCirclesOpacity(self, value):
        """Set spinning circles opacity and trigger repaint."""
        self._spinning_circles_opacity = value
        self.update()
        
    def _update_rotation(self):
        """Update rotation angle for gradient ring with performance optimization."""
        old_angle = self._rotation_angle
        self._rotation_angle = (self._rotation_angle + 1.6) % 360  # Increased step for smoother animation at lower FPS
        # Only update if angle changed significantly (reduce unnecessary repaints)
        if abs(self._rotation_angle - old_angle) > 2:
            self.update()
        
    def _update_inner_rotation(self):
        """Update inner rotation angle for purple-red animation with performance optimization."""
        old_angle = self._inner_rotation_angle
        self._inner_rotation_angle = (self._inner_rotation_angle + 2.4) % 360  # Increased step for smoother animation at lower FPS
        # Only update if angle changed significantly (reduce unnecessary repaints)
        if abs(self._inner_rotation_angle - old_angle) > 2:
            self.update()
        
    def _update_color_variation(self):
        """Update color variation angle for dynamic color changes with performance optimization."""
        old_angle = self._color_variation_angle
        self._color_variation_angle = (self._color_variation_angle + 1.0) % 360  # Increased step for smoother animation at lower FPS
        # Only update if angle changed significantly (reduce unnecessary repaints)
        if abs(self._color_variation_angle - old_angle) > 2:
            self.update()
            
    def _update_spinning_circles(self):
        """Update spinning circles rotation angle."""
        old_angle = self._spinning_circles_angle
        self._spinning_circles_angle = (self._spinning_circles_angle + 1.5) % 360  # Slower, smoother rotation
        # Only update if angle changed significantly (reduce unnecessary repaints)
        if abs(self._spinning_circles_angle - old_angle) > 2:
            self.update()
            
    def _update_purple_aura(self):
        """Update purple aura rotation angle."""
        old_angle = self._purple_aura_angle
        self._purple_aura_angle = (self._purple_aura_angle + 2.0) % 360  # Moderate rotation speed
        # Only update if angle changed significantly (reduce unnecessary repaints)
        if abs(self._purple_aura_angle - old_angle) > 2:
            self.update()
        
    def set_recording(self, recording: bool):
        """Set recording state and control pulse animations."""
        self._is_recording = recording
        if recording:
            # Stop idle pulses and start recording pulse
            self._idle_pulse_animation.stop()
            self._mystery_pulse_animation.stop()
            # Spinning circles animation disabled
            self._pulse_animation.start()
        else:
            # Stop recording pulse and start idle pulses
            self._pulse_animation.stop()
            self._pulse_opacity = 0.3
            self._idle_pulse_animation.start()
            self._mystery_pulse_animation.start()
            # Spinning circles animation disabled
        self.update()
        
    def set_processing(self, processing: bool):
        """Set processing state for spinning animation."""
        self._is_processing = processing
        self.update()
        
    def paintEvent(self, event):
        """Custom paint event for drawing the microphone circle with soft glow."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Enable clipping so drawing stays within this widget's rect.
        # This prevents the glow from visually overlapping widgets below.
        painter.setClipping(True)
        painter.setClipRect(self.rect())
        
        # Get widget dimensions and calculate responsive radius
        rect = self.rect()
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        
        # Calculate radius as percentage of widget size (responsive)
        widget_size = min(rect.width(), rect.height())
        radius = int(widget_size * 0.35)  # 35% of widget size for main circle
        
        # Apply DPI scaling to line widths and effects
        dpi_factor = DPIScalingHelper.get_device_pixel_ratio()
        
        # Draw subtle blue glow layer around entire circle
        self._draw_subtle_blue_glow(painter, center_x, center_y, radius, dpi_factor)
        
        # Draw soft outer glow aura (no hard borders)
        self._draw_soft_glow_aura(painter, center_x, center_y, radius, dpi_factor)
        
        # Draw subtle purple spinning aura
        self._draw_purple_spinning_aura(painter, center_x, center_y, radius, dpi_factor)
        
        # Draw main circle background with subtle gradient
        self._draw_main_circle(painter, center_x, center_y, radius, dpi_factor)
        
        # Draw inner purple-red spinning animation
        self._draw_inner_purple_red_animation(painter, center_x, center_y, radius, dpi_factor)
        
        # Draw idle glow if not recording and not processing
        if not self._is_recording and not self._is_processing:
            self._draw_idle_glow(painter, center_x, center_y, radius, dpi_factor)
        
        # Draw microphone icon
        self._draw_microphone_icon(painter, center_x, center_y, radius, dpi_factor)
        
        # Draw enhanced pulse glow if recording
        if self._is_recording:
            self._draw_recording_glow(painter, center_x, center_y, radius, dpi_factor)
            
    def _draw_soft_glow_aura(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw soft outer glow aura with dark blue Tron-like gradient."""
        # Create multiple layers of soft glow for realistic neon effect - MORE SUBTLE
        # Scale glow distances based on radius (responsive)
        glow_layers = [
            (radius + int(radius * 0.2), 0.50),  # Outer soft glow - MORE SUBTLE
            (radius + int(radius * 0.15), 0.60),  # Mid glow - MORE SUBTLE
            (radius + int(radius * 0.1), 0.70),  # Inner glow - MORE SUBTLE
        ]
        
        for glow_radius, opacity in glow_layers:
            # Create conical gradient for rotating color effect
            conical_gradient = QConicalGradient(center_x, center_y, self._rotation_angle * 0.2)  # Very slow rotation
            
            # Define dark blue Tron-like color palette
            dark_blue = QColor(0, 50, 100)      # Deep dark blue
            electric_blue = QColor(0, 100, 200) # Electric blue
            neon_blue = QColor(0, 150, 255)     # Neon blue
            cyan_blue = QColor(0, 200, 255)     # Cyan blue
            
            # Apply reduced opacity for subtle effect
            dark_blue.setAlphaF(opacity * 0.4)
            electric_blue.setAlphaF(opacity * 0.35)
            neon_blue.setAlphaF(opacity * 0.3)
            cyan_blue.setAlphaF(opacity * 0.35)
            
            # Create smooth color transitions
            conical_gradient.setColorAt(0.0, dark_blue)
            conical_gradient.setColorAt(0.25, electric_blue)
            conical_gradient.setColorAt(0.5, neon_blue)
            conical_gradient.setColorAt(0.75, cyan_blue)
            conical_gradient.setColorAt(1.0, dark_blue)
            
            # Create radial gradient for soft falloff
            radial_gradient = QRadialGradient(center_x, center_y, glow_radius)
            
            # Use cyan_blue as the center color (from the conical gradient)
            center_color = cyan_blue
            edge_color = QColor(0, 0, 0, 0)  # Transparent edge
            
            radial_gradient.setColorAt(0.0, center_color)
            radial_gradient.setColorAt(0.5, QColor(center_color.red(), center_color.green(), center_color.blue(), int(opacity * 0.5 * 255)))
            radial_gradient.setColorAt(1.0, edge_color)
            
            painter.setBrush(QBrush(radial_gradient))
            painter.setPen(Qt.NoPen)
            
            glow_rect = QRectF(center_x - glow_radius, center_y - glow_radius,
                             glow_radius * 2, glow_radius * 2)
            painter.drawEllipse(glow_rect)
            
        # Draw vibrant neon ring animation
        self._draw_neon_ring_animation(painter, center_x, center_y, radius, dpi_factor)
    
    def _draw_purple_spinning_aura(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw subtle purple spinning aura around the circle."""
        # Create multiple layers of purple spinning aura - MORE SUBTLE
        purple_layers = [
            (radius + 60, 0.25),  # Outer purple aura - MORE SUBTLE
            (radius + 45, 0.30),  # Mid purple aura - MORE SUBTLE
            (radius + 30, 0.35),  # Inner purple aura - MORE SUBTLE
        ]
        
        for aura_radius, opacity in purple_layers:
            # Create conical gradient for spinning purple effect
            conical_gradient = QConicalGradient(center_x, center_y, self._purple_aura_angle)
            
            # Define TRON-LIKE MYSTERIOUS purple color palette
            deep_purple = QColor(50, 0, 100)      # Deep mysterious purple
            electric_purple = QColor(100, 0, 200) # Electric Tron purple
            neon_purple = QColor(150, 0, 255)    # Bright neon purple
            cyan_purple = QColor(0, 150, 255)    # Cyan-purple for Tron effect
            
            # Apply SUBTLE opacity with random variation
            import math
            random_factor = math.sin(self._purple_aura_angle * 0.7) * 0.15 + 0.85  # Reduced random variation 0.7-1.0
            
            deep_purple.setAlphaF(opacity * 0.4 * random_factor)      # Reduced from 0.6
            electric_purple.setAlphaF(opacity * 0.35 * random_factor) # Reduced from 0.5
            neon_purple.setAlphaF(opacity * 0.3 * random_factor)       # Reduced from 0.4
            cyan_purple.setAlphaF(opacity * 0.35 * random_factor)     # Reduced from 0.5
            
            # Create MYSTERIOUS color transitions with random stops
            conical_gradient.setColorAt(0.0, deep_purple)
            conical_gradient.setColorAt(0.2, electric_purple)
            conical_gradient.setColorAt(0.5, neon_purple)
            conical_gradient.setColorAt(0.8, cyan_purple)
            conical_gradient.setColorAt(1.0, deep_purple)
            
            # Create radial gradient for soft falloff
            radial_gradient = QRadialGradient(center_x, center_y, aura_radius)
            
            # Use neon_purple as the center color
            center_color = neon_purple
            edge_color = QColor(0, 0, 0, 0)  # Transparent edge
            
            radial_gradient.setColorAt(0.0, center_color)
            radial_gradient.setColorAt(0.4, QColor(center_color.red(), center_color.green(), center_color.blue(), int(opacity * 0.5 * 255)))  # Reduced from 0.7
            radial_gradient.setColorAt(0.7, QColor(center_color.red(), center_color.green(), center_color.blue(), int(opacity * 0.2 * 255)))  # Reduced from 0.3
            radial_gradient.setColorAt(1.0, edge_color)
            
            painter.setBrush(QBrush(radial_gradient))
            painter.setPen(Qt.NoPen)
            
            # Create MYSTERIOUS asymmetrical shape with random variation
            import math
            angle_rad = math.radians(self._purple_aura_angle)
            
            # Calculate MYSTERIOUS oval dimensions with multiple random factors
            # This creates unpredictable, organic shapes that change randomly
            width_factor = (1.0 + 0.4 * math.sin(angle_rad * 1.7) + 
                           0.2 * math.sin(angle_rad * 3.1) + 
                           0.1 * math.sin(angle_rad * 5.3))  # Complex random variation
            height_factor = (1.0 + 0.4 * math.cos(angle_rad * 1.9) + 
                           0.2 * math.cos(angle_rad * 2.7) + 
                           0.1 * math.cos(angle_rad * 4.1))  # Complex random variation
            
            oval_width = aura_radius * 2 * width_factor
            oval_height = aura_radius * 2 * height_factor
            
            aura_rect = QRectF(center_x - oval_width/2, center_y - oval_height/2,
                             oval_width, oval_height)
            painter.drawEllipse(aura_rect)
    
    def _draw_inner_purple_red_animation(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw subtle inner spinning animation with dark blue tones."""
        # Create multiple inner spinning elements
        inner_elements = [
            (radius * 0.3, 0.08),   # Small inner ring
            (radius * 0.2, 0.12),   # Medium inner ring
            (radius * 0.15, 0.15),  # Smallest inner ring
        ]
        
        for element_radius, opacity in inner_elements:
            # Create conical gradient for dark blue spinning effect
            gradient = QConicalGradient(center_x, center_y, self._inner_rotation_angle)
            
            # Define dark blue Tron-like color palette
            dark_blue = QColor(0, 50, 100)      # Deep dark blue
            electric_blue = QColor(0, 100, 200) # Electric blue
            neon_blue = QColor(0, 150, 255)     # Neon blue
            cyan_blue = QColor(0, 200, 255)     # Cyan blue
            
            # Apply opacity to colors
            dark_blue.setAlphaF(opacity)
            electric_blue.setAlphaF(opacity * 0.8)
            neon_blue.setAlphaF(opacity * 0.6)
            cyan_blue.setAlphaF(opacity * 0.7)
            
            # Create smooth color transitions
            gradient.setColorAt(0.0, dark_blue)      # 0° - Dark blue
            gradient.setColorAt(0.25, electric_blue) # 90° - Electric blue
            gradient.setColorAt(0.5, neon_blue)     # 180° - Neon blue
            gradient.setColorAt(0.75, cyan_blue)    # 270° - Cyan blue
            gradient.setColorAt(1.0, dark_blue)     # 360° - Back to dark blue
            
            # Draw the inner spinning element
            painter.setPen(QPen(QBrush(gradient), 1.0))
            painter.setBrush(Qt.NoBrush)
            
            element_rect = QRectF(center_x - element_radius, center_y - element_radius,
                                 element_radius * 2, element_radius * 2)
            painter.drawEllipse(element_rect)
    
    def _draw_subtle_blue_glow(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw a dark blue Tron-like glow layer around the entire circle."""
        # Create multiple layers of dark blue glow with slow rotation - MORE SUBTLE
        glow_layers = [
            (radius + 35, 0.40),  # Inner prominent glow - MORE SUBTLE
            (radius + 55, 0.25),  # Mid subtle glow - MORE SUBTLE
            (radius + 55, 0.60),  # Outer glow - MORE SUBTLE
        ]
        
        for glow_radius, opacity in glow_layers:
            # Create conical gradient for rotating color effect
            gradient = QConicalGradient(center_x, center_y, self._rotation_angle * 0.3)  # Slower rotation for glow
            
            # Define dark blue Tron-like color palette
            dark_blue = QColor(0, 50, 100)      # Deep dark blue
            electric_blue = QColor(0, 100, 200) # Electric blue
            neon_blue = QColor(0, 150, 255)     # Neon blue
            cyan_blue = QColor(0, 200, 255)     # Cyan blue
            
            # Apply opacity to colors
            dark_blue.setAlphaF(opacity)
            electric_blue.setAlphaF(opacity * 0.9)
            neon_blue.setAlphaF(opacity * 0.8)
            cyan_blue.setAlphaF(opacity * 0.7)
            
            # Create dynamic color transitions based on color variation angle
            # This creates a slow, subtle color cycling effect
            color_phase = self._color_variation_angle / 360.0
            
            # Determine which colors to show based on the phase
            if color_phase < 0.25:  # Dark blue to Electric blue transition
                gradient.setColorAt(0.0, dark_blue)
                gradient.setColorAt(0.5, electric_blue)
                gradient.setColorAt(1.0, dark_blue)
            elif color_phase < 0.5:  # Electric blue to Neon blue transition
                gradient.setColorAt(0.0, electric_blue)
                gradient.setColorAt(0.5, neon_blue)
                gradient.setColorAt(1.0, electric_blue)
            elif color_phase < 0.75:  # Neon blue to Cyan blue transition
                gradient.setColorAt(0.0, neon_blue)
                gradient.setColorAt(0.5, cyan_blue)
                gradient.setColorAt(1.0, neon_blue)
            else:  # Cyan blue to Dark blue transition
                gradient.setColorAt(0.0, cyan_blue)
                gradient.setColorAt(0.5, dark_blue)
                gradient.setColorAt(1.0, cyan_blue)
            
            # Create radial falloff for soft edges
            radial_gradient = QRadialGradient(center_x, center_y, glow_radius)
            
            # Use the primary color as the center color
            center_color = electric_blue
            edge_color = QColor(0, 0, 0, 0)  # Transparent edge
            
            radial_gradient.setColorAt(0.0, center_color)
            radial_gradient.setColorAt(0.3, QColor(center_color.red(), center_color.green(), center_color.blue(), int(opacity * 0.7 * 255)))
            radial_gradient.setColorAt(0.7, edge_color)
            radial_gradient.setColorAt(1.0, edge_color)
            
            painter.setBrush(QBrush(radial_gradient))
            painter.setPen(Qt.NoPen)
            
            glow_rect = QRectF(center_x - glow_radius, center_y - glow_radius,
                             glow_radius * 2, glow_radius * 2)
            painter.drawEllipse(glow_rect)
            
        # Add subtle blue inner glow when recording
        if self._is_recording:
            self._draw_recording_blue_glow(painter, center_x, center_y, radius, dpi_factor)
            
    def _draw_main_circle(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw the main circle with subtle gradient and no hard borders."""
        # Create radial gradient for depth without borders
        gradient = QRadialGradient(center_x, center_y, radius)
        
        # Soft gradient from slightly lighter center to darker edges
        center_color = QColor("#2d3139")
        edge_color = QColor("#1a1d24")
        
        gradient.setColorAt(0.0, center_color)
        gradient.setColorAt(0.7, edge_color)
        gradient.setColorAt(1.0, edge_color)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)  # No border for soft appearance
        
        circle_rect = QRectF(center_x - radius, center_y - radius, 
                           radius * 2, radius * 2)
        painter.drawEllipse(circle_rect)
        
    def _draw_recording_blue_glow(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw subtle dark blue inner glow when recording."""
        # Create subtle dark blue glow layers that appear only when recording
        blue_glow_layers = [
            (radius + 15, 0.08),   # Inner blue glow
            (radius + 25, 0.05),   # Outer blue glow
        ]
        
        for glow_radius, opacity in blue_glow_layers:
            # Create radial gradient for soft blue glow
            radial_gradient = QRadialGradient(center_x, center_y, glow_radius)
            
            # Define subtle electric blue color
            blue_color = QColor(0, 100, 200)  # Electric blue
            blue_color.setAlphaF(opacity)
            
            # Create soft falloff
            radial_gradient.setColorAt(0.0, blue_color)
            radial_gradient.setColorAt(0.4, QColor(blue_color.red(), blue_color.green(), blue_color.blue(), int(opacity * 0.6 * 255)))
            radial_gradient.setColorAt(0.8, QColor(0, 0, 0, 0))  # Transparent edge
            radial_gradient.setColorAt(1.0, QColor(0, 0, 0, 0))  # Transparent edge
            
            painter.setBrush(QBrush(radial_gradient))
            painter.setPen(Qt.NoPen)
            
            glow_rect = QRectF(center_x - glow_radius, center_y - glow_radius,
                             glow_radius * 2, glow_radius * 2)
            painter.drawEllipse(glow_rect)
        
    def _draw_recording_glow(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw subtle dark blue pulse glow when recording (less dramatic)."""
        # Create subtle pulsing glow layers
        pulse_intensity = self._pulse_opacity
        
        glow_layers = [
            (radius + 25, pulse_intensity * 0.2),  # Outer pulse (reduced)
            (radius + 15, pulse_intensity * 0.3),  # Mid pulse (reduced)
            (radius + 8, pulse_intensity * 0.4),   # Inner pulse (reduced)
        ]
        
        for glow_radius, opacity in glow_layers:
            # Create radial gradient for soft glow
            radial_gradient = QRadialGradient(center_x, center_y, glow_radius)
            
            # Use subtle electric blue color for recording state
            electric_blue = QColor(0, 100, 200)  # Electric blue
            electric_blue.setAlphaF(opacity * 0.5)  # Much more subtle
            
            # Create soft falloff
            radial_gradient.setColorAt(0.0, electric_blue)
            radial_gradient.setColorAt(0.3, QColor(electric_blue.red(), electric_blue.green(), electric_blue.blue(), int(opacity * 0.4 * 255)))
            radial_gradient.setColorAt(0.7, QColor(0, 0, 0, 0))  # Transparent edge
            radial_gradient.setColorAt(1.0, QColor(0, 0, 0, 0))  # Transparent edge
            
            painter.setBrush(QBrush(radial_gradient))
            painter.setPen(Qt.NoPen)
            
            glow_rect = QRectF(center_x - glow_radius, center_y - glow_radius,
                             glow_radius * 2, glow_radius * 2)
            painter.drawEllipse(glow_rect)
            
    def _draw_idle_glow(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw mysterious idle pulse glow when not recording (gentle breathing effect)."""
        # Create mysterious pulsing glow layers with multiple rhythms for alive feel
        idle_pulse_intensity = self._idle_pulse_opacity
        mystery_pulse_intensity = self._mystery_pulse_opacity
        
        # Calculate symmetric pulse - when intensity is high, glow expands outward
        # When intensity is low, glow contracts inward - REDUCED BY 75%
        pulse_factor = (idle_pulse_intensity - 0.2) / 0.05  # Convert 0.15-0.25 range to -1 to +1
        mystery_factor = (mystery_pulse_intensity - 0.15) / 0.05  # Convert 0.1-0.2 range to -1 to +1
        
        # Create multiple mysterious glow layers with different behaviors - REDUCED BY 75%
        glow_layers = [
            # Primary breathing layer - REDUCED BY 75% - much more subtle
            (radius + 30 + (pulse_factor * 6), idle_pulse_intensity * 0.15, 1.0),  # Outer glow with symmetric pulse
            (radius + 20 + (pulse_factor * 4), idle_pulse_intensity * 0.18, 1.0),    # Mid glow with symmetric pulse
            (radius + 12 + (pulse_factor * 3), idle_pulse_intensity * 0.2, 1.0),     # Inner glow with symmetric pulse
            
            # Secondary mysterious layer (different rhythm) - REDUCED BY 75% - much more subtle
            (radius + 35 + (mystery_factor * 4), mystery_pulse_intensity * 0.12, 0.8),  # Mysterious outer layer
            (radius + 25 + (mystery_factor * 3), mystery_pulse_intensity * 0.15, 0.9),   # Mysterious mid layer
        ]
        
        for glow_radius, opacity, color_intensity in glow_layers:
            # Create radial gradient for soft glow
            radial_gradient = QRadialGradient(center_x, center_y, glow_radius)
            
            # Create mysterious color variations based on pulse intensity
            # Use neon blue colors for more vibrant, electric feel
            base_red = int(0 + (mystery_pulse_intensity * 5))    # 0-5 range - minimal red for pure blue
            base_green = int(100 + (idle_pulse_intensity * 50))  # 100-150 range - bright green for neon
            base_blue = int(200 + (mystery_pulse_intensity * 55)) # 200-255 range - bright blue for neon
            
            mysterious_color = QColor(base_red, base_green, base_blue)
            mysterious_color.setAlphaF(opacity * 0.3 * color_intensity)  # Slightly more visible for neon effect
            
            # Create soft falloff with more gradient stops for mysterious effect
            radial_gradient.setColorAt(0.0, mysterious_color)
            radial_gradient.setColorAt(0.15, QColor(mysterious_color.red(), mysterious_color.green(), mysterious_color.blue(), int(opacity * 0.7 * color_intensity * 255)))
            radial_gradient.setColorAt(0.35, QColor(mysterious_color.red(), mysterious_color.green(), mysterious_color.blue(), int(opacity * 0.4 * color_intensity * 255)))
            radial_gradient.setColorAt(0.6, QColor(mysterious_color.red(), mysterious_color.green(), mysterious_color.blue(), int(opacity * 0.2 * color_intensity * 255)))
            radial_gradient.setColorAt(0.85, QColor(mysterious_color.red(), mysterious_color.green(), mysterious_color.blue(), int(opacity * 0.05 * color_intensity * 255)))
            radial_gradient.setColorAt(1.0, QColor(0, 0, 0, 0))  # Transparent edge
            
            painter.setBrush(QBrush(radial_gradient))
            painter.setPen(Qt.NoPen)
            
            glow_rect = QRectF(center_x - glow_radius, center_y - glow_radius,
                             glow_radius * 2, glow_radius * 2)
            painter.drawEllipse(glow_rect)
            
    def _draw_spinning_circles(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw subtle spinning circles with glow effects and smooth random movements."""
        import math
        
        # Get current spinning circles opacity (much more subtle)
        base_opacity = self._spinning_circles_opacity
        
        # Define circle positions around the main circle (like orbital positions)
        num_circles = 5  # Reduced from 6 for more subtle effect
        circle_radius = 4  # Smaller circles for subtlety
        
        for i in range(num_circles):
            # Calculate orbital position with smooth spinning rotation
            angle = (i * 72) + self._spinning_circles_angle  # 72 degrees apart, plus rotation
            angle_rad = math.radians(angle)
            
            # Calculate distance from center with subtle variation
            orbital_radius = radius * (0.65 + math.sin(math.radians(self._spinning_circles_angle * 0.3 + i * 30)) * 0.05)
            
            # Calculate circle position
            circle_x = center_x + orbital_radius * math.cos(angle_rad)
            circle_y = center_y + orbital_radius * math.sin(angle_rad)
            
            # Create smooth opacity variation for each circle
            # Use multiple sine waves for more organic, random-like behavior
            opacity_variation = (
                math.sin(math.radians(self._spinning_circles_angle * 0.4 + i * 45)) * 0.2 +
                math.sin(math.radians(self._spinning_circles_angle * 0.7 + i * 60)) * 0.1 +
                0.7
            )
            circle_opacity = base_opacity * opacity_variation
            
            # Create subtle color variation
            color_intensity = (
                math.sin(math.radians(self._spinning_circles_angle * 0.3 + i * 40)) * 0.1 +
                math.sin(math.radians(self._spinning_circles_angle * 0.6 + i * 50)) * 0.05 +
                0.85
            )
            
            # Create subtle mysterious color for spinning circles
            mysterious_color = QColor(
                int(80 + color_intensity * 15),   # Red component - much more subtle
                int(100 + color_intensity * 10),  # Green component - much more subtle
                int(150 + color_intensity * 20)   # Blue component - much more subtle
            )
            mysterious_color.setAlphaF(circle_opacity * 0.3)  # Much more subtle
            
            # Draw glow effect around each circle
            self._draw_circle_glow(painter, circle_x, circle_y, circle_radius, mysterious_color, circle_opacity)
            
            # Draw the main spinning circle
            painter.setBrush(QBrush(mysterious_color))
            painter.setPen(Qt.NoPen)
            
            circle_rect = QRectF(circle_x - circle_radius, circle_y - circle_radius,
                               circle_radius * 2, circle_radius * 2)
            painter.drawEllipse(circle_rect)
            
    def _draw_circle_glow(self, painter, center_x, center_y, circle_radius, base_color, opacity):
        """Draw subtle glow effect around a spinning circle."""
        # Create multiple glow layers for each circle
        glow_layers = [
            (circle_radius + 6, opacity * 0.1),   # Outer glow
            (circle_radius + 3, opacity * 0.15),  # Mid glow
            (circle_radius + 1, opacity * 0.2),   # Inner glow
        ]
        
        for glow_radius, glow_opacity in glow_layers:
            # Create radial gradient for soft glow
            radial_gradient = QRadialGradient(center_x, center_y, glow_radius)
            
            # Use the base color with reduced opacity for glow
            glow_color = QColor(base_color.red(), base_color.green(), base_color.blue())
            glow_color.setAlphaF(glow_opacity)
            
            # Create soft falloff
            radial_gradient.setColorAt(0.0, glow_color)
            radial_gradient.setColorAt(0.3, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), int(glow_opacity * 0.5 * 255)))
            radial_gradient.setColorAt(0.7, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), int(glow_opacity * 0.2 * 255)))
            radial_gradient.setColorAt(1.0, QColor(0, 0, 0, 0))  # Transparent edge
            
            painter.setBrush(QBrush(radial_gradient))
            painter.setPen(Qt.NoPen)
            
            glow_rect = QRectF(center_x - glow_radius, center_y - glow_radius,
                             glow_radius * 2, glow_radius * 2)
            painter.drawEllipse(glow_rect)
            
    def _draw_microphone_icon(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw the equalizer SVG icon inside the circle."""
        try:
            # Create SVG renderer
            svg_renderer = QSvgRenderer("assets/equalizer_icon.svg")
            
            if svg_renderer.isValid():
                # Calculate icon size as percentage of radius (responsive)
                icon_size = int(radius * 0.9)  # 90% of radius for good proportion
                
                # Apply DPI scaling to icon size
                icon_size = DPIScalingHelper.scale_pixel_value(icon_size, dpi_factor)
                
                # Calculate position to center the middle bar with the circle center
                # The middle bar is at x=24 in a 48px SVG, so we need to offset accordingly
                icon_x = center_x - icon_size // 2
                icon_y = center_y - icon_size // 2
                
                # Draw the SVG icon
                svg_renderer.render(painter, QRectF(icon_x, icon_y, icon_size, icon_size))
            else:
                # Fallback to simple equalizer bars if SVG fails
                self._draw_fallback_equalizer(painter, center_x, center_y, radius, dpi_factor)
                
        except Exception as e:
            # Fallback to simple equalizer bars if SVG loading fails
            self._draw_fallback_equalizer(painter, center_x, center_y, radius, dpi_factor)
    
    def _draw_fallback_equalizer(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw a simple equalizer icon as fallback."""
        # Create gradient for equalizer bars with dark blue Tron-like colors
        gradient = QLinearGradient(center_x - radius * 0.4, center_y, center_x + radius * 0.4, center_y)
        gradient.setColorAt(0.0, QColor(0, 100, 200))  # Electric blue
        gradient.setColorAt(1.0, QColor(0, 200, 255))  # Cyan blue
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        
        # Draw 5 equalizer bars with different heights, centered properly
        bar_width = int(radius * 0.08)  # Responsive bar width
        bar_spacing = int(radius * 0.12)  # Responsive bar spacing
        total_width = (bar_width * 5) + (bar_spacing * 4)
        start_x = center_x - total_width // 2
        
        # Heights: shorter, medium, tallest (center), medium, shorter
        bar_heights = [int(radius * 0.3), int(radius * 0.5), int(radius * 0.7), int(radius * 0.5), int(radius * 0.3)]
        
        # Apply DPI scaling to corner radius
        corner_radius = DPIScalingHelper.scale_pixel_value(3, dpi_factor)
        
        for i, height in enumerate(bar_heights):
            bar_x = start_x + i * (bar_width + bar_spacing)
            bar_y = center_y - height // 2  # Center each bar vertically around center_y
            
            # Draw rounded rectangle for each bar
            painter.drawRoundedRect(int(bar_x), int(bar_y), int(bar_width), int(height), corner_radius, corner_radius)
        
    def _draw_neon_ring_animation(self, painter, center_x, center_y, radius, dpi_factor):
        """Draw dark blue Tron-like neon ring animation."""
        # Create rotating neon ring effect with dark blue colors
        ring_radius = radius + 6
        ring_width = 1.5
        
        # Create conical gradient for seamless rotating effect
        gradient = QConicalGradient(center_x, center_y, self._rotation_angle)
        
        # Enhanced opacity for better visibility when recording
        base_opacity = 0.30 + (0.20 * abs(self._pulse_opacity - 0.5) * 2)  # Increased from 0.15 + 0.10
        if self._is_recording:
            base_opacity *= 1.5  # More prominent when recording
        
        # Define dark blue Tron-like color palette for ring
        dark_blue = QColor(0, 50, 100)      # Deep dark blue
        electric_blue = QColor(0, 100, 200) # Electric blue
        neon_blue = QColor(0, 150, 255)     # Neon blue
        cyan_blue = QColor(0, 200, 255)     # Cyan blue
        
        # Create smooth gradient transitions with more color stops
        gradient.setColorAt(0.0, QColor(dark_blue.red(), dark_blue.green(), dark_blue.blue(), int(base_opacity * 255)))
        gradient.setColorAt(0.2, QColor(electric_blue.red(), electric_blue.green(), electric_blue.blue(), int(base_opacity * 0.9 * 255)))
        gradient.setColorAt(0.4, QColor(neon_blue.red(), neon_blue.green(), neon_blue.blue(), int(base_opacity * 0.8 * 255)))
        gradient.setColorAt(0.6, QColor(cyan_blue.red(), cyan_blue.green(), cyan_blue.blue(), int(base_opacity * 0.9 * 255)))
        gradient.setColorAt(0.8, QColor(neon_blue.red(), neon_blue.green(), neon_blue.blue(), int(base_opacity * 0.8 * 255)))
        gradient.setColorAt(1.0, QColor(dark_blue.red(), dark_blue.green(), dark_blue.blue(), int(base_opacity * 255)))
        
        # Draw the ring using pen for seamless effect
        painter.setPen(QPen(QBrush(gradient), ring_width))
        painter.setBrush(Qt.NoBrush)
        
        # Draw the ring
        ring_rect = QRectF(center_x - ring_radius, center_y - ring_radius,
                          ring_radius * 2, ring_radius * 2)
        painter.drawEllipse(ring_rect)