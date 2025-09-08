#!/usr/bin/env python3
"""
Heystive Persian Voice Assistant - Unified Main Entry Point
Professional reorganization combining the best of Steve and Heystive implementations
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('heystive.log')
    ]
)

logger = logging.getLogger(__name__)

class HeystiveUnifiedLauncher:
    """
    Unified launcher for Heystive Persian Voice Assistant
    Supports desktop, web, and CLI modes
    """
    
    def __init__(self):
        self.modes = {
            'desktop': self._launch_desktop,
            'web': self._launch_web,
            'cli': self._launch_cli
        }
        
        logger.info("🎤 Heystive Persian Voice Assistant - Unified System")
        logger.info("=" * 60)
        
    def _launch_desktop(self, args):
        """Launch desktop application (Heystive implementation)"""
        try:
            logger.info("🖥️ Starting Desktop Application...")
            
            # Import desktop app
            sys.path.insert(0, str(Path(__file__).parent / "ui" / "desktop"))
            from heystive_main_app import HeyStiveApp
            
            # Launch desktop app
            app = HeyStiveApp()
            app.run()
            
        except Exception as e:
            logger.error(f"❌ Desktop app failed to start: {e}")
            sys.exit(1)
    
    def _launch_web(self, args):
        """Launch web interface (Steve implementation)"""
        try:
            logger.info("🌐 Starting Web Interface...")
            
            # Import web interface
            sys.path.insert(0, str(Path(__file__).parent / "ui" / "web"))
            from professional_web_interface import SteveProfessionalWebInterface
            
            # Launch web interface
            web_app = SteveProfessionalWebInterface()
            web_app.run(host='0.0.0.0', port=args.port, debug=args.debug)
            
        except Exception as e:
            logger.error(f"❌ Web interface failed to start: {e}")
            sys.exit(1)
    
    def _launch_cli(self, args):
        """Launch CLI interface"""
        try:
            logger.info("💻 Starting CLI Interface...")
            
            # Import voice pipeline
            from core.voice_pipeline import SteveVoiceAssistant
            
            # Launch CLI mode
            assistant = SteveVoiceAssistant({})
            assistant.start_cli_mode()
            
        except Exception as e:
            logger.error(f"❌ CLI interface failed to start: {e}")
            sys.exit(1)
    
    def launch(self, mode: str, args):
        """Launch the specified mode"""
        if mode not in self.modes:
            logger.error(f"❌ Unknown mode: {mode}")
            logger.info(f"Available modes: {', '.join(self.modes.keys())}")
            sys.exit(1)
        
        logger.info(f"🚀 Launching Heystive in {mode} mode...")
        self.modes[mode](args)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Heystive Persian Voice Assistant - Unified System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode desktop              # Launch desktop app
  python main.py --mode web --port 8080      # Launch web interface
  python main.py --mode cli                  # Launch CLI interface
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
    
    # Initialize launcher
    launcher = HeystiveUnifiedLauncher()
    
    # Launch specified mode
    launcher.launch(args.mode, args)

if __name__ == "__main__":
    main()