# Theme Support for Unified Components

## Current Status

✅ **Works perfectly for current dark-mode-only app**  
⚠️ **Needs update when light mode is fully implemented**

## Issue

Our `SettingsSection` and `InfoLabel` components use f-strings with `ColorTokens`:

```python
self.setStyleSheet(f"""
    QLabel {{
        color: {ColorTokens.TEXT_SECONDARY};  # Becomes "#B8BFC8" at creation
    }}
""")
```

This "bakes in" the colors at component creation time, so they won't update when theme switches.

## Solutions (for when light mode is implemented)

### Option 1: Rely on Stylesheet Cascade (Simplest) ✨

The dialog's `get_dialog_stylesheet()` applies global QLabel and QGroupBox styles. If we remove the `!important` flags and specific colors from our components, they would inherit from parent.

**Changes needed:**
```python
# In SettingsSection.apply_styling()
self.setStyleSheet(f"""
    QGroupBox {{
        font-weight: 600;
        border: 1px solid;  # Remove specific color
        border-radius: {LayoutTokens.RADIUS_MD}px;
        margin-top: 20px;
        padding-top: 20px;
        # Let colors cascade from parent
    }}
""")
```

**Pros:** Simple, works automatically with theme switching  
**Cons:** Less control over specific styling

### Option 2: Theme-Aware Components (Most Robust) 🔧

Make components listen to theme changes and re-apply styling:

```python
class SettingsSection(QGroupBox):
    def __init__(self, title: str, layout_type: str = "form", theme_manager=None):
        super().__init__(title)
        self.theme_manager = theme_manager
        self.init_layout(layout_type)
        self.apply_styling()
        
        # Connect to theme changes
        if theme_manager:
            theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def on_theme_changed(self, theme: str):
        """Reapply styling when theme changes."""
        self.apply_styling()
    
    def apply_styling(self):
        """Apply theme-appropriate styling."""
        # Get colors from current theme
        colors = self.get_theme_colors()
        self.setStyleSheet(f"""
            QGroupBox {{
                color: {colors['text_primary']};
                border: 1px solid {colors['border_subtle']};
                background-color: {colors['bg_primary']};
                ...
            }}
        """)
```

**Pros:** Full control, explicit theme support  
**Cons:** More complex, requires passing theme_manager

### Option 3: Dynamic ColorTokens (Medium Complexity) 🎨

Make `ColorTokens` a class that updates based on theme:

```python
class ColorTokens:
    _current_theme = "dark"
    
    @classmethod
    def set_theme(cls, theme: str):
        cls._current_theme = theme
    
    @classmethod
    @property
    def TEXT_PRIMARY(cls):
        if cls._current_theme == "dark":
            return "#FFFFFF"
        else:
            return "#000000"
    
    # ... other properties
```

Then when theme switches, call `ColorTokens.set_theme("light")` and recreate components.

**Pros:** Centralized color management  
**Cons:** Requires component recreation on theme change

### Option 4: Use QSS Variables (If Qt supports) 🔮

Some Qt versions support CSS-like variables. Could define colors globally.

## Recommended Approach

### For Now (Dark Mode Only)
✅ **No changes needed** - current implementation is perfect

### When Light Mode is Added
Recommend **Option 1** (Stylesheet Cascade) because:
1. Simplest to implement
2. Leverages existing dialog stylesheet system
3. Automatic theme switching
4. Minimal code changes

### Implementation Plan

When light mode is implemented:

1. **Update ThemeManager** to have real light/dark stylesheets
2. **Modify Component Styles** to remove hard-coded colors:
   ```python
   # Remove: color: {ColorTokens.TEXT_PRIMARY} !important;
   # Replace with: inherit from parent or use generic color names
   ```
3. **Test** theme switching with preferences dialog open
4. **Adjust** as needed based on visual results

## Testing Checklist (For Future Light Mode)

When implementing light mode:
- [ ] Open preferences dialog
- [ ] Switch theme to light
- [ ] Verify sections have proper colors
- [ ] Verify info labels are readable
- [ ] Switch back to dark
- [ ] Verify everything still looks good
- [ ] Test with dialog open during theme switch
- [ ] Test with dialog closed during theme switch

## Notes

- Current app is dark-mode only (see `theme_manager.py` line 309)
- `ColorTokens` are currently static dark-mode values
- Dialog has `get_dialog_stylesheet()` that could cascade colors
- Consider using `!important` sparingly to allow cascade

## Related Files

- `ui/components/base_components.py` - Component implementations
- `ui/theme_manager.py` - Theme switching logic
- `ui/layout_system.py` - ColorTokens definitions
- `ui/preferences_dialog.py` - Dialog that uses components

---

**Status:** Documented for future reference  
**Priority:** Low (only needed when light mode is implemented)  
**Impact:** Medium (affects visual appearance only)

