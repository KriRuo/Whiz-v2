# Settings Components - Quick Reference Card

## 🎯 Quick Import

```python
from ui.components import SettingsSection, InfoLabel
```

## 📦 SettingsSection Component

### Syntax

```python
section = SettingsSection(title: str, layout_type: str)
```

### Parameters

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `title` | `str` | Any string | Section heading text |
| `layout_type` | `str` | `"form"`, `"vertical"`, `"horizontal"` | Layout style |

### Quick Examples

```python
# Form layout (most common for settings)
section = SettingsSection("Audio Settings", layout_type="form")
section.layout().addRow("Device:", device_combo)

# Vertical layout (for checkboxes)
section = SettingsSection("Options", layout_type="vertical")
section.layout().addWidget(checkbox1)
section.layout().addWidget(checkbox2)

# Horizontal layout (for button groups)
section = SettingsSection("Actions", layout_type="horizontal")
section.layout().addWidget(btn1)
section.layout().addWidget(btn2)
```

### Layout Access

```python
# Get the section's layout
layout = section.layout()

# Form layout methods
layout.addRow("Label:", widget)
layout.addRow(widget)

# Vertical/Horizontal layout methods
layout.addWidget(widget)
layout.addStretch()
```

## 📝 InfoLabel Component

### Syntax

```python
label = InfoLabel(text: str, font_size: int = 12)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | Required | Info text to display |
| `font_size` | `int` | `12` | Font size in pixels |

### Quick Examples

```python
# Standard info label
info = InfoLabel("This setting controls audio quality.")

# Larger font for important info
important = InfoLabel("⚠️ Requires restart!", font_size=14)

# Multi-line info (automatic wrapping)
help_text = InfoLabel(
    "Line 1: This is helpful info\n"
    "Line 2: More details here\n"
    "Line 3: Even more context"
)
```

## 🔄 Migration Cheat Sheet

### Pattern 1: Basic Section

**BEFORE** ❌
```python
group = QGroupBox("Settings")
layout = self.create_group_layout(group, "form")
layout.addRow("Option:", widget)
parent.addWidget(group)
```

**AFTER** ✅
```python
section = SettingsSection("Settings", layout_type="form")
section.layout().addRow("Option:", widget)
parent.addWidget(section)
```

### Pattern 2: Info Label

**BEFORE** ❌
```python
info = QLabel("Help text")
info.setWordWrap(True)
info.setStyleSheet(f"color: {ColorTokens.TEXT_SECONDARY}; font-size: 12px; padding: 12px; background-color: transparent; border-radius: 6px;")
```

**AFTER** ✅
```python
info = InfoLabel("Help text")
```

### Pattern 3: Complete Section with Info

**BEFORE** ❌
```python
group = QGroupBox("Theme")
layout = self.create_group_layout(group, "form")

combo = QComboBox()
combo.addItems(["light", "dark"])
layout.addRow("Theme:", combo)

info = QLabel("Choose your theme")
info.setWordWrap(True)
info.setStyleSheet(f"color: {ColorTokens.TEXT_SECONDARY}; font-size: 12px; padding: 12px; background-color: transparent; border-radius: 6px;")
layout.addRow(info)

parent.addWidget(group)
```

**AFTER** ✅
```python
section = SettingsSection("Theme", layout_type="form")

combo = QComboBox()
combo.addItems(["light", "dark"])
section.layout().addRow("Theme:", combo)

info = InfoLabel("Choose your theme")
section.layout().addRow(info)

parent.addWidget(section)
```

## 🎨 Styling Reference

### SettingsSection Styling

| Property | Value | Token |
|----------|-------|-------|
| Border | 1px solid | `BORDER_SUBTLE` |
| Border Radius | Medium | `RADIUS_MD` |
| Background | Primary | `BG_PRIMARY` |
| Title Color | Primary | `TEXT_PRIMARY` |
| Title Size | Extra Large | `FONT_XL` |
| Title Weight | Bold | `700` |
| Top Margin | 20px | Fixed |
| Title Padding | 0 MD 0 MD | `SPACING_MD` |

### InfoLabel Styling

| Property | Value | Token |
|----------|-------|-------|
| Text Color | Secondary | `TEXT_SECONDARY` |
| Font Size | 12px | Default (customizable) |
| Padding | 12px | Fixed |
| Background | Transparent | N/A |
| Border Radius | 6px | Fixed |
| Word Wrap | Enabled | Auto |
| Line Height | 1.4 | Fixed |

## ⚡ Common Patterns

### Pattern: Settings Group with Multiple Options

```python
# Create section
section = SettingsSection("Audio Settings", layout_type="form")

