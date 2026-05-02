#!/usr/bin/env python3
"""
tests/unit/test_service_metrics.py
----------------------------------
Unit tests for service metrics collection system.

Tests counters, gauges, histograms, and metrics aggregation.

Author: Whiz Development Team
Date: 2026-02-08
"""

import unittest
import time
from core.service_metrics import (
    Counter, Gauge, Histogram,
    ServiceMetrics, MetricsAggregator,
    get_metrics_aggregator
)


class TestCounter(unittest.TestCase):
    """Test Counter metric"""
    
    def test_create_counter(self):
        """Test creating a counter"""
        counter = Counter(name="test_counter")
        
        self.assertEqual(counter.name, "test_counter")
        self.assertEqual(counter.get_value(), 0)
    
    def test_increment_counter(self):
        """Test incrementing a counter"""
        counter = Counter(name="test_counter")
        
        counter.increment()
        self.assertEqual(counter.get_value(), 1)
        
        counter.increment(5)
        self.assertEqual(counter.get_value(), 6)
    
    def test_reset_counter(self):
        """Test resetting a counter"""
        counter = Counter(name="test_counter")
        counter.increment(10)
        
        counter.reset()
        self.assertEqual(counter.get_value(), 0)


class TestGauge(unittest.TestCase):
    """Test Gauge metric"""
    
    def test_create_gauge(self):
        """Test creating a gauge"""
        gauge = Gauge(name="test_gauge")
        
        self.assertEqual(gauge.name, "test_gauge")
        self.assertEqual(gauge.get_value(), 0.0)
    
    def test_set_gauge(self):
        """Test setting gauge value"""
        gauge = Gauge(name="test_gauge")
        
        gauge.set(42.5)
        self.assertEqual(gauge.get_value(), 42.5)
    
    def test_increment_gauge(self):
        """Test incrementing a gauge"""
        gauge = Gauge(name="test_gauge")
        gauge.set(10.0)
        
        gauge.increment(5.0)
        self.assertEqual(gauge.get_value(), 15.0)
    
    def test_decrement_gauge(self):
        """Test decrementing a gauge"""
        gauge = Gauge(name="test_gauge")
        gauge.set(10.0)
        
        gauge.decrement(3.0)
        self.assertEqual(gauge.get_value(), 7.0)


class TestHistogram(unittest.TestCase):
    """Test Histogram metric"""
    
    def test_create_histogram(self):
        """Test creating a histogram"""
        histogram = Histogram(name="test_histogram")
        
        self.assertEqual(histogram.name, "test_histogram")
        self.assertEqual(len(histogram.values), 0)
    
    def test_record_values(self):
        """Test recording values in histogram"""
        histogram = Histogram(name="test_histogram")
        
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        for value in values:
            histogram.record(value)
        
        self.assertEqual(len(histogram.values), len(values))
    
    def test_get_statistics(self):
        """Test getting histogram statistics"""
        histogram = Histogram(name="test_histogram")
        
        # Record a series of values
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        for value in values:
            histogram.record(value)
        
        stats = histogram.get_statistics()
        
        self.assertEqual(stats["count"], 10)
        self.assertEqual(stats["min"], 1.0)
        self.assertEqual(stats["max"], 10.0)
        self.assertEqual(stats["mean"], 5.5)
        self.assertGreater(stats["p50"], 0)
        self.assertGreater(stats["p95"], 0)
        self.assertGreater(stats["p99"], 0)
    
    def test_empty_histogram_statistics(self):
        """Test statistics for empty histogram"""
        histogram = Histogram(name="test_histogram")
        
        stats = histogram.get_statistics()
        
        self.assertEqual(stats["count"], 0)
        self.assertEqual(stats["min"], 0.0)
        self.assertEqual(stats["max"], 0.0)
    
    def test_max_size_limit(self):
        """Test that histogram respects max size"""
        histogram = Histogram(name="test_histogram", max_size=10)
        
        # Record more values than max_size
        for i in range(20):
            histogram.record(float(i))
        
        # Should only keep last 10 values
        self.assertEqual(len(histogram.values), 10)
        self.assertEqual(histogram.values[0], 10.0)  # First value after trimming


