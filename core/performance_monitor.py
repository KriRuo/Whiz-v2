#!/usr/bin/env python3
"""
core/performance_monitor.py
--------------------------
Performance monitoring and profiling tools for Whiz Voice-to-Text Application.

This module provides performance monitoring capabilities to help identify
bottlenecks and optimize application performance.

Features:
    - CPU and memory usage monitoring
    - Transcription speed measurement
    - Model loading time tracking
    - Audio processing performance metrics
    - Performance reporting and logging

Dependencies:
    - psutil: System and process monitoring
    - time: Timing measurements
    - threading: Thread-safe operations
    - typing: Type hints

Example:
    Basic usage:
        from core.performance_monitor import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        # ... perform operations ...
        
        metrics = monitor.get_metrics()
        monitor.stop_monitoring()

Author: Whiz Development Team
Last Updated: October 10, 2025
"""

import time
import threading
try:
    import psutil  # Optional dependency
    _PSUTIL_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency fallback
    psutil = None
    _PSUTIL_AVAILABLE = False
from typing import Dict, List, Optional, Callable
from datetime import datetime
from contextlib import contextmanager

from .logging_config import get_logger

logger = get_logger(__name__)


class PerformanceMonitor:
    """
    Performance monitoring and profiling tool.
    
    Tracks CPU usage, memory consumption, transcription speed,
    and other performance metrics to help identify bottlenecks.
    """
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.monitoring = False
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'transcription_times': [],
            'model_load_times': [],
            'audio_processing_times': [],
            'startup_time': None,
            'total_transcriptions': 0,
            'average_transcription_time': 0.0
        }
        
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._start_time = time.time()
        
        # Performance thresholds
        self.thresholds = {
            'cpu_usage_warning': 80.0,  # CPU usage percentage
            'memory_usage_warning': 500 * 1024 * 1024,  # 500MB in bytes
            'transcription_time_warning': 5.0,  # seconds
            'model_load_time_warning': 10.0  # seconds
        }
        
        logger.info("Performance monitor initialized")
    
    def start_monitoring(self, interval: float = 1.0):
        """
        Start continuous performance monitoring.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring:
            logger.warning("Performance monitoring already active")
            return
        
        self.monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info(f"Performance monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        
        logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        if not _PSUTIL_AVAILABLE:
            # Psutil not available; skip monitoring loop gracefully
            logger.info("psutil not available; performance monitoring disabled")
            return

        process = psutil.Process()
        
        while self.monitoring:
            try:
                # Get current metrics
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
                
                with self._lock:
                    self.metrics['cpu_usage'].append(cpu_percent)
                    self.metrics['memory_usage'].append(memory_mb)
                    
                    # Keep only last 100 measurements to prevent memory growth
                    if len(self.metrics['cpu_usage']) > 100:
                        self.metrics['cpu_usage'] = self.metrics['cpu_usage'][-100:]
                    if len(self.metrics['memory_usage']) > 100:
                        self.metrics['memory_usage'] = self.metrics['memory_usage'][-100:]
                
                # Check for performance warnings
                self._check_performance_warnings(cpu_percent, memory_mb)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                time.sleep(interval)
    
    def _check_performance_warnings(self, cpu_percent: float, memory_mb: float):
        """Check for performance warnings and log them."""
        if cpu_percent > self.thresholds['cpu_usage_warning']:
            logger.warning(f"High CPU usage detected: {cpu_percent:.1f}%")
        
        memory_bytes = memory_mb * 1024 * 1024
        if memory_bytes > self.thresholds['memory_usage_warning']:
            logger.warning(f"High memory usage detected: {memory_mb:.1f}MB")
    
    @contextmanager
    def time_operation(self, operation_name: str):
        """
        Context manager for timing operations.
        
        Args:
            operation_name: Name of the operation being timed
            
        Example:
            with monitor.time_operation("transcription"):
                result = transcribe_audio(audio_data)
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_operation_time(operation_name, duration)
    
    def record_operation_time(self, operation_name: str, duration: float):
        """
        Record the duration of an operation.
        
        Args:
            operation_name: Name of the operation
            duration: Duration in seconds
        """
        with self._lock:
            if operation_name == "transcription":
                self.metrics['transcription_times'].append(duration)
                self.metrics['total_transcriptions'] += 1
                
                # Update average transcription time
                times = self.metrics['transcription_times']
                self.metrics['average_transcription_time'] = sum(times) / len(times)
                
                # Keep only last 50 transcription times
                if len(times) > 50:
                    self.metrics['transcription_times'] = times[-50:]
                
                # Check for slow transcription warning
                if duration > self.thresholds['transcription_time_warning']:
                    logger.warning(f"Slow transcription detected: {duration:.2f}s")
                    
            elif operation_name == "model_loading":
                self.metrics['model_load_times'].append(duration)
                
                # Check for slow model loading warning
                if duration > self.thresholds['model_load_time_warning']:
                    logger.warning(f"Slow model loading detected: {duration:.2f}s")
                    
            elif operation_name == "audio_processing":
                self.metrics['audio_processing_times'].append(duration)
                
                # Keep only last 100 audio processing times
                if len(self.metrics['audio_processing_times']) > 100:
                    self.metrics['audio_processing_times'] = self.metrics['audio_processing_times'][-100:]
    
    def record_startup_time(self):
        """Record the application startup time."""
        startup_time = time.time() - self._start_time
        self.metrics['startup_time'] = startup_time
        logger.info(f"Application startup time: {startup_time:.2f}s")
    
    def get_metrics(self) -> Dict:
        """
        Get current performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        with self._lock:
            # Calculate current averages
            current_cpu = self.metrics['cpu_usage'][-10:] if self.metrics['cpu_usage'] else [0]
            current_memory = self.metrics['memory_usage'][-10:] if self.metrics['memory_usage'] else [0]
            
            return {
                'current_cpu_usage': sum(current_cpu) / len(current_cpu) if current_cpu else 0,
                'current_memory_usage_mb': sum(current_memory) / len(current_memory) if current_memory else 0,
                'max_cpu_usage': max(self.metrics['cpu_usage']) if self.metrics['cpu_usage'] else 0,
                'max_memory_usage_mb': max(self.metrics['memory_usage']) if self.metrics['memory_usage'] else 0,
                'total_transcriptions': self.metrics['total_transcriptions'],
                'average_transcription_time': self.metrics['average_transcription_time'],
                'startup_time': self.metrics['startup_time'],
                'uptime': time.time() - self._start_time,
                'monitoring_active': self.monitoring
            }
    
    def get_performance_report(self) -> str:
        """
        Generate a detailed performance report.
        
        Returns:
            Formatted performance report string
        """
        metrics = self.get_metrics()
        
        report = f"""
