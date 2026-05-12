#!/usr/bin/env python3
"""
Whiz — splash-screen entry point.

Shows the animated mascot splash immediately on launch, loads the model in
the background, then fades the splash out and reveals the main window.
"""

import os
# Must be set before ctranslate2/torch — their OpenMP runtimes read these
# at initialisation time and cannot be changed afterwards.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# ctranslate2 must be imported before any Qt module on Windows to avoid a
# shared-allocator conflict between its OpenMP runtime and Qt's.
import ctranslate2  # noqa: F401 — import side-effect only

import sys
import time
import traceback
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from speech_controller import SpeechController
from speech_ui import SpeechApp
from core.settings_manager import SettingsManager
from core.logging_config import initialize_logging, get_logger
from core.platform_utils import PlatformUtils


def _setup_ffmpeg_path():
    try:
        ffmpeg_bin = Path(__file__).parent.resolve() / "ffmpeg" / "bin"
        if ffmpeg_bin.exists() and (ffmpeg_bin / "ffmpeg.exe").exists():
            s = str(ffmpeg_bin)
            if s not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{s}{os.pathsep}{os.environ.get('PATH', '')}"
    except Exception:
        pass


_setup_ffmpeg_path()


def _set_taskbar_icon(window):
    try:
        import ctypes
        hwnd = int(window.winId())
        user32 = ctypes.windll.user32
        ico = str(PlatformUtils.get_resource_path("assets/images/icons/app_icon_transparent.ico"))
        hicon = user32.LoadImageW(None, ico, 1, 0, 0, 0x00000010)
        if hicon:
            user32.SendMessageW(hwnd, 0x0080, 0, hicon)
            user32.SendMessageW(hwnd, 0x0080, 1, hicon)
    except Exception:
        pass


def main():
    try:
        initialize_logging(log_level='INFO', log_to_file=True, log_to_console=True)
        logger = get_logger(__name__)
        logger.info("Starting Whiz (splash mode)...")

        # ── DPI setup (must happen before QApplication) ──────────────────────
        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            user32.SetProcessDpiAwarenessContext.argtypes = [wintypes.HANDLE]
            user32.SetProcessDpiAwarenessContext.restype  = wintypes.BOOL
            if not user32.SetProcessDpiAwarenessContext(-4):
                raise Exception("v2 failed")
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps,    True)

        # QApplication must exist before any QWidget or QMessageBox is created.
        app = QApplication(sys.argv)
        app.setApplicationName("Whiz")
        app.setApplicationVersion("1.0")
        app.setStyle('Fusion')

        # ── single instance check (needs QApplication for QSharedMemory) ─────
        from core.single_instance_manager import SingleInstanceManager
        single_instance = SingleInstanceManager()
        ok, msg = single_instance.try_acquire_lock()
        if not ok:
            logger.error(f"Single instance check failed: {msg}")
            QMessageBox.critical(None, "Application Already Running",
                                 f"Cannot start Whiz: {msg}\n\nAnother instance is already running.")
            return 1
        elif msg:
            return 0

        from ui.icon_manager import IconManager
        app.setWindowIcon(IconManager.get_app_icon())
        IconManager.set_windows_icon(IconManager.ICON_PATH)

        # ── show splash immediately ───────────────────────────────────────────
        _splash_shown_at = time.monotonic()
        _SPLASH_MIN_SECONDS = 1.5  # always visible for at least this long

        from splash_screen import SplashScreen
        splash = SplashScreen()
        splash.show()
        app.processEvents()  # paint splash at full opacity before heavy init

        # ── controller + main window (window stays hidden) ───────────────────
        settings_manager = SettingsManager()
        app.processEvents()

        from core.cleanup_manager import register_cleanup_task, CleanupPhase
        register_cleanup_task(
            "single_instance_lock_cleanup",
            CleanupPhase.SYSTEM_RESOURCES,
            single_instance.cleanup_for_manager,
            timeout=5.0,
            critical=False,
        )

        settings = settings_manager.load_all()
        app.processEvents()

        controller = SpeechController(
            hotkey    = settings.get("behavior/hotkey",      "alt gr"),
            model_size= settings.get("whisper/model_name",   "tiny"),
            auto_paste= settings.get("behavior/auto_paste",  True),
            language  = settings.get("whisper/language",     None),
            temperature=settings.get("whisper/temperature",  0.0),
            engine    = settings.get("whisper/engine",       "faster"),
        )
        app.processEvents()

        window = SpeechApp(controller, settings_manager)
        app.processEvents()
        window.single_instance_manager = single_instance

        # Skip the in-tab mascot — the splash screen covers this role.
        try:
            window.record_tab.mascot_widget._timer.stop()
            window.record_tab._circle_stack.setCurrentIndex(1)
        except Exception:
            pass

        # ── wire dismiss → reveal ─────────────────────────────────────────────
        def _reveal():
            window.show()
            _set_taskbar_icon(window)
            logger.info("Main window shown after splash.")

        splash.finished.connect(_reveal)

        # Poll for model ready at 250 ms intervals.
        # Dismiss on "loaded" OR on any error/timeout — never leave the splash blocking forever.
        # Enforce a minimum visible duration so the splash is always seen.
        poll = QTimer()
        poll.setInterval(250)
        _MODEL_WAIT_TIMEOUT = 90  # seconds

        def _check():
            status = controller.get_model_status()
            elapsed = time.monotonic() - _splash_shown_at
            timed_out = elapsed >= _MODEL_WAIT_TIMEOUT
            min_elapsed = elapsed >= _SPLASH_MIN_SECONDS
            ready = status == "loaded" or status.startswith("error:") or timed_out
            if ready and min_elapsed:
                poll.stop()
                if status.startswith("error:"):
                    logger.error(f"Model load failed, showing main window: {status}")
                elif timed_out:
                    logger.warning(f"Model load timed out after {elapsed:.0f}s, showing main window anyway")
                splash.dismiss()

        poll.timeout.connect(_check)
        poll.start()

        logger.info("Splash shown; model loading in background.")
        return app.exec_()

    except ImportError as e:
        logger.error(f"Import error: {e}")
        QMessageBox.critical(None, "Missing Dependencies",
                             f"Required packages are missing: {e}\n\n"
                             "Run: pip install -r requirements.txt")
        return 1

    except Exception as e:
        logger.error(traceback.format_exc())
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Application Error")
        msg.setText("An unexpected error occurred:")
        msg.setDetailedText(str(e))
        msg.exec_()
        return 1


if __name__ == "__main__":
    sys.exit(main())
