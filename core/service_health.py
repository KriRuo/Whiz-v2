#!/usr/bin/env python3
"""
core/service_health.py
----------------------
Health check system for backend services.

Provides health monitoring, readiness checks, and liveness probes
for TranscriptionService and RecordingService.

Author: Whiz Development Team
Date: 2026-02-08
Version: 2.0.0
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List, Any
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ReadinessStatus(Enum):
    """Service readiness status"""
    READY = "ready"
    NOT_READY = "not_ready"
    INITIALIZING = "initializing"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    status: HealthStatus
    service_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "status": self.status.value,
            "service_name": self.service_name,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "details": self.details
        }
    
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self.status == HealthStatus.HEALTHY


@dataclass
class ReadinessCheckResult:
    """Result of a readiness check"""
    status: ReadinessStatus
    service_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    message: str = ""
    dependencies_ready: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "status": self.status.value,
            "service_name": self.service_name,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "dependencies_ready": self.dependencies_ready
        }
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self.status == ReadinessStatus.READY


class ServiceHealthMonitor:
    """
    Health monitoring for backend services.
    
    Provides health checks, readiness checks, and liveness probes.
    """
    
    def __init__(self):
        """Initialize health monitor"""
        self._health_checks: Dict[str, HealthCheckResult] = {}
        self._readiness_checks: Dict[str, ReadinessCheckResult] = {}
        logger.info("ServiceHealthMonitor initialized")
    
    def register_health_check(self, service_name: str, result: HealthCheckResult) -> None:
        """
        Register a health check result.
        
        Args:
            service_name: Name of the service
            result: Health check result
        """
        self._health_checks[service_name] = result
        logger.debug(f"Health check registered for {service_name}: {result.status.value}")
    
    def register_readiness_check(self, service_name: str, result: ReadinessCheckResult) -> None:
        """
        Register a readiness check result.
        
        Args:
            service_name: Name of the service
            result: Readiness check result
        """
        self._readiness_checks[service_name] = result
        logger.debug(f"Readiness check registered for {service_name}: {result.status.value}")
    
    def get_health_status(self, service_name: str) -> Optional[HealthCheckResult]:
        """
        Get health status for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Health check result or None if not registered
        """
        return self._health_checks.get(service_name)
    
    def get_readiness_status(self, service_name: str) -> Optional[ReadinessCheckResult]:
        """
        Get readiness status for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Readiness check result or None if not registered
        """
        return self._readiness_checks.get(service_name)
    
    def get_all_health_checks(self) -> Dict[str, HealthCheckResult]:
        """Get all health check results"""
        return self._health_checks.copy()
    
    def get_all_readiness_checks(self) -> Dict[str, ReadinessCheckResult]:
        """Get all readiness check results"""
        return self._readiness_checks.copy()
    
    def is_system_healthy(self) -> bool:
        """
        Check if all services are healthy.
        
        Returns:
            True if all services are healthy, False otherwise
        """
        if not self._health_checks:
            return False
        
        return all(check.is_healthy() for check in self._health_checks.values())
    
    def is_system_ready(self) -> bool:
        """
        Check if all services are ready.
        
        Returns:
            True if all services are ready, False otherwise
        """
        if not self._readiness_checks:
            return False
        
        return all(check.is_ready() for check in self._readiness_checks.values())
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """
        Get overall system health summary.
        
        Returns:
            Dictionary with system health information
        """
        healthy_count = sum(1 for check in self._health_checks.values() if check.is_healthy())
        total_count = len(self._health_checks)
        
        return {
            "system_healthy": self.is_system_healthy(),
            "system_ready": self.is_system_ready(),
            "healthy_services": healthy_count,
            "total_services": total_count,
            "timestamp": datetime.now().isoformat(),
            "services": {
                name: check.to_dict() 
                for name, check in self._health_checks.items()
            }
        }


# Global health monitor instance
_health_monitor: Optional[ServiceHealthMonitor] = None


def get_health_monitor() -> ServiceHealthMonitor:
    """
    Get the global health monitor instance.
    
    Returns:
        ServiceHealthMonitor instance
    """
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = ServiceHealthMonitor()
    return _health_monitor
