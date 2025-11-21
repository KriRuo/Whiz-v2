## Domain: Platform Integration & Environment

### Responsibilities
- Detect the current platform (Windows, macOS, Linux) and expose helper APIs for platform-specific behavior.
- Provide consistent locations for configuration, logs, temporary files, and assets across environments and packaging modes.
- Support both development (running from source) and packaged (PyInstaller, installers) execution.

### Key Modules
- `core/platform_utils.py`
  - Platform detection (`is_windows`, `is_macos`, `is_linux`, `get_platform`).
  - Paths:
    - `get_config_dir()` for app configuration storage.
    - `get_temp_dir()` for app-specific temp data.
    - `get_log_dir()` for log files (per-platform conventions).
    - `get_assets_dir()` / `get_resource_path()` for locating bundled resources in both source and frozen builds.
  - Executable path discovery for PyInstaller vs. source mode.
- `core/platform_features.py`
  - Higher-level feature detection (e.g., whether particular hotkey modes, auto-paste, or visual behaviors are supported on the current OS).
  - Used by `SpeechController` to tailor capabilities and fallbacks.
- Installers & Launchers
  - `installer-windows.iss`, `installers/`:
    - Windows-specific installer packaging, shortcuts, icons, and asset layout.
  - `scripts/launch/*`:
    - Platform-specific launch scripts for development or power users (.bat, .ps1, .vbs, .sh).

### Typical Flow
- At startup:
  - Core code uses `PlatformUtils` to determine platform and select appropriate behaviors (e.g., custom titlebar on Windows only).
  - Logging, configuration, and temp directories are resolved via `PlatformUtils` and created if missing.
- During runtime:
  - Platform feature checks influence hotkey behavior, auto-paste support, and UI affordances.
  - Resource loading goes through `get_resource_path` or `get_assets_dir` to handle both source and bundled layouts.

### Constraints & Notes
- Platform checks should be **centralized** in `PlatformUtils` / `PlatformFeatures`, not scattered as raw `sys.platform` checks.
- Paths returned by helpers should be treated as authoritative for config/log/temp/asset locations.
- When adding new platform-dependent behavior, prefer:
  - A capability flag in `PlatformFeatures` (easier to test and document).
  - A helper in `PlatformUtils` if it relates to paths or environment.


