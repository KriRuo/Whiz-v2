# DPI Testing Checklist

This document provides comprehensive testing procedures to validate multi-monitor DPI adaptation functionality in the Whiz application.

## Prerequisites

- Windows 10 version 1703 or later (for PerMonitorV2 support)
- Multiple monitors with different DPI scaling settings
- Whiz application built with the new DPI configuration

## Test Categories

### 1. Single Monitor DPI Scaling Tests

#### Test 1.1: Standard DPI Scaling (100%)
**Setup:**
- Set display scaling to 100% (96 DPI)
- Single monitor setup

**Expected Behavior:**
- ✓ Application opens at 80% of screen size, centered
- ✓ Text and icons appear crisp and properly sized
- ✓ UI elements are not blurry
- ✓ Window title bar and borders scale correctly

#### Test 1.2: 125% DPI Scaling
**Setup:**
- Set display scaling to 125% (120 DPI)
- Single monitor setup

**Expected Behavior:**
- ✓ Application opens at 80% of screen size, centered
- ✓ Text and icons are 25% larger but remain crisp
- ✓ UI elements maintain proper proportions
- ✓ No blurriness or pixelation

#### Test 1.3: 150% DPI Scaling
**Setup:**
- Set display scaling to 150% (144 DPI)
- Single monitor setup

**Expected Behavior:**
- ✓ Application opens at 80% of screen size, centered
- ✓ Text and icons are 50% larger but remain crisp
- ✓ UI elements maintain proper proportions
- ✓ All text remains readable

#### Test 1.4: 175% DPI Scaling
**Setup:**
- Set display scaling to 175% (168 DPI)
- Single monitor setup

**Expected Behavior:**
- ✓ Application opens at 80% of screen size, centered
- ✓ Text and icons are 75% larger but remain crisp
- ✓ UI elements maintain proper proportions
- ✓ No layout issues or overlapping elements

#### Test 1.5: 200% DPI Scaling
**Setup:**
- Set display scaling to 200% (192 DPI)
- Single monitor setup

**Expected Behavior:**
- ✓ Application opens at 80% of screen size, centered
- ✓ Text and icons are 100% larger but remain crisp
- ✓ UI elements maintain proper proportions
- ✓ All functionality remains accessible

### 2. Multi-Monitor DPI Tests

#### Test 2.1: Mixed DPI Monitors (100% + 150%)
**Setup:**
- Primary monitor: 100% scaling
- Secondary monitor: 150% scaling
- Launch application on primary monitor

**Expected Behavior:**
- ✓ Application opens at 80% of primary screen size, centered
- ✓ Text and icons appear crisp on primary monitor
- ✓ No blurriness

**Additional Test:**
- Move application to secondary monitor (150% scaling)
- ✓ Application automatically rescales to 150% DPI
- ✓ Text and icons become larger but remain crisp
- ✓ No blurriness or pixelation

#### Test 2.2: Mixed DPI Monitors (125% + 200%)
**Setup:**
- Primary monitor: 125% scaling
- Secondary monitor: 200% scaling
- Launch application on primary monitor

**Expected Behavior:**
- ✓ Application opens at 80% of primary screen size, centered
- ✓ Proper scaling on primary monitor

**Additional Test:**
- Move application to secondary monitor (200% scaling)
- ✓ Application automatically rescales to 200% DPI
- ✓ Dramatic size increase but maintains crispness
- ✓ All UI elements remain functional

#### Test 2.3: Three Monitor Setup
**Setup:**
- Monitor 1: 100% scaling
- Monitor 2: 150% scaling  
- Monitor 3: 200% scaling

**Expected Behavior:**
- ✓ Application can be moved between all monitors
- ✓ Automatic rescaling occurs on each monitor
- ✓ No off-screen positioning issues
- ✓ Consistent behavior across all monitors

### 3. Monitor Plug/Unplug Tests

#### Test 3.1: External Monitor Disconnection
**Setup:**
- Laptop + external monitor (different DPI scaling)
- Application running on external monitor
- Disconnect external monitor

**Expected Behavior:**
- ✓ Application automatically moves to laptop screen
- ✓ Rescales to laptop's DPI setting
- ✓ Remains functional and properly sized
- ✓ No off-screen positioning

#### Test 3.2: External Monitor Connection
**Setup:**
- Application running on laptop screen
- Connect external monitor with different DPI scaling
- Move application to external monitor

**Expected Behavior:**
- ✓ Application can be moved to external monitor
- ✓ Automatically rescales to external monitor's DPI
- ✓ Maintains proper proportions
- ✓ No positioning issues

#### Test 3.3: Application Launch After Monitor Changes
**Setup:**
- Change monitor configuration (plug/unplug)
- Launch application

