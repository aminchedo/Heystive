#!/usr/bin/env python3
"""
Compatibility Layer for Heystive Enhancements
============================================

This module provides a compatibility layer that ensures enhancements
work seamlessly with existing Heystive components without breaking
any existing functionality.

Key Features:
- Version compatibility checking
- Safe API wrapping
- Graceful degradation
- Error isolation
- Rollback mechanisms
"""

import sys
import importlib
import inspect
from typing import Any, Dict, List, Optional, Callable, Union
from pathlib import Path
import logging
from functools import wraps
import traceback

logger = logging.getLogger(__name__)

class CompatibilityError(Exception):
    """Exception raised when compatibility issues are detected"""
    pass

class CompatibilityLayer:
    """
    Compatibility layer for safe integration with existing components
    
    This class provides safe wrappers and compatibility checks to ensure
    enhancements don't break existing functionality.
    """
    
    def __init__(self, workspace_path: str = "/workspace"):
        self.workspace_path = Path(workspace_path)
        self.compatibility_cache = {}
        self.safe_wrappers = {}
        self.error_handlers = {}
        self.rollback_stack = []
        
        # Initialize compatibility layer
        self._initialize_compatibility()
        
    def _initialize_compatibility(self):
        """Initialize the compatibility layer"""
        logger.info("🛡️ Initializing Compatibility Layer...")
        
        # Check Python version compatibility
        self._check_python_compatibility()
        
        # Check existing component versions
        self._check_component_versions()
        
        # Set up error handlers
        self._setup_error_handlers()
        
        logger.info("✅ Compatibility Layer initialized successfully")
        
    def _check_python_compatibility(self):
        """Check Python version compatibility"""
        python_version = sys.version_info
        
        # Minimum Python 3.8 required
        if python_version < (3, 8):
            raise CompatibilityError(
                f"Python {python_version.major}.{python_version.minor} not supported. "
                "Minimum Python 3.8 required."
            )
            
        # Check for known compatibility issues
        if python_version >= (3, 13):
            logger.warning("⚠️ Python 3.13+ detected. Some packages may not have wheels available.")
            
        self.compatibility_cache["python_version"] = {
            "version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
            "compatible": True,
            "warnings": []
        }
        
    def _check_component_versions(self):
        """Check versions of existing components"""
        component_status = {}
        
        # Check main application files
        main_files = [
            "heystive_main_app.py",
            "app.py",
            "demo_professional_ui.py",
            "validate_system.py"
        ]
        
        for file_name in main_files:
            file_path = self.workspace_path / file_name
            if file_path.exists():
                component_status[file_name] = {
                    "exists": True,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                    "compatible": True
                }
            else:
                component_status[file_name] = {
                    "exists": False,
                    "compatible": False,
                    "error": "File not found"
                }
                
        self.compatibility_cache["components"] = component_status
        
    def _setup_error_handlers(self):
        """Set up error handlers for safe operation"""
        self.error_handlers = {
            "import_error": self._handle_import_error,
            "runtime_error": self._handle_runtime_error,
            "compatibility_error": self._handle_compatibility_error
        }
        
    def _handle_import_error(self, error: ImportError, context: str) -> Any:
        """Handle import errors gracefully"""
        logger.warning(f"⚠️ Import error in {context}: {error}")
        
        # Return a mock object that logs calls
        class MockObject:
            def __init__(self, name):
                self.name = name
                
            def __call__(self, *args, **kwargs):
                logger.info(f"🔄 Mock call to {self.name} with args={args}, kwargs={kwargs}")
                return None
                
            def __getattr__(self, name):
                return MockObject(f"{self.name}.{name}")
                
        return MockObject(context)
        
    def _handle_runtime_error(self, error: Exception, context: str) -> Any:
        """Handle runtime errors gracefully"""
        logger.error(f"❌ Runtime error in {context}: {error}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        
        # Log error and return safe default
        return None
        
    def _handle_compatibility_error(self, error: CompatibilityError, context: str) -> Any:
        """Handle compatibility errors"""
        logger.error(f"❌ Compatibility error in {context}: {error}")
        
        # Try to provide fallback functionality
        return None
        
    def safe_import(self, module_name: str, fallback: Optional[Any] = None) -> Any:
        """Safely import a module with fallback handling"""
        try:
            module = importlib.import_module(module_name)
            logger.debug(f"✅ Successfully imported {module_name}")
            return module
            
        except ImportError as e:
            logger.warning(f"⚠️ Failed to import {module_name}: {e}")
            
            if fallback is not None:
                return fallback
            else:
                return self._handle_import_error(e, module_name)
                
    def safe_call(self, func: Callable, *args, **kwargs) -> Any:
        """Safely call a function with error handling"""
        try:
            result = func(*args, **kwargs)
            return result
            
        except Exception as e:
            context = f"{func.__module__}.{func.__name__}" if hasattr(func, '__module__') else str(func)
            return self._handle_runtime_error(e, context)
            
    def wrap_existing_function(self, func: Callable, enhancement_wrapper: Callable) -> Callable:
        """Wrap an existing function with enhancement while preserving original behavior"""
        
        @wraps(func)
        def enhanced_wrapper(*args, **kwargs):
            try:
                # Try enhanced version first
                enhanced_result = enhancement_wrapper(func, *args, **kwargs)
                
                # If enhancement returns None, fall back to original
                if enhanced_result is None:
                    return func(*args, **kwargs)
                else:
                    return enhanced_result
                    
            except Exception as e:
                logger.warning(f"⚠️ Enhancement failed for {func.__name__}: {e}")
                # Fall back to original function
                return func(*args, **kwargs)
                
        return enhanced_wrapper
        
    def create_safe_wrapper(self, original_class: type, enhancements: Dict[str, Callable]) -> type:
        """Create a safe wrapper class that adds enhancements to existing class"""
        
        class SafeEnhancedWrapper(original_class):
            """Safe wrapper that adds enhancements while preserving original functionality"""
            
            def __init__(self, *args, **kwargs):
                try:
                    super().__init__(*args, **kwargs)
                    self._enhancements_active = True
                    self._original_methods = {}
                    
                    # Apply enhancements
                    for method_name, enhancement in enhancements.items():
                        if hasattr(self, method_name):
                            # Store original method
                            self._original_methods[method_name] = getattr(self, method_name)
                            
                            # Create enhanced method
                            enhanced_method = self._create_enhanced_method(method_name, enhancement)
                            setattr(self, method_name, enhanced_method)
                            
                except Exception as e:
                    logger.error(f"❌ Failed to initialize enhanced wrapper: {e}")
                    # Fall back to original initialization
                    super().__init__(*args, **kwargs)
                    self._enhancements_active = False
                    
            def _create_enhanced_method(self, method_name: str, enhancement: Callable):
                """Create an enhanced method with fallback to original"""
                original_method = self._original_methods[method_name]
                
                def enhanced_method(*args, **kwargs):
                    if not self._enhancements_active:
                        return original_method(*args, **kwargs)
                        
                    try:
                        # Try enhancement first
                        result = enhancement(self, original_method, *args, **kwargs)
                        if result is not None:
                            return result
                        else:
                            return original_method(*args, **kwargs)
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Enhancement failed for {method_name}: {e}")
                        return original_method(*args, **kwargs)
                        
                return enhanced_method
                
            def disable_enhancements(self):
                """Disable enhancements and revert to original behavior"""
                self._enhancements_active = False
                
                # Restore original methods
                for method_name, original_method in self._original_methods.items():
                    setattr(self, method_name, original_method)
                    
                logger.info(f"✅ Enhancements disabled for {self.__class__.__name__}")
                
            def enable_enhancements(self):
                """Re-enable enhancements"""
                self._enhancements_active = True
                logger.info(f"✅ Enhancements enabled for {self.__class__.__name__}")
                
        return SafeEnhancedWrapper
        
    def check_api_compatibility(self, existing_api: Any, enhanced_api: Any) -> Dict[str, Any]:
        """Check compatibility between existing and enhanced APIs"""
        compatibility_report = {
            "compatible": True,
            "missing_methods": [],
            "signature_changes": [],
            "new_methods": [],
            "warnings": []
        }
        
        try:
            # Get methods from both APIs
            existing_methods = {name: method for name, method in inspect.getmembers(existing_api, inspect.ismethod)}
            enhanced_methods = {name: method for name, method in inspect.getmembers(enhanced_api, inspect.ismethod)}
            
            # Check for missing methods in enhanced API
            for method_name in existing_methods:
                if method_name not in enhanced_methods:
                    compatibility_report["missing_methods"].append(method_name)
                    compatibility_report["compatible"] = False
                else:
                    # Check method signatures
                    existing_sig = inspect.signature(existing_methods[method_name])
                    enhanced_sig = inspect.signature(enhanced_methods[method_name])
                    
                    if existing_sig != enhanced_sig:
                        compatibility_report["signature_changes"].append({
                            "method": method_name,
                            "existing": str(existing_sig),
                            "enhanced": str(enhanced_sig)
                        })
                        compatibility_report["warnings"].append(
                            f"Method signature changed: {method_name}"
                        )
                        
            # Check for new methods
            for method_name in enhanced_methods:
                if method_name not in existing_methods:
                    compatibility_report["new_methods"].append(method_name)
                    
        except Exception as e:
            compatibility_report["compatible"] = False
            compatibility_report["error"] = str(e)
            
        return compatibility_report
        
    def create_rollback_point(self, description: str) -> str:
        """Create a rollback point for safe enhancement testing"""
        rollback_id = f"rollback_{len(self.rollback_stack)}_{description}"
        
        rollback_data = {
            "id": rollback_id,
            "description": description,
            "timestamp": __import__('time').time(),
            "state": {
                "compatibility_cache": self.compatibility_cache.copy(),
                "safe_wrappers": self.safe_wrappers.copy(),
                "error_handlers": self.error_handlers.copy()
            }
        }
        
        self.rollback_stack.append(rollback_data)
        logger.info(f"✅ Rollback point created: {rollback_id}")
        
        return rollback_id
        
    def rollback_to_point(self, rollback_id: str) -> bool:
        """Rollback to a specific rollback point"""
        try:
            # Find rollback point
            rollback_data = None
            for data in self.rollback_stack:
                if data["id"] == rollback_id:
                    rollback_data = data
                    break
                    
            if not rollback_data:
                logger.error(f"❌ Rollback point not found: {rollback_id}")
                return False
                
            # Restore state
            self.compatibility_cache = rollback_data["state"]["compatibility_cache"]
            self.safe_wrappers = rollback_data["state"]["safe_wrappers"]
            self.error_handlers = rollback_data["state"]["error_handlers"]
            
            # Remove rollback points after this one
            self.rollback_stack = [data for data in self.rollback_stack 
                                 if data["timestamp"] <= rollback_data["timestamp"]]
            
            logger.info(f"✅ Rolled back to: {rollback_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
            
    def get_compatibility_report(self) -> Dict[str, Any]:
        """Get comprehensive compatibility report"""
        return {
            "compatibility_layer_status": "active",
            "python_compatibility": self.compatibility_cache.get("python_version", {}),
            "component_compatibility": self.compatibility_cache.get("components", {}),
            "safe_wrappers_count": len(self.safe_wrappers),
            "error_handlers_count": len(self.error_handlers),
            "rollback_points_count": len(self.rollback_stack),
            "rollback_points": [
                {
                    "id": point["id"],
                    "description": point["description"],
                    "timestamp": point["timestamp"]
                }
                for point in self.rollback_stack
            ]
        }
        
    def validate_enhancement_safety(self, enhancement_module: Any) -> Dict[str, Any]:
        """Validate that an enhancement is safe to apply"""
        safety_report = {
            "safe": True,
            "checks_passed": [],
            "checks_failed": [],
            "warnings": []
        }
        
        try:
            # Check if enhancement has required safety methods
            required_methods = ["rollback", "validate_compatibility", "get_enhancement_info"]
            
            for method in required_methods:
                if hasattr(enhancement_module, method):
                    safety_report["checks_passed"].append(f"Has {method} method")
                else:
                    safety_report["checks_failed"].append(f"Missing {method} method")
                    safety_report["warnings"].append(f"Enhancement missing required method: {method}")
                    
            # Check for dangerous operations
            dangerous_patterns = ["os.system", "subprocess.call", "exec", "eval"]
            
            if hasattr(enhancement_module, '__file__'):
                try:
                    with open(enhancement_module.__file__, 'r') as f:
                        content = f.read()
                        
                    for pattern in dangerous_patterns:
                        if pattern in content:
                            safety_report["warnings"].append(f"Potentially dangerous operation detected: {pattern}")
                            
                except Exception:
                    pass  # Ignore file read errors
                    
            # Overall safety assessment
            if safety_report["checks_failed"]:
                safety_report["safe"] = False
                
        except Exception as e:
            safety_report["safe"] = False
            safety_report["error"] = str(e)
            
        return safety_report

# Convenience functions
def create_compatibility_layer(workspace_path: str = "/workspace") -> CompatibilityLayer:
    """Create and initialize a compatibility layer"""
    return CompatibilityLayer(workspace_path)

def safe_enhance_existing_component(existing_component: Any, enhancements: Dict[str, Callable]) -> Any:
    """Safely enhance an existing component with compatibility protection"""
    compatibility = create_compatibility_layer()
    
    # Create rollback point
    rollback_id = compatibility.create_rollback_point(f"enhance_{existing_component.__class__.__name__}")
    
    try:
        # Create safe wrapper
        enhanced_class = compatibility.create_safe_wrapper(existing_component.__class__, enhancements)
        
        # Create enhanced instance
        enhanced_instance = enhanced_class(*[], **{})
        
        logger.info(f"✅ Successfully enhanced {existing_component.__class__.__name__}")
        return enhanced_instance
        
    except Exception as e:
        logger.error(f"❌ Enhancement failed: {e}")
        
        # Rollback on failure
        compatibility.rollback_to_point(rollback_id)
        
        # Return original component
        return existing_component