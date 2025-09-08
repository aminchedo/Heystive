"""
Monitoring API Endpoints
Provides REST endpoints for performance and health monitoring
Can be added to existing web interfaces without breaking APIs
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from flask import jsonify, request

from steve.utils.performance_monitor import global_performance_monitor
from steve.utils.health_checker import global_health_checker

class MonitoringEndpoints:
    """
    Monitoring API endpoints that can be added to existing Flask apps
    Provides health, performance, and system status endpoints
    """
    
    @staticmethod
    def health_check():
        """GET /api/health - Basic health check endpoint"""
        try:
            summary = global_health_checker.get_system_health_summary()
            
            return jsonify({
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
                "system_health": summary,
                "uptime_seconds": summary.get("uptime_seconds", 0),
                "version": "1.0.0"
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @staticmethod
    def detailed_health():
        """GET /api/health/detailed - Detailed health information"""
        try:
            components = {}
            
            # Get health for all registered components
            for component_name in global_health_checker.components:
                health = global_health_checker.get_component_health(component_name)
                if health:
                    components[component_name] = {
                        "status": health.status,
                        "success_rate": health.success_rate,
                        "error_count": health.error_count,
                        "warning_count": health.warning_count,
                        "total_operations": health.total_operations,
                        "average_response_time": health.average_response_time,
                        "memory_usage_mb": health.memory_usage_mb,
                        "cpu_usage_percent": health.cpu_usage_percent,
                        "uptime_seconds": health.uptime_seconds,
                        "last_check": health.last_check
                    }
            
            summary = global_health_checker.get_system_health_summary()
            
            return jsonify({
                "system_summary": summary,
                "components": components,
                "timestamp": datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @staticmethod
    def performance_metrics():
        """GET /api/metrics/performance - Performance metrics"""
        try:
            summary = global_performance_monitor.get_performance_summary()
            
            return jsonify({
                "performance_summary": summary,
                "timestamp": datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @staticmethod
    def component_performance():
        """GET /api/metrics/performance/<component> - Component-specific performance"""
        component = request.view_args.get('component', 'Unknown')
        
        try:
            metrics = global_performance_monitor.get_component_metrics(component)
            
            if not metrics:
                return jsonify({
                    "error": f"No metrics found for component: {component}",
                    "timestamp": datetime.now().isoformat()
                }), 404
            
            # Convert metrics to serializable format
            serializable_metrics = {}
            for func_name, metric in metrics.items():
                serializable_metrics[func_name] = {
                    "call_count": metric.call_count,
                    "average_time": metric.average_time,
                    "min_time": metric.min_time,
                    "max_time": metric.max_time,
                    "success_rate": metric.success_rate,
                    "throughput_per_second": metric.throughput_per_second,
                    "memory_usage_mb": metric.memory_usage_mb,
                    "cpu_usage_percent": metric.cpu_usage_percent
                }
            
            return jsonify({
                "component": component,
                "metrics": serializable_metrics,
                "timestamp": datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @staticmethod
    def system_resources():
        """GET /api/metrics/resources - System resource usage"""
        try:
            # Get recent resource history (last hour)
            history = global_performance_monitor.get_resource_history(minutes=60)
            
            if not history:
                return jsonify({
                    "error": "No resource history available",
                    "timestamp": datetime.now().isoformat()
                }), 404
            
            # Convert to serializable format
            resource_data = []
            for snapshot in history:
                resource_data.append({
                    "timestamp": snapshot.timestamp,
                    "cpu_percent": snapshot.cpu_percent,
                    "memory_mb": snapshot.memory_mb,
                    "memory_percent": snapshot.memory_percent,
                    "disk_usage_percent": snapshot.disk_usage_percent,
                    "active_threads": snapshot.active_threads
                })
            
            # Calculate current averages
            if resource_data:
                recent_data = resource_data[-12:]  # Last 12 samples (1 hour if 5min intervals)
                avg_cpu = sum(d["cpu_percent"] for d in recent_data) / len(recent_data)
                avg_memory = sum(d["memory_percent"] for d in recent_data) / len(recent_data)
                current_threads = recent_data[-1]["active_threads"]
            else:
                avg_cpu = avg_memory = current_threads = 0
            
            return jsonify({
                "current_averages": {
                    "cpu_percent": avg_cpu,
                    "memory_percent": avg_memory,
                    "active_threads": current_threads
                },
                "history": resource_data,
                "timestamp": datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @staticmethod
    def metrics_export():
        """GET /api/metrics/export - Export all metrics as JSON"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "health_summary": global_health_checker.get_system_health_summary(),
                "performance_summary": global_performance_monitor.get_performance_summary(),
                "component_health": {},
                "component_performance": {},
                "resource_history": []
            }
            
            # Export component health
            for component_name in global_health_checker.components:
                health = global_health_checker.get_component_health(component_name)
                if health:
                    export_data["component_health"][component_name] = {
                        "status": health.status,
                        "success_rate": health.success_rate,
                        "error_count": health.error_count,
                        "total_operations": health.total_operations,
                        "average_response_time": health.average_response_time,
                        "uptime_seconds": health.uptime_seconds
                    }
            
            # Export component performance
            all_metrics = global_performance_monitor.get_all_metrics()
            for component, functions in all_metrics.items():
                export_data["component_performance"][component] = {}
                for func_name, metric in functions.items():
                    export_data["component_performance"][component][func_name] = {
                        "call_count": metric.call_count,
                        "average_time": metric.average_time,
                        "success_rate": metric.success_rate,
                        "throughput_per_second": metric.throughput_per_second
                    }
            
            # Export resource history (last 24 hours)
            history = global_performance_monitor.get_resource_history(minutes=1440)
            for snapshot in history:
                export_data["resource_history"].append({
                    "timestamp": snapshot.timestamp,
                    "cpu_percent": snapshot.cpu_percent,
                    "memory_percent": snapshot.memory_percent,
                    "active_threads": snapshot.active_threads
                })
            
            return jsonify(export_data), 200
            
        except Exception as e:
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @staticmethod
    def monitoring_status():
        """GET /api/monitoring/status - Monitoring system status"""
        try:
            return jsonify({
                "health_monitoring": {
                    "active": True,
                    "registered_components": len(global_health_checker.components),
                    "check_interval": global_health_checker.check_interval
                },
                "performance_monitoring": {
                    "active": global_performance_monitor.monitoring_active,
                    "monitored_functions": len(global_performance_monitor.function_stats),
                    "resource_samples": len(global_performance_monitor.resource_history)
                },
                "timestamp": datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500

def register_monitoring_routes(app):
    """
    Register monitoring routes with an existing Flask app
    Can be called to add monitoring endpoints without breaking existing routes
    """
    
    # Health endpoints
    app.add_url_rule('/api/health', 'health_check', 
                    MonitoringEndpoints.health_check, methods=['GET'])
    
    app.add_url_rule('/api/health/detailed', 'detailed_health',
                    MonitoringEndpoints.detailed_health, methods=['GET'])
    
    # Performance endpoints  
    app.add_url_rule('/api/metrics/performance', 'performance_metrics',
                    MonitoringEndpoints.performance_metrics, methods=['GET'])
    
    app.add_url_rule('/api/metrics/performance/<component>', 'component_performance',
                    MonitoringEndpoints.component_performance, methods=['GET'])
    
    # Resource endpoints
    app.add_url_rule('/api/metrics/resources', 'system_resources',
                    MonitoringEndpoints.system_resources, methods=['GET'])
    
    # Export endpoints
    app.add_url_rule('/api/metrics/export', 'metrics_export',
                    MonitoringEndpoints.metrics_export, methods=['GET'])
    
    # Status endpoints
    app.add_url_rule('/api/monitoring/status', 'monitoring_status',
                    MonitoringEndpoints.monitoring_status, methods=['GET'])
    
    print("✅ Monitoring endpoints registered:")
    print("   GET /api/health - Basic health check")
    print("   GET /api/health/detailed - Detailed component health")
    print("   GET /api/metrics/performance - Performance summary")
    print("   GET /api/metrics/performance/<component> - Component performance")
    print("   GET /api/metrics/resources - System resource usage")
    print("   GET /api/metrics/export - Export all metrics")
    print("   GET /api/monitoring/status - Monitoring system status")

# Standalone monitoring server (optional)
def create_monitoring_app():
    """Create a standalone Flask app for monitoring (optional)"""
    from flask import Flask
    
    app = Flask(__name__)
    register_monitoring_routes(app)
    
    @app.route('/')
    def monitoring_home():
        return jsonify({
            "service": "Steve Voice Assistant - Monitoring API",
            "version": "1.0.0",
            "endpoints": [
                "/api/health",
                "/api/health/detailed", 
                "/api/metrics/performance",
                "/api/metrics/performance/<component>",
                "/api/metrics/resources",
                "/api/metrics/export",
                "/api/monitoring/status"
            ],
            "timestamp": datetime.now().isoformat()
        })
    
    return app

# Example usage:
"""
# Pattern 1: Add to existing Flask app
from steve.utils.monitoring_endpoints import register_monitoring_routes
register_monitoring_routes(existing_app)

# Pattern 2: Create standalone monitoring server
from steve.utils.monitoring_endpoints import create_monitoring_app
monitoring_app = create_monitoring_app()
monitoring_app.run(host='0.0.0.0', port=8081)

# Pattern 3: Use endpoints directly
from steve.utils.monitoring_endpoints import MonitoringEndpoints
health_data = MonitoringEndpoints.health_check()
"""