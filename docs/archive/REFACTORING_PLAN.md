# Preferences Dialog Refactoring Plan

## 🎯 Objective

Systematically migrate all preferences dialog tabs to use the new unified components (`SettingsSection` and `InfoLabel`) for improved maintainability and consistency.

## 📊 Current State Analysis

### Tabs to Refactor

| Tab | Sections | Info Labels | Lines to Refactor | Complexity | Priority |
|-----|----------|-------------|-------------------|------------|----------|
| General | 3 | 3 | ~70 | Low | 1 (Pilot) |
| Behavior | 3 | 3 | ~90 | Low | 2 |
| Audio | 3 | 2 | ~80 | Medium | 3 |
| Transcription | 2 | 2 | ~50 | Low | 4 |
| Advanced | 2 | 2 | ~60 | Low | 5 |
| **TOTAL** | **13** | **12** | **~350** | - | - |

### Estimated Impact

- **Code Reduction:** ~115 lines removed (33% reduction)
- **Maintenance Points:** 13 section styles + 12 info label styles → 2 component classes
- **Time per Tab:** 15-30 minutes
- **Total Time:** 1.5-2.5 hours for all tabs

---

## 🗓️ Phased Approach

### Phase 1: Pilot Refactor (General Tab)
**Goal:** Validate approach with simplest, most visible tab  
**Time:** 30 minutes  
**Risk:** Low

### Phase 2: Easy Tabs (Behavior, Transcription, Advanced)
**Goal:** Build momentum with similar complexity tabs  
**Time:** 1 hour  
**Risk:** Low

### Phase 3: Complex Tab (Audio)
**Goal:** Handle the most complex tab with device testing  
**Time:** 30 minutes  
**Risk:** Medium

### Phase 4: Cleanup
**Goal:** Remove obsolete helper methods, update documentation  
**Time:** 15 minutes  
**Risk:** Low

---

## 📋 Detailed Refactoring Steps

### PHASE 1: General Tab (Pilot)

#### Pre-Refactor Checklist
- [ ] Review [`examples/preferences_refactored_example.py`](../examples/preferences_refactored_example.py)
- [ ] Read [`docs/component_quick_reference.md`](component_quick_reference.md)
- [ ] Backup current `ui/preferences_dialog.py`
- [ ] Create a new git branch: `git checkout -b refactor/preferences-unified-components`

#### Step 1.1: Update Imports (2 min)
```python
# Add to imports at top of file
from ui.components import SettingsSection, InfoLabel
```

**File:** `ui/preferences_dialog.py` (line ~8)

#### Step 1.2: Refactor UI Settings Section (5 min)

**Current (lines 382-399):**
```python
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
```

**Replace with:**
```python
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
```

#### Step 1.3: Refactor Language Settings Section (5 min)

**Current (lines 401-422):**
Replace `QGroupBox` with `SettingsSection` and info `QLabel` with `InfoLabel` following the same pattern.

#### Step 1.4: Refactor Engine Settings Section (5 min)

**Current (lines 424-443):**
Replace `QGroupBox` with `SettingsSection` and info `QLabel` with `InfoLabel` following the same pattern.

#### Step 1.5: Test General Tab (10 min)

**Test Checklist:**
- [ ] Launch application
- [ ] Open Preferences → General tab
- [ ] Verify sections appear correctly
- [ ] Check section borders and spacing
- [ ] Verify text colors (primary and secondary)
- [ ] Test theme dropdown functionality
- [ ] Test language dropdown functionality
- [ ] Test engine dropdown functionality
- [ ] Compare visually with old version (screenshot comparison)
- [ ] Check console for any errors

**Acceptance Criteria:**
- ✅ Visual appearance matches original design
- ✅ All dropdowns work correctly
- ✅ Text is readable and properly colored
- ✅ No console errors
- ✅ Settings save/load correctly

#### Step 1.6: Commit Pilot Changes (2 min)

```bash
git add ui/preferences_dialog.py
git commit -m "refactor: migrate General tab to unified components

- Replace QGroupBox with SettingsSection
- Replace info QLabel with InfoLabel
- Reduce code by ~30% in General tab
- Maintain visual parity with original design"
```

**Decision Point:** If tests pass, proceed to Phase 2. If issues found, fix before continuing.

---

### PHASE 2: Easy Tabs (Behavior, Transcription, Advanced)

#### TASK 2.1: Refactor Behavior Tab (20 min)

**Sections to refactor:**
1. Recording Behavior (lines 454-487)
2. Visual Indicator (lines 489-512)
3. Hotkey Settings (lines 514-536)

**Pattern:**
```python
# For each section:
section = SettingsSection("Section Name", layout_type="form")
# ... add widgets ...
info = InfoLabel("Help text here")
section.layout().addRow(info)
layout.addWidget(section)
```

