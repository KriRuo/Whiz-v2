import numpy as np
import wave
import struct
import os

def create_modern_sound_effect(filename, frequency=400, duration=0.3, fade_duration=0.05, volume=0.3):
    """
    Create a modern, lower-pitched sound effect with smooth fade in/out
    
    Args:
        filename: Output WAV file name
        frequency: Base frequency in Hz (lower = deeper tone)
        duration: Sound duration in seconds
        fade_duration: Fade in/out duration in seconds
        volume: Volume level (0.0 to 1.0)
    """
    # Audio parameters
    sample_rate = 44100
    samples = int(sample_rate * duration)
    
    # Create time array
    t = np.linspace(0, duration, samples, False)
    
    # Generate base tone with harmonics for richness
    fundamental = np.sin(2 * np.pi * frequency * t)
    harmonic1 = 0.5 * np.sin(2 * np.pi * frequency * 2 * t)  # Second harmonic
    harmonic2 = 0.25 * np.sin(2 * np.pi * frequency * 3 * t)  # Third harmonic
    
    # Combine tones
    audio = fundamental + harmonic1 + harmonic2
    
    # Apply fade in/out
    audio = apply_fade(audio, fade_duration, sample_rate)
    
    # Normalize and apply volume
    audio = audio / np.max(np.abs(audio)) * volume
    
    # Convert to 16-bit integers
    audio_int = (audio * 32767).astype(np.int16)
    
    # Save sound
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int.tobytes())
    
    print(f"Created {filename} - {frequency}Hz, {duration}s, volume {volume}")

def apply_fade(audio, fade_duration, sample_rate):
    """Apply fade in/out to audio"""
    fade_samples = int(fade_duration * sample_rate)
    
    if len(audio) > 2 * fade_samples:
        # Fade in
        fade_in = np.linspace(0, 1, fade_samples)
        audio[:fade_samples] *= fade_in
        
        # Fade out
        fade_out = np.linspace(1, 0, fade_samples)
        audio[-fade_samples:] *= fade_out
    
    return audio

def normalize_audio(audio):
    """Normalize audio to prevent clipping"""
    return audio / np.max(np.abs(audio)) * 0.8

def save_wav_file(filename, audio, sample_rate):
    """Save audio as WAV file"""
    audio_int = (audio * 32767).astype(np.int16)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int.tobytes())

def create_sweep_sound(filename, start_freq, end_freq, duration, fade_duration, description):
    """Create a frequency sweep sound"""
    sample_rate = 44100
    samples = int(sample_rate * duration)
    
    t = np.linspace(0, duration, samples, False)
    
    # Create frequency sweep
    freq_sweep = np.linspace(start_freq, end_freq, samples)
    
    # Generate sweep sound
    audio = np.sin(2 * np.pi * freq_sweep * t)
    
    # Apply fade in/out
    audio = apply_fade(audio, fade_duration, sample_rate)
    
    # Normalize and save
    audio = normalize_audio(audio)
    save_wav_file(filename, audio, sample_rate)
    print(f"- {description}")

def create_bell_sound(filename, start_freq, end_freq, duration, fade_duration, description):
    """Create a bell-like sound with rich harmonics"""
    sample_rate = 44100
    samples = int(sample_rate * duration)
    
    t = np.linspace(0, duration, samples, False)
    
    # Create frequency sweep
    freq_sweep = np.linspace(start_freq, end_freq, samples)
    
    # Generate bell-like sound with multiple harmonics
    fundamental = np.sin(2 * np.pi * freq_sweep * t)
    harmonic1 = 0.3 * np.sin(2 * np.pi * freq_sweep * 2 * t)  # 2nd harmonic
    harmonic2 = 0.15 * np.sin(2 * np.pi * freq_sweep * 3 * t)  # 3rd harmonic
    harmonic3 = 0.1 * np.sin(2 * np.pi * freq_sweep * 4 * t)  # 4th harmonic
    
    # Combine harmonics
    audio = fundamental + harmonic1 + harmonic2 + harmonic3
    
    # Apply fade in/out
    audio = apply_fade(audio, fade_duration, sample_rate)
    
    # Normalize and save
    audio = normalize_audio(audio)
    save_wav_file(filename, audio, sample_rate)
    print(f"- {description}")

