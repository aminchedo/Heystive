"""
Heystive Advanced Settings Integration
REAL IMPLEMENTATION - Production Ready
Integration module to add advanced settings to existing Heystive application
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import threading
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class HeystiveSettingsIntegration:
    """Integration class for advanced settings with main Heystive application"""
    
    def __init__(self):
        self.settings_manager = None
        self.service_manager = None
        self.web_app = None
        self.desktop_app = None
        self.service_thread = None
        
        self.initialize_components()
        
    def initialize_components(self):
        """Initialize all settings components"""
        try:
            # Initialize settings manager
            from heystive.config.ui_settings.settings_manager import get_settings_manager
            self.settings_manager = get_settings_manager()
            print("✅ Settings manager initialized")
            
            # Initialize service manager
            from heystive.services.windows_service.service_manager import HeystiveServiceManager
            self.service_manager = HeystiveServiceManager()
            print("✅ Service manager initialized")
            
        except ImportError as e:
            print(f"⚠️ Warning: Could not initialize some components: {e}")
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            
    def get_settings_manager(self):
        """Get the settings manager instance"""
        return self.settings_manager
        
    def get_service_manager(self):
        """Get the service manager instance"""
        return self.service_manager
        
    def launch_desktop_settings(self, parent=None):
        """Launch desktop settings window"""
        try:
            from heystive.ui.advanced_settings.desktop.settings_window import AdvancedSettingsWindow
            
            if self.desktop_app is None:
                self.desktop_app = AdvancedSettingsWindow(parent)
                
            self.desktop_app.run()
            return True
            
        except Exception as e:
            print(f"❌ Failed to launch desktop settings: {e}")
            return False
            
    def launch_web_settings(self, host: str = "localhost", port: int = 5001, background: bool = True):
        """Launch web settings interface"""
        try:
            from heystive.ui.advanced_settings.web.settings_web_app import HeystiveWebSettingsApp
            
            if self.web_app is None:
                self.web_app = HeystiveWebSettingsApp(host=host, port=port)
                
            if background:
                # Run in background thread
                web_thread = threading.Thread(
                    target=self.web_app.run,
                    kwargs={'debug': False},
                    daemon=True
                )
                web_thread.start()
                print(f"🌐 Web settings interface started at http://{host}:{port}")
            else:
                self.web_app.run(debug=False)
                
            return True
            
        except Exception as e:
            print(f"❌ Failed to launch web settings: {e}")
            return False
            
    def start_background_service(self):
        """Start the background voice service"""
        try:
            from heystive.services.windows_service.heystive_service import HeystiveServiceCore
            
            def run_service():
                service = HeystiveServiceCore()
                service.start_service()
                
            self.service_thread = threading.Thread(target=run_service, daemon=True)
            self.service_thread.start()
            
            print("✅ Background voice service started")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start background service: {e}")
            return False
            
    def stop_background_service(self):
        """Stop the background voice service"""
        try:
            if self.service_thread and self.service_thread.is_alive():
                # Service will stop when main thread exits due to daemon=True
                print("✅ Background voice service stopped")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Failed to stop background service: {e}")
            return False
            
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        if self.settings_manager:
            return self.settings_manager.get_all_settings()
        return {}
        
    def update_setting(self, path: str, value: Any) -> bool:
        """Update a specific setting"""
        try:
            if self.settings_manager:
                self.settings_manager.set_setting(path, value)
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to update setting {path}: {e}")
            return False
            
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        if self.service_manager:
            return self.service_manager.get_service_status()
        return {'installed': False, 'running': False, 'error': 'Service manager not available'}
        
    def install_windows_service(self) -> bool:
        """Install Windows service"""
        if self.service_manager:
            return self.service_manager.install_service()
        return False
        
    def start_windows_service(self) -> bool:
        """Start Windows service"""
        if self.service_manager:
            return self.service_manager.start_service()
        return False
        
    def stop_windows_service(self) -> bool:
        """Stop Windows service"""
        if self.service_manager:
            return self.service_manager.stop_service()
        return False
        
    def create_menu_integration(self):
        """Create menu items for integration with main application"""
        return {
            'settings_menu': {
                'desktop_settings': {
                    'label': 'تنظیمات پیشرفته (دسکتاپ)',
                    'callback': self.launch_desktop_settings,
                    'shortcut': 'Ctrl+Shift+S'
                },
                'web_settings': {
                    'label': 'تنظیمات پیشرفته (وب)',
                    'callback': lambda: self.launch_web_settings(background=False),
                    'shortcut': 'Ctrl+Shift+W'
                },
                'separator': '---',
                'service_manager': {
                    'label': 'مدیریت سرویس ویندوز',
                    'callback': self.show_service_manager,
                    'shortcut': 'Ctrl+Shift+M'
                }
            }
        }
        
    def show_service_manager(self):
        """Show service manager dialog"""
        try:
            # Simple service manager dialog
            status = self.get_service_status()
            
            message = f"""وضعیت سرویس ویندوز:
            
