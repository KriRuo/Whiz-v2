## File: `core/windows_startup.py`

### Purpose
- Manages Windows run-at-startup via the `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` registry key.
- Windows-only — not imported on macOS or Linux.

### Public API

| Method | Signature | Behaviour |
|--------|-----------|-----------|
| `enable` | `enable(exe_path: str) -> None` | Writes `"<exe_path> --tray"` to the Run key under the name `"Whiz"`. |
| `disable` | `disable() -> None` | Deletes the `"Whiz"` Run entry; silently no-ops if the entry does not exist. |
| `is_enabled` | `is_enabled() -> bool` | Returns `True` if the `"Whiz"` Run entry is present. |

### Notes / Gotchas
- The `--tray` flag appended by `enable()` causes the app to start minimised to tray rather than showing the main window.
- Called from `ui/preferences_dialog.py` "Start with Windows" checkbox; no direct UI dependency inside this module.
- Uses `winreg` from the stdlib — no third-party dependencies.