class TestServiceMetrics(unittest.TestCase):
    """Test ServiceMetrics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.metrics = ServiceMetrics("TestService")
    
    def test_create_service_metrics(self):
        """Test creating service metrics"""
        self.assertEqual(self.metrics.service_name, "TestService")
    
    def test_get_or_create_counter(self):
        """Test getting or creating a counter"""
        counter1 = self.metrics.counter("test_counter")
        counter2 = self.metrics.counter("test_counter")
        
        # Should return the same instance
        self.assertIs(counter1, counter2)
    
    def test_increment_counter_shortcut(self):
        """Test incrementing counter with shortcut method"""
        self.metrics.increment_counter("requests", 5)
        
        counter = self.metrics.counter("requests")
        self.assertEqual(counter.get_value(), 5)
    
    def test_get_or_create_gauge(self):
        """Test getting or creating a gauge"""
        gauge1 = self.metrics.gauge("test_gauge")
        gauge2 = self.metrics.gauge("test_gauge")
        
        # Should return the same instance
        self.assertIs(gauge1, gauge2)
    
    def test_set_gauge_shortcut(self):
        """Test setting gauge with shortcut method"""
        self.metrics.set_gauge("cpu_usage", 75.5)
        
        gauge = self.metrics.gauge("cpu_usage")
        self.assertEqual(gauge.get_value(), 75.5)
    
    def test_get_or_create_histogram(self):
        """Test getting or creating a histogram"""
        histogram1 = self.metrics.histogram("test_histogram")
        histogram2 = self.metrics.histogram("test_histogram")
        
        # Should return the same instance
        self.assertIs(histogram1, histogram2)
    
    def test_record_histogram_shortcut(self):
        """Test recording histogram with shortcut method"""
        self.metrics.record_histogram("latency", 50.0)
        self.metrics.record_histogram("latency", 75.0)
        
        histogram = self.metrics.histogram("latency")
        self.assertEqual(len(histogram.values), 2)
    
    def test_metrics_with_tags(self):
        """Test metrics with tags"""
        tags1 = {"endpoint": "/api/v1"}
        tags2 = {"endpoint": "/api/v2"}
        
        self.metrics.increment_counter("requests", tags=tags1)
        self.metrics.increment_counter("requests", tags=tags2)
        self.metrics.increment_counter("requests", tags=tags1)
        
        # Should be two separate counters
        counter1 = self.metrics.counter("requests", tags1)
        counter2 = self.metrics.counter("requests", tags2)
        
        self.assertEqual(counter1.get_value(), 2)
        self.assertEqual(counter2.get_value(), 1)
    
    def test_get_all_metrics(self):
        """Test getting all metrics"""
        self.metrics.increment_counter("requests", 10)
        self.metrics.set_gauge("cpu_usage", 50.0)
        self.metrics.record_histogram("latency", 100.0)
        
        all_metrics = self.metrics.get_all_metrics()
        
        self.assertIn("service", all_metrics)
        self.assertIn("timestamp", all_metrics)
        self.assertIn("uptime_seconds", all_metrics)
        self.assertIn("counters", all_metrics)
        self.assertIn("gauges", all_metrics)
        self.assertIn("histograms", all_metrics)
        
        self.assertEqual(all_metrics["service"], "TestService")
    
    def test_get_summary(self):
        """Test getting metrics summary"""
        self.metrics.increment_counter("requests")
        self.metrics.set_gauge("cpu_usage", 50.0)
        self.metrics.record_histogram("latency", 100.0)
        
        summary = self.metrics.get_summary()
        
        self.assertEqual(summary["service"], "TestService")
        self.assertEqual(summary["total_counters"], 1)
        self.assertEqual(summary["total_gauges"], 1)
        self.assertEqual(summary["total_histograms"], 1)
    
    def test_reset_all_metrics(self):
        """Test resetting all metrics"""
        self.metrics.increment_counter("requests", 10)
        self.metrics.set_gauge("cpu_usage", 50.0)
        self.metrics.record_histogram("latency", 100.0)
        
        self.metrics.reset_all()
        
        # Counters should be reset to 0
        counter = self.metrics.counter("requests")
        self.assertEqual(counter.get_value(), 0)
        
        # Gauges should be reset to 0
        gauge = self.metrics.gauge("cpu_usage")
        self.assertEqual(gauge.get_value(), 0.0)
        
        # Histograms should be cleared
        histogram = self.metrics.histogram("latency")
        self.assertEqual(len(histogram.values), 0)


class TestMetricsAggregator(unittest.TestCase):
    """Test MetricsAggregator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.aggregator = MetricsAggregator()
    
    def test_register_service(self):
        """Test registering a service"""
        metrics = self.aggregator.register_service("Service1")
        
        self.assertIsInstance(metrics, ServiceMetrics)
        self.assertEqual(metrics.service_name, "Service1")
    
    def test_register_same_service_twice(self):
        """Test registering the same service twice returns same instance"""
        metrics1 = self.aggregator.register_service("Service1")
        metrics2 = self.aggregator.register_service("Service1")
        
        self.assertIs(metrics1, metrics2)
    
    def test_get_service_metrics(self):
        """Test getting metrics for a service"""
        self.aggregator.register_service("Service1")
        
        metrics = self.aggregator.get_service_metrics("Service1")
        
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.service_name, "Service1")
    
    def test_get_nonexistent_service_metrics(self):
        """Test getting metrics for non-existent service"""
        metrics = self.aggregator.get_service_metrics("NonExistent")
        
        self.assertIsNone(metrics)
    
    def test_get_all_metrics(self):
        """Test getting all service metrics"""
        # Register multiple services
        self.aggregator.register_service("Service1")
        self.aggregator.register_service("Service2")
        
        # Add some metrics
        metrics1 = self.aggregator.get_service_metrics("Service1")
        metrics1.increment_counter("requests", 10)
        
        metrics2 = self.aggregator.get_service_metrics("Service2")
        metrics2.set_gauge("cpu_usage", 50.0)
        
        all_metrics = self.aggregator.get_all_metrics()
        
        self.assertIn("timestamp", all_metrics)
        self.assertIn("services", all_metrics)
        self.assertIn("Service1", all_metrics["services"])
        self.assertIn("Service2", all_metrics["services"])
    
    def test_get_summary(self):
        """Test getting aggregated summary"""
        self.aggregator.register_service("Service1")
        self.aggregator.register_service("Service2")
        
        summary = self.aggregator.get_summary()
        
        self.assertEqual(summary["total_services"], 2)
        self.assertIn("services", summary)


class TestGlobalMetricsAggregator(unittest.TestCase):
    """Test global metrics aggregator singleton"""
    
    def test_get_metrics_aggregator_singleton(self):
        """Test that get_metrics_aggregator returns the same instance"""
        aggregator1 = get_metrics_aggregator()
        aggregator2 = get_metrics_aggregator()
        
        self.assertIs(aggregator1, aggregator2)


if __name__ == "__main__":
    unittest.main()
