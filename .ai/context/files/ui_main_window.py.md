## File: `ui/main_window.py`

### Purpose
- Main PyQt5 window class for Whiz:
  - Hosts the Record/Transcripts UI, footer, and preferences entry points.
  - Implements Windows-specific custom titlebar and frameless behavior.
  - Manages responsive geometry, DPI-aware layout, and multi-monitor behavior.
  - Integrates the system tray and minimize-to-tray behavior.

### Key Responsibilities & Behavior
- **Construction & Layout**
  - Accepts a `SettingsManager` instance and stores it as `self.settings_manager`.
  - Builds the window in `init_window()`:
    - Determines whether to use a custom titlebar via `PlatformUtils.is_windows()`.
    - For Windows:
      - Applies frameless window hints and hit-testing via `TitleBar`, `apply_frameless_window_hints`, and `setup_window_resize_border`.
    - Creates:
      - A central widget with a top-level vertical layout.
      - Optional custom titlebar (Windows-only).
      - A `content_widget` with a layout created by `LayoutBuilder.create_main_layout(...)`.
      - A `GradientTabWidget` to host tabs (Record, Transcripts, etc.).
      - A small footer widget with a `QLabel` used to display model/status info.
    - Applies responsive styles via `MainStyles.get_responsive_stylesheet()` and disables tab label elision.
- **Responsive Geometry**
  - `setup_responsive_geometry()`:
    - Detects the appropriate screen (cursor screen, or primary as fallback).
    - Uses `ResponsiveBreakpoints` and `ResponsiveSizing` to:
      - Classify screen size and compute window dimensions.
      - Set min/max window sizes from `ResponsiveSizing.WINDOW_SIZING`.
      - Center the window on the chosen screen while staying within bounds.
  - `connect_screen_change_detection()` and `handle_screen_change()`:
    - Listen to screen changes for multi-monitor setups.
    - Recompute window size constraints and regenerate the responsive stylesheet when screen class or DPI changes.
    - Emit `window_state_changed` so child widgets can adapt.
  - `resizeEvent()` also emits `window_state_changed` for live layout updates.
- **Preferences & Settings**
  - Exposes signals:
    - `preferences_opened`, `settings_changed`, and `window_state_changed`.
  - `open_preferences()`:
    - Ensures only one preferences dialog is open at a time via `_preferences_dialog_open`.
    - Emits `preferences_opened`, constructs `PreferencesDialog` with `settings_manager`, and connects `settings_changed` back to `on_settings_changed()`.
  - `on_settings_changed(settings: dict)`:
    - Calls `settings_manager.apply_all(self)` to propagate settings to controller and UI.
    - Updates sound options (enabled flag, start/stop tone files) immediately.
    - Emits `settings_changed(settings)` for outer application code (`SpeechApp`) to react.
  - For non-Windows platforms, `add_native_settings_button()` adds a bottom-aligned ⚙️ button to open preferences.
- **Tray & Lifecycle**
  - `init_system_tray()`:
    - Creates a `SystemTrayIcon` when the tray is available.
    - Wires tray signals to `show_from_tray`, `show_settings`, and `quit_application`.
    - Updates a `behavior/system_tray_available` setting via `SettingsManager`.
  - `set_minimize_to_tray(enabled)` toggles tray behavior and updates tray menu text.
  - `closeEvent(event)`:
    - If minimize-to-tray is enabled and tray exists, hides to tray and ignores the close event.
    - Otherwise, saves window state via `SettingsManager`, cleans up tray, and accepts the close.
  - `quit_application()`:
    - Saves window state, calls `controller.cleanup()` (if present) and tray cleanup, then quits the app.

### Dependencies & Interactions
- Depends on:
  - `ui.custom_titlebar`, `ui.layout_system`, `ui.widgets.gradient_tab_widget`, `ui.system_tray`, `ui.styles.main_styles`.
  - `core.platform_utils.PlatformUtils` for platform checks.
  - `core.logging_config.get_logger` and `SettingsManager` for logging and settings.
- Interacts with:
  - `SpeechApp` / controlling class, usually via:
    - Attached `controller` attribute (e.g., `SpeechController`) for cleanup and settings application.
    - `settings_changed` signal to inform higher-level app code.

### Notes / Gotchas
- The main window assumes `settings_manager` is the authoritative source for saving/restoring geometry/state and some behavior flags.
- Custom titlebar behavior is **Windows-only**; Linux/macOS must use the native titlebar path guarded by `PlatformUtils`.
- `MainWindow` does not itself manage the Record/Transcripts tab content; it relies on the caller to add tabs and handle controller wiring.


