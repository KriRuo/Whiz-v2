"""
Settings manager for Whiz Voice-to-Text application.
Handles QSettings persistence, JSON import/export, and window state management.
"""

import json
import os
import logging
import time
from typing import Any, Dict, Optional, Tuple
from PyQt5.QtCore import QSettings, QByteArray
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from .settings_schema import SETTINGS_SCHEMA

# Set up logging
logger = logging.getLogger(__name__)

class SettingsManager:
    """Manages application settings with QSettings persistence and JSON import/export."""
    
    def __init__(self, organization: str = "Whiz", application: str = "VoiceToText"):
        """
        Initialize the settings manager.
        
        Args:
            organization: Organization name for QSettings
            application: Application name for QSettings
        """
        self.organization = organization
        self.application = application
        self.settings = QSettings(organization, application)
        
        # Settings cache for performance optimization
        self._settings_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[float] = None
        self._cache_valid = False
        
        # Load all settings on initialization
        self._loaded_settings = self.load_all()
        
        logger.info(f"Settings manager initialized for {organization}/{application}")
        logger.info(f"Settings file location: {self.settings.fileName()}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value with validation.
        
        Args:
            key: Setting key (e.g., 'ui/theme')
            default: Default value if key not found
            
        Returns:
            Validated setting value
        """
        if default is None:
            default = SETTINGS_SCHEMA.get_default_value(key)
        
        try:
            # Get raw value from QSettings
            raw_value = self.settings.value(key, default)
            
            # Validate using schema
            if key in SETTINGS_SCHEMA.schema:
                try:
                    validated_value = SETTINGS_SCHEMA.validate_setting(key, raw_value)
                    return validated_value
                except ValueError as e:
                    logger.warning(f"Setting '{key}' validation failed: {e}, using default")
                    return default
            else:
                return raw_value
                
        except Exception as e:
            logger.error(f"Error getting setting '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value with validation.
        
        Args:
            key: Setting key (e.g., 'ui/theme')
            value: Value to set
        """
        try:
            # Validate the value using schema
            if key in SETTINGS_SCHEMA.schema:
                validated_value = SETTINGS_SCHEMA.validate_setting(key, value)
            else:
                validated_value = value
            
            # Store in QSettings
            self.settings.setValue(key, validated_value)
            self.settings.sync()  # Ensure immediate write
            
            # Update loaded settings cache
            self._loaded_settings[key] = validated_value
            
            # Invalidate cache since settings changed
            self._invalidate_cache()
            
            logger.debug(f"Setting '{key}' set to '{validated_value}'")
            
        except Exception as e:
            logger.error(f"Error setting '{key}' to '{value}': {e}")
            raise
    
    def load_all(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load all settings, merging with defaults and applying migration.
        Uses caching for performance optimization.
        
        Args:
            force_reload: If True, bypass cache and reload from QSettings
            
        Returns:
            Dictionary of all settings with validated values
        """
        # Check if we can use cached settings
        if not force_reload and self._cache_valid and self._settings_cache is not None:
            logger.debug("Using cached settings (performance optimization)")
            return self._settings_cache.copy()
        
        logger.debug("Loading settings from QSettings (cache miss or forced reload)")
        
        loaded = {}
        
        # Start with schema defaults
        defaults = SETTINGS_SCHEMA.get_all_defaults()
        
        # Load all settings from QSettings
        for key in self.settings.allKeys():
            try:
                raw_value = self.settings.value(key)
                if key in SETTINGS_SCHEMA.schema:
                    try:
                        validated_value = SETTINGS_SCHEMA.validate_setting(key, raw_value)
                        loaded[key] = validated_value
                    except ValueError as e:
                        logger.warning(f"Setting '{key}' validation failed: {e}, using default")
                        loaded[key] = defaults.get(key)
                else:
                    loaded[key] = raw_value
            except Exception as e:
                logger.error(f"Error loading setting '{key}': {e}")
                loaded[key] = defaults.get(key)
        
        # Add defaults for missing settings
        for key, default_value in defaults.items():
            if key not in loaded:
                loaded[key] = default_value
        
        # Apply migration
        migrated_settings = SETTINGS_SCHEMA.migrate_settings(loaded)
        
        # Update cache
        self._settings_cache = migrated_settings.copy()
        self._cache_timestamp = time.time()
        self._cache_valid = True
        self._loaded_settings = migrated_settings
        
        logger.info(f"Loaded {len(migrated_settings)} settings with schema validation")
        return migrated_settings
    
    def apply_all(self, main_window: QMainWindow) -> None:
        """
        Apply all settings to the main window and its components.
        
        Args:
            main_window: The main application window
        """
        try:
            # Reload settings from QSettings to ensure we have the latest values
            settings = self.load_all()
            
            # Apply theme
            self._apply_theme(main_window, settings.get("ui/theme", "system"))
            
            # Apply behavior settings
            self._apply_behavior_settings(main_window, settings)
            
            # Apply audio settings
            self._apply_audio_settings(main_window, settings)
            
            # Apply Whisper settings
            self._apply_whisper_settings(main_window, settings)
            
            # Always start on Record tab (index 0) - handled by MainWindow
            
            logger.info("All settings applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
    
    def save_window(self, main_window: QMainWindow) -> None:
        """
        Save window geometry and state.
        
        Args:
            main_window: The main application window
        """
        try:
            # Save geometry
            geometry = main_window.saveGeometry()
            self.settings.setValue("window/geometry", geometry)
            
            # Save state
            state = main_window.saveState()
            self.settings.setValue("window/state", state)
            
            self.settings.sync()
            logger.debug("Window geometry and state saved")
            
        except Exception as e:
            logger.error(f"Error saving window state: {e}")
    
    def restore_window(self, main_window: QMainWindow) -> None:
        """
        Restore window geometry and state.
        
        Args:
            main_window: The main application window
        """
        try:
            # Restore geometry
            geometry = self.settings.value("window/geometry")
            if geometry and isinstance(geometry, QByteArray):
                main_window.restoreGeometry(geometry)
                logger.debug("Window geometry restored")
            
            # Restore state
            state = self.settings.value("window/state")
            if state and isinstance(state, QByteArray):
                main_window.restoreState(state)
                logger.debug("Window state restored")
            
        except Exception as e:
            logger.error(f"Error restoring window state: {e}")
    
    def _apply_behavior_settings(self, main_window: QMainWindow, settings: Dict[str, Any]) -> None:
        """Apply behavior settings to the main window."""
        try:
            # Apply behavior settings to controller if available
            if hasattr(main_window, 'controller'):
                controller = main_window.controller
                
                # Update auto-paste if it has changed
                new_auto_paste = settings.get("behavior/auto_paste", True)
                if hasattr(controller, 'set_auto_paste'):
                    controller.set_auto_paste(new_auto_paste)
                    logger.info(f"Auto-paste updated to {new_auto_paste}")
                
                # Update toggle mode if it has changed
                new_toggle_mode = settings.get("behavior/toggle_mode", False)
                if hasattr(controller, 'set_toggle_mode'):
                    controller.set_toggle_mode(new_toggle_mode)
                    logger.info(f"Toggle mode updated to {new_toggle_mode}")
                
                # Update hotkey if it has changed
                new_hotkey = settings.get("behavior/hotkey", "alt gr")
                if hasattr(controller, 'set_hotkey'):
                    controller.set_hotkey(new_hotkey)
                    logger.info(f"Hotkey updated to {new_hotkey}")
                
                # Update visual indicator if it has changed
                new_visual_indicator = settings.get("behavior/visual_indicator", True)
                new_indicator_position = settings.get("behavior/indicator_position", "Bottom Center")
                if hasattr(controller, 'set_visual_indicator'):
                    controller.set_visual_indicator(new_visual_indicator, new_indicator_position)
                    logger.info(f"Visual indicator updated to {new_visual_indicator} at {new_indicator_position}")
                
                # Update visual indicator widget if available
                if hasattr(main_window, 'visual_indicator') and main_window.visual_indicator is not None:
                    try:
                        main_window.visual_indicator.update_position(new_indicator_position)
                        logger.info(f"Visual indicator position updated to {new_indicator_position}")
                    except RuntimeError as e:
                        # Widget has been deleted, ignore the error
                        logger.debug(f"Visual indicator widget no longer available: {e}")
                        main_window.visual_indicator = None
                
                # Update hotkey instruction if available
                if hasattr(main_window, 'update_hotkey_instruction'):
                    main_window.update_hotkey_instruction()
                    logger.info("Hotkey instruction updated")
            
            # Apply minimize to tray setting to main window
            new_minimize_to_tray = settings.get("behavior/minimize_to_tray", False)
            if hasattr(main_window, 'set_minimize_to_tray'):
                main_window.set_minimize_to_tray(new_minimize_to_tray)
                logger.info(f"Minimize to tray updated to {new_minimize_to_tray}")
                    
        except Exception as e:
            logger.error(f"Error applying behavior settings: {e}")
    
    def export_json(self, path: str) -> None:
        """
        Export settings to JSON file.
        
        Args:
            path: Path to export file
        """
        try:
            # Get all settings except binary data
            export_data = {}
            for key, value in self._loaded_settings.items():
                if key in ["window/geometry", "window/state"]:
                    continue  # Skip binary window data only
                
                # Convert to JSON-serializable format
                if isinstance(value, (str, int, float, bool)) or value is None:
                    export_data[key] = value
                else:
                    export_data[key] = str(value)
            
            # Write to file
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings exported to {path}")
            
        except Exception as e:
            logger.error(f"Error exporting settings to {path}: {e}")
            raise
    
    def import_json(self, path: str, merge: bool = True, overwrite: bool = False) -> Dict[str, Any]:
        """
        Import settings from JSON file.
        
        Args:
            path: Path to import file
            merge: If True, merge with existing settings
            overwrite: If True, overwrite existing settings
            
        Returns:
            Dictionary with import results: {applied: [...], invalid: {...}, unknown: [...]}
        """
        try:
            # Read JSON file
            with open(path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            result = {
                "applied": [],
                "invalid": {},
                "unknown": []
            }
            
            # Process each setting
            for key, value in import_data.items():
                if key in SETTINGS_SCHEMA.schema:
                    try:
                        # Validate the value
                        validated_value = SETTINGS_SCHEMA.validate_setting(key, value)
                        
                        # Set the value
                        self.set(key, validated_value)
                        result["applied"].append(key)
                        
                    except Exception as e:
                        logger.warning(f"Invalid value for '{key}': {value} - {e}")
                        result["invalid"][key] = str(e)
                else:
                    logger.warning(f"Unknown setting key: '{key}'")
                    result["unknown"].append(key)
            
            logger.info(f"Settings imported from {path}: {len(result['applied'])} applied")
            return result
            
        except Exception as e:
            logger.error(f"Error importing settings from {path}: {e}")
            raise
    
    def restore_defaults(self) -> None:
        """Restore all settings to their default values."""
        try:
            for key, default_value in SETTINGS_SCHEMA.get_all_defaults().items():
                self.settings.setValue(key, default_value)
            
            self.settings.sync()
            
            # Invalidate cache and reload
            self._invalidate_cache()
            self._loaded_settings = self.load_all(force_reload=True)
            
            logger.info("All settings restored to defaults")
            
        except Exception as e:
            logger.error(f"Error restoring defaults: {e}")
            raise
    
    def _invalidate_cache(self) -> None:
        """Invalidate the settings cache."""
        self._cache_valid = False
        self._settings_cache = None
        self._cache_timestamp = None
        logger.debug("Settings cache invalidated")
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get cache status information for debugging."""
        return {
            "cache_valid": self._cache_valid,
            "cache_timestamp": self._cache_timestamp,
            "cache_age_seconds": time.time() - self._cache_timestamp if self._cache_timestamp else None,
            "cached_settings_count": len(self._settings_cache) if self._settings_cache else 0
        }
    
    def _apply_theme(self, main_window: QMainWindow, theme: str) -> None:
        """Apply theme to the main window."""
        try:
            if hasattr(main_window, 'apply_theme'):
                main_window.apply_theme(theme)
            else:
                logger.warning("Main window does not support theme application")
        except Exception as e:
            logger.error(f"Error applying theme '{theme}': {e}")
    
    def _apply_audio_settings(self, main_window: QMainWindow, settings: Dict[str, Any]) -> None:
        """Apply audio settings to the main window."""
        try:
            # Apply sound effects (use audio/* keys with fallback to legacy sound/*)
            if hasattr(main_window, 'sound_enabled'):
                sound_enabled = settings.get("audio/effects_enabled",
                                            settings.get("sound/enabled", True))
                main_window.sound_enabled = sound_enabled
            
            # Apply tone files (use audio/* keys with fallback to legacy sound/*)
            if hasattr(main_window, 'sound_start') and hasattr(main_window, 'sound_end'):
                start_tone = settings.get("audio/start_tone",
                                         settings.get("sound/start_tone", "assets/sound_start_v9.wav"))
                stop_tone = settings.get("audio/stop_tone",
                                        settings.get("sound/end_tone", "assets/sound_end_v9.wav"))
                
                # Update sound sources if files exist
                if os.path.exists(start_tone):
                    from PyQt5.QtCore import QUrl
                    main_window.sound_start.setSource(QUrl.fromLocalFile(start_tone))
                
                if os.path.exists(stop_tone):
                    from PyQt5.QtCore import QUrl
                    main_window.sound_end.setSource(QUrl.fromLocalFile(stop_tone))
            
            # Apply audio device settings
            self._apply_audio_device_settings(main_window, settings)
            
        except Exception as e:
            logger.error(f"Error applying audio settings: {e}")
    
    def _apply_audio_device_settings(self, main_window: QMainWindow, settings: Dict[str, Any]) -> None:
        """Apply audio device settings to the main window."""
        try:
            # Apply device selection to controller if available
            if hasattr(main_window, 'controller'):
                controller = main_window.controller
                
                # Get saved device preference
                device_index = settings.get("audio/input_device", None)
                device_name = settings.get("audio/input_device_name", "System Default")
                
                # Apply device selection
                if hasattr(controller, 'set_audio_device'):
                    success = controller.set_audio_device(device_index)
                    if success:
                        logger.info(f"Audio device updated to: {device_name}")
                    else:
                        logger.warning(f"Failed to set audio device: {device_name}")
                else:
                    logger.warning("Controller does not support audio device selection")
            
        except Exception as e:
            logger.error(f"Error applying audio device settings: {e}")
    
    def _apply_whisper_settings(self, main_window: QMainWindow, settings: Dict[str, Any]) -> None:
        """Apply Whisper settings to the main window."""
        try:
            # Apply model settings to controller if available
            if hasattr(main_window, 'controller'):
                controller = main_window.controller
                
                # Update model if it has changed
                new_model = settings.get("whisper/model_name", "tiny")
                if hasattr(controller, 'model_size') and controller.model_size != new_model:
                    logger.info(f"Changing model from {controller.model_size} to {new_model}")
                    controller.set_model(new_model)
                
                # Update temperature if it has changed
                new_temperature = settings.get("whisper/temperature", 0.0)
                if hasattr(controller, 'temperature') and controller.temperature != new_temperature:
                    controller.temperature = new_temperature
                    logger.info(f"Temperature updated to {new_temperature}")
                
                # Update speed mode if it has changed
                new_speed_mode = settings.get("whisper/speed_mode", True)
                if hasattr(controller, 'speed_mode') and controller.speed_mode != new_speed_mode:
                    controller.speed_mode = new_speed_mode
                    logger.info(f"Speed mode updated to {new_speed_mode}")
            
        except Exception as e:
            logger.error(f"Error applying Whisper settings: {e}")
    
    def get_settings_file_path(self) -> str:
        """Get the path to the settings file."""
        return self.settings.fileName()
    
    def clear_all(self) -> None:
        """Clear all settings (use with caution)."""
        try:
            self.settings.clear()
            self.settings.sync()
            self._loaded_settings = self.load_all()
            logger.info("All settings cleared")
        except Exception as e:
            logger.error(f"Error clearing settings: {e}")
            raise
