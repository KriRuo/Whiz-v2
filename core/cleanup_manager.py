#!/usr/bin/env python3
"""
core/cleanup_manager.py
-----------------------
Centralized resource cleanup management for Whiz Voice-to-Text Application.

This module provides a comprehensive cleanup system with ordered phases,
verification, and timeout protection to ensure proper resource management
during application shutdown.

Features:
    - Ordered cleanup phases
    - Verification of cleanup success
    - Timeout protection
    - Detailed logging and error reporting
    - Rollback capabilities for failed cleanup

Author: Whiz Development Team
Last Updated: December 2024
"""

import time
import threading
import logging
from typing import Dict, List, Callable, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from contextlib import contextmanager

from .logging_config import get_logger

logger = get_logger(__name__)

class CleanupPhase(Enum):
    """Cleanup phases in order of execution"""
    UI_WIDGETS = "ui_widgets"
    AUDIO_RESOURCES = "audio_resources"
    HOTKEY_RESOURCES = "hotkey_resources"
    MODEL_RESOURCES = "model_resources"
    FILE_RESOURCES = "file_resources"
    NETWORK_RESOURCES = "network_resources"
    SYSTEM_RESOURCES = "system_resources"
    FINAL_CLEANUP = "final_cleanup"

class CleanupStatus(Enum):
    """Status of cleanup operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"

@dataclass
class CleanupTask:
    """Represents a single cleanup task"""
    name: str
    phase: CleanupPhase
    cleanup_func: Callable[[], bool]
    verify_func: Optional[Callable[[], bool]] = None
    timeout_seconds: float = 10.0
    critical: bool = True
    rollback_func: Optional[Callable[[], None]] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class CleanupResult:
    """Result of a cleanup operation"""
    task_name: str
    status: CleanupStatus
    duration: float
    error: Optional[Exception] = None
    verification_passed: bool = True

class CleanupManager:
    """Manages ordered resource cleanup with verification"""
    
    def __init__(self, global_timeout: float = 60.0):
        """
        Initialize cleanup manager.
        
        Args:
            global_timeout: Maximum time for entire cleanup process
        """
        self.global_timeout = global_timeout
        self.tasks: Dict[str, CleanupTask] = {}
        self.results: Dict[str, CleanupResult] = {}
        self._cleanup_lock = threading.Lock()
        self._cleanup_started = False
        self._cleanup_completed = False
        
        logger.info(f"Cleanup manager initialized with {global_timeout}s timeout")
    
    def register_task(self, task: CleanupTask) -> None:
        """
        Register a cleanup task.
        
        Args:
            task: Cleanup task to register
        """
        with self._cleanup_lock:
            if self._cleanup_started:
                raise RuntimeError("Cannot register tasks after cleanup has started")
            
            self.tasks[task.name] = task
            self.results[task.name] = CleanupResult(
                task_name=task.name,
                status=CleanupStatus.PENDING,
                duration=0.0
            )
            
            logger.debug(f"Registered cleanup task: {task.name} (phase: {task.phase.value})")
    
    def register_simple_task(self, name: str, phase: CleanupPhase, 
                           cleanup_func: Callable[[], bool],
                           verify_func: Optional[Callable[[], bool]] = None,
                           timeout: float = 10.0, critical: bool = True) -> None:
        """
        Register a simple cleanup task.
        
        Args:
            name: Task name
            phase: Cleanup phase
            cleanup_func: Function to perform cleanup
            verify_func: Function to verify cleanup (optional)
            timeout: Task timeout in seconds
            critical: Whether task failure should stop cleanup
        """
        task = CleanupTask(
            name=name,
            phase=phase,
            cleanup_func=cleanup_func,
            verify_func=verify_func,
            timeout_seconds=timeout,
            critical=critical
        )
        self.register_task(task)
    
    def cleanup_all(self) -> Dict[str, CleanupResult]:
        """
        Execute all cleanup tasks in ordered phases.
        
        Returns:
            Dictionary of cleanup results
        """
        with self._cleanup_lock:
            if self._cleanup_started:
                logger.warning("Cleanup already started, returning existing results")
                return self.results.copy()
            
            self._cleanup_started = True
            cleanup_start_time = time.time()
            
            logger.info("Starting comprehensive cleanup process")
        
        try:
            # Execute cleanup phases in order
            phases = list(CleanupPhase)
            for phase in phases:
                phase_start_time = time.time()
                logger.info(f"Starting cleanup phase: {phase.value}")
                
                # Get tasks for this phase
                phase_tasks = [task for task in self.tasks.values() if task.phase == phase]
                
                if not phase_tasks:
                    logger.debug(f"No tasks for phase: {phase.value}")
                    continue
                
                # Execute tasks in this phase
                phase_success = self._execute_phase(phase_tasks)
                
                phase_duration = time.time() - phase_start_time
                logger.info(f"Phase {phase.value} completed in {phase_duration:.2f}s (success: {phase_success})")
                
                # Check global timeout
                total_duration = time.time() - cleanup_start_time
                if total_duration > self.global_timeout:
                    logger.error(f"Global cleanup timeout exceeded: {total_duration:.2f}s")
                    self._mark_timeout_tasks()
                    break
                
                # Stop if critical task failed
                if not phase_success:
                    critical_failed = any(
                        result.status == CleanupStatus.FAILED and self.tasks[result.task_name].critical
                        for result in self.results.values()
                    )
                    if critical_failed:
                        logger.error("Critical cleanup task failed, stopping cleanup process")
                        break
            
            total_duration = time.time() - cleanup_start_time
            logger.info(f"Cleanup process completed in {total_duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Unexpected error during cleanup: {e}")
        
        finally:
            with self._cleanup_lock:
                self._cleanup_completed = True
        
        return self.results.copy()
    
    def _execute_phase(self, tasks: List[CleanupTask]) -> bool:
        """Execute all tasks in a phase"""
        phase_success = True
        
        for task in tasks:
            # Check dependencies
            if not self._check_dependencies(task):
                logger.warning(f"Skipping task {task.name} due to failed dependencies")
                self.results[task.name].status = CleanupStatus.SKIPPED
                continue
            
            # Execute task
            task_success = self._execute_task(task)
            if not task_success and task.critical:
                phase_success = False
        
        return phase_success
    
    def _check_dependencies(self, task: CleanupTask) -> bool:
        """Check if task dependencies are satisfied"""
        for dep_name in task.dependencies:
            if dep_name not in self.results:
                logger.error(f"Dependency {dep_name} not found for task {task.name}")
                return False
            
            dep_result = self.results[dep_name]
            if dep_result.status not in [CleanupStatus.COMPLETED]:
                logger.warning(f"Dependency {dep_name} not completed for task {task.name}")
                return False
        
        return True
    
    def _execute_task(self, task: CleanupTask) -> bool:
        """Execute a single cleanup task"""
        logger.debug(f"Executing cleanup task: {task.name}")
        
        start_time = time.time()
        result = self.results[task.name]
        result.status = CleanupStatus.IN_PROGRESS
        
        try:
            # Execute cleanup with timeout
            cleanup_success = self._execute_with_timeout(
                task.cleanup_func, 
                task.timeout_seconds,
                f"cleanup_{task.name}"
            )
            
            if not cleanup_success:
                logger.error(f"Cleanup task {task.name} failed")
                result.status = CleanupStatus.FAILED
                return False
            
            # Verify cleanup if verification function provided
            if task.verify_func:
                verify_success = self._execute_with_timeout(
                    task.verify_func,
                    5.0,  # Shorter timeout for verification
                    f"verify_{task.name}"
                )
                
                if not verify_success:
                    logger.warning(f"Verification failed for task {task.name}")
                    result.verification_passed = False
            
            # Task completed successfully
            result.status = CleanupStatus.COMPLETED
            result.duration = time.time() - start_time
            
            logger.debug(f"Cleanup task {task.name} completed successfully in {result.duration:.2f}s")
            return True
            
        except Exception as e:
            result.status = CleanupStatus.FAILED
            result.error = e
            result.duration = time.time() - start_time
            
            logger.error(f"Cleanup task {task.name} failed with error: {e}")
            
            # Attempt rollback if available
            if task.rollback_func:
                try:
                    logger.info(f"Attempting rollback for task {task.name}")
                    task.rollback_func()
                except Exception as rollback_error:
                    logger.error(f"Rollback failed for task {task.name}: {rollback_error}")
            
            return False
    
    def _execute_with_timeout(self, func: Callable[[], bool], timeout: float, operation_name: str) -> bool:
        """Execute a function with timeout protection"""
        result = [False]
        exception = [None]
        
        def target():
            try:
                result[0] = func()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            logger.error(f"Operation {operation_name} timed out after {timeout}s")
            return False
        
        if exception[0]:
            logger.error(f"Operation {operation_name} failed: {exception[0]}")
            return False
        
        return result[0]
    
    def _mark_timeout_tasks(self):
        """Mark remaining tasks as timed out"""
        for task_name, result in self.results.items():
            if result.status == CleanupStatus.PENDING:
                result.status = CleanupStatus.TIMEOUT
                logger.warning(f"Task {task_name} marked as timed out")
    
    def get_cleanup_summary(self) -> Dict[str, Any]:
        """Get a summary of cleanup results"""
        total_tasks = len(self.results)
        completed_tasks = sum(1 for r in self.results.values() if r.status == CleanupStatus.COMPLETED)
        failed_tasks = sum(1 for r in self.results.values() if r.status == CleanupStatus.FAILED)
        timeout_tasks = sum(1 for r in self.results.values() if r.status == CleanupStatus.TIMEOUT)
        
        total_duration = sum(r.duration for r in self.results.values())
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'timeout_tasks': timeout_tasks,
            'success_rate': completed_tasks / total_tasks if total_tasks > 0 else 0,
            'total_duration': total_duration,
            'cleanup_started': self._cleanup_started,
            'cleanup_completed': self._cleanup_completed
        }
    
    def is_cleanup_complete(self) -> bool:
        """Check if cleanup process is complete"""
        return self._cleanup_completed
    
    @contextmanager
    def cleanup_context(self):
        """Context manager for automatic cleanup"""
        try:
            yield self
        finally:
            if not self.is_cleanup_complete():
                logger.info("Cleanup context exiting, performing cleanup")
                self.cleanup_all()

# Global cleanup manager instance
_global_cleanup_manager: Optional[CleanupManager] = None

def get_cleanup_manager() -> CleanupManager:
    """Get or create global cleanup manager instance"""
    global _global_cleanup_manager
    if _global_cleanup_manager is None:
        _global_cleanup_manager = CleanupManager()
    return _global_cleanup_manager

def register_cleanup_task(name: str, phase: CleanupPhase, cleanup_func: Callable[[], bool],
                        verify_func: Optional[Callable[[], bool]] = None,
                        timeout: float = 10.0, critical: bool = True) -> None:
    """Register a cleanup task with the global manager"""
    manager = get_cleanup_manager()
    manager.register_simple_task(name, phase, cleanup_func, verify_func, timeout, critical)

def perform_cleanup() -> Dict[str, CleanupResult]:
    """Perform cleanup using the global manager"""
    manager = get_cleanup_manager()
    return manager.cleanup_all()
