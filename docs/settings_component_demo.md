# Settings Component Usage Guide

This guide demonstrates how to use the new unified `SettingsSection` and `InfoLabel` components for creating consistent settings pages.

## New Unified Components

### 1. SettingsSection
A reusable QGroupBox wrapper with consistent styling for section headers.

**Features:**
- Consistent border, padding, and typography
- Supports "form", "vertical", and "horizontal" layout types
- Automatic styling using ColorTokens and LayoutTokens

### 2. InfoLabel
A reusable QLabel for help/info text with consistent styling.

**Features:**
- Secondary text color for reduced visual weight
- Automatic word wrapping
- Consistent padding and line height
- Customizable font size

## Before and After Comparison

### BEFORE (Old Pattern)

```python
def create_general_tab(self):
    """Create the General tab using layout system."""
    tab = QWidget()
    layout = self.create_tab_layout(tab)
    
    # UI Settings Group
    ui_group = QGroupBox("User Interface")
    ui_layout = self.create_group_layout(ui_group, "form")
    
    # Theme selection
    self.theme_combo = self.create_styled_combobox(["system", "light", "dark"])
    ui_layout.addRow("Theme:", self.theme_combo)
    
    # Theme info
    theme_info = QLabel(
        "• system: Follow your system's dark/light mode setting\n"
        "• light: Always use light theme\n"
        "• dark: Always use dark theme"
    )
    theme_info.setWordWrap(True)
    theme_info.setStyleSheet(f"color: {ColorTokens.TEXT_SECONDARY}; font-size: 12px; padding: 12px; background-color: transparent; border-radius: 6px;")
    ui_layout.addRow("Theme Info:", theme_info)
    
    layout.addWidget(ui_group)
    
    # Language Settings Group
    language_group = QGroupBox("Language Settings")
    language_layout = self.create_group_layout(language_group, "form")
    
    # Language selection
    self.language_combo = self.create_styled_combobox([
        "auto", "en", "de", "es", "fr", "it", "pt", "ru", "ja", "ko", "zh", 
        "sv", "fi", "no", "da", "nl", "pl", "tr", "ar", "hi"
    ])
    language_layout.addRow("Language:", self.language_combo)
    
    # Language info
    language_info = QLabel(
        "• auto: Automatically detect language from speech\n"
        "• Specific languages: Force transcription in that language\n"
        "• Using a specific language can improve accuracy"
    )
    language_info.setWordWrap(True)
    language_info.setStyleSheet(f"color: {ColorTokens.TEXT_SECONDARY}; font-size: 12px; padding: 12px; background-color: transparent; border-radius: 6px;")
    language_layout.addRow("Language Info:", language_info)
    
    layout.addWidget(language_group)
```

**Issues with old pattern:**
- Repetitive QGroupBox creation
- Manual layout creation each time
- Inline stylesheet for every info label (not DRY)
- Harder to maintain consistency across tabs
- More verbose and error-prone

### AFTER (New Pattern with Unified Components)

```python
from ui.components import SettingsSection, InfoLabel

def create_general_tab(self):
    """Create the General tab using unified components."""
    tab = QWidget()
    layout = self.create_tab_layout(tab)
    
    # UI Settings Section
    ui_section = SettingsSection("User Interface", layout_type="form")
    
    # Theme selection
    self.theme_combo = self.create_styled_combobox(["system", "light", "dark"])
    ui_section.layout().addRow("Theme:", self.theme_combo)
    
    # Theme info
    theme_info = InfoLabel(
        "• system: Follow your system's dark/light mode setting\n"
        "• light: Always use light theme\n"
        "• dark: Always use dark theme"
    )
    ui_section.layout().addRow(theme_info)
    
    layout.addWidget(ui_section)
    
    # Language Settings Section
    language_section = SettingsSection("Language Settings", layout_type="form")
    
    # Language selection
    self.language_combo = self.create_styled_combobox([
        "auto", "en", "de", "es", "fr", "it", "pt", "ru", "ja", "ko", "zh", 
        "sv", "fi", "no", "da", "nl", "pl", "tr", "ar", "hi"
    ])
    language_section.layout().addRow("Language:", self.language_combo)
    
    # Language info
    language_info = InfoLabel(
        "• auto: Automatically detect language from speech\n"
        "• Specific languages: Force transcription in that language\n"
        "• Using a specific language can improve accuracy"
    )
    language_section.layout().addRow(language_info)
    
    layout.addWidget(language_section)
```

