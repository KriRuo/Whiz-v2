"""
Screenshot Helper for Preferences Dialog Refactoring

This script helps take and organize screenshots of preferences tabs
for before/after visual comparison during refactoring.

Usage:
    # Before refactoring
    python scripts/take_refactor_screenshots.py --phase before

    # After refactoring each tab
    python scripts/take_refactor_screenshots.py --phase after --tab general
    python scripts/take_refactor_screenshots.py --phase after --tab behavior
    # ... etc
"""

import sys
import os
from datetime import datetime
from pathlib import Path

def print_instructions(phase: str, tab: str = None):
    """Print instructions for taking screenshots."""
    
    print("\n" + "="*70)
    print("📸 SCREENSHOT HELPER - Preferences Dialog Refactoring")
    print("="*70 + "\n")
    
    # Create screenshots directory
    screenshots_dir = Path("refactoring_screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    if phase == "before":
        print("📋 PHASE: Taking 'BEFORE' screenshots")
        print("\nInstructions:")
        print("1. Launch the application")
        print("2. Open Preferences dialog (Settings → Preferences)")
        print("3. For EACH tab, take a screenshot and save as:")
        print()
        
        tabs = ["general", "behavior", "audio", "transcription", "advanced"]
        for tab in tabs:
            filename = f"before_{tab}.png"
            filepath = screenshots_dir / filename
            print(f"   • {tab.capitalize()} tab → {filepath}")
        
        print("\n4. Make sure to capture:")
        print("   - Section borders and spacing")
        print("   - Text colors (primary and secondary)")
        print("   - Section titles")
        print("   - Info label styling")
        print()
        print("💡 TIP: Use Windows Snipping Tool (Win+Shift+S)")
        print("         or macOS Screenshot (Cmd+Shift+4)")
        
    elif phase == "after":
        if not tab:
            print("❌ ERROR: --tab required for 'after' phase")
            print("\nUsage: python scripts/take_refactor_screenshots.py --phase after --tab <tab_name>")
            print("\nAvailable tabs: general, behavior, audio, transcription, advanced")
            return
        
        print(f"📋 PHASE: Taking 'AFTER' screenshot for {tab.upper()} tab")
        print("\nInstructions:")
        print("1. Launch the application with refactored code")
        print(f"2. Open Preferences → {tab.capitalize()} tab")
        print(f"3. Take a screenshot and save as:")
        print()
        
        filename = f"after_{tab}.png"
        filepath = screenshots_dir / filename
        print(f"   → {filepath}")
        print()
        print("4. Compare with 'before' screenshot:")
        before_file = screenshots_dir / f"before_{tab}.png"
        print(f"   → {before_file}")
        print()
        
        # Check if before screenshot exists
        if before_file.exists():
            print("✅ 'Before' screenshot exists - ready for comparison!")
        else:
            print("⚠️  WARNING: 'Before' screenshot not found!")
            print("   Take a 'before' screenshot first for accurate comparison.")
        
        print("\n5. Visual comparison checklist:")
        print("   [ ] Section borders match")
        print("   [ ] Spacing is identical")
        print("   [ ] Text colors match (primary vs secondary)")
        print("   [ ] Section title styling matches")
        print("   [ ] Info label styling matches")
        print("   [ ] Overall layout is identical")
        
    else:
        print("❌ ERROR: Invalid phase. Use 'before' or 'after'")
        return
    
    print("\n" + "="*70)
    print(f"📂 Screenshots directory: {screenshots_dir.absolute()}")
    print("="*70 + "\n")


def main():
    """Main entry point."""
    
    # Simple argument parsing
    args = sys.argv[1:]
    
    if not args or "--help" in args or "-h" in args:
        print("\n" + "="*70)
        print("📸 Screenshot Helper for Preferences Dialog Refactoring")
        print("="*70)
        print("\nUsage:")
        print("  # Before refactoring (take all 5 screenshots)")
        print("  python scripts/take_refactor_screenshots.py --phase before")
        print()
        print("  # After refactoring each tab")
        print("  python scripts/take_refactor_screenshots.py --phase after --tab general")
        print("  python scripts/take_refactor_screenshots.py --phase after --tab behavior")
        print("  python scripts/take_refactor_screenshots.py --phase after --tab audio")
        print("  python scripts/take_refactor_screenshots.py --phase after --tab transcription")
        print("  python scripts/take_refactor_screenshots.py --phase after --tab advanced")
        print()
        print("Options:")
        print("  --phase <before|after>   Refactoring phase")
        print("  --tab <tab_name>         Tab name (required for 'after' phase)")
        print("  --help, -h               Show this help message")
        print()
        return
    
    # Parse arguments
    phase = None
    tab = None
    
    for i, arg in enumerate(args):
        if arg == "--phase" and i + 1 < len(args):
            phase = args[i + 1].lower()
        elif arg == "--tab" and i + 1 < len(args):
            tab = args[i + 1].lower()
    
    if not phase:
        print("❌ ERROR: --phase is required")
        print("\nUse --help for usage instructions")
        return
    
    # Print instructions
    print_instructions(phase, tab)


if __name__ == "__main__":
    main()

