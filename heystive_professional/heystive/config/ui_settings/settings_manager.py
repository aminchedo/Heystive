"""
Advanced Settings Management System
REAL IMPLEMENTATION - Production Ready
Handles settings for both web and desktop interfaces
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading
import copy

class AdvancedSettingsManager:
    """Thread-safe settings manager for Heystive interfaces"""
    
    def __init__(self):
        self.settings_dir = Path(__file__).parent
        self.settings_file = self.settings_dir / "heystive_settings.json"
        self.backup_dir = self.settings_dir / "backups"
        self.lock = threading.RLock()
        
        # Ensure directories exist
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Default settings structure
        self.default_settings = {
            "version": "2.0.0",
            "last_updated": None,
            "ui": {
                "theme": "dark",
                "language": "persian",
                "rtl_layout": True,
                "font_size": "medium",
                "animations_enabled": True,
                "sound_effects": True,
                "notification_sounds": True,
                "system_tray_enabled": True
            },
            "voice": {
                "wake_words": {
                    "persian": ["هی استو", "هی استیو", "های استیو", "استیو"],
                    "english": ["hey steve", "steve", "استیو"]
                },
                "sensitivity": 0.7,
                "noise_reduction": True,
                "auto_gain_control": True,
                "input_device": "default",
                "output_device": "default",
                "sample_rate": 16000,
                "channels": 1
            },
            "tts": {
                "default_engine": "piper",
                "voice_speed": 1.0,
                "voice_pitch": 1.0,
                "voice_volume": 0.8,
                "persian_voice": "fa_IR-gyro-medium",
                "english_voice": "en_US-lessac-medium",
                "output_format": "wav",
                "quality": "medium"
            },
            "service": {
                "auto_start": True,
                "run_on_startup": True,
                "minimize_to_tray": True,
                "show_notifications": True,
                "log_level": "INFO",
                "max_log_size_mb": 50,
                "keep_logs_days": 30
            },
            "advanced": {
                "api_timeout": 30,
                "max_retries": 3,
                "cache_enabled": True,
                "cache_size_mb": 100,
                "debug_mode": False,
                "performance_monitoring": True,
                "usage_analytics": False,
                "auto_updates": True
            },
            "shortcuts": {
                "activate_voice": "Ctrl+Shift+Space",
                "show_hide_ui": "Ctrl+Shift+H",
                "settings": "Ctrl+Comma",
                "quit": "Ctrl+Q"
            },
            "web_interface": {
                "port": 5001,
                "host": "localhost",
                "auto_open_browser": True,
                "enable_remote_access": False,
                "ssl_enabled": False,
                "session_timeout_minutes": 60
            },
            "desktop_interface": {
                "window_width": 1200,
                "window_height": 800,
                "remember_position": True,
                "always_on_top": False,
                "opacity": 1.0,
                "startup_minimized": False
            }
        }
        
        # Load or create settings
        self.settings = self.load_settings()
        
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file with validation"""
        with self.lock:
            try:
                if self.settings_file.exists():
                    with open(self.settings_file, 'r', encoding='utf-8') as f:
                        loaded_settings = json.load(f)
                    
                    # Validate and merge with defaults
                    merged_settings = self._merge_settings(self.default_settings, loaded_settings)
                    
                    # Update version if needed
                    if merged_settings.get("version") != self.default_settings["version"]:
                        merged_settings["version"] = self.default_settings["version"]
                        merged_settings["last_updated"] = datetime.now().isoformat()
                        self.save_settings(merged_settings)
                    
                    return merged_settings
                else:
                    # Create default settings file
                    settings = copy.deepcopy(self.default_settings)
                    settings["last_updated"] = datetime.now().isoformat()
                    self.save_settings(settings)
                    return settings
                    
            except Exception as e:
                print(f"Error loading settings: {e}")
                # Return default settings if loading fails
                return copy.deepcopy(self.default_settings)
                
    def _merge_settings(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded settings with defaults"""
        merged = copy.deepcopy(default)
        
        for key, value in loaded.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self._merge_settings(merged[key], value)
                else:
                    merged[key] = value
            else:
                merged[key] = value
                
        return merged
        
    def save_settings(self, settings: Optional[Dict[str, Any]] = None):
        """Save settings to file with backup"""
        with self.lock:
            try:
                if settings is None:
                    settings = self.settings
                    
                # Create backup before saving
                self._create_backup()
                
                # Update timestamp
                settings["last_updated"] = datetime.now().isoformat()
                
                # Save to file
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                
                self.settings = settings
                
            except Exception as e:
                print(f"Error saving settings: {e}")
                raise
                
    def _create_backup(self):
        """Create backup of current settings"""
        if self.settings_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"settings_backup_{timestamp}.json"
            
            try:
                import shutil
                shutil.copy2(self.settings_file, backup_file)
                
                # Keep only last 10 backups
                backups = sorted(self.backup_dir.glob("settings_backup_*.json"))
                if len(backups) > 10:
                    for old_backup in backups[:-10]:
                        old_backup.unlink()
                        
            except Exception as e:
                print(f"Warning: Could not create settings backup: {e}")
                
    def get_setting(self, path: str, default: Any = None) -> Any:
        """Get setting value using dot notation path"""
        with self.lock:
            keys = path.split('.')
            value = self.settings
            
            try:
                for key in keys:
                    value = value[key]
                return value
            except (KeyError, TypeError):
                return default
                
    def set_setting(self, path: str, value: Any):
        """Set setting value using dot notation path"""
        with self.lock:
            keys = path.split('.')
            settings = self.settings
            
            # Navigate to parent
            for key in keys[:-1]:
                if key not in settings:
                    settings[key] = {}
                settings = settings[key]
                
            # Set value
            settings[keys[-1]] = value
            
            # Save changes
            self.save_settings()
            
    def reset_to_defaults(self, section: Optional[str] = None):
        """Reset settings to defaults"""
        with self.lock:
            if section:
                if section in self.default_settings:
                    self.settings[section] = copy.deepcopy(self.default_settings[section])
                else:
                    raise ValueError(f"Unknown settings section: {section}")
            else:
                self.settings = copy.deepcopy(self.default_settings)
                
            self.save_settings()
            
    def export_settings(self, file_path: Path) -> bool:
        """Export settings to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
            
    def import_settings(self, file_path: Path) -> bool:
        """Import settings from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
                
            # Validate and merge
            merged_settings = self._merge_settings(self.default_settings, imported_settings)
            self.save_settings(merged_settings)
            
            return True
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
            
    def get_all_settings(self) -> Dict[str, Any]:
        """Get complete settings dictionary"""
        with self.lock:
            return copy.deepcopy(self.settings)
            
    def validate_settings(self) -> List[str]:
        """Validate current settings and return list of issues"""
        issues = []
        
        try:
            # Validate voice settings
            sensitivity = self.get_setting('voice.sensitivity', 0.7)
            if not 0.0 <= sensitivity <= 1.0:
                issues.append(f"Voice sensitivity must be between 0.0 and 1.0, got {sensitivity}")
                
            # Validate TTS settings
            speed = self.get_setting('tts.voice_speed', 1.0)
            if not 0.1 <= speed <= 3.0:
                issues.append(f"TTS speed must be between 0.1 and 3.0, got {speed}")
                
            # Validate service settings
            log_size = self.get_setting('service.max_log_size_mb', 50)
            if not isinstance(log_size, (int, float)) or log_size <= 0:
                issues.append(f"Log size must be positive number, got {log_size}")
                
            # Validate web interface settings
            port = self.get_setting('web_interface.port', 5001)
            if not isinstance(port, int) or not 1024 <= port <= 65535:
                issues.append(f"Web port must be between 1024 and 65535, got {port}")
                
        except Exception as e:
            issues.append(f"Settings validation error: {e}")
            
        return issues

# Global settings manager instance
_settings_manager = None

def get_settings_manager() -> AdvancedSettingsManager:
    """Get global settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = AdvancedSettingsManager()
    return _settings_manager

# Convenience functions
def get_setting(path: str, default: Any = None) -> Any:
    """Get setting value using dot notation"""
    return get_settings_manager().get_setting(path, default)

def set_setting(path: str, value: Any):
    """Set setting value using dot notation"""
    get_settings_manager().set_setting(path, value)

def save_settings():
    """Save current settings"""
    get_settings_manager().save_settings()

if __name__ == "__main__":
    # Test settings manager
    manager = AdvancedSettingsManager()
    
    print("Testing settings manager...")
    print(f"Theme: {manager.get_setting('ui.theme')}")
    print(f"Wake words: {manager.get_setting('voice.wake_words.persian')}")
    
    # Test validation
    issues = manager.validate_settings()
    if issues:
        print("Validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ Settings validation passed")