**Test Checklist:**
- [ ] All checkboxes work
- [ ] Dropdown selections save
- [ ] Visual indicator position combo works
- [ ] Info text displays correctly
- [ ] No visual regressions

**Commit:**
```bash
git add ui/preferences_dialog.py
git commit -m "refactor: migrate Behavior tab to unified components"
```

#### TASK 2.2: Refactor Transcription Tab (15 min)

**Sections to refactor:**
1. Whisper Model Settings (lines 627-651)
2. Performance Settings (lines 653-669)

**Note:** Performance Settings uses vertical layout (not form):
```python
perf_section = SettingsSection("Performance Settings", layout_type="vertical")
perf_info = InfoLabel("For best performance:\n...")
perf_section.layout().addWidget(perf_info)
```

**Test Checklist:**
- [ ] Model size dropdown works
- [ ] Speed mode checkbox works
- [ ] Performance info displays in vertical layout
- [ ] Settings save correctly

**Commit:**
```bash
git add ui/preferences_dialog.py
git commit -m "refactor: migrate Transcription tab to unified components"
```

#### TASK 2.3: Refactor Advanced Tab (15 min)

**Sections to refactor:**
1. Expert Settings (lines 680-716)
2. Temperature Settings (lines 718-748)
3. Advanced Settings (lines 750-764)

**Special considerations:**
- Temperature Settings group is conditionally shown/hidden
- Ensure visibility toggling still works after refactor

**Test Checklist:**
- [ ] Expert mode checkbox toggles temperature section
- [ ] Temperature slider works
- [ ] Reset to recommended button works
- [ ] Settings file info displays correctly

**Commit:**
```bash
git add ui/preferences_dialog.py
git commit -m "refactor: migrate Advanced tab to unified components"
```

---

### PHASE 3: Complex Tab (Audio)

#### TASK 3.1: Refactor Audio Tab (30 min)

**Sections to refactor:**
1. Audio Effects (lines 545-553)
2. Microphone Device (lines 555-587)
3. Tone Files (lines 589-617)

**Complexity factors:**
- Device combo has refresh/test buttons
- Tone files have browse/test buttons
- Warning label visibility (conditional)

**Special handling for Device Section:**
```python
device_section = SettingsSection("Microphone Device", layout_type="form")

# Device selection with buttons layout
device_selection_layout = self.create_horizontal_layout()
self.device_combo = self.create_styled_combobox()
# ... add buttons ...
device_section.layout().addRow("Device:", device_selection_layout)

# Warning (conditional display)
self.no_device_warning = InfoLabel(
    "⚠️ No microphone detected. Please connect a microphone and click Refresh.\n"
    "Make sure your microphone is plugged in and enabled in system settings.",
    font_size=12
)
# Override color for warning
self.no_device_warning.setStyleSheet(f"color: {ColorTokens.TEXT_PRIMARY}; font-size: 12px; padding: 12px; background-color: #ffebee; border: 1px solid #f44336; border-radius: 6px;")
self.no_device_warning.hide()
device_section.layout().addRow(self.no_device_warning)
```

**Test Checklist:**
- [ ] Audio effects checkbox works
- [ ] Device dropdown works
- [ ] Refresh button refreshes devices
- [ ] Test button opens test dialog
- [ ] Browse buttons open file dialog
- [ ] Test tone buttons play sounds
- [ ] No device warning shows/hides correctly
- [ ] Device selection saves correctly

**Commit:**
```bash
git add ui/preferences_dialog.py
git commit -m "refactor: migrate Audio tab to unified components

Handles complex layouts with button groups and conditional warnings"
```

---

### PHASE 4: Cleanup and Polish

#### TASK 4.1: Review and Test All Tabs (15 min)

**Full Integration Test:**
- [ ] Open each tab in sequence
- [ ] Verify visual consistency across all tabs
- [ ] Test one setting from each tab
- [ ] Verify settings persist after restart
- [ ] Check theme switching (light/dark/system)
- [ ] Test on different screen sizes
- [ ] Check for any console warnings/errors

#### TASK 4.2: Update Line Numbers in Documentation (5 min)

Since we've changed line numbers, update references in:
- [ ] `REFACTORING_PLAN.md` (this file)
- [ ] Code comments if any reference specific tabs

#### TASK 4.3: Final Commit and Merge (5 min)

```bash
# Final commit
git add .
git commit -m "docs: update documentation after refactor completion"

# Merge to main
git checkout main
git merge refactor/preferences-unified-components

# Optional: Tag the release
git tag -a v1.0-unified-components -m "Unified preferences components refactor complete"
```

---

## 🧪 Testing Strategy

