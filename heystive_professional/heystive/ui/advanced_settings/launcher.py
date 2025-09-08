"""
Heystive Advanced Settings Launcher
REAL IMPLEMENTATION - Production Ready
Unified launcher for both desktop and web settings interfaces
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def launch_desktop_settings():
    """Launch desktop settings interface"""
    try:
        print("🖥️ Launching Desktop Settings Interface...")
        
        # Import and run desktop settings
        from heystive.ui.advanced_settings.desktop.settings_window import AdvancedSettingsWindow
        
        app = AdvancedSettingsWindow()
        app.run()
        
    except ImportError as e:
        print(f"❌ Failed to import desktop settings: {e}")
        print("💡 Make sure tkinter is available on your system")
        return False
    except Exception as e:
        print(f"❌ Failed to launch desktop settings: {e}")
        return False
        
    return True

def launch_web_settings(host: str = "localhost", port: int = 5001, debug: bool = False):
    """Launch web settings interface"""
    try:
        print("🌐 Launching Web Settings Interface...")
        print(f"   URL: http://{host}:{port}")
        
        # Import and run web settings
        from heystive.ui.advanced_settings.web.settings_web_app import HeystiveWebSettingsApp
        
        app = HeystiveWebSettingsApp(host=host, port=port)
        app.run(debug=debug)
        
    except ImportError as e:
        print(f"❌ Failed to import web settings: {e}")
        print("💡 Make sure Flask is available: pip install flask")
        return False
    except Exception as e:
        print(f"❌ Failed to launch web settings: {e}")
        return False
        
    return True

def launch_service_manager():
    """Launch service management interface"""
    try:
        print("⚙️ Launching Service Manager...")
        
        from heystive.services.windows_service.service_manager import HeystiveServiceManager
        
        manager = HeystiveServiceManager()
        status = manager.get_service_status()
        
        print("\n" + "="*50)
        print("HEYSTIVE SERVICE MANAGER")
        print("="*50)
        print(f"Service Status:")
        print(f"  Installed: {status['installed']}")
        print(f"  Running: {status['running']}")
        print(f"  Platform: {status['platform']}")
        if 'detailed_status' in status:
            print(f"  Detailed Status: {status['detailed_status']}")
        print(f"  Last Check: {status['timestamp']}")
        
        print("\nAvailable Commands:")
        print("  1. Install Service")
        print("  2. Start Service")
        print("  3. Stop Service")
        print("  4. Uninstall Service")
        print("  5. Create Startup Shortcut")
        print("  6. Refresh Status")
        print("  0. Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (0-6): ").strip()
                
                if choice == '0':
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    print("Installing service...")
                    if manager.install_service():
                        print("✅ Service installed successfully")
                    else:
                        print("❌ Service installation failed")
                elif choice == '2':
                    print("Starting service...")
                    if manager.start_service():
                        print("✅ Service started successfully")
                    else:
                        print("❌ Service start failed")
                elif choice == '3':
                    print("Stopping service...")
                    if manager.stop_service():
                        print("✅ Service stopped successfully")
                    else:
                        print("❌ Service stop failed")
                elif choice == '4':
                    confirm = input("Are you sure you want to uninstall the service? (y/N): ")
                    if confirm.lower() in ['y', 'yes']:
                        print("Uninstalling service...")
                        if manager.uninstall_service():
                            print("✅ Service uninstalled successfully")
                        else:
                            print("❌ Service uninstall failed")
                elif choice == '5':
                    print("Creating startup shortcut...")
                    if manager.create_startup_shortcut():
                        print("✅ Startup shortcut created successfully")
                    else:
                        print("❌ Startup shortcut creation failed")
                elif choice == '6':
                    status = manager.get_service_status()
                    print(f"\nUpdated Status:")
                    print(f"  Installed: {status['installed']}")
                    print(f"  Running: {status['running']}")
                    if 'detailed_status' in status:
                        print(f"  Detailed Status: {status['detailed_status']}")
                else:
                    print("❌ Invalid choice. Please enter a number between 0-6.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
    except ImportError as e:
        print(f"❌ Failed to import service manager: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to launch service manager: {e}")
        return False
        
    return True

def test_settings_system():
    """Test the settings system"""
    try:
        print("🧪 Testing Settings System...")
        
        from heystive.config.ui_settings.settings_manager import get_settings_manager
        
        manager = get_settings_manager()
        
        # Test basic operations
        print("📋 Running settings tests...")
        
        # Test getting settings
        theme = manager.get_setting('ui.theme', 'dark')
        print(f"✅ Current theme: {theme}")
        
        # Test setting a value
        manager.set_setting('ui.test_setting', 'test_value')
        test_value = manager.get_setting('ui.test_setting')
        print(f"✅ Test setting: {test_value}")
        
        # Test validation
        issues = manager.validate_settings()
        if issues:
            print("⚠️ Validation issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Settings validation passed")
        
        # Test getting all settings
        all_settings = manager.get_all_settings()
        print(f"✅ Total settings sections: {len(all_settings)}")
        
        print("✅ Settings system test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Failed to import settings manager: {e}")
        return False
    except Exception as e:
        print(f"❌ Settings system test failed: {e}")
        return False
        
    return True

def show_help():
    """Show help information"""
    help_text = """
🎤 HEYSTIVE ADVANCED SETTINGS LAUNCHER

This launcher provides access to Heystive's advanced settings and service management.

AVAILABLE INTERFACES:
  desktop    - Launch desktop settings interface (GUI)
  web        - Launch web settings interface (Browser-based)
  service    - Launch service management interface (CLI)
  test       - Test the settings system

EXAMPLES:
  python launcher.py desktop                    # Launch desktop GUI
  python launcher.py web                        # Launch web interface on default port
  python launcher.py web --port 8080            # Launch web interface on custom port
  python launcher.py web --host 0.0.0.0        # Launch web interface for remote access
  python launcher.py service                    # Launch service manager
  python launcher.py test                       # Test settings system

OPTIONS:
  --host HOST     Web interface host (default: localhost)
  --port PORT     Web interface port (default: 5001)
  --debug         Enable debug mode for web interface
  --help          Show this help message

FEATURES:
  ✅ Advanced settings management for both web and desktop
  ✅ Windows service for always-running wake word detection
  ✅ Persian RTL interface support
  ✅ Cross-platform compatibility
  ✅ Real-time service status monitoring
  ✅ Settings import/export functionality
  ✅ Comprehensive validation system
"""
    print(help_text)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Heystive Advanced Settings Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'interface',
        nargs='?',
        choices=['desktop', 'web', 'service', 'test'],
        default='desktop',
        help='Interface to launch (default: desktop)'
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='Web interface host (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Web interface port (default: 5001)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode for web interface'
    )
    
    args = parser.parse_args()
    
    # Show banner
    print("🎤 HEYSTIVE ADVANCED SETTINGS LAUNCHER")
    print("=" * 50)
    
    success = False
    
    try:
        if args.interface == 'desktop':
            success = launch_desktop_settings()
        elif args.interface == 'web':
            success = launch_web_settings(args.host, args.port, args.debug)
        elif args.interface == 'service':
            success = launch_service_manager()
        elif args.interface == 'test':
            success = test_settings_system()
        else:
            show_help()
            return
            
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        success = False
    
    if success:
        print("✅ Operation completed successfully")
    else:
        print("❌ Operation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()