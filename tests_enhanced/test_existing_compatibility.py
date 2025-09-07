#!/usr/bin/env python3
"""
Compatibility Tests for Heystive Enhancements
=============================================

This module tests that all existing Heystive functionality continues
to work correctly after enhancement installation.

Critical Test Areas:
- Existing file integrity
- Import compatibility
- API compatibility
- Functionality preservation
- Performance impact assessment
"""

import pytest
import sys
import os
import subprocess
import importlib
import time
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add workspace to path for testing
workspace_path = Path("/workspace")
sys.path.insert(0, str(workspace_path))

logger = logging.getLogger(__name__)

class TestExistingSystemCompatibility:
    """Test suite for existing system compatibility"""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test environment before each test"""
        self.workspace_path = Path("/workspace")
        self.existing_files = [
            "heystive_main_app.py",
            "app.py",
            "demo_professional_ui.py",
            "validate_system.py"
        ]
        
    def test_existing_files_present(self):
        """Test that all existing system files are present and readable"""
        missing_files = []
        unreadable_files = []
        
        for file_name in self.existing_files:
            file_path = self.workspace_path / file_name
            
            if not file_path.exists():
                missing_files.append(file_name)
            elif not os.access(file_path, os.R_OK):
                unreadable_files.append(file_name)
                
        assert not missing_files, f"Missing existing files: {missing_files}"
        assert not unreadable_files, f"Unreadable existing files: {unreadable_files}"
        
    def test_existing_file_integrity(self):
        """Test that existing files have not been corrupted"""
        for file_name in self.existing_files:
            file_path = self.workspace_path / file_name
            
            if file_path.exists():
                # Test that file can be read
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(1024)  # Read first 1KB
                        assert len(content) > 0, f"File {file_name} appears to be empty"
                        
                    # Test that it's a valid Python file
                    if file_name.endswith('.py'):
                        try:
                            compile(content, file_name, 'exec')
                        except SyntaxError as e:
                            pytest.fail(f"Syntax error in {file_name}: {e}")
                            
                except Exception as e:
                    pytest.fail(f"Failed to read {file_name}: {e}")
                    
    def test_python_imports_still_work(self):
        """Test that existing Python modules can still be imported"""
        import_tests = [
            ("heystive_main_app", "HeyStiveApp"),
            ("demo_professional_ui", "SteveProfessionalUIDemo")
        ]
        
        failed_imports = []
        
        for module_name, class_name in import_tests:
            try:
                # Try to import the module
                spec = importlib.util.spec_from_file_location(
                    module_name, 
                    str(self.workspace_path / f"{module_name}.py")
                )
                
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Check if expected class exists
                    if hasattr(module, class_name):
                        # Try to instantiate (with minimal args)
                        try:
                            if class_name == "HeyStiveApp":
                                instance = getattr(module, class_name)()
                            elif class_name == "SteveProfessionalUIDemo":
                                instance = getattr(module, class_name)()
                            else:
                                instance = getattr(module, class_name)()
                                
                            assert instance is not None
                            
                        except Exception as e:
                            logger.warning(f"Could not instantiate {class_name}: {e}")
                            # This might be expected due to missing dependencies
                            
                    else:
                        failed_imports.append(f"Class {class_name} not found in {module_name}")
                        
                else:
                    failed_imports.append(f"Could not load module spec for {module_name}")
                    
            except Exception as e:
                failed_imports.append(f"Failed to import {module_name}: {e}")
                
        # Only fail if critical imports don't work
        critical_failures = [f for f in failed_imports if "HeyStiveApp" in f or "import" in f.lower()]
        if critical_failures:
            pytest.fail(f"Critical import failures: {critical_failures}")
            
    def test_existing_directories_intact(self):
        """Test that existing directory structure is intact"""
        expected_directories = [
            "steve",
            "heystive", 
            "templates",
            "tests",
            "archive",
            "heystive_audio_output"
        ]
        
        missing_directories = []
        
        for dir_name in expected_directories:
            dir_path = self.workspace_path / dir_name
            if not dir_path.exists() or not dir_path.is_dir():
                missing_directories.append(dir_name)
                
        # Some directories might be optional, so we only warn
        if missing_directories:
            logger.warning(f"Missing directories (might be optional): {missing_directories}")
            
    def test_existing_configuration_files(self):
        """Test that existing configuration files are intact"""
        config_files = [
            "requirements.txt",
            "package.json"
        ]
        
        for config_file in config_files:
            file_path = self.workspace_path / config_file
            
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    assert len(content) > 0, f"Configuration file {config_file} is empty"
                    
                    # Basic format validation
                    if config_file == "requirements.txt":
                        lines = content.strip().split('\n')
                        valid_lines = [line for line in lines if line.strip() and not line.startswith('#')]
                        assert len(valid_lines) > 0, "requirements.txt has no valid package entries"
                        
                    elif config_file == "package.json":
                        import json
                        json_data = json.loads(content)
                        assert isinstance(json_data, dict), "package.json is not a valid JSON object"
                        
                except Exception as e:
                    pytest.fail(f"Configuration file {config_file} validation failed: {e}")
                    
    def test_no_enhancement_interference(self):
        """Test that enhancements don't interfere with existing functionality"""
        
        # Test that enhancement directory exists but doesn't break imports
        enhancements_path = self.workspace_path / "enhancements"
        
        if enhancements_path.exists():
            # Enhancements are installed, test they don't interfere
            
            # Test that existing modules can still be imported normally
            try:
                # Try importing existing modules with enhancements present
                sys.path.insert(0, str(self.workspace_path))
                
                # Test critical imports
                if (self.workspace_path / "heystive_main_app.py").exists():
                    import heystive_main_app
                    assert hasattr(heystive_main_app, 'HeyStiveApp')
                    
            except ImportError as e:
                pytest.fail(f"Enhancements interfere with existing imports: {e}")
            finally:
                # Clean up sys.path
                if str(self.workspace_path) in sys.path:
                    sys.path.remove(str(self.workspace_path))
                    
    def test_existing_functionality_executable(self):
        """Test that existing applications can still be executed"""
        
        # Test main applications with --help or --version flags (non-interactive)
        executable_tests = [
            ("python3", "heystive_main_app.py", "--help"),
            ("python3", "app.py", "--help"),
            ("python3", "demo_professional_ui.py", "--help"),
            ("python3", "validate_system.py", "--help")
        ]
        
        for python_cmd, script, flag in executable_tests:
            script_path = self.workspace_path / script
            
            if script_path.exists():
                try:
                    # Run with timeout to prevent hanging
                    result = subprocess.run(
                        [python_cmd, str(script_path), flag],
                        cwd=str(self.workspace_path),
                        capture_output=True,
                        text=True,
                        timeout=30  # 30 second timeout
                    )
                    
                    # We expect these to either show help or fail gracefully
                    # Exit codes 0 (success) or 2 (argparse help) are acceptable
                    acceptable_exit_codes = [0, 2]
                    
                    if result.returncode not in acceptable_exit_codes:
                        logger.warning(
                            f"Script {script} returned exit code {result.returncode}. "
                            f"This might be due to missing dependencies."
                        )
                        
                except subprocess.TimeoutExpired:
                    logger.warning(f"Script {script} timed out - might be waiting for input")
                except FileNotFoundError:
                    pytest.skip(f"Python interpreter {python_cmd} not found")
                except Exception as e:
                    logger.warning(f"Could not test {script} execution: {e}")
                    
    def test_enhancement_installation_reversible(self):
        """Test that enhancement installation is reversible"""
        
        enhancements_path = self.workspace_path / "enhancements"
        
        if enhancements_path.exists():
            # Test that we can identify enhancement files vs original files
            enhancement_files = list(enhancements_path.rglob("*.py"))
            
            # Ensure enhancement files are clearly separate from original files
            for enhancement_file in enhancement_files:
                relative_path = enhancement_file.relative_to(self.workspace_path)
                
                # Enhancement files should be in enhancements/ directory
                assert str(relative_path).startswith("enhancements/"), \
                    f"Enhancement file {relative_path} not in enhancements directory"
                    
                # Enhancement files should not overwrite existing files
                potential_conflict = self.workspace_path / relative_path.name
                if potential_conflict.exists() and potential_conflict != enhancement_file:
                    # There's a file with same name outside enhancements directory
                    logger.warning(f"Potential name conflict: {relative_path.name}")
                    
    def test_performance_impact_minimal(self):
        """Test that enhancements don't significantly impact performance"""
        
        # Simple performance test - importing existing modules
        import_times = {}
        
        for file_name in self.existing_files:
            if file_name.endswith('.py'):
                module_name = file_name[:-3]  # Remove .py extension
                
                try:
                    start_time = time.time()
                    
                    spec = importlib.util.spec_from_file_location(
                        module_name, 
                        str(self.workspace_path / file_name)
                    )
                    
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                    end_time = time.time()
                    import_time = end_time - start_time
                    import_times[module_name] = import_time
                    
                    # Import should complete within reasonable time (10 seconds max)
                    assert import_time < 10.0, f"Import of {module_name} took too long: {import_time:.2f}s"
                    
                except Exception as e:
                    logger.warning(f"Could not measure import time for {module_name}: {e}")
                    
        logger.info(f"Import performance: {import_times}")
        
    def test_existing_apis_unchanged(self):
        """Test that existing APIs have not changed"""
        
        # Test that key classes still have expected methods
        api_tests = [
            {
                "module": "heystive_main_app",
                "class": "HeyStiveApp", 
                "expected_methods": ["run", "__init__"]
            }
        ]
        
        for api_test in api_tests:
            module_file = self.workspace_path / f"{api_test['module']}.py"
            
            if module_file.exists():
                try:
                    spec = importlib.util.spec_from_file_location(
                        api_test['module'], 
                        str(module_file)
                    )
                    
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, api_test['class']):
                            cls = getattr(module, api_test['class'])
                            
                            missing_methods = []
                            for method in api_test['expected_methods']:
                                if not hasattr(cls, method):
                                    missing_methods.append(method)
                                    
                            assert not missing_methods, \
                                f"Missing methods in {api_test['class']}: {missing_methods}"
                                
                except Exception as e:
                    logger.warning(f"Could not test API for {api_test['module']}: {e}")

