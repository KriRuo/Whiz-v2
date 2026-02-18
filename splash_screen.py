#!/usr/bin/env python3
"""
splash_screen.py
----------------
Modern splash screen for Whiz Voice-to-Text Application.

This module implements a splash screen that displays while the main application
loads in a background thread. It provides visual feedback during initialization
and integrates with the logging framework for real-time progress updates.

Features:
    - Blue gradient design with "Whiz" branding
    - Real-time log display from initialization process
    - Background thread initialization (QThread)
    - Smooth fade-out animation
    - Error handling with user-friendly dialogs
    - Cross-platform compatibility

Dependencies:
    - PyQt5: GUI framework for splash screen
    - core.logging_config: Centralized logging system
    - core.settings_manager: Settings management
    - speech_controller: Main speech recognition controller
    - speech_ui: Main application window

Example:
    Basic usage:
        splash = SplashScreen(app)
        splash.show()
        splash.start_initialization()

Author: Whiz Development Team
Last Updated: October 10, 2025
"""

import sys
import traceback
import time
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget, QVBoxLayout, QLabel, QTextEdit, QDesktopWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont

# Import core modules
from core.logging_config import get_logger
from core.settings_manager import SettingsManager
from core.performance_monitor import get_performance_monitor
from core.config import WHISPER_CONFIG
# SpeechController and SpeechApp imported lazily to avoid heavy dependencies at startup

logger = get_logger(__name__)


class InitializationWorker(QThread):
    """
    Background worker thread for application initialization.
    
    This thread handles the heavy initialization tasks while the splash screen
    displays progress updates. It initializes all core components including
    settings, platform detection, audio/hotkey managers, and the speech controller.
    
    Signals:
        progress_updated(int, str): Emitted when progress updates (progress%, message)
        initialization_complete(object, object): Emitted when done (controller, settings_manager)
        initialization_failed(str): Emitted on error (error_message)
    """
    
    progress_updated = pyqtSignal(int, str)  # progress, message
    initialization_complete = pyqtSignal(object, object)  # controller, settings_manager
    initialization_failed = pyqtSignal(str)  # error message
    
    def __init__(self):
        """
        Initialize the initialization worker thread.
        
        Sets up the initialization steps with realistic timing estimates.
        """
        super().__init__()
        self.steps = [
            ("Initializing logging system...", 5),
            ("Loading settings manager...", 15),
            ("Detecting platform features...", 25),
            ("Initializing audio manager...", 35),
            ("Initializing hotkey manager...", 45),
            ("Preparing speech controller...", 60),
            ("Loading Whisper model...", 80),
            ("Finalizing initialization...", 95),
            ("Ready!", 100)
        ]
        
    def run(self):
        """
        Execute initialization steps with progress reporting.
        
        Runs through all initialization steps, emitting progress signals
        and handling errors gracefully. Uses the logging framework for
        detailed progress tracking.
        """
        try:
            # Step 1: Initialize logging system and performance monitoring
            self.progress_updated.emit(5, "Initializing logging system...")
            logger.info("Splash screen initialization started")
            
            # Start performance monitoring
            performance_monitor = get_performance_monitor()
            performance_monitor.start_monitoring(interval=2.0)  # Monitor every 2 seconds
            
            # Step 2: Initialize settings manager
            self.progress_updated.emit(15, "Loading settings manager...")
            settings_manager = SettingsManager()
            settings = settings_manager.load_all()
            logger.info(f"Settings manager loaded {len(settings)} settings")
            
            # Step 3: Platform detection
            self.progress_updated.emit(25, "Detecting platform features...")
            from core.platform_features import PlatformFeatures
            platform_features = PlatformFeatures()
            features = platform_features.detect_all_features()
            logger.info(f"Platform features detected: {features}")
            
            # Step 4: Initialize audio manager
            self.progress_updated.emit(35, "Initializing audio manager...")
            from core.audio_manager import AudioManager
            audio_manager = AudioManager(sample_rate=16000, channels=1, chunk_size=1024)  # Use optimized chunk size
            logger.info(f"Audio manager initialized. Available: {audio_manager.is_available()}")
            
            # Step 5: Initialize hotkey manager
            self.progress_updated.emit(45, "Initializing hotkey manager...")
            from core.hotkey_manager import HotkeyManager
            hotkey_manager = HotkeyManager()
            logger.info(f"Hotkey manager initialized. Available: {hotkey_manager.is_available()}")
            
            # Step 6: Prepare speech controller (lazy model loading)
            self.progress_updated.emit(50, "Preparing speech controller...")
            # Import SpeechController here to avoid heavy dependencies at module level
            from speech_controller import SpeechController
            controller = SpeechController(
                hotkey=settings.get("behavior/hotkey", "alt gr"),  # Use saved hotkey or default
                model_size=settings.get("whisper/model_name", "tiny"),
                auto_paste=settings.get("behavior/auto_paste", True),
                language=settings.get("whisper/language", None),
                temperature=settings.get("whisper/temperature", 0.0),
                engine=settings.get("whisper/engine", WHISPER_CONFIG.DEFAULT_ENGINE)
            )
            logger.info("Speech controller initialized successfully")
            
            # Step 7: Show window early! (was at 100%)
            self.progress_updated.emit(40, "Opening window...")
            time.sleep(0.05)  # Brief pause for visual feedback
            
            # Emit success NOW instead of waiting
            self.initialization_complete.emit(controller, settings_manager)
            
            # Continue with remaining initialization in background
            self.progress_updated.emit(60, "Finalizing setup...")
            
            # Step 7: Model will load on first use (lazy loading)
            self.progress_updated.emit(80, "Ready for transcription...")
            logger.info("Application ready - model will load on first transcription")
            
            # Step 8: Finalize initialization
            self.progress_updated.emit(95, "Finalizing initialization...")
            logger.info("Initialization completed successfully")
            
            # Step 9: Ready
            self.progress_updated.emit(100, "Ready!")
            
            # Record startup time for performance monitoring
            performance_monitor.record_startup_time()
            
        except Exception as e:
            error_msg = f"Initialization failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.initialization_failed.emit(error_msg)


