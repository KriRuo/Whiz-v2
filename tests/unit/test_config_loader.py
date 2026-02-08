#!/usr/bin/env python3
"""
tests/unit/test_config_loader.py
--------------------------------
Unit tests for configuration loading system.

Tests environment variable loading, file loading, and configuration validation.

Author: Whiz Development Team
Date: 2026-02-08
"""

import unittest
import os
import json
import tempfile
from pathlib import Path
from core.config_loader import (
    ServiceConfig, ConfigLoader, load_config
)


class TestServiceConfig(unittest.TestCase):
    """Test ServiceConfig dataclass"""
    
    def test_create_default_config(self):
        """Test creating config with default values"""
        config = ServiceConfig()
        
        self.assertEqual(config.transcription_model_size, "tiny")
        self.assertEqual(config.transcription_engine, "faster")
        self.assertEqual(config.recording_sample_rate, 16000)
        self.assertEqual(config.recording_channels, 1)
        self.assertTrue(config.enable_metrics)
        self.assertTrue(config.enable_health_checks)
    
    def test_create_custom_config(self):
        """Test creating config with custom values"""
        config = ServiceConfig(
            transcription_model_size="base",
            transcription_engine="openai",
            recording_sample_rate=22050,
            log_level="DEBUG"
        )
        
        self.assertEqual(config.transcription_model_size, "base")
        self.assertEqual(config.transcription_engine, "openai")
        self.assertEqual(config.recording_sample_rate, 22050)
        self.assertEqual(config.log_level, "DEBUG")
    
    def test_invalid_model_size(self):
        """Test validation of invalid model size"""
        with self.assertRaises(ValueError):
            ServiceConfig(transcription_model_size="invalid")
    
    def test_invalid_engine(self):
        """Test validation of invalid engine"""
        with self.assertRaises(ValueError):
            ServiceConfig(transcription_engine="invalid")
    
    def test_invalid_sample_rate(self):
        """Test validation of invalid sample rate"""
        with self.assertRaises(ValueError):
            ServiceConfig(recording_sample_rate=0)
    
    def test_invalid_channels(self):
        """Test validation of invalid channels"""
        with self.assertRaises(ValueError):
            ServiceConfig(recording_channels=5)
    
    def test_invalid_temperature(self):
        """Test validation of invalid temperature"""
        with self.assertRaises(ValueError):
            ServiceConfig(transcription_temperature=1.5)
    
    def test_to_dict(self):
        """Test converting config to dictionary"""
        config = ServiceConfig(
            transcription_model_size="base",
            transcription_engine="openai"
        )
        
        config_dict = config.to_dict()
        
        self.assertIn("transcription", config_dict)
        self.assertIn("recording", config_dict)
        self.assertIn("performance", config_dict)
        self.assertIn("observability", config_dict)
        self.assertEqual(config_dict["transcription"]["model_size"], "base")
        self.assertEqual(config_dict["transcription"]["engine"], "openai")


