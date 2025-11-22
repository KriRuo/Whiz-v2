# Quick Start: Preferences Dialog Refactoring

**Goal:** Migrate preferences tabs to use unified components (`SettingsSection` and `InfoLabel`)  
**Time:** 2-3 hours total  
**Difficulty:** Easy

---

## 🚀 Get Started in 5 Minutes

### 1. Prepare (2 minutes)

```bash
# Create feature branch
git checkout -b refactor/preferences-unified-components

# Backup current file (optional)
cp ui/preferences_dialog.py ui/preferences_dialog.py.backup
```

### 2. Quick Reference (1 minute)

Open these files in separate tabs:
- [`docs/component_quick_reference.md`](docs/component_quick_reference.md) - Code patterns
- [`REFACTORING_PROGRESS.md`](REFACTORING_PROGRESS.md) - Track progress

### 3. Add Imports (1 minute)

**File:** `ui/preferences_dialog.py` (around line 8)

```python
from ui.components import SettingsSection, InfoLabel
```

### 4. Start Refactoring (1 minute to first change)

**Find this pattern:**
```python
ui_group = QGroupBox("User Interface")
ui_layout = self.create_group_layout(ui_group, "form")
# ... widgets ...
info = QLabel("Help text")
info.setWordWrap(True)
info.setStyleSheet(f"color: {ColorTokens.TEXT_SECONDARY}; font-size: 12px; padding: 12px; background-color: transparent; border-radius: 6px;")
ui_layout.addRow(info)
layout.addWidget(ui_group)
```

**Replace with:**
```python
ui_section = SettingsSection("User Interface", layout_type="form")
# ... widgets ...
ui_section.layout().addRow(InfoLabel("Help text"))
layout.addWidget(ui_section)
```

**Done!** You just refactored your first section. 🎉

---

## 📋 The Complete Process

### Order of Refactoring

```
1. General Tab (3 sections) ← START HERE (easiest)
   ├─ UI Settings
   ├─ Language Settings
   └─ Engine Settings

2. Behavior Tab (3 sections)
   ├─ Recording Behavior
   ├─ Visual Indicator
   └─ Hotkey Settings

3. Transcription Tab (2 sections)
   ├─ Whisper Model Settings
   └─ Performance Settings

4. Advanced Tab (3 sections)
   ├─ Expert Settings
   ├─ Temperature Settings
   └─ Advanced Settings

5. Audio Tab (3 sections) ← DO LAST (most complex)
   ├─ Audio Effects
   ├─ Microphone Device
   └─ Tone Files
```

### For Each Tab:

1. **Refactor** sections (5-10 min per section)
2. **Test** functionality (5 min)
3. **Commit** changes (1 min)
4. **Move to next** tab

---

## 🎯 The Two Patterns You Need

### Pattern 1: Section with Form Layout (90% of cases)

```python
# BEFORE
group = QGroupBox("Section Title")
layout = self.create_group_layout(group, "form")
layout.addRow("Setting:", widget)
parent.addWidget(group)

# AFTER
section = SettingsSection("Section Title", layout_type="form")
section.layout().addRow("Setting:", widget)
parent.addWidget(section)
```

### Pattern 2: Info Label (100% of info labels)

```python
# BEFORE
info = QLabel("Help text here")
info.setWordWrap(True)
info.setStyleSheet(f"color: {ColorTokens.TEXT_SECONDARY}; font-size: 12px; padding: 12px; background-color: transparent; border-radius: 6px;")
layout.addRow(info)

# AFTER
layout.addRow(InfoLabel("Help text here"))
```

**That's it!** These two patterns cover ~95% of the refactoring.

---

## ✅ Testing Checklist (Per Tab)

After refactoring each tab, test:

- [ ] Tab opens without errors
- [ ] Sections have borders and proper spacing
- [ ] Text is white (primary) or gray (secondary/info)
- [ ] All dropdowns work
- [ ] All checkboxes work
- [ ] Settings save when you close and reopen
- [ ] Looks identical to before

**If any test fails:** Review the change, compare with examples, fix and re-test.

---

## 🔥 Pro Tips

