import sys
import time
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QComboBox, QCheckBox, 
                             QLineEdit, QLabel, QGroupBox, QMessageBox, QTabWidget,
                             QScrollArea, QTextEdit, QFrame, QSlider, QFormLayout, QDesktopWidget,
                             QSizePolicy, QDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QMetaObject, QPoint, QRectF, QUrl
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QCursor, QPainter, QPen, QLinearGradient
from PyQt5.QtMultimedia import QSoundEffect
from speech_controller import SpeechController
from waveform_widget import WaveformWidget  # Import the dedicated widget
from ui.main_window import MainWindow
from ui.visual_indicator import VisualIndicatorWidget
from ui.styles.main_styles import MainStyles
from ui.record_tab import RecordTab
from ui.transcripts_tab import TranscriptsTab
from ui.widget_lifecycle import WidgetLifecycleManager, LifecycleAwareWidget
from core.cleanup_manager import CleanupPhase, register_cleanup_task
from core.settings_manager import SettingsManager
from ui.preferences_dialog import PreferencesDialog
from core.logging_config import get_logger

logger = get_logger(__name__)


class SpeechApp(MainWindow):
    # Define signals for thread-safe communication
    transcript_updated = pyqtSignal()
    status_updated = pyqtSignal(str)
    
    def __init__(self, controller: SpeechController, settings_manager: SettingsManager):
        super().__init__(settings_manager)
        self.controller = controller
        
        # Track initialization state to prevent sounds during startup
        self._is_initializing = True
        
        # Initialize lifecycle manager
        self.lifecycle_manager = WidgetLifecycleManager(self)
        
        # Initialize waveform widget
        self.waveform_widget = WaveformWidget()
        
        # Initialize visual indicator widget
        self.visual_indicator = VisualIndicatorWidget("Bottom Center")
        
        # Register widgets with lifecycle manager
        self.lifecycle_manager.register_widget(
            self.visual_indicator,
            "visual_indicator",
            self._cleanup_visual_indicator
        )
        
        # Register UI cleanup tasks
        self._register_ui_cleanup_tasks()
        
        # Connect signals to slots
        self.status_updated.connect(self._update_status_safe)
        
        # Connect MainWindow signals
        self.settings_changed.connect(self.on_settings_changed)
        
        # Set up callbacks
        self.controller.set_status_callback(self.update_status)
        self.controller.set_transcript_callback(self.on_new_transcript)
        self.controller.set_audio_level_callback(self.waveform_widget.update_level)
        
        # Initialize UI components
        self.init_app_ui()
        
        # Apply settings to the application
        self.settings_manager.apply_all(self)
        
        # Update UI based on feature availability
        self.update_feature_availability()
        
        # Restore window geometry and state
        # Note: Not restoring saved geometry - using proportional sizing for multi-monitor compatibility
        # Window will always open at 80% of current screen size, centered
        # self.settings_manager.restore_window(self)
        
        # Force layout recomputation after app starts to fix initial tab height
        # Activate visual indicator
        self.lifecycle_manager.activate_widget("visual_indicator")
        
        # DISABLED: This was overriding our responsive window sizing
        # QTimer.singleShot(100, self.adjustSize)
        
        # Start background model loading for faster first recording
        QTimer.singleShot(500, self.start_background_model_loading)
        
        # Mark initialization as complete after a short delay
        QTimer.singleShot(1000, self._mark_initialization_complete)
    
    def _register_ui_cleanup_tasks(self):
        """Register UI cleanup tasks"""
        # Widget lifecycle cleanup
        register_cleanup_task(
            "widget_lifecycle_cleanup",
            CleanupPhase.UI_WIDGETS,
            self._cleanup_widget_lifecycle,
            self._verify_widget_cleanup,
            timeout=5.0,
            critical=True
        )
        
        # System tray cleanup
        register_cleanup_task(
            "system_tray_cleanup",
            CleanupPhase.UI_WIDGETS,
            self._cleanup_system_tray,
            self._verify_system_tray_cleanup,
            timeout=3.0,
            critical=False
        )
        
        logger.info("UI cleanup tasks registered successfully")
    
    def _cleanup_widget_lifecycle(self) -> bool:
        """Clean up widget lifecycle manager"""
        try:
            if hasattr(self, 'lifecycle_manager') and self.lifecycle_manager:
                self.lifecycle_manager.cleanup_all_widgets()
                logger.debug("Widget lifecycle manager cleaned up")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up widget lifecycle: {e}")
            return False
    
    def _verify_widget_cleanup(self) -> bool:
        """Verify widget cleanup"""
        try:
            # Check if visual indicator is properly cleaned up
            if hasattr(self, 'visual_indicator'):
                return self.visual_indicator is None or not self.visual_indicator.isVisible()
            return True
        except Exception as e:
            logger.error(f"Error verifying widget cleanup: {e}")
            return False
    
    def _cleanup_system_tray(self) -> bool:
        """Clean up system tray"""
        try:
            if hasattr(self, 'system_tray') and self.system_tray:
                self.system_tray.hide()
                self.system_tray = None
                logger.debug("System tray cleaned up")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up system tray: {e}")
            return False
    
    def _verify_system_tray_cleanup(self) -> bool:
        """Verify system tray cleanup"""
        try:
            return not hasattr(self, 'system_tray') or self.system_tray is None
        except Exception as e:
            logger.error(f"Error verifying system tray cleanup: {e}")
            return False
    
    def _cleanup_visual_indicator(self):
        """Cleanup method for visual indicator widget"""
        try:
            if hasattr(self, 'visual_indicator') and self.visual_indicator is not None:
                self.visual_indicator.hide_recording()
                self.visual_indicator.deleteLater()
                logger.debug("Visual indicator cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up visual indicator: {e}")
    
    def _mark_initialization_complete(self):
        """Mark initialization as complete to enable sounds"""
        self._is_initializing = False
    
    def play_start_sound(self):
        """Play start recording sound"""
        try:
            # Check if sound effects are enabled
            if not self.settings_manager.get("audio/effects_enabled", True):
                return
            
            # Get sound file path from settings
            sound_file = self.settings_manager.get("audio/start_tone", "assets/sound_start_v9.wav")
            
            # Play sound using QSoundEffect
            from PyQt5.QtMultimedia import QSoundEffect
            from PyQt5.QtCore import QUrl
            
            sound_effect = QSoundEffect()
            sound_effect.setSource(QUrl.fromLocalFile(sound_file))
            sound_effect.play()
            
        except Exception as e:
            logger.debug(f"Could not play start sound: {e}")
    
    def play_stop_sound(self):
        """Play stop recording sound"""
        try:
            # Check if sound effects are enabled
            if not self.settings_manager.get("audio/effects_enabled", True):
                return
            
            # Get sound file path from settings
            sound_file = self.settings_manager.get("audio/stop_tone", "assets/sound_end_v9.wav")
            
            # Play sound using QSoundEffect
            from PyQt5.QtMultimedia import QSoundEffect
            from PyQt5.QtCore import QUrl
            
            sound_effect = QSoundEffect()
            sound_effect.setSource(QUrl.fromLocalFile(sound_file))
            sound_effect.play()
            
        except Exception as e:
            logger.debug(f"Could not play stop sound: {e}")
        
    def init_app_ui(self):
        """Initialize application-specific UI components"""
        # Create tabs
        # Create Record tab first (leftmost position)
        self.record_tab = RecordTab(self)
        self.add_tab(self.record_tab, "Record")
        
        # Create Transcripts tab second (rightmost position)
        self.transcripts_tab = TranscriptsTab(self)
        self.add_tab(self.transcripts_tab, "Transcripts")
        
        # Connect tab change signal for dynamic resizing
        self.connect_tab_changed(self.on_tab_changed)
        
        # Update hotkey instruction now that tabs are created
        self.update_hotkey_instruction()
    
    def start_background_model_loading(self):
        """Start loading the Whisper model in the background"""
        # Check if controller is lazy-loaded and needs initialization first
        if hasattr(self.controller, '_ensure_initialized'):
            # This is a LazySpeechController, ensure it's initialized
            if not self.controller._ensure_initialized():
                logger.warning("Failed to initialize controller for model loading")
                return
        
        if self.controller.preload_model():
            logger.info("Started background model loading...")
            # Update status to show loading
            self.update_status("Idle")  # This will show "Model: Loading..."
        else:
            logger.info("Model already loaded or loading")
        
    def start_recording(self):
        """Start recording via GUI button"""
        # Ensure controller is initialized before recording
        if hasattr(self.controller, '_ensure_initialized'):
            if not self.controller._ensure_initialized():
                QMessageBox.warning(
                    self,
                    "Recording Error",
                    "Audio system is not ready. Please check your microphone and try again."
                )
                return
        
        self.controller.start_recording()
        self.record_tab.start_button.setEnabled(False)
        self.record_tab.stop_button.setEnabled(True)
        
        # Play start sound (only after initialization)
        if not self._is_initializing:
            self.play_start_sound()
        
    def stop_recording(self):
        """Stop recording via GUI button"""
        self.controller.stop_recording()
        self.record_tab.start_button.setEnabled(True)
        self.record_tab.stop_button.setEnabled(False)
        
        # Play stop sound (only after initialization)
        if not self._is_initializing:
            self.play_stop_sound()
        
        # Refresh transcript log after recording
        # Find the transcripts tab and refresh it
        self.transcripts_tab.refresh_transcript_log()
        
    def on_new_transcript(self):
        """Handle new transcript added - emit signal for thread-safe update"""
        self.transcript_updated.emit()
        
    def update_status(self, status: str):
        """Update the status display - emit signal for thread-safe update"""
        self.status_updated.emit(status)
    
    def _update_status_safe(self, status: str):
        """Thread-safe status update"""
        # Get current language from controller
        if hasattr(self.controller, 'language') and self.controller.language:
            if self.controller.language == "auto":
                current_language = "Auto"
            else:
                # Convert language code to display name
                lang_map = {
                    "en": "English", "de": "German", "es": "Spanish", 
                    "sv": "Swedish", "fi": "Finnish", "pt": "Portuguese", "fr": "French"
                }
                current_language = lang_map.get(self.controller.language, self.controller.language)
        else:
            current_language = "Auto"
        
        # Get model status for footer
        model_status = self.controller.get_model_status()
        if model_status == "loaded":
            model_info = f"Model: Ready | Language: {current_language}"
        elif model_status == "loading":
            model_info = "Model: Loading..."
        elif model_status.startswith("error"):
            model_info = "Model: Error"
        else:
            model_info = "Model: Not loaded"
        
        # Combine status and model info for footer
        footer_text = f"{status} | {model_info}"
        
        # Update footer with combined information
        self.update_footer(footer_text)
        
        # Clear main status area (no text displayed)
        self.record_tab.update_status("")
        
        # Update waveform widget state
        if status == "Recording...":
            self.waveform_widget.set_state("recording")
        elif status == "Processing...":
            self.waveform_widget.set_state("transcribing")
        else:  # Idle or any other status
            self.waveform_widget.set_state("idle")
        
        # Update button states based on status
        if status == "Recording...":
            self.record_tab.start_button.setEnabled(False)
            self.record_tab.stop_button.setEnabled(True)
            # Show visual indicator if enabled
            if (self.controller.visual_indicator_enabled and 
                self.lifecycle_manager.is_widget_active("visual_indicator")):
                visual_indicator = self.lifecycle_manager.get_widget("visual_indicator")
                if visual_indicator is not None:
                    visual_indicator.show_recording()
            # Play start sound for hotkey-triggered recording (only after initialization)
            if not self._is_initializing:
                self.play_start_sound()
        elif status == "Idle":
            self.record_tab.start_button.setEnabled(True)
            self.record_tab.stop_button.setEnabled(False)
            # Hide visual indicator
            if hasattr(self, 'visual_indicator') and self.visual_indicator is not None:
                try:
                    self.visual_indicator.hide_recording()
                except RuntimeError:
                    # Widget has been deleted, ignore the error
                    self.visual_indicator = None
            # Play stop sound for hotkey-triggered recording (only after initialization)
            if not self._is_initializing:
                self.play_stop_sound()
        elif status == "Processing...":
            self.record_tab.start_button.setEnabled(False)
            self.record_tab.stop_button.setEnabled(False)
            # Hide visual indicator during processing
            if self.lifecycle_manager.is_widget_active("visual_indicator"):
                visual_indicator = self.lifecycle_manager.get_widget("visual_indicator")
                if visual_indicator is not None:
                    visual_indicator.hide_recording()
            
    def update_hotkey_instruction(self):
        """Update the hotkey instruction label in the Record tab"""
        hotkey = self.controller.hotkey
        mode_text = "toggle" if self.controller.toggle_mode else "hold"
        
        if self.controller.toggle_mode:
            instruction = f"Press '{hotkey}' once to start recording, press again to stop"
        else:
            instruction = f"Hold '{hotkey}' to record, release to transcribe"
        
        self.record_tab.hotkey_instruction_label.setText(instruction)
    
    def show_preferences_dialog(self):
        """Show the preferences dialog (called from system tray)."""
        self.open_preferences()
            
    def on_tab_changed(self, index: int):
        """Handle tab change - maintain responsive window sizing"""
        # DISABLED: This was overriding our responsive window sizing
        # Let the responsive system maintain the proper window size
        # self.adjustSize()
        
    
    def on_settings_changed(self, settings: dict):
        """Handle settings changes from MainWindow"""
        try:
            # Update UI elements that might have changed
            if "hotkey/combo" in settings:
                self.update_hotkey_instruction()
            
            # Handle Whisper settings changes
            if "whisper/model_name" in settings:
                new_model = settings["whisper/model_name"]
                if hasattr(self.controller, 'set_model'):
                    self.controller.set_model(new_model)
                    self.update_status(f"Model changed to: {new_model}")
            
            if "whisper/temperature" in settings:
                new_temperature = settings["whisper/temperature"]
                if hasattr(self.controller, 'temperature'):
                    self.controller.temperature = new_temperature
                    self.update_status(f"Temperature updated to: {new_temperature}")
            
            if "whisper/speed_mode" in settings:
                new_speed_mode = settings["whisper/speed_mode"]
                if hasattr(self.controller, 'speed_mode'):
                    self.controller.speed_mode = new_speed_mode
                    self.update_status(f"Speed mode updated to: {new_speed_mode}")
            
            # Handle behavior settings changes
            if "behavior/auto_paste" in settings:
                new_auto_paste = settings["behavior/auto_paste"]
                if hasattr(self.controller, 'set_auto_paste'):
                    self.controller.set_auto_paste(new_auto_paste)
                    self.update_status(f"Auto-paste updated to: {new_auto_paste}")
            
            if "behavior/toggle_mode" in settings:
                new_toggle_mode = settings["behavior/toggle_mode"]
                if hasattr(self.controller, 'set_toggle_mode'):
                    self.controller.set_toggle_mode(new_toggle_mode)
                    self.update_hotkey_instruction()
                    self.update_status(f"Toggle mode updated to: {new_toggle_mode}")
            
            if "behavior/hotkey" in settings:
                new_hotkey = settings["behavior/hotkey"]
                if hasattr(self.controller, 'set_hotkey'):
                    self.controller.set_hotkey(new_hotkey)
                    self.update_hotkey_instruction()
                    self.update_status(f"Hotkey updated to: {new_hotkey}")
            
            if "behavior/minimize_to_tray" in settings:
                new_minimize_to_tray = settings["behavior/minimize_to_tray"]
                self.set_minimize_to_tray(new_minimize_to_tray)
                self.update_status(f"Minimize to tray updated to: {new_minimize_to_tray}")
            
            if "behavior/visual_indicator" in settings or "behavior/indicator_position" in settings:
                new_visual_indicator = settings.get("behavior/visual_indicator", True)
                new_indicator_position = settings.get("behavior/indicator_position", "Bottom Center")
                if hasattr(self.controller, 'set_visual_indicator'):
                    self.controller.set_visual_indicator(new_visual_indicator, new_indicator_position)
                    if self.lifecycle_manager.is_widget_active("visual_indicator"):
                        visual_indicator = self.lifecycle_manager.get_widget("visual_indicator")
                        if visual_indicator is not None:
                            visual_indicator.update_position(new_indicator_position)
                    self.update_status(f"Visual indicator updated: {new_visual_indicator} at {new_indicator_position}")
            
        except Exception as e:
            logger.error(f"Error applying settings changes: {e}")
    
    def closeEvent(self, event):
        """Handle application close - override MainWindow's closeEvent"""
        try:
            print(f"SpeechApp closeEvent called - minimize_to_tray_enabled: {self.minimize_to_tray_enabled}, system_tray: {self.system_tray is not None}")
            
            # Clean up all managed widgets
            self.lifecycle_manager.cleanup_all_widgets()
            
            # Call parent's closeEvent first to handle minimize to tray logic
            super().closeEvent(event)
            
            # Only cleanup controller if we're actually quitting (not minimizing to tray)
            if event.isAccepted() and not (self.minimize_to_tray_enabled and self.system_tray):
                print("SpeechApp: Actually quitting, cleaning up controller...")
                self.controller.cleanup()
                
                # Single instance lock cleanup is handled by CleanupManager
                # No need to manually release lock here
            else:
                print("SpeechApp: Minimizing to tray or event ignored, skipping controller cleanup...")
                # Note: Single instance lock should NOT be released when minimizing to tray
            
        except Exception as e:
            logger.error(f"Error during application close: {e}")
            super().closeEvent(event)
    
    def update_feature_availability(self):
        """Update UI elements based on feature availability"""
        try:
            # Update record tab feature availability
            if hasattr(self, 'record_tab'):
                self.record_tab.update_feature_availability()
            
            # Update hotkey instruction
            self.update_hotkey_instruction()
            
        except Exception as e:
            logger.error(f"Error updating feature availability: {e}")
