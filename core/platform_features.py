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
            # Check for sounddevice
            import sounddevice as sd
            features["recording"] = FeatureStatus.AVAILABLE
            features["device_selection"] = FeatureStatus.AVAILABLE
            features["real_time_levels"] = FeatureStatus.AVAILABLE
            
            # Check for available devices
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            
            if len(input_devices) > 0:
                features["recording"] = FeatureStatus.AVAILABLE
            else:
                features["recording"] = FeatureStatus.UNAVAILABLE
                
        except ImportError:
            logger.warning("sounddevice not available")
        except Exception as e:
            logger.warning(f"Audio detection error: {e}")
        
        try:
            # Check for playback capabilities
            import sounddevice as sd
            devices = sd.query_devices()
            output_devices = [d for d in devices if d['max_output_channels'] > 0]
            
            if len(output_devices) > 0:
                features["playback"] = FeatureStatus.AVAILABLE
                
        except Exception as e:
            logger.warning(f"Playback detection error: {e}")
        
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
            
            if platform == PlatformType.MACOS:
                # macOS requires accessibility permissions
                features["permissions_required"] = True
                features["permission_type"] = "accessibility"
                features["permission_message"] = (
                    "macOS requires accessibility permissions for global hotkeys. "
                    "Please enable 'Whiz' in System Preferences > Security & Privacy > Privacy > Accessibility."
                )
            elif platform == PlatformType.LINUX:
                # Linux may require X11 or Wayland
                if sys.platform.startswith('linux'):
                    display = sys.environ.get('DISPLAY')
                    wayland_display = sys.environ.get('WAYLAND_DISPLAY')
                    
                    if display or wayland_display:
                        features["permissions_required"] = False
                    else:
                        features["permissions_required"] = True
                        features["permission_type"] = "display_server"
                        features["permission_message"] = (
                            "Linux requires a display server (X11 or Wayland) for global hotkeys."
                        )
            elif platform == PlatformType.WINDOWS:
                # Windows generally works without special permissions
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
            
            # Check clipboard access
            try:
                import pyperclip
                pyperclip.copy("test")
                test_content = pyperclip.paste()
                if test_content == "test":
                    features["clipboard_access"] = FeatureStatus.AVAILABLE
                else:
                    features["clipboard_access"] = FeatureStatus.LIMITED
            except:
                features["clipboard_access"] = FeatureStatus.UNAVAILABLE
            
            # Check platform-specific requirements
            platform = PlatformUtils.get_platform()
            
            if platform == PlatformType.MACOS:
                # macOS may require accessibility permissions for text pasting
                features["permissions_required"] = True
                features["permission_type"] = "accessibility"
                features["permission_message"] = (
                    "macOS may require accessibility permissions for auto-paste. "
                    "Please enable 'Whiz' in System Preferences > Security & Privacy > Privacy > Accessibility."
                )
            elif platform == PlatformType.LINUX:
                # Linux may require X11 or Wayland
                if sys.platform.startswith('linux'):
                    display = sys.environ.get('DISPLAY')
                    wayland_display = sys.environ.get('WAYLAND_DISPLAY')
                    
                    if not (display or wayland_display):
                        features["permissions_required"] = True
                        features["permission_type"] = "display_server"
                        features["permission_message"] = (
                            "Linux requires a display server (X11 or Wayland) for auto-paste."
                        )
            
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
        
        if platform == PlatformType.WINDOWS:
            features["notifications"] = FeatureStatus.AVAILABLE
            features["system_tray"] = FeatureStatus.AVAILABLE
            features["startup_integration"] = FeatureStatus.AVAILABLE
            features["file_associations"] = FeatureStatus.AVAILABLE
            
        elif platform == PlatformType.MACOS:
            features["notifications"] = FeatureStatus.AVAILABLE
            features["system_tray"] = FeatureStatus.LIMITED  # Menu bar instead
            features["startup_integration"] = FeatureStatus.AVAILABLE
            features["file_associations"] = FeatureStatus.AVAILABLE
            
        elif platform == PlatformType.LINUX:
            # Linux depends on desktop environment
            desktop = sys.environ.get('XDG_CURRENT_DESKTOP', '').lower()
            
            if desktop in ['gnome', 'kde', 'xfce', 'lxde', 'mate']:
                features["notifications"] = FeatureStatus.AVAILABLE
                features["system_tray"] = FeatureStatus.AVAILABLE
                features["startup_integration"] = FeatureStatus.AVAILABLE
            else:
                features["notifications"] = FeatureStatus.LIMITED
                features["system_tray"] = FeatureStatus.LIMITED
                features["startup_integration"] = FeatureStatus.LIMITED
            
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
        
        # Check platform-specific requirements
        if platform == PlatformType.MACOS:
            features["accessibility_required"] = True
            features["permission_instructions"] = {
                "accessibility": "System Preferences > Security & Privacy > Privacy > Accessibility",
                "microphone": "System Preferences > Security & Privacy > Privacy > Microphone"
            }
        elif platform == PlatformType.LINUX:
            features["accessibility_required"] = False  # Depends on desktop environment
        elif platform == PlatformType.WINDOWS:
            features["accessibility_required"] = False  # Generally not required
        
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
        
        if platform == PlatformType.WINDOWS:
            features["custom_titlebar"] = FeatureStatus.AVAILABLE
            features["dark_mode"] = FeatureStatus.AVAILABLE
            features["high_dpi"] = FeatureStatus.AVAILABLE
            features["transparency"] = FeatureStatus.AVAILABLE
            
        elif platform == PlatformType.MACOS:
            features["custom_titlebar"] = FeatureStatus.LIMITED  # Different approach needed
            features["dark_mode"] = FeatureStatus.AVAILABLE
            features["high_dpi"] = FeatureStatus.AVAILABLE
            features["transparency"] = FeatureStatus.AVAILABLE
            
        elif platform == PlatformType.LINUX:
            features["custom_titlebar"] = FeatureStatus.LIMITED  # Depends on window manager
            features["dark_mode"] = FeatureStatus.AVAILABLE
            features["high_dpi"] = FeatureStatus.LIMITED  # Depends on desktop environment
            features["transparency"] = FeatureStatus.LIMITED  # Depends on compositor
        
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
        
        # Check for permission requirements
        permissions = features.get("permissions", {})
        if permissions.get("accessibility_required", False):
            platform = PlatformUtils.get_platform()
            if platform == PlatformType.MACOS:
                recommendations["enable_permissions"].append({
                    "type": "accessibility",
                    "description": "Enable accessibility permissions for global hotkeys",
                    "instructions": "System Preferences > Security & Privacy > Privacy > Accessibility"
                })
        
        # Check for system requirements
        platform = PlatformUtils.get_platform()
        if platform == PlatformType.LINUX:
            if not sys.environ.get('DISPLAY') and not sys.environ.get('WAYLAND_DISPLAY'):
                recommendations["system_requirements"].append({
                    "requirement": "Display Server",
                    "description": "Linux requires X11 or Wayland for GUI features",
                    "solutions": ["Install X11 server", "Use Wayland session"]
                })
        
        return recommendations