def create_warm_bass_sound(filename, start_freq, end_freq, duration, fade_duration, description):
    """Create a warm bass sound with subtle harmonics"""
    sample_rate = 44100
    samples = int(sample_rate * duration)
    
    t = np.linspace(0, duration, samples, False)
    
    # Create frequency sweep
    freq_sweep = np.linspace(start_freq, end_freq, samples)
    
    # Generate warm bass with gentle harmonics
    fundamental = np.sin(2 * np.pi * freq_sweep * t)
    harmonic1 = 0.25 * np.sin(2 * np.pi * freq_sweep * 1.5 * t)  # 1.5x harmonic
    harmonic2 = 0.1 * np.sin(2 * np.pi * freq_sweep * 2.5 * t)  # 2.5x harmonic
    
    # Combine with slight low-pass character
    audio = fundamental + harmonic1 + harmonic2
    
    # Apply fade in/out
    audio = apply_fade(audio, fade_duration, sample_rate)
    
    # Normalize and save
    audio = normalize_audio(audio)
    save_wav_file(filename, audio, sample_rate)
    print(f"- {description}")

def create_punchy_bass_sound(filename, start_freq, end_freq, duration, fade_duration, description):
    """Create a punchy bass sound with quick attack"""
    sample_rate = 44100
    samples = int(sample_rate * duration)
    
    t = np.linspace(0, duration, samples, False)
    
    # Create frequency sweep
    freq_sweep = np.linspace(start_freq, end_freq, samples)
    
    # Generate punchy bass with quick attack envelope
    fundamental = np.sin(2 * np.pi * freq_sweep * t)
    
    # Create punchy envelope (quick attack, medium decay)
    attack_samples = int(0.1 * sample_rate)  # 100ms attack
    decay_samples = int(0.2 * sample_rate)   # 200ms decay
    
    envelope = np.ones(samples)
    if samples > attack_samples:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    if samples > decay_samples:
        envelope[attack_samples:decay_samples] = np.linspace(1, 0.3, decay_samples - attack_samples)
        envelope[decay_samples:] = 0.3
    
    audio = fundamental * envelope
    
    # Apply fade in/out
    audio = apply_fade(audio, fade_duration, sample_rate)
    
    # Normalize and save
    audio = normalize_audio(audio)
    save_wav_file(filename, audio, sample_rate)
    print(f"- {description}")

def create_bass_click_sound(filename, start_freq, end_freq, duration, fade_duration, description):
    """Create a bass click sound with quick attack and release"""
    sample_rate = 44100
    samples = int(sample_rate * duration)
    
    t = np.linspace(0, duration, samples, False)
    
    # Create frequency sweep
    freq_sweep = np.linspace(start_freq, end_freq, samples)
    
    # Generate click-like bass
    fundamental = np.sin(2 * np.pi * freq_sweep * t)
    
    # Create click envelope (very quick attack and release)
    click_samples = int(0.05 * sample_rate)  # 50ms click
    release_samples = int(0.1 * sample_rate) # 100ms release
    
    envelope = np.ones(samples)
    if samples > click_samples:
        envelope[:click_samples] = np.linspace(0, 1, click_samples)
    if samples > release_samples:
        envelope[click_samples:release_samples] = np.linspace(1, 0, release_samples - click_samples)
        envelope[release_samples:] = 0
    
    audio = fundamental * envelope
    
    # Apply fade in/out
    audio = apply_fade(audio, fade_duration, sample_rate)
    
    # Normalize and save
    audio = normalize_audio(audio)
    save_wav_file(filename, audio, sample_rate)
    print(f"- {description}")

def create_original_sounds():
    """Create the original modern sound effects"""
    os.makedirs('assets', exist_ok=True)
    
    print("=== Creating Original Modern Sound Effects ===")
    
    # Start sound: Gentle ascending tone (300Hz → 400Hz)
    create_sweep_sound("assets/sound_start.wav", 300, 400, 0.4, 0.1, "Gentle ascending tone")
    
    # End sound: Gentle descending tone (400Hz → 300Hz)
    create_sweep_sound("assets/sound_end.wav", 400, 300, 0.5, 0.1, "Gentle descending tone")
    
    print("Original sounds created successfully!")

