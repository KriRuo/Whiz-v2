# Custom Title Bar Implementation

This document describes the custom title bar implementation for the Speech-to-Text Tool PyQt5 application.

## Overview

The custom title bar replaces the standard Windows title bar with a modern, styled header that matches the app's design while maintaining all native Windows behaviors including:

- Window dragging
- Double-click to maximize/restore
- Edge and corner resizing
- Windows Snap functionality
- Minimize/Maximize/Close buttons

## Files Added/Modified

### New Files
- `ui/custom_titlebar.py` - Main implementation of the custom title bar
- `test_titlebar.py` - Test script to verify functionality

### Modified Files
- `speech_ui.py` - Updated to integrate the custom title bar

## Implementation Details

### TitleBar Widget (`ui/custom_titlebar.py`)

The `TitleBar` class is a QWidget that provides:

1. **Visual Components**:
   - App icon (🎤 microphone emoji)
   - Title text ("Speech-to-Text Tool")
   - Minimize button (−)
   - Maximize/Restore button (□/❐)
   - Close button (×)

2. **Functionality**:
   - Mouse drag handling for window movement
   - Double-click to toggle maximize/restore
   - Button click handlers for window actions
   - Modern styling with gradient background

3. **Styling**:
   - 44px height (standard title bar height)
   - Navy gradient background matching app theme
   - Rounded top corners
   - Hover and pressed states for buttons
   - Special styling for close button (red hover)

### Window Integration (`speech_ui.py`)

The main window integration includes:

1. **Frameless Window Setup**:
   - Applied `Qt.FramelessWindowHint` flag
   - Maintained window functionality flags

2. **Layout Structure**:
   - Title bar at the top
   - Content widget below with rounded bottom corners
   - Seamless visual connection between title bar and content

3. **Event Handling**:
   - Connected title bar signals to window methods
   - Added `toggle_maximize()` method for maximize/restore functionality

### Windows Hit-Testing

The `WindowHitTester` class provides Windows-specific hit-testing for proper resize and snap functionality:

1. **Resize Borders**: 8px border around window edges and corners
2. **Hit-Test Constants**: Maps cursor positions to Windows hit-test codes
3. **Native Event Override**: Intercepts Windows messages for proper behavior

## Usage

### Basic Integration

```python
from ui.custom_titlebar import TitleBar, apply_frameless_window_hints, setup_window_resize_border

# In your main window's init_ui method:
apply_frameless_window_hints(self)

# Create title bar
self.title_bar = TitleBar(self)
self.title_bar.minimize_clicked.connect(self.showMinimized)
self.title_bar.maximize_clicked.connect(self.toggle_maximize)
self.title_bar.close_clicked.connect(self.close)

# Set up Windows hit-testing
setup_window_resize_border(self, self.title_bar)

# Add to layout
layout.addWidget(self.title_bar)
```

### Customization

#### Changing Colors
Edit the stylesheet in `TitleBar.setup_styling()`:

```python
#TitleBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a365d, stop:1 #2d3748);  # Change these colors
}
```

#### Changing Title Text
```python
self.title_bar.set_title("Your Custom Title")
```

#### Adding App Icon
Replace the emoji icon with a proper QIcon:

```python
# In TitleBar.init_ui()
icon = QIcon("path/to/your/icon.png")
self.icon_label.setPixmap(icon.pixmap(24, 24))
```

## Testing

### Manual Testing Checklist

- [ ] **Window Dragging**: Click and drag the title bar to move the window
- [ ] **Double-Click Maximize**: Double-click title bar to toggle maximize/restore
- [ ] **Button Functionality**:
  - [ ] Minimize button works
  - [ ] Maximize/Restore button works and updates icon
  - [ ] Close button works
- [ ] **Resize Functionality**:
  - [ ] Resize from left edge
  - [ ] Resize from right edge
  - [ ] Resize from top edge
  - [ ] Resize from bottom edge
  - [ ] Resize from corners (top-left, top-right, bottom-left, bottom-right)
- [ ] **Windows Snap**: Win+Arrow keys work for snapping
- [ ] **Visual Appearance**:
  - [ ] Rounded corners look clean
  - [ ] No visual seams between title bar and content
  - [ ] Hover states work on buttons
  - [ ] Close button has red hover state

### Automated Testing

Run the test script:

```bash
python test_titlebar.py
```

This opens a test window where you can verify all functionality.

## Platform Support

- **Primary**: Windows 10/11 (full functionality with native hit-testing)
- **Fallback**: Other platforms (basic frameless functionality without native hit-testing)

## Troubleshooting

### Common Issues

1. **Window not draggable**: Ensure `apply_frameless_window_hints()` is called
2. **Resize not working**: Check that `setup_window_resize_border()` is called on Windows
3. **Visual glitches**: Verify stylesheet is applied correctly and margins are set to 0
4. **Buttons not working**: Ensure signals are connected properly

### Debug Tips

- Check console output for any error messages
- Verify all imports are working correctly
- Test on different DPI scaling settings (100%, 125%, 150%)
- Ensure PyQt5 version compatibility

## Future Enhancements

Potential improvements for the custom title bar:

1. **System Integration**: Better integration with Windows 11 snap layouts
2. **Accessibility**: Add keyboard navigation support
3. **Theming**: Support for light/dark themes
4. **Animation**: Smooth transitions for maximize/restore
5. **Customization**: User-configurable colors and styles
