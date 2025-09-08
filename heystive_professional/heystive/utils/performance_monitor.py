"""
Performance Monitoring System
Non-intrusive performance monitoring overlay
Adds monitoring decorators without changing core processing logic
"""

import asyncio
import logging
import time
import functools
import threading
import psutil
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import json
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a function or component"""
    function_name: str
    component_name: str
    call_count: int
    total_time: float
    average_time: float
    min_time: float
    max_time: float
    last_call_time: float
    success_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    throughput_per_second: float
    timestamp: str

@dataclass
class ResourceSnapshot:
    """System resource snapshot"""
    timestamp: str
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_threads: int

class PerformanceMonitor:
    """
    Non-intrusive performance monitoring system
    Tracks function performance without modifying core logic
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.function_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "call_times": deque(maxlen=max_history),
            "call_count": 0,
            "total_time": 0.0,
            "success_count": 0,
            "failure_count": 0,
            "last_call": None,
            "memory_samples": deque(maxlen=100),
            "cpu_samples": deque(maxlen=100)
        })
        
        self.resource_history: deque = deque(maxlen=max_history)
        self.monitoring_active = False
        self.resource_thread = None
        self.lock = threading.Lock()
        
        # Performance thresholds
        self.thresholds = {
            "slow_function_ms": 1000,  # Functions slower than 1s
            "memory_warning_mb": 500,   # Memory usage warning
            "cpu_warning_percent": 80,  # CPU usage warning
            "low_throughput_ops": 1     # Operations per second warning
        }
    
    def monitor_performance(self, component_name: str = "Unknown", 
                          track_resources: bool = True):
        """
        Decorator to monitor function performance without changing logic
        Usage: @monitor_performance("TTS")
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self._monitor_sync_function(
                    func, component_name, track_resources, *args, **kwargs
                )
            return wrapper
        return decorator
    
    def monitor_performance_async(self, component_name: str = "Unknown",
                                track_resources: bool = True):
        """
        Async decorator to monitor function performance
        Usage: @monitor_performance_async("STT")
        """
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await self._monitor_async_function(
                    func, component_name, track_resources, *args, **kwargs
                )
            return wrapper
        return decorator
    
    def _monitor_sync_function(self, func: Callable, component_name: str,
                             track_resources: bool, *args, **kwargs):
        """Monitor synchronous function execution"""
        func_key = f"{component_name}::{func.__name__}"
        start_time = time.time()
        start_memory = None
        start_cpu = None
        
        if track_resources:
            try:
                process = psutil.Process()
                start_memory = process.memory_info().rss / 1024 / 1024  # MB
                start_cpu = process.cpu_percent()
            except:
                pass
        
        success = False
        result = None
        exception = None
        
        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            exception = e
            raise
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Record performance data
            self._record_function_call(
                func_key, execution_time, success, 
                start_memory, start_cpu, track_resources
            )
            
            # Log slow functions
            if execution_time * 1000 > self.thresholds["slow_function_ms"]:
                logger.warning(f"Slow function detected: {func_key} took {execution_time:.3f}s")
    
    async def _monitor_async_function(self, func: Callable, component_name: str,
                                    track_resources: bool, *args, **kwargs):
        """Monitor asynchronous function execution"""
        func_key = f"{component_name}::{func.__name__}"
        start_time = time.time()
        start_memory = None
        start_cpu = None
        
        if track_resources:
            try:
                process = psutil.Process()
                start_memory = process.memory_info().rss / 1024 / 1024  # MB
                start_cpu = process.cpu_percent()
            except:
                pass
        
        success = False
        result = None
        
        try:
            result = await func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            raise
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Record performance data
            self._record_function_call(
                func_key, execution_time, success,
                start_memory, start_cpu, track_resources
            )
            
            # Log slow functions
            if execution_time * 1000 > self.thresholds["slow_function_ms"]:
                logger.warning(f"Slow async function detected: {func_key} took {execution_time:.3f}s")
    
    def _record_function_call(self, func_key: str, execution_time: float,
                            success: bool, start_memory: Optional[float],
                            start_cpu: Optional[float], track_resources: bool):
        """Record function call performance data"""
        with self.lock:
            stats = self.function_stats[func_key]
            
            # Update call statistics
            stats["call_count"] += 1
            stats["total_time"] += execution_time
            stats["call_times"].append(execution_time)
            stats["last_call"] = datetime.now().isoformat()
            
            if success:
                stats["success_count"] += 1
            else:
                stats["failure_count"] += 1
            
            # Record resource usage
            if track_resources and start_memory is not None:
                try:
                    process = psutil.Process()
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    current_cpu = process.cpu_percent()
                    
                    stats["memory_samples"].append(current_memory)
                    stats["cpu_samples"].append(current_cpu)
                except:
                    pass
    
    def get_function_metrics(self, func_key: str) -> Optional[PerformanceMetrics]:
        """Get performance metrics for a specific function"""
        if func_key not in self.function_stats:
            return None
        
        stats = self.function_stats[func_key]
        call_times = list(stats["call_times"])
        
        if not call_times:
            return None
        
        # Calculate statistics
        avg_time = statistics.mean(call_times)
        min_time = min(call_times)
        max_time = max(call_times)
        success_rate = stats["success_count"] / stats["call_count"] if stats["call_count"] > 0 else 0
        
        # Calculate throughput (calls per second over last minute)
        recent_calls = [t for t in call_times if t > 0]  # Filter valid times
        throughput = len(recent_calls) / 60.0 if recent_calls else 0
        
        # Resource usage
        memory_usage = statistics.mean(stats["memory_samples"]) if stats["memory_samples"] else 0
        cpu_usage = statistics.mean(stats["cpu_samples"]) if stats["cpu_samples"] else 0
        
        # Parse component and function name
        parts = func_key.split("::")
        component_name = parts[0] if len(parts) > 1 else "Unknown"
        function_name = parts[1] if len(parts) > 1 else func_key
        
        return PerformanceMetrics(
            function_name=function_name,
            component_name=component_name,
            call_count=stats["call_count"],
            total_time=stats["total_time"],
            average_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            last_call_time=call_times[-1] if call_times else 0,
            success_rate=success_rate,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            throughput_per_second=throughput,
            timestamp=datetime.now().isoformat()
        )
    
    def get_component_metrics(self, component_name: str) -> Dict[str, PerformanceMetrics]:
        """Get all metrics for a component"""
        component_metrics = {}
        
        for func_key in self.function_stats:
            if func_key.startswith(f"{component_name}::"):
                metrics = self.get_function_metrics(func_key)
                if metrics:
                    component_metrics[metrics.function_name] = metrics
        
        return component_metrics
    
    def get_all_metrics(self) -> Dict[str, Dict[str, PerformanceMetrics]]:
        """Get all performance metrics organized by component"""
        all_metrics = defaultdict(dict)
        
        for func_key in self.function_stats:
            metrics = self.get_function_metrics(func_key)
            if metrics:
                all_metrics[metrics.component_name][metrics.function_name] = metrics
        
        return dict(all_metrics)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        total_functions = len(self.function_stats)
        total_calls = sum(stats["call_count"] for stats in self.function_stats.values())
        total_time = sum(stats["total_time"] for stats in self.function_stats.values())
        
        # Find slowest functions
        slowest_functions = []
        for func_key, stats in self.function_stats.items():
            if stats["call_times"]:
                avg_time = statistics.mean(stats["call_times"])
                slowest_functions.append((func_key, avg_time))
        
        slowest_functions.sort(key=lambda x: x[1], reverse=True)
        
        # Component breakdown
        component_stats = defaultdict(lambda: {"calls": 0, "time": 0.0, "functions": 0})
        for func_key, stats in self.function_stats.items():
            component = func_key.split("::")[0]
            component_stats[component]["calls"] += stats["call_count"]
            component_stats[component]["time"] += stats["total_time"]
            component_stats[component]["functions"] += 1
        
        return {
            "total_functions_monitored": total_functions,
            "total_function_calls": total_calls,
            "total_execution_time": total_time,
            "average_call_time": total_time / total_calls if total_calls > 0 else 0,
            "slowest_functions": slowest_functions[:10],  # Top 10 slowest
            "component_breakdown": dict(component_stats),
            "timestamp": datetime.now().isoformat()
        }
    
    def start_resource_monitoring(self, interval: float = 5.0):
        """Start background resource monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.resource_thread = threading.Thread(
            target=self._resource_monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.resource_thread.start()
        logger.info("Performance resource monitoring started")
    
    def stop_resource_monitoring(self):
        """Stop background resource monitoring"""
        self.monitoring_active = False
        if self.resource_thread:
            self.resource_thread.join(timeout=5)
        logger.info("Performance resource monitoring stopped")
    
    def _resource_monitoring_loop(self, interval: float):
        """Background resource monitoring loop"""
        while self.monitoring_active:
            try:
                snapshot = self._capture_resource_snapshot()
                with self.lock:
                    self.resource_history.append(snapshot)
                
                # Check for resource warnings
                if snapshot.memory_percent > 90:
                    logger.warning(f"High memory usage: {snapshot.memory_percent:.1f}%")
                if snapshot.cpu_percent > self.thresholds["cpu_warning_percent"]:
                    logger.warning(f"High CPU usage: {snapshot.cpu_percent:.1f}%")
                
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                time.sleep(interval)
    
    def _capture_resource_snapshot(self) -> ResourceSnapshot:
        """Capture current system resource snapshot"""
        try:
            # System-wide metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return ResourceSnapshot(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_mb=memory.used / 1024 / 1024,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                active_threads=threading.active_count()
            )
        except Exception as e:
            logger.error(f"Failed to capture resource snapshot: {e}")
            return ResourceSnapshot(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0, memory_mb=0, memory_percent=0,
                disk_usage_percent=0, network_bytes_sent=0,
                network_bytes_recv=0, active_threads=0
            )
    
    def get_resource_history(self, minutes: int = 60) -> List[ResourceSnapshot]:
        """Get resource history for specified minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            recent_snapshots = []
            for snapshot in self.resource_history:
                snapshot_time = datetime.fromisoformat(snapshot.timestamp)
                if snapshot_time >= cutoff_time:
                    recent_snapshots.append(snapshot)
        
        return recent_snapshots
    
    def export_metrics(self, filepath: str):
        """Export performance metrics to JSON file"""
        try:
            metrics_data = {
                "summary": self.get_performance_summary(),
                "function_metrics": {},
                "resource_history": [asdict(snapshot) for snapshot in self.resource_history]
            }
            
            # Export all function metrics
            for func_key in self.function_stats:
                metrics = self.get_function_metrics(func_key)
                if metrics:
                    metrics_data["function_metrics"][func_key] = asdict(metrics)
            
            # Write to file
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            logger.info(f"Performance metrics exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")

# Global performance monitor instance
global_performance_monitor = PerformanceMonitor()

# Convenience decorators
def monitor_performance(component: str = "Unknown", track_resources: bool = True):
    """Convenience decorator for performance monitoring"""
    return global_performance_monitor.monitor_performance(component, track_resources)

def monitor_performance_async(component: str = "Unknown", track_resources: bool = True):
    """Convenience decorator for async performance monitoring"""
    return global_performance_monitor.monitor_performance_async(component, track_resources)

# Convenience functions
def start_performance_monitoring(resource_interval: float = 5.0):
    """Start global performance monitoring"""
    global_performance_monitor.start_resource_monitoring(resource_interval)

def stop_performance_monitoring():
    """Stop global performance monitoring"""
    global_performance_monitor.stop_resource_monitoring()

def get_performance_summary():
    """Get global performance summary"""
    return global_performance_monitor.get_performance_summary()

def get_component_performance(component: str):
    """Get performance metrics for a component"""
    return global_performance_monitor.get_component_metrics(component)

def export_performance_metrics(filepath: str = "logs/performance_metrics.json"):
    """Export performance metrics to file"""
    global_performance_monitor.export_metrics(filepath)

# Context manager for temporary performance monitoring
class PerformanceContext:
    """Context manager for monitoring code blocks"""
    
    def __init__(self, name: str, component: str = "Unknown"):
        self.name = name
        self.component = component
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            func_key = f"{self.component}::{self.name}"
            success = exc_type is None
            
            global_performance_monitor._record_function_call(
                func_key, duration, success, None, None, False
            )

# Usage examples:
"""
# Pattern 1: Decorator for existing functions (no code changes needed)
@monitor_performance("TTS")
def existing_tts_function():
    # Original code unchanged
    pass

# Pattern 2: Async decorator
@monitor_performance_async("STT")
async def existing_stt_function():
    # Original code unchanged
    pass

# Pattern 3: Context manager for code blocks
with PerformanceContext("audio_processing", "TTS"):
    # Process audio
    pass

# Pattern 4: Manual monitoring points
start_performance_monitoring()  # Start background monitoring
# ... application runs ...
summary = get_performance_summary()  # Get metrics
export_performance_metrics()  # Export to file
stop_performance_monitoring()  # Stop monitoring
"""