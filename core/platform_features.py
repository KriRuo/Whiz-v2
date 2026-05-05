"""
Platform Feature Detection

This module detects available features and capabilities on the current platform,
enabling graceful degradation when features are unavailable.
"""

import sys
from typing import Dict, Any, Optional
from enum import Enum

from .platform_utils import PlatformUtils, PlatformType
from .logging_config import get_logger
logger = get_logger(__name__)

class FeatureStatus(Enum):
    """Feature availability status"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    LIMITED = "limited"
    UNKNOWN = "unknown"

class PlatformFeatures:
    """Platform feature detection and capability checking"""
    
    def __init__(self):
        self._features_cache: Optional[Dict[str, Any]] = None
        self._platform_info = PlatformUtils.get_platform_info()
        
        logger.info(f"PlatformFeatures initialized for {self._platform_info['platform']}")
    
    def detect_all_features(self) -> Dict[str, Any]:
        """
        Detect all available features on the current platform.
        
        Returns:
            Dictionary with feature availability status
        """
        if self._features_cache is not None:
            return self._features_cache
        
        features = {
            "audio": self._detect_audio_features(),
            "hotkeys": self._detect_hotkey_features(),
            "autopaste": self._detect_autopaste_features(),
            "system_integration": self._detect_system_integration(),
            "permissions": self._detect_permissions(),
            "ui_features": self._detect_ui_features()
        }
        
        self._features_cache = features
        logger.info("Feature detection completed")
        return features
    
    def _detect_audio_features(self) -> Dict[str, Any]:
        """Detect audio-related features"""
        features = {
            "recording": FeatureStatus.UNAVAILABLE,
            "playback": FeatureStatus.UNAVAILABLE,
            "device_selection": FeatureStatus.UNAVAILABLE,
            "real_time_levels": FeatureStatus.UNAVAILABLE
        }
        
        try:
            import sounddevice as sd
            # Query once and reuse — each call polls all audio drivers.
            devices = sd.query_devices()

            features["device_selection"] = FeatureStatus.AVAILABLE
            features["real_time_levels"] = FeatureStatus.AVAILABLE
            features["recording"] = (
                FeatureStatus.AVAILABLE
                if any(d['max_input_channels'] > 0 for d in devices)
                else FeatureStatus.UNAVAILABLE
            )
            features["playback"] = (
                FeatureStatus.AVAILABLE
                if any(d['max_output_channels'] > 0 for d in devices)
                else FeatureStatus.UNAVAILABLE
            )
        except ImportError:
            logger.warning("sounddevice not available")
        except Exception as e:
            logger.warning(f"Audio detection error: {e}")
        
        return features
    
    def _detect_hotkey_features(self) -> Dict[str, Any]:
        """Detect hotkey-related features"""
        features = {
            "global_hotkeys": FeatureStatus.UNAVAILABLE,
            "key_combination": FeatureStatus.UNAVAILABLE,
            "permissions_required": False
        }
        
        try:
            # Check for pynput
            from pynput import keyboard
            
            features["global_hotkeys"] = FeatureStatus.AVAILABLE
            features["key_combination"] = FeatureStatus.AVAILABLE
            
            # Check platform-specific requirements
            platform = PlatformUtils.get_platform()
            
            features["permissions_required"] = False
            
        except ImportError:
            logger.warning("pynput not available")
        except Exception as e:
            logger.warning(f"Hotkey detection error: {e}")
        
        return features
    
    def _detect_autopaste_features(self) -> Dict[str, Any]:
        """Detect auto-paste related features"""
        features = {
            "clipboard_access": FeatureStatus.UNAVAILABLE,
            "text_pasting": FeatureStatus.UNAVAILABLE,
            "permissions_required": False
        }
        
        try:
            # Check for pyautogui
            import pyautogui

            features["text_pasting"] = FeatureStatus.AVAILABLE

            # Check clipboard access by import only — avoid writing to the clipboard
            # at startup (Win32 OpenClipboard is a cooperative mutex and can block if
            # another process holds the lock).
            try:
                import pyperclip  # noqa: F401
                features["clipboard_access"] = FeatureStatus.AVAILABLE
            except ImportError:
                features["clipboard_access"] = FeatureStatus.UNAVAILABLE

            features["permissions_required"] = False

        except ImportError:
            logger.warning("pyautogui not available")
        except Exception as e:
            logger.warning(f"Auto-paste detection error: {e}")
        
        return features
    
    def _detect_system_integration(self) -> Dict[str, Any]:
        """Detect system integration features"""
        features = {
            "notifications": FeatureStatus.UNAVAILABLE,
            "system_tray": FeatureStatus.UNAVAILABLE,
            "startup_integration": FeatureStatus.UNAVAILABLE,
            "file_associations": FeatureStatus.UNAVAILABLE
        }
        
        platform = PlatformUtils.get_platform()
        
        features["notifications"] = FeatureStatus.AVAILABLE
        features["system_tray"] = FeatureStatus.AVAILABLE
        features["startup_integration"] = FeatureStatus.AVAILABLE
        features["file_associations"] = FeatureStatus.AVAILABLE
        
        return features
    
    def _detect_permissions(self) -> Dict[str, Any]:
        """Detect current permissions and requirements"""
        features = {
            "admin_required": False,
            "accessibility_required": False,
            "microphone_required": True,
            "current_permissions": []
        }
        
        platform = PlatformUtils.get_platform()
        
        # Check admin/root status
        if PlatformUtils.is_admin():
            features["current_permissions"].append("admin")
        else:
            features["admin_required"] = False  # Not required for basic functionality
        
        features["accessibility_required"] = False
        
        return features
    
    def _detect_ui_features(self) -> Dict[str, Any]:
        """Detect UI-related features"""
        features = {
            "custom_titlebar": FeatureStatus.UNAVAILABLE,
            "dark_mode": FeatureStatus.UNAVAILABLE,
            "high_dpi": FeatureStatus.UNAVAILABLE,
            "transparency": FeatureStatus.UNAVAILABLE
        }
        
        platform = PlatformUtils.get_platform()
        
        features["custom_titlebar"] = FeatureStatus.AVAILABLE
        features["dark_mode"] = FeatureStatus.AVAILABLE
        features["high_dpi"] = FeatureStatus.AVAILABLE
        features["transparency"] = FeatureStatus.AVAILABLE
        
        return features
    
    def is_feature_available(self, feature_path: str) -> bool:
        """
        Check if a specific feature is available.
        
        Args:
            feature_path: Dot-separated path to feature (e.g., 'audio.recording')
            
        Returns:
            True if feature is available, False otherwise
        """
        features = self.detect_all_features()
        
        # Navigate through nested dictionary
        current = features
        for part in feature_path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        
        # Check if it's a FeatureStatus enum
        if isinstance(current, FeatureStatus):
            return current in [FeatureStatus.AVAILABLE, FeatureStatus.LIMITED]
        
        return bool(current)
    
    def get_feature_status(self, feature_path: str) -> FeatureStatus:
        """
        Get the status of a specific feature.
        
        Args:
            feature_path: Dot-separated path to feature
            
        Returns:
            FeatureStatus enum value
        """
        features = self.detect_all_features()
        
        # Navigate through nested dictionary
        current = features
        for part in feature_path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return FeatureStatus.UNKNOWN
        
        # Return the status if it's a FeatureStatus enum
        if isinstance(current, FeatureStatus):
            return current
        
        return FeatureStatus.UNKNOWN
    
    def get_missing_features(self) -> Dict[str, Any]:
        """
        Get information about missing or limited features.
        
        Returns:
            Dictionary with missing feature information
        """
        features = self.detect_all_features()
        missing = {}
        
        def check_feature(path: str, feature_dict: dict, prefix: str = ""):
            for key, value in feature_dict.items():
                current_path = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, FeatureStatus):
                    if value == FeatureStatus.UNAVAILABLE:
                        missing[current_path] = {
                            "status": value,
                            "message": f"Feature '{current_path}' is not available on this platform"
                        }
                    elif value == FeatureStatus.LIMITED:
                        missing[current_path] = {
                            "status": value,
                            "message": f"Feature '{current_path}' has limited functionality on this platform"
                        }
                elif isinstance(value, dict):
                    check_feature(current_path, value, current_path)
        
        check_feature("", features)
        return missing
    
    def get_recommendations(self) -> Dict[str, Any]:
        """
        Get recommendations for improving feature availability.
        
        Returns:
            Dictionary with recommendations
        """
        recommendations = {
            "install_packages": [],
            "enable_permissions": [],
            "system_requirements": [],
            "workarounds": []
        }
        
        features = self.detect_all_features()
        
        # Check for missing packages
        if not self.is_feature_available("audio.recording"):
            recommendations["install_packages"].append("sounddevice")
        
        if not self.is_feature_available("hotkeys.global_hotkeys"):
            recommendations["install_packages"].append("pynput")
        
        if not self.is_feature_available("autopaste.text_pasting"):
            recommendations["install_packages"].append("pyautogui")
        
        return recommendations
