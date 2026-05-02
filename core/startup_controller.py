"""core/startup_controller.py — Wires run_at_startup setting to WindowsStartupManager."""

from .logging_config import get_logger

logger = get_logger(__name__)


class StartupController:
    """Applies the run_at_startup preference by calling WindowsStartupManager."""

    def __init__(self, startup_manager, exe_path: str):
        self._mgr = startup_manager
        self._exe_path = exe_path

    def apply(self, enabled: bool) -> None:
        """Enable or disable Windows autostart."""
        if enabled:
            self._mgr.enable(self._exe_path)
            logger.info(f"Autostart enabled: {self._exe_path}")
        else:
            self._mgr.disable()
            logger.info("Autostart disabled")

    def current_state(self) -> bool:
        """Return current registry state."""
        return self._mgr.is_enabled()