# Add multiple settings
section.layout().addRow("Input Device:", input_combo)
section.layout().addRow("Output Device:", output_combo)
section.layout().addRow("Sample Rate:", sample_spin)

# Add info
info = InfoLabel("Configure your audio devices here.")
section.layout().addRow(info)

# Add to parent
parent_layout.addWidget(section)
```

### Pattern: Checkbox Group with Vertical Layout

```python
# Create section with vertical layout
section = SettingsSection("Features", layout_type="vertical")

# Add checkboxes
section.layout().addWidget(QCheckBox("Enable feature 1"))
section.layout().addWidget(QCheckBox("Enable feature 2"))
section.layout().addWidget(QCheckBox("Enable feature 3"))

# Add info
info = InfoLabel("Enable or disable features as needed.")
section.layout().addWidget(info)

# Add to parent
parent_layout.addWidget(section)
```

### Pattern: Action Buttons with Horizontal Layout

```python
# Create section with horizontal layout
section = SettingsSection("Quick Actions", layout_type="horizontal")

# Add buttons
section.layout().addWidget(QPushButton("Test"))
section.layout().addWidget(QPushButton("Refresh"))
section.layout().addWidget(QPushButton("Reset"))
section.layout().addStretch()  # Push buttons to left

# Add to parent
parent_layout.addWidget(section)
```

## 📊 Benefits Matrix

| Aspect | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Code Lines** | 15/section | 10/section | ⬇️ 33% |
| **Info Label Lines** | 6 lines | 1 line | ⬇️ 83% |
| **Inline Styles** | 13+ locations | 0 | ⬇️ 100% |
| **Consistency Risk** | High | Zero | ✅ |
| **Maintainability** | Low | High | ⬆️ |
| **Readability** | Medium | High | ⬆️ |
| **DRY Compliance** | No | Yes | ✅ |

## 🚦 Decision Guide

### When to use SettingsSection?

✅ **Use when:**
- Creating any settings group with a title
- Need consistent section styling
- Want to ensure visual consistency
- Building preferences/settings dialogs

❌ **Don't use when:**
- Need completely custom styling
- Not in a settings context
- Building non-dialog UI (consider alternatives)

### When to use InfoLabel?

✅ **Use when:**
- Adding help/info text
- Need secondary text color
- Want consistent info styling
- Displaying multi-line explanations

❌ **Don't use when:**
- Need primary text color (use QLabel)
- Need custom complex styling
- Building non-info UI elements

## 💡 Tips & Tricks

### Tip 1: Access Layout Easily
```python
# Store layout reference if adding many widgets
section = SettingsSection("Settings", layout_type="form")
layout = section.layout()  # Get once, use many times
layout.addRow("A:", widget_a)
layout.addRow("B:", widget_b)
layout.addRow("C:", widget_c)
```

### Tip 2: Mix Components
```python
# Use both components together naturally
section = SettingsSection("Audio", layout_type="form")
section.layout().addRow("Device:", combo)
section.layout().addRow(InfoLabel("Choose your microphone"))
```

### Tip 3: Custom Font Size for Emphasis
```python
# Use larger font for important warnings
warning = InfoLabel("⚠️ This requires a restart!", font_size=14)
```

### Tip 4: Empty Label for Spacing
```python
# Use empty label for visual separation
section.layout().addRow(InfoLabel(""))  # Adds spacing
```

## 🔍 Troubleshooting

### Issue: Layout not appearing
**Solution:** Make sure to add the section to parent layout
```python
parent_layout.addWidget(section)  # Don't forget this!
```

### Issue: Text not wrapping
**Solution:** InfoLabel has auto word wrap, but ensure parent width is set
```python
# InfoLabel automatically wraps, no action needed
info = InfoLabel("Long text...")  # Wraps automatically
```

### Issue: Wrong layout type error
**Solution:** Use only valid layout types
```python
# Valid
SettingsSection("Title", layout_type="form")      # ✅
SettingsSection("Title", layout_type="vertical")  # ✅
SettingsSection("Title", layout_type="horizontal") # ✅

# Invalid
SettingsSection("Title", layout_type="grid")      # ❌ ValueError
```

## 📚 Related Documentation

- **Full Guide:** `docs/settings_component_demo.md`
- **Working Examples:** `examples/preferences_refactored_example.py`
- **Summary:** `docs/component_unification_summary.md`
- **Source Code:** `ui/components/base_components.py`

---

**Last Updated:** 2025-11-22  
**Version:** 1.0

