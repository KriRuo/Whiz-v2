#!/usr/bin/env python3
"""
Speech-to-Text Tool with PyQt GUI
A hotkey-based voice-to-text application using Whisper and sounddevice.
"""

import sys
import traceback
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from speech_controller import SpeechController
from speech_ui import SpeechApp
from core.settings_manager import SettingsManager
from core.logging_config import initialize_logging, get_logger
from core.platform_utils import PlatformUtils

# Add FFmpeg to PATH if it exists locally
# This ensures Whisper can use FFmpeg for audio processing
def _setup_ffmpeg_path():
    """Add local FFmpeg installation to PATH if available"""
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.resolve()
        ffmpeg_bin = project_root / "ffmpeg" / "bin"
        
        # Check if FFmpeg exists
        if ffmpeg_bin.exists() and (ffmpeg_bin / "ffmpeg.exe").exists():
            # Add to PATH for this session
            ffmpeg_path_str = str(ffmpeg_bin)
            if ffmpeg_path_str not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{ffmpeg_path_str}{os.pathsep}{os.environ.get('PATH', '')}"
                return True
    except Exception:
        pass  # Silently fail - FFmpeg may be in system PATH
    return False

# Setup FFmpeg before anything else
_setup_ffmpeg_path()

def main():
    """Main application entry point"""
    try:
        # Initialize logging first
        initialize_logging(log_level='INFO', log_to_file=True, log_to_console=True)
        logger = get_logger(__name__)
        logger.info("Starting Whiz application...")
        
        # Check for single instance enforcement
        from core.single_instance_manager import SingleInstanceManager
        single_instance = SingleInstanceManager()
        
        success, message = single_instance.try_acquire_lock()
        if not success:
            logger.error(f"Single instance check failed: {message}")
            QMessageBox.critical(
                None,
                "Application Already Running",
                f"Cannot start Whiz: {message}\n\n"
                "Another instance of Whiz is already running.\n"
                "Please close the existing instance or wait for it to finish."
            )
            return 1
        elif message:
            logger.info(f"Single instance check: {message}")
            # Existing instance was activated, exit this instance
            return 0
        
        # ===== MULTI-MONITOR DPI AWARENESS SETUP =====
        # This configuration ensures proper scaling across different monitors and DPI settings
        
        # Step 1: Set Windows per-monitor DPI awareness (v2) via ctypes
        # This enables automatic scaling for each monitor independently
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes
                
                # Set per-monitor DPI awareness v2 (Windows 10 1703+)
                # This allows each monitor to have different DPI scaling
                # Use the correct constant value for PerMonitorV2
                DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
                
                # Get the SetProcessDpiAwarenessContext function
                user32 = ctypes.windll.user32
                
                # Try the modern API first (Windows 10 1703+)
                try:
                    # Define the function signature
                    user32.SetProcessDpiAwarenessContext.argtypes = [wintypes.HANDLE]
                    user32.SetProcessDpiAwarenessContext.restype = wintypes.BOOL
                    
                    # Call with the correct context value
                    result = user32.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
                    if result:
                        logger.info("Windows per-monitor DPI awareness (v2) enabled")
                    else:
                        raise Exception("SetProcessDpiAwarenessContext returned False")
                        
                except Exception as e:
                    logger.warning(f"Modern DPI awareness failed: {e}")
                    # Fallback: try older DPI awareness method
                    try:
                        user32.SetProcessDPIAware()
                        logger.info("Windows basic DPI awareness enabled (fallback)")
                    except Exception as e2:
                        logger.warning(f"Could not set basic DPI awareness: {e2}")
                        
            except Exception as e:
                logger.warning(f"Could not set Windows DPI awareness: {e}")
        
        # Step 2: Set Qt environment variables for automatic scaling
        # QT_AUTO_SCREEN_SCALE_FACTOR enables automatic detection of screen scale factors
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        
        # Step 3: Set Qt High DPI attributes
        # These must be set BEFORE creating QApplication
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # Enable automatic DPI scaling
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)       # Scale pixmaps/icons properly
        
        logger.info("High DPI configuration completed")
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Whiz")
        app.setApplicationVersion("1.0")
        
        # Set application icon
        from ui.icon_manager import IconManager

        icon = IconManager.get_app_icon()
        app.setWindowIcon(icon)
        logger.info("Application icon set")

        # Try to set Windows process icon
        if IconManager.set_windows_icon(IconManager.ICON_PATH):
            logger.info("Windows process icon set successfully")
        else:
            logger.warning("Could not set Windows process icon")
        
        # Set application style
        app.setStyle('Fusion')
        
        # Initialize settings manager
        logger.info("Initializing settings manager...")
        settings_manager = SettingsManager()
        
        # Register single instance cleanup with CleanupManager
        from core.cleanup_manager import register_cleanup_task, CleanupPhase
        register_cleanup_task(
            "single_instance_lock_cleanup",
            CleanupPhase.SYSTEM_RESOURCES,
            single_instance.cleanup_for_manager,
            timeout=5.0,
            critical=False  # Non-critical - atexit/signal handlers will handle it
        )
        logger.info("Single instance cleanup registered with CleanupManager")
        
        # Initialize the speech controller with settings
        logger.info("Initializing Speech-to-Text Tool...")
        settings = settings_manager.load_all()
        controller = SpeechController(
            hotkey=settings.get("behavior/hotkey", "alt gr"),  # Use saved hotkey or default
            model_size=settings.get("whisper/model_name", "tiny"),  # Default to fastest model
            auto_paste=settings.get("behavior/auto_paste", True),  # Use saved auto-paste setting
            language=settings.get("whisper/language", None),  # Use saved language or auto-detect
            temperature=settings.get("whisper/temperature", 0.0),  # Default to fastest temperature
            engine=settings.get("whisper/engine", "openai")  # Default to openai engine (faster-whisper has PyQt/ONNX issues)
        )
        
        # Check if controller initialized successfully
        if not controller.audio_manager.is_available():
            logger.warning("Audio system not available - running in limited mode")
            # Continue running with limited functionality instead of exiting
        
        # Create and show the main window
        window = SpeechApp(controller, settings_manager)
        
        # Store single instance manager for cleanup
        window.single_instance_manager = single_instance
        
        window.show()
        
        # On Windows, set the taskbar icon using Windows API
        if sys.platform == "win32":
            try:
                import ctypes
                
                # Get the window handle
                hwnd = int(window.winId())
                
                # Load the icon
                user32 = ctypes.windll.user32
                icon_path_obj = PlatformUtils.get_resource_path("assets/images/icons/app_icon_transparent.ico")
                abs_icon_path = str(icon_path_obj)
                
                hicon = user32.LoadImageW(
                    None, abs_icon_path, 1, 0, 0, 0x00000010
                )
                
                if hicon:
                    # Set both small and large icons
                    WM_SETICON = 0x0080
                    ICON_SMALL = 0
                    ICON_BIG = 1
                    
                    user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
                    user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
                    
                    logger.info("Windows taskbar icon set successfully")
            except Exception as e:
                logger.warning(f"Could not set Windows taskbar icon: {e}")
        
        logger.info("Application started successfully!")
        logger.info("Press AltGr (or your configured hotkey) to start recording.")
        logger.info("Hold Mode: Hold the key down while speaking, release to transcribe.")
        logger.info("Toggle Mode: Press once to start, press again to stop.")
        
        # Start the event loop
        result = app.exec_()
        
        # Cleanup is handled by CleanupManager and signal handlers
        # No need to manually release lock here
        
        return result
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("DEPENDENCY ERROR - Required packages are missing.")
        logger.error("To fix this: Run python setup_and_run.py or install manually: pip install -r requirements.txt")
        
        # Cleanup is handled by signal handlers and atexit
        # No need to manually release lock here
        
        # Show user-friendly error dialog
        QMessageBox.critical(
            None,
            "Missing Dependencies",
            f"Required packages are missing: {e}\n\n"
            "Please run the setup script:\n"
            "python setup_and_run.py\n\n"
            "Or install manually:\n"
            "pip install -r requirements.txt"
        )
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        
        # Cleanup is handled by signal handlers and atexit
        # No need to manually release lock here
        
        # Show error dialog with helpful information
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("Application Error")
        error_msg.setText("An unexpected error occurred:")
        error_msg.setDetailedText(
            f"{str(e)}\n\n"
            "For help, please:\n"
            "• Check microphone permissions\n"
            "• Ensure audio drivers are working\n"
            "• Try running as administrator\n"
            "• Run: python setup_and_run.py"
        )
        error_msg.exec_()
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
