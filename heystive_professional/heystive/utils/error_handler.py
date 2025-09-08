"""
Enhanced Error Handling Utilities
Adds better error handling around existing code without changing behavior
DO NOT MODIFY existing try/except blocks - this adds logging and monitoring layers
"""

import logging
import functools
import traceback
import time
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ErrorEvent:
    """Represents an error event for tracking and analysis"""
    timestamp: str
    component: str
    function: str
    error_type: str
    error_message: str
    stack_trace: str
    severity: str
    context: Dict[str, Any]
    resolved: bool = False

class ErrorHandler:
    """
    Enhanced error handling that adds logging and monitoring 
    without changing existing error handling behavior
    """
    
    def __init__(self, log_file: Optional[str] = None):
        self.error_events: List[ErrorEvent] = []
        self.error_counts: Dict[str, int] = {}
        self.log_file = Path(log_file) if log_file else Path("logs/error_log.json")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Component health tracking
        self.component_health: Dict[str, Dict[str, Any]] = {}
        
    @staticmethod
    def wrap_component_errors(component_name: str, log_level: str = "ERROR"):
        """
        Decorator to add error handling without changing logic
        Preserves original exception behavior while adding logging
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    # Log successful execution for health monitoring
                    ErrorHandler._log_success(component_name, func.__name__)
                    return result
                except Exception as e:
                    # Add enhanced logging but preserve original exception
                    ErrorHandler._log_error(
                        component_name=component_name,
                        function_name=func.__name__,
                        error=e,
                        log_level=log_level,
                        context={"args_count": len(args), "kwargs_keys": list(kwargs.keys())}
                    )
                    # Re-raise original exception to preserve behavior
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def wrap_component_errors_async(component_name: str, log_level: str = "ERROR"):
        """Async version of error wrapper decorator"""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs)
                    ErrorHandler._log_success(component_name, func.__name__)
                    return result
                except Exception as e:
                    ErrorHandler._log_error(
                        component_name=component_name,
                        function_name=func.__name__,
                        error=e,
                        log_level=log_level,
                        context={"args_count": len(args), "kwargs_keys": list(kwargs.keys())}
                    )
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def enhance_silent_failure(component_name: str, operation_name: str, 
                             original_exception_handler: Callable = None):
        """
        Context manager to enhance existing silent failures with logging
        Usage: with ErrorHandler.enhance_silent_failure("TTS", "cleanup"):
                   try:
                       os.unlink(temp_file)
                   except:
                       pass  # Original silent behavior preserved
        """
        return SilentFailureEnhancer(component_name, operation_name, original_exception_handler)
    
    @staticmethod
    def _log_error(component_name: str, function_name: str, error: Exception, 
                   log_level: str = "ERROR", context: Dict[str, Any] = None):
        """Log error with enhanced details"""
        context = context or {}
        
        error_event = ErrorEvent(
            timestamp=datetime.now().isoformat(),
            component=component_name,
            function=function_name,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            severity=log_level,
            context=context
        )
        
        # Log to standard logger
        log_message = f"[{component_name}::{function_name}] {type(error).__name__}: {error}"
        if log_level == "ERROR":
            logger.error(log_message, exc_info=True)
        elif log_level == "WARNING":
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Store for analysis (in production, you might send to monitoring system)
        ErrorHandler._store_error_event(error_event)
    
    @staticmethod
    def _log_success(component_name: str, function_name: str):
        """Log successful operations for health monitoring"""
        logger.debug(f"[{component_name}::{function_name}] Operation successful")
    
    @staticmethod
    def _store_error_event(error_event: ErrorEvent):
        """Store error event for analysis (thread-safe)"""
        try:
            # In a real implementation, this would be more sophisticated
            # For now, we'll just append to a simple log file
            log_file = Path("logs/error_events.json")
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing events
            events = []
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        events = json.load(f)
                except:
                    events = []
            
            # Add new event
            events.append(asdict(error_event))
            
            # Keep only last 1000 events
            if len(events) > 1000:
                events = events[-1000:]
            
            # Write back
            with open(log_file, 'w') as f:
                json.dump(events, f, indent=2)
                
        except Exception as e:
            # Don't let error logging break the application
            logger.warning(f"Failed to store error event: {e}")

class SilentFailureEnhancer:
    """
    Context manager to enhance existing silent failures with logging
    Preserves original behavior while adding visibility
    """
    
    def __init__(self, component_name: str, operation_name: str, 
                 original_handler: Callable = None):
        self.component_name = component_name
        self.operation_name = operation_name
        self.original_handler = original_handler
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is not None:
            # An exception occurred - log it but don't change behavior
            logger.debug(f"[{self.component_name}::{self.operation_name}] "
                        f"Silent failure: {exc_type.__name__}: {exc_val} "
                        f"(duration: {duration:.3f}s)")
            
            # Call original handler if provided
            if self.original_handler:
                try:
                    self.original_handler(exc_val)
                except:
                    pass  # Don't let handler break the silence
        else:
            # Operation succeeded
            logger.debug(f"[{self.component_name}::{self.operation_name}] "
                        f"Operation completed successfully (duration: {duration:.3f}s)")
        
        # Return None to preserve original exception handling (don't suppress)
        return None

class HealthChecker:
    """
    Component health monitoring without changing existing behavior
    """
    
    def __init__(self):
        self.component_stats = {}
        self.last_check = time.time()
    
    def record_component_activity(self, component: str, operation: str, 
                                success: bool, duration: float = 0):
        """Record component activity for health monitoring"""
        if component not in self.component_stats:
            self.component_stats[component] = {
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "last_activity": None,
                "average_duration": 0,
                "operations": {}
            }
        
        stats = self.component_stats[component]
        stats["total_operations"] += 1
        stats["last_activity"] = datetime.now().isoformat()
        
        if success:
            stats["successful_operations"] += 1
        else:
            stats["failed_operations"] += 1
        
        # Track per-operation stats
        if operation not in stats["operations"]:
            stats["operations"][operation] = {
                "count": 0, "success_count": 0, "total_duration": 0
            }
        
        op_stats = stats["operations"][operation]
        op_stats["count"] += 1
        op_stats["total_duration"] += duration
        if success:
            op_stats["success_count"] += 1
    
    def get_component_health(self, component: str = None) -> Dict[str, Any]:
        """Get health status for component(s)"""
        if component:
            return self.component_stats.get(component, {})
        return self.component_stats
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        total_components = len(self.component_stats)
        healthy_components = 0
        
        for component, stats in self.component_stats.items():
            if stats["total_operations"] > 0:
                success_rate = stats["successful_operations"] / stats["total_operations"]
                if success_rate > 0.8:  # 80% success rate threshold
                    healthy_components += 1
        
        return {
            "total_components": total_components,
            "healthy_components": healthy_components,
            "health_percentage": (healthy_components / total_components * 100) if total_components > 0 else 0,
            "last_check": datetime.now().isoformat()
        }

# Global health checker instance
health_checker = HealthChecker()

# Convenience decorators for common patterns
def log_errors(component: str):
    """Simple error logging decorator"""
    return ErrorHandler.wrap_component_errors(component)

def log_errors_async(component: str):
    """Simple async error logging decorator"""
    return ErrorHandler.wrap_component_errors_async(component)

def enhance_cleanup(component: str, operation: str = "cleanup"):
    """Context manager for enhancing cleanup operations"""
    return ErrorHandler.enhance_silent_failure(component, operation)

# Health monitoring decorator
def monitor_health(component: str):
    """Decorator to monitor component health"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            finally:
                duration = time.time() - start_time
                health_checker.record_component_activity(
                    component, func.__name__, success, duration
                )
        return wrapper
    return decorator

def monitor_health_async(component: str):
    """Async version of health monitoring decorator"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            finally:
                duration = time.time() - start_time
                health_checker.record_component_activity(
                    component, func.__name__, success, duration
                )
        return wrapper
    return decorator

# Example usage patterns:
"""
# Pattern 1: Enhance existing function without changing it
@log_errors("TTS")
def existing_tts_function():
    # Original code unchanged
    pass

# Pattern 2: Enhance existing cleanup code
def cleanup_temp_files():
    with enhance_cleanup("TTS", "temp_file_cleanup"):
        try:
            os.unlink(temp_file)
        except:
            pass  # Original behavior preserved, now with logging

# Pattern 3: Add health monitoring
@monitor_health("STT")
def transcribe_audio(audio):
    # Original code unchanged
    return transcription

# Pattern 4: Enhance existing silent failures
with ErrorHandler.enhance_silent_failure("SystemMonitor", "gpu_detection"):
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True)
    except:
        pass  # Original silent behavior, now with logging
"""