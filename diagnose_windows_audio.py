#!/usr/bin/env python3
"""
Diagnostic script for Whiz audio and transcription issues on Windows 11
Run this to identify the root cause of recording/transcription failures
"""

import sys
import os
from pathlib import Path

# Fix Unicode encoding for Windows terminal
if sys.platform == 'win32':
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("Whiz Windows 11 Diagnostic Tool")
print("=" * 70)
print()

# 1. Check Python environment
print("[1] Python Environment")
print(f"    Python version: {sys.version}")
print(f"    Platform: {sys.platform}")
print()

# 2. Check sounddevice availability
print("[2] Audio Library (sounddevice)")
try:
    import sounddevice as sd
    print("    ✅ sounddevice installed")
    print(f"    Version: {sd.__version__}")
except ImportError as e:
    print(f"    ❌ sounddevice NOT installed: {e}")
    print("    Fix: pip install sounddevice")
print()

# 3. Check audio devices
print("[3] Audio Devices")
try:
    import sounddevice as sd
    devices = sd.query_devices()
    input_devices = [d for i, d in enumerate(devices) if d.get('max_input_channels', 0) > 0]
    
    if input_devices:
        print(f"    ✅ Found {len(input_devices)} input device(s)")
        for i, device in enumerate(input_devices):
            default_marker = " (DEFAULT)" if device.get('default_samplerate') else ""
            print(f"       {i}: {device['name']}{default_marker}")
            print(f"           Channels: {device.get('max_input_channels')}, "
                  f"Sample Rate: {device.get('default_samplerate')} Hz")
    else:
        print("    ❌ No input devices found!")
        print("    Check: Microphone connected? Privacy settings?")
except Exception as e:
    print(f"    ❌ Error querying devices: {e}")
print()

# 4. Check Whisper engines
print("[4] Whisper Engines")
try:
    import whisper
    print(f"    ✅ openai-whisper installed (version: {whisper.__version__ if hasattr(whisper, '__version__') else 'unknown'})")
except ImportError:
    print("    ❌ openai-whisper NOT installed")
    print("    Fix: pip install openai-whisper")

try:
    import faster_whisper
    print(f"    ✅ faster-whisper installed (version: {faster_whisper.__version__ if hasattr(faster_whisper, '__version__') else 'unknown'})")
    print("    ⚠️  WARNING: faster-whisper has known PyQt5 compatibility issues!")
except ImportError:
    print("    ❌ faster-whisper NOT installed")
print()

# 5. Check FFmpeg
print("[5] FFmpeg")
import subprocess
try:
    # Check if ffmpeg is in PATH
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        version_line = result.stdout.split('\n')[0]
        print(f"    ✅ FFmpeg found: {version_line}")
    else:
        print("    ❌ FFmpeg not working properly")
except FileNotFoundError:
    print("    ❌ FFmpeg NOT in PATH")
    # Check local installation
    project_root = Path(__file__).parent
    ffmpeg_local = project_root / "ffmpeg" / "bin" / "ffmpeg.exe"
    if ffmpeg_local.exists():
        print(f"    ✅ Found local FFmpeg at: {ffmpeg_local}")
        print(f"    ⚠️  But it's not in PATH - may cause issues")
    else:
        print("    ❌ FFmpeg not found in project directory either")
except Exception as e:
    print(f"    ❌ Error checking FFmpeg: {e}")
print()

# 6. Check settings
print("[6] Current Settings")
try:
    from core.settings_manager import SettingsManager
    sm = SettingsManager()
    
    engine = sm.get('whisper/engine')
    model = sm.get('whisper/model_name')
    auto_paste = sm.get('behavior/auto_paste')
    hotkey = sm.get('behavior/hotkey')
    device = sm.get('audio/input_device_name')
    
    print(f"    Whisper Engine: {engine}")
    if engine == 'faster':
        print("    ⚠️  WARNING: You're using faster-whisper which crashes on Windows!")
        print("    Recommendation: Change to 'openai'")
    else:
        print("    ✅ Using stable openai engine")
    
    print(f"    Model Size: {model}")
    print(f"    Auto-paste: {auto_paste}")
    print(f"    Hotkey: {hotkey}")
    print(f"    Audio Device: {device}")
    
