#!/usr/bin/env python3
"""
Heystive Persian Voice Assistant - Professional Entry Point
Unified, production-ready Persian voice assistant system
"""

import sys
import argparse
import logging
from pathlib import Path

# Add heystive package to path
sys.path.insert(0, str(Path(__file__).parent / "heystive"))

def main():
    """Main entry point for Heystive Persian Voice Assistant"""
    parser = argparse.ArgumentParser(
        description="Heystive Persian Voice Assistant - Professional System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎤 Heystive Persian Voice Assistant
Professional reorganization combining best features from Steve and Heystive

Examples:
  python main.py --mode desktop              # Launch desktop app
  python main.py --mode web --port 8080      # Launch web interface  
  python main.py --mode cli                  # Launch CLI interface

Features:
  • Advanced Persian TTS with multiple engines
  • Professional web interface with real-time features
  • Desktop application with system integration
  • Comprehensive voice processing pipeline
  • Smart home integration capabilities
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["desktop", "web", "cli"], 
        default="desktop",
        help="Interface mode (default: desktop)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=5000,
        help="Port for web interface (default: 5000)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--config", 
        help="Configuration file path"
    )
    
    args = parser.parse_args()
    
    print("🎤 Heystive Persian Voice Assistant")
    print("=" * 50)
    print(f"Mode: {args.mode}")
    
    try:
        # Import and run the unified main system
        from main import HeystiveUnifiedLauncher
        
        launcher = HeystiveUnifiedLauncher()
        launcher.launch(args.mode, args)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting Heystive: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()