### Tip 1: Use Find & Replace Smartly
- Find: `QGroupBox("`
- Review each occurrence
- Replace with `SettingsSection(` and add `, layout_type="form")`

### Tip 2: Track Your Progress
Update [`REFACTORING_PROGRESS.md`](REFACTORING_PROGRESS.md) as you go. It's satisfying! ✅

### Tip 3: Commit Often
Commit after each tab. Makes rollback easy if needed.

```bash
git commit -m "refactor: migrate General tab to unified components"
git commit -m "refactor: migrate Behavior tab to unified components"
# etc.
```

### Tip 4: Take Breaks
- After each tab, take a 5-minute break
- Prevents fatigue and mistakes

### Tip 5: Visual Comparison
Take screenshots before and after to compare:

```bash
# Before refactoring
python scripts/take_refactor_screenshots.py --phase before

# After each tab
python scripts/take_refactor_screenshots.py --phase after --tab general
```

---

## 🐛 Common Issues & Fixes

### Issue 1: "Name 'SettingsSection' is not defined"
**Cause:** Forgot to add import  
**Fix:** Add `from ui.components import SettingsSection, InfoLabel` at top

### Issue 2: Section doesn't show up
**Cause:** Forgot `parent.addWidget(section)`  
**Fix:** Make sure to add section to parent layout

### Issue 3: Layout methods don't work
**Cause:** Trying to access layout without `.layout()`  
**Fix:** Use `section.layout().addRow(...)` not `section.addRow(...)`

### Issue 4: Text color is wrong
**Cause:** Info label using wrong component  
**Fix:** Use `InfoLabel` for secondary text, regular `QLabel` for primary

### Issue 5: Visual differences after refactor
**Cause:** Different component styling  
**Fix:** Check `base_components.py` styling, adjust if needed

---

## 📊 Progress Tracker

| Tab | Sections | Status | Time |
|-----|----------|--------|------|
| General | 3 | ⬜ | ___ min |
| Behavior | 3 | ⬜ | ___ min |
| Transcription | 2 | ⬜ | ___ min |
| Advanced | 3 | ⬜ | ___ min |
| Audio | 3 | ⬜ | ___ min |
| **TOTAL** | **14** | ⬜ | ___ min |

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete

---

## 🎯 Success = Simple

You'll know you're successful when:

1. **Code is shorter** - Each section is ~5 fewer lines
2. **No inline styles** - No `setStyleSheet` for info labels
3. **Looks identical** - Visual comparison shows no difference
4. **Works perfectly** - All settings save and load correctly

---

## 🚦 Quick Decision Tree

**Q: Is this a section with a title border?**  
→ YES: Use `SettingsSection`  
→ NO: Keep as is

**Q: Is this gray help/info text?**  
→ YES: Use `InfoLabel`  
→ NO: Keep as `QLabel`

**Q: Does the section need a form layout (label: widget pairs)?**  
→ YES: `SettingsSection("Title", layout_type="form")`  
→ NO: Use `layout_type="vertical"` or `"horizontal"`

---

## 📞 Need Help?

1. **Code examples:** [`examples/preferences_refactored_example.py`](examples/preferences_refactored_example.py)
2. **Quick patterns:** [`docs/component_quick_reference.md`](docs/component_quick_reference.md)
3. **Full plan:** [`docs/REFACTORING_PLAN.md`](docs/REFACTORING_PLAN.md)
4. **Architecture:** [`docs/component_architecture.md`](docs/component_architecture.md)

---

## 🎉 You're Ready!

**Your first step:**
1. Open `ui/preferences_dialog.py`
2. Add imports
3. Find the General tab's `create_general_tab` method
4. Refactor the first section
5. Test it
6. Keep going!

**You got this!** 💪

The components are already implemented and tested. You're just replacing old patterns with new ones. It's straightforward, and you'll see immediate improvement in code quality.

---

**Quick Start Version:** 1.0  
**Last Updated:** 2025-11-22

**Next:** Open [`REFACTORING_PROGRESS.md`](REFACTORING_PROGRESS.md) to start tracking!

