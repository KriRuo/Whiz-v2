#!/usr/bin/env python3
"""
main_with_splash.py
-------------------
Entry point for Whiz Voice-to-Text Application with splash screen.

This module serves as the main entry point when users want to launch Whiz
with a splash screen. It initializes the logging framework, creates the
splash screen, and handles the transition to the main application.

The splash screen provides visual feedback during initialization and loads
the main application in a background thread for a smooth user experience.

Features:
    - Logging framework initialization
    - Splash screen with progress display
    - Background initialization thread
    - Error handling and user feedback
    - Cross-platform compatibility

Dependencies:
    - PyQt5: GUI framework
    - core.logging_config: Centralized logging system
    - splash_screen: Splash screen implementation

Example:
    Launch with splash screen:
        python main_with_splash.py
    
    Or use the batch file:
        launch-whiz-splash.bat

Author: Whiz Development Team
Last Updated: October 10, 2025
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# Import core modules
from core.logging_config import initialize_logging, get_logger
from core.single_instance_manager import SingleInstanceManager
from splash_screen import SplashScreen


def main():
    """
    Main application entry point with splash screen.
    
    Initializes the logging framework, creates the Qt application,
    shows the splash screen, and starts the initialization process.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Initialize logging first
        initialize_logging(log_level='INFO', log_to_file=True, log_to_console=True)
        logger = get_logger(__name__)
        logger.info("Starting Whiz application with splash screen...")
        
        # Check for single instance enforcement
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
        
        # Set application style
        app.setStyle('Fusion')
        
        logger.info("Creating splash screen...")
        
        # Create splash screen
        splash = SplashScreen(app)
        splash.single_instance_manager = single_instance  # Store for cleanup
        splash.show()
        
        # Start initialization
        splash.start_initialization()
        
        logger.info("Splash screen displayed, starting event loop...")
        
        # Start event loop
        return app.exec_()
        
    except ImportError as e:
        # Handle missing dependencies
        error_msg = f"Import error: {e}"
        print(error_msg)
        print("\n" + "="*50)
        print("DEPENDENCY ERROR")
        print("="*50)
        print("Required packages are missing.")
        print("\nTo fix this:")
        print("1. Run: python setup_and_run.py")
        print("2. Or install manually: pip install -r requirements.txt")
        print("\nIf you're a new user, just run launch-whiz.bat")
        
        # Clean up single instance lock if we have it
        try:
            if 'single_instance' in locals():
                single_instance.release_lock()
        except Exception:
            pass
        
        # Show user-friendly error dialog
        try:
            QMessageBox.critical(
                None,
                "Missing Dependencies",
                f"Required packages are missing: {e}\n\n"
                "Please run the setup script:\n"
                "python setup_and_run.py\n\n"
                "Or double-click launch-whiz.bat"
            )
        except:
            pass  # If Qt isn't available, just print the error
            
        return 1
        
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {e}"
        print(error_msg)
        traceback.print_exc()
        
        # Clean up single instance lock if we have it
        try:
            if 'single_instance' in locals():
                single_instance.release_lock()
        except Exception:
            pass
        
        # Show error dialog with helpful information
        try:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("Application Error")
            error_dialog.setText("An unexpected error occurred:")
            error_dialog.setDetailedText(
                f"{str(e)}\n\n"
                "For help, please:\n"
                "• Check microphone permissions\n"
                "• Ensure audio drivers are working\n"
                "• Try running as administrator\n"
                "• Check system requirements\n\n"
                "Full error details:\n"
                f"{traceback.format_exc()}"
            )
            error_dialog.exec_()
        except:
            pass  # If Qt isn't available, just print the error
        
        return 1


if __name__ == "__main__":
    sys.exit(main())