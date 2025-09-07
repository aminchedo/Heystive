#!/usr/bin/env python3
"""
Standalone Model Download Script
Downloads Persian language models for Steve Voice Assistant
Usage: python scripts/download_models.py [--tier high|medium|low] [--models model1,model2]
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from steve.utils.model_downloader import ModelDownloader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print script banner"""
    print("=" * 60)
    print("🎯 Steve Voice Assistant - Model Downloader")
    print("📥 Persian Language Model Download Utility")
    print("=" * 60)

async def download_by_tier(tier: str, models_dir: str) -> bool:
    """Download models by hardware tier"""
    try:
        print(f"\n🔍 Downloading models for hardware tier: {tier}")
        print("-" * 40)
        
        downloader = ModelDownloader(models_dir)
        
        if tier == "auto":
            print("🤖 Auto-detecting system capabilities...")
            success = await downloader.auto_download_for_system()
        else:
            successful_downloads = await downloader.download_missing_models(tier)
            success = len(successful_downloads) > 0
            
        if success:
            print("✅ Model download completed successfully!")
        else:
            print("❌ Model download failed or no models were needed")
            
        return success
        
    except Exception as e:
        logger.error(f"Tier download failed: {e}")
        return False

async def download_specific_models(model_ids: List[str], models_dir: str, force: bool = False) -> bool:
    """Download specific models by ID"""
    try:
        print(f"\n🎯 Downloading specific models: {', '.join(model_ids)}")
        print("-" * 40)
        
        downloader = ModelDownloader(models_dir)
        successful_downloads = 0
        
        for model_id in model_ids:
            print(f"📥 Downloading {model_id}...")
            success = await downloader.download_specific_model(model_id, force)
            if success:
                print(f"✅ {model_id} downloaded successfully")
                successful_downloads += 1
            else:
                print(f"❌ {model_id} download failed")
        
        print(f"\n📊 Download Summary: {successful_downloads}/{len(model_ids)} models downloaded")
        return successful_downloads > 0
        
    except Exception as e:
        logger.error(f"Specific model download failed: {e}")
        return False

def show_model_status(models_dir: str):
    """Show current model status"""
    try:
        print("\n📊 Current Model Status")
        print("-" * 40)
        
        downloader = ModelDownloader(models_dir)
        status = downloader.get_model_status()
        
        if "error" in status:
            print(f"❌ Error getting model status: {status['error']}")
            return
        
        print(f"📦 Total Models: {status['total_models']}")
        print(f"✅ Downloaded: {status['downloaded_models']}")
        print(f"❌ Missing: {status['missing_models']}")
        print(f"📈 Completion: {status['download_completion']:.1%}")
        
        print("\n📋 Model Details:")
        for model_id, info in status["models"].items():
            status_icon = "✅" if info["downloaded"] else "❌"
            size_info = f"({info['size_mb']}MB)" if info['size_mb'] else ""
            print(f"  {status_icon} {model_id}: {info['name']} {size_info}")
            print(f"     {info['description']}")
            print(f"     Type: {info['type']}, Quality: {info['quality']}, HW: {info['hardware_requirements']}")
            print()
        
        # Show download statistics
        stats = status["download_stats"]
        if stats["total_downloads"] > 0:
            print("📈 Download Statistics:")
            print(f"  Total Downloads: {stats['total_downloads']}")
            print(f"  Successful: {stats['successful_downloads']}")
            print(f"  Success Rate: {stats.get('success_rate', 0):.1%}")
            print(f"  Total Downloaded: {stats.get('total_mb_downloaded', 0):.1f}MB")
            print(f"  Average Time: {stats.get('average_download_time', 0):.1f}s")
        
    except Exception as e:
        logger.error(f"Error showing model status: {e}")

def validate_models(models_dir: str):
    """Validate downloaded models"""
    try:
        print("\n🔍 Validating Downloaded Models")
        print("-" * 40)
        
        downloader = ModelDownloader(models_dir)
        validation_results = downloader.validate_models()
        
        valid_count = sum(1 for valid in validation_results.values() if valid)
        total_count = len(validation_results)
        
        print(f"✅ Valid Models: {valid_count}/{total_count}")
        
        for model_id, is_valid in validation_results.items():
            status_icon = "✅" if is_valid else "❌"
            print(f"  {status_icon} {model_id}")
        
    except Exception as e:
        logger.error(f"Model validation failed: {e}")

def cleanup_models(models_dir: str, keep_models: List[str] = None):
    """Clean up unused models"""
    try:
        print("\n🧹 Cleaning Up Unused Models")
        print("-" * 40)
        
        if keep_models:
            print(f"Keeping models: {', '.join(keep_models)}")
        else:
            print("Removing all models (use --keep to preserve specific models)")
        
        downloader = ModelDownloader(models_dir)
        removed_count = downloader.cleanup_unused_models(keep_models)
        
        print(f"🗑️  Removed {removed_count} models")
        
    except Exception as e:
        logger.error(f"Model cleanup failed: {e}")

async def main():
    """Main script function"""
    parser = argparse.ArgumentParser(
        description="Download Persian language models for Steve Voice Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/download_models.py --tier auto          # Auto-detect and download
  python scripts/download_models.py --tier medium       # Download medium-tier models
  python scripts/download_models.py --models whisper_small,kamtera_female_vits
  python scripts/download_models.py --status            # Show current status
  python scripts/download_models.py --validate          # Validate models
  python scripts/download_models.py --cleanup           # Remove all models
        """
    )
    
    parser.add_argument("--tier", choices=["auto", "high", "medium", "low"],
                       help="Hardware tier for model selection")
    parser.add_argument("--models", type=str,
                       help="Comma-separated list of specific models to download")
    parser.add_argument("--models-dir", default="./models",
                       help="Directory to store models (default: ./models)")
    parser.add_argument("--force", action="store_true",
                       help="Force re-download existing models")
    parser.add_argument("--status", action="store_true",
                       help="Show current model status")
    parser.add_argument("--validate", action="store_true",
                       help="Validate downloaded models")
    parser.add_argument("--cleanup", action="store_true",
                       help="Clean up unused models")
    parser.add_argument("--keep", type=str,
                       help="Comma-separated list of models to keep during cleanup")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print_banner()
    
    # Handle status display
    if args.status:
        show_model_status(args.models_dir)
        return 0
    
    # Handle model validation
    if args.validate:
        validate_models(args.models_dir)
        return 0
    
    # Handle model cleanup
    if args.cleanup:
        keep_models = args.keep.split(",") if args.keep else None
        cleanup_models(args.models_dir, keep_models)
        return 0
    
    # Handle model downloads
    success = False
    
    if args.tier:
        success = await download_by_tier(args.tier, args.models_dir)
    elif args.models:
        model_list = [model.strip() for model in args.models.split(",")]
        success = await download_specific_models(model_list, args.models_dir, args.force)
    else:
        # Default: auto-detect and download
        print("🤖 No specific options provided, auto-detecting system...")
        success = await download_by_tier("auto", args.models_dir)
    
    # Show final status
    print("\n" + "=" * 60)
    if success:
        print("🎉 Model download completed successfully!")
        show_model_status(args.models_dir)
        return 0
    else:
        print("❌ Model download failed or no action taken")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Download cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)