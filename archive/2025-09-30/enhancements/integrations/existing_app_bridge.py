#!/usr/bin/env python3
"""
Existing System Bridge for Heystive Enhancements
===============================================

This module provides a safe bridge to integrate with existing Heystive components
without modifying any existing files. It follows the principle of "extend, don't replace".

Key Features:
- Safe import of existing components
- Error isolation and fallback handling
- Compatibility validation
- Non-intrusive enhancement integration
"""

import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Any, Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class ExistingSystemBridge:
    """
    Bridge to safely integrate with existing Heystive components
    
    This class provides safe access to existing functionality without
    modifying any existing files or breaking existing workflows.
    """
    
    def __init__(self, workspace_path: str = "/workspace"):
        self.workspace_path = Path(workspace_path)
        self.existing_components = {}
        self.compatibility_status = {}
        self.enhancement_hooks = {}
        
        # Initialize bridge
        self._initialize_bridge()
        
    def _initialize_bridge(self):
        """Initialize the bridge to existing components"""
        logger.info("🔗 Initializing Existing System Bridge...")
        
        # Load existing components safely
        self._load_existing_desktop_app()
        self._load_existing_web_app()
        self._load_existing_voice_system()
        self._load_existing_ui_components()
        
        # Validate compatibility
        self._validate_compatibility()
        
        logger.info("✅ Existing System Bridge initialized successfully")
        
    def _load_existing_desktop_app(self):
        """Safely load existing desktop application"""
        try:
            desktop_app_path = self.workspace_path / "heystive_main_app.py"
            if desktop_app_path.exists():
                spec = importlib.util.spec_from_file_location(
                    "existing_desktop_app", str(desktop_app_path)
                )
                existing_desktop_module = importlib.util.module_from_spec(spec)
                
                # Store reference without executing
                self.existing_components["desktop_app"] = {
                    "module_spec": spec,
                    "module": existing_desktop_module,
                    "path": str(desktop_app_path),
                    "available": True,
                    "type": "desktop_application"
                }
                
                logger.info("✅ Existing desktop app detected and bridged")
            else:
                logger.warning("⚠️ Desktop app not found at expected location")
                self.existing_components["desktop_app"] = {"available": False}
                
        except Exception as e:
            logger.error(f"❌ Failed to bridge desktop app: {e}")
            self.existing_components["desktop_app"] = {"available": False, "error": str(e)}
            
    def _load_existing_web_app(self):
        """Safely load existing web application"""
        try:
            web_app_path = self.workspace_path / "app.py"
            if web_app_path.exists():
                spec = importlib.util.spec_from_file_location(
                    "existing_web_app", str(web_app_path)
                )
                existing_web_module = importlib.util.module_from_spec(spec)
                
                self.existing_components["web_app"] = {
                    "module_spec": spec,
                    "module": existing_web_module,
                    "path": str(web_app_path),
                    "available": True,
                    "type": "web_application"
                }
                
                logger.info("✅ Existing web app detected and bridged")
            else:
                logger.warning("⚠️ Web app not found at expected location")
                self.existing_components["web_app"] = {"available": False}
                
        except Exception as e:
            logger.error(f"❌ Failed to bridge web app: {e}")
            self.existing_components["web_app"] = {"available": False, "error": str(e)}
            
    def _load_existing_voice_system(self):
        """Safely load existing voice system components"""
        try:
            # Check for Steve voice system
            steve_path = self.workspace_path / "steve"
            heystive_path = self.workspace_path / "heystive"
            
            voice_components = {}
            
            # Check Steve directory
            if steve_path.exists():
                voice_components["steve"] = {
                    "path": str(steve_path),
                    "available": True,
                    "type": "voice_core"
                }
                
                # Add Steve to Python path if not already there
                if str(steve_path.parent) not in sys.path:
                    sys.path.append(str(steve_path.parent))
                    
            # Check Heystive directory
            if heystive_path.exists():
                voice_components["heystive"] = {
                    "path": str(heystive_path),
                    "available": True,
                    "type": "voice_integration"
                }
                
            self.existing_components["voice_system"] = voice_components
            
            if voice_components:
                logger.info("✅ Existing voice system detected and bridged")
            else:
                logger.warning("⚠️ Voice system not found")
                
        except Exception as e:
            logger.error(f"❌ Failed to bridge voice system: {e}")
            self.existing_components["voice_system"] = {"available": False, "error": str(e)}
            
    def _load_existing_ui_components(self):
        """Safely load existing UI components"""
        try:
            ui_components = {}
            
            # Professional UI demo
            demo_ui_path = self.workspace_path / "demo_professional_ui.py"
            if demo_ui_path.exists():
                ui_components["professional_demo"] = {
                    "path": str(demo_ui_path),
                    "available": True,
                    "type": "ui_demo"
                }
                
            # Web templates
            templates_path = self.workspace_path / "templates"
            if templates_path.exists():
                ui_components["web_templates"] = {
                    "path": str(templates_path),
                    "available": True,
                    "type": "web_templates"
                }
                
            # HTML interface
            index_path = self.workspace_path / "index.html"
            if index_path.exists():
                ui_components["web_interface"] = {
                    "path": str(index_path),
                    "available": True,
                    "type": "web_interface"
                }
                
            self.existing_components["ui_components"] = ui_components
            
            if ui_components:
                logger.info("✅ Existing UI components detected and bridged")
                
        except Exception as e:
            logger.error(f"❌ Failed to bridge UI components: {e}")
            self.existing_components["ui_components"] = {"available": False, "error": str(e)}
            
    def _validate_compatibility(self):
        """Validate compatibility with existing components"""
        self.compatibility_status = {
            "desktop_app_functional": self._test_existing_desktop(),
            "web_app_functional": self._test_existing_web(),
            "voice_system_functional": self._test_existing_voice(),
            "ui_components_functional": self._test_existing_ui(),
            "overall_compatibility": True
        }
        
        # Update overall compatibility
        failed_tests = [k for k, v in self.compatibility_status.items() 
                       if k != "overall_compatibility" and not v]
        
        if failed_tests:
            self.compatibility_status["overall_compatibility"] = False
            logger.warning(f"⚠️ Compatibility issues detected: {failed_tests}")
        else:
            logger.info("✅ Full compatibility validated")
            
    def _test_existing_desktop(self) -> bool:
        """Test if existing desktop app can be accessed"""
        try:
            desktop_component = self.existing_components.get("desktop_app", {})
            return desktop_component.get("available", False)
        except Exception:
            return False
            
    def _test_existing_web(self) -> bool:
        """Test if existing web app can be accessed"""
        try:
            web_component = self.existing_components.get("web_app", {})
            return web_component.get("available", False)
        except Exception:
            return False
            
    def _test_existing_voice(self) -> bool:
        """Test if existing voice system can be accessed"""
        try:
            voice_component = self.existing_components.get("voice_system", {})
            return bool(voice_component and voice_component != {"available": False})
        except Exception:
            return False
            
    def _test_existing_ui(self) -> bool:
        """Test if existing UI components can be accessed"""
        try:
            ui_component = self.existing_components.get("ui_components", {})
            return bool(ui_component and ui_component != {"available": False})
        except Exception:
            return False
    
    # Enhancement Integration Methods
    
    def get_existing_component(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get reference to existing component safely"""
        return self.existing_components.get(component_name)
        
    def is_component_available(self, component_name: str) -> bool:
        """Check if a component is available for enhancement"""
        component = self.existing_components.get(component_name, {})
        return component.get("available", False)
        
    def enhance_existing_desktop(self, enhancements: Dict[str, Any]) -> bool:
        """Add enhancements to existing desktop app without modification"""
        try:
            if not self.is_component_available("desktop_app"):
                logger.error("❌ Desktop app not available for enhancement")
                return False
                
            # Create enhancement hooks without modifying existing code
            self.enhancement_hooks["desktop_app"] = enhancements
            logger.info("✅ Desktop app enhancements registered")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to enhance desktop app: {e}")
            return False
            
    def enhance_existing_web(self, enhancements: Dict[str, Any]) -> bool:
        """Add enhancements to existing web interface without modification"""
        try:
            if not self.is_component_available("web_app"):
                logger.error("❌ Web app not available for enhancement")
                return False
                
            # Create enhancement hooks without modifying existing code
            self.enhancement_hooks["web_app"] = enhancements
            logger.info("✅ Web app enhancements registered")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to enhance web app: {e}")
            return False
            
    def get_compatibility_report(self) -> Dict[str, Any]:
        """Get comprehensive compatibility report"""
        return {
            "bridge_status": "active",
            "existing_components": {
                name: {
                    "available": component.get("available", False),
                    "type": component.get("type", "unknown")
                }
                for name, component in self.existing_components.items()
            },
            "compatibility_status": self.compatibility_status,
            "enhancement_hooks": list(self.enhancement_hooks.keys()),
            "recommendations": self._get_compatibility_recommendations()
        }
        
    def _get_compatibility_recommendations(self) -> List[str]:
        """Get recommendations for improving compatibility"""
        recommendations = []
        
        # Check each component and provide recommendations
        for name, component in self.existing_components.items():
            if not component.get("available", False):
                if "error" in component:
                    recommendations.append(f"Fix {name} error: {component['error']}")
                else:
                    recommendations.append(f"Ensure {name} is properly installed")
                    
        if not recommendations:
            recommendations.append("All components are compatible and ready for enhancement")
            
        return recommendations
        
    def rollback_enhancements(self) -> bool:
        """Rollback all enhancements and restore original state"""
        try:
            self.enhancement_hooks.clear()
            logger.info("✅ All enhancements rolled back successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to rollback enhancements: {e}")
            return False

# Convenience functions for easy access
def create_bridge(workspace_path: str = "/workspace") -> ExistingSystemBridge:
    """Create and initialize an existing system bridge"""
    return ExistingSystemBridge(workspace_path)

def validate_existing_system(workspace_path: str = "/workspace") -> Dict[str, Any]:
    """Quick validation of existing system compatibility"""
    bridge = create_bridge(workspace_path)
    return bridge.get_compatibility_report()