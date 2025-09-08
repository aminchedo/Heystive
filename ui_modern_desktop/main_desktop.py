#!/usr/bin/env python3
"""
Heystive Modern Desktop Application - PySide6 Implementation
Modern Material Design interface for Persian Voice Assistant
"""

import sys
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "heystive_professional" / "heystive"))

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
        QLabel, QPushButton, QTextEdit, QSlider, QComboBox, QProgressBar,
        QSystemTrayIcon, QMenu, QMessageBox, QSplashScreen, QFrame,
        QScrollArea, QTabWidget, QGroupBox, QCheckBox, QSpinBox
    )
    from PySide6.QtCore import (
        Qt, QTimer, QThread, Signal, QPropertyAnimation, QEasingCurve,
        QSettings, QSize, QPoint, QRect, QUrl, QRunnable, QThreadPool
    )
    from PySide6.QtGui import (
        QFont, QIcon, QPixmap, QPainter, QColor, QPalette, QAction,
        QFontDatabase, QLinearGradient, QBrush, QCursor
    )
    from PySide6.QtMultimedia import QAudioInput, QMediaDevices
except ImportError as e:
    print(f"❌ PySide6 not installed: {e}")
    print("Install with: pip install PySide6")
    sys.exit(1)

# Import modern components
from components.modern_main_window import ModernMainWindow
from components.voice_control_widget import VoiceControlWidget
from components.persian_text_widget import PersianTextWidget
from components.system_tray_icon import SystemTrayIcon
from components.notification_manager import NotificationManager
from components.settings_dialog import SettingsDialog
from components.voice_visualizer import VoiceVisualizer

# Import utilities
from utils.api_client import HeystiveAPIClient
from utils.hotkey_manager import HotkeyManager
from utils.desktop_integration import DesktopIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('heystive_desktop.log')
    ]
)

logger = logging.getLogger(__name__)