**Benefits of new pattern:**
- ✅ Cleaner, more readable code
- ✅ No repetitive QGroupBox styling
- ✅ No inline stylesheets to maintain
- ✅ Consistent styling automatically applied
- ✅ Easier to update global styling (change once in component)
- ✅ Less verbose and less error-prone
- ✅ Better adherence to DRY principle

## Usage Examples

### Example 1: Form Layout Section

```python
# Create a settings section with form layout
audio_section = SettingsSection("Audio Settings", layout_type="form")

# Add form rows
audio_section.layout().addRow("Input Device:", device_combo)
audio_section.layout().addRow("Sample Rate:", sample_rate_spin)

# Add info label
info = InfoLabel("Choose your preferred microphone for recording.")
audio_section.layout().addRow(info)

# Add to parent layout
parent_layout.addWidget(audio_section)
```

### Example 2: Vertical Layout Section

```python
# Create a section with vertical layout for checkboxes
behavior_section = SettingsSection("Recording Behavior", layout_type="vertical")

# Add checkboxes vertically
behavior_section.layout().addWidget(auto_paste_checkbox)
behavior_section.layout().addWidget(toggle_mode_checkbox)

# Add info label
info = InfoLabel("These settings control how recordings are handled.")
behavior_section.layout().addWidget(info)

# Add to parent layout
parent_layout.addWidget(behavior_section)
```

### Example 3: Horizontal Layout Section

```python
# Create a section with horizontal layout for button groups
actions_section = SettingsSection("Quick Actions", layout_type="horizontal")

# Add buttons horizontally
actions_section.layout().addWidget(test_button)
actions_section.layout().addWidget(refresh_button)
actions_section.layout().addWidget(reset_button)

# Add to parent layout
parent_layout.addWidget(actions_section)
```

### Example 4: Custom Font Size Info Label

```python
# Create info label with larger text
important_info = InfoLabel(
    "⚠️ This setting requires restart to take effect.",
    font_size=14
)
section.layout().addRow(important_info)
```

## Migration Guide

To migrate existing settings pages to use the new components:

### Step 1: Update imports

```python
from ui.components import SettingsSection, InfoLabel
```

### Step 2: Replace QGroupBox creation

**Old:**
```python
section = QGroupBox("Section Title")
layout = self.create_group_layout(section, "form")
```

**New:**
```python
section = SettingsSection("Section Title", layout_type="form")
```

### Step 3: Replace info labels

**Old:**
```python
info = QLabel("Info text")
info.setWordWrap(True)
info.setStyleSheet(f"color: {ColorTokens.TEXT_SECONDARY}; font-size: 12px; padding: 12px; background-color: transparent; border-radius: 6px;")
```

**New:**
```python
info = InfoLabel("Info text")
```

### Step 4: Access layout directly

**Old:**
```python
ui_layout = self.create_group_layout(ui_group, "form")
ui_layout.addRow("Setting:", widget)
```

**New:**
```python
ui_section = SettingsSection("UI Settings", layout_type="form")
ui_section.layout().addRow("Setting:", widget)
```

## Component Styling

Both components use centralized ColorTokens and LayoutTokens:

### SettingsSection Styling
- **Border:** 1px solid BORDER_SUBTLE
- **Border Radius:** RADIUS_MD
- **Background:** BG_PRIMARY
- **Title Color:** TEXT_PRIMARY
- **Title Font Size:** FONT_XL
- **Title Font Weight:** 700
- **Margins:** 20px top, SPACING_LG left padding

### InfoLabel Styling
- **Text Color:** TEXT_SECONDARY
- **Font Size:** 12px (customizable)
- **Padding:** 12px all sides
- **Background:** transparent
- **Border Radius:** 6px
- **Line Height:** 1.4

## Benefits Summary

### Code Quality
- ✅ Follows Single Responsibility Principle
- ✅ Adheres to DRY (Don't Repeat Yourself)
- ✅ Easier to maintain and update
- ✅ Reduces code duplication by ~40%

### Consistency
- ✅ Guaranteed visual consistency
- ✅ Centralized styling in one place
- ✅ Easier to apply global design changes

### Readability
- ✅ More semantic component names
- ✅ Less visual noise in code
- ✅ Clearer intent

### Maintainability
- ✅ Update styling in one place
- ✅ Less chance of styling inconsistencies
- ✅ Easier onboarding for new developers

## Next Steps

1. **Review** this documentation with the team
2. **Migrate** one tab as a pilot (recommend: General tab)
3. **Test** thoroughly to ensure visual parity
4. **Migrate** remaining tabs systematically
5. **Remove** old helper methods that are no longer needed
6. **Document** any custom variations if needed