def create_sound_variations():
    """Create 10 sound effect variations for review"""
    os.makedirs('assets', exist_ok=True)
    sample_rate = 44100
    
    # Variation 1: Deep bass tones (150-200Hz)
    print("\n=== Creating Variation 1: Deep Bass ===")
    create_sweep_sound("assets/sound_start_v1.wav", 150, 200, 0.6, 0.4, "Deep ascending bass")
    create_sweep_sound("assets/sound_end_v1.wav", 200, 150, 0.7, 0.4, "Deep descending bass")
    
    # Variation 2: Mid-range tones (400-600Hz) with longer duration
    print("\n=== Creating Variation 2: Mid-Range Extended ===")
    create_sweep_sound("assets/sound_start_v2.wav", 400, 600, 0.8, 0.3, "Mid-range ascending extended")
    create_sweep_sound("assets/sound_end_v2.wav", 600, 400, 0.9, 0.3, "Mid-range descending extended")
    
    # Variation 3: High-pitched quick tones (800-1000Hz)
    print("\n=== Creating Variation 3: High-Pitched Quick ===")
    create_sweep_sound("assets/sound_start_v3.wav", 800, 1000, 0.2, 0.1, "High-pitched ascending quick")
    create_sweep_sound("assets/sound_end_v3.wav", 1000, 800, 0.25, 0.1, "High-pitched descending quick")
    
    # Variation 4: Bell-like tones (500-700Hz)
    print("\n=== Creating Variation 4: Bell-Like ===")
    create_bell_sound("assets/sound_start_v4.wav", 500, 700, 0.4, 0.15, "Bell-like ascending")
    create_bell_sound("assets/sound_end_v4.wav", 700, 500, 0.45, 0.15, "Bell-like descending")
    
    # Variation 5: Electronic beep (600-800Hz)
    print("\n=== Creating Variation 5: Electronic Beep ===")
    create_sweep_sound("assets/sound_start_v5.wav", 600, 800, 0.3, 0.08, "Electronic ascending beep")
    create_sweep_sound("assets/sound_end_v5.wav", 800, 600, 0.35, 0.08, "Electronic descending beep")
    
    # NEW VARIATIONS - Bass Focused with Short Duration
    
    # Variation 6: Ultra Deep Bass (80-120Hz) - Very short
    print("\n=== Creating Variation 6: Ultra Deep Bass ===")
    create_sweep_sound("assets/sound_start_v6.wav", 80, 120, 0.25, 0.08, "Ultra deep ascending bass")
    create_sweep_sound("assets/sound_end_v6.wav", 120, 80, 0.3, 0.08, "Ultra deep descending bass")
    
    # Variation 7: Warm Bass (180-250Hz) - Short with rich harmonics
    print("\n=== Creating Variation 7: Warm Bass ===")
    create_warm_bass_sound("assets/sound_start_v7.wav", 180, 250, 0.35, 0.1, "Warm ascending bass")
    create_warm_bass_sound("assets/sound_end_v7.wav", 250, 180, 0.4, 0.1, "Warm descending bass")
    
    # Variation 8: Punchy Bass (200-280Hz) - Quick attack
    print("\n=== Creating Variation 8: Punchy Bass ===")
    create_punchy_bass_sound("assets/sound_start_v8.wav", 200, 280, 0.2, 0.05, "Punchy ascending bass")
    create_punchy_bass_sound("assets/sound_end_v8.wav", 280, 200, 0.25, 0.05, "Punchy descending bass")
    
    # Variation 9: Sub Bass (60-100Hz) - Very low frequency
    print("\n=== Creating Variation 9: Sub Bass ===")
    create_sweep_sound("assets/sound_start_v9.wav", 60, 100, 0.4, 0.12, "Sub bass ascending")
    create_sweep_sound("assets/sound_end_v9.wav", 100, 60, 0.45, 0.12, "Sub bass descending")
    
    # Variation 10: Bass Click (150-200Hz) - Click-like character
    print("\n=== Creating Variation 10: Bass Click ===")
    create_bass_click_sound("assets/sound_start_v10.wav", 150, 200, 0.15, 0.03, "Bass click ascending")
    create_bass_click_sound("assets/sound_end_v10.wav", 200, 150, 0.18, 0.03, "Bass click descending")
    
    print("\nAll sounds have smooth fade in/out for professional feel")

if __name__ == "__main__":
    print("🎵 Sound Effect Generator")
    print("=" * 50)
    
    # Create original sounds
    create_original_sounds()
    
    # Create variations
    create_sound_variations()
    
    print("\n✅ All sound effects created successfully!")
    print("📁 Check the 'assets' folder for all sound files") 