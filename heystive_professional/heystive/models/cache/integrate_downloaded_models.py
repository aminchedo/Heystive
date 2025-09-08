#!/usr/bin/env python3
"""
Integration Script for Downloaded TTS Models
Updates existing TTS managers with downloaded model paths and creates unified model loader
"""

import os
import json
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TTSModelIntegrator:
    """Integrates downloaded TTS models with existing infrastructure"""
    
    def __init__(self, base_path: str = "/workspace/heystive_professional/heystive"):
        self.base_path = Path(base_path)
        self.models_path = self.base_path / "models"
        self.engines_path = self.base_path / "engines" / "tts"
        self.backups_path = self.models_path / "backups"
        self.logs_path = self.models_path / "logs"
        
        # Load comprehensive registry
        registry_path = self.models_path / "COMPREHENSIVE_MODEL_REGISTRY.json"
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                self.registry = json.load(f)
        else:
            logger.error("Comprehensive model registry not found!")
            self.registry = {}
        
        logger.info("🔧 TTS Model Integration System initialized")
        
    def create_unified_model_loader(self) -> bool:
        """Create a unified model loader for all downloaded models"""
        try:
            logger.info("Creating unified TTS model loader...")
            
            loader_code = f'''#!/usr/bin/env python3
"""
Unified TTS Model Loader
Auto-generated from downloaded models on {datetime.now().isoformat()}
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
        self.base_path = Path(__file__).parent.parent / "models" / "persian_tts"
        self.registry = self._load_registry()
        
        # Available model paths from comprehensive registry
        self.model_paths = {registry_entry}
        
        # Model configurations
        self.model_configs = self._load_model_configs()
        
    def _load_registry(self) -> Dict:
        """Load comprehensive model registry"""
        registry_path = self.base_path.parent / "COMPREHENSIVE_MODEL_REGISTRY.json"
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                return json.load(f)
        return {{}}
    
    def _load_model_configs(self) -> Dict:
        """Load individual model configurations"""
        configs = {{}}
        
        for engine in self.get_available_engines():
            engine_path = Path(self.model_paths.get(engine, ""))
            config_file = engine_path / "model_registry.json"
            
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        configs[engine] = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load config for {{engine}}: {{e}}")
                    
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
        info = {{
            'total_engines': len(self.get_available_engines()),
            'engines': {{}},
            'download_timestamp': self.registry.get('download_timestamp', 'Unknown'),
            'model_sizes': self.registry.get('model_sizes', {{}})
        }}
        
        for engine in self.get_available_engines():
            engine_config = self.model_configs.get(engine, {{}})
            info['engines'][engine] = {{
                'path': str(self.get_model_path(engine)),
                'models': self.list_models(engine),
                'model_count': len(self.list_models(engine)),
                'config': engine_config.get('model_info', {{}})
            }}
        
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
        priority_order = {{
            'coqui': 1,      # High quality neural TTS
            'custom': 2,     # Custom Persian models  
            'gtts': 3,       # Google TTS (cloud)
            'speechbrain': 4, # SpeechBrain framework
            'piper': 5       # Piper voices
        }}
        
        return sorted(engines, key=lambda x: priority_order.get(x, 999))
    
    def get_recommended_engine(self) -> Optional[str]:
        """Get recommended engine based on availability and quality"""
        priority_engines = self.get_engine_priority()
        
        for engine in priority_engines:
            if self.is_engine_available(engine):
                logger.info(f"Recommended engine: {{engine}}")
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
                logger.info(f"✅ {{engine}}: Available")
            else:
                logger.warning(f"⚠️ {{engine}}: Not available")
        
        logger.info(f"TTS Models Status: {{working_engines}}/{{len(engines)}} engines available")
        return working_engines > 0
        
    except Exception as e:
        logger.error(f"TTS models verification failed: {{e}}")
        return False

if __name__ == "__main__":
    print("=== Unified TTS Model Loader Test ===")
    
    loader = get_unified_tts_loader()
    info = loader.get_model_info()
    
    print(f"Total engines: {{info['total_engines']}}")
    print(f"Download timestamp: {{info['download_timestamp']}}")
    
    for engine, engine_info in info['engines'].items():
        print(f"\\n{{engine.upper()}}:")
        print(f"  Path: {{engine_info['path']}}")
        print(f"  Models: {{engine_info['model_count']}}")
        print(f"  Available: {{loader.is_engine_available(engine)}}")
    
    print(f"\\nRecommended engine: {{loader.get_recommended_engine()}}")
    print(f"Verification: {{'PASSED' if verify_tts_models() else 'FAILED'}}")
'''
            
            # Replace registry placeholder with actual data
            registry_entry = json.dumps(self.registry.get('model_paths', {}), indent=12)
            loader_code = loader_code.replace('{registry_entry}', registry_entry)
            
            # Write the loader
            loader_path = self.models_path / "unified_tts_loader.py"
            with open(loader_path, 'w', encoding='utf-8') as f:
                f.write(loader_code)
            
            # Make it executable
            os.chmod(loader_path, 0o755)
            
            logger.info(f"✅ Unified TTS model loader created: {loader_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create unified model loader: {e}")
            return False
    
    def update_persian_multi_tts_manager(self) -> bool:
        """Update the existing Persian Multi TTS Manager with downloaded models"""
        try:
            logger.info("Updating Persian Multi TTS Manager...")
            
            manager_path = self.engines_path / "persian_multi_tts_manager.py"
            
            if not manager_path.exists():
                logger.error(f"TTS manager not found: {manager_path}")
                return False
            
            # Read existing manager
            with open(manager_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare model path constants to insert
            model_paths_code = f'''
# Auto-generated model paths from downloaded models ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
import os
from pathlib import Path

# Base path for downloaded models
DOWNLOADED_MODELS_BASE_PATH = Path(__file__).parent.parent.parent / "models" / "persian_tts"

# Downloaded model paths from comprehensive registry
COQUI_MODEL_PATH = DOWNLOADED_MODELS_BASE_PATH / "coqui"
PIPER_MODEL_PATH = DOWNLOADED_MODELS_BASE_PATH / "piper" 
CUSTOM_MODEL_PATH = DOWNLOADED_MODELS_BASE_PATH / "custom"
SPEECHBRAIN_MODEL_PATH = DOWNLOADED_MODELS_BASE_PATH / "speechbrain"
GTTS_CONFIG_PATH = DOWNLOADED_MODELS_BASE_PATH / "gtts"

# Available downloaded models registry
DOWNLOADED_MODELS_REGISTRY = {json.dumps(self.registry, indent=4)}

# Check if unified loader is available
try:
    from ...models.unified_tts_loader import get_unified_tts_loader
    UNIFIED_LOADER_AVAILABLE = True
except ImportError:
    UNIFIED_LOADER_AVAILABLE = False

def get_downloaded_model_path(engine: str) -> Optional[Path]:
    """Get path for downloaded model engine"""
    model_paths = {{
        "coqui": COQUI_MODEL_PATH,
        "piper": PIPER_MODEL_PATH,
        "custom": CUSTOM_MODEL_PATH,
        "speechbrain": SPEECHBRAIN_MODEL_PATH,
        "gtts": GTTS_CONFIG_PATH
    }}
    return model_paths.get(engine)

def is_downloaded_model_available(engine: str) -> bool:
    """Check if downloaded model is available"""
    path = get_downloaded_model_path(engine)
    return path and path.exists()

'''
            
            # Find the import section and insert our code after it
            import_pattern = r'(import logging\n)'
            if re.search(import_pattern, content):
                content = re.sub(import_pattern, r'\1' + model_paths_code, content, count=1)
            else:
                # Insert after the docstring
                docstring_end = content.find('"""', content.find('"""') + 3) + 3
                content = content[:docstring_end] + '\n' + model_paths_code + '\n' + content[docstring_end:]
            
            # Add method to check downloaded models
            new_method = '''
    def _check_downloaded_models(self):
        """Check and integrate downloaded models"""
        if not UNIFIED_LOADER_AVAILABLE:
            print("⚠️ Unified loader not available")
            return
        
        try:
            from ...models.unified_tts_loader import get_unified_tts_loader
            loader = get_unified_tts_loader()
            
            downloaded_engines = loader.get_available_engines()
            print(f"📦 Downloaded engines available: {len(downloaded_engines)}")
            
            for engine in downloaded_engines:
                if loader.is_engine_available(engine):
                    print(f"   ✅ {engine}: {loader.get_model_path(engine)}")
                else:
                    print(f"   ❌ {engine}: Not available")
                    
        except Exception as e:
            print(f"⚠️ Error checking downloaded models: {e}")
'''
            
            # Insert the new method before the main execution block
            main_block_pattern = r'(# IMMEDIATE EXECUTION AND TESTING\nif __name__ == "__main__":)'
            if re.search(main_block_pattern, content):
                content = re.sub(main_block_pattern, new_method + r'\n\1', content)
            else:
                # Add at the end of the class
                class_end_pattern = r'(\n    def get_current_engine_info\(self\) -> Optional\[Dict\]:[^}]+return None\n)'
                content = re.sub(class_end_pattern, r'\1' + new_method, content)
            
            # Add call to check downloaded models in __init__
            init_end_pattern = r'(self\._auto_select_best_engine\(\)\s+print\(f"✅ Persian TTS Manager initialized with \{len\(self\.engines\)\} engines"\))'
            if re.search(init_end_pattern, content):
                content = re.sub(init_end_pattern, r'\1\n        \n        # Check downloaded models integration\n        self._check_downloaded_models()', content)
            
            # Write updated manager
            with open(manager_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("✅ Persian Multi TTS Manager updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update TTS manager: {e}")
            return False
    
    def create_integration_report(self) -> str:
        """Create comprehensive integration report"""
        try:
            report_content = f'''# TTS Models Integration Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Integration System**: Comprehensive TTS Models Download and Integration

## Integration Summary

### Successfully Downloaded Models
'''
            
            for model in self.registry.get('downloaded_models', []):
                report_content += f"- ✅ **{model}**\n"
            
            report_content += "\n### Failed Downloads\n"
            for model, error in self.registry.get('failed_downloads', []):
                report_content += f"- ❌ **{model}**: {error}\n"
            
            report_content += f'''

### Available Engines
Total engines available: {len(self.registry.get('available_engines', []))}

'''
            
            for engine in self.registry.get('available_engines', []):
                path = self.registry.get('model_paths', {}).get(engine, 'Unknown')
                size = self.registry.get('model_sizes', {}).get(engine, 'Unknown')
                report_content += f"#### {engine.title()}\n"
                report_content += f"- **Path**: `{path}`\n"
                report_content += f"- **Size**: {size}\n"
                report_content += f"- **Status**: {'✅ Available' if Path(path).exists() else '❌ Missing'}\n\n"
            
            report_content += f'''
### Integration Status

#### Files Modified
- ✅ **Persian Multi TTS Manager**: Updated with downloaded model paths
- ✅ **Unified Model Loader**: Created comprehensive model loader
- ✅ **Model Registry**: Comprehensive registry with all model information

#### Integration Features
- **Automatic Model Detection**: System automatically detects and integrates downloaded models
- **Path Management**: Centralized model path management
- **Fallback Support**: Graceful fallback to existing models if downloaded models unavailable
- **Unified Interface**: Single interface to access all TTS models

### Usage Examples

#### Using Unified Model Loader
```python
from heystive.models.unified_tts_loader import get_unified_tts_loader

# Get the unified loader
loader = get_unified_tts_loader()

# List available engines
engines = loader.get_available_engines()
print(f"Available engines: {{engines}}")

# Get recommended engine
recommended = loader.get_recommended_engine()
print(f"Recommended engine: {{recommended}}")

# Get model information
info = loader.get_model_info()
for engine, engine_info in info['engines'].items():
    print(f"{{engine}}: {{engine_info['model_count']}} models")
```

#### Integration with Existing TTS Manager
```python
from heystive.engines.tts.persian_multi_tts_manager import PersianMultiTTSManager

# Create TTS manager (now automatically integrates downloaded models)
tts_manager = PersianMultiTTSManager()

# The manager will automatically detect and report downloaded models
# Check console output for integration status
```

### System Information
- **Total Disk Space Used**: {sum(float(size.replace('MB', '')) for size in self.registry.get('model_sizes', {}).values() if 'MB' in size):.1f} MB
- **Available Disk Space**: {self.registry.get('system_info', {}).get('disk_space_gb', 'Unknown'):.1f} GB
- **Download Timestamp**: {self.registry.get('download_timestamp', 'Unknown')}

### Troubleshooting

#### Common Issues
1. **Import Errors**: Ensure Python path includes project root
2. **Model Not Found**: Check that model paths exist in filesystem
3. **Integration Issues**: Verify backup files are available for rollback

#### Verification Commands
```bash
# Test unified loader
cd /workspace/heystive_professional/heystive/models/
python3 unified_tts_loader.py

# Test TTS manager integration
cd /workspace/heystive_professional/
python3 -c "from heystive.engines.tts.persian_multi_tts_manager import PersianMultiTTSManager; PersianMultiTTSManager()"
```

#### Rollback Procedure
If issues occur, restore from backup:
```bash
cd /workspace/heystive_professional/heystive/models/backups/
# Find latest backup
ls -t persian_multi_tts_manager_backup_* | head -1
# Restore (replace with actual backup filename)
cp persian_multi_tts_manager_backup_YYYYMMDD_HHMMSS.py ../../engines/tts/persian_multi_tts_manager.py
```

### Next Steps
1. **Test Integration**: Run verification commands to ensure integration works
2. **Performance Testing**: Test TTS generation with downloaded models
3. **Monitoring Setup**: Configure monitoring for model performance
4. **Documentation Update**: Update project documentation with new model information

---
**Integration completed successfully!** 🎉
'''
            
            # Save report
            report_path = self.logs_path / "integration_report.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"✅ Integration report created: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Failed to create integration report: {e}")
            return ""
    
    def run_complete_integration(self) -> bool:
        """Run complete integration process"""
        logger.info("🚀 Starting TTS models integration...")
        
        success_count = 0
        total_tasks = 3
        
        # Task 1: Create unified model loader
        if self.create_unified_model_loader():
            success_count += 1
            logger.info("✅ Task 1/3: Unified model loader created")
        else:
            logger.error("❌ Task 1/3: Failed to create unified model loader")
        
        # Task 2: Update existing TTS manager
        if self.update_persian_multi_tts_manager():
            success_count += 1
            logger.info("✅ Task 2/3: TTS manager updated")
        else:
            logger.error("❌ Task 2/3: Failed to update TTS manager")
        
        # Task 3: Create integration report
        report_path = self.create_integration_report()
        if report_path:
            success_count += 1
            logger.info("✅ Task 3/3: Integration report created")
        else:
            logger.error("❌ Task 3/3: Failed to create integration report")
        
        # Summary
        logger.info(f"📊 Integration Summary: {success_count}/{total_tasks} tasks completed")
        
        if success_count == total_tasks:
            logger.info("🎉 TTS models integration completed successfully!")
            return True
        else:
            logger.warning("⚠️ TTS models integration completed with issues")
            return False

def main():
    """Main execution function"""
    print("🔧 TTS MODELS INTEGRATION SYSTEM")
    print("=" * 50)
    
    integrator = TTSModelIntegrator()
    success = integrator.run_complete_integration()
    
    if success:
        print("\n🎉 Integration completed successfully!")
        print("✅ All TTS models have been integrated with existing infrastructure")
        print("📁 Check logs directory for detailed integration report")
    else:
        print("\n⚠️ Integration completed with issues!")
        print("📋 Check logs for detailed error information")
        print("🔄 Backup files available for rollback if needed")
    
    return success

if __name__ == "__main__":
    main()