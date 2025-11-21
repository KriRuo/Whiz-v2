## Domain: UI & Layout

### Responsibilities
- Provide a **modern, responsive PyQt5 UI** for recording, managing transcripts, and configuring settings.
- Implement a custom Windows titlebar and frameless window behavior while supporting native titlebars elsewhere.
- Maintain consistent styling, spacing, and typography across components and screen sizes.

### Key Modules
- `ui/main_window.py`
  - Main window composition: titlebar, tab widget, content area, and footer.
  - System tray integration and minimize-to-tray behavior.
  - Responsive window geometry, DPI handling, and screen change detection.
- `ui/layout_system.py`
  - Layout design tokens (`LayoutTokens`, `ColorTokens`, spacing/margin/font scales).
  - Responsive helpers (`ScreenSizeClass`, `ResponsiveBreakpoints`, `ResponsiveSizing`).
  - DPI scaling helpers and adaptive spacing.
- `ui/record_tab.py`
  - Recording UI: mic controls, waveform, status label, tips, and visual indicator integration.
- `ui/transcripts_tab.py`
  - Transcript list UI with scroll area, timestamps, and copy-to-clipboard actions.
- `ui/preferences_dialog.py`
  - Settings UI with categorized tabs, live validation, and audio device testing.
- `ui/custom_titlebar.py`
  - Custom titlebar implementation for Windows (frameless window, window controls, drag behavior).
- `ui/styles/main_styles.py`, `ui/styles/theme_dark.qss`, `ui/styles/theme_light.qss`
  - Central stylesheet and theme-specific overrides.
- `ui/widgets/*` and `ui/components/*`
  - Reusable visual components (e.g., mic halo, gradient tabs, transcript expander, mic circle).

### Typical Flow
- Startup:
  - `main.py` creates the main application and instantiates `MainWindow`.
  - `MainWindow` sets up layout, titlebar, tab widget, footer, and system tray.
  - Stylesheets are applied via `MainStyles.get_responsive_stylesheet()`.
- Interaction:
  - Record tab emits signals/callbacks to `SpeechController` for recording actions.
  - Transcripts tab is updated via callbacks/signals carrying new transcript data.
  - Preferences dialog reads/writes settings via `SettingsManager`, then emits changes back to main UI and controller.

### Constraints & Notes
- UI code must **not perform heavy work** directly:
  - Long-running operations (model loading, transcription) should stay in controller/core layers.
  - UI should react to signals and callbacks instead of blocking.
- Layout changes should use the **layout system** (tokens, responsive helpers) instead of hard-coded pixel values where possible.
- Styling should be centralized in stylesheets or token-based helpers, avoiding duplicated inline styles unless necessary.
- Windows-specific behaviors (frameless window, hit testing) live in titlebar/system-tray modules and should be guarded by platform checks.


