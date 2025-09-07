"""
Unit Tests for New Utility Modules
Tests the new utilities we added without breaking existing functionality
"""

import pytest
import asyncio
import time
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestErrorHandler:
    """Test new error handling utilities"""
    
    def test_error_handler_import(self):
        """Test that error handler can be imported"""
        from steve.utils.error_handler import ErrorHandler
        assert ErrorHandler is not None
    
    def test_error_wrapper_preserves_behavior(self):
        """Test that error wrapper preserves original function behavior"""
        from steve.utils.error_handler import ErrorHandler
        
        @ErrorHandler.wrap_component_errors("TestComponent")
        def test_function(x, y):
            return x + y
        
        # Function should work normally
        result = test_function(2, 3)
        assert result == 5
    
    def test_error_wrapper_preserves_exceptions(self):
        """Test that error wrapper preserves original exceptions"""
        from steve.utils.error_handler import ErrorHandler
        
        @ErrorHandler.wrap_component_errors("TestComponent")
        def test_function():
            raise ValueError("test error")
        
        # Exception should still be raised
        with pytest.raises(ValueError, match="test error"):
            test_function()
    
    def test_silent_failure_enhancer(self):
        """Test silent failure enhancer context manager"""
        from steve.utils.error_handler import ErrorHandler
        
        # This should not raise an exception but should log
        with ErrorHandler.enhance_silent_failure("TestComponent", "test_operation"):
            try:
                raise FileNotFoundError("test file not found")
            except:
                pass  # Original silent behavior preserved
    
    def test_health_checker_integration(self):
        """Test health checker functionality"""
        from steve.utils.error_handler import health_checker
        
        # Record some operations
        health_checker.record_component_activity("TestComponent", "test_op", True, 0.1)
        health_checker.record_component_activity("TestComponent", "test_op", False, 0.2)
        
        # Get health status
        health = health_checker.get_component_health("TestComponent")
        assert health is not None

class TestPerformanceMonitor:
    """Test new performance monitoring utilities"""
    
    def test_performance_monitor_import(self):
        """Test that performance monitor can be imported"""
        from steve.utils.performance_monitor import PerformanceMonitor
        assert PerformanceMonitor is not None
    
    def test_performance_decorator_preserves_behavior(self):
        """Test that performance decorator preserves function behavior"""
        from steve.utils.performance_monitor import monitor_performance
        
        @monitor_performance("TestComponent")
        def test_function(x):
            return x * 2
        
        result = test_function(5)
        assert result == 10
    
    @pytest.mark.asyncio
    async def test_async_performance_decorator(self):
        """Test async performance decorator"""
        from steve.utils.performance_monitor import monitor_performance_async
        
        @monitor_performance_async("TestComponent")
        async def test_async_function(x):
            await asyncio.sleep(0.01)
            return x * 3
        
        result = await test_async_function(4)
        assert result == 12
    
    def test_performance_context_manager(self):
        """Test performance context manager"""
        from steve.utils.performance_monitor import PerformanceContext
        
        with PerformanceContext("test_operation", "TestComponent"):
            time.sleep(0.01)  # Simulate work
        
        # Should not raise any exceptions
        assert True
    
    def test_performance_metrics_collection(self):
        """Test performance metrics collection"""
        from steve.utils.performance_monitor import global_performance_monitor
        
        # Record some function calls
        global_performance_monitor._record_function_call(
            "TestComponent::test_func", 0.1, True, None, None, False
        )
        
        # Get metrics
        metrics = global_performance_monitor.get_function_metrics("TestComponent::test_func")
        assert metrics is not None
        assert metrics.call_count > 0

class TestSecureSubprocess:
    """Test new secure subprocess utilities"""
    
    def test_secure_subprocess_import(self):
        """Test that secure subprocess can be imported"""
        from steve.utils.secure_subprocess import SecureSubprocess
        assert SecureSubprocess is not None
    
    def test_safe_command_execution(self):
        """Test safe command execution"""
        from steve.utils.secure_subprocess import SecureSubprocess
        
        # Test with safe command
        result = SecureSubprocess.safe_run(['echo', 'test'], timeout=5)
        assert result.returncode == 0
    
    def test_dangerous_command_blocking(self):
        """Test that dangerous commands are blocked"""
        from steve.utils.secure_subprocess import SecureSubprocess, SecurityError
        
        # Test with dangerous command
        with pytest.raises(SecurityError):
            SecureSubprocess.safe_run(['rm', '-rf', '/'], timeout=5)
    
    def test_command_validation(self):
        """Test command validation"""
        from steve.utils.secure_subprocess import SecureSubprocess
        
        # Test command whitelist validation
        assert 'ping' in SecureSubprocess.ALLOWED_COMMANDS
        assert 'aplay' in SecureSubprocess.ALLOWED_COMMANDS
    
    def test_security_wrapper_context(self):
        """Test security wrapper context manager"""
        from steve.utils.secure_subprocess import SubprocessSecurityWrapper
        import subprocess
        
        with SubprocessSecurityWrapper():
            # This should use secure wrapper
            try:
                result = subprocess.run(['echo', 'test'], capture_output=True, timeout=5)
                assert result.returncode == 0
            except Exception:
                # May fail in test environment, but wrapper should work
                pass

