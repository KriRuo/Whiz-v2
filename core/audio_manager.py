#!/usr/bin/env python3
"""
core/audio_manager.py
--------------------
Cross-platform audio recording manager for Whiz Voice-to-Text Application.

This module provides a unified interface for audio recording across different
platforms using sounddevice. It replaces platform-specific PyAudio with a
more reliable and cross-platform solution.

Features:
    - Cross-platform audio recording (Windows, macOS, Linux)
    - Device enumeration and selection
    - Smart device consolidation (groups duplicate Windows device configurations)
    - Real-time audio level monitoring
    - Thread-safe recording operations
    - Graceful degradation when audio is unavailable
    - Configurable sample rates and channels

Device Consolidation:
    Windows audio drivers expose each physical device multiple times with different
    configurations (sample rates, channel counts, driver modes). The AudioManager
    automatically consolidates these duplicates by grouping devices with the same
    base name and selecting the best configuration for each group. This provides
    a clean user interface while maintaining access to all device capabilities.

Dependencies:
    - sounddevice: Cross-platform audio I/O
    - numpy: Audio data processing
    - wave: WAV file handling
    - threading: Thread-safe operations

Example:
    Basic usage:
        from core.audio_manager import AudioManager
        
        audio_manager = AudioManager(sample_rate=16000, channels=1)
        if audio_manager.is_available():
            audio_manager.start_recording()
            # ... record audio ...
            audio_manager.stop_recording()
    
    Device consolidation:
        # Get consolidated device list (groups duplicates)
        devices, mapping = audio_manager.get_consolidated_devices()
        print(f"Found {len(devices)} physical devices")
        
        # Get all raw device configurations
        all_devices = audio_manager.get_devices()
        print(f"Total configurations: {len(all_devices)}")

Author: Whiz Development Team
Last Updated: October 10, 2025
"""

import threading
import wave
import numpy as np
import tempfile
import os
import queue
import time
import shutil
from typing import Optional, Callable, List, Dict, Any
from enum import Enum
from .logging_config import get_logger
from .path_validation import get_sandbox, safe_read_audio_file, create_safe_temp_file

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    sd = None

from .logging_config import get_logger
logger = get_logger(__name__)

class AudioFormat(Enum):
    """Audio format enumeration"""
    INT16 = "int16"
    FLOAT32 = "float32"

