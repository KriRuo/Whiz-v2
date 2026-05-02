#!/usr/bin/env python3
"""
tests/integration/test_service_observability_integration.py
----------------------------------------------------------
Integration tests for service observability (health checks and metrics).

Tests the integration of health checks and metrics with actual services.

Author: Whiz Development Team
Date: 2026-02-08
"""

import unittest
from unittest.mock import Mock, patch
from core.transcription_service import TranscriptionService, TranscriptionConfig
from core.recording_service import RecordingService, RecordingConfig
from core.service_health import get_health_monitor, HealthStatus, ReadinessStatus
from core.service_metrics import get_metrics_aggregator


class TestTranscriptionServiceHealth(unittest.TestCase):
    """Test health checks for TranscriptionService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = TranscriptionConfig(
            model_size="tiny",
            engine="faster",
            language="auto"
        )
        self.service = TranscriptionService(self.config)
    
    def test_health_check_before_model_load(self):
        """Test health check before model is loaded"""
        health = self.service.health_check()
        
        self.assertIn("status", health)
        self.assertEqual(health["service_name"], "TranscriptionService")
        # Should be healthy (lazy loading)
        self.assertIn(health["status"], ["healthy", "degraded"])
    
    def test_readiness_check_before_model_load(self):
        """Test readiness check before model is loaded"""
        readiness = self.service.readiness_check()
        
        self.assertIn("status", readiness)
        self.assertEqual(readiness["service_name"], "TranscriptionService")
    
    def test_health_check_with_load_error(self):
        """Test health check when model loading failed"""
        # Simulate a load error
        self.service.model_load_error = "Mock error"
        
        health = self.service.health_check()
        
        self.assertEqual(health["status"], "unhealthy")
        self.assertIn("error", health["details"])
    
    def test_health_check_when_loaded(self):
        """Test health check when model is loaded"""
        # Simulate model loaded
        self.service.model_loaded = True
        self.service.model = Mock()
        
        health = self.service.health_check()
        
        self.assertEqual(health["status"], "healthy")
        self.assertIn("engine", health["details"])


class TestRecordingServiceHealth(unittest.TestCase):
    """Test health checks for RecordingService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = RecordingConfig(
            sample_rate=16000,
            channels=1
        )
        # Mock AudioManager to avoid hardware dependencies
        with patch('core.recording_service.AudioManager'):
            self.service = RecordingService(self.config)
    
    def test_health_check_idle_state(self):
        """Test health check in idle state"""
        health = self.service.health_check()
        
        self.assertIn("status", health)
        self.assertEqual(health["service_name"], "RecordingService")
        self.assertIn("state", health["details"])
    
    def test_readiness_check_idle_state(self):
        """Test readiness check in idle state"""
        readiness = self.service.readiness_check()
        
        self.assertIn("status", readiness)
        self.assertEqual(readiness["service_name"], "RecordingService")
    
    def test_health_check_audio_unavailable(self):
        """Test health check when audio is unavailable"""
        # Mock audio unavailable
        self.service.audio_manager.is_available = Mock(return_value=False)
        
        health = self.service.health_check()
        
        self.assertEqual(health["status"], "unhealthy")
        self.assertIn("audio_available", health["details"])
    
    def test_readiness_check_audio_unavailable(self):
        """Test readiness check when audio is unavailable"""
        # Mock audio unavailable
        self.service.audio_manager.is_available = Mock(return_value=False)
        
        readiness = self.service.readiness_check()
        
        self.assertEqual(readiness["status"], "not_ready")
        self.assertFalse(readiness["dependencies_ready"])


class TestHealthMonitorIntegration(unittest.TestCase):
    """Test health monitor integration with services"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.health_monitor = get_health_monitor()
        
        # Create services
        self.transcription_config = TranscriptionConfig(model_size="tiny")
        self.transcription_service = TranscriptionService(self.transcription_config)
        
        with patch('core.recording_service.AudioManager'):
            self.recording_config = RecordingConfig()
            self.recording_service = RecordingService(self.recording_config)
    
    def test_register_service_health_checks(self):
        """Test registering health checks from services"""
        # Get health checks from services
        transcription_health = self.transcription_service.health_check()
        recording_health = self.recording_service.health_check()
        
        # Verify they can be converted to HealthCheckResult
        self.assertIn("status", transcription_health)
        self.assertIn("service_name", transcription_health)
        self.assertIn("status", recording_health)
        self.assertIn("service_name", recording_health)
    
    def test_system_health_with_multiple_services(self):
        """Test system health with multiple services"""
        from core.service_health import HealthCheckResult, HealthStatus
        
        # Register health checks for both services
        self.health_monitor.register_health_check(
            "TranscriptionService",
            HealthCheckResult(
                status=HealthStatus.HEALTHY,
                service_name="TranscriptionService",
                message="Service is healthy"
            )
        )
        
        self.health_monitor.register_health_check(
            "RecordingService",
            HealthCheckResult(
                status=HealthStatus.HEALTHY,
                service_name="RecordingService",
                message="Service is healthy"
            )
        )
        
        # Check overall system health
        self.assertTrue(self.health_monitor.is_system_healthy())
        
        summary = self.health_monitor.get_system_health_summary()
        self.assertEqual(summary["total_services"], 2)
        self.assertEqual(summary["healthy_services"], 2)


class TestMetricsIntegration(unittest.TestCase):
    """Test metrics integration with services"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.metrics_aggregator = get_metrics_aggregator()
    
    def test_register_services_for_metrics(self):
        """Test registering services for metrics collection"""
        transcription_metrics = self.metrics_aggregator.register_service("TranscriptionService")
        recording_metrics = self.metrics_aggregator.register_service("RecordingService")
        
        self.assertEqual(transcription_metrics.service_name, "TranscriptionService")
        self.assertEqual(recording_metrics.service_name, "RecordingService")
    
    def test_collect_metrics_from_services(self):
        """Test collecting metrics from services"""
        transcription_metrics = self.metrics_aggregator.register_service("TranscriptionService")
        
        # Simulate some operations
        transcription_metrics.increment_counter("transcriptions_total", 5)
        transcription_metrics.set_gauge("model_load_time", 2.5)
        transcription_metrics.record_histogram("transcription_duration", 1.2)
        
        # Get all metrics
        all_metrics = self.metrics_aggregator.get_all_metrics()
        
        self.assertIn("services", all_metrics)
        self.assertIn("TranscriptionService", all_metrics["services"])
    
    def test_service_metrics_summary(self):
        """Test getting service metrics summary"""
        transcription_metrics = self.metrics_aggregator.register_service("TranscriptionService")
        recording_metrics = self.metrics_aggregator.register_service("RecordingService")
        
        # Add some metrics
        transcription_metrics.increment_counter("operations")
        recording_metrics.increment_counter("recordings")
        
        summary = self.metrics_aggregator.get_summary()
        
        self.assertEqual(summary["total_services"], 2)
        self.assertIn("TranscriptionService", summary["services"])
        self.assertIn("RecordingService", summary["services"])


if __name__ == "__main__":
    unittest.main()