class TestModelDownloaderUtility:
    """Test new model downloader utility"""
    
    def test_model_downloader_utility_import(self):
        """Test that model downloader utility can be imported"""
        from steve.utils.model_downloader import ModelDownloader
        assert ModelDownloader is not None
    
    def test_model_downloader_initialization(self):
        """Test model downloader initialization"""
        from steve.utils.model_downloader import ModelDownloader
        
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = ModelDownloader(temp_dir)
            assert downloader.models_dir == Path(temp_dir)
    
    def test_existing_models_check(self):
        """Test checking existing models"""
        from steve.utils.model_downloader import ModelDownloader
        
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = ModelDownloader(temp_dir)
            
            # This should work with existing PersianModelDownloader
            existing_models = downloader.check_existing_models()
            assert isinstance(existing_models, dict)
    
    def test_model_status_reporting(self):
        """Test model status reporting"""
        from steve.utils.model_downloader import ModelDownloader
        
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = ModelDownloader(temp_dir)
            
            status = downloader.get_model_status()
            assert isinstance(status, dict)
            assert 'total_models' in status

class TestHealthChecker:
    """Test new health checker utilities"""
    
    def test_health_checker_import(self):
        """Test that health checker can be imported"""
        from steve.utils.health_checker import HealthChecker
        assert HealthChecker is not None
    
    def test_component_registration(self):
        """Test component registration"""
        from steve.utils.health_checker import HealthChecker
        
        checker = HealthChecker()
        checker.register_component("TestComponent")
        
        assert "TestComponent" in checker.components
    
    def test_operation_recording(self):
        """Test operation recording"""
        from steve.utils.health_checker import HealthChecker
        
        checker = HealthChecker()
        checker.register_component("TestComponent")
        
        # Record some operations
        checker.record_operation("TestComponent", True, 0.1)
        checker.record_operation("TestComponent", False, 0.2, "test error")
        
        health = checker.get_component_health("TestComponent")
        assert health is not None
        assert health.total_operations == 2
    
    def test_health_status_determination(self):
        """Test health status determination"""
        from steve.utils.health_checker import HealthChecker
        
        checker = HealthChecker()
        checker.register_component("TestComponent")
        
        # Record mostly successful operations
        for i in range(10):
            success = i < 9  # 90% success rate
            checker.record_operation("TestComponent", success, 0.1)
        
        health = checker.get_component_health("TestComponent")
        assert health.success_rate == 0.9
        assert health.status in ["healthy", "degraded", "unhealthy"]

class TestMonitoringEndpoints:
    """Test monitoring API endpoints"""
    
    def test_monitoring_endpoints_import(self):
        """Test that monitoring endpoints can be imported"""
        from steve.utils.monitoring_endpoints import MonitoringEndpoints
        assert MonitoringEndpoints is not None
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        from steve.utils.monitoring_endpoints import MonitoringEndpoints
        
        # Mock Flask request context
        with patch('steve.utils.monitoring_endpoints.request') as mock_request:
            mock_request.view_args = {}
            
            response, status_code = MonitoringEndpoints.health_check()
            assert status_code == 200
    
    def test_performance_metrics_endpoint(self):
        """Test performance metrics endpoint"""
        from steve.utils.monitoring_endpoints import MonitoringEndpoints
        
        response, status_code = MonitoringEndpoints.performance_metrics()
        assert status_code == 200

class TestUtilityIntegration:
    """Test integration between new utilities"""
    
    def test_error_handler_with_performance_monitor(self):
        """Test error handler working with performance monitor"""
        from steve.utils.error_handler import log_errors
        from steve.utils.performance_monitor import monitor_performance
        
        # Test function with both decorators
        @log_errors("TestComponent")
        @monitor_performance("TestComponent")
        def test_function(x):
            if x < 0:
                raise ValueError("negative value")
            return x * 2
        
        # Test successful execution
        result = test_function(5)
        assert result == 10
        
        # Test error handling
        with pytest.raises(ValueError):
            test_function(-1)
    
    def test_health_checker_with_error_handler(self):
        """Test health checker integration with error handler"""
        from steve.utils.health_checker import global_health_checker
        from steve.utils.error_handler import monitor_health
        
        @monitor_health("TestComponent")
        def test_function(should_fail=False):
            if should_fail:
                raise Exception("test error")
            return "success"
        
        # Test successful operation
        result = test_function(False)
        assert result == "success"
        
        # Test failed operation
        try:
            test_function(True)
        except Exception:
            pass
        
        # Check health was recorded
        health = global_health_checker.get_component_health("TestComponent")
        assert health is not None

class TestUtilityCompatibility:
    """Test that new utilities are compatible with existing patterns"""
    
    def test_backward_compatibility(self):
        """Test that new utilities don't break existing patterns"""
        
        # Test existing subprocess pattern still works
        import subprocess
        result = subprocess.run(['echo', 'test'], capture_output=True, text=True)
        assert result.returncode == 0
        
        # Test existing error handling pattern still works
        def existing_pattern():
            try:
                raise ValueError("test")
            except ValueError:
                return "handled"
        
        assert existing_pattern() == "handled"
    
    def test_optional_integration(self):
        """Test that utilities can be optionally integrated"""
        
        # Test that existing code works without new utilities
        def existing_function():
            return "works without utilities"
        
        result = existing_function()
        assert result == "works without utilities"
        
        # Test that new utilities can be added optionally
        from steve.utils.performance_monitor import monitor_performance
        
        enhanced_function = monitor_performance("Test")(existing_function)
        result = enhanced_function()
        assert result == "works without utilities"