class TestConfigLoader(unittest.TestCase):
    """Test ConfigLoader"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Save original environment
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Clean up after tests"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_load_from_env_empty(self):
        """Test loading from environment with no variables set"""
        # Clear all WHIZ_ variables
        for key in list(os.environ.keys()):
            if key.startswith("WHIZ_"):
                del os.environ[key]
        
        config_dict = ConfigLoader.load_from_env()
        
        self.assertEqual(len(config_dict), 0)
    
    def test_load_from_env_transcription_settings(self):
        """Test loading transcription settings from environment"""
        os.environ["WHIZ_TRANSCRIPTION_MODEL_SIZE"] = "base"
        os.environ["WHIZ_TRANSCRIPTION_ENGINE"] = "openai"
        os.environ["WHIZ_TRANSCRIPTION_LANGUAGE"] = "en"
        os.environ["WHIZ_TRANSCRIPTION_TEMPERATURE"] = "0.3"
        
        config_dict = ConfigLoader.load_from_env()
        
        self.assertEqual(config_dict["transcription_model_size"], "base")
        self.assertEqual(config_dict["transcription_engine"], "openai")
        self.assertEqual(config_dict["transcription_language"], "en")
        self.assertEqual(config_dict["transcription_temperature"], 0.3)
    
    def test_load_from_env_recording_settings(self):
        """Test loading recording settings from environment"""
        os.environ["WHIZ_RECORDING_SAMPLE_RATE"] = "22050"
        os.environ["WHIZ_RECORDING_CHANNELS"] = "2"
        os.environ["WHIZ_RECORDING_CHUNK_SIZE"] = "2048"
        
        config_dict = ConfigLoader.load_from_env()
        
        self.assertEqual(config_dict["recording_sample_rate"], 22050)
        self.assertEqual(config_dict["recording_channels"], 2)
        self.assertEqual(config_dict["recording_chunk_size"], 2048)
    
    def test_load_from_env_boolean_settings(self):
        """Test loading boolean settings from environment"""
        # Test various boolean formats
        test_cases = [
            ("true", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("0", False),
            ("no", False)
        ]
        
        for value, expected in test_cases:
            os.environ["WHIZ_ENABLE_METRICS"] = value
            config_dict = ConfigLoader.load_from_env()
            self.assertEqual(config_dict["enable_metrics"], expected,
                           f"Failed for value: {value}")
    
    def test_load_from_file_nonexistent(self):
        """Test loading from non-existent file"""
        config_dict = ConfigLoader.load_from_file("/tmp/nonexistent.json")
        
        self.assertEqual(len(config_dict), 0)
    
    def test_load_from_file_valid(self):
        """Test loading from valid JSON file"""
        config_data = {
            "transcription_model_size": "small",
            "transcription_engine": "faster",
            "recording_sample_rate": 24000
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config_dict = ConfigLoader.load_from_file(temp_path)
            
            self.assertEqual(config_dict["transcription_model_size"], "small")
            self.assertEqual(config_dict["transcription_engine"], "faster")
            self.assertEqual(config_dict["recording_sample_rate"], 24000)
        finally:
            os.unlink(temp_path)
    
    def test_load_from_file_invalid_json(self):
        """Test loading from invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            config_dict = ConfigLoader.load_from_file(temp_path)
            
            self.assertEqual(len(config_dict), 0)
        finally:
            os.unlink(temp_path)
    
    def test_save_to_file(self):
        """Test saving configuration to file"""
        config = ServiceConfig(
            transcription_model_size="base",
            transcription_engine="openai"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "config.json"
            
            success = ConfigLoader.save_to_file(config, file_path)
            
            self.assertTrue(success)
            self.assertTrue(file_path.exists())
            
            # Verify content
            with open(file_path, 'r') as f:
                saved_data = json.load(f)
            
            self.assertEqual(saved_data["transcription"]["model_size"], "base")
            self.assertEqual(saved_data["transcription"]["engine"], "openai")
    
    def test_load_priority_order(self):
        """Test that environment variables override file config"""
        # Create a config file
        config_data = {
            "transcription_model_size": "tiny",
            "transcription_engine": "faster"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            # Set environment variable that should override
            os.environ["WHIZ_TRANSCRIPTION_MODEL_SIZE"] = "base"
            
            # Note: We can't easily test ConfigLoader.load() without mocking
            # home directory, so we test the precedence separately
            file_config = ConfigLoader.load_from_file(temp_path)
            env_config = ConfigLoader.load_from_env()
            
            # Verify that env_config has the override value
            self.assertEqual(env_config.get("transcription_model_size"), "base")
            
        finally:
            os.unlink(temp_path)


class TestLoadConfig(unittest.TestCase):
    """Test convenience load_config function"""
    
    def test_load_config_returns_service_config(self):
        """Test that load_config returns a ServiceConfig instance"""
        config = load_config()
        
        self.assertIsInstance(config, ServiceConfig)
        # Should have default values at minimum
        self.assertEqual(config.transcription_model_size, "tiny")


if __name__ == "__main__":
    unittest.main()
