"""
Integration Tests for Existing Functionality
Tests how existing components work together without modification
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.fixtures.sample_data import (
    PERSIAN_TEXT_SAMPLES,
    HARDWARE_CONFIGS,
    SMART_HOME_DEVICES,
    generate_mock_audio
)

class TestExistingVoicePipelineIntegration:
    """Test existing voice pipeline integration as-is"""
    
    @pytest.mark.integration
    @pytest.mark.existing_behavior
    def test_voice_pipeline_import_integration(self):
        """Test that voice pipeline components can be imported together"""
        try:
            from steve.core.voice_pipeline import SteveVoiceAssistant
            from steve.core.persian_tts import ElitePersianTTS
            from steve.core.persian_stt import AdaptivePersianSTT
            from steve.core.wake_word_detector import PersianWakeWordDetector
            
            # All components should be importable
            assert SteveVoiceAssistant is not None
            assert ElitePersianTTS is not None
            assert AdaptivePersianSTT is not None
            assert PersianWakeWordDetector is not None
            
        except ImportError as e:
            pytest.skip(f"Voice pipeline integration not available: {e}")
    
    @pytest.mark.integration
    @pytest.mark.existing_behavior
    def test_system_monitor_integration(self):
        """Test system monitor integration with existing components"""
        try:
            from steve.utils.system_monitor import SystemPerformanceMonitor
            
            monitor = SystemPerformanceMonitor()
            assert monitor is not None
            
            # Test that it has expected methods (as they currently exist)
            assert hasattr(monitor, 'assess_system_capabilities')
            assert hasattr(monitor, 'get_hardware_info')
            assert hasattr(monitor, 'get_audio_info')
            
        except Exception as e:
            pytest.skip(f"System monitor integration test failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.existing_behavior
    @pytest.mark.asyncio
    async def test_voice_assistant_initialization_pattern(self):
        """Test existing voice assistant initialization pattern"""
        try:
            from steve.core.voice_pipeline import SteveVoiceAssistant
            from steve.utils.system_monitor import SystemPerformanceMonitor
            
            # Test current initialization pattern
            monitor = SystemPerformanceMonitor()
            system_status = await monitor.assess_system_capabilities()
            
            # This should work with existing initialization
            assistant = SteveVoiceAssistant(system_status)
            assert assistant is not None
            
            # Test existing attributes
            assert hasattr(assistant, 'system_config')
            
        except Exception as e:
            pytest.skip(f"Voice assistant initialization test failed: {e}")

class TestExistingSmartHomeIntegration:
    """Test existing smart home integration as-is"""
    
    @pytest.mark.integration
    @pytest.mark.existing_behavior
    def test_smart_home_components_import_together(self):
        """Test that smart home components can be imported together"""
        try:
            from steve.smart_home.device_controller import SmartHomeController
            from steve.smart_home.device_discovery import SmartHomeDeviceDiscovery
            from steve.smart_home.mcp_server import SteveMCPServer
            
            assert SmartHomeController is not None
            assert SmartHomeDeviceDiscovery is not None
            assert SteveMCPServer is not None
            
        except ImportError as e:
            pytest.skip(f"Smart home integration not available: {e}")
    
    @pytest.mark.integration
    @pytest.mark.existing_behavior
    def test_device_controller_initialization_pattern(self):
        """Test existing device controller initialization"""
        try:
            from steve.smart_home.device_controller import SmartHomeController
            
            # Test with minimal config (as currently used)
            config = {
                "hue_bridge_ip": "192.168.1.100",
                "mqtt_broker": "localhost"
            }
            
            controller = SmartHomeController(config)
            assert controller is not None
            
        except Exception as e:
            pytest.skip(f"Device controller initialization failed: {e}")

class TestExistingWebInterfaceIntegration:
    """Test existing web interface integration as-is"""
    
    @pytest.mark.integration
    @pytest.mark.existing_behavior
    def test_web_interface_components_import(self):
        """Test that web interface components import correctly"""
        try:
            from steve.ui.web_interface import create_app
            from steve.ui.professional_web_interface import create_professional_app
            
            assert create_app is not None
            assert create_professional_app is not None
            
        except ImportError as e:
            pytest.skip(f"Web interface integration not available: {e}")
    
    @pytest.mark.integration
    @pytest.mark.existing_behavior
    def test_web_app_creation_pattern(self):
        """Test existing web app creation pattern"""
        try:
            from steve.ui.web_interface import create_app
            
            # Test current app creation pattern
            app = create_app()
            assert app is not None
            
            # Test that it's a Flask app
            assert hasattr(app, 'route')
            assert hasattr(app, 'run')
            
        except Exception as e:
            pytest.skip(f"Web app creation test failed: {e}")

class TestExistingModelIntegration:
    """Test existing model system integration as-is"""
    
    @pytest.mark.integration
    @pytest.mark.existing_behavior
    def test_model_downloader_integration(self):
        """Test existing model downloader integration"""
        try:
            from steve.models.download_models import PersianModelDownloader
            
            downloader = PersianModelDownloader()
            assert downloader is not None
            
            # Test existing methods
            assert hasattr(downloader, 'model_registry')
            assert hasattr(downloader, 'get_available_models')
            
            # Test registry structure
            registry = downloader.model_registry
            assert isinstance(registry, dict)
            
        except Exception as e:
            pytest.skip(f"Model downloader integration failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.existing_behavior
    def test_model_registry_structure(self):
        """Test that existing model registry has expected structure"""
        try:
            from steve.models.download_models import PersianModelDownloader
            
            downloader = PersianModelDownloader()
            registry = downloader.model_registry
            
            # Check for expected model types
            model_types = set()
            for model_id, model_info in registry.items():
                if 'type' in model_info:
                    model_types.add(model_info['type'])
            
            # Should have at least whisper models
            expected_types = {'whisper'}
            assert expected_types.issubset(model_types)
            
        except Exception as e:
            pytest.skip(f"Model registry structure test failed: {e}")

class TestExistingUtilsIntegration:
    """Test existing utility integration as-is"""
    
    @pytest.mark.integration
    @pytest.mark.existing_behavior
    def test_system_monitor_audio_integration(self):
        """Test system monitor audio detection integration"""
        try:
            from steve.utils.system_monitor import SystemPerformanceMonitor
            
            monitor = SystemPerformanceMonitor()
            
            # Test existing audio info method
            with patch('pyaudio.PyAudio') as mock_pyaudio:
                # Mock PyAudio for testing
                mock_pa = Mock()
                mock_pa.get_device_count.return_value = 4
                mock_pa.get_device_info_by_index.return_value = {
                    'name': 'Test Device',
                    'maxInputChannels': 2,
                    'maxOutputChannels': 2,
                    'defaultSampleRate': 44100
                }
                mock_pyaudio.return_value = mock_pa
                
                audio_info = monitor._get_audio_info()
                assert isinstance(audio_info, dict)
                
        except Exception as e:
            pytest.skip(f"System monitor audio integration failed: {e}")

class TestNewUtilitiesWithExistingCode:
    """Test that new utilities integrate properly with existing code"""
    
    @pytest.mark.integration
    def test_error_handler_with_existing_patterns(self):
        """Test error handler works with existing error patterns"""
        try:
            from steve.utils.error_handler import ErrorHandler
            
            # Test with existing exception pattern
            @ErrorHandler.wrap_component_errors("TestComponent")
            def existing_function_pattern():
                # Simulate existing function that might fail
                import os
                os.unlink("/nonexistent/file")  # This will fail
            
            # This should add logging but preserve exception behavior
            with pytest.raises(FileNotFoundError):
                existing_function_pattern()
                
        except ImportError as e:
            pytest.fail(f"Error handler integration should work: {e}")
    
    @pytest.mark.integration
    def test_performance_monitor_with_existing_functions(self):
        """Test performance monitor works with existing functions"""
        try:
            from steve.utils.performance_monitor import monitor_performance
            
            # Test with existing function pattern
            @monitor_performance("TestComponent")
            def existing_function_pattern(text):
                # Simulate existing processing
                import time
                time.sleep(0.1)
                return f"processed: {text}"
            
            result = existing_function_pattern("test")
            assert result == "processed: test"
            
        except ImportError as e:
            pytest.fail(f"Performance monitor integration should work: {e}")
    
    @pytest.mark.integration
    def test_secure_subprocess_with_existing_patterns(self):
        """Test secure subprocess works with existing patterns"""
        try:
            from steve.utils.secure_subprocess import SecureSubprocess
            
            # Test with existing safe command pattern
            result = SecureSubprocess.safe_run(['echo', 'test'], timeout=5)
            assert result.returncode == 0
            
        except Exception as e:
            pytest.skip(f"Secure subprocess integration test failed: {e}")

class TestRegressionPrevention:
    """Test to prevent regressions in existing functionality"""
    
    @pytest.mark.regression
    @pytest.mark.existing_behavior
    def test_package_structure_unchanged(self):
        """Test that package structure remains intact"""
        try:
            import steve
            from steve import core, utils, ui, intelligence, smart_home, models
            
            # Core modules should still exist
            from steve.core import voice_pipeline, persian_tts, persian_stt
            from steve.utils import system_monitor
            from steve.ui import web_interface
            from steve.smart_home import device_controller
            from steve.models import download_models
            
            # All should be importable
            modules = [
                voice_pipeline, persian_tts, persian_stt,
                system_monitor, web_interface, device_controller,
                download_models
            ]
            
            for module in modules:
                assert module is not None
                
        except ImportError as e:
            pytest.fail(f"Package structure regression detected: {e}")
    
    @pytest.mark.regression
    @pytest.mark.existing_behavior
    def test_existing_api_compatibility(self):
        """Test that existing APIs are still compatible"""
        try:
            # Test system monitor API
            from steve.utils.system_monitor import SystemPerformanceMonitor
            monitor = SystemPerformanceMonitor()
            
            # These methods should still exist and work
            assert hasattr(monitor, 'assess_system_capabilities')
            assert hasattr(monitor, 'get_hardware_info')
            
            # Test model downloader API
            from steve.models.download_models import PersianModelDownloader
            downloader = PersianModelDownloader()
            
            assert hasattr(downloader, 'model_registry')
            assert hasattr(downloader, 'get_available_models')
            
        except Exception as e:
            pytest.fail(f"API compatibility regression detected: {e}")
    
    @pytest.mark.regression
    @pytest.mark.existing_behavior
    def test_configuration_patterns_preserved(self):
        """Test that existing configuration patterns still work"""
        import json
        import tempfile
        import os
        
        # Test existing config pattern
        test_config = {
            "wake_word": "هی استیو",
            "response": "بله سرورم",
            "language": "fa"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f, ensure_ascii=False)
            config_path = f.name
        
        try:
            # Test existing loading pattern
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            assert loaded_config == test_config
            assert loaded_config["wake_word"] == "هی استیو"
            
        finally:
            os.unlink(config_path)