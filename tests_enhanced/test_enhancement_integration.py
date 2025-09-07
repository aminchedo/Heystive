#!/usr/bin/env python3
"""
Integration Tests for Heystive Enhancements
==========================================

This module tests the integration between enhancements and existing
Heystive functionality to ensure seamless operation.

Test Areas:
- Enhancement activation/deactivation
- Bridge system functionality
- Feature extension integration
- GUI enhancement integration
- Performance with enhancements enabled
"""

import pytest
import sys
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add workspace to path for testing
workspace_path = Path("/workspace")
sys.path.insert(0, str(workspace_path))

logger = logging.getLogger(__name__)

class TestEnhancementIntegration:
    """Test suite for enhancement integration"""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test environment before each test"""
        self.workspace_path = Path("/workspace")
        self.enhancements_path = self.workspace_path / "enhancements"
        
    def test_existing_system_bridge_creation(self):
        """Test that existing system bridge can be created"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not installed")
            
        try:
            from enhancements.integrations.existing_app_bridge import ExistingSystemBridge
            
            # Test bridge creation
            bridge = ExistingSystemBridge(str(self.workspace_path))
            
            assert bridge is not None, "Bridge creation failed"
            assert hasattr(bridge, 'existing_components'), "Bridge missing existing_components"
            assert hasattr(bridge, 'compatibility_status'), "Bridge missing compatibility_status"
            
            # Test compatibility report
            report = bridge.get_compatibility_report()
            
            assert isinstance(report, dict), "Compatibility report should be a dictionary"
            assert 'bridge_status' in report, "Missing bridge_status in report"
            assert report['bridge_status'] == 'active', "Bridge should be active"
            
        except ImportError:
            pytest.skip("ExistingSystemBridge not available")
        except Exception as e:
            pytest.fail(f"Bridge creation test failed: {e}")
            
    def test_compatibility_layer_functionality(self):
        """Test compatibility layer functionality"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not installed")
            
        try:
            from enhancements.integrations.compatibility_layer import CompatibilityLayer
            
            # Test compatibility layer creation
            compat_layer = CompatibilityLayer(str(self.workspace_path))
            
            assert compat_layer is not None, "Compatibility layer creation failed"
            
            # Test safe import functionality
            test_module = compat_layer.safe_import("os")  # Should succeed
            assert test_module is not None, "Safe import of 'os' failed"
            
            # Test safe import with fallback
            fake_module = compat_layer.safe_import("nonexistent_module_xyz", fallback="fallback_value")
            assert fake_module == "fallback_value", "Safe import fallback failed"
            
            # Test rollback point creation
            rollback_id = compat_layer.create_rollback_point("test_rollback")
            assert rollback_id is not None, "Rollback point creation failed"
            assert rollback_id in [point["id"] for point in compat_layer.rollback_stack]
            
        except ImportError:
            pytest.skip("CompatibilityLayer not available")
        except Exception as e:
            pytest.fail(f"Compatibility layer test failed: {e}")
            
    def test_feature_extensions_integration(self):
        """Test feature extensions integration"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not installed")
            
        try:
            from enhancements.integrations.feature_extensions import (
                VoiceCommandExtensions,
                TTSEnhancementExtensions,
                SmartHomeExtensions
            )
            
            # Test voice command extensions
            voice_ext = VoiceCommandExtensions()
            assert voice_ext is not None, "Voice command extensions creation failed"
            assert hasattr(voice_ext, 'persian_commands'), "Missing persian_commands"
            assert len(voice_ext.persian_commands) > 0, "No Persian commands loaded"
            
            # Test TTS enhancement extensions
            tts_ext = TTSEnhancementExtensions()
            assert tts_ext is not None, "TTS enhancement extensions creation failed"
            assert hasattr(tts_ext, 'persian_voice_profiles'), "Missing persian_voice_profiles"
            
            # Test smart home extensions
            smart_ext = SmartHomeExtensions()
            assert smart_ext is not None, "Smart home extensions creation failed"
            assert hasattr(smart_ext, 'persian_device_names'), "Missing persian_device_names"
            
        except ImportError:
            pytest.skip("Feature extensions not available")
        except Exception as e:
            pytest.fail(f"Feature extensions test failed: {e}")
            
    def test_modern_gui_components_generation(self):
        """Test modern GUI components generation"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not installed")
            
        try:
            from enhancements.modern_gui.modern_web_components import ModernWebComponentsGenerator
            
            # Test component generator creation
            generator = ModernWebComponentsGenerator()
            
            assert generator is not None, "Component generator creation failed"
            assert hasattr(generator, 'themes'), "Missing themes"
            assert 'material_persian' in generator.themes, "Missing material_persian theme"
            
            # Test CSS generation
            css_content = generator.generate_material_css()
            
            assert isinstance(css_content, str), "CSS content should be string"
            assert len(css_content) > 1000, "CSS content seems too short"
            assert '--md-primary' in css_content, "Missing CSS variables"
            assert 'rtl' in css_content, "Missing RTL support"
            
            # Test JavaScript generation
            js_content = generator.generate_voice_components_js()
            
            assert isinstance(js_content, str), "JavaScript content should be string"
            assert len(js_content) > 1000, "JavaScript content seems too short"
            assert 'PersianVoiceVisualizer' in js_content, "Missing voice visualizer class"
            
        except ImportError:
            pytest.skip("Modern web components not available")
        except Exception as e:
            pytest.fail(f"Modern GUI components test failed: {e}")
            
    def test_persian_ui_advanced_components(self):
        """Test advanced Persian UI components"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not installed")
            
        try:
            from enhancements.modern_gui.persian_ui_advanced import PersianVoiceUIComponents
            
            # Test Persian UI components creation
            ui_components = PersianVoiceUIComponents()
            
            assert ui_components is not None, "Persian UI components creation failed"
            assert hasattr(ui_components, 'typography'), "Missing typography system"
            assert hasattr(ui_components, 'colors'), "Missing color system"
            assert hasattr(ui_components, 'layout'), "Missing layout system"
            
            # Test component generation
            button_html = ui_components.generate_persian_button("تست", "primary", "medium", "light")
            
            assert isinstance(button_html, str), "Button HTML should be string"
            assert 'تست' in button_html, "Button text missing"
            assert 'rtl' in button_html, "Missing RTL direction"
            
            # Test voice status component
            status_html = ui_components.generate_voice_status_component("light")
            
            assert isinstance(status_html, str), "Status HTML should be string"
            assert 'persian-voice-status' in status_html, "Missing component class"
            
        except ImportError:
            pytest.skip("Persian UI advanced not available")
        except Exception as e:
            pytest.fail(f"Persian UI advanced test failed: {e}")
            
    def test_enhancement_installer_functionality(self):
        """Test enhancement installer functionality"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not installed")
            
        try:
            from enhancements.tools.enhancement_installer import EnhancementInstaller
            
            # Test installer creation
            installer = EnhancementInstaller(str(self.workspace_path))
            
            assert installer is not None, "Enhancement installer creation failed"
            assert hasattr(installer, 'installed_enhancements'), "Missing installed_enhancements"
            assert hasattr(installer, 'active_enhancements'), "Missing active_enhancements"
            
            # Test requirements check
            requirements = installer.check_enhancement_requirements()
            
            assert isinstance(requirements, dict), "Requirements should be dictionary"
            assert 'python_compatible' in requirements, "Missing python compatibility check"
            assert 'workspace_writable' in requirements, "Missing workspace writability check"
            
            # Test enhancement status
            status = installer.get_enhancement_status()
            
            assert isinstance(status, dict), "Status should be dictionary"
            assert 'installer_version' in status, "Missing installer version"
            assert 'workspace_path' in status, "Missing workspace path"
            
            # Test diagnostics
            diagnostics = installer.run_enhancement_diagnostics()
            
            assert isinstance(diagnostics, dict), "Diagnostics should be dictionary"
            assert 'timestamp' in diagnostics, "Missing timestamp"
            assert 'overall_health' in diagnostics, "Missing overall health"
            
        except ImportError:
            pytest.skip("Enhancement installer not available")
        except Exception as e:
            pytest.fail(f"Enhancement installer test failed: {e}")

class TestEnhancementPerformance:
    """Test suite for enhancement performance impact"""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test environment before each test"""
        self.workspace_path = Path("/workspace")
        self.enhancements_path = self.workspace_path / "enhancements"
        
    def test_enhancement_import_performance(self):
        """Test that enhancement imports don't significantly impact performance"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not installed")
            
        import_times = {}
        
        # Test importing enhancement modules
        enhancement_modules = [
            "enhancements",
            "enhancements.modern_gui.enhanced_desktop",
            "enhancements.modern_gui.modern_web_components",
            "enhancements.integrations.existing_app_bridge",
            "enhancements.integrations.compatibility_layer"
        ]
        
        for module_name in enhancement_modules:
            try:
                start_time = time.time()
                
                import importlib
                importlib.import_module(module_name)
                
                end_time = time.time()
                import_time = end_time - start_time
                import_times[module_name] = import_time
                
                # Import should complete within reasonable time (5 seconds max)
                assert import_time < 5.0, f"Import of {module_name} took too long: {import_time:.2f}s"
                
            except ImportError:
                logger.warning(f"Could not import {module_name} for performance test")
            except Exception as e:
                pytest.fail(f"Performance test failed for {module_name}: {e}")
                
        logger.info(f"Enhancement import performance: {import_times}")
        
    def test_bridge_creation_performance(self):
        """Test bridge creation performance"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not installed")
            
        try:
            from enhancements.integrations.existing_app_bridge import ExistingSystemBridge
            
            # Measure bridge creation time
            start_time = time.time()
            bridge = ExistingSystemBridge(str(self.workspace_path))
            end_time = time.time()
            
            creation_time = end_time - start_time
            
            # Bridge creation should be fast (under 2 seconds)
            assert creation_time < 2.0, f"Bridge creation took too long: {creation_time:.2f}s"
            
            # Test compatibility report generation time
            start_time = time.time()
            report = bridge.get_compatibility_report()
            end_time = time.time()
            
            report_time = end_time - start_time
            
            # Report generation should be fast (under 1 second)
            assert report_time < 1.0, f"Compatibility report took too long: {report_time:.2f}s"
            
            logger.info(f"Bridge creation: {creation_time:.3f}s, Report: {report_time:.3f}s")
            
        except ImportError:
            pytest.skip("ExistingSystemBridge not available")
        except Exception as e:
            pytest.fail(f"Bridge performance test failed: {e}")
            
    def test_component_generation_performance(self):
        """Test UI component generation performance"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not available")
            
        try:
            from enhancements.modern_gui.modern_web_components import ModernWebComponentsGenerator
            
            generator = ModernWebComponentsGenerator()
            
            # Test CSS generation performance
            start_time = time.time()
            css_content = generator.generate_material_css()
            end_time = time.time()
            
            css_time = end_time - start_time
            
            # CSS generation should be fast (under 1 second)
            assert css_time < 1.0, f"CSS generation took too long: {css_time:.2f}s"
            
            # Test JavaScript generation performance
            start_time = time.time()
            js_content = generator.generate_voice_components_js()
            end_time = time.time()
            
            js_time = end_time - start_time
            
            # JavaScript generation should be fast (under 1 second)
            assert js_time < 1.0, f"JavaScript generation took too long: {js_time:.2f}s"
            
            logger.info(f"CSS generation: {css_time:.3f}s, JS generation: {js_time:.3f}s")
            
        except ImportError:
            pytest.skip("ModernWebComponentsGenerator not available")
        except Exception as e:
            pytest.fail(f"Component generation performance test failed: {e}")

class TestEnhancementFunctionality:
    """Test suite for enhancement functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test environment before each test"""
        self.workspace_path = Path("/workspace")
        self.enhancements_path = self.workspace_path / "enhancements"
        
    @pytest.mark.asyncio
    async def test_voice_command_extensions_functionality(self):
        """Test voice command extensions functionality"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not installed")
            
        try:
            from enhancements.integrations.feature_extensions import VoiceCommandExtensions
            
            voice_ext = VoiceCommandExtensions()
            
            # Test Persian text normalization
            test_text = "سلام استیو ساعت چنده؟"
            normalized = voice_ext._normalize_persian_text(test_text)
            
            assert isinstance(normalized, str), "Normalized text should be string"
            assert len(normalized) > 0, "Normalized text should not be empty"
            
            # Test pattern matching
            pattern = "ساعت چنده"
            matches = voice_ext._match_persian_pattern(normalized, pattern)
            
            assert isinstance(matches, bool), "Pattern match should return boolean"
            
            # Test performance metrics
            metrics = voice_ext.get_performance_metrics()
            
            assert isinstance(metrics, dict), "Performance metrics should be dictionary"
            
        except ImportError:
            pytest.skip("VoiceCommandExtensions not available")
        except Exception as e:
            pytest.fail(f"Voice command extensions functionality test failed: {e}")
            
    def test_persian_smart_home_command_parsing(self):
        """Test Persian smart home command parsing"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not installed")
            
        try:
            from enhancements.integrations.feature_extensions import SmartHomeExtensions
            
            smart_ext = SmartHomeExtensions()
            
            # Test parsing Persian commands
            test_commands = [
                "چراغ نشیمن رو روشن کن",
                "پریز آشپزخانه رو خاموش کن",
                "دمای اتاق رو ۲۵ درجه کن"
            ]
            
            for command in test_commands:
                parsed = smart_ext._parse_persian_smart_home_command(command)
                
                assert isinstance(parsed, dict), f"Parsed command should be dictionary for: {command}"
                assert 'success' in parsed, f"Missing success field for: {command}"
                assert 'device' in parsed, f"Missing device field for: {command}"
                assert 'action' in parsed, f"Missing action field for: {command}"
                
                if parsed['success']:
                    # Test English command conversion
                    english_command = smart_ext._convert_to_english_command(parsed)
                    assert isinstance(english_command, str), "English command should be string"
                    assert len(english_command) > 0, "English command should not be empty"
                    
        except ImportError:
            pytest.skip("SmartHomeExtensions not available")
        except Exception as e:
            pytest.fail(f"Persian smart home command parsing test failed: {e}")
            
    def test_persian_ui_component_generation(self):
        """Test Persian UI component generation"""
        if not self.enhancements_path.exists():
            pytest.skip("Enhancements not installed")
            
        try:
            from enhancements.modern_gui.persian_ui_advanced import PersianVoiceUIComponents
            
            ui_components = PersianVoiceUIComponents()
            
            # Test button generation
            button_html = ui_components.generate_persian_button("تست دکمه", "primary", "medium", "light")
            
            assert isinstance(button_html, str), "Button HTML should be string"
            assert 'تست دکمه' in button_html, "Button text should be present"
            assert 'direction: rtl' in button_html, "Button should have RTL direction"
            assert 'persian-button' in button_html, "Button should have Persian class"
            
            # Test text field generation
            textfield_html = ui_components.generate_persian_text_field("نام کاربری", "نام خود را وارد کنید")
            
            assert isinstance(textfield_html, str), "Text field HTML should be string"
            assert 'نام کاربری' in textfield_html, "Label should be present"
            assert 'نام خود را وارد کنید' in textfield_html, "Placeholder should be present"
            assert 'direction: rtl' in textfield_html, "Text field should have RTL direction"
            
            # Test card generation
            card_html = ui_components.generate_persian_card(
                "عنوان کارت", 
                "محتوای کارت تست", 
                ["تایید", "لغو"], 
                "light"
            )
            
            assert isinstance(card_html, str), "Card HTML should be string"
            assert 'عنوان کارت' in card_html, "Card title should be present"
            assert 'محتوای کارت تست' in card_html, "Card content should be present"
            assert 'تایید' in card_html, "Card action should be present"
            
        except ImportError:
            pytest.skip("PersianVoiceUIComponents not available")
        except Exception as e:
            pytest.fail(f"Persian UI component generation test failed: {e}")

# Test execution helpers
def run_integration_tests():
    """Run all integration tests"""
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    run_integration_tests()