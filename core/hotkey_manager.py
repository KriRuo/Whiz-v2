#!/usr/bin/env python3
"""
core/hotkey_manager.py
---------------------
Cross-platform hotkey management for Whiz Voice-to-Text Application.

This module provides a unified interface for global hotkey registration
across different platforms using pynput. It replaces platform-specific
keyboard libraries with a more reliable and cross-platform solution.

Features:
    - Cross-platform hotkey registration (Windows, macOS, Linux)
    - Hold and toggle mode support
    - Thread-safe hotkey management
    - Graceful degradation when input is unavailable
    - Configurable hotkey combinations
    - Event callback system

Dependencies:
    - pynput: Cross-platform input handling
    - threading: Thread-safe operations
    - enum: Mode enumeration

Example:
    Basic usage:
        from core.hotkey_manager import HotkeyManager, HotkeyMode
        
        hotkey_manager = HotkeyManager()
        if hotkey_manager.is_available():
            hotkey_manager.set_hotkey("alt gr")
            hotkey_manager.set_mode(HotkeyMode.HOLD)
            hotkey_manager.start_listening()

Author: Whiz Development Team
Last Updated: October 10, 2025
"""

import threading
from typing import Optional, Callable, Dict, Any, List
from enum import Enum

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    keyboard = None

from .logging_config import get_logger
logger = get_logger(__name__)

class HotkeyMode(Enum):
    """Hotkey operation modes"""
    HOLD = "hold"  # Hold key to record, release to stop
    TOGGLE = "toggle"  # Press once to start, press again to stop

