#!/usr/bin/env python3
"""
Test script to verify audio level calculation functionality
"""

import numpy as np
import pyaudio
import time

def test_audio_level_calculation():
    """Test the audio level calculation logic"""
    
    # Audio parameters (same as in speech_controller)
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    
    try:
        # Open stream
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("Testing audio level calculation...")
        print("Speak into your microphone to see audio levels.")
        print("Press Ctrl+C to stop.")
        
        # Test for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                
                # Calculate audio level (same logic as in speech_controller)
                audio_data = np.frombuffer(data, dtype=np.int16)
                rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
                level = min(1.0, rms / 5000.0)  # Normalize to 0-1 range
                
                # Display level as a simple bar
                bar_length = int(level * 50)
                bar = "█" * bar_length + "░" * (50 - bar_length)
                print(f"\rAudio Level: [{bar}] {level:.3f}", end="", flush=True)
                
            except OSError as e:
                print(f"\nStream read warning: {e}")
                time.sleep(0.01)
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        audio.terminate()

if __name__ == "__main__":
    test_audio_level_calculation()
