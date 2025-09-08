"""
Component Health Monitoring System
Non-intrusive health monitoring and status reporting
Adds health checks without changing existing component behavior
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import json
import psutil
import threading

logger = logging.getLogger(__name__)

@dataclass
class ComponentHealth:
    """Health status of a system component"""
    component_name: str
    status: str  # "healthy", "degraded", "unhealthy", "unknown"
    last_check: str
    uptime_seconds: float
    success_rate: float
    error_count: int
    warning_count: int
    total_operations: int
    average_response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    details: Dict[str, Any]

class HealthChecker:
    """
    Periodic component health monitoring
    Non-intrusive status reporting and alerting
    """
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.components: Dict[str, Dict[str, Any]] = {}
        self.health_history: List[Dict[str, Any]] = []
        self.running = False
        self.check_thread = None
        
        # Health thresholds
        self.thresholds = {
            "success_rate_warning": 0.9,  # 90%
            "success_rate_critical": 0.7,  # 70%
            "response_time_warning": 5.0,  # 5 seconds
            "response_time_critical": 10.0,  # 10 seconds
            "memory_warning_mb": 500,  # 500 MB
            "memory_critical_mb": 1000,  # 1 GB
            "error_rate_warning": 0.05,  # 5%
            "error_rate_critical": 0.1   # 10%
        }
        
        # Built-in health checks for core components
        self.health_checks = {
            "TTS": self._check_tts_health,
            "STT": self._check_stt_health,
            "VoicePipeline": self._check_voice_pipeline_health,
            "SystemMonitor": self._check_system_monitor_health,
            "SmartHome": self._check_smart_home_health
        }
    
    def register_component(self, component_name: str, health_check: Optional[Callable] = None):
        """Register a component for health monitoring"""
        self.components[component_name] = {
            "start_time": time.time(),
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "total_response_time": 0.0,
            "last_activity": None,
            "health_check": health_check,
            "status": "unknown",
            "errors": [],
            "warnings": []
        }
        logger.info(f"Registered component for health monitoring: {component_name}")
    
    def record_operation(self, component_name: str, success: bool, 
                        response_time: float = 0, error_msg: str = None):
        """Record an operation for health tracking"""
        if component_name not in self.components:
            self.register_component(component_name)
        
        comp = self.components[component_name]
        comp["total_operations"] += 1
        comp["total_response_time"] += response_time
        comp["last_activity"] = time.time()
        
        if success:
            comp["successful_operations"] += 1
        else:
            comp["failed_operations"] += 1
            if error_msg:
                comp["errors"].append({
                    "timestamp": datetime.now().isoformat(),
                    "message": error_msg
                })
                # Keep only last 50 errors
                if len(comp["errors"]) > 50:
                    comp["errors"] = comp["errors"][-50:]
    
    def record_warning(self, component_name: str, warning_msg: str):
        """Record a warning for a component"""
        if component_name not in self.components:
            self.register_component(component_name)
        
        comp = self.components[component_name]
        comp["warnings"].append({
            "timestamp": datetime.now().isoformat(),
            "message": warning_msg
        })
        # Keep only last 50 warnings
        if len(comp["warnings"]) > 50:
            comp["warnings"] = comp["warnings"][-50:]
    
    def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """Get detailed health status for a component"""
        if component_name not in self.components:
            return None
        
        comp = self.components[component_name]
        
        # Calculate metrics
        uptime = time.time() - comp["start_time"]
        success_rate = (comp["successful_operations"] / comp["total_operations"]) if comp["total_operations"] > 0 else 1.0
        avg_response_time = (comp["total_response_time"] / comp["total_operations"]) if comp["total_operations"] > 0 else 0.0
        
        # Determine status
        status = self._determine_component_status(component_name, success_rate, avg_response_time)
        
        # Get process info
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()
        except:
            memory_mb = 0
            cpu_percent = 0
        
        return ComponentHealth(
            component_name=component_name,
            status=status,
            last_check=datetime.now().isoformat(),
            uptime_seconds=uptime,
            success_rate=success_rate,
            error_count=len(comp["errors"]),
            warning_count=len(comp["warnings"]),
            total_operations=comp["total_operations"],
            average_response_time=avg_response_time,
            memory_usage_mb=memory_mb,
            cpu_usage_percent=cpu_percent,
            details={
                "last_activity": comp["last_activity"],
                "recent_errors": comp["errors"][-5:] if comp["errors"] else [],
                "recent_warnings": comp["warnings"][-5:] if comp["warnings"] else []
            }
        )
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        total_components = len(self.components)
        healthy_count = 0
        degraded_count = 0
        unhealthy_count = 0
        
        component_statuses = {}
        
        for comp_name in self.components:
            health = self.get_component_health(comp_name)
            if health:
                component_statuses[comp_name] = health.status
                if health.status == "healthy":
                    healthy_count += 1
                elif health.status == "degraded":
                    degraded_count += 1
                elif health.status == "unhealthy":
                    unhealthy_count += 1
        
        # Overall system status
        if unhealthy_count > 0:
            overall_status = "unhealthy"
        elif degraded_count > total_components * 0.3:  # More than 30% degraded
            overall_status = "degraded"
        elif healthy_count > total_components * 0.8:  # More than 80% healthy
            overall_status = "healthy"
        else:
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "total_components": total_components,
            "healthy_components": healthy_count,
            "degraded_components": degraded_count,
            "unhealthy_components": unhealthy_count,
            "health_percentage": (healthy_count / total_components * 100) if total_components > 0 else 0,
            "component_statuses": component_statuses,
            "timestamp": datetime.now().isoformat()
        }
    
    def start_monitoring(self):
        """Start periodic health monitoring"""
        if self.running:
            return
        
        self.running = True
        self.check_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.check_thread.start()
        logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop periodic health monitoring"""
        self.running = False
        if self.check_thread:
            self.check_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._perform_health_checks()
                self._save_health_snapshot()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                time.sleep(self.check_interval)
    
    def _perform_health_checks(self):
        """Perform health checks for all registered components"""
        for component_name in self.components:
            try:
                # Run custom health check if available
                comp = self.components[component_name]
                if comp["health_check"]:
                    start_time = time.time()
                    try:
                        health_result = comp["health_check"]()
                        response_time = time.time() - start_time
                        self.record_operation(component_name, True, response_time)
                    except Exception as e:
                        response_time = time.time() - start_time
                        self.record_operation(component_name, False, response_time, str(e))
                
                # Run built-in health check if available
                elif component_name in self.health_checks:
                    start_time = time.time()
                    try:
                        self.health_checks[component_name]()
                        response_time = time.time() - start_time
                        self.record_operation(component_name, True, response_time)
                    except Exception as e:
                        response_time = time.time() - start_time
                        self.record_operation(component_name, False, response_time, str(e))
                        
            except Exception as e:
                logger.error(f"Health check failed for {component_name}: {e}")
    
    def _determine_component_status(self, component_name: str, success_rate: float, 
                                  avg_response_time: float) -> str:
        """Determine component health status based on metrics"""
        if success_rate < self.thresholds["success_rate_critical"]:
            return "unhealthy"
        elif avg_response_time > self.thresholds["response_time_critical"]:
            return "unhealthy"
        elif success_rate < self.thresholds["success_rate_warning"]:
            return "degraded"
        elif avg_response_time > self.thresholds["response_time_warning"]:
            return "degraded"
        else:
            return "healthy"
    
    def _save_health_snapshot(self):
        """Save current health snapshot to file"""
        try:
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "summary": self.get_system_health_summary(),
                "components": {}
            }
            
            for comp_name in self.components:
                health = self.get_component_health(comp_name)
                if health:
                    snapshot["components"][comp_name] = asdict(health)
            
            # Save to file
            log_dir = Path("logs/health")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            health_file = log_dir / "health_history.json"
            
            # Load existing history
            history = []
            if health_file.exists():
                try:
                    with open(health_file, 'r') as f:
                        history = json.load(f)
                except:
                    history = []
            
            # Add new snapshot
            history.append(snapshot)
            
            # Keep only last 100 snapshots
            if len(history) > 100:
                history = history[-100:]
            
            # Save updated history
            with open(health_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save health snapshot: {e}")
    
    # Built-in health checks for core components
    def _check_tts_health(self):
        """Basic TTS health check"""
        # This would test if TTS is responsive
        # For now, just check if we can import the module
        from steve.core.persian_tts import ElitePersianTTS
        logger.debug("TTS health check passed")
    
    def _check_stt_health(self):
        """Basic STT health check"""
        from steve.core.persian_stt import AdaptivePersianSTT
        logger.debug("STT health check passed")
    
    def _check_voice_pipeline_health(self):
        """Basic voice pipeline health check"""
        from steve.core.voice_pipeline import SteveVoiceAssistant
        logger.debug("Voice pipeline health check passed")
    
    def _check_system_monitor_health(self):
        """Basic system monitor health check"""
        from steve.utils.system_monitor import SystemPerformanceMonitor
        logger.debug("System monitor health check passed")
    
    def _check_smart_home_health(self):
        """Basic smart home health check"""
        from steve.smart_home.device_controller import SmartHomeController
        logger.debug("Smart home health check passed")

# Global health checker instance
global_health_checker = HealthChecker()

# Convenience functions
def start_health_monitoring(check_interval: int = 60):
    """Start global health monitoring"""
    global_health_checker.check_interval = check_interval
    global_health_checker.start_monitoring()

def stop_health_monitoring():
    """Stop global health monitoring"""
    global_health_checker.stop_monitoring()

def record_component_operation(component: str, success: bool, response_time: float = 0, error: str = None):
    """Record component operation for health tracking"""
    global_health_checker.record_operation(component, success, response_time, error)

def get_system_health():
    """Get current system health summary"""
    return global_health_checker.get_system_health_summary()

def get_component_health(component: str):
    """Get health status for specific component"""
    return global_health_checker.get_component_health(component)