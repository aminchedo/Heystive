"""
Enhanced Model Downloader Utility
Wrapper around existing PersianModelDownloader with additional features
DO NOT MODIFY EXISTING TTS/STT ENGINES - This is a NEW utility module
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Import existing model downloader (DO NOT MODIFY IT)
sys.path.insert(0, str(Path(__file__).parent.parent))
from steve.models.download_models import PersianModelDownloader

logger = logging.getLogger(__name__)

class ModelDownloader:
    """
    Enhanced model downloading utility that wraps existing PersianModelDownloader
    Adds convenience methods and integration points WITHOUT modifying existing code
    """
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Use existing PersianModelDownloader (DO NOT MODIFY)
        self.persian_downloader = PersianModelDownloader(str(self.models_dir))
        
        # Additional features (NEW functionality)
        self.download_queue = []
        self.auto_download_enabled = False
        
    def check_existing_models(self) -> Dict[str, bool]:
        """
        Check which models are already downloaded
        Uses existing functionality without modification
        """
        try:
            available_models = self.persian_downloader.get_available_models()
            return {model_id: info["downloaded"] for model_id, info in available_models.items()}
        except Exception as e:
            logger.error(f"Error checking existing models: {e}")
            return {}
    
    async def download_missing_models(self, hardware_tier: str = "medium") -> List[str]:
        """
        Download only missing models based on hardware tier
        Enhances existing functionality without modifying it
        """
        try:
            logger.info(f"Downloading missing models for hardware tier: {hardware_tier}")
            
            # Use existing hardware tier download method
            successful_downloads = await self.persian_downloader.download_models_for_hardware_tier(hardware_tier)
            
            if successful_downloads:
                logger.info(f"Successfully downloaded {len(successful_downloads)} models")
            else:
                logger.warning("No models were downloaded")
                
            return successful_downloads
            
        except Exception as e:
            logger.error(f"Error downloading missing models: {e}")
            return []
    
    async def download_specific_model(self, model_id: str, force: bool = False) -> bool:
        """
        Download a specific model by ID
        Uses existing functionality
        """
        try:
            return await self.persian_downloader.download_model(model_id, force_download=force)
        except Exception as e:
            logger.error(f"Error downloading model {model_id}: {e}")
            return False
    
    def get_model_status(self) -> Dict[str, Any]:
        """
        Get comprehensive model status information
        Enhances existing functionality
        """
        try:
            # Get model info from existing downloader
            available_models = self.persian_downloader.get_available_models()
            download_stats = self.persian_downloader.get_download_stats()
            
            # Calculate additional statistics
            total_models = len(available_models)
            downloaded_models = sum(1 for info in available_models.values() if info["downloaded"])
            missing_models = total_models - downloaded_models
            
            return {
                "total_models": total_models,
                "downloaded_models": downloaded_models,
                "missing_models": missing_models,
                "download_completion": downloaded_models / total_models if total_models > 0 else 0,
                "models": available_models,
                "download_stats": download_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting model status: {e}")
            return {"error": str(e)}
    
    def get_model_path(self, model_id: str) -> Optional[Path]:
        """
        Get local path for a model if it exists
        Uses existing functionality
        """
        try:
            return self.persian_downloader.get_model_path(model_id)
        except Exception as e:
            logger.error(f"Error getting model path for {model_id}: {e}")
            return None
    
    def cleanup_unused_models(self, keep_models: List[str] = None) -> int:
        """
        Clean up unused models
        Uses existing functionality
        """
        try:
            return self.persian_downloader.cleanup_models(keep_models)
        except Exception as e:
            logger.error(f"Error cleaning up models: {e}")
            return 0
    
    async def auto_download_for_system(self) -> bool:
        """
        Automatically download appropriate models for current system
        NEW convenience method that uses existing functionality
        """
        try:
            # Detect system capabilities (basic detection)
            import psutil
            
            ram_gb = psutil.virtual_memory().total / (1024**3)
            cpu_cores = psutil.cpu_count()
            
            # Determine hardware tier based on system specs
            if ram_gb >= 16 and cpu_cores >= 8:
                hardware_tier = "high"
            elif ram_gb >= 8 and cpu_cores >= 4:
                hardware_tier = "medium"
            else:
                hardware_tier = "low"
            
            logger.info(f"Auto-detected hardware tier: {hardware_tier} (RAM: {ram_gb:.1f}GB, CPU: {cpu_cores} cores)")
            
            # Download models for detected tier
            successful_downloads = await self.download_missing_models(hardware_tier)
            
            return len(successful_downloads) > 0
            
        except Exception as e:
            logger.error(f"Auto-download failed: {e}")
            return False
    
    def validate_models(self) -> Dict[str, bool]:
        """
        Validate all downloaded models
        NEW convenience method
        """
        try:
            model_status = {}
            available_models = self.persian_downloader.get_available_models()
            
            for model_id, info in available_models.items():
                if info["downloaded"]:
                    model_path = self.get_model_path(model_id)
                    if model_path and model_path.exists():
                        # Basic validation - check if file is not empty
                        model_status[model_id] = model_path.stat().st_size > 1024
                    else:
                        model_status[model_id] = False
                else:
                    model_status[model_id] = False
            
            return model_status
            
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return {}

# Convenience function for easy importing
async def download_models_for_hardware(hardware_tier: str = "auto", models_dir: str = "./models") -> bool:
    """
    Convenience function to download models for specific hardware tier
    """
    try:
        downloader = ModelDownloader(models_dir)
        
        if hardware_tier == "auto":
            return await downloader.auto_download_for_system()
        else:
            successful_downloads = await downloader.download_missing_models(hardware_tier)
            return len(successful_downloads) > 0
            
    except Exception as e:
        logger.error(f"Hardware tier download failed: {e}")
        return False

# Convenience function for checking model availability
def check_model_availability(models_dir: str = "./models") -> Dict[str, bool]:
    """
    Convenience function to check which models are available
    """
    try:
        downloader = ModelDownloader(models_dir)
        return downloader.check_existing_models()
    except Exception as e:
        logger.error(f"Model availability check failed: {e}")
        return {}