#!/usr/bin/env python3
"""
core/settings_schema.py
-----------------------
Comprehensive settings schema and validation for Whiz Voice-to-Text Application.

This module provides a complete schema definition for all application settings
with validation, type checking, and migration support.

Features:
    - Complete schema definition for all settings
    - Type validation and range checking
    - Schema versioning and migration
    - Default value management
    - Validation error reporting

Author: Whiz Development Team
Last Updated: December 2024
"""

import re
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum
from dataclasses import dataclass
from .logging_config import get_logger

logger = get_logger(__name__)

class SettingType(Enum):
    """Types of settings"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"
    LIST = "list"
    DICT = "dict"

@dataclass
class SettingSchema:
    """Schema definition for a single setting"""
    key: str
    type: SettingType
    default: Any
    description: str
    validator: Optional[Callable[[Any], Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    pattern: Optional[str] = None
    required: bool = True
    deprecated: bool = False
    migration_path: Optional[str] = None

class SettingsSchema:
    """Comprehensive settings schema with validation and migration"""
    
    # Schema version for migration
    SCHEMA_VERSION = "2.0"
    
    def __init__(self):
        self.schema: Dict[str, SettingSchema] = {}
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Initialize the complete settings schema"""
        
    # UI Settings
        self.schema["ui/theme"] = SettingSchema(
            key="ui/theme",
            type=SettingType.ENUM,
            default="dark",
            description="Application theme",
            allowed_values=["light", "dark", "auto"],
            validator=self._validate_theme
        )
        
        self.schema["ui/window_width"] = SettingSchema(
            key="ui/window_width",
            type=SettingType.INTEGER,
            default=400,  # Changed from 800
            description="Main window width",
            min_value=380,  # Changed from 400
            max_value=450,  # Changed from 2000
            validator=self._validate_window_size
        )
        
        self.schema["ui/window_height"] = SettingSchema(
            key="ui/window_height",
            type=SettingType.INTEGER,
            default=550,  # Increased by 50px to match responsive sizing
            description="Main window height",
            min_value=530,  # Increased by 50px
            max_value=600,  # Increased by 50px
            validator=self._validate_window_size
        )
        
        
        self.schema["ui/start_minimized"] = SettingSchema(
            key="ui/start_minimized",
            type=SettingType.BOOLEAN,
            default=False,
            description="Start application minimized"
        )
    
    # Behavior Settings
        self.schema["behavior/hotkey"] = SettingSchema(
            key="behavior/hotkey",
            type=SettingType.STRING,
            default="alt gr",
            description="Global hotkey for recording",
            validator=self._validate_hotkey
        )
        
        self.schema["behavior/auto_paste"] = SettingSchema(
            key="behavior/auto_paste",
            type=SettingType.BOOLEAN,
            default=True,
            description="Automatically paste transcribed text"
        )
        
        self.schema["behavior/visual_indicator"] = SettingSchema(
            key="behavior/visual_indicator",
            type=SettingType.BOOLEAN,
            default=True,
            description="Show visual recording indicator"
        )
        
        self.schema["behavior/indicator_position"] = SettingSchema(
            key="behavior/indicator_position",
            type=SettingType.ENUM,
            default="Bottom Center",
            description="Position of visual indicator",
            allowed_values=["Top Left", "Top Center", "Top Right", 
                          "Middle Left", "Middle Center", "Middle Right",
                          "Bottom Left", "Bottom Center", "Bottom Right"],
            validator=self._validate_indicator_position
        )
        
        self.schema["behavior/toggle_mode"] = SettingSchema(
            key="behavior/toggle_mode",
            type=SettingType.BOOLEAN,
            default=False,
            description="Use toggle mode instead of hold mode for hotkey"
        )
        
        self.schema["behavior/minimize_to_tray"] = SettingSchema(
            key="behavior/minimize_to_tray",
            type=SettingType.BOOLEAN,
            default=False,
            description="Minimize to system tray instead of closing"
        )
    
    # Audio Settings
        self.schema["audio/input_device"] = SettingSchema(
            key="audio/input_device",
            type=SettingType.INTEGER,
            default=None,
            description="Audio input device index",
            min_value=0,
            required=False,  # Allow None for system default
            validator=self._validate_device_index
        )
        
        self.schema["audio/sample_rate"] = SettingSchema(
            key="audio/sample_rate",
            type=SettingType.INTEGER,
            default=16000,
            description="Audio sample rate",
            allowed_values=[8000, 16000, 22050, 44100, 48000],
            validator=self._validate_sample_rate
        )
        
        self.schema["audio/channels"] = SettingSchema(
            key="audio/channels",
            type=SettingType.INTEGER,
            default=1,
            description="Number of audio channels",
            min_value=1,
            max_value=2,
            validator=self._validate_channels
        )
        
        self.schema["audio/chunk_size"] = SettingSchema(
            key="audio/chunk_size",
            type=SettingType.INTEGER,
            default=1024,
            description="Audio chunk size",
            min_value=256,
            max_value=4096,
            validator=self._validate_chunk_size
        )
        
        self.schema["audio/effects_enabled"] = SettingSchema(
            key="audio/effects_enabled",
            type=SettingType.BOOLEAN,
            default=True,
            description="Enable start/stop sound effects"
        )
        
        self.schema["audio/start_tone"] = SettingSchema(
            key="audio/start_tone",
            type=SettingType.STRING,
            default="assets/sound_start_v9.wav",
            description="Path to start recording tone file",
            validator=self._validate_sound_file
        )
        
        self.schema["audio/stop_tone"] = SettingSchema(
            key="audio/stop_tone",
            type=SettingType.STRING,
            default="assets/sound_end_v9.wav",
            description="Path to stop recording tone file",
            validator=self._validate_sound_file
        )
        
        self.schema["audio/input_device_name"] = SettingSchema(
            key="audio/input_device_name",
            type=SettingType.STRING,
            default="System Default",
            description="Display name for selected audio input device"
        )
    
    # Whisper Settings
        self.schema["whisper/engine"] = SettingSchema(
            key="whisper/engine",
            type=SettingType.ENUM,
            default="faster",
            description="Whisper engine: 'faster' (5-10x faster, recommended) or 'openai' (original implementation)",
            allowed_values=["openai", "faster"],
            validator=self._validate_whisper_engine
        )
        
        self.schema["whisper/model_name"] = SettingSchema(
            key="whisper/model_name",
            type=SettingType.ENUM,
            default="tiny",
            description="Whisper model size",
            allowed_values=["tiny", "base", "small", "medium", "large"],
            validator=self._validate_model_name
        )
        
        self.schema["whisper/language"] = SettingSchema(
            key="whisper/language",
            type=SettingType.STRING,
            default="auto",
            description="Language for transcription",
            validator=self._validate_language
        )
        
        self.schema["whisper/temperature"] = SettingSchema(
            key="whisper/temperature",
            type=SettingType.FLOAT,
            default=0.0,
            description="Temperature for transcription",
            min_value=0.0,
            max_value=1.0,
            validator=self._validate_temperature
        )
        
        self.schema["whisper/speed_mode"] = SettingSchema(
            key="whisper/speed_mode",
            type=SettingType.BOOLEAN,
            default=True,
            description="Enable speed optimizations"
        )
        
        # Advanced Settings
        self.schema["advanced/expert_mode"] = SettingSchema(
            key="advanced/expert_mode",
            type=SettingType.BOOLEAN,
            default=False,
            description="Enable expert mode settings"
        )
        
        self.schema["advanced/log_level"] = SettingSchema(
            key="advanced/log_level",
            type=SettingType.ENUM,
            default="INFO",
            description="Logging level",
            allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            validator=self._validate_log_level
        )
        
        self.schema["advanced/log_to_file"] = SettingSchema(
            key="advanced/log_to_file",
            type=SettingType.BOOLEAN,
            default=True,
            description="Log to file"
        )
        
        self.schema["advanced/log_to_console"] = SettingSchema(
            key="advanced/log_to_console",
            type=SettingType.BOOLEAN,
            default=True,
            description="Log to console"
        )
        
        # (Removed legacy sound/* keys in favor of audio/* namespace)
        
        # Migration mappings for deprecated settings
        self._migration_mappings = {
            "audio/device": "audio/input_device",  # Old key -> new key
            "whisper/model_size": "whisper/model_name",  # Old key -> new key
            "theme": "ui/theme",  # Old key -> new key
            "model_size": "whisper/model_name",  # Old key -> new key
            "auto_paste": "behavior/auto_paste",  # Old key -> new key
            "ui/minimize_to_tray": "behavior/minimize_to_tray",  # Consolidate to behavior namespace
            # Legacy sound/* to audio/* mappings
            "sound/enabled": "audio/effects_enabled",
            "sound/start_tone": "audio/start_tone",
            "sound/end_tone": "audio/stop_tone",
            # Legacy hotkey_mode enum to toggle_mode boolean
            "behavior/hotkey_mode": "behavior/toggle_mode",
        }
    
    def validate_setting(self, key: str, value: Any) -> Any:
        """
        Validate a setting value against its schema.
        
        Args:
            key: Setting key
            value: Value to validate
            
        Returns:
            Validated value
            
        Raises:
            ValueError: If validation fails
        """
        if key not in self.schema:
            logger.warning(f"Unknown setting key: {key}")
            return value
    
        schema = self.schema[key]
        
        # Check if setting is deprecated
        if schema.deprecated:
            logger.warning(f"Setting '{key}' is deprecated")
        
        # Type validation
        validated_value = self._validate_type(value, schema)
        
        # Range validation
        if schema.min_value is not None and validated_value is not None and validated_value < schema.min_value:
            raise ValueError(f"Setting '{key}' value {validated_value} is below minimum {schema.min_value}")
        
        if schema.max_value is not None and validated_value is not None and validated_value > schema.max_value:
            raise ValueError(f"Setting '{key}' value {validated_value} is above maximum {schema.max_value}")
        
        # Allowed values validation
        if schema.allowed_values is not None and validated_value not in schema.allowed_values:
            raise ValueError(f"Setting '{key}' value '{validated_value}' not in allowed values: {schema.allowed_values}")
        
        # Pattern validation
        if schema.pattern is not None:
            if not re.match(schema.pattern, str(validated_value)):
                raise ValueError(f"Setting '{key}' value '{validated_value}' doesn't match pattern '{schema.pattern}'")
        
        # Custom validator
        if schema.validator:
            try:
                validated_value = schema.validator(validated_value)
            except Exception as e:
                raise ValueError(f"Setting '{key}' validation failed: {e}")
        
        return validated_value
    
    def get_default_value(self, key: str) -> Any:
        """Get the default value for a setting"""
        if key in self.schema:
            return self.schema[key].default
        return None
    
    def get_all_defaults(self) -> Dict[str, Any]:
        """Get all default values"""
        return {key: schema.default for key, schema in self.schema.items()}
    
    def migrate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate settings from old schema versions.
        
        Args:
            settings: Current settings dictionary
            
        Returns:
            Migrated settings dictionary
        """
        migrated = settings.copy()
        
        # Apply migration mappings
        for old_key, new_key in self._migration_mappings.items():
            if old_key in migrated and new_key not in migrated:
                logger.info(f"Migrating setting '{old_key}' to '{new_key}'")
                
                # Special handling for hotkey_mode enum to toggle_mode boolean
                if old_key == "behavior/hotkey_mode" and new_key == "behavior/toggle_mode":
                    old_value = migrated[old_key]
                    if old_value == "toggle":
                        migrated[new_key] = True
                    elif old_value == "hold":
                        migrated[new_key] = False
                    else:
                        # Default to False (hold mode) for unknown values
                        migrated[new_key] = False
                        logger.warning(f"Unknown hotkey_mode value '{old_value}', defaulting to False")
                else:
                    migrated[new_key] = migrated[old_key]
                
                del migrated[old_key]
        
        # Add schema version
        migrated["_schema_version"] = self.SCHEMA_VERSION
        
        return migrated
    
    def _validate_type(self, value: Any, schema: SettingSchema) -> Any:
        """Validate and convert value to correct type"""
        try:
            # Handle None values for optional settings
            if value is None and not schema.required:
                return None
            
            if schema.type == SettingType.STRING:
                return str(value)
            elif schema.type == SettingType.INTEGER:
                if value is None:
                    return None
                return int(value)
            elif schema.type == SettingType.FLOAT:
                if value is None:
                    return None
                return float(value)
            elif schema.type == SettingType.BOOLEAN:
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                else:
                    return bool(value)
            elif schema.type == SettingType.ENUM:
                return str(value)
            elif schema.type == SettingType.LIST:
                if isinstance(value, list):
                    return value
                elif isinstance(value, str):
                    return [item.strip() for item in value.split(',')]
                else:
                    return [value]
            elif schema.type == SettingType.DICT:
                if isinstance(value, dict):
                    return value
                else:
                    return {}
            else:
                return value
        except (ValueError, TypeError) as e:
            raise ValueError(f"Type conversion failed: {e}")
    
    # Custom validators
    def _validate_theme(self, value: str) -> str:
        """Validate theme setting"""
        if value not in ["light", "dark", "auto"]:
            raise ValueError(f"Invalid theme: {value}")
        return value

    def _validate_window_size(self, value: int) -> int:
        """Validate window size"""
        if not isinstance(value, int) or value < 100:
            raise ValueError(f"Invalid window size: {value}")
        return value
    
    def _validate_hotkey(self, value: str) -> str:
        """Validate hotkey setting"""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Hotkey cannot be empty")
        
        # Basic hotkey validation
        parts = [part.strip().lower() for part in value.split('+')]
        valid_modifiers = ['ctrl', 'alt', 'shift', 'cmd', 'win', 'alt gr']
        valid_keys = ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
                     'caps lock', 'space', 'enter', 'tab', 'escape', 'esc', 'backspace', 'delete',
                     'home', 'end', 'page up', 'page down', 'insert', 'print screen', 'scroll lock',
                     'pause', 'break', 'num lock', 'menu', 'left', 'right', 'up', 'down']
        
        for part in parts:
            if part not in valid_modifiers and part not in valid_keys and not part.isalnum():
                raise ValueError(f"Invalid hotkey component: {part}")
        
        return value
    
    def _validate_hotkey_mode(self, value: str) -> str:
        """Validate hotkey mode"""
        if value not in ["hold", "toggle"]:
            raise ValueError(f"Invalid hotkey mode: {value}")
        return value
    
    def _validate_indicator_position(self, value: str) -> str:
        """Validate indicator position"""
        valid_positions = ["Top Left", "Top Center", "Top Right", 
                          "Middle Left", "Middle Center", "Middle Right",
                          "Bottom Left", "Bottom Center", "Bottom Right"]
        if value not in valid_positions:
            raise ValueError(f"Invalid indicator position: {value}")
        return value
    
    def _validate_device_index(self, value: Any) -> Optional[int]:
        """Validate device index"""
        if value is None:
            return None
        try:
            int_value = int(value)
            if int_value < 0:
                raise ValueError(f"Invalid device index: {int_value}")
            return int_value
        except (ValueError, TypeError):
            raise ValueError(f"Invalid device index: {value}")
    
    def _validate_sample_rate(self, value: int) -> int:
        """Validate sample rate"""
        valid_rates = [8000, 16000, 22050, 44100, 48000]
        if value not in valid_rates:
            raise ValueError(f"Invalid sample rate: {value}")
        return value
    
    def _validate_channels(self, value: int) -> int:
        """Validate channel count"""
        if value not in [1, 2]:
            raise ValueError(f"Invalid channel count: {value}")
        return value
    
    def _validate_chunk_size(self, value: int) -> int:
        """Validate chunk size"""
        if not isinstance(value, int) or value < 256 or value > 4096:
            raise ValueError(f"Invalid chunk size: {value}")
        return value
    
    def _validate_whisper_engine(self, value: str) -> str:
        """Validate Whisper engine"""
        if value not in ["openai", "faster"]:
            raise ValueError(f"Invalid Whisper engine: {value}")
        return value
    
    def _validate_model_name(self, value: str) -> str:
        """Validate model name"""
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if value not in valid_models:
            raise ValueError(f"Invalid model name: {value}")
        return value
    
    def _validate_language(self, value: str) -> str:
        """Validate language setting"""
        if value == "auto":
            return value
        
        # Basic language code validation (ISO 639-1)
        if not isinstance(value, str) or len(value) != 2:
            raise ValueError(f"Invalid language code: {value}")
        
        return value.lower()
    
    def _validate_temperature(self, value: float) -> float:
        """Validate temperature setting"""
        if not isinstance(value, (int, float)) or value < 0.0 or value > 1.0:
            raise ValueError(f"Invalid temperature: {value}")
        return float(value)
    
    def _validate_log_level(self, value: str) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value not in valid_levels:
            raise ValueError(f"Invalid log level: {value}")
        return value
    
    def _validate_sound_file(self, value: str) -> str:
        """Validate sound file path"""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Sound file path cannot be empty")
        
        # Basic file extension validation - be more flexible for asset files
        valid_extensions = ('.wav', '.mp3', '.ogg', '.m4a', '.aac')
        if not value.lower().endswith(valid_extensions):
            # Allow asset paths without extension validation
            if value.startswith('assets/'):
                return value
            raise ValueError(f"Invalid sound file format: {value}")
        
        return value

# Global schema instance
SETTINGS_SCHEMA = SettingsSchema()