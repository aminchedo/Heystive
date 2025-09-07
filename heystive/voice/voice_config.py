#!/usr/bin/env python3
"""
HEYSTIVE VOICE CONFIGURATION MANAGER
Manages voice settings, engine configurations, and user preferences
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class VoiceConfigManager:
    """
    Manages voice configuration for HeyStive
    Handles loading, saving, and updating voice settings
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("/workspace/heystive/config/voice_settings.yaml")
        self.config = {}
        self.user_preferences = {}
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_config()
    
    def load_config(self) -> bool:
        """Load voice configuration from YAML file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"Voice configuration loaded from {self.config_path}")
                return True
            else:
                # Create default configuration
                self._create_default_config()
                self.save_config()
                logger.info(f"Default voice configuration created at {self.config_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to load voice configuration: {e}")
            self._create_default_config()
            return False
    
    def save_config(self) -> bool:
        """Save voice configuration to YAML file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
            logger.info(f"Voice configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save voice configuration: {e}")
            return False
    
    def _create_default_config(self):
        """Create default voice configuration"""
        self.config = {
            'voice': {
                'enabled': True,
                'default_engine': 'kamtera_female',
                'auto_select_best': True,
                'audio': {
                    'sample_rate': 22050,
                    'output_format': 'wav',
                    'volume': 0.8,
                    'speed': 1.0,
                    'output_directory': '/workspace/heystive_audio_output'
                },
                'engines': {
                    'kamtera_female': {
                        'model_path': 'Kamtera/persian-tts-female-vits',
                        'enabled': True,
                        'quality': 'premium',
                        'voice_type': 'female',
                        'accent': 'persian',
                        'priority': 1
                    },
                    'kamtera_male': {
                        'model_path': 'Kamtera/persian-tts-male-vits',
                        'enabled': True,
                        'quality': 'high',
                        'voice_type': 'male',
                        'accent': 'persian',
                        'priority': 2
                    },
                    'informal_persian': {
                        'model_path': 'karim23657/persian-tts-female-GPTInformal-Persian-vits',
                        'enabled': True,
                        'quality': 'high',
                        'voice_type': 'female',
                        'accent': 'informal_persian',
                        'priority': 3
                    },
                    'google_tts': {
                        'model_path': 'Persian (fa) via gtts',
                        'enabled': True,
                        'quality': 'high',
                        'voice_type': 'neutral',
                        'accent': 'persian',
                        'priority': 4,
                        'requires_internet': True
                    },
                    'system_tts': {
                        'model_path': 'pyttsx3 with Persian optimization',
                        'enabled': True,
                        'quality': 'medium',
                        'voice_type': 'system',
                        'accent': 'system_default',
                        'priority': 5
                    },
                    'espeak_persian': {
                        'model_path': 'eSpeak-NG Persian fallback',
                        'enabled': True,
                        'quality': 'basic',
                        'voice_type': 'synthetic',
                        'accent': 'persian',
                        'priority': 6
                    }
                },
                'text_processing': {
                    'normalize_digits': True,
                    'normalize_persian_chars': True,
                    'remove_extra_spaces': True,
                    'max_text_length': 1000
                },
                'performance': {
                    'cache_models': True,
                    'parallel_processing': False,
                    'memory_limit_mb': 2048,
                    'timeout_seconds': 30
                },
                'user_preferences': {
                    'preferred_voice': 'kamtera_female',
                    'volume_level': 0.8,
                    'speech_rate': 1.0,
                    'auto_play': True,
                    'save_audio_files': True
                }
            }
        }
    
    def get_voice_enabled(self) -> bool:
        """Check if voice is enabled"""
        return self.config.get('voice', {}).get('enabled', True)
    
    def set_voice_enabled(self, enabled: bool) -> bool:
        """Enable or disable voice functionality"""
        if 'voice' not in self.config:
            self.config['voice'] = {}
        self.config['voice']['enabled'] = enabled
        return self.save_config()
    
    def get_default_engine(self) -> str:
        """Get the default TTS engine"""
        return self.config.get('voice', {}).get('default_engine', 'kamtera_female')
    
    def set_default_engine(self, engine_name: str) -> bool:
        """Set the default TTS engine"""
        if 'voice' not in self.config:
            self.config['voice'] = {}
        self.config['voice']['default_engine'] = engine_name
        return self.save_config()
    
    def get_engine_config(self, engine_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific engine"""
        engines = self.config.get('voice', {}).get('engines', {})
        return engines.get(engine_name)
    
    def set_engine_enabled(self, engine_name: str, enabled: bool) -> bool:
        """Enable or disable a specific engine"""
        if 'voice' not in self.config:
            self.config['voice'] = {}
        if 'engines' not in self.config['voice']:
            self.config['voice']['engines'] = {}
        if engine_name not in self.config['voice']['engines']:
            self.config['voice']['engines'][engine_name] = {}
        
        self.config['voice']['engines'][engine_name]['enabled'] = enabled
        return self.save_config()
    
    def get_enabled_engines(self) -> Dict[str, Dict[str, Any]]:
        """Get all enabled engines"""
        engines = self.config.get('voice', {}).get('engines', {})
        return {name: config for name, config in engines.items() 
                if config.get('enabled', True)}
    
    def get_audio_settings(self) -> Dict[str, Any]:
        """Get audio settings"""
        return self.config.get('voice', {}).get('audio', {})
    
    def set_audio_setting(self, setting: str, value: Any) -> bool:
        """Set an audio setting"""
        if 'voice' not in self.config:
            self.config['voice'] = {}
        if 'audio' not in self.config['voice']:
            self.config['voice']['audio'] = {}
        
        self.config['voice']['audio'][setting] = value
        return self.save_config()
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        return self.config.get('voice', {}).get('user_preferences', {})
    
    def set_user_preference(self, preference: str, value: Any) -> bool:
        """Set a user preference"""
        if 'voice' not in self.config:
            self.config['voice'] = {}
        if 'user_preferences' not in self.config['voice']:
            self.config['voice']['user_preferences'] = {}
        
        self.config['voice']['user_preferences'][preference] = value
        return self.save_config()
    
    def get_text_processing_settings(self) -> Dict[str, Any]:
        """Get text processing settings"""
        return self.config.get('voice', {}).get('text_processing', {})
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """Get performance settings"""
        return self.config.get('voice', {}).get('performance', {})
    
    def get_output_directory(self) -> str:
        """Get the output directory for audio files"""
        audio_settings = self.get_audio_settings()
        output_dir = audio_settings.get('output_directory', '/workspace/heystive_audio_output')
        
        # Ensure directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate the current configuration"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check if voice is enabled
        if not self.get_voice_enabled():
            validation_results['warnings'].append("Voice is disabled")
        
        # Check default engine
        default_engine = self.get_default_engine()
        if not default_engine:
            validation_results['errors'].append("No default engine specified")
            validation_results['valid'] = False
        
        # Check if default engine is enabled
        engine_config = self.get_engine_config(default_engine)
        if engine_config and not engine_config.get('enabled', True):
            validation_results['warnings'].append(f"Default engine '{default_engine}' is disabled")
        
        # Check enabled engines
        enabled_engines = self.get_enabled_engines()
        if not enabled_engines:
            validation_results['errors'].append("No engines are enabled")
            validation_results['valid'] = False
        
        # Check output directory
        output_dir = self.get_output_directory()
        if not os.path.exists(output_dir):
            try:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                validation_results['errors'].append(f"Cannot create output directory: {e}")
                validation_results['valid'] = False
        
        return validation_results
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        self._create_default_config()
        return self.save_config()
    
    def export_config(self, export_path: str) -> bool:
        """Export current configuration to a file"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
            logger.info(f"Configuration exported to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Import configuration from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = yaml.safe_load(f)
            
            if imported_config:
                self.config = imported_config
                return self.save_config()
            else:
                logger.error("Imported configuration is empty")
                return False
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False

# Test the configuration manager
if __name__ == "__main__":
    print("🧪 Testing Voice Configuration Manager...")
    
    # Create config manager
    config_manager = VoiceConfigManager()
    
    # Test basic functionality
    print(f"Voice enabled: {config_manager.get_voice_enabled()}")
    print(f"Default engine: {config_manager.get_default_engine()}")
    print(f"Output directory: {config_manager.get_output_directory()}")
    
    # List enabled engines
    enabled_engines = config_manager.get_enabled_engines()
    print(f"Enabled engines: {list(enabled_engines.keys())}")
    
    # Validate configuration
    validation = config_manager.validate_config()
    print(f"Configuration valid: {validation['valid']}")
    if validation['errors']:
        print(f"Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
    
    print("✅ Voice Configuration Manager test completed!")