### Visual Regression Testing

**Before Refactoring:**
1. Take screenshots of each tab (General, Behavior, Audio, Transcription, Advanced)
2. Document any specific styling details
3. Note section spacing, colors, fonts

**After Each Tab Refactoring:**
1. Take screenshot of refactored tab
2. Compare side-by-side with "before" screenshot
3. Check for:
   - Border consistency
   - Text color (primary vs secondary)
   - Spacing between elements
   - Section title alignment
   - Overall visual hierarchy

### Functional Testing

**For Each Tab:**
```python
# Test template
def test_tab_functionality():
    """Test refactored tab maintains all functionality."""
    
    # 1. Visual check
    assert section_visible()
    assert info_labels_visible()
    assert proper_spacing()
    
    # 2. Interaction check
    for widget in interactive_widgets:
        assert widget.isEnabled()
        assert widget responds to interaction
    
    # 3. Data persistence check
    change_setting()
    close_dialog()
    reopen_dialog()
    assert setting_persisted()
```

### Rollback Procedure

If issues are found during any phase:

1. **Identify the Issue:**
   - Visual regression?
   - Functional bug?
   - Performance problem?

2. **Determine Scope:**
   - Single tab affected? → Roll back that tab only
   - Multiple tabs affected? → Roll back to last stable commit
   - Component issue? → Fix component, re-test all tabs

3. **Rollback Command:**
   ```bash
   # Roll back to specific commit
   git revert <commit-hash>
   
   # Or reset to before refactor started
   git reset --hard origin/main
   ```

4. **Document the Issue:**
   - What went wrong?
   - Why did it happen?
   - How to prevent in future?

---

## 📈 Progress Tracking

### Refactoring Checklist

#### Phase 1: Pilot
- [ ] Update imports
- [ ] Refactor General tab (3 sections)
- [ ] Test General tab thoroughly
- [ ] Commit pilot changes
- [ ] **DECISION POINT:** Go/No-Go for Phase 2

#### Phase 2: Easy Tabs
- [ ] Refactor Behavior tab (3 sections)
- [ ] Test Behavior tab
- [ ] Commit Behavior changes
- [ ] Refactor Transcription tab (2 sections)
- [ ] Test Transcription tab
- [ ] Commit Transcription changes
- [ ] Refactor Advanced tab (3 sections)
- [ ] Test Advanced tab
- [ ] Commit Advanced changes

#### Phase 3: Complex Tab
- [ ] Refactor Audio tab (3 sections)
- [ ] Test Audio tab extensively
- [ ] Commit Audio changes

#### Phase 4: Cleanup
- [ ] Full integration test
- [ ] Update documentation
- [ ] Final commit
- [ ] Merge to main
- [ ] Tag release (optional)

---

## 📊 Metrics to Track

### Code Quality Metrics

| Metric | Before | Target After | Actual After |
|--------|--------|--------------|--------------|
| Total Lines | ~1475 | ~1360 | ___ |
| Section Creation Lines | ~195 | ~65 | ___ |
| Info Label Lines | ~72 | ~12 | ___ |
| Inline Stylesheets | 25 | 0 | ___ |
| Maintainability Index | Medium | High | ___ |

### Success Criteria

✅ **Must Have:**
- [ ] All tabs refactored successfully
- [ ] Zero visual regressions
- [ ] All functionality preserved
- [ ] No new bugs introduced
- [ ] Code reduction of at least 25%

✅ **Should Have:**
- [ ] Code reduction of 30%+
- [ ] Improved code readability
- [ ] Faster future modifications
- [ ] Better documentation

✅ **Nice to Have:**
- [ ] Performance improvements
- [ ] Easier testing
- [ ] Reusable patterns for other dialogs

---

## 🎯 Quick Reference: Refactoring Patterns

### Pattern 1: Basic Section with Info
```python
# Before
group = QGroupBox("Title")
layout = self.create_group_layout(group, "form")
layout.addRow("Label:", widget)
info = QLabel("Help text")
info.setWordWrap(True)
info.setStyleSheet(f"color: {ColorTokens.TEXT_SECONDARY}; font-size: 12px; padding: 12px; background-color: transparent; border-radius: 6px;")
layout.addRow(info)
parent.addWidget(group)

# After
section = SettingsSection("Title", layout_type="form")
section.layout().addRow("Label:", widget)
section.layout().addRow(InfoLabel("Help text"))
parent.addWidget(section)
```

### Pattern 2: Checkbox Group (Vertical Layout)
```python
# Before
group = QGroupBox("Title")
layout = self.create_group_layout(group, "form")
layout.addRow(checkbox1)
layout.addRow(checkbox2)
parent.addWidget(group)

# After
section = SettingsSection("Title", layout_type="form")
section.layout().addRow(checkbox1)
section.layout().addRow(checkbox2)
parent.addWidget(section)
```

