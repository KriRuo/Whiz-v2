"""
Layout System for Whiz Voice-to-Text Application
Centralized layout management with consistent spacing and design tokens.
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QWidget, QApplication, QDesktopWidget
from PyQt5.QtCore import Qt
from enum import Enum
import math


class ScreenSizeClass(Enum):
    """Screen size classifications for responsive design."""
    XSMALL = "xsmall"    # < 768px (small laptops)
    SMALL = "small"       # 768px - 1024px (tablets, small laptops)
    MEDIUM = "medium"     # 1024px - 1440px (laptops, small desktops)
    LARGE = "large"       # 1440px - 1920px (desktops)
    XLARGE = "xlarge"     # > 1920px (large desktops, 4K)


class ResponsiveBreakpoints:
    """Responsive breakpoint definitions and screen detection."""
    
    # Breakpoint definitions (width-based)
    BREAKPOINTS = {
        ScreenSizeClass.XSMALL: 768,
        ScreenSizeClass.SMALL: 1024,
        ScreenSizeClass.MEDIUM: 1440,
        ScreenSizeClass.LARGE: 1920,
        ScreenSizeClass.XLARGE: float('inf')
    }
    
    @staticmethod
    def get_screen_size_class(screen_width: int) -> ScreenSizeClass:
        """Determine screen size class based on width."""
        for size_class, breakpoint in ResponsiveBreakpoints.BREAKPOINTS.items():
            if screen_width < breakpoint:
                return size_class
        return ScreenSizeClass.XLARGE
    
    @staticmethod
    def get_current_screen_size_class() -> ScreenSizeClass:
        """Get current screen size class from primary screen."""
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            return ResponsiveBreakpoints.get_screen_size_class(geometry.width())
        return ScreenSizeClass.MEDIUM  # fallback


class DPIScalingHelper:
    """Helper for DPI-aware scaling calculations."""
    
    @staticmethod
    def get_device_pixel_ratio() -> float:
        """Get current device pixel ratio."""
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            if screen:
                return screen.devicePixelRatio()
        return 1.0
    
    @staticmethod
    def scale_pixel_value(value: int, dpi_factor: float = None) -> int:
        """Scale a pixel value by DPI factor."""
        if dpi_factor is None:
            dpi_factor = DPIScalingHelper.get_device_pixel_ratio()
        
        # Don't apply additional scaling if Qt is already handling it
        # Qt's automatic scaling means we should use logical pixels directly
        return value
    
    @staticmethod
    def get_dpi_scaled_font_size(base_size: int, dpi_factor: float = None) -> int:
        """Get DPI-scaled font size."""
        if dpi_factor is None:
            dpi_factor = DPIScalingHelper.get_device_pixel_ratio()
        
        # Don't apply additional scaling if Qt is already handling it
        # Qt's automatic scaling means we should use logical pixels directly
        return base_size


class ResponsiveFontSize:
    """Responsive font size calculator based on screen size and DPI."""
    
    # Base font sizes for different screen classes
    BASE_FONT_SIZES = {
        ScreenSizeClass.XSMALL: {
            'xs': 9, 'sm': 10, 'md': 11, 'lg': 12, 'xl': 13, 'xxl': 14, 'title': 16
        },
        ScreenSizeClass.SMALL: {
            'xs': 9, 'sm': 10, 'md': 11, 'lg': 12, 'xl': 13, 'xxl': 15, 'title': 17
        },
        ScreenSizeClass.MEDIUM: {
            'xs': 10, 'sm': 11, 'md': 12, 'lg': 13, 'xl': 14, 'xxl': 16, 'title': 18
        },
        ScreenSizeClass.LARGE: {
            'xs': 10, 'sm': 11, 'md': 12, 'lg': 13, 'xl': 14, 'xxl': 16, 'title': 19
        },
        ScreenSizeClass.XLARGE: {
            'xs': 11, 'sm': 12, 'md': 13, 'lg': 14, 'xl': 15, 'xxl': 17, 'title': 20
        }
    }
    
    @staticmethod
    def get_font_size(size_key: str, screen_class: ScreenSizeClass = None, dpi_factor: float = None) -> int:
        """Get responsive font size for given key."""
        if screen_class is None:
            screen_class = ResponsiveBreakpoints.get_current_screen_size_class()
        
        base_size = ResponsiveFontSize.BASE_FONT_SIZES[screen_class].get(size_key, 12)
        
        if dpi_factor is None:
            dpi_factor = DPIScalingHelper.get_device_pixel_ratio()
        
        return DPIScalingHelper.get_dpi_scaled_font_size(base_size, dpi_factor)


class AdaptiveSpacing:
    """Adaptive spacing calculator for dynamic margins and padding."""
    
    # Base spacing multipliers for different screen classes
    SPACING_MULTIPLIERS = {
        ScreenSizeClass.XSMALL: 0.8,   # Compact spacing for small screens
        ScreenSizeClass.SMALL: 0.9,    # Slightly reduced spacing
        ScreenSizeClass.MEDIUM: 1.0,   # Base spacing
        ScreenSizeClass.LARGE: 1.1,   # Slightly increased spacing
        ScreenSizeClass.XLARGE: 1.2    # More generous spacing
    }
    
    @staticmethod
    def get_spacing(base_spacing: int, screen_class: ScreenSizeClass = None, dpi_factor: float = None) -> int:
        """Get adaptive spacing value."""
        if screen_class is None:
            screen_class = ResponsiveBreakpoints.get_current_screen_size_class()
        
        multiplier = AdaptiveSpacing.SPACING_MULTIPLIERS[screen_class]
        scaled_spacing = int(base_spacing * multiplier)
        
        if dpi_factor is None:
            dpi_factor = DPIScalingHelper.get_device_pixel_ratio()
        
        return DPIScalingHelper.scale_pixel_value(scaled_spacing, dpi_factor)


class LayoutTokens:
    """Design tokens for consistent spacing and sizing."""
    
    # Font family
    FONT_FAMILY = "Inter"
    FONT_FALLBACK = "Segoe UI,system-ui,-apple-system"
    
    # Base spacing scale (8px base unit) - will be scaled responsively
    SPACING_XS = 4    # Minimal spacing
    SPACING_SM = 8    # Small spacing
    SPACING_MD = 12   # Medium spacing
    SPACING_LG = 16   # Large spacing
    SPACING_XL = 24   # Extra large spacing
    
    # Base margin scale - will be scaled responsively
    MARGIN_XS = 4
    MARGIN_SM = 8
    MARGIN_MD = 12
    MARGIN_LG = 16
    MARGIN_XL = 20
    MARGIN_XXL = 24
    
    # Border radius scale - will be scaled responsively
    RADIUS_SM = 6
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16
    
    # Base font sizes - will be scaled responsively
    FONT_XS = 10      # Timestamps
    FONT_SM = 11      # Content labels
    FONT_MD = 12      # Hints
    FONT_LG = 13      # Subtext/Status
    FONT_XL = 14      # Tab labels, Buttons
    FONT_XXL = 16     # Large text
    FONT_TITLE = 18   # Title
    
    # Responsive font size getters
    @staticmethod
    def get_responsive_font_size(size_key: str) -> int:
        """Get responsive font size."""
        return ResponsiveFontSize.get_font_size(size_key)
    
    # Responsive spacing getters
    @staticmethod
    def get_responsive_spacing(base_spacing: int) -> int:
        """Get responsive spacing value."""
        return AdaptiveSpacing.get_spacing(base_spacing)
    
    # Responsive margin getters
    @staticmethod
    def get_responsive_margin(base_margin: int) -> int:
        """Get responsive margin value."""
        return AdaptiveSpacing.get_spacing(base_margin)


class AnimationTokens:
    """Animation timing tokens for consistent transitions."""
    
    DURATION_FAST = 200      # Button hovers, quick transitions
    DURATION_NORMAL = 300    # Standard animations
    DURATION_SLOW = 800      # Pulse effects
    DURATION_ROTATE = 2000   # Continuous rotations
    EASING_SMOOTH = "ease-in-out"


class ColorTokens:
    """Color tokens for theme-aware styling."""
    
    # Dark Theme (default)
    BG_PRIMARY = "#1a1d24"           # Main dark background
    BG_SECONDARY = "#23272f"         # Card backgrounds
    BG_TERTIARY = "#2d3139"          # Elevated elements
    
    ACCENT_PRIMARY = "#00d4ff"       # Cyan (Start button, active states)
    ACCENT_GRADIENT_START = "#00d4ff"  # Cyan
    ACCENT_GRADIENT_END = "#a855f7"    # Purple
    
    TEXT_PRIMARY = "#e4e6eb"         # Main text
    TEXT_SECONDARY = "#9ca3af"       # Secondary text
    TEXT_TERTIARY = "#6b7280"        # Tertiary text
    
    BUTTON_PRIMARY = "#00d4ff"       # Start button
    BUTTON_SECONDARY = "#4a5056"     # Stop button
    BUTTON_HOVER = "#00b8e6"         # Hover states
    BUTTON_SECONDARY_HOVER = "#5a6066"  # Secondary button hover
    
    BORDER = "#3a3f47"               # Main borders
    BORDER_SUBTLE = "#3a3f47"        # Subtle borders
    GLOW_NEON = "#00d4ff"            # Neon glow effect


class LayoutBuilder:
    """Builder pattern for creating consistent layouts."""
    
    @staticmethod
    def create_main_layout(widget: QWidget, spacing: int = LayoutTokens.SPACING_LG, 
                          margins: tuple = (LayoutTokens.MARGIN_XL, LayoutTokens.MARGIN_XL, 
                                          LayoutTokens.MARGIN_XL, LayoutTokens.MARGIN_XL)) -> QVBoxLayout:
        """Create a main vertical layout with consistent spacing."""
        layout = QVBoxLayout(widget)
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        return layout
    
    @staticmethod
    def create_horizontal_layout(spacing: int = LayoutTokens.SPACING_MD) -> QHBoxLayout:
        """Create a horizontal layout with consistent spacing."""
        layout = QHBoxLayout()
        layout.setSpacing(spacing)
        return layout
    
    @staticmethod
    def create_form_layout(spacing: int = LayoutTokens.SPACING_MD) -> QFormLayout:
        """Create a form layout with consistent spacing."""
        layout = QFormLayout()
        layout.setSpacing(spacing)
        return layout
    
    @staticmethod
    def create_container_layout(widget: QWidget, spacing: int = LayoutTokens.SPACING_SM,
                               margins: tuple = (LayoutTokens.MARGIN_SM, LayoutTokens.MARGIN_SM,
                                               LayoutTokens.MARGIN_SM, LayoutTokens.MARGIN_SM)) -> QVBoxLayout:
        """Create a container layout for nested components."""
        layout = QVBoxLayout(widget)
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        return layout


class ResponsiveSizing:
    """Centralized responsive sizing calculations."""
    
    # Breakpoint-based sizing configurations
    WINDOW_SIZING = {
        ScreenSizeClass.XSMALL: {
            'width_percent': 0.25, 'height_percent': 0.50,
            'min_width': 380, 'min_height': 530,  # Increased by 50px
            'max_width': 450, 'max_height': 600   # Increased by 50px
        },
        ScreenSizeClass.SMALL: {
            'width_percent': 0.25, 'height_percent': 0.50,
            'min_width': 380, 'min_height': 530,  # Increased by 50px
            'max_width': 450, 'max_height': 600   # Increased by 50px
        },
        ScreenSizeClass.MEDIUM: {
            'width_percent': 0.23, 'height_percent': 0.45,
            'min_width': 380, 'min_height': 530,  # Increased by 50px
            'max_width': 450, 'max_height': 600   # Increased by 50px
        },
        ScreenSizeClass.LARGE: {
            'width_percent': 0.20, 'height_percent': 0.40,
            'min_width': 380, 'min_height': 530,  # Increased by 50px
            'max_width': 450, 'max_height': 600   # Increased by 50px
        },
        ScreenSizeClass.XLARGE: {
            'width_percent': 0.18, 'height_percent': 0.35,
            'min_width': 380, 'min_height': 530,  # Increased by 50px
            'max_width': 450, 'max_height': 600   # Increased by 50px
        }
    }
    
    DIALOG_SIZING = {
        ScreenSizeClass.XSMALL: {
            'width_percent': 0.90, 'height_percent': 0.80,
            'min_width': 600, 'min_height': 500,
            'max_width': 800, 'max_height': 700
        },
        ScreenSizeClass.SMALL: {
            'width_percent': 0.80, 'height_percent': 0.75,
            'min_width': 650, 'min_height': 550,
            'max_width': 900, 'max_height': 800
        },
        ScreenSizeClass.MEDIUM: {
            'width_percent': 0.70, 'height_percent': 0.70,
            'min_width': 700, 'min_height': 600,
            'max_width': 1000, 'max_height': 900
        },
        ScreenSizeClass.LARGE: {
            'width_percent': 0.60, 'height_percent': 0.65,
            'min_width': 750, 'min_height': 650,
            'max_width': 1100, 'max_height': 1000
        },
        ScreenSizeClass.XLARGE: {
            'width_percent': 0.50, 'height_percent': 0.60,
            'min_width': 800, 'min_height': 700,
            'max_width': 1200, 'max_height': 1100
        }
    }
    
    @staticmethod
    def calculate_window_size(screen_width: int, screen_height: int, 
                            screen_class: ScreenSizeClass = None) -> tuple:
        """Calculate responsive window dimensions based on screen class."""
        if screen_class is None:
            screen_class = ResponsiveBreakpoints.get_screen_size_class(screen_width)
        
        config = ResponsiveSizing.WINDOW_SIZING[screen_class]
        
        # Calculate base dimensions (screen dimensions are already in logical pixels)
        width = int(screen_width * config['width_percent'])
        height = int(screen_height * config['height_percent'])
        
        # Apply constraints (use logical pixel values directly)
        min_width = config['min_width']
        min_height = config['min_height']
        max_width = config['max_width']
        max_height = config['max_height']
        
        width = max(min_width, min(max_width, width))
        height = max(min_height, min(max_height, height))
        
        return width, height
    
    @staticmethod
    def calculate_dialog_size(screen_width: int, screen_height: int,
                             screen_class: ScreenSizeClass = None) -> tuple:
        """Calculate responsive dialog dimensions based on screen class."""
        if screen_class is None:
            screen_class = ResponsiveBreakpoints.get_screen_size_class(screen_width)
        
        config = ResponsiveSizing.DIALOG_SIZING[screen_class]
        dpi_factor = DPIScalingHelper.get_device_pixel_ratio()
        
        # Calculate base dimensions (screen dimensions are already in physical pixels)
        width = int(screen_width * config['width_percent'])
        height = int(screen_height * config['height_percent'])
        
        # Apply constraints (only scale the constraint values, not the calculated dimensions)
        min_width = DPIScalingHelper.scale_pixel_value(config['min_width'], dpi_factor)
        min_height = DPIScalingHelper.scale_pixel_value(config['min_height'], dpi_factor)
        max_width = DPIScalingHelper.scale_pixel_value(config['max_width'], dpi_factor)
        max_height = DPIScalingHelper.scale_pixel_value(config['max_height'], dpi_factor)
        
        width = max(min_width, min(max_width, width))
        height = max(min_height, min(max_height, height))
        
        return width, height


class ComponentFactory:
    """Factory for creating consistent UI components."""
    
    @staticmethod
    def create_spacing_widget(height: int = LayoutTokens.SPACING_MD) -> QWidget:
        """Create a spacing widget for consistent vertical spacing."""
        widget = QWidget()
        widget.setFixedHeight(height)
        return widget
    
    @staticmethod
    def create_divider() -> QWidget:
        """Create a visual divider."""
        widget = QWidget()
        widget.setFixedHeight(1)
        widget.setStyleSheet("background-color: rgba(255, 182, 193, 0.3);")
        return widget
