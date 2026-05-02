"""core/launch_mode.py — Detect how the application was launched."""


def is_tray_launch(argv: list) -> bool:
    """Return True if argv contains '--tray' (silent tray-only launch)."""
    return "--tray" in argv