**Expected Behavior:**
- ✓ Application opens on current primary monitor
- ✓ Uses 80% of available screen size, centered
- ✓ Proper DPI scaling for current monitor
- ✓ No off-screen positioning

### 4. Application-Specific Functionality Tests

#### Test 4.1: Recording Interface
**Setup:**
- Various DPI settings (100%, 150%, 200%)
- Test recording functionality

**Expected Behavior:**
- ✓ Recording buttons remain properly sized and clickable
- ✓ Waveform visualization scales correctly
- ✓ Visual indicators appear at correct size
- ✓ All recording controls remain accessible

#### Test 4.2: Settings Dialog
**Setup:**
- Open preferences/settings dialog
- Various DPI settings

**Expected Behavior:**
- ✓ Settings dialog opens at appropriate size
- ✓ All form elements remain properly sized
- ✓ Text remains readable at all DPI levels
- ✓ Dialog can be resized if needed

#### Test 4.3: System Tray Integration
**Setup:**
- Minimize to system tray
- Various DPI settings

**Expected Behavior:**
- ✓ System tray icon appears correctly
- ✓ Context menu scales properly
- ✓ Restore from tray works correctly
- ✓ Icon remains crisp at all DPI levels

### 5. PyInstaller Package Tests

#### Test 5.1: Packaged Executable
**Setup:**
- Build application using PyInstaller with new manifest
- Test on various DPI settings

**Expected Behavior:**
- ✓ Executable launches with proper DPI awareness
- ✓ Windows recognizes application as DPI-aware
- ✓ No blurriness in packaged version
- ✓ All functionality works identically to development version

#### Test 5.2: Manifest Validation
**Setup:**
- Check Windows application properties

**Expected Behavior:**
- ✓ Windows shows application as "Per-Monitor DPI Aware"
- ✓ Manifest is properly embedded
- ✓ No compatibility mode warnings

### 6. Edge Cases and Error Handling

#### Test 6.1: Very High DPI (300%+)
**Setup:**
- Set display scaling to 300% or higher
- Launch application

**Expected Behavior:**
- ✓ Application remains functional
- ✓ Text remains readable (may be very large)
- ✓ No crashes or layout issues
- ✓ All controls remain accessible

#### Test 6.2: Very Low Resolution Monitor
**Setup:**
- Test on low-resolution monitor (1024x768 or lower)
- Various DPI settings

**Expected Behavior:**
- ✓ Application opens at appropriate size for screen
- ✓ No off-screen positioning
- ✓ All UI elements remain accessible
- ✓ Minimum size constraints respected

#### Test 6.3: Rapid Monitor Changes
**Setup:**
- Quickly plug/unplug external monitor multiple times
- Move application between monitors rapidly

**Expected Behavior:**
- ✓ Application handles changes gracefully
- ✓ No crashes or freezes
- ✓ Proper rescaling occurs
- ✓ No memory leaks or performance issues

## Validation Checklist

For each test, verify:

- [ ] Application opens at 80% of screen size, centered
- [ ] Text and icons remain crisp (no blurriness)
- [ ] UI elements maintain proper proportions
- [ ] No off-screen positioning issues
- [ ] Automatic rescaling when moving between monitors
- [ ] All functionality remains accessible
- [ ] No crashes or freezes
- [ ] Performance remains acceptable
- [ ] System tray integration works correctly
- [ ] Settings dialog scales properly

## Reporting Issues

When reporting DPI-related issues, include:

1. **System Information:**
   - Windows version and build number
   - Monitor configuration (resolution, DPI scaling)
   - Graphics driver version

2. **Test Conditions:**
   - Specific DPI scaling settings
   - Monitor setup (single/multi)
   - Application launch method (development vs packaged)

3. **Expected vs Actual Behavior:**
   - What should happen
   - What actually happens
   - Screenshots if applicable

4. **Steps to Reproduce:**
   - Detailed steps to reproduce the issue
   - Whether issue is consistent or intermittent

## Success Criteria

The DPI adaptation implementation is successful when:

- ✓ All single-monitor DPI tests pass (100% - 200% scaling)
- ✓ Multi-monitor tests pass with mixed DPI settings
- ✓ Monitor plug/unplug scenarios work correctly
- ✓ Packaged executable behaves identically to development version
- ✓ No regression in existing functionality
- ✓ Performance remains acceptable across all scenarios

## Notes

- Some tests may require Windows 10 version 1703 or later for full PerMonitorV2 support
- Older Windows versions will fall back to basic DPI awareness
- Testing should be performed on both development and packaged versions
- Consider testing with different graphics drivers if issues arise