except Exception as e:
    print(f"    ❌ Error reading settings: {e}")
print()

# 7. Check model files
print("[7] Model Files")
home = Path.home()

# Check OpenAI Whisper models
openai_cache = home / ".cache" / "whisper"
if openai_cache.exists():
    models = list(openai_cache.glob("*.pt"))
    if models:
        print(f"    ✅ OpenAI Whisper models found: {len(models)}")
        for model in models:
            size_mb = model.stat().st_size / (1024 * 1024)
            print(f"       - {model.name} ({size_mb:.1f} MB)")
    else:
        print("    ⚠️  OpenAI Whisper cache exists but no models found")
else:
    print("    ❌ No OpenAI Whisper models cached")

# Check faster-whisper models
faster_cache = home / ".cache" / "huggingface" / "hub"
if faster_cache.exists():
    models = list(faster_cache.glob("models--*faster-whisper*"))
    if models:
        print(f"    ✅ faster-whisper models found: {len(models)}")
        for model in models:
            print(f"       - {model.name}")
    else:
        print("    ⚠️  Hugging Face cache exists but no faster-whisper models")
else:
    print("    ❌ No faster-whisper models cached")
print()

# 8. Test audio recording
print("[8] Audio Recording Test")
try:
    from core.audio_manager import AudioManager
    
    audio_mgr = AudioManager(sample_rate=16000, channels=1, chunk_size=1024)
    
    if not audio_mgr.is_available():
        print("    ❌ AudioManager reports audio NOT available")
    else:
        print("    ✅ AudioManager initialized")
        
        # Check device validation status
        status = audio_mgr.get_status()
        print(f"    Device validation: {'ENABLED' if status['validation_enabled'] else 'DISABLED'}")
        if not status['validation_enabled']:
            print("    ⚠️  Device validation is DISABLED - potential issue!")
        
        print(f"    Selected device: {status['selected_device']}")
        print(f"    Available devices: {status['device_count']}")
        
        # Try a quick recording test
        print("    Attempting 1-second test recording...")
        import time
        if audio_mgr.start_recording():
            print("    ✅ Recording started")
            time.sleep(1)
            frames = audio_mgr.stop_recording()
            total_bytes = sum(len(f) for f in frames)
            print(f"    ✅ Recording stopped: {len(frames)} frames, {total_bytes} bytes")
            
            if total_bytes == 0:
                print("    ❌ CRITICAL: No audio data captured!")
                print("    Check: Microphone permissions in Windows Settings")
            elif total_bytes < 1000:
                print("    ⚠️  WARNING: Very little audio captured")
            else:
                print("    ✅ Audio capture appears to be working")
        else:
            print("    ❌ Failed to start recording")
            
except Exception as e:
    print(f"    ❌ Error testing audio: {e}")
    import traceback
    print(f"    Traceback:\n{traceback.format_exc()}")
print()

# 9. Summary and Recommendations
print("=" * 70)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 70)

print("\n🔍 Common Issues on Windows 11:")
print("   1. Microphone privacy settings blocking access")
print("   2. faster-whisper engine causing PyQt5 crashes")
print("   3. Device validation disabled (masking real issues)")
print("   4. Audio format conversion issues (float32 → int16)")

print("\n💡 Recommended Fixes:")
print("   1. Ensure microphone permissions enabled:")
print("      Settings > Privacy > Microphone > Allow apps to access")
print("   2. Switch to openai-whisper engine:")
print("      python -c \"from core.settings_manager import SettingsManager; sm = SettingsManager(); sm.set('whisper/engine', 'openai')\"")
print("   3. Enable device validation for better error reporting")
print("   4. Check Windows audio drivers are up to date")

print("\n📝 Log Files:")
print(f"   Main log: {os.environ.get('LOCALAPPDATA', '')}\\Temp\\whiz\\logs\\whiz.log")
print(f"   Error log: {os.environ.get('LOCALAPPDATA', '')}\\Temp\\whiz\\logs\\whiz_errors.log")

print("\n" + "=" * 70)

