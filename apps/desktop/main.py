import os, sys, requests, logging
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from apps.desktop.hotkeys import GlobalHotkeys
from apps.desktop.components.main_window import ModernMainWindow

logging.basicConfig(filename="heystive_desktop.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8765")

class HeystiveDesktopApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Heystive Desktop")
        self.app.setApplicationVersion("1.0.0")
        
        # Create main window
        self.main_window = ModernMainWindow()
        
        # Setup global hotkeys
        self.hotkeys = GlobalHotkeys(
            on_toggle_listen=self.toggle_listen, 
            on_focus=self.focus_window
        )
        self.hotkeys.start()
        
        # Setup system tray
        self.setup_system_tray()
        
    def setup_system_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self.app)
            self.tray_icon.setIcon(QIcon("🎤"))  # Simple emoji icon
            
            # Create tray menu
            tray_menu = QMenu()
            
            show_action = tray_menu.addAction("نمایش پنجره")
            show_action.triggered.connect(self.main_window.show)
            
            hide_action = tray_menu.addAction("مخفی کردن")
            hide_action.triggered.connect(self.main_window.hide)
            
            tray_menu.addSeparator()
            
            quit_action = tray_menu.addAction("خروج")
            quit_action.triggered.connect(self.app.quit)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_icon_activated)
            self.tray_icon.show()
            
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
                
    def toggle_listen(self):
        """Toggle listening state via hotkey"""
        logging.info("Global hotkey triggered: toggle listen")
        if hasattr(self.main_window, 'listen_action'):
            self.main_window.listen_action.trigger()
        else:
            # Fallback if main window not ready
            self.main_window.show_notification("کلید میانبر: تغییر حالت گوش دادن", "info")
    
    def focus_window(self):
        """Focus main window via hotkey"""
        logging.info("Global hotkey triggered: focus window")
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        
    def run(self):
        """Run the application"""
        # Show main window
        self.main_window.show()
        
        # Start application
        return self.app.exec()

if __name__ == "__main__":
    app = HeystiveDesktopApp()
    sys.exit(app.run())