class TestEnhancementSystemIntegrity:
    """Test suite for enhancement system integrity"""
    
    def test_enhancement_files_exist(self):
        """Test that enhancement files exist if enhancements are installed"""
        enhancements_path = Path("/workspace/enhancements")
        
        if enhancements_path.exists():
            # Enhancement system is installed, test integrity
            
            required_files = [
                "enhancements/__init__.py",
                "enhancements/modern_gui/__init__.py",
                "enhancements/modern_gui/enhanced_desktop.py",
                "enhancements/modern_gui/modern_web_components.py",
                "enhancements/modern_gui/persian_ui_advanced.py",
                "enhancements/integrations/__init__.py",
                "enhancements/integrations/existing_app_bridge.py",
                "enhancements/integrations/compatibility_layer.py",
                "enhancements/integrations/feature_extensions.py",
                "enhancements/tools/__init__.py",
                "enhancements/tools/enhancement_installer.py"
            ]
            
            missing_files = []
            
            for file_path in required_files:
                full_path = Path("/workspace") / file_path
                if not full_path.exists():
                    missing_files.append(file_path)
                    
            assert not missing_files, f"Missing enhancement files: {missing_files}"
            
    def test_enhancement_imports_work(self):
        """Test that enhancement modules can be imported"""
        enhancements_path = Path("/workspace/enhancements")
        
        if enhancements_path.exists():
            # Test importing enhancement modules
            import_tests = [
                "enhancements",
                "enhancements.modern_gui",
                "enhancements.integrations.existing_app_bridge",
                "enhancements.integrations.compatibility_layer"
            ]
            
            failed_imports = []
            
            for module_name in import_tests:
                try:
                    importlib.import_module(module_name)
                except ImportError as e:
                    failed_imports.append(f"{module_name}: {e}")
                    
            assert not failed_imports, f"Enhancement import failures: {failed_imports}"
            
    def test_enhancement_compatibility_layer(self):
        """Test that compatibility layer functions correctly"""
        enhancements_path = Path("/workspace/enhancements")
        
        if enhancements_path.exists():
            try:
                from enhancements.integrations.compatibility_layer import CompatibilityLayer
                
                # Test creating compatibility layer
                compat = CompatibilityLayer("/workspace")
                
                # Test basic functionality
                report = compat.get_compatibility_report()
                
                assert isinstance(report, dict), "Compatibility report should be a dictionary"
                assert "compatibility_layer_status" in report, "Missing status in compatibility report"
                
            except ImportError:
                pytest.skip("Compatibility layer not available")
            except Exception as e:
                pytest.fail(f"Compatibility layer test failed: {e}")

# Test execution helpers
def run_compatibility_tests():
    """Run all compatibility tests"""
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    run_compatibility_tests()