### Pattern 3: Section with Horizontal Button Layout
```python
# Before
group = QGroupBox("Title")
layout = self.create_group_layout(group, "form")
button_layout = self.create_horizontal_layout()
button_layout.addWidget(btn1)
button_layout.addWidget(btn2)
layout.addRow("Label:", button_layout)
parent.addWidget(group)

# After
section = SettingsSection("Title", layout_type="form")
button_layout = self.create_horizontal_layout()
button_layout.addWidget(btn1)
button_layout.addWidget(btn2)
section.layout().addRow("Label:", button_layout)
parent.addWidget(section)
```

### Pattern 4: Custom Styled Info Label
```python
# Before (warning label)
info = QLabel("⚠️ Warning text")
info.setWordWrap(True)
info.setStyleSheet("color: #f44336; font-size: 12px; padding: 12px; background: #ffebee; border: 1px solid #f44336; border-radius: 6px;")

# After (override InfoLabel styling)
info = InfoLabel("⚠️ Warning text", font_size=12)
info.setStyleSheet("color: #f44336; padding: 12px; background: #ffebee; border: 1px solid #f44336; border-radius: 6px;")
```

---

## 🚨 Risk Mitigation

### Identified Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Visual regression | Medium | High | Screenshot comparison, thorough testing |
| Breaking functionality | Low | High | Incremental approach, test after each tab |
| Merge conflicts | Low | Medium | Frequent commits, clear communication |
| Performance impact | Very Low | Low | Components are lightweight wrappers |
| User disruption | Very Low | Medium | No user-facing changes if done correctly |

### Contingency Plans

**If visual regressions occur:**
- Adjust component styling in `base_components.py`
- All instances update automatically
- Re-test affected tabs

**If functionality breaks:**
- Roll back specific tab
- Debug issue
- Fix and re-test before continuing

**If major issues arise:**
- Pause refactoring
- Review approach
- Adjust plan as needed

---

## 📝 Notes and Observations

### Things to Watch For

1. **Conditional Visibility:** Some sections/info labels are shown/hidden conditionally
   - Temperature settings (Expert mode)
   - Device warning (No devices)
   - Ensure `.show()` and `.hide()` still work

2. **Custom Styling Overrides:** Some labels have custom colors (warnings, errors)
   - InfoLabel can be overridden after creation
   - Document any custom overrides

3. **Layout Nesting:** Some sections have complex nested layouts
   - Horizontal layouts within form layouts
   - Button groups within sections
   - Should work seamlessly with SettingsSection

4. **Signal Connections:** Ensure all signal connections remain intact
   - Device combo `currentIndexChanged`
   - Checkbox `stateChanged`
   - Button `clicked`

---

## ✅ Success Indicators

### Immediate Success (Post-Refactor)
- [ ] All 5 tabs refactored
- [ ] Zero visual differences from original
- [ ] All functionality works
- [ ] Code reduced by 30%+
- [ ] No linting errors

### Short-term Success (1-2 weeks)
- [ ] No bugs reported related to preferences
- [ ] Team feedback is positive
- [ ] Future preference changes are faster

### Long-term Success (1-3 months)
- [ ] Other dialogs adopt same pattern
- [ ] Reduced maintenance burden
- [ ] Consistent UI across application

---

## 📚 Resources

### Documentation
- [Component Quick Reference](component_quick_reference.md)
- [Refactored Examples](../examples/preferences_refactored_example.py)
- [Full Usage Guide](settings_component_demo.md)
- [Architecture Overview](component_architecture.md)

### Source Files
- `ui/components/base_components.py` - Component implementation
- `ui/preferences_dialog.py` - File to refactor

### Testing
- Manual testing checklist (above)
- Visual comparison screenshots
- Functional test scenarios

---

## 🎉 Completion Criteria

The refactoring is complete when:

✅ All 5 tabs use SettingsSection and InfoLabel  
✅ All tests pass (visual and functional)  
✅ Code is committed and merged  
✅ Documentation is updated  
✅ Team is notified  
✅ Success metrics are achieved  

**Estimated Completion Time:** 2-3 hours of focused work

**Recommended Schedule:**
- Day 1: Phase 1 (Pilot) - 30 min
- Day 2: Phase 2 (Easy tabs) - 1 hour
- Day 3: Phase 3 (Complex tab) - 30 min
- Day 3: Phase 4 (Cleanup) - 15 min

Or complete all in one session if preferred.

---

**Plan Version:** 1.0  
**Created:** 2025-11-22  
**Status:** Ready to Execute

**Next Step:** Begin Phase 1 - General Tab Refactoring