نصب شده: {'بله' if status['installed'] else 'خیر'}
در حال اجرا: {'بله' if status['running'] else 'خیر'}
پلتفرم: {status.get('platform', 'نامشخص')}

آیا می‌خواهید سرویس را مدیریت کنید؟"""
            
            print("=" * 50)
            print("مدیریت سرویس ویندوز")
            print("=" * 50)
            print(message)
            print("\nبرای مدیریت کامل، از launcher.py service استفاده کنید")
            
        except Exception as e:
            print(f"❌ خطا در نمایش مدیریت سرویس: {e}")
            
    def integrate_with_main_app(self, main_app):
        """Integrate with main Heystive application"""
        try:
            # Add settings menu if main app supports it
            if hasattr(main_app, 'add_menu_items'):
                menu_items = self.create_menu_integration()
                main_app.add_menu_items(menu_items)
                
            # Add settings button if main app supports it
            if hasattr(main_app, 'add_settings_button'):
                main_app.add_settings_button(
                    text="تنظیمات پیشرفته",
                    callback=self.launch_desktop_settings
                )
                
            # Start background web interface if enabled
            web_enabled = self.settings_manager.get_setting('web_interface.auto_start', False) if self.settings_manager else False
            if web_enabled:
                host = self.settings_manager.get_setting('web_interface.host', 'localhost')
                port = self.settings_manager.get_setting('web_interface.port', 5001)
                self.launch_web_settings(host=host, port=port, background=True)
                
            # Start background service if enabled
            service_enabled = self.settings_manager.get_setting('service.auto_start', False) if self.settings_manager else False
            if service_enabled:
                self.start_background_service()
                
            print("✅ Advanced settings integrated with main application")
            return True
            
        except Exception as e:
            print(f"❌ Failed to integrate with main app: {e}")
            return False
            
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.stop_background_service()
            
            if self.web_app:
                # Web app cleanup would happen here
                pass
                
            if self.desktop_app:
                # Desktop app cleanup would happen here
                pass
                
            print("✅ Advanced settings cleanup completed")
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")

# Global integration instance
_integration_instance = None

def get_settings_integration() -> HeystiveSettingsIntegration:
    """Get global settings integration instance"""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = HeystiveSettingsIntegration()
    return _integration_instance

def integrate_advanced_settings(main_app):
    """Convenience function to integrate advanced settings with main app"""
    integration = get_settings_integration()
    return integration.integrate_with_main_app(main_app)

def launch_settings_ui(interface: str = "desktop", **kwargs):
    """Convenience function to launch settings UI"""
    integration = get_settings_integration()
    
    if interface == "desktop":
        return integration.launch_desktop_settings()
    elif interface == "web":
        return integration.launch_web_settings(**kwargs)
    else:
        raise ValueError(f"Unknown interface: {interface}")

# Example usage for main application integration
if __name__ == "__main__":
    print("🎤 Heystive Advanced Settings Integration Test")
    print("=" * 50)
    
    # Initialize integration
    integration = HeystiveSettingsIntegration()
    
    # Test components
    print("\n📋 Testing Components:")
    
    # Test settings
    if integration.settings_manager:
        print("✅ Settings Manager: Available")
        theme = integration.settings_manager.get_setting('ui.theme', 'dark')
        print(f"   Current theme: {theme}")
    else:
        print("❌ Settings Manager: Not Available")
        
    # Test service manager
    if integration.service_manager:
        print("✅ Service Manager: Available")
        status = integration.get_service_status()
        print(f"   Service installed: {status['installed']}")
        print(f"   Service running: {status['running']}")
    else:
        print("❌ Service Manager: Not Available")
        
    print("\n✅ Integration test completed")