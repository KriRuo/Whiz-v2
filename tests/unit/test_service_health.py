#!/usr/bin/env python3
"""
tests/unit/test_service_health.py
---------------------------------
Unit tests for service health monitoring system.

Tests health checks, readiness checks, and health monitoring functionality.

Author: Whiz Development Team
Date: 2026-02-08
"""

import unittest
from datetime import datetime
from core.service_health import (
    HealthStatus, ReadinessStatus,
    HealthCheckResult, ReadinessCheckResult,
    ServiceHealthMonitor, get_health_monitor
)


class TestHealthCheckResult(unittest.TestCase):
    """Test HealthCheckResult dataclass"""
    
    def test_create_health_check_result(self):
        """Test creating a health check result"""
        result = HealthCheckResult(
            status=HealthStatus.HEALTHY,
            service_name="TestService",
            message="All systems operational"
        )
        
        self.assertEqual(result.status, HealthStatus.HEALTHY)
        self.assertEqual(result.service_name, "TestService")
        self.assertEqual(result.message, "All systems operational")
        self.assertTrue(result.is_healthy())
    
    def test_health_check_to_dict(self):
        """Test converting health check result to dictionary"""
        result = HealthCheckResult(
            status=HealthStatus.DEGRADED,
            service_name="TestService",
            message="Performance degraded",
            details={"cpu": "high"}
        )
        
        result_dict = result.to_dict()
        
        self.assertEqual(result_dict["status"], "degraded")
        self.assertEqual(result_dict["service_name"], "TestService")
        self.assertEqual(result_dict["message"], "Performance degraded")
        self.assertEqual(result_dict["details"]["cpu"], "high")
        self.assertIn("timestamp", result_dict)
    
    def test_unhealthy_status(self):
        """Test unhealthy status"""
        result = HealthCheckResult(
            status=HealthStatus.UNHEALTHY,
            service_name="TestService",
            message="Service failure"
        )
        
        self.assertFalse(result.is_healthy())


class TestReadinessCheckResult(unittest.TestCase):
    """Test ReadinessCheckResult dataclass"""
    
    def test_create_readiness_check_result(self):
        """Test creating a readiness check result"""
        result = ReadinessCheckResult(
            status=ReadinessStatus.READY,
            service_name="TestService",
            message="Ready to serve requests"
        )
        
        self.assertEqual(result.status, ReadinessStatus.READY)
        self.assertEqual(result.service_name, "TestService")
        self.assertTrue(result.is_ready())
    
    def test_not_ready_status(self):
        """Test not ready status"""
        result = ReadinessCheckResult(
            status=ReadinessStatus.NOT_READY,
            service_name="TestService",
            message="Dependencies not available",
            dependencies_ready=False
        )
        
        self.assertFalse(result.is_ready())
        self.assertFalse(result.dependencies_ready)
    
    def test_initializing_status(self):
        """Test initializing status"""
        result = ReadinessCheckResult(
            status=ReadinessStatus.INITIALIZING,
            service_name="TestService",
            message="Service is starting up"
        )
        
        self.assertFalse(result.is_ready())


class TestServiceHealthMonitor(unittest.TestCase):
    """Test ServiceHealthMonitor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = ServiceHealthMonitor()
    
    def test_register_health_check(self):
        """Test registering a health check"""
        result = HealthCheckResult(
            status=HealthStatus.HEALTHY,
            service_name="TestService",
            message="Healthy"
        )
        
        self.monitor.register_health_check("TestService", result)
        
        retrieved = self.monitor.get_health_status("TestService")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.status, HealthStatus.HEALTHY)
    
    def test_register_readiness_check(self):
        """Test registering a readiness check"""
        result = ReadinessCheckResult(
            status=ReadinessStatus.READY,
            service_name="TestService",
            message="Ready"
        )
        
        self.monitor.register_readiness_check("TestService", result)
        
        retrieved = self.monitor.get_readiness_status("TestService")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.status, ReadinessStatus.READY)
    
    def test_is_system_healthy_all_healthy(self):
        """Test system health when all services are healthy"""
        services = ["Service1", "Service2", "Service3"]
        
        for service_name in services:
            result = HealthCheckResult(
                status=HealthStatus.HEALTHY,
                service_name=service_name,
                message="Healthy"
            )
            self.monitor.register_health_check(service_name, result)
        
        self.assertTrue(self.monitor.is_system_healthy())
    
    def test_is_system_healthy_one_unhealthy(self):
        """Test system health when one service is unhealthy"""
        self.monitor.register_health_check(
            "Service1",
            HealthCheckResult(HealthStatus.HEALTHY, "Service1", "OK")
        )
        self.monitor.register_health_check(
            "Service2",
            HealthCheckResult(HealthStatus.UNHEALTHY, "Service2", "Failed")
        )
        
        self.assertFalse(self.monitor.is_system_healthy())
    
    def test_is_system_ready_all_ready(self):
        """Test system readiness when all services are ready"""
        services = ["Service1", "Service2"]
        
        for service_name in services:
            result = ReadinessCheckResult(
                status=ReadinessStatus.READY,
                service_name=service_name,
                message="Ready"
            )
            self.monitor.register_readiness_check(service_name, result)
        
        self.assertTrue(self.monitor.is_system_ready())
    
    def test_get_system_health_summary(self):
        """Test getting system health summary"""
        self.monitor.register_health_check(
            "Service1",
            HealthCheckResult(HealthStatus.HEALTHY, "Service1", "OK")
        )
        self.monitor.register_health_check(
            "Service2",
            HealthCheckResult(HealthStatus.DEGRADED, "Service2", "Slow")
        )
        
        summary = self.monitor.get_system_health_summary()
        
        self.assertIn("system_healthy", summary)
        self.assertIn("system_ready", summary)
        self.assertIn("healthy_services", summary)
        self.assertIn("total_services", summary)
        self.assertEqual(summary["total_services"], 2)
        self.assertEqual(summary["healthy_services"], 1)
    
    def test_get_all_health_checks(self):
        """Test getting all health checks"""
        self.monitor.register_health_check(
            "Service1",
            HealthCheckResult(HealthStatus.HEALTHY, "Service1", "OK")
        )
        self.monitor.register_health_check(
            "Service2",
            HealthCheckResult(HealthStatus.HEALTHY, "Service2", "OK")
        )
        
        all_checks = self.monitor.get_all_health_checks()
        
        self.assertEqual(len(all_checks), 2)
        self.assertIn("Service1", all_checks)
        self.assertIn("Service2", all_checks)


class TestGlobalHealthMonitor(unittest.TestCase):
    """Test global health monitor singleton"""
    
    def test_get_health_monitor_singleton(self):
        """Test that get_health_monitor returns the same instance"""
        monitor1 = get_health_monitor()
        monitor2 = get_health_monitor()
        
        self.assertIs(monitor1, monitor2)


if __name__ == "__main__":
    unittest.main()
