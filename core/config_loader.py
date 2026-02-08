#!/usr/bin/env python3
"""
core/config_loader.py
--------------------
Environment-aware configuration loader for backend services.

Supports loading configuration from:
- Environment variables
- Config files (JSON, YAML)
- Command-line arguments
- Default values

Author: Whiz Development Team
Date: 2026-02-08
Version: 2.0.0
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """
    Configuration for backend services with environment variable support.
    
    Supports hierarchical configuration loading:
    1. Default values
    2. Config file
    3. Environment variables (highest priority)
    """
    
    # Transcription configuration
    transcription_model_size: str = "tiny"
    transcription_engine: str = "faster"
    transcription_language: str = "auto"
    transcription_temperature: float = 0.0
    
    # Recording configuration
    recording_sample_rate: int = 16000
    recording_channels: int = 1
    recording_chunk_size: int = 2048
    recording_device_index: Optional[int] = None
    
    # Performance configuration
    enable_gpu: bool = True
    compute_type_cpu: str = "int8"
    compute_type_gpu: str = "float16"
    
    # Observability configuration
    enable_metrics: bool = True
    enable_health_checks: bool = True
    log_level: str = "INFO"
    
    # Resource limits
    max_recording_duration: int = 600  # seconds
    model_idle_timeout: int = 300  # seconds
    transcription_timeout: int = 60  # seconds
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate()
    
    def _validate(self) -> None:
        """Validate configuration values"""
        # Validate model size
        valid_models = ("tiny", "base", "small", "medium", "large")
        if self.transcription_model_size not in valid_models:
            raise ValueError(
                f"Invalid model size: {self.transcription_model_size}. "
                f"Must be one of: {valid_models}"
            )
        
        # Validate engine
        valid_engines = ("faster", "openai")
        if self.transcription_engine not in valid_engines:
            raise ValueError(
                f"Invalid engine: {self.transcription_engine}. "
                f"Must be one of: {valid_engines}"
            )
        
        # Validate sample rate
        if self.recording_sample_rate <= 0:
            raise ValueError(f"Invalid sample rate: {self.recording_sample_rate}")
        
        # Validate channels
        if self.recording_channels not in (1, 2):
            raise ValueError(f"Invalid channels: {self.recording_channels}")
        
        # Validate temperature
        if not 0.0 <= self.transcription_temperature <= 1.0:
            raise ValueError(
                f"Invalid temperature: {self.transcription_temperature}. "
                f"Must be between 0.0 and 1.0"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "transcription": {
                "model_size": self.transcription_model_size,
                "engine": self.transcription_engine,
                "language": self.transcription_language,
                "temperature": self.transcription_temperature
            },
            "recording": {
                "sample_rate": self.recording_sample_rate,
                "channels": self.recording_channels,
                "chunk_size": self.recording_chunk_size,
                "device_index": self.recording_device_index
            },
            "performance": {
                "enable_gpu": self.enable_gpu,
                "compute_type_cpu": self.compute_type_cpu,
                "compute_type_gpu": self.compute_type_gpu
            },
            "observability": {
                "enable_metrics": self.enable_metrics,
                "enable_health_checks": self.enable_health_checks,
                "log_level": self.log_level
            },
            "limits": {
                "max_recording_duration": self.max_recording_duration,
                "model_idle_timeout": self.model_idle_timeout,
                "transcription_timeout": self.transcription_timeout
            }
        }


class ConfigLoader:
    """
    Load configuration from multiple sources.
    
    Priority order (highest to lowest):
    1. Environment variables
    2. Config file
    3. Default values
    """
    
    ENV_PREFIX = "WHIZ_"
    
    @staticmethod
    def load_from_env() -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Environment variables should be prefixed with WHIZ_
        Example: WHIZ_TRANSCRIPTION_MODEL_SIZE=base
        
        Returns:
            Dictionary of configuration values
        """
        config = {}
        
        # Transcription settings
        if model_size := os.getenv(f"{ConfigLoader.ENV_PREFIX}TRANSCRIPTION_MODEL_SIZE"):
            config["transcription_model_size"] = model_size
        
        if engine := os.getenv(f"{ConfigLoader.ENV_PREFIX}TRANSCRIPTION_ENGINE"):
            config["transcription_engine"] = engine
        
        if language := os.getenv(f"{ConfigLoader.ENV_PREFIX}TRANSCRIPTION_LANGUAGE"):
            config["transcription_language"] = language
        
        if temp := os.getenv(f"{ConfigLoader.ENV_PREFIX}TRANSCRIPTION_TEMPERATURE"):
            config["transcription_temperature"] = float(temp)
        
        # Recording settings
        if sample_rate := os.getenv(f"{ConfigLoader.ENV_PREFIX}RECORDING_SAMPLE_RATE"):
            config["recording_sample_rate"] = int(sample_rate)
        
        if channels := os.getenv(f"{ConfigLoader.ENV_PREFIX}RECORDING_CHANNELS"):
            config["recording_channels"] = int(channels)
        
        if chunk_size := os.getenv(f"{ConfigLoader.ENV_PREFIX}RECORDING_CHUNK_SIZE"):
            config["recording_chunk_size"] = int(chunk_size)
        
        if device_index := os.getenv(f"{ConfigLoader.ENV_PREFIX}RECORDING_DEVICE_INDEX"):
            config["recording_device_index"] = int(device_index)
        
        # Performance settings
        if enable_gpu := os.getenv(f"{ConfigLoader.ENV_PREFIX}ENABLE_GPU"):
            config["enable_gpu"] = enable_gpu.lower() in ("true", "1", "yes")
        
        # Observability settings
        if enable_metrics := os.getenv(f"{ConfigLoader.ENV_PREFIX}ENABLE_METRICS"):
            config["enable_metrics"] = enable_metrics.lower() in ("true", "1", "yes")
        
        if enable_health := os.getenv(f"{ConfigLoader.ENV_PREFIX}ENABLE_HEALTH_CHECKS"):
            config["enable_health_checks"] = enable_health.lower() in ("true", "1", "yes")
        
        if log_level := os.getenv(f"{ConfigLoader.ENV_PREFIX}LOG_LEVEL"):
            config["log_level"] = log_level.upper()
        
        # Resource limits
        if max_duration := os.getenv(f"{ConfigLoader.ENV_PREFIX}MAX_RECORDING_DURATION"):
            config["max_recording_duration"] = int(max_duration)
        
        if model_timeout := os.getenv(f"{ConfigLoader.ENV_PREFIX}MODEL_IDLE_TIMEOUT"):
            config["model_idle_timeout"] = int(model_timeout)
        
        if trans_timeout := os.getenv(f"{ConfigLoader.ENV_PREFIX}TRANSCRIPTION_TIMEOUT"):
            config["transcription_timeout"] = int(trans_timeout)
        
        logger.info(f"Loaded {len(config)} configuration values from environment")
        return config
    
    @staticmethod
    def load_from_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Dictionary of configuration values
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"Config file not found: {file_path}")
            return {}
        
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            logger.info(f"Loaded configuration from {file_path}")
            return config
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config file {file_path}: {e}")
            return {}
        
        except Exception as e:
            logger.error(f"Failed to load config file {file_path}: {e}")
            return {}
    
    @staticmethod
    def load() -> ServiceConfig:
        """
        Load configuration from all sources.
        
        Priority order:
        1. Environment variables (highest)
        2. Config file
        3. Default values (lowest)
        
        Returns:
            ServiceConfig with merged configuration
        """
        # Start with defaults (from ServiceConfig dataclass)
        config_dict = {}
        
        # Load from config file if exists
        config_file = Path.home() / ".whiz" / "config.json"
        if config_file.exists():
            file_config = ConfigLoader.load_from_file(config_file)
            config_dict.update(file_config)
        
        # Load from environment variables (highest priority)
        env_config = ConfigLoader.load_from_env()
        config_dict.update(env_config)
        
        # Create ServiceConfig instance
        try:
            config = ServiceConfig(**config_dict)
            logger.info("Configuration loaded successfully")
            return config
        
        except Exception as e:
            logger.error(f"Failed to create configuration: {e}")
            # Return default configuration
            return ServiceConfig()
    
    @staticmethod
    def save_to_file(config: ServiceConfig, file_path: Union[str, Path]) -> bool:
        """
        Save configuration to JSON file.
        
        Args:
            config: Configuration to save
            file_path: Path to save configuration
            
        Returns:
            True if saved successfully, False otherwise
        """
        file_path = Path(file_path)
        
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(file_path, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            logger.info(f"Configuration saved to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save configuration to {file_path}: {e}")
            return False


def load_config() -> ServiceConfig:
    """
    Convenience function to load configuration.
    
    Returns:
        ServiceConfig instance
    """
    return ConfigLoader.load()
