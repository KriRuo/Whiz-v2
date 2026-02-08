#!/usr/bin/env python3
"""
core/service_metrics.py
-----------------------
Metrics collection system for backend services.

Provides structured metrics collection for monitoring service performance,
resource usage, and operational statistics.

Author: Whiz Development Team
Date: 2026-02-08
Version: 2.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """A single metric data point"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "unit": self.unit
        }


@dataclass
class Counter:
    """Counter metric that only increases"""
    name: str
    value: int = 0
    tags: Dict[str, str] = field(default_factory=dict)
    
    def increment(self, amount: int = 1) -> None:
        """Increment counter"""
        self.value += amount
    
    def get_value(self) -> int:
        """Get current value"""
        return self.value
    
    def reset(self) -> None:
        """Reset counter to zero"""
        self.value = 0


@dataclass
class Gauge:
    """Gauge metric that can go up or down"""
    name: str
    value: float = 0.0
    tags: Dict[str, str] = field(default_factory=dict)
    
    def set(self, value: float) -> None:
        """Set gauge value"""
        self.value = value
    
    def increment(self, amount: float = 1.0) -> None:
        """Increment gauge"""
        self.value += amount
    
    def decrement(self, amount: float = 1.0) -> None:
        """Decrement gauge"""
        self.value -= amount
    
    def get_value(self) -> float:
        """Get current value"""
        return self.value


@dataclass
class Histogram:
    """Histogram metric for tracking distributions"""
    name: str
    values: List[float] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    max_size: int = 1000  # Keep last 1000 values
    
    def record(self, value: float) -> None:
        """Record a value"""
        self.values.append(value)
        # Keep only recent values
        if len(self.values) > self.max_size:
            self.values = self.values[-self.max_size:]
    
    def get_statistics(self) -> Dict[str, float]:
        """Get statistical summary"""
        if not self.values:
            return {
                "count": 0,
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "p50": 0.0,
                "p95": 0.0,
                "p99": 0.0
            }
        
        sorted_values = sorted(self.values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": sum(sorted_values) / count,
            "p50": sorted_values[int(count * 0.50)],
            "p95": sorted_values[int(count * 0.95)],
            "p99": sorted_values[int(count * 0.99)]
        }