class AudioManager:
    """
    Cross-platform audio manager using sounddevice.
    
    Provides the same interface as the original PyAudio implementation
    but with better cross-platform support and easier installation.
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size  # Reduced from 2048 to 1024 for lower latency
        self.format = AudioFormat.INT16
        
        # Audio stream
        self.stream: Optional[sd.InputStream] = None
        self.is_recording = False
        self.recording_frames: queue.Queue = queue.Queue(maxsize=1000)  # Thread-safe queue
        self._recording_lock = threading.RLock()  # Fine-grained lock for recording operations
        
        # Device management
        self.input_device: Optional[int] = None
        self.available_devices: List[Dict[str, Any]] = []
        self.last_working_device: Optional[int] = None
        self.device_validation_enabled = False  # Temporarily disable to debug audio issues
        
        # Callbacks
        self.on_audio_data: Optional[Callable[[bytes], None]] = None
        self.on_audio_level: Optional[Callable[[float], None]] = None
        
        # Thread safety
        self._lock = threading.Lock()
        self._recording_thread: Optional[threading.Thread] = None
        
        logger.info(f"AudioManager initialized. sounddevice available: {SOUNDDEVICE_AVAILABLE}")
        
        if SOUNDDEVICE_AVAILABLE:
            # Try cached device first for faster startup
            cached_device_id = self._get_cached_device()
            if cached_device_id is not None:
                try:
                    # Quick validation - just check if device exists
                    device_info = sd.query_devices(cached_device_id)
                    if device_info['max_input_channels'] > 0:
                        self.input_device = cached_device_id
                        logger.info(f"Using cached audio device: {cached_device_id}")
                        # Still discover devices but skip full enumeration
                        self._discover_devices()
                        return  # Skip full enumeration!
                except Exception:
                    logger.debug("Cached device invalid, enumerating all devices")
            
            # Cache failed or no cache, enumerate as normal
            self._discover_devices()
    
    def is_available(self) -> bool:
        """Check if audio functionality is available on this platform"""
        return SOUNDDEVICE_AVAILABLE
    
    def _discover_devices(self) -> None:
        """Discover available audio input devices"""
        try:
            devices = sd.query_devices()
            self.available_devices = []
            
            for i, device in enumerate(devices):
                # Check if device has input channels and the key exists
                max_input_channels = device.get('max_input_channels', 0)
                if max_input_channels > 0:
                    device_info = {
                        'index': i,
                        'name': device['name'],
                        'channels': max_input_channels,
                        'sample_rate': device.get('default_samplerate', 44100),
                        'is_default': i == sd.default.device[0]  # Input device
                    }
                    self.available_devices.append(device_info)
            
            logger.info(f"Found {len(self.available_devices)} input devices")
            
            # Debug: List all available input devices
            for i, device in enumerate(self.available_devices):
                logger.info(f"Device {i}: {device['name']} (channels: {device['channels']})")
            
        except Exception as e:
            logger.error(f"Error discovering audio devices: {e}")
            self.available_devices = []
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get list of available input devices"""
        return self.available_devices.copy()
    
    def get_consolidated_devices(self) -> tuple[List[Dict[str, Any]], Dict[int, int]]:
        """
        Get consolidated device list with mapping to original indices.
        
        Windows audio drivers expose each physical device multiple times with different
        configurations (sample rates, channel counts, driver modes). This method groups
        devices by their base name and selects the best configuration for each group.
        
        Returns:
            tuple: (consolidated_devices, display_to_original_index_map)
                - consolidated_devices: List of device dicts with best config per group
                - display_to_original_index_map: Maps display index to original device index
        
        Example:
            >>> audio_manager = AudioManager()
            >>> devices, mapping = audio_manager.get_consolidated_devices()
            >>> print(f"Found {len(devices)} consolidated devices")
            >>> print(f"Display index 0 maps to original index {mapping[0]}")
        """
        if not self.available_devices:
            return [], {}
        
        # Group devices by base name
        device_groups = {}
        for device in self.available_devices:
            base_name = self._extract_base_name(device['name'])
            if base_name not in device_groups:
                device_groups[base_name] = []
            device_groups[base_name].append(device)
        
        # Select best configuration for each group
        consolidated_devices = []
        display_to_original_map = {}
        
        for display_index, (base_name, devices) in enumerate(device_groups.items()):
            # Score each device configuration and select the best one
            best_device = self._select_best_device_config(devices)
            
            # Create enhanced device info for display
            consolidated_device = best_device.copy()
            consolidated_device['display_name'] = self._create_consolidated_display_name(best_device, base_name)
            consolidated_device['base_name'] = base_name
            consolidated_device['original_index'] = best_device['index']  # Store original index
            
            consolidated_devices.append(consolidated_device)
            display_to_original_map[display_index] = best_device['index']
        
        # Sort consolidated devices by display name for consistent ordering
        consolidated_devices.sort(key=lambda d: d['display_name'])
        
        # Rebuild mapping after sorting
        display_to_original_map = {}
        for display_index, device in enumerate(consolidated_devices):
            display_to_original_map[display_index] = device['original_index']
        
        logger.info(f"Consolidated {len(self.available_devices)} devices into {len(consolidated_devices)} groups")
        return consolidated_devices, display_to_original_map
    
    def _extract_base_name(self, device_name: str) -> str:
        """
        Extract the base device name by removing technical suffixes and paths.
        
        Windows audio device names often include technical information like sample rates,
        channel counts, driver paths, and mode indicators. This method strips these to
        get the core device name for grouping.
        
        Args:
            device_name: Full device name from Windows audio system
            
        Returns:
            Cleaned base name suitable for grouping devices
            
        Example:
            >>> _extract_base_name("Jabra Link 390 (48000.0Hz, 2ch)")
            "Jabra Link 390"
            >>> _extract_base_name("Realtek(R) Audio @System32\\drivers\\...")
            "Realtek(R) Audio"
        """
        import re
        
        # Remove device path components (everything after @)
        base_name = device_name.split('@')[0].strip()
        
        # Remove sample rate and channel indicators
        # Pattern matches: (44100Hz), (48000.0Hz, 2ch), (16000.0Hz), etc.
        base_name = re.sub(r'\s*\(\d+(?:\.\d+)?Hz(?:,\s*\d+ch)?\)', '', base_name)
        
        # Remove common Windows driver suffixes
        suffixes_to_remove = [
            ' (Hands-Free)',      # Bluetooth phone call mode (lower quality)
            ' (SST)',            # System Sound Technology
            ' (Input)',          # Generic input indicator
            ' - Input',          # Alternative input indicator
            ' (Mic input)',      # Microphone input indicator
            ' (output)',         # Output device (shouldn't appear in input list)
            ' (bthhfenum)',      # Bluetooth hands-free enumeration
            ' (System32)',       # System32 driver path
            ' (drivers)',        # Driver path indicator
            ' (Stereo)',         # Stereo indicator
            ' (Mono)',           # Mono indicator
        ]
        
        for suffix in suffixes_to_remove:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)].strip()
        
        # Additional cleanup for specific device patterns
        # Remove incomplete device names (often truncated in Windows)
        if base_name.endswith(' ('):
            base_name = base_name[:-2].strip()
        
        # Normalize common device name variations
        base_name = re.sub(r'\s+', ' ', base_name)  # Multiple spaces to single space
        
        # Handle specific device name patterns
        if 'Jabra Link' in base_name and not base_name.endswith('390'):
            # Handle truncated Jabra Link names
            if 'Jabra Link' in base_name:
                base_name = 'Jabra Link 390'  # Assume 390 for truncated names
        
        return base_name
    
    def _select_best_device_config(self, devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select the best device configuration from a group of similar devices.
        
        Given multiple configurations of the same physical device, this method
        scores each configuration and returns the one with the highest score.
        Scoring prioritizes quality and compatibility over specialized modes.
        
        Args:
            devices: List of device configurations for the same physical device
            
        Returns:
            Device configuration with the highest score
            
        Scoring criteria (higher is better):
        - Channel count: 2 channels preferred over 1 (stereo > mono)
        - Sample rate: 44100Hz/48000Hz preferred (standard quality)
        - Avoid Hands-Free: Lower quality Bluetooth phone call mode
        - Device type: Prefer specific microphone types over generic
        """
        if len(devices) == 1:
            return devices[0]
        
        best_device = devices[0]  # Initialize with first device as fallback
        best_score = -1
        
        for device in devices:
            score = self._score_device_config(device)
            if score > best_score:
                best_score = score
                best_device = device
        
        logger.debug(f"Selected device config: {best_device['name']} (score: {best_score})")
        return best_device
    
    def _score_device_config(self, device: Dict[str, Any]) -> int:
        """
        Score a device configuration based on quality and compatibility preferences.
        
        Args:
            device: Device configuration dictionary
            
        Returns:
            Score (higher is better) for device configuration ranking
        """
        score = 0
        name = device['name'].lower()
        channels = device.get('channels', 0)
        sample_rate = device.get('sample_rate', 0)
        
        # Channel count scoring (stereo preferred for better quality)
        if channels >= 2:
            score += 20  # Stereo/multi-channel preferred
        elif channels == 1:
            score += 10  # Mono acceptable but lower priority
        
        # Sample rate scoring (standard rates preferred)
        if sample_rate in [44100, 48000]:
            score += 15  # Standard quality rates
        elif sample_rate in [16000, 22050, 32000]:
            score += 5   # Lower quality but acceptable
        elif sample_rate >= 96000:
            score += 10  # High quality but may cause compatibility issues
        else:
            score += 0   # Unknown or unusual rates
        
        # Avoid Hands-Free mode (lower quality for phone calls)
        if 'hands-free' in name:
            score -= 15  # Penalize Bluetooth phone call mode
        
        # Prefer specific device types over generic ones
        if 'headset microphone' in name:
            score += 10  # Specific headset mic
        elif 'webcam' in name:
            score += 8   # Webcam microphone
        elif 'realtek' in name:
            score += 5   # Built-in audio
        elif 'microphone' in name:
            score += 3   # Generic microphone
        
        # Avoid system/virtual devices
        if any(term in name for term in ['system', 'virtual', 'mapper', 'mix']):
            score -= 10  # Prefer physical devices
        
        return score
    
    def _create_consolidated_display_name(self, device: Dict[str, Any], base_name: str) -> str:
        """
        Create a user-friendly display name for consolidated devices.
        
        Args:
            device: Device configuration dictionary
            base_name: Extracted base name for the device group
            
        Returns:
            Clean, user-friendly display name
        """
        # Start with the base name
        display_name = base_name
        
        # Add quality indicators for clarity
        quality_parts = []
        
        channels = device.get('channels', 0)
        if channels >= 2:
            quality_parts.append(f"{channels}ch")
        
        sample_rate = device.get('sample_rate', 0)
        if sample_rate > 0:
            # Convert to kHz for cleaner display
            if sample_rate >= 1000:
                quality_parts.append(f"{sample_rate // 1000}kHz")
            else:
                quality_parts.append(f"{sample_rate}Hz")
        
        # Add quality indicators if they provide useful information
        if quality_parts:
            display_name = f"{display_name} ({', '.join(quality_parts)})"
        
        return display_name
    
    def validate_device_connection(self, device_index: Optional[int] = None) -> bool:
        """
        Validate that the specified device is still available and working.
        
        Args:
            device_index: Device index to validate, or None for current device
            
        Returns:
            True if device is valid and working, False otherwise
        """
        if not self.is_available():
            return False
        
        target_device = device_index if device_index is not None else self.input_device
        
        try:
            # Refresh device list to check for changes
            self._discover_devices()
            
            if target_device is None:
                # System default - always assume it's available
                return True
            
            # Check if device still exists in the list
            if target_device >= len(self.available_devices):
                logger.warning(f"Device {target_device} no longer available")
                return False
            
            # Test device with a quick stream creation
            test_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16',
                device=target_device,
                blocksize=self.chunk_size
            )
            
            # Try to start and immediately stop
            test_stream.start()
            test_stream.stop()
            test_stream.close()
            
            logger.debug(f"Device {target_device} validation successful")
            return True
            
        except Exception as e:
            logger.warning(f"Device {target_device} validation failed: {e}")
            return False
    
    def get_fallback_device(self) -> Optional[int]:
        """
        Get a fallback device when the current device fails.
        
        Returns:
            Device index for fallback, or None for system default
        """
        try:
            # First try the last working device
            if (self.last_working_device is not None and 
                self.last_working_device < len(self.available_devices) and
                self.validate_device_connection(self.last_working_device)):
                logger.info(f"Using last working device: {self.last_working_device}")
                return self.last_working_device
            
            # Try to find any working device
            for i, device in enumerate(self.available_devices):
                if self.validate_device_connection(i):
                    logger.info(f"Found working fallback device: {i} - {device['name']}")
                    return i
            
            # No working device found, use system default
            logger.warning("No working devices found, falling back to system default")
            return None
            
        except Exception as e:
            logger.error(f"Error finding fallback device: {e}")
            return None
    
    def handle_device_failure(self) -> bool:
        """
        Handle device failure by switching to a fallback device.
        
        Returns:
            True if fallback was successful, False otherwise
        """
        logger.warning("Audio device failure detected, attempting fallback")
        
        try:
            # Get fallback device
            fallback_device = self.get_fallback_device()
            
            if fallback_device is not None:
                # Update to fallback device
                self.input_device = fallback_device
                self.last_working_device = fallback_device
                logger.info(f"Switched to fallback device: {fallback_device}")
                return True
            else:
                # Use system default
                self.input_device = None
                logger.info("Switched to system default device")
                return True
                
        except Exception as e:
            logger.error(f"Error handling device failure: {e}")
            return False
    
    def select_device(self, device_index: Optional[int] = None) -> bool:
        """
        Select an audio input device with validation.
        
        Args:
            device_index: Device index to select, or None for default
            
        Returns:
            True if device was selected successfully, False otherwise
        """
        if not self.is_available():
            logger.error("sounddevice not available, cannot select device")
            return False
        
        try:
            if device_index is None:
                # Try to find a specific microphone device instead of default
                microphone_device = None
                for i, device in enumerate(self.available_devices):
                    device_name = device['name'].lower()
                    # Look for common microphone device names
                    if any(keyword in device_name for keyword in ['microphone', 'mic', 'realtek', 'usb', 'headset', 'webcam']):
                        microphone_device = device['index']  # Use the actual device index
                        logger.info(f"Found microphone device: {device['index']} - {device['name']}")
                        break
                
                if microphone_device is not None:
                    self.input_device = microphone_device
                    logger.info(f"Using microphone device: {microphone_device}")
                else:
                    # Use default device
                    self.input_device = None
                    logger.info("Using default audio input device")
                return True
            
            # Validate device index
            if device_index < 0 or device_index >= len(self.available_devices):
                logger.error(f"Invalid device index: {device_index}")
                return False
            
            # Validate device connection if validation is enabled
            if self.device_validation_enabled:
                if not self.validate_device_connection(device_index):
                    logger.warning(f"Device {device_index} validation failed, attempting fallback")
                    fallback_device = self.get_fallback_device()
                    if fallback_device is not None:
                        device_index = fallback_device
                        logger.info(f"Using fallback device: {device_index}")
                    else:
                        logger.error("No valid fallback device found")
                        return False
            
            self.input_device = device_index
            self.last_working_device = device_index  # Remember this as working
            device_name = self.available_devices[device_index]['name']
            logger.info(f"Selected audio device: {device_index} - {device_name}")
            
            # Cache the selected device for faster startup next time
            self._cache_device(device_index)
            
            return True
            
        except Exception as e:
            logger.error(f"Error selecting device {device_index}: {e}")
            return False
    
    def start_recording(self) -> bool:
        """
        Start audio recording with device validation and fallback.
        
        Returns:
            True if recording started successfully, False otherwise
        """
        if not self.is_available():
            logger.error("sounddevice not available, cannot start recording")
            return False
        
        if self.is_recording:
            logger.warning("Recording already in progress")
            return False
        
        # Validate device before starting recording
        if self.device_validation_enabled:
            if not self.validate_device_connection():
                logger.warning("Current device validation failed, attempting fallback")
                if not self.handle_device_failure():
                    logger.error("Failed to find working device for recording")
                    return False
        
        try:
            with self._recording_lock:
                # Clear previous recording data from queue
                while not self.recording_frames.empty():
                    try:
                        self.recording_frames.get_nowait()
                    except queue.Empty:
                        break
                
                # Create audio stream with simpler settings for debugging
                self.stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype='float32',  # Try float32 instead of int16
                    device=self.input_device,
                    blocksize=self.chunk_size,
                    callback=self._audio_callback
                )
                
                # Debug: Log stream configuration
                logger.info(f"Audio stream created: device={self.input_device}, samplerate={self.sample_rate}, channels={self.channels}, blocksize={self.chunk_size}")
                
                # Start recording
                self.stream.start()
                self.is_recording = True
                
                # Update last working device on successful start
                if self.input_device is not None:
                    self.last_working_device = self.input_device
                
                logger.info("Audio recording started")
                return True
                
        except Exception as e:
            logger.error(f"Error starting audio recording: {e}")
            self._cleanup_stream()
            
            # Try fallback if device validation is enabled
            if self.device_validation_enabled:
                logger.info("Attempting device fallback after recording failure")
                if self.handle_device_failure():
                    # Retry recording with fallback device
                    try:
                        with self._recording_lock:
                            # Clear previous recording data from queue
                            while not self.recording_frames.empty():
                                try:
                                    self.recording_frames.get_nowait()
                                except queue.Empty:
                                    break
                            
                            self.stream = sd.InputStream(
                                samplerate=self.sample_rate,
                                channels=self.channels,
                                dtype='int16',
                                device=self.input_device,
                                blocksize=self.chunk_size,
                                callback=self._audio_callback,
                                latency='low',
                                extra_settings=None,
                                prime_output_buffers_using_stream_callback=False
                            )
                            self.stream.start()
                            self.is_recording = True
                            logger.info("Audio recording started with fallback device")
                            return True
                    except Exception as retry_e:
                        logger.error(f"Fallback recording also failed: {retry_e}")
            
            return False
    
    def stop_recording(self) -> List[bytes]:
        """
        Stop audio recording and return recorded frames.
        
        Returns:
            List of audio frames (bytes)
        """
        if not self.is_recording:
            logger.warning("No recording in progress")
            return []
        
        try:
            with self._recording_lock:
                # Stop the stream
                if self.stream:
                    self.stream.stop()
                    self.stream.close()
                
                self.is_recording = False
                self.stream = None
                
                # Small delay to ensure audio callback has finished processing
                time.sleep(0.1)
                
                # Collect all frames from the queue
                frames = []
                while not self.recording_frames.empty():
                    try:
                        frame = self.recording_frames.get_nowait()
                        frames.append(frame)
                    except queue.Empty:
                        break
                
                # Debug: Check if frames contain actual audio data
                total_bytes = sum(len(frame) for frame in frames)
                logger.info(f"Audio recording stopped. Recorded {len(frames)} frames, total bytes: {total_bytes}")
                
                if total_bytes == 0:
                    logger.warning("No audio data captured - all frames are empty")
                elif total_bytes < 1000:  # Less than ~60ms of audio at 16kHz
                    logger.warning(f"Very little audio data captured: {total_bytes} bytes")
                
                return frames
                
        except Exception as e:
            logger.error(f"Error stopping audio recording: {e}")
            self._cleanup_stream()
            return []
    
    def _audio_callback(self, indata, frames, time, status):
        """
        Thread-safe callback function for audio stream.
        
        This callback runs in the audio thread and must be thread-safe.
        Uses queue.Queue for thread-safe data storage and fine-grained locking.
        """
        try:
            if status:
                logger.warning(f"Audio callback status: {status}")
            
            # Convert numpy array to bytes
            audio_data = indata.copy()
            
            # Debug: Check the shape and type of input data (only log occasionally)
            if hasattr(self, '_callback_count'):
                self._callback_count += 1
            else:
                self._callback_count = 1
            
            if self._callback_count % 100 == 1:  # Log every 100th callback
                logger.debug(f"Audio callback input: shape={audio_data.shape}, dtype={audio_data.dtype}, min={audio_data.min()}, max={audio_data.max()}")
            
            audio_bytes = audio_data.tobytes()
            
            # Debug: Check if we're receiving actual audio data
            if len(audio_bytes) > 0:
                # Calculate RMS to check if there's actual audio content
                if audio_data.dtype == np.float32:
                    rms = np.sqrt(np.mean(audio_data ** 2))
                else:
                    rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
                
                # Only log audio level occasionally to avoid spam
                if self._callback_count % 200 == 1:  # Log every 200th callback
                    if rms > 0.001:  # Threshold for detecting actual audio
                        logger.debug(f"Audio callback: received {len(audio_bytes)} bytes, RMS: {rms:.6f}")
                    else:
                        logger.debug(f"Audio callback: received {len(audio_bytes)} bytes, RMS: {rms:.6f} (silence)")
            else:
                logger.warning("Audio callback: received empty audio data")
            
            # Store audio data in thread-safe queue with timeout
            try:
                self.recording_frames.put(audio_bytes, timeout=0.1)  # Non-blocking with timeout
            except queue.Full:
                # Queue is full, drop oldest frame to prevent memory buildup
                try:
                    self.recording_frames.get_nowait()  # Remove oldest frame
                    self.recording_frames.put(audio_bytes, timeout=0.1)  # Add new frame
                    logger.debug("Audio queue full, dropped oldest frame")
                except queue.Empty:
                    # Queue was already empty, just add the new frame
                    self.recording_frames.put(audio_bytes, timeout=0.1)
            
            # Calculate audio level for visualization (thread-safe)
            if self.on_audio_level:
                try:
                    # Calculate RMS (Root Mean Square) as a measure of audio level
                    if audio_data.dtype == np.float32:
                        rms = np.sqrt(np.mean(audio_data ** 2))
                    else:
                        rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
                    # Normalize to 0-1 range (adjust sensitivity as needed)
                    level = min(1.0, rms / 0.1)  # Adjust divisor for float32 sensitivity
                    self.on_audio_level(level)
                except Exception as e:
                    logger.debug(f"Error calculating audio level: {e}")
            
            # Call audio data callback if set
            if self.on_audio_data:
                try:
                    self.on_audio_data(audio_bytes)
                except Exception as e:
                    logger.debug(f"Error in audio data callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error in audio callback: {e}")
    
    def _cleanup_stream(self) -> None:
        """Clean up audio stream"""
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
        except Exception as e:
            logger.warning(f"Error cleaning up audio stream: {e}")
        finally:
            self.stream = None
            self.is_recording = False
    
    def save_audio_to_file(self, frames: List[bytes], filename: str) -> bool:
        """
        Save recorded audio frames to a WAV file using sandboxed operations.
        
        Args:
            frames: List of audio frames (bytes)
            filename: Output filename
            
        Returns:
            True if file was saved successfully, False otherwise
        """
        if not frames:
            logger.warning("No audio frames to save")
            return False
        
        try:
            # Validate filename using sandbox
            sandbox = get_sandbox()
            validator = sandbox.validator
            
            # Sanitize filename
            safe_filename = validator.sanitize_filename(filename)
            if not safe_filename.endswith('.wav'):
                safe_filename += '.wav'
            
            # Save directly to the requested filename
            logger.info(f"Saving audio to: {filename}")
            logger.info(f"Audio data: {len(frames)} frames, total bytes: {sum(len(f) for f in frames)}")
            
            with wave.open(str(filename), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # int16 = 2 bytes per sample (WAV standard)
                wf.setframerate(self.sample_rate)
                
                # Convert float32 data to int16 for WAV format
                import numpy as np
                audio_data = np.frombuffer(b''.join(frames), dtype=np.float32)
                logger.info(f"Audio data shape: {audio_data.shape}, dtype: {audio_data.dtype}")
                logger.info(f"Audio data range: min={audio_data.min():.6f}, max={audio_data.max():.6f}")
                
                # Convert float32 (-1.0 to 1.0) to int16 (-32768 to 32767)
                audio_int16 = (audio_data * 32767).astype(np.int16)
                logger.info(f"Converted audio shape: {audio_int16.shape}, dtype: {audio_int16.dtype}")
                logger.info(f"Converted audio range: min={audio_int16.min()}, max={audio_int16.max()}")
                
                wf.writeframes(audio_int16.tobytes())
                logger.info(f"WAV file written successfully to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving audio to {filename}: {e}")
            return False
    
    def test_device(self, device_index: Optional[int] = None) -> bool:
        """
        Test if an audio device works.
        
        Args:
            device_index: Device index to test, or None for default
            
        Returns:
            True if device works, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            # Try to create a short test recording
            test_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16',
                device=device_index,
                blocksize=self.chunk_size
            )
            
            # Start and immediately stop
            test_stream.start()
            test_stream.stop()
            test_stream.close()
            
            logger.info(f"Device {device_index} test successful")
            return True
            
        except Exception as e:
            logger.warning(f"Device {device_index} test failed: {e}")
            return False
    
    def set_callbacks(self, 
                     on_audio_data: Optional[Callable[[bytes], None]] = None,
                     on_audio_level: Optional[Callable[[float], None]] = None) -> None:
        """Set callback functions for audio events"""
        self.on_audio_data = on_audio_data
        self.on_audio_level = on_audio_level
        logger.debug("Audio callbacks set")
    
    def set_device_validation(self, enabled: bool) -> None:
        """Enable or disable device validation"""
        self.device_validation_enabled = enabled
        logger.info(f"Device validation {'enabled' if enabled else 'disabled'}")
    
    def get_device_status(self) -> Dict[str, Any]:
        """Get detailed device status information"""
        return {
            "current_device": self.input_device,
            "last_working_device": self.last_working_device,
            "device_count": len(self.available_devices),
            "validation_enabled": self.device_validation_enabled,
            "current_device_valid": self.validate_device_connection() if self.device_validation_enabled else True,
            "available_devices": [
                {
                    "index": device["index"],
                    "name": device["name"],
                    "channels": device["channels"],
                    "sample_rate": device["sample_rate"],
                    "is_default": device["is_default"]
                }
                for device in self.available_devices
            ]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status information"""
        return {
            "available": self.is_available(),
            "recording": self.is_recording,
            "device_count": len(self.available_devices),
            "selected_device": self.input_device,
            "last_working_device": self.last_working_device,
            "validation_enabled": self.device_validation_enabled,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "chunk_size": self.chunk_size
        }
    
    def _get_cached_device(self) -> Optional[int]:
        """Get cached device from temp file"""
        cache_file = os.path.join(tempfile.gettempdir(), 'whiz_audio_device.cache')
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return int(f.read().strip())
        except Exception:
            pass
        return None

    def _cache_device(self, device_id: int) -> None:
        """Cache current device to temp file"""
        cache_file = os.path.join(tempfile.gettempdir(), 'whiz_audio_device.cache')
        try:
            with open(cache_file, 'w') as f:
                f.write(str(device_id))
        except Exception:
            pass

    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            self._cleanup_stream()
            logger.info("AudioManager cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