=== Whiz Performance Report ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

System Performance:
  Current CPU Usage: {metrics['current_cpu_usage']:.1f}%
  Peak CPU Usage: {metrics['max_cpu_usage']:.1f}%
  Current Memory Usage: {metrics['current_memory_usage_mb']:.1f}MB
  Peak Memory Usage: {metrics['max_memory_usage_mb']:.1f}MB

Transcription Performance:
  Total Transcriptions: {metrics['total_transcriptions']}
  Average Transcription Time: {metrics['average_transcription_time']:.2f}s
  
Application Performance:
  Startup Time: {metrics['startup_time']:.2f}s (if recorded)
  Uptime: {metrics['uptime']:.1f}s
  Monitoring Active: {metrics['monitoring_active']}

Performance Recommendations:
"""
        
        # Add recommendations based on metrics
        if metrics['current_cpu_usage'] > 70:
            report += "  - Consider reducing UI animation frequency\n"
        
        if metrics['current_memory_usage_mb'] > 400:
            report += "  - Consider using smaller Whisper model\n"
        
        if metrics['average_transcription_time'] > 3.0:
            report += "  - Consider enabling speed optimizations\n"
        
        if metrics['startup_time'] and metrics['startup_time'] > 5.0:
            report += "  - Consider implementing lazy loading\n"
        
        return report
    
    def log_performance_summary(self):
        """Log a performance summary to the logger."""
        metrics = self.get_metrics()
        
        logger.info("=== Performance Summary ===")
        logger.info(f"CPU Usage: {metrics['current_cpu_usage']:.1f}% (peak: {metrics['max_cpu_usage']:.1f}%)")
        logger.info(f"Memory Usage: {metrics['current_memory_usage_mb']:.1f}MB (peak: {metrics['max_memory_usage_mb']:.1f}MB)")
        logger.info(f"Transcriptions: {metrics['total_transcriptions']} (avg: {metrics['average_transcription_time']:.2f}s)")
        logger.info(f"Uptime: {metrics['uptime']:.1f}s")


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global performance monitor instance.
    
    Returns:
        PerformanceMonitor instance
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def start_performance_monitoring(interval: float = 1.0):
    """Start global performance monitoring."""
    monitor = get_performance_monitor()
    monitor.start_monitoring(interval)


def stop_performance_monitoring():
    """Stop global performance monitoring."""
    monitor = get_performance_monitor()
    monitor.stop_monitoring()


def log_performance_report():
    """Log a performance report."""
    monitor = get_performance_monitor()
    monitor.log_performance_summary()