class ServiceMetrics:
    """
    Metrics collection system for backend services.
    
    Provides structured metrics collection for:
    - Counters (monotonically increasing values)
    - Gauges (values that can go up or down)
    - Histograms (distributions of values)
    """
    
    def __init__(self, service_name: str):
        """
        Initialize metrics collector.
        
        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}
        self._lock = threading.Lock()
        self._start_time = datetime.now()
        
        logger.info(f"ServiceMetrics initialized for {service_name}")
    
    # Counter methods
    
    def counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> Counter:
        """
        Get or create a counter.
        
        Args:
            name: Counter name
            tags: Optional tags for categorization
            
        Returns:
            Counter instance
        """
        with self._lock:
            key = self._make_key(name, tags)
            if key not in self._counters:
                self._counters[key] = Counter(name, tags=tags or {})
            return self._counters[key]
    
    def increment_counter(self, name: str, amount: int = 1, 
                         tags: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter.
        
        Args:
            name: Counter name
            amount: Amount to increment
            tags: Optional tags
        """
        self.counter(name, tags).increment(amount)
    
    # Gauge methods
    
    def gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> Gauge:
        """
        Get or create a gauge.
        
        Args:
            name: Gauge name
            tags: Optional tags for categorization
            
        Returns:
            Gauge instance
        """
        with self._lock:
            key = self._make_key(name, tags)
            if key not in self._gauges:
                self._gauges[key] = Gauge(name, tags=tags or {})
            return self._gauges[key]
    
    def set_gauge(self, name: str, value: float, 
                  tags: Optional[Dict[str, str]] = None) -> None:
        """
        Set a gauge value.
        
        Args:
            name: Gauge name
            value: Value to set
            tags: Optional tags
        """
        self.gauge(name, tags).set(value)
    
    # Histogram methods
    
    def histogram(self, name: str, tags: Optional[Dict[str, str]] = None) -> Histogram:
        """
        Get or create a histogram.
        
        Args:
            name: Histogram name
            tags: Optional tags for categorization
            
        Returns:
            Histogram instance
        """
        with self._lock:
            key = self._make_key(name, tags)
            if key not in self._histograms:
                self._histograms[key] = Histogram(name, tags=tags or {})
            return self._histograms[key]
    
    def record_histogram(self, name: str, value: float, 
                        tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a value in a histogram.
        
        Args:
            name: Histogram name
            value: Value to record
            tags: Optional tags
        """
        self.histogram(name, tags).record(value)
    
    # Utility methods
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a unique key for a metric"""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics as a dictionary.
        
        Returns:
            Dictionary containing all metrics
        """
        with self._lock:
            uptime = (datetime.now() - self._start_time).total_seconds()
            
            return {
                "service": self.service_name,
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": uptime,
                "counters": {
                    name: counter.get_value() 
                    for name, counter in self._counters.items()
                },
                "gauges": {
                    name: gauge.get_value() 
                    for name, gauge in self._gauges.items()
                },
                "histograms": {
                    name: hist.get_statistics() 
                    for name, hist in self._histograms.items()
                }
            }
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of key metrics.
        
        Returns:
            Dictionary with summary statistics
        """
        metrics = self.get_all_metrics()
        
        return {
            "service": self.service_name,
            "timestamp": metrics["timestamp"],
            "uptime_seconds": metrics["uptime_seconds"],
            "total_counters": len(self._counters),
            "total_gauges": len(self._gauges),
            "total_histograms": len(self._histograms)
        }
    
    def reset_all(self) -> None:
        """Reset all metrics"""
        with self._lock:
            for counter in self._counters.values():
                counter.reset()
            for gauge in self._gauges.values():
                gauge.set(0.0)
            self._histograms.clear()
            self._start_time = datetime.now()
        
        logger.info(f"All metrics reset for {self.service_name}")


class MetricsAggregator:
    """
    Aggregate metrics from multiple services.
    """
    
    def __init__(self):
        """Initialize metrics aggregator"""
        self._service_metrics: Dict[str, ServiceMetrics] = {}
        self._lock = threading.Lock()
        logger.info("MetricsAggregator initialized")
    
    def register_service(self, service_name: str) -> ServiceMetrics:
        """
        Register a service for metrics collection.
        
        Args:
            service_name: Name of the service
            
        Returns:
            ServiceMetrics instance for the service
        """
        with self._lock:
            if service_name not in self._service_metrics:
                self._service_metrics[service_name] = ServiceMetrics(service_name)
                logger.info(f"Service registered for metrics: {service_name}")
            return self._service_metrics[service_name]
    
    def get_service_metrics(self, service_name: str) -> Optional[ServiceMetrics]:
        """
        Get metrics for a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            ServiceMetrics instance or None
        """
        return self._service_metrics.get(service_name)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from all services.
        
        Returns:
            Dictionary with all service metrics
        """
        with self._lock:
            return {
                "timestamp": datetime.now().isoformat(),
                "services": {
                    name: metrics.get_all_metrics()
                    for name, metrics in self._service_metrics.items()
                }
            }
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all service metrics.
        
        Returns:
            Dictionary with summary information
        """
        with self._lock:
            return {
                "timestamp": datetime.now().isoformat(),
                "total_services": len(self._service_metrics),
                "services": {
                    name: metrics.get_summary()
                    for name, metrics in self._service_metrics.items()
                }
            }


# Global metrics aggregator
_metrics_aggregator: Optional[MetricsAggregator] = None


def get_metrics_aggregator() -> MetricsAggregator:
    """
    Get the global metrics aggregator instance.
    
    Returns:
        MetricsAggregator instance
    """
    global _metrics_aggregator
    if _metrics_aggregator is None:
        _metrics_aggregator = MetricsAggregator()
    return _metrics_aggregator
