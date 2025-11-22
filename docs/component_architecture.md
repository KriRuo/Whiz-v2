# Settings Component Architecture

## Component Hierarchy

```
ui/components/
│
├── base_components.py
│   ├── BaseTab (existing)
│   ├── BaseDialog (existing)
│   ├── StatusDisplay (existing)
│   ├── ActionButton (existing)
│   ├── InfoPanel (existing)
│   ├── ButtonGroup (existing)
│   ├── SettingsSection (NEW) ⭐
│   └── InfoLabel (NEW) ⭐
│
└── __init__.py (exports all components)
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    PreferencesDialog                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Tab Widget                         │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │           General Tab (QWidget)               │  │  │
│  │  │  ┌────────────────────────────────────────┐  │  │  │
│  │  │  │   SettingsSection                      │  │  │  │
│  │  │  │   ("User Interface")                   │  │  │  │
│  │  │  │  ┌──────────────────────────────────┐ │  │  │  │
│  │  │  │  │ Form Layout                      │ │  │  │  │
│  │  │  │  │  - QComboBox (Theme)             │ │  │  │  │
│  │  │  │  │  - InfoLabel (Help text)         │ │  │  │  │
│  │  │  │  └──────────────────────────────────┘ │  │  │  │
│  │  │  └────────────────────────────────────────┘  │  │  │
│  │  │  ┌────────────────────────────────────────┐  │  │  │
│  │  │  │   SettingsSection                      │  │  │  │
│  │  │  │   ("Language Settings")                │  │  │  │
│  │  │  │  ┌──────────────────────────────────┐ │  │  │  │
│  │  │  │  │ Form Layout                      │ │  │  │  │
│  │  │  │  │  - QComboBox (Language)          │ │  │  │  │
│  │  │  │  │  - InfoLabel (Help text)         │ │  │  │  │
│  │  │  │  └──────────────────────────────────┘ │  │  │  │
│  │  │  └────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Flow

```
Developer writes:
    section = SettingsSection("Title", layout_type="form")
         ↓
    Inherits from QGroupBox
         ↓
    init_layout() creates appropriate layout (QFormLayout)
         ↓
    apply_styling() applies consistent styles using ColorTokens
         ↓
    Ready to use with section.layout()

Developer writes:
    info = InfoLabel("Help text")
         ↓
    Inherits from QLabel
         ↓
    setWordWrap(True) automatically
         ↓
    apply_styling() applies consistent styles using ColorTokens
         ↓
    Ready to display
```

## Data Flow

```
ColorTokens & LayoutTokens (layout_system.py)
        ↓
    SettingsSection.apply_styling()
    InfoLabel.apply_styling()
        ↓
    Consistent visual appearance
        ↓
    All sections look identical
```

## Inheritance Tree

```
QGroupBox (Qt)
    ↓
SettingsSection (Custom)
    ├── Has: QFormLayout | QVBoxLayout | QHBoxLayout
    └── Uses: ColorTokens, LayoutTokens

QLabel (Qt)
    ↓
InfoLabel (Custom)
    └── Uses: ColorTokens
```

## Component Interaction

```
┌──────────────────────┐
│  preferences_dialog  │
│       .py            │
└──────────┬───────────┘
           │ imports
           ↓
┌──────────────────────┐
│  ui/components/      │
│    __init__.py       │
└──────────┬───────────┘
           │ imports
           ↓
┌──────────────────────┐
│  base_components.py  │
│  - SettingsSection   │
│  - InfoLabel         │
└──────────┬───────────┘
           │ uses
           ↓
┌──────────────────────┐
│  layout_system.py    │
│  - ColorTokens       │
│  - LayoutTokens      │
└──────────────────────┘
```

## Styling Flow

```
User Changes Theme
        ↓
ColorTokens update (layout_system.py)
        ↓
Components use ColorTokens
        ↓
All SettingsSection instances update automatically
All InfoLabel instances update automatically
        ↓
Consistent appearance maintained
```

## Component Lifecycle

### SettingsSection

```
1. Instantiation
   section = SettingsSection("Title", layout_type="form")
   
2. Initialization
   - Call super().__init__(title)
   - Create QGroupBox with title
   
3. Layout Creation
   - init_layout(layout_type)
   - Create QFormLayout | QVBoxLayout | QHBoxLayout
   
4. Styling Application
   - apply_styling()
   - Apply ColorTokens and LayoutTokens
   
5. Usage
   - section.layout().addRow(...)
   - Add widgets to the section
   
6. Display
   - parent_layout.addWidget(section)
   - Render with consistent styling
```

### InfoLabel

```
1. Instantiation
   info = InfoLabel("Text", font_size=12)
   
