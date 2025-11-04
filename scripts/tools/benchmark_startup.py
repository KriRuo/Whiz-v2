#!/usr/bin/env python3
"""
benchmark_startup.py
--------------------
Performance benchmark script for Whiz startup optimization.

This script measures startup time improvements from the optimizations:
- Audio device caching
- Splash screen timing improvements
- Faster fade animations

Usage:
    python benchmark_startup.py
"""

import time
import sys
import subprocess
import os
from pathlib import Path
from typing import List, Tuple

# Change to project root directory (parent of scripts/tools/)
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))


def measure_startup_time(script_name: str, iterations: int = 3) -> Tuple[float, List[float]]:
    """
    Measure average startup time for a given script.
    
    Args:
        script_name: Name of the script to measure
        iterations: Number of iterations to average
        
    Returns:
        Tuple of (average_time, list_of_times)
    """
    times = []
    
    print(f"Measuring {script_name} startup time ({iterations} iterations)...")
    
    for i in range(iterations):
        print(f"  Run {i+1}/{iterations}...", end=" ", flush=True)
        
        start_time = time.time()
        
        try:
            # Run the script and wait for it to start
            proc = subprocess.Popen(
                [sys.executable, script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for the process to start and then terminate it
            # We'll look for specific log messages to determine when startup is complete
            timeout = 10  # 10 second timeout
            elapsed = 0
            
            while elapsed < timeout:
                if proc.poll() is not None:
                    # Process finished
                    break
                
                time.sleep(0.1)
                elapsed += 0.1
                
                # Check if we see the "Application started successfully!" message
                try:
                    stdout, stderr = proc.communicate(timeout=0.1)
                    if "Application started successfully!" in stdout:
                        break
                except subprocess.TimeoutExpired:
                    continue
            
            end_time = time.time()
            
            # Terminate the process if it's still running
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
            
            run_time = end_time - start_time
            times.append(run_time)
            print(f"{run_time:.2f}s")
            
        except Exception as e:
            print(f"Error: {e}")
            continue
        
        # Cool down between runs
        if i < iterations - 1:
            time.sleep(2)
    
    if times:
        avg_time = sum(times) / len(times)
        return avg_time, times
    else:
        return 0.0, []


def measure_import_time() -> float:
    """Measure the time to import key modules."""
    print("Measuring import times...")
    
    # Test PyQt5 import
    start = time.time()
    try:
        from PyQt5.QtWidgets import QApplication
        pyqt_time = time.time() - start
        print(f"  PyQt5 import: {pyqt_time:.3f}s")
    except ImportError as e:
        print(f"  PyQt5 import failed: {e}")
        pyqt_time = 0
    
    # Test core modules import
    start = time.time()
    try:
        from core.audio_manager import AudioManager
        from core.settings_manager import SettingsManager
        core_time = time.time() - start
        print(f"  Core modules import: {core_time:.3f}s")
    except ImportError as e:
        print(f"  Core modules import failed: {e}")
        core_time = 0
    
    return pyqt_time + core_time


def run_benchmark():
    """Run the complete startup benchmark."""
    print("=" * 60)
    print("Whiz Startup Performance Benchmark")
    print("=" * 60)
    print()
    
    # Measure import times
    import_time = measure_import_time()
    print(f"Total import time: {import_time:.3f}s")
    print()
    
    # Check if scripts exist
    scripts_to_test = [
        ("main.py", "Direct startup (baseline)"),
        ("main_with_splash.py", "Splash screen startup (optimized)")
    ]
    
    results = {}
    
    for script_name, description in scripts_to_test:
        if not os.path.exists(script_name):
            print(f"⚠️  {script_name} not found, skipping...")
            continue
        
        print(f"Testing: {description}")
        print("-" * 40)
        
        avg_time, times = measure_startup_time(script_name, iterations=3)
        results[script_name] = {
            'avg': avg_time,
            'times': times,
            'description': description
        }
        
        print(f"Average startup time: {avg_time:.2f}s")
        print(f"Individual times: {[f'{t:.2f}s' for t in times]}")
        print()
    
    # Calculate improvements
    if 'main.py' in results and 'main_with_splash.py' in results:
        baseline = results['main.py']['avg']
        optimized = results['main_with_splash.py']['avg']
        
        if baseline > 0:
            improvement = ((baseline - optimized) / baseline) * 100
            print("=" * 60)
            print("PERFORMANCE COMPARISON")
            print("=" * 60)
            print(f"Baseline (main.py):           {baseline:.2f}s")
            print(f"Optimized (main_with_splash): {optimized:.2f}s")
            print(f"Improvement:                  {improvement:.1f}% faster")
            print()
            
            if improvement > 0:
                print("✅ Optimization successful!")
            else:
                print("⚠️  No improvement detected (may need more iterations)")
        else:
            print("⚠️  Could not calculate improvement (baseline time is 0)")
    
    print()
    print("Benchmark complete!")
    print()
    print("Note: This benchmark measures time to 'Application started successfully!'")
    print("The actual perceived improvement may be higher due to splash screen masking.")


def test_audio_cache_performance():
    """Test audio device caching performance specifically."""
    print("Testing audio device caching performance...")
    
    try:
        from core.audio_manager import AudioManager
        
        # Test without cache (first run)
        print("  First run (no cache)...")
        start = time.time()
        manager1 = AudioManager()
        first_run_time = time.time() - start
        print(f"    Time: {first_run_time:.3f}s")
        
        # Test with cache (second run)
        print("  Second run (with cache)...")
        start = time.time()
        manager2 = AudioManager()
        second_run_time = time.time() - start
        print(f"    Time: {second_run_time:.3f}s")
        
        if first_run_time > 0:
            cache_improvement = ((first_run_time - second_run_time) / first_run_time) * 100
            print(f"  Cache improvement: {cache_improvement:.1f}%")
        
    except Exception as e:
        print(f"  Audio cache test failed: {e}")


if __name__ == "__main__":
    print("Starting Whiz startup performance benchmark...")
    print("This will test the optimizations implemented for faster startup.")
    print()
    
    # Test audio caching specifically
    test_audio_cache_performance()
    print()
    
    # Run main benchmark
    run_benchmark()
    
    print()
    print("For manual testing:")
    print("1. Time from double-click to window appearance")
    print("2. Time from window appearance to first recording ready")
    print("3. Check console logs for 'Using cached audio device' message")
