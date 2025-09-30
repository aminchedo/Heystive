#!/usr/bin/env python3
"""
Enhancement Installer for Heystive Persian Voice Assistant
=========================================================

This module provides safe installation and management of enhancements
without modifying any existing system files.

Key Features:
- Safe installation with rollback capability
- Dependency management for enhancement packages
- Compatibility validation before installation
- Non-intrusive enhancement activation
- Complete removal and cleanup utilities
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import json
import tempfile
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancementInstaller:
    """
    Safe installer for Heystive enhancements
    
    Manages installation, activation, and removal of enhancements
    while preserving all existing functionality.
    """
    
    def __init__(self, workspace_path: str = "/workspace"):
        self.workspace_path = Path(workspace_path)
        self.enhancements_path = self.workspace_path / "enhancements"
        self.config_path = self.enhancements_path / "config"
        self.backup_path = self.enhancements_path / "backups"
        
        # Enhancement metadata
        self.installed_enhancements = {}
        self.active_enhancements = {}
        self.enhancement_dependencies = {}
        
        # Initialize installer
        self._initialize_installer()
        
    def _initialize_installer(self):
        """Initialize the enhancement installer"""
        logger.info("🔧 Initializing Enhancement Installer...")
        
        # Create necessary directories
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing enhancement configuration
        self._load_enhancement_config()
        
        # Validate existing system
        self._validate_existing_system()
        
        logger.info("✅ Enhancement Installer initialized successfully")
        
    def _load_enhancement_config(self):
        """Load enhancement configuration from file"""
        config_file = self.config_path / "enhancements.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self.installed_enhancements = config.get("installed", {})
                self.active_enhancements = config.get("active", {})
                self.enhancement_dependencies = config.get("dependencies", {})
                
                logger.info(f"✅ Loaded configuration for {len(self.installed_enhancements)} enhancements")
                
            except Exception as e:
                logger.error(f"❌ Failed to load enhancement config: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
            
    def _create_default_config(self):
        """Create default enhancement configuration"""
        default_config = {
            "installed": {},
            "active": {},
            "dependencies": {},
            "version": "1.0.0",
            "created": datetime.now().isoformat()
        }
        
        self._save_enhancement_config(default_config)
        
    def _save_enhancement_config(self, config: Optional[Dict] = None):
        """Save enhancement configuration to file"""
        if config is None:
            config = {
                "installed": self.installed_enhancements,
                "active": self.active_enhancements,
                "dependencies": self.enhancement_dependencies,
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat()
            }
            
        config_file = self.config_path / "enhancements.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            logger.debug("✅ Enhancement configuration saved")
            
        except Exception as e:
            logger.error(f"❌ Failed to save enhancement config: {e}")
            
    def _validate_existing_system(self):
        """Validate that existing system is intact"""
        required_files = [
            "heystive_main_app.py",
            "app.py",
            "demo_professional_ui.py",
            "validate_system.py"
        ]
        
        missing_files = []
        for file_name in required_files:
            if not (self.workspace_path / file_name).exists():
                missing_files.append(file_name)
                
        if missing_files:
            logger.warning(f"⚠️ Missing existing system files: {missing_files}")
        else:
            logger.info("✅ Existing system validation passed")
            
    def check_enhancement_requirements(self) -> Dict[str, Any]:
        """Check system requirements for enhancements"""
        requirements = {
            "python_version": sys.version_info[:2],
            "python_compatible": sys.version_info >= (3, 8),
            "workspace_writable": os.access(self.workspace_path, os.W_OK),
            "disk_space_mb": self._get_available_disk_space(),
            "existing_system_intact": self._check_existing_system_integrity(),
            "dependencies_available": self._check_enhancement_dependencies()
        }
        
        requirements["overall_ready"] = all([
            requirements["python_compatible"],
            requirements["workspace_writable"],
            requirements["disk_space_mb"] > 100,  # At least 100MB free
            requirements["existing_system_intact"]
        ])
        
        return requirements
        
    def _get_available_disk_space(self) -> int:
        """Get available disk space in MB"""
        try:
            stat = shutil.disk_usage(self.workspace_path)
            return stat.free // (1024 * 1024)  # Convert to MB
        except Exception:
            return 0
            
    def _check_existing_system_integrity(self) -> bool:
        """Check if existing system files are intact"""
        try:
            # Check main files exist and are readable
            main_files = [
                "heystive_main_app.py",
                "app.py", 
                "demo_professional_ui.py"
            ]
            
            for file_name in main_files:
                file_path = self.workspace_path / file_name
                if not file_path.exists() or not file_path.is_file():
                    return False
                    
                # Try to read first few lines to ensure file is not corrupted
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read(1024)  # Read first 1KB
                except Exception:
                    return False
                    
            return True
            
        except Exception:
            return False
            
    def _check_enhancement_dependencies(self) -> Dict[str, bool]:
        """Check if enhancement dependencies are available"""
        dependencies = {
            "PySide6": self._check_package_available("PySide6"),
            "flask": self._check_package_available("flask"),
            "pathlib": True,  # Built-in
            "json": True,     # Built-in
            "logging": True   # Built-in
        }
        
        return dependencies
        
    def _check_package_available(self, package_name: str) -> bool:
        """Check if a Python package is available"""
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False
            
    def install_enhancements(self, enhancement_list: Optional[List[str]] = None) -> Dict[str, Any]:
        """Install specified enhancements or all available ones"""
        if enhancement_list is None:
            enhancement_list = ["modern_gui", "web_components", "compatibility_layer"]
            
        installation_results = {
            "successful": [],
            "failed": [],
            "skipped": [],
            "overall_success": True
        }
        
        logger.info(f"🔧 Installing enhancements: {enhancement_list}")
        
        # Check requirements first
        requirements = self.check_enhancement_requirements()
        if not requirements["overall_ready"]:
            installation_results["overall_success"] = False
            installation_results["error"] = "System requirements not met"
            return installation_results
            
        # Create backup before installation
        backup_id = self._create_system_backup()
        
        try:
            for enhancement_name in enhancement_list:
                result = self._install_single_enhancement(enhancement_name)
                
                if result["success"]:
                    installation_results["successful"].append(enhancement_name)
                    
                    # Register enhancement
                    self.installed_enhancements[enhancement_name] = {
                        "version": "1.0.0",
                        "installed_date": datetime.now().isoformat(),
                        "backup_id": backup_id,
                        "status": "installed"
                    }
                else:
                    installation_results["failed"].append({
                        "name": enhancement_name,
                        "error": result.get("error", "Unknown error")
                    })
                    installation_results["overall_success"] = False
                    
            # Save configuration
            self._save_enhancement_config()
            
            if installation_results["overall_success"]:
                logger.info(f"✅ Successfully installed {len(installation_results['successful'])} enhancements")
            else:
                logger.warning(f"⚠️ Installation completed with {len(installation_results['failed'])} failures")
                
        except Exception as e:
            logger.error(f"❌ Installation failed: {e}")
            installation_results["overall_success"] = False
            installation_results["error"] = str(e)
            
            # Rollback on failure
            self._restore_system_backup(backup_id)
            
        return installation_results
        
    def _install_single_enhancement(self, enhancement_name: str) -> Dict[str, Any]:
        """Install a single enhancement"""
        result = {"success": False, "error": None}
        
        try:
            logger.info(f"🔧 Installing enhancement: {enhancement_name}")
            
            # Check if already installed
            if enhancement_name in self.installed_enhancements:
                result["success"] = True
                result["message"] = "Already installed"
                return result
                
            # Install based on enhancement type
            if enhancement_name == "modern_gui":
                result = self._install_modern_gui()
            elif enhancement_name == "web_components":
                result = self._install_web_components()
            elif enhancement_name == "compatibility_layer":
                result = self._install_compatibility_layer()
            else:
                result["error"] = f"Unknown enhancement: {enhancement_name}"
                
        except Exception as e:
            result["error"] = str(e)
            
        return result
        
    def _install_modern_gui(self) -> Dict[str, Any]:
        """Install modern GUI enhancements"""
        try:
            # Check if PySide6 is available
            if not self._check_package_available("PySide6"):
                return {
                    "success": False,
                    "error": "PySide6 not available. Install with: pip install PySide6"
                }
                
            # Modern GUI components are already in place
            # Just validate they exist
            gui_path = self.enhancements_path / "modern_gui"
            if not gui_path.exists():
                return {
                    "success": False,
                    "error": "Modern GUI components not found"
                }
                
            return {"success": True, "message": "Modern GUI components ready"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _install_web_components(self) -> Dict[str, Any]:
        """Install modern web components"""
        try:
            # Generate web components
            from ..modern_gui.modern_web_components import generate_modern_web_components
            
            result = generate_modern_web_components()
            if result:
                return {"success": True, "message": "Web components generated successfully"}
            else:
                return {"success": False, "error": "Failed to generate web components"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _install_compatibility_layer(self) -> Dict[str, Any]:
        """Install compatibility layer"""
        try:
            # Compatibility layer is already in place
            # Just validate it exists
            compat_path = self.enhancements_path / "integrations" / "compatibility_layer.py"
            if not compat_path.exists():
                return {
                    "success": False,
                    "error": "Compatibility layer not found"
                }
                
            return {"success": True, "message": "Compatibility layer ready"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def activate_enhancement(self, enhancement_name: str) -> bool:
        """Activate an installed enhancement"""
        try:
            if enhancement_name not in self.installed_enhancements:
                logger.error(f"❌ Enhancement not installed: {enhancement_name}")
                return False
                
            # Mark as active
            self.active_enhancements[enhancement_name] = {
                "activated_date": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Save configuration
            self._save_enhancement_config()
            
            logger.info(f"✅ Activated enhancement: {enhancement_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to activate enhancement {enhancement_name}: {e}")
            return False
            
    def deactivate_enhancement(self, enhancement_name: str) -> bool:
        """Deactivate an enhancement without uninstalling"""
        try:
            if enhancement_name in self.active_enhancements:
                del self.active_enhancements[enhancement_name]
                
                # Save configuration
                self._save_enhancement_config()
                
                logger.info(f"✅ Deactivated enhancement: {enhancement_name}")
                return True
            else:
                logger.warning(f"⚠️ Enhancement not active: {enhancement_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to deactivate enhancement {enhancement_name}: {e}")
            return False
            
    def uninstall_enhancement(self, enhancement_name: str) -> bool:
        """Completely uninstall an enhancement"""
        try:
            # Deactivate first
            self.deactivate_enhancement(enhancement_name)
            
            # Remove from installed list
            if enhancement_name in self.installed_enhancements:
                del self.installed_enhancements[enhancement_name]
                
            # Clean up enhancement-specific files
            self._cleanup_enhancement_files(enhancement_name)
            
            # Save configuration
            self._save_enhancement_config()
            
            logger.info(f"✅ Uninstalled enhancement: {enhancement_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to uninstall enhancement {enhancement_name}: {e}")
            return False
            
    def _cleanup_enhancement_files(self, enhancement_name: str):
        """Clean up files specific to an enhancement"""
        try:
            # Clean up generated web components
            if enhancement_name == "web_components":
                web_components_path = self.enhancements_path / "web_components"
                if web_components_path.exists():
                    shutil.rmtree(web_components_path)
                    
            logger.debug(f"✅ Cleaned up files for {enhancement_name}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to clean up files for {enhancement_name}: {e}")
            
    def _create_system_backup(self) -> str:
        """Create a backup of the current system state"""
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir = self.backup_path / backup_id
        
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup configuration
            config_backup = {
                "installed": self.installed_enhancements.copy(),
                "active": self.active_enhancements.copy(),
                "dependencies": self.enhancement_dependencies.copy(),
                "backup_date": datetime.now().isoformat()
            }
            
            with open(backup_dir / "config.json", 'w') as f:
                json.dump(config_backup, f, indent=2)
                
            logger.info(f"✅ System backup created: {backup_id}")
            return backup_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create backup: {e}")
            return ""
            
    def _restore_system_backup(self, backup_id: str) -> bool:
        """Restore system from backup"""
        backup_dir = self.backup_path / backup_id
        
        try:
            if not backup_dir.exists():
                logger.error(f"❌ Backup not found: {backup_id}")
                return False
                
            # Restore configuration
            with open(backup_dir / "config.json", 'r') as f:
                backup_config = json.load(f)
                
            self.installed_enhancements = backup_config.get("installed", {})
            self.active_enhancements = backup_config.get("active", {})
            self.enhancement_dependencies = backup_config.get("dependencies", {})
            
            # Save restored configuration
            self._save_enhancement_config()
            
            logger.info(f"✅ System restored from backup: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to restore backup {backup_id}: {e}")
            return False
            
    def get_enhancement_status(self) -> Dict[str, Any]:
        """Get status of all enhancements"""
        return {
            "installer_version": "1.0.0",
            "workspace_path": str(self.workspace_path),
            "enhancements_path": str(self.enhancements_path),
            "installed_count": len(self.installed_enhancements),
            "active_count": len(self.active_enhancements),
            "installed_enhancements": self.installed_enhancements,
            "active_enhancements": self.active_enhancements,
            "system_requirements": self.check_enhancement_requirements(),
            "available_backups": [d.name for d in self.backup_path.iterdir() if d.is_dir()]
        }
        
    def run_enhancement_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics on enhancement system"""
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "system_requirements": self.check_enhancement_requirements(),
            "file_integrity": self._check_enhancement_file_integrity(),
            "dependency_status": self._check_enhancement_dependencies(),
            "configuration_valid": self._validate_enhancement_config(),
            "backup_status": self._check_backup_integrity()
        }
        
        # Overall health score
        health_checks = [
            diagnostics["system_requirements"]["overall_ready"],
            diagnostics["file_integrity"]["all_files_present"],
            diagnostics["configuration_valid"],
            len(diagnostics["backup_status"]["valid_backups"]) > 0
        ]
        
        diagnostics["overall_health"] = sum(health_checks) / len(health_checks)
        diagnostics["status"] = "healthy" if diagnostics["overall_health"] > 0.8 else "needs_attention"
        
        return diagnostics
        
    def _check_enhancement_file_integrity(self) -> Dict[str, Any]:
        """Check integrity of enhancement files"""
        required_files = [
            "enhancements/__init__.py",
            "enhancements/modern_gui/__init__.py",
            "enhancements/modern_gui/enhanced_desktop.py",
            "enhancements/modern_gui/modern_web_components.py",
            "enhancements/integrations/__init__.py",
            "enhancements/integrations/existing_app_bridge.py",
            "enhancements/integrations/compatibility_layer.py",
            "enhancements/tools/__init__.py",
            "enhancements/tools/enhancement_installer.py"
        ]
        
        file_status = {}
        all_present = True
        
        for file_path in required_files:
            full_path = self.workspace_path / file_path
            file_status[file_path] = {
                "exists": full_path.exists(),
                "readable": full_path.exists() and os.access(full_path, os.R_OK),
                "size": full_path.stat().st_size if full_path.exists() else 0
            }
            
            if not file_status[file_path]["exists"]:
                all_present = False
                
        return {
            "all_files_present": all_present,
            "file_details": file_status,
            "missing_files": [f for f, s in file_status.items() if not s["exists"]]
        }
        
    def _validate_enhancement_config(self) -> bool:
        """Validate enhancement configuration"""
        try:
            config_file = self.config_path / "enhancements.json"
            
            if not config_file.exists():
                return False
                
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Check required keys
            required_keys = ["installed", "active", "dependencies"]
            for key in required_keys:
                if key not in config:
                    return False
                    
            return True
            
        except Exception:
            return False
            
    def _check_backup_integrity(self) -> Dict[str, Any]:
        """Check integrity of backup system"""
        valid_backups = []
        invalid_backups = []
        
        if not self.backup_path.exists():
            return {
                "backup_system_initialized": False,
                "valid_backups": [],
                "invalid_backups": []
            }
            
        for backup_dir in self.backup_path.iterdir():
            if backup_dir.is_dir():
                config_file = backup_dir / "config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r') as f:
                            json.load(f)  # Validate JSON
                        valid_backups.append(backup_dir.name)
                    except Exception:
                        invalid_backups.append(backup_dir.name)
                else:
                    invalid_backups.append(backup_dir.name)
                    
        return {
            "backup_system_initialized": True,
            "valid_backups": valid_backups,
            "invalid_backups": invalid_backups,
            "total_backups": len(valid_backups) + len(invalid_backups)
        }

# Convenience functions
def create_enhancement_installer(workspace_path: str = "/workspace") -> EnhancementInstaller:
    """Create and initialize an enhancement installer"""
    return EnhancementInstaller(workspace_path)

def quick_install_enhancements(workspace_path: str = "/workspace") -> Dict[str, Any]:
    """Quick installation of all available enhancements"""
    installer = create_enhancement_installer(workspace_path)
    return installer.install_enhancements()