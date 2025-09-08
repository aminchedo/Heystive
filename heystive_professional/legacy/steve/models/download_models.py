"""
Persian Model Downloader
Downloads and manages Persian language models for Steve Voice Assistant
"""

import asyncio
import logging
import os
import requests
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import json
import time
import zipfile
import tarfile
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class PersianModelDownloader:
    """
    Advanced Persian model downloader and manager
    Handles Whisper, TTS, and other Persian language models
    """
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Model registry
        self.model_registry = self._load_model_registry()
        
        # Download statistics
        self.download_stats = {
            "total_downloads": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "total_bytes_downloaded": 0,
            "download_times": {}
        }
        
        # Create subdirectories
        self._create_model_directories()
    
    def _create_model_directories(self):
        """Create model subdirectories"""
        subdirs = ["whisper", "tts", "wake_word", "embeddings", "cache"]
        
        for subdir in subdirs:
            (self.models_dir / subdir).mkdir(exist_ok=True)
    
    def _load_model_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load model registry with Persian language models"""
        return {
            # Whisper models for Persian STT
            "whisper_tiny": {
                "name": "Whisper Tiny",
                "description": "Smallest Whisper model for Persian speech recognition",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e/tiny.pt",
                "size_mb": 39,
                "checksum": "65147644a518d12f04e32d6f3b26facc3f8dd46e",
                "type": "whisper",
                "language": "multilingual",
                "quality": "basic",
                "hardware_requirements": "minimal"
            },
            "whisper_small": {
                "name": "Whisper Small",
                "description": "Small Whisper model for Persian speech recognition",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/small.pt",
                "size_mb": 244,
                "checksum": "ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e",
                "type": "whisper",
                "language": "multilingual",
                "quality": "good",
                "hardware_requirements": "low"
            },
            "whisper_medium": {
                "name": "Whisper Medium",
                "description": "Medium Whisper model for Persian speech recognition",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt",
                "size_mb": 769,
                "checksum": "345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1",
                "type": "whisper",
                "language": "multilingual",
                "quality": "excellent",
                "hardware_requirements": "medium"
            },
            "whisper_large_v3": {
                "name": "Whisper Large v3",
                "description": "Latest large Whisper model for Persian speech recognition",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt",
                "size_mb": 1550,
                "checksum": "e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb",
                "type": "whisper",
                "language": "multilingual",
                "quality": "premium",
                "hardware_requirements": "high"
            },
            
            # Persian TTS models
            "kamtera_female_vits": {
                "name": "Kamtera Female VITS",
                "description": "High-quality Persian female voice TTS model",
                "url": "https://huggingface.co/Kamtera/persian-tts-female-vits/resolve/main/checkpoint_88000.pth",
                "config_url": "https://huggingface.co/Kamtera/persian-tts-female-vits/resolve/main/config.json",
                "size_mb": 120,
                "checksum": "",  # Would need to be determined
                "type": "tts_vits",
                "language": "persian",
                "voice": "female",
                "quality": "premium",
                "hardware_requirements": "medium"
            },
            "kamtera_male_vits": {
                "name": "Kamtera Male VITS",
                "description": "High-quality Persian male voice TTS model",
                "url": "https://huggingface.co/Kamtera/persian-tts-male-vits/resolve/main/best_model_91323.pth",
                "config_url": "https://huggingface.co/Kamtera/persian-tts-male-vits/resolve/main/config.json",
                "size_mb": 120,
                "checksum": "",
                "type": "tts_vits",
                "language": "persian",
                "voice": "male",
                "quality": "premium",
                "hardware_requirements": "medium"
            },
            "facebook_mms_persian": {
                "name": "Facebook MMS Persian",
                "description": "Facebook's Massively Multilingual Speech Persian TTS",
                "url": "https://huggingface.co/facebook/mms-tts-fas/resolve/main/pytorch_model.bin",
                "config_url": "https://huggingface.co/facebook/mms-tts-fas/resolve/main/config.json",
                "size_mb": 180,
                "checksum": "",
                "type": "tts_transformers",
                "language": "persian",
                "voice": "neutral",
                "quality": "good",
                "hardware_requirements": "medium"
            },
            
            # Persian embeddings for semantic understanding
            "persian_sentence_transformers": {
                "name": "Persian Sentence Transformers",
                "description": "Persian sentence embeddings for semantic understanding",
                "url": "https://huggingface.co/HooshvareLab/bert-fa-base-uncased/resolve/main/pytorch_model.bin",
                "config_url": "https://huggingface.co/HooshvareLab/bert-fa-base-uncased/resolve/main/config.json",
                "size_mb": 440,
                "checksum": "",
                "type": "embeddings",
                "language": "persian",
                "quality": "excellent",
                "hardware_requirements": "medium"
            }
        }
    
    async def download_model(self, model_id: str, force_download: bool = False) -> bool:
        """
        Download a specific model
        
        Args:
            model_id: Model identifier from registry
            force_download: Force download even if model exists
            
        Returns:
            True if download successful
        """
        try:
            if model_id not in self.model_registry:
                logger.error(f"Model {model_id} not found in registry")
                return False
            
            model_info = self.model_registry[model_id]
            model_path = self._get_model_path(model_id, model_info)
            
            # Check if model already exists
            if model_path.exists() and not force_download:
                logger.info(f"Model {model_id} already exists at {model_path}")
                return True
            
            logger.info(f"Downloading model: {model_info['name']} ({model_info['size_mb']}MB)")
            
            # Update download stats
            self.download_stats["total_downloads"] += 1
            start_time = time.time()
            
            # Download main model file
            success = await self._download_file(
                model_info["url"], 
                model_path,
                model_info.get("checksum", "")
            )
            
            if not success:
                self.download_stats["failed_downloads"] += 1
                return False
            
            # Download config file if available
            if "config_url" in model_info:
                config_path = model_path.parent / f"{model_path.stem}_config.json"
                await self._download_file(model_info["config_url"], config_path)
            
            # Update download stats
            download_time = time.time() - start_time
            self.download_stats["successful_downloads"] += 1
            self.download_stats["download_times"][model_id] = download_time
            self.download_stats["total_bytes_downloaded"] += model_info["size_mb"] * 1024 * 1024
            
            logger.info(f"Model {model_id} downloaded successfully in {download_time:.2f}s")
            
            # Verify model integrity
            if await self._verify_model(model_id, model_path):
                logger.info(f"Model {model_id} verification successful")
                return True
            else:
                logger.warning(f"Model {model_id} verification failed")
                return False
            
        except Exception as e:
            logger.error(f"Model download failed for {model_id}: {e}")
            self.download_stats["failed_downloads"] += 1
            return False
    
    async def _download_file(self, url: str, file_path: Path, expected_checksum: str = "") -> bool:
        """Download a file with progress tracking"""
        try:
            logger.info(f"Downloading {url} to {file_path}")
            
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download with streaming
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Log progress every 10MB
                        if downloaded_size % (10 * 1024 * 1024) == 0:
                            progress = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                            logger.info(f"Download progress: {progress:.1f}%")
            
            # Verify checksum if provided
            if expected_checksum:
                if not await self._verify_checksum(file_path, expected_checksum):
                    logger.error(f"Checksum verification failed for {file_path}")
                    file_path.unlink()  # Delete corrupted file
                    return False
            
            logger.info(f"File downloaded successfully: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"File download failed: {e}")
            if file_path.exists():
                file_path.unlink()  # Clean up partial download
            return False
    
    async def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum"""
        try:
            sha256_hash = hashlib.sha256()
            
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_checksum = sha256_hash.hexdigest()
            return actual_checksum == expected_checksum
            
        except Exception as e:
            logger.error(f"Checksum verification failed: {e}")
            return False
    
    def _get_model_path(self, model_id: str, model_info: Dict[str, Any]) -> Path:
        """Get the local path for a model"""
        model_type = model_info["type"]
        
        # Determine subdirectory based on model type
        if model_type == "whisper":
            subdir = "whisper"
            extension = ".pt"
        elif model_type.startswith("tts"):
            subdir = "tts"
            extension = ".pth" if "vits" in model_type else ".bin"
        elif model_type == "embeddings":
            subdir = "embeddings"
            extension = ".bin"
        else:
            subdir = "cache"
            extension = ".bin"
        
        # Extract filename from URL or use model_id
        url_path = urlparse(model_info["url"]).path
        if url_path:
            filename = Path(url_path).name
        else:
            filename = f"{model_id}{extension}"
        
        return self.models_dir / subdir / filename
    
    async def _verify_model(self, model_id: str, model_path: Path) -> bool:
        """Verify model integrity and compatibility"""
        try:
            model_info = self.model_registry[model_id]
            model_type = model_info["type"]
            
            # Basic file existence and size check
            if not model_path.exists():
                return False
            
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            expected_size_mb = model_info["size_mb"]
            
            # Allow 10% variance in file size
            if abs(file_size_mb - expected_size_mb) > expected_size_mb * 0.1:
                logger.warning(f"Model size mismatch: expected {expected_size_mb}MB, got {file_size_mb:.1f}MB")
                return False
            
            # Type-specific verification
            if model_type == "whisper":
                return await self._verify_whisper_model(model_path)
            elif model_type.startswith("tts"):
                return await self._verify_tts_model(model_path)
            elif model_type == "embeddings":
                return await self._verify_embeddings_model(model_path)
            else:
                # Generic verification - just check if file is readable
                return model_path.is_file() and model_path.stat().st_size > 0
            
        except Exception as e:
            logger.error(f"Model verification failed: {e}")
            return False
    
    async def _verify_whisper_model(self, model_path: Path) -> bool:
        """Verify Whisper model"""
        try:
            import torch
            
            # Try to load the model
            model = torch.load(model_path, map_location="cpu")
            
            # Check if it has expected Whisper structure
            expected_keys = ["dims", "model_state_dict"]
            for key in expected_keys:
                if key not in model:
                    logger.warning(f"Whisper model missing key: {key}")
                    return False
            
            logger.info("Whisper model verification successful")
            return True
            
        except ImportError:
            logger.warning("PyTorch not available for Whisper model verification")
            return True  # Assume valid if we can't verify
        except Exception as e:
            logger.error(f"Whisper model verification failed: {e}")
            return False
    
    async def _verify_tts_model(self, model_path: Path) -> bool:
        """Verify TTS model"""
        try:
            # Basic file format check
            if model_path.suffix in [".pth", ".pt"]:
                import torch
                model = torch.load(model_path, map_location="cpu")
                return isinstance(model, dict)
            elif model_path.suffix == ".bin":
                # Assume it's a valid binary model file
                return model_path.stat().st_size > 1024  # At least 1KB
            else:
                return True
                
        except ImportError:
            logger.warning("PyTorch not available for TTS model verification")
            return True
        except Exception as e:
            logger.error(f"TTS model verification failed: {e}")
            return False
    
    async def _verify_embeddings_model(self, model_path: Path) -> bool:
        """Verify embeddings model"""
        try:
            # Basic file check
            return model_path.stat().st_size > 1024 * 1024  # At least 1MB
            
        except Exception as e:
            logger.error(f"Embeddings model verification failed: {e}")
            return False
    
    async def download_models_for_hardware_tier(self, hardware_tier: str) -> List[str]:
        """
        Download appropriate models for hardware tier
        
        Args:
            hardware_tier: "high", "medium", or "low"
            
        Returns:
            List of successfully downloaded model IDs
        """
        try:
            logger.info(f"Downloading models for hardware tier: {hardware_tier}")
            
            # Select models based on hardware tier
            if hardware_tier == "high":
                model_ids = [
                    "whisper_large_v3",
                    "kamtera_female_vits",
                    "persian_sentence_transformers"
                ]
            elif hardware_tier == "medium":
                model_ids = [
                    "whisper_medium",
                    "facebook_mms_persian",
                    "persian_sentence_transformers"
                ]
            else:  # low
                model_ids = [
                    "whisper_small",
                    "facebook_mms_persian"
                ]
            
            # Download models in parallel
            download_tasks = []
            for model_id in model_ids:
                task = asyncio.create_task(self.download_model(model_id))
                download_tasks.append((model_id, task))
            
            # Wait for all downloads
            successful_downloads = []
            for model_id, task in download_tasks:
                try:
                    success = await task
                    if success:
                        successful_downloads.append(model_id)
                        logger.info(f"Successfully downloaded: {model_id}")
                    else:
                        logger.error(f"Failed to download: {model_id}")
                except Exception as e:
                    logger.error(f"Download task failed for {model_id}: {e}")
            
            logger.info(f"Downloaded {len(successful_downloads)}/{len(model_ids)} models for {hardware_tier} tier")
            return successful_downloads
            
        except Exception as e:
            logger.error(f"Hardware tier model download failed: {e}")
            return []
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available models with download status"""
        available_models = {}
        
        for model_id, model_info in self.model_registry.items():
            model_path = self._get_model_path(model_id, model_info)
            
            available_models[model_id] = {
                "name": model_info["name"],
                "description": model_info["description"],
                "type": model_info["type"],
                "language": model_info["language"],
                "quality": model_info["quality"],
                "size_mb": model_info["size_mb"],
                "hardware_requirements": model_info["hardware_requirements"],
                "downloaded": model_path.exists(),
                "local_path": str(model_path) if model_path.exists() else None
            }
        
        return available_models
    
    def get_model_path(self, model_id: str) -> Optional[Path]:
        """Get local path for a model if it exists"""
        if model_id not in self.model_registry:
            return None
        
        model_info = self.model_registry[model_id]
        model_path = self._get_model_path(model_id, model_info)
        
        return model_path if model_path.exists() else None
    
    def cleanup_models(self, keep_models: List[str] = None) -> int:
        """
        Clean up unused models
        
        Args:
            keep_models: List of model IDs to keep
            
        Returns:
            Number of models removed
        """
        try:
            keep_models = keep_models or []
            removed_count = 0
            
            for model_id, model_info in self.model_registry.items():
                if model_id not in keep_models:
                    model_path = self._get_model_path(model_id, model_info)
                    
                    if model_path.exists():
                        model_path.unlink()
                        removed_count += 1
                        logger.info(f"Removed model: {model_id}")
                        
                        # Also remove config file if exists
                        config_path = model_path.parent / f"{model_path.stem}_config.json"
                        if config_path.exists():
                            config_path.unlink()
            
            logger.info(f"Cleaned up {removed_count} models")
            return removed_count
            
        except Exception as e:
            logger.error(f"Model cleanup failed: {e}")
            return 0
    
    def get_download_stats(self) -> Dict[str, Any]:
        """Get download statistics"""
        stats = self.download_stats.copy()
        
        # Calculate success rate
        if stats["total_downloads"] > 0:
            stats["success_rate"] = stats["successful_downloads"] / stats["total_downloads"]
        else:
            stats["success_rate"] = 0.0
        
        # Calculate average download time
        if stats["download_times"]:
            stats["average_download_time"] = sum(stats["download_times"].values()) / len(stats["download_times"])
        else:
            stats["average_download_time"] = 0.0
        
        # Convert bytes to MB
        stats["total_mb_downloaded"] = stats["total_bytes_downloaded"] / (1024 * 1024)
        
        return stats
    
    async def update_model_registry(self, registry_url: str = None) -> bool:
        """Update model registry from remote source"""
        try:
            if not registry_url:
                # Default registry URL (would be hosted somewhere)
                registry_url = "https://raw.githubusercontent.com/steve-voice-assistant/models/main/registry.json"
            
            response = requests.get(registry_url, timeout=10)
            response.raise_for_status()
            
            new_registry = response.json()
            
            # Validate registry format
            if not isinstance(new_registry, dict):
                logger.error("Invalid registry format")
                return False
            
            # Update registry
            self.model_registry.update(new_registry)
            
            # Save updated registry locally
            registry_file = self.models_dir / "registry.json"
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.model_registry, f, indent=2, ensure_ascii=False)
            
            logger.info("Model registry updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Model registry update failed: {e}")
            return False