class HeystiveModernDesktop(QMainWindow):
    """
    Modern Desktop Application for Heystive Persian Voice Assistant
    Features Material Design UI with Persian RTL support
    """
    
    # Signals
    voice_processed = Signal(dict)
    system_status_updated = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        # Application state
        self.is_initialized = False
        self.is_voice_active = False
        self.current_theme = 'dark'
        
        # Core components
        self.api_client = None
        self.main_widget = None
        self.voice_widget = None
        self.system_tray = None
        self.notification_manager = None
        self.hotkey_manager = None
        self.desktop_integration = None
        
        # Settings
        self.settings = QSettings('Heystive', 'ModernDesktop')
        
        # Timers
        self.status_timer = QTimer()
        self.animation_timer = QTimer()
        
        # Initialize application
        self.init_application()
    
    def init_application(self):
        """Initialize the complete application"""
        try:
            logger.info("🚀 Initializing Heystive Modern Desktop Application...")
            
            # Setup window properties
            self.setup_window()
            
            # Load Persian fonts
            self.load_persian_fonts()
            
            # Apply theme
            self.apply_theme()
            
            # Initialize API client
            self.init_api_client()
            
            # Create UI components
            self.create_ui()
            
            # Setup system integration
            self.setup_system_integration()
            
            # Connect signals
            self.connect_signals()
            
            # Load settings
            self.load_settings()
            
            # Start background tasks
            self.start_background_tasks()
            
            # Show welcome message
            self.show_welcome()
            
            self.is_initialized = True
            logger.info("✅ Heystive Modern Desktop initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize application: {e}")
            self.show_error_message(f"خطا در راه‌اندازی برنامه: {str(e)}")
            sys.exit(1)
    
    def setup_window(self):
        """Setup main window properties"""
        # Window title and icon
        self.setWindowTitle("Heystive - استیو دستیار صوتی")
        self.setWindowIcon(QIcon(str(Path(__file__).parent / "resources" / "icons" / "heystive.png")))
        
        # Window size and position
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Center window on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # Window flags for modern appearance
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        
        # Enable right-to-left layout for Persian
        self.setLayoutDirection(Qt.RightToLeft)
        
        logger.info("🪟 Window setup complete")
    
    def load_persian_fonts(self):
        """Load Persian fonts for UI"""
        try:
            fonts_dir = Path(__file__).parent / "resources" / "fonts"
            
            # Load Vazir font family
            vazir_fonts = [
                "Vazir-Regular.ttf",
                "Vazir-Bold.ttf",
                "Vazir-Light.ttf",
                "Vazir-Medium.ttf"
            ]
            
            for font_file in vazir_fonts:
                font_path = fonts_dir / font_file
                if font_path.exists():
                    font_id = QFontDatabase.addApplicationFont(str(font_path))
                    if font_id != -1:
                        font_families = QFontDatabase.applicationFontFamilies(font_id)
                        logger.info(f"📝 Loaded font: {font_families}")
            
            # Set default application font
            default_font = QFont("Vazir", 10)
            QApplication.setFont(default_font)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load Persian fonts: {e}")
    
    def apply_theme(self):
        """Apply Material Design theme"""
        try:
            # Load theme stylesheet
            theme_file = Path(__file__).parent / "styles" / f"material_{self.current_theme}.qss"
            
            if theme_file.exists():
                with open(theme_file, 'r', encoding='utf-8') as f:
                    stylesheet = f.read()
                self.setStyleSheet(stylesheet)
            else:
                # Fallback to built-in theme
                self.apply_builtin_theme()
            
            logger.info(f"🎨 Applied {self.current_theme} theme")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to apply theme: {e}")
            self.apply_builtin_theme()
    
    def apply_builtin_theme(self):
        """Apply built-in dark theme"""
        palette = QPalette()
        
        # Dark theme colors
        palette.setColor(QPalette.Window, QColor(33, 37, 43))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(42, 46, 54))
        palette.setColor(QPalette.AlternateBase, QColor(66, 73, 85))
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 59, 69))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        self.setPalette(palette)
    
    def init_api_client(self):
        """Initialize API client for backend communication"""
        try:
            backend_url = self.settings.value('backend_url', 'http://localhost:8000')
            self.api_client = HeystiveAPIClient(backend_url)
            
            logger.info(f"🔗 API client initialized: {backend_url}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize API client: {e}")
            self.api_client = None
    
    def create_ui(self):
        """Create the main user interface"""
        try:
            # Create main widget
            self.main_widget = ModernMainWindow(self)
            self.setCentralWidget(self.main_widget)
            
            # Get references to key components
            self.voice_widget = self.main_widget.voice_widget
            
            logger.info("🖥️ UI components created")
            
        except Exception as e:
            logger.error(f"❌ Failed to create UI: {e}")
            raise
    
    def setup_system_integration(self):
        """Setup system integration features"""
        try:
            # System tray icon
            if QSystemTrayIcon.isSystemTrayAvailable():
                self.system_tray = SystemTrayIcon(self)
                self.system_tray.show()
            
            # Notification manager
            self.notification_manager = NotificationManager(self)
            
            # Hotkey manager
            self.hotkey_manager = HotkeyManager(self)
            self.hotkey_manager.register_hotkey('Ctrl+Alt+V', self.toggle_voice_recording)
            self.hotkey_manager.register_hotkey('Ctrl+Alt+H', self.show_hide_window)
            
            # Desktop integration
            self.desktop_integration = DesktopIntegration(self)
            
            logger.info("🔧 System integration setup complete")
            
        except Exception as e:
            logger.warning(f"⚠️ System integration setup failed: {e}")
    
    def connect_signals(self):
        """Connect all signal-slot connections"""
        try:
            # Voice widget signals
            if self.voice_widget:
                self.voice_widget.voice_recorded.connect(self.process_voice_data)
                self.voice_widget.recording_started.connect(self.on_recording_started)
                self.voice_widget.recording_stopped.connect(self.on_recording_stopped)
                self.voice_widget.error_occurred.connect(self.handle_voice_error)
            
            # System tray signals
            if self.system_tray:
                self.system_tray.activated.connect(self.on_tray_activated)
                self.system_tray.message_clicked.connect(self.show_main_window)
            
            # Timer signals
            self.status_timer.timeout.connect(self.update_system_status)
            
            # Application signals
            self.voice_processed.connect(self.on_voice_processed)
            self.system_status_updated.connect(self.on_system_status_updated)
            self.error_occurred.connect(self.handle_error)
            
            logger.info("🔗 Signal connections established")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect signals: {e}")
    
    def load_settings(self):
        """Load application settings"""
        try:
            # Window geometry
            geometry = self.settings.value('window_geometry')
            if geometry:
                self.restoreGeometry(geometry)
            
            # Window state
            state = self.settings.value('window_state')
            if state:
                self.restoreState(state)
            
            # Theme
            self.current_theme = self.settings.value('theme', 'dark')
            
            # Voice settings
            if self.voice_widget:
                volume_threshold = self.settings.value('voice_threshold', 30, type=int)
                silence_timeout = self.settings.value('silence_timeout', 2000, type=int)
                
                self.voice_widget.set_volume_threshold(volume_threshold)
                self.voice_widget.set_silence_timeout(silence_timeout)
            
            logger.info("⚙️ Settings loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load settings: {e}")
    
    def save_settings(self):
        """Save application settings"""
        try:
            # Window geometry and state
            self.settings.setValue('window_geometry', self.saveGeometry())
            self.settings.setValue('window_state', self.saveState())
            
            # Theme
            self.settings.setValue('theme', self.current_theme)
            
            # Voice settings
            if self.voice_widget:
                self.settings.setValue('voice_threshold', self.voice_widget.get_volume_threshold())
                self.settings.setValue('silence_timeout', self.voice_widget.get_silence_timeout())
            
            logger.info("💾 Settings saved")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save settings: {e}")
    
    def start_background_tasks(self):
        """Start background tasks and timers"""
        try:
            # System status updates every 5 seconds
            self.status_timer.start(5000)
            
            # Initial status update
            self.update_system_status()
            
            logger.info("⏰ Background tasks started")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to start background tasks: {e}")
    
    def show_welcome(self):
        """Show welcome message"""
        if self.notification_manager:
            self.notification_manager.show_notification(
                "خوش آمدید",
                "دستیار صوتی استیو آماده خدمات‌رسانی است",
                duration=3000
            )
    
    # Voice Processing Methods
    def toggle_voice_recording(self):
        """Toggle voice recording on/off"""
        if self.voice_widget:
            self.voice_widget.toggle_recording()
    
    def process_voice_data(self, audio_data: bytes):
        """Process recorded voice data"""
        if not self.api_client:
            self.handle_error("API client not available")
            return
        
        try:
            logger.info(f"🎤 Processing voice data: {len(audio_data)} bytes")
            
            # Show processing status
            if self.main_widget:
                self.main_widget.set_status("در حال پردازش صدا...")
            
            # Process in background thread
            worker = VoiceProcessingWorker(self.api_client, audio_data)
            worker.result_ready.connect(self.voice_processed.emit)
            worker.error_occurred.connect(self.error_occurred.emit)
            
            QThreadPool.globalInstance().start(worker)
            
        except Exception as e:
            logger.error(f"❌ Voice processing failed: {e}")
            self.handle_error(f"خطا در پردازش صوت: {str(e)}")
    
    def on_voice_processed(self, result: Dict[str, Any]):
        """Handle processed voice result"""
        try:
            if result.get('status') == 'success':
                response_text = result.get('response_text', '')
                audio_url = result.get('audio_url')
                
                # Display response
                if self.main_widget:
                    self.main_widget.display_response(response_text)
                
                # Play audio response
                if audio_url and self.voice_widget:
                    self.voice_widget.play_audio_response(audio_url)
                
                # Show notification
                if self.notification_manager:
                    self.notification_manager.show_notification(
                        "پاسخ استیو",
                        response_text[:100] + "..." if len(response_text) > 100 else response_text
                    )
                
                logger.info("✅ Voice processing completed successfully")
                
            else:
                error_msg = result.get('message', 'خطای نامشخص')
                self.handle_error(f"خطا در پردازش صوت: {error_msg}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle voice result: {e}")
            self.handle_error(f"خطا در نمایش نتیجه: {str(e)}")
        finally:
            if self.main_widget:
                self.main_widget.set_status("آماده")
    
    def on_recording_started(self):
        """Handle recording start"""
        self.is_voice_active = True
        if self.main_widget:
            self.main_widget.set_status("در حال ضبط...")
        
        logger.info("🎤 Voice recording started")
    
    def on_recording_stopped(self):
        """Handle recording stop"""
        self.is_voice_active = False
        if self.main_widget:
            self.main_widget.set_status("پردازش...")
        
        logger.info("⏹️ Voice recording stopped")
    
    def handle_voice_error(self, error_msg: str):
        """Handle voice recording errors"""
        self.is_voice_active = False
        if self.main_widget:
            self.main_widget.set_status("خطا در ضبط")
        
        self.handle_error(f"خطا در ضبط صوت: {error_msg}")
    
    # System Status Methods
    def update_system_status(self):
        """Update system status information"""
        if not self.api_client:
            return
        
        try:
            worker = SystemStatusWorker(self.api_client)
            worker.result_ready.connect(self.system_status_updated.emit)
            worker.error_occurred.connect(self.error_occurred.emit)
            
            QThreadPool.globalInstance().start(worker)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to update system status: {e}")
    
    def on_system_status_updated(self, status: Dict[str, Any]):
        """Handle system status update"""
        try:
            if self.main_widget:
                self.main_widget.update_system_info(status)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to handle system status: {e}")
    
    # UI Event Handlers
    def on_tray_activated(self, reason):
        """Handle system tray activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_hide_window()
    
    def show_hide_window(self):
        """Toggle window visibility"""
        if self.isVisible():
            self.hide()
        else:
            self.show_main_window()
    
    def show_main_window(self):
        """Show and activate main window"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def handle_error(self, error_msg: str):
        """Handle application errors"""
        logger.error(f"🚨 Application Error: {error_msg}")
        
        if self.notification_manager:
            self.notification_manager.show_notification(
                "خطا",
                error_msg,
                icon=NotificationManager.Icon.Critical
            )
    
    def show_error_message(self, message: str):
        """Show error message dialog"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("خطا")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def show_settings_dialog(self):
        """Show settings dialog"""
        try:
            settings_dialog = SettingsDialog(self)
            if settings_dialog.exec() == QDialog.Accepted:
                # Apply new settings
                self.load_settings()
                
        except Exception as e:
            logger.error(f"❌ Failed to show settings: {e}")
    
    # Window Events
    def closeEvent(self, event):
        """Handle window close event"""
        if self.system_tray and self.system_tray.isVisible():
            # Hide to system tray instead of closing
            event.ignore()
            self.hide()
            
            if self.notification_manager:
                self.notification_manager.show_notification(
                    "استیو",
                    "برنامه در سینی سیستم اجرا می‌شود",
                    duration=2000
                )
        else:
            # Save settings and quit
            self.save_settings()
            event.accept()
    
    def changeEvent(self, event):
        """Handle window state changes"""
        if event.type() == event.WindowStateChange:
            if self.isMinimized() and self.system_tray and self.system_tray.isVisible():
                # Hide to system tray when minimized
                QTimer.singleShot(100, self.hide)
        
        super().changeEvent(event)


# Background Worker Classes
class VoiceProcessingWorker(QRunnable):
    """Worker thread for voice processing"""
    
    result_ready = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, api_client, audio_data):
        super().__init__()
        self.api_client = api_client
        self.audio_data = audio_data
    
    def run(self):
        try:
            result = self.api_client.process_voice_data(self.audio_data)
            self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))


class SystemStatusWorker(QRunnable):
    """Worker thread for system status updates"""
    
    result_ready = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
    
    def run(self):
        try:
            status = self.api_client.get_system_status()
            self.result_ready.emit(status)
        except Exception as e:
            self.error_occurred.emit(str(e))


def main():
    """Main entry point for the desktop application"""
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Heystive Modern Desktop")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Heystive")
        app.setOrganizationDomain("heystive.com")
        
        # Set application properties
        app.setQuitOnLastWindowClosed(False)  # Keep running in system tray
        
        # Create and show main window
        main_window = HeystiveModernDesktop()
        main_window.show()
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"❌ Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()