2. Initialization
   - Call super().__init__(text)
   - Create QLabel with text
   
3. Word Wrap
   - setWordWrap(True)
   - Enable automatic text wrapping
   
4. Styling Application
   - apply_styling(font_size)
   - Apply ColorTokens with custom font size
   
5. Display
   - layout.addRow(info)
   - Render with consistent styling
```

## Comparison: Old vs New Architecture

### OLD Architecture (Scattered)

```
preferences_dialog.py
    ├── create_general_tab()
    │   ├── QGroupBox("Title") + inline styling
    │   ├── QLabel() + setWordWrap() + inline stylesheet ❌
    │   └── QLabel() + setWordWrap() + inline stylesheet ❌
    │
    ├── create_behavior_tab()
    │   ├── QGroupBox("Title") + inline styling
    │   ├── QLabel() + setWordWrap() + inline stylesheet ❌
    │   └── QLabel() + setWordWrap() + inline stylesheet ❌
    │
    └── create_transcription_tab()
        ├── QGroupBox("Title") + inline styling
        └── QLabel() + setWordWrap() + inline stylesheet ❌

Problems:
- Styling scattered across 13+ locations
- Hard to maintain consistency
- Repetitive code
- High risk of typos/inconsistencies
```

### NEW Architecture (Centralized)

```
base_components.py
    ├── SettingsSection
    │   └── apply_styling() ✅ (ONE place)
    │
    └── InfoLabel
        └── apply_styling() ✅ (ONE place)

preferences_dialog.py
    ├── create_general_tab()
    │   ├── SettingsSection("Title") ✅
    │   └── InfoLabel("Text") ✅
    │
    ├── create_behavior_tab()
    │   ├── SettingsSection("Title") ✅
    │   └── InfoLabel("Text") ✅
    │
    └── create_transcription_tab()
        ├── SettingsSection("Title") ✅
        └── InfoLabel("Text") ✅

Benefits:
- Styling centralized in 2 components
- Guaranteed consistency
- No repetitive code
- Zero risk of inconsistencies
```

## Token Integration

### ColorTokens Used

```python
SettingsSection:
    - TEXT_PRIMARY (title)
    - BORDER_SUBTLE (border)
    - BG_PRIMARY (background)

InfoLabel:
    - TEXT_SECONDARY (text)
```

### LayoutTokens Used

```python
SettingsSection:
    - RADIUS_MD (border radius)
    - SPACING_LG (title left padding)
    - SPACING_MD (layout spacing, title padding)
    - FONT_XL (title font size)

InfoLabel:
    - None (uses fixed values)
```

## Extension Points

### Custom SettingsSection

```python
class CustomSettingsSection(SettingsSection):
    def apply_styling(self):
        # Call parent styling first
        super().apply_styling()
        
        # Add custom styling
        self.setStyleSheet(self.styleSheet() + """
            QGroupBox {
                /* Custom additions */
            }
        """)
```

### Custom InfoLabel

```python
class WarningLabel(InfoLabel):
    def __init__(self, text: str):
        super().__init__(f"⚠️ {text}", font_size=14)
    
    def apply_styling(self, font_size: int):
        super().apply_styling(font_size)
        # Could add warning-specific styling here
```

## Performance Considerations

### Memory
- **Minimal overhead**: Components are lightweight wrappers
- **No extra objects**: Direct Qt widget inheritance
- **Efficient**: Styling applied once at creation

### Rendering
- **Native Qt rendering**: No custom painting
- **Hardware accelerated**: Uses Qt's standard rendering
- **Fast**: No performance difference vs manual creation

### Maintenance
- **Faster updates**: Change styling in one place
- **Fewer bugs**: Consistent behavior reduces issues
- **Better testing**: Centralized code easier to test

## Future Enhancements

### Possible Additions

1. **SettingsGroup** - Container for multiple SettingsSections
2. **SettingsRow** - Pre-built label + widget row
3. **SettingsCheckbox** - Styled checkbox with consistent appearance
4. **SettingsComboBox** - Already exists (create_styled_combobox)
5. **SettingsSpinBox** - Styled spinbox with consistent appearance

### Integration Opportunities

1. Use in other dialogs beyond preferences
2. Create settings page builder/DSL
3. Add animation/transitions for section expand/collapse
4. Add validation feedback to sections
5. Add section state persistence (expanded/collapsed)

## Summary

The new component architecture provides:

✅ **Centralized** styling and behavior  
✅ **Consistent** visual appearance  
✅ **Maintainable** single source of truth  
✅ **Extensible** for future needs  
✅ **Performant** with minimal overhead  
✅ **Compatible** with existing code  

---

**Architecture Version:** 1.0  
**Last Updated:** 2025-11-22  
**Status:** Implemented and Ready

