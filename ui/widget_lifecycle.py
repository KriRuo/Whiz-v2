#!/usr/bin/env python3
"""
ui/widget_lifecycle.py
-----------------------
Widget lifecycle management for Whiz Voice-to-Text Application.

This module provides proper widget lifecycle management to replace
the RuntimeError exception handling pattern with explicit state tracking.

Features:
    - Widget state tracking (CREATED, ACTIVE, DESTROYED)
    - Proper cleanup methods
    - Weak reference management
    - Lifecycle event callbacks

Author: Whiz Development Team
Last Updated: December 2024
"""

import weakref
from enum import Enum
from typing import Optional, Callable, Dict, Any, List
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget

from core.logging_config import get_logger
logger = get_logger(__name__)

class WidgetState(Enum):
    """Widget lifecycle states"""
    CREATED = "created"
    ACTIVE = "active"
    DESTROYED = "destroyed"

class WidgetLifecycleManager(QObject):
    """
    Manages widget lifecycle states and cleanup.
    
    Provides proper state tracking and cleanup methods to replace
    RuntimeError exception handling patterns.
    """
    
    # Signals for lifecycle events
    widget_created = pyqtSignal(object, str)  # widget, name
    widget_activated = pyqtSignal(object, str)  # widget, name
    widget_destroyed = pyqtSignal(object, str)  # widget, name
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._widgets: Dict[str, Dict[str, Any]] = {}
        self._cleanup_callbacks: Dict[str, List[Callable]] = {}
        
        logger.debug("WidgetLifecycleManager initialized")
    
    def register_widget(self, widget: QWidget, name: str, 
                       cleanup_callback: Optional[Callable] = None) -> bool:
        """
        Register a widget for lifecycle management.
        
        Args:
            widget: The widget to manage
            name: Unique name for the widget
            cleanup_callback: Optional cleanup function to call
            
        Returns:
            True if registered successfully, False otherwise
        """
        try:
            if name in self._widgets:
                logger.warning(f"Widget '{name}' already registered")
                return False
            
            # Create weak reference to avoid circular references
            widget_ref = weakref.ref(widget, self._make_cleanup_callback(name))
            
            self._widgets[name] = {
                'ref': widget_ref,
                'state': WidgetState.CREATED,
                'created_time': self._get_timestamp(),
                'cleanup_callback': cleanup_callback
            }
            
            # Store cleanup callback
            if cleanup_callback:
                self._cleanup_callbacks[name] = [cleanup_callback]
            
            logger.debug(f"Widget '{name}' registered in CREATED state")
            self.widget_created.emit(widget, name)
            
            return True
            
        except Exception as e:
            logger.error(f"Error registering widget '{name}': {e}")
            return False
    
    def activate_widget(self, name: str) -> bool:
        """
        Mark a widget as active.
        
        Args:
            name: Widget name
            
        Returns:
            True if activated successfully, False otherwise
        """
        try:
            if name not in self._widgets:
                logger.warning(f"Widget '{name}' not registered")
                return False
            
            widget_info = self._widgets[name]
            widget = widget_info['ref']()
            
            if widget is None:
                logger.warning(f"Widget '{name}' has been garbage collected")
                self._remove_widget(name)
                return False
            
            widget_info['state'] = WidgetState.ACTIVE
            widget_info['activated_time'] = self._get_timestamp()
            
            logger.debug(f"Widget '{name}' activated")
            self.widget_activated.emit(widget, name)
            
            return True
            
        except Exception as e:
            logger.error(f"Error activating widget '{name}': {e}")
            return False
    
    def destroy_widget(self, name: str) -> bool:
        """
        Properly destroy a widget and clean up resources.
        
        Args:
            name: Widget name
            
        Returns:
            True if destroyed successfully, False otherwise
        """
        try:
            if name not in self._widgets:
                logger.warning(f"Widget '{name}' not registered")
                return False
            
            widget_info = self._widgets[name]
            widget = widget_info['ref']()
            
            # Call cleanup callbacks
            if name in self._cleanup_callbacks:
                for callback in self._cleanup_callbacks[name]:
                    try:
                        callback()
                    except Exception as e:
                        logger.error(f"Error in cleanup callback for '{name}': {e}")
            
            # Emit destroyed signal
            if widget is not None:
                self.widget_destroyed.emit(widget, name)
            
            # Update state
            widget_info['state'] = WidgetState.DESTROYED
            widget_info['destroyed_time'] = self._get_timestamp()
            
            logger.debug(f"Widget '{name}' destroyed")
            
            # Remove from active management
            self._remove_widget(name)
            
            return True
            
        except Exception as e:
            logger.error(f"Error destroying widget '{name}': {e}")
            return False
    
    def is_widget_active(self, name: str) -> bool:
        """
        Check if a widget is in active state.
        
        Args:
            name: Widget name
            
        Returns:
            True if widget is active, False otherwise
        """
        if name not in self._widgets:
            return False
        
        widget_info = self._widgets[name]
        widget = widget_info['ref']()
        
        if widget is None:
            # Widget was garbage collected
            self._remove_widget(name)
            return False
        
        return widget_info['state'] == WidgetState.ACTIVE
    
    def get_widget_state(self, name: str) -> Optional[WidgetState]:
        """
        Get the current state of a widget.
        
        Args:
            name: Widget name
            
        Returns:
            Widget state or None if not found
        """
        if name not in self._widgets:
            return None
        
        widget_info = self._widgets[name]
        widget = widget_info['ref']()
        
        if widget is None:
            # Widget was garbage collected
            self._remove_widget(name)
            return WidgetState.DESTROYED
        
        return widget_info['state']
    
    def get_widget(self, name: str) -> Optional[QWidget]:
        """
        Get a widget by name.
        
        Args:
            name: Widget name
            
        Returns:
            Widget instance or None if not found/destroyed
        """
        if name not in self._widgets:
            return None
        
        widget_info = self._widgets[name]
        widget = widget_info['ref']()
        
        if widget is None:
            # Widget was garbage collected
            self._remove_widget(name)
            return None
        
        return widget
    
    def add_cleanup_callback(self, name: str, callback: Callable) -> bool:
        """
        Add a cleanup callback for a widget.
        
        Args:
            name: Widget name
            callback: Cleanup function
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            if name not in self._widgets:
                logger.warning(f"Widget '{name}' not registered")
                return False
            
            if name not in self._cleanup_callbacks:
                self._cleanup_callbacks[name] = []
            
            self._cleanup_callbacks[name].append(callback)
            logger.debug(f"Cleanup callback added for widget '{name}'")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding cleanup callback for '{name}': {e}")
            return False
    
    def cleanup_all_widgets(self) -> None:
        """Clean up all managed widgets."""
        logger.info("Cleaning up all managed widgets")
        
        widget_names = list(self._widgets.keys())
        for name in widget_names:
            self.destroy_widget(name)
    
    def get_status(self) -> Dict[str, Any]:
        """Get lifecycle manager status."""
        active_count = 0
        destroyed_count = 0
        
        for widget_info in self._widgets.values():
            if widget_info['state'] == WidgetState.ACTIVE:
                active_count += 1
            elif widget_info['state'] == WidgetState.DESTROYED:
                destroyed_count += 1
        
        return {
            "total_widgets": len(self._widgets),
            "active_widgets": active_count,
            "destroyed_widgets": destroyed_count,
            "widgets": {
                name: {
                    "state": info['state'].value,
                    "created_time": info.get('created_time'),
                    "activated_time": info.get('activated_time'),
                    "destroyed_time": info.get('destroyed_time')
                }
                for name, info in self._widgets.items()
            }
        }
    
    def _remove_widget(self, name: str) -> None:
        """Remove widget from management."""
        if name in self._widgets:
            del self._widgets[name]
        
        if name in self._cleanup_callbacks:
            del self._cleanup_callbacks[name]
    
    def _make_cleanup_callback(self, name: str) -> Callable:
        """Create a cleanup callback for when widget is garbage collected."""
        def cleanup_callback(widget_ref):
            logger.debug(f"Widget '{name}' was garbage collected")
            if name in self._widgets:
                self._widgets[name]['state'] = WidgetState.DESTROYED
                self._remove_widget(name)
        
        return cleanup_callback
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().isoformat()

class LifecycleAwareWidget(QWidget):
    """
    Base class for widgets that need lifecycle management.
    
    Provides automatic registration with lifecycle manager and
    proper cleanup methods.
    """
    
    def __init__(self, lifecycle_manager: Optional[WidgetLifecycleManager] = None, 
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.lifecycle_manager = lifecycle_manager
        self.lifecycle_name = self.__class__.__name__
        
        if self.lifecycle_manager:
            self.lifecycle_manager.register_widget(self, self.lifecycle_name, 
                                                  self._cleanup_resources)
    
    def activate(self) -> bool:
        """Activate this widget."""
        if self.lifecycle_manager:
            return self.lifecycle_manager.activate_widget(self.lifecycle_name)
        return True
    
    def destroy_widget(self) -> bool:
        """Destroy this widget properly."""
        if self.lifecycle_manager:
            return self.lifecycle_manager.destroy_widget(self.lifecycle_name)
        else:
            self._cleanup_resources()
            self.deleteLater()
            return True
    
    def is_active(self) -> bool:
        """Check if this widget is active."""
        if self.lifecycle_manager:
            return self.lifecycle_manager.is_widget_active(self.lifecycle_name)
        return True
    
    def _cleanup_resources(self) -> None:
        """Override this method to implement widget-specific cleanup."""
        logger.debug(f"Cleaning up resources for {self.lifecycle_name}")
        pass
    
    def closeEvent(self, event):
        """Override closeEvent to ensure proper cleanup."""
        self.destroy_widget()
        super().closeEvent(event)
