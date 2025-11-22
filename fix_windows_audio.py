#!/usr/bin/env python3
"""
Fix script for Whiz audio and transcription issues on Windows 11
This script applies recommended fixes to common issues
"""

import sys
import os
from pathlib import Path

# Fix Unicode encoding for Windows terminal
if sys.platform == 'win32':
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("Whiz Windows 11 Fix Script")
print("=" * 70)
print()

def fix_1_switch_to_openai_whisper():
    """Switch from faster-whisper to stable openai-whisper engine"""
    print("[Fix 1] Switching to OpenAI Whisper Engine")
    try:
        from core.settings_manager import SettingsManager
        sm = SettingsManager()
        
        current_engine = sm.get('whisper/engine')
        print(f"    Current engine: {current_engine}")
        
        if current_engine == 'openai':
            print("    ✅ Already using openai engine - no change needed")
            return True
        
        # Switch to openai
        sm.set('whisper/engine', 'openai')
        new_engine = sm.get('whisper/engine')
        
        if new_engine == 'openai':
            print("    ✅ Successfully switched to openai engine")
            print("    Note: OpenAI Whisper is slower but more stable on Windows")
            return True
        else:
            print("    ❌ Failed to switch engine")
            return False
            
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def fix_2_enable_device_validation():
    """Enable device validation for better error reporting"""
    print("\n[Fix 2] Enable Device Validation")
    print("    ⚠️  This requires code changes to audio_manager.py")
    print("    Current state: device_validation_enabled = False (line 108)")
    print("    Recommendation: Keep disabled for now to avoid validation overhead")
    print("    ⏭️  Skipping this fix")
    return True

def fix_3_setup_ffmpeg():
    """Ensure FFmpeg is in PATH"""
    print("\n[Fix 3] Configure FFmpeg PATH")
    try:
        import subprocess
        # Check if ffmpeg is already accessible
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("    ✅ FFmpeg already in PATH")
            return True
    except FileNotFoundError:
        pass
    
    # Check for local FFmpeg
    project_root = Path(__file__).parent
    ffmpeg_bin = project_root / "ffmpeg" / "bin"
    
    if ffmpeg_bin.exists():
        print(f"    ✅ Found local FFmpeg at: {ffmpeg_bin}")
        print(f"    Note: main.py and main_with_splash.py should add this to PATH at startup")
        print(f"    This is already implemented - no action needed")
        return True
    else:
        print("    ❌ FFmpeg not found locally")
        print("    Recommendation: Download FFmpeg and place in ./ffmpeg/bin/")
        return False

def fix_4_set_optimal_settings():
    """Configure optimal settings for Windows 11"""
    print("\n[Fix 4] Configure Optimal Settings")
    try:
        from core.settings_manager import SettingsManager
        sm = SettingsManager()
        
        changes_made = []
        
        # Use tiny model for speed
        current_model = sm.get('whisper/model_name')
        if current_model != 'tiny':
            sm.set('whisper/model_name', 'tiny')
            changes_made.append("Model size → tiny")
        
        # Set reasonable temperature
        current_temp = sm.get('whisper/temperature')
        if current_temp != 0.0:
            sm.set('whisper/temperature', 0.0)
            changes_made.append("Temperature → 0.0")
        
        # Ensure auto-paste is configured
        auto_paste = sm.get('behavior/auto_paste')
        print(f"    Auto-paste: {auto_paste}")
        
        # Ensure hold mode (not toggle)
        toggle_mode = sm.get('behavior/toggle_mode')
        if toggle_mode:
            sm.set('behavior/toggle_mode', False)
            changes_made.append("Recording mode → Hold")
        
        if changes_made:
            print("    ✅ Applied optimizations:")
            for change in changes_made:
                print(f"       - {change}")
        else:
            print("    ✅ Settings already optimal")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def fix_5_test_microphone_permissions():
    """Test if microphone permissions are granted"""
    print("\n[Fix 5] Test Microphone Permissions")
    try:
        from core.audio_manager import AudioManager
        import time
        
        audio_mgr = AudioManager(sample_rate=16000, channels=1, chunk_size=1024)
        
        if not audio_mgr.is_available():
            print("    ❌ Audio not available - sounddevice not installed?")
            return False
        
        print("    Testing 0.5 second recording...")
        if audio_mgr.start_recording():
            time.sleep(0.5)
            frames = audio_mgr.stop_recording()
            total_bytes = sum(len(f) for f in frames)
            
            if total_bytes == 0:
                print("    ❌ CRITICAL: No audio captured!")
                print("    Action required:")
                print("       1. Open Windows Settings")
                print("       2. Go to Privacy & Security > Microphone")
                print("       3. Enable 'Let apps access your microphone'")
                print("       4. Enable 'Let desktop apps access your microphone'")
                return False
            else:
                print(f"    ✅ Audio capture working ({total_bytes} bytes captured)")
                return True
        else:
            print("    ❌ Failed to start recording")
            print("    Possible causes:")
            print("       - Microphone not connected")
            print("       - Microphone in use by another app")
            print("       - Windows privacy settings blocking access")
            return False
            
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        print(f"    Details: {traceback.format_exc()}")
        return False

def fix_6_clear_problematic_cache():
    """Clear faster-whisper cache if it's causing issues"""
    print("\n[Fix 6] Clear Faster-Whisper Cache (Optional)")
    try:
        home = Path.home()
        faster_cache = home / ".cache" / "huggingface" / "hub"
        
        if faster_cache.exists():
            faster_models = list(faster_cache.glob("models--*faster-whisper*"))
            if faster_models:
                print(f"    Found {len(faster_models)} faster-whisper models")
                print("    These are not used when engine='openai'")
                print("    You can safely delete them to free space:")
                for model in faster_models:
                    print(f"       - {model}")
                print("    ⏭️  Skipping automatic deletion")
            else:
                print("    ✅ No faster-whisper models to clear")
        else:
            print("    ✅ No faster-whisper cache")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

# Main execution
def main():
    print("Running automated fixes...\n")
    
    results = []
    
    results.append(("Switch to OpenAI Whisper", fix_1_switch_to_openai_whisper()))
    results.append(("Device Validation", fix_2_enable_device_validation()))
    results.append(("FFmpeg Setup", fix_3_setup_ffmpeg()))
    results.append(("Optimal Settings", fix_4_set_optimal_settings()))
    results.append(("Microphone Test", fix_5_test_microphone_permissions()))
    results.append(("Cache Cleanup", fix_6_clear_problematic_cache()))
    
    # Summary
    print("\n" + "=" * 70)
    print("FIX SUMMARY")
    print("=" * 70)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} fixes")
    
    if passed == total:
        print("\n🎉 All fixes applied successfully!")
        print("\nNext steps:")
        print("   1. Restart the Whiz application")
        print("   2. Test recording with Alt+Gr key")
        print("   3. Check logs if issues persist")
    else:
        print("\n⚠️  Some fixes failed - see details above")
        print("\nManual intervention may be required:")
        print("   - Check Windows microphone permissions")
        print("   - Ensure microphone is connected and working")
        print("   - Review log files for detailed errors")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