class HotkeyManager:
    """
    Cross-platform hotkey manager using pynput.
    
    Provides the same interface as the original keyboard-based implementation
    but with better cross-platform support and no root/admin requirements.
    """
    
    def __init__(self):
        self.hotkey: Optional[str] = None
        self.mode: HotkeyMode = HotkeyMode.HOLD
        self.is_listening: bool = False
        self.listener: Optional[keyboard.Listener] = None
        self.is_recording: bool = False
        
        # Modifier key state tracking
        self._modifier_states: Dict[str, bool] = {
            'ctrl': False,
            'alt': False,
            'shift': False,
            'cmd': False,  # Command key on macOS
            'alt gr': False,
            'win': False   # Windows key
        }
        
        # Parsed hotkey components
        self._hotkey_modifiers: List[str] = []
        self._hotkey_main_key: Optional[str] = None
        
        # Callbacks
        self.on_start_recording: Optional[Callable[[], None]] = None
        self.on_stop_recording: Optional[Callable[[], None]] = None
        self.on_toggle_recording: Optional[Callable[[], None]] = None
        
        # Thread safety
        self._lock = threading.Lock()
        
        logger.info(f"HotkeyManager initialized. pynput available: {PYNPUT_AVAILABLE}")
    
    def is_available(self) -> bool:
        """Check if hotkey functionality is available on this platform"""
        return PYNPUT_AVAILABLE
    
    def set_hotkey(self, hotkey: str) -> bool:
        """
        Set the hotkey combination.
        
        Args:
            hotkey: Hotkey string (e.g., "alt gr", "ctrl+shift+a", "F8")
            
        Returns:
            True if hotkey was set successfully, False otherwise
        """
        if not self.is_available():
            logger.error("pynput not available, cannot set hotkey")
            return False
        
        try:
            with self._lock:
                # Stop current listener if running
                self._stop_listener()
                
                # Validate hotkey format
                if not self._validate_hotkey(hotkey):
                    logger.error(f"Invalid hotkey format: {hotkey}")
                    return False
                
                self.hotkey = hotkey
                self._parse_hotkey_components(hotkey)
                logger.info(f"Hotkey set to: {hotkey}")
                logger.debug(f"Parsed modifiers: {self._hotkey_modifiers}, main key: {self._hotkey_main_key}")
                return True
                
        except Exception as e:
            logger.error(f"Error setting hotkey '{hotkey}': {e}")
            return False
    
    def _parse_hotkey_components(self, hotkey: str) -> None:
        """
        Parse hotkey string into modifiers and main key.
        
        Args:
            hotkey: Hotkey string to parse
        """
        try:
            # Reset components
            self._hotkey_modifiers = []
            self._hotkey_main_key = None
            
            if not hotkey:
                return
            
            # Split by '+' and normalize
            parts = [part.strip().lower() for part in hotkey.split('+')]
            
            # Known modifier keys
            modifier_keys = {
                'ctrl': 'ctrl',
                'control': 'ctrl',
                'alt': 'alt',
                'shift': 'shift',
                'cmd': 'cmd',
                'command': 'cmd',
                'meta': 'cmd',
                'win': 'win',
                'windows': 'win',
                'super': 'win'
            }
            
            # Special case for "alt gr" - it's a single key, not a modifier combination
            if hotkey.lower().strip() == 'alt gr':
                self._hotkey_main_key = 'alt gr'
                self._hotkey_modifiers = []
            else:
                # Parse components for other hotkeys
                for part in parts:
                    if part in modifier_keys:
                        modifier = modifier_keys[part]
                        if modifier not in self._hotkey_modifiers:
                            self._hotkey_modifiers.append(modifier)
                    else:
                        # This should be the main key
                        if self._hotkey_main_key is None:
                            self._hotkey_main_key = part
                        else:
                            logger.warning(f"Multiple main keys found in hotkey: {hotkey}")
            
            # Validate that we have a main key
            if self._hotkey_main_key is None:
                logger.warning(f"No main key found in hotkey: {hotkey}")
                # Use the last part as main key if no modifiers were found
                if parts:
                    self._hotkey_main_key = parts[-1]
            
            logger.debug(f"Parsed hotkey '{hotkey}': modifiers={self._hotkey_modifiers}, main_key={self._hotkey_main_key}")
            
        except Exception as e:
            logger.error(f"Error parsing hotkey components '{hotkey}': {e}")
            self._hotkey_modifiers = []
            self._hotkey_main_key = None
    
    def set_mode(self, mode: HotkeyMode) -> bool:
        """Set the hotkey operation mode"""
        with self._lock:
            self.mode = mode
            logger.info(f"Hotkey mode set to: {mode.value}")
            return True
    
    def register_hotkeys(self) -> bool:
        """
        Register the current hotkey for global listening.
        
        Returns:
            True if registration was successful, False otherwise
        """
        if not self.is_available():
            logger.error("pynput not available, cannot register hotkeys")
            return False
        
        if not self.hotkey:
            logger.error("No hotkey set, cannot register")
            return False
        
        try:
            with self._lock:
                # Stop current listener if running
                self._stop_listener()
                
                # Parse hotkey into pynput format
                hotkey_keys = self._parse_hotkey(self.hotkey)
                if not hotkey_keys:
                    logger.error(f"Failed to parse hotkey: {self.hotkey}")
                    return False
                
                # Create listener based on mode
                if self.mode == HotkeyMode.TOGGLE:
                    self.listener = keyboard.Listener(
                        on_press=self._on_key_press,
                        on_release=self._on_key_release
                    )
                else:  # HOLD mode
                    self.listener = keyboard.Listener(
                        on_press=self._on_key_press,
                        on_release=self._on_key_release
                    )
                
                # Start listener
                self.listener.start()
                self.is_listening = True
                
                logger.info(f"Hotkey registered: {self.hotkey} ({self.mode.value} mode)")
                return True
                
        except Exception as e:
            logger.error(f"Error registering hotkey: {e}")
            return False
    
    def unregister_hotkeys(self) -> None:
        """Unregister all hotkeys and stop listening"""
        with self._lock:
            self._stop_listener()
            logger.info("Hotkeys unregistered")
    
    def set_callbacks(self, 
                     on_start: Optional[Callable[[], None]] = None,
                     on_stop: Optional[Callable[[], None]] = None,
                     on_toggle: Optional[Callable[[], None]] = None) -> None:
        """Set callback functions for hotkey events"""
        self.on_start_recording = on_start
        self.on_stop_recording = on_stop
        self.on_toggle_recording = on_toggle
        logger.debug("Hotkey callbacks set")
    
    def _stop_listener(self) -> None:
        """Stop the current listener thread"""
        if self.listener and self.is_listening:
            try:
                self.listener.stop()
                self.listener.join(timeout=1.0)
            except Exception as e:
                logger.warning(f"Error stopping listener: {e}")
            finally:
                self.listener = None
                self.is_listening = False
    
    def _validate_hotkey(self, hotkey: str) -> bool:
        """Validate hotkey format"""
        if not hotkey or not isinstance(hotkey, str):
            return False
        
        # Basic validation - check for common key combinations
        valid_keys = [
            'alt', 'ctrl', 'shift', 'cmd', 'meta',
            'alt gr', 'altgr', 'space', 'enter', 'tab',
            'esc', 'escape', 'backspace', 'delete',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
            'up', 'down', 'left', 'right', 'page up', 'page down',
            'home', 'end', 'insert', 'caps lock'
        ]
        
        # Split by + and check each part
        parts = [part.strip().lower() for part in hotkey.split('+')]
        
        for part in parts:
            if part not in valid_keys and not (len(part) == 1 and part.isalnum()):
                logger.warning(f"Unknown key in hotkey: {part}")
                # Don't fail validation, just warn - pynput might handle it
        
        return True
    
    def _parse_hotkey(self, hotkey: str) -> Optional[list]:
        """
        Parse hotkey string into pynput key objects.
        
        Args:
            hotkey: Hotkey string (e.g., "alt gr", "ctrl+shift+a")
            
        Returns:
            List of pynput key objects, or None if parsing failed
        """
        try:
            parts = [part.strip() for part in hotkey.split('+')]
            keys = []
            
            for part in parts:
                # Map common key names to pynput keys
                key_mapping = {
                    'alt gr': keyboard.Key.alt_gr,
                    'altgr': keyboard.Key.alt_gr,
                    'ctrl': keyboard.Key.ctrl,
                    'alt': keyboard.Key.alt,
                    'shift': keyboard.Key.shift,
                    'cmd': keyboard.Key.cmd,
                    'meta': keyboard.Key.cmd,
                    'space': keyboard.Key.space,
                    'enter': keyboard.Key.enter,
                    'tab': keyboard.Key.tab,
                    'esc': keyboard.Key.esc,
                    'escape': keyboard.Key.esc,
                    'backspace': keyboard.Key.backspace,
                    'delete': keyboard.Key.delete,
                    'caps lock': keyboard.Key.caps_lock,
                    'F1': keyboard.Key.f1,
                    'F2': keyboard.Key.f2,
                    'F3': keyboard.Key.f3,
                    'F4': keyboard.Key.f4,
                    'F5': keyboard.Key.f5,
                    'F6': keyboard.Key.f6,
                    'F7': keyboard.Key.f7,
                    'F8': keyboard.Key.f8,
                    'F9': keyboard.Key.f9,
                    'F10': keyboard.Key.f10,
                    'F11': keyboard.Key.f11,
                    'F12': keyboard.Key.f12,
                    'up': keyboard.Key.up,
                    'down': keyboard.Key.down,
                    'left': keyboard.Key.left,
                    'right': keyboard.Key.right,
                    'page up': keyboard.Key.page_up,
                    'page down': keyboard.Key.page_down,
                    'home': keyboard.Key.home,
                    'end': keyboard.Key.end,
                    'insert': keyboard.Key.insert,
                }
                
                if part in key_mapping:
                    keys.append(key_mapping[part])
                elif len(part) == 1 and part.isalnum():
                    # Single character key
                    keys.append(keyboard.KeyCode.from_char(part))
                else:
                    logger.warning(f"Unknown key: {part}")
                    return None
            
            return keys
            
        except Exception as e:
            logger.error(f"Error parsing hotkey '{hotkey}': {e}")
            return None
    
    def _on_key_press(self, key) -> None:
        """Handle key press events with modifier state tracking"""
        try:
            # Update modifier states
            self._update_modifier_state(key, True)
            
            if self.mode == HotkeyMode.TOGGLE:
                # In toggle mode, check if this is our hotkey
                if self._is_hotkey_pressed(key):
                    if self.on_toggle_recording:
                        self.on_toggle_recording()
            else:  # HOLD mode
                # In hold mode, start recording when hotkey is pressed
                if self._is_hotkey_pressed(key) and not self.is_recording:
                    self.is_recording = True
                    if self.on_start_recording:
                        self.on_start_recording()
                        
        except Exception as e:
            logger.error(f"Error in key press handler: {e}")
    
    def _on_key_release(self, key) -> None:
        """Handle key release events with modifier state tracking"""
        try:
            # Update modifier states
            self._update_modifier_state(key, False)
            
            if self.mode == HotkeyMode.HOLD:
                # In hold mode, stop recording when hotkey is released
                if self._is_hotkey_pressed(key) and self.is_recording:
                    self.is_recording = False
                    if self.on_stop_recording:
                        self.on_stop_recording()
                        
        except Exception as e:
            logger.error(f"Error in key release handler: {e}")
    
    def _update_modifier_state(self, key, pressed: bool) -> None:
        """
        Update modifier key states based on key events.
        
        Args:
            key: The key that was pressed/released
            pressed: True if key was pressed, False if released
        """
        try:
            # Map pynput keys to our modifier names
            key_to_modifier = {
                keyboard.Key.ctrl_l: 'ctrl',
                keyboard.Key.ctrl_r: 'ctrl',
                keyboard.Key.alt_l: 'alt',
                keyboard.Key.alt_r: 'alt',
                keyboard.Key.shift_l: 'shift',
                keyboard.Key.shift_r: 'shift',
                keyboard.Key.cmd_l: 'cmd',
                keyboard.Key.cmd_r: 'cmd',
                keyboard.Key.alt_gr: 'alt gr',
                keyboard.Key.cmd: 'cmd',
                keyboard.Key.ctrl: 'ctrl',
                keyboard.Key.alt: 'alt',
                keyboard.Key.shift: 'shift',
            }
            
            # Check if this is a modifier key
            if key in key_to_modifier:
                modifier = key_to_modifier[key]
                self._modifier_states[modifier] = pressed
                logger.debug(f"Modifier '{modifier}' {'pressed' if pressed else 'released'}")
            
        except Exception as e:
            logger.error(f"Error updating modifier state: {e}")
    
    def _is_hotkey_pressed(self, key) -> bool:
        """
        Check if the pressed key matches our hotkey with proper modifier state tracking.
        
        Args:
            key: The key that was pressed
            
        Returns:
            True if the hotkey combination is matched, False otherwise
        """
        try:
            if not self.hotkey or not self._hotkey_main_key:
                return False
            
            # Check if the main key matches
            main_key_matches = self._key_matches_main_key(key)
            if not main_key_matches:
                return False
            
            # Check if all required modifiers are pressed
            for modifier in self._hotkey_modifiers:
                if not self._modifier_states.get(modifier, False):
                    logger.debug(f"Required modifier '{modifier}' not pressed")
                    return False
            
            # Check that no extra modifiers are pressed (optional - can be configured)
            # For now, we'll be lenient and allow extra modifiers
            
            logger.debug(f"Hotkey combination matched: {self.hotkey}")
            return True
            
        except Exception as e:
            logger.error(f"Error checking hotkey match: {e}")
            return False
    
    def _key_matches_main_key(self, key) -> bool:
        """
        Check if the pressed key matches our main key.
        
        Args:
            key: The key that was pressed
            
        Returns:
            True if the key matches our main key, False otherwise
        """
        try:
            if not self._hotkey_main_key:
                return False
            
            # Convert key to string for comparison
            key_str = self._key_to_string(key).lower()
            main_key_lower = self._hotkey_main_key.lower()
            
            # Direct match
            if key_str == main_key_lower:
                return True
            
            # Special cases for common keys
            special_mappings = {
                'space': ' ',
                'enter': '\n',
                'return': '\n',
                'tab': '\t',
                'backspace': '\b',
                'delete': '\x7f',
                'escape': '\x1b',
                'esc': '\x1b',
                'alt gr': 'alt_gr',  # Alt Gr key string uses underscore
                'altgr': 'alt_gr'    # Alternative Alt Gr spelling
            }
            
            # Check special mappings
            if main_key_lower in special_mappings:
                return key_str == special_mappings[main_key_lower]
            
            # Check reverse mappings
            for special_key, char in special_mappings.items():
                if main_key_lower == char and key_str == special_key:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error matching main key: {e}")
            return False
    
    def _key_to_string(self, key) -> str:
        """
        Convert a pynput key to a string representation.
        
        Args:
            key: The pynput key object
            
        Returns:
            String representation of the key
        """
        try:
            if hasattr(key, 'char') and key.char is not None:
                return key.char
            elif hasattr(key, 'name'):
                return key.name
            else:
                return str(key)
        except Exception as e:
            logger.error(f"Error converting key to string: {e}")
            return str(key)
    
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            self.unregister_hotkeys()
            logger.info("HotkeyManager cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status information"""
        return {
            "available": self.is_available(),
            "hotkey": self.hotkey,
            "mode": self.mode.value if self.mode else None,
            "listening": self.is_listening,
            "recording": self.is_recording,
            "parsed_modifiers": self._hotkey_modifiers,
            "parsed_main_key": self._hotkey_main_key,
            "modifier_states": self._modifier_states.copy()
        }