class SplashScreen(QWidget):
    """
    Modern splash screen with background initialization.
    
    This splash screen displays a branded loading screen while the main
    application initializes in a background thread. It provides real-time
    progress updates and handles errors gracefully.
    
    Features:
        - Blue gradient design with "Whiz" branding
        - Real-time log display from initialization
        - Smooth fade-out animation
        - Error handling with user-friendly dialogs
        - Cross-platform window centering
    """
    
    def __init__(self, app):
        """
        Initialize the splash screen.
        
        Args:
            app (QApplication): The main Qt application instance
        """
        super().__init__()
        self.app = app
        self.controller = None
        self.settings_manager = None
        self.main_window = None
        
        # Initialize UI
        self.init_ui()
        self.setup_worker()
        
    def init_ui(self):
        """
        Initialize the splash screen user interface.
        
        Creates a frameless window with blue gradient background,
        "Whiz" title, status label, and log display area.
        """
        # Window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 400)
        
        # Center the window
        self.center_window()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(0)
        
        # App title
        self.title_label = QLabel("Whiz")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self.title_label.setStyleSheet("""
            QLabel {
                color: #00C6FF;
                font-weight: bold;
                text-shadow: 0 0 10px rgba(0, 198, 255, 0.5);
            }
        """)
        
        header_layout.addWidget(self.title_label)
        main_layout.addLayout(header_layout)
        
        # Status container
        status_container = QWidget()
        status_container.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.4);
                border: 2px solid rgba(0, 198, 255, 0.6);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        status_layout = QVBoxLayout(status_container)
        status_layout.setSpacing(15)
        status_layout.setContentsMargins(30, 20, 30, 20)
        
        # Status label
        self.status_label = QLabel("Preparing something spectacular...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-weight: bold;
                padding: 20px 0;
            }
        """)
        
        status_layout.addWidget(self.status_label)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setFixedHeight(120)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(0, 198, 255, 0.4);
                border-radius: 6px;
                color: #FFFFFF;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.3);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #00C6FF;
                border-radius: 4px;
                min-height: 20px;
            }
        """)
        
        status_layout.addWidget(self.log_text)
        main_layout.addWidget(status_container)
        
        # Apply main styling
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 78, 146, 0.5), stop:1 rgba(0, 4, 40, 0.5));
                border-radius: 20px;
                border: 2px solid rgba(0, 198, 255, 0.6);
            }
        """)
        
    def center_window(self):
        """
        Center the splash screen on the desktop.
        
        Calculates the center position based on screen geometry and
        moves the window to that position.
        """
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
        
    def setup_worker(self):
        """
        Set up the initialization worker thread.
        
        Connects the worker's signals to the appropriate handlers
        for progress updates, completion, and error handling.
        """
        self.worker = InitializationWorker()
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.initialization_complete.connect(self.on_initialization_complete)
        self.worker.initialization_failed.connect(self.on_initialization_failed)
        
    def start_initialization(self):
        """
        Start the background initialization process.
        
        Launches the worker thread to begin application initialization
        while the splash screen displays progress updates.
        """
        logger.info("Starting background initialization...")
        self.worker.start()
    
    def update_progress(self, progress, message):
        """
        Update the splash screen with progress information.
        
        Args:
            progress (int): Progress percentage (0-100)
            message (str): Progress message to display
        """
        # Update status label
        self.status_label.setText(message)
        
        # Add to log display
        self.log_text.append(f"[{progress}%] {message}")
        
        # Scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
        # Process events to update UI
        self.app.processEvents()
        
    def center_window(self):
        """
        Center the splash screen window on the screen.
        
        Calculates the center position based on screen geometry and
        moves the window to that position.
        """
        # Get screen geometry
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # Get window size
        window_size = self.size()
        window_width = window_size.width()
        window_height = window_size.height()
        
        # Calculate center position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Move window to center
        self.move(x, y)
    
    def setup_responsive_geometry(self):
        """
        Setup responsive geometry for the splash screen.
        
        This method handles responsive sizing and positioning
        for different screen resolutions and DPI settings.
        """
        # Get screen geometry
        screen = QDesktopWidget().screenGeometry()
        
        # Calculate responsive size based on screen size
        base_width = 500
        base_height = 400
        
        # Scale based on screen size (minimum 80% of screen, maximum base size)
        scale_factor = min(0.8, max(0.4, min(screen.width() / 1920, screen.height() / 1080)))
        
        responsive_width = int(base_width * scale_factor)
        responsive_height = int(base_height * scale_factor)
        
        # Set responsive size
        self.setFixedSize(responsive_width, responsive_height)
        
        # Center the window
        self.center_window()
        
    def on_initialization_complete(self, controller, settings_manager):
        """
        Handle successful initialization completion.
        
        Args:
            controller (SpeechController): Initialized speech controller
            settings_manager (SettingsManager): Initialized settings manager
        """
        logger.info("Initialization completed successfully!")
        self.status_label.setText("Ready!")
        
        # Store initialized objects
        self.controller = controller
        self.settings_manager = settings_manager
        
        # Start fade out animation
        QTimer.singleShot(1000, self.fade_out)
        
    def on_initialization_failed(self, error_message):
        """
        Handle initialization failure.
        
        Args:
            error_message (str): Error message describing the failure
        """
        logger.error(f"Initialization failed: {error_message}")
        self.status_label.setText("Initialization Failed!")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #f44336;
                font-weight: bold;
            }
        """)
        
        # Show error message after delay
        QTimer.singleShot(2000, self.show_error_dialog)
        
    def show_error_dialog(self):
        """
        Show error dialog and close application.
        
        Displays a user-friendly error message and exits the application
        when initialization fails.
        """
        QMessageBox.critical(
            self,
            "Initialization Error",
            "Failed to initialize the application.\n\n"
            "Please check:\n"
            "• Microphone permissions\n"
            "• Audio drivers\n"
            "• System requirements\n\n"
            "For help, visit the project documentation."
        )
        self.app.quit()
        
    def fade_out(self):
        """
        Start fade-out animation.
        
        Creates a smooth fade-out animation that transitions from
        the splash screen to the main application window.
        """
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)  # Faster fade-out for better UX
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.finished.connect(self.show_main_window)
        self.fade_animation.start()
        
    def show_main_window(self):
        """
        Show the main application window.
        
        Creates and displays the main SpeechApp window, then closes
        the splash screen. Handles window positioning and focus.
        """
        try:
            logger.info("Creating main application window...")
            
            # Import SpeechApp here to avoid heavy dependencies at module level
            from speech_ui import SpeechApp
            
            # Create main window
            self.main_window = SpeechApp(self.controller, self.settings_manager)
            
            # Pass single instance manager to main window
            if hasattr(self, 'single_instance_manager'):
                self.main_window.single_instance_manager = self.single_instance_manager
            
            # Position window
            screen = QDesktopWidget().screenGeometry()
            window_size = self.main_window.size()
            x = 100
            y = 100
            x = max(0, min(x, screen.width() - window_size.width()))
            y = max(0, min(y, screen.height() - window_size.height()))
            self.main_window.move(x, y)
            
            # Show window
            self.main_window.show()
            self.main_window.showNormal()
            self.main_window.raise_()
            self.main_window.activateWindow()
            self.main_window.setFocus()
            
            # Close splash screen
            self.close()
            
            logger.info("Application started successfully!")
            logger.info("Press AltGr (or your configured hotkey) to start recording.")
            logger.info("Hold Mode: Hold the key down while speaking, release to transcribe.")
            logger.info("Toggle Mode: Press once to start, press again to stop.")
            
        except Exception as e:
            logger.error(f"Error creating main window: {e}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Application Error",
                f"Failed to create main window: {e}\n\n"
                "Please restart the application."
            )
            self.app.quit()
    
    def closeEvent(self, event):
        """Handle splash screen close event"""
        try:
            # Single instance lock cleanup is handled by CleanupManager
            # No need to manually release lock here
            
            # Clean up worker thread
            if hasattr(self, 'worker') and self.worker.isRunning():
                self.worker.quit()
                self.worker.wait(3000)  # Wait up to 3 seconds
                
        except Exception as e:
            logger.error(f"Error during splash screen close: {e}")
        finally:
            event.accept()
            
    def cleanup(self):
        """
        Clean up splash screen resources.
        
        Terminates the worker thread if still running and performs
        any necessary cleanup operations.
        """
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()