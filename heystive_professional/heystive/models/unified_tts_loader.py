#!/usr/bin/env python3
"""
Unified TTS Model Loader
Auto-generated from downloaded models on 2025-09-08T02:42:46
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class UnifiedTTSModelLoader:
    """Unified loader for all downloaded TTS models"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent / "persian_tts"
        self.registry = self._load_registry()
        
        # Available model paths from comprehensive registry
        self.model_paths = {
            "coqui": "/workspace/heystive_professional/heystive/models/persian_tts/coqui",
            "gtts": "/workspace/heystive_professional/heystive/models/persian_tts/gtts",
            "speechbrain": "/workspace/heystive_professional/heystive/models/persian_tts/speechbrain",
            "piper": "/workspace/heystive_professional/heystive/models/persian_tts/piper",
            "custom": "/workspace/heystive_professional/heystive/models/persian_tts/custom"
        }
        
        # Model configurations
        self.model_configs = self._load_model_configs()
        
    def _load_registry(self) -> Dict:
        """Load comprehensive model registry"""
        registry_path = self.base_path.parent / "COMPREHENSIVE_MODEL_REGISTRY.json"
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_model_configs(self) -> Dict:
        """Load individual model configurations"""
        configs = {}
        
        for engine in self.get_available_engines():
            engine_path = Path(self.model_paths.get(engine, ""))
            config_file = engine_path / "model_registry.json"
            
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        configs[engine] = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load config for {engine}: {e}")
                    
        return configs
    
    def get_available_engines(self) -> List[str]:
        """Get list of available TTS engines"""
        return self.registry.get('available_engines', [])
    
    def get_downloaded_models(self) -> List[str]:
        """Get list of successfully downloaded models"""
        return self.registry.get('downloaded_models', [])
    
    def get_model_path(self, engine: str) -> Optional[Path]:
        """Get model path for specific engine"""
        if engine in self.model_paths:
            return Path(self.model_paths[engine])
        return None
    
    def list_models(self, engine: str) -> List[str]:
        """List available models for engine"""
        engine_path = self.get_model_path(engine)
        if not engine_path or not engine_path.exists():
            return []
        
        models = []
        # Look for common model file extensions
        for ext in ['*.pt', '*.pth', '*.onnx', '*.bin', '*.json', '*.py']:
            models.extend([f.name for f in engine_path.rglob(ext)])
        return sorted(set(models))
    
    def get_model_info(self) -> Dict:
        """Get comprehensive model information"""
        info = {
            'total_engines': len(self.get_available_engines()),
            'engines': {},
            'download_timestamp': self.registry.get('download_timestamp', 'Unknown'),
            'model_sizes': self.registry.get('model_sizes', {})
        }
        
        for engine in self.get_available_engines():
            engine_config = self.model_configs.get(engine, {})
            info['engines'][engine] = {
                'path': str(self.get_model_path(engine)),
                'models': self.list_models(engine),
                'model_count': len(self.list_models(engine)),
                'config': engine_config.get('model_info', {})
            }
        
        return info
    
    def get_engine_config(self, engine: str) -> Optional[Dict]:
        """Get configuration for specific engine"""
        return self.model_configs.get(engine)
    
    def is_engine_available(self, engine: str) -> bool:
        """Check if engine is available and has models"""
        if engine not in self.get_available_engines():
            return False
        
        engine_path = self.get_model_path(engine)
        return engine_path and engine_path.exists()
    
    def get_engine_priority(self) -> List[str]:
        """Get engines ordered by priority (quality and availability)"""
        engines = self.get_available_engines()
        
        # Priority order based on quality and type
        priority_order = {
            'coqui': 1,      # High quality neural TTS
            'custom': 2,     # Custom Persian models  
            'gtts': 3,       # Google TTS (cloud)
            'speechbrain': 4, # SpeechBrain framework
            'piper': 5       # Piper voices
        }
        
        return sorted(engines, key=lambda x: priority_order.get(x, 999))
    
    def get_recommended_engine(self) -> Optional[str]:
        """Get recommended engine based on availability and quality"""
        priority_engines = self.get_engine_priority()
        
        for engine in priority_engines:
            if self.is_engine_available(engine):
                logger.info(f"Recommended engine: {engine}")
                return engine
        
        return None

# Global instance
_unified_loader = None

def get_unified_tts_loader() -> UnifiedTTSModelLoader:
    """Get the global unified TTS model loader instance"""
    global _unified_loader
    if _unified_loader is None:
        _unified_loader = UnifiedTTSModelLoader()
    return _unified_loader

def verify_tts_models() -> bool:
    """Verify TTS models installation"""
    try:
        loader = get_unified_tts_loader()
        engines = loader.get_available_engines()
        
        if not engines:
            logger.error("No TTS engines available")
            return False
        
        working_engines = 0
        for engine in engines:
            if loader.is_engine_available(engine):
                working_engines += 1
                logger.info(f"✅ {engine}: Available")
            else:
                logger.warning(f"⚠️ {engine}: Not available")
        
        logger.info(f"TTS Models Status: {working_engines}/{len(engines)} engines available")
        return working_engines > 0
        
    except Exception as e:
        logger.error(f"TTS models verification failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Unified TTS Model Loader Test ===")
    
    loader = get_unified_tts_loader()
    info = loader.get_model_info()
    
    print(f"Total engines: {info['total_engines']}")
    print(f"Download timestamp: {info['download_timestamp']}")
    
    for engine, engine_info in info['engines'].items():
        print(f"\n{engine.upper()}:")
        print(f"  Path: {engine_info['path']}")
        print(f"  Models: {engine_info['model_count']}")
        print(f"  Available: {loader.is_engine_available(engine)}")
    
    print(f"\nRecommended engine: {loader.get_recommended_engine()}")
    print(f"Verification: {'PASSED' if verify_tts_models() else 'FAILED'}")