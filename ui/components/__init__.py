"""
UI Components Module for Whiz Voice-to-Text Application
Contains reusable UI components with consistent styling and behavior.
"""

from .base_components import (
    BaseTab,
    BaseDialog,
    StatusDisplay,
    ActionButton,
    InfoPanel,
    ButtonGroup
)
from .mic_circle import AnimationCircleWidget

__all__ = [
    'BaseTab',
    'BaseDialog', 
    'StatusDisplay',
    'ActionButton',
    'InfoPanel',
    'ButtonGroup',
    'AnimationCircleWidget'
]
