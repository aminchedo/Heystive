"""
Modern Main Window Component for Heystive Desktop
Material Design interface with Persian RTL support, toolbar, sidebar, and command palette
"""

import sys
import os
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame,
    QLabel, QPushButton, QTextEdit, QScrollArea, QSplitter,
    QGroupBox, QProgressBar, QSpacerItem, QSizePolicy, QToolBar,
    QToolButton, QDialog, QLineEdit, QListWidget, QApplication,
    QMessageBox, QSystemTrayIcon, QMenu, QStatusBar
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PySide6.QtGui import QFont, QPixmap, QIcon, QKeySequence, QAction, QShortcut

from .voice_control_widget import VoiceControlWidget
from .persian_text_widget import PersianTextWidget
from .voice_visualizer import VoiceVisualizer
from .command_palette import CommandPalette

class NotificationWidget(QFrame):
    """Non-blocking notification widget"""
    
    def __init__(self, message: str, notification_type: str = "info", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setObjectName("notification")
        self.setProperty("class", notification_type)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Icon
        icon_map = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️"
        }
        icon_label = QLabel(icon_map.get(notification_type, "ℹ️"))
        icon_label.setFont(QFont("Arial", 14))
        layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setFont(QFont("Vazir", 10))
        layout.addWidget(message_label)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setMaximumSize(24, 24)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        # Auto-close timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.close)
        self.timer.start(3000)  # 3 seconds

class ModernMainWindow(QMainWindow):
    """
    Modern main window with Material Design, Persian support, toolbar, sidebar, and command palette
    """
    
    # Signals
    status_changed = Signal(str)
    response_displayed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State
        self.current_status = "آماده"
        self.system_info = {}
        self.conversation_history = []
        self.current_theme = "light"
        self.backend_url = os.environ.get("BACKEND_URL", "http://127.0.0.1:8765")
        
        # Initialize UI
        self.init_ui()
        self.setup_shortcuts()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("دستیار صوتی استیو - رابط مدرن")
        self.setMinimumSize(1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Create main content area
        content_widget = self.create_content_area()
        main_layout.addWidget(content_widget, 1)
        
        # Create status bar
        self.create_status_bar()
        
        # Apply styling
        self.apply_styling()
        
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(toolbar)
        
        # Listen action
        self.listen_action = QAction("🎤 گوش دادن", self)
        self.listen_action.setCheckable(True)
        self.listen_action.triggered.connect(self.toggle_listen)
        toolbar.addAction(self.listen_action)
        
        # Mute action
        self.mute_action = QAction("🔇 قطع صدا", self)
        self.mute_action.triggered.connect(self.mute_listening)
        toolbar.addAction(self.mute_action)
        
        toolbar.addSeparator()
        
        # Logs action
        logs_action = QAction("📋 گزارشات", self)
        logs_action.triggered.connect(self.open_logs)
        toolbar.addAction(logs_action)
        
        # Models action
        models_action = QAction("🤖 مدل‌ها", self)
        models_action.triggered.connect(self.open_models)
        toolbar.addAction(models_action)
        
        toolbar.addSeparator()
        
        # Settings action
        settings_action = QAction("⚙️ تنظیمات", self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
        
        # Theme action
        self.theme_action = QAction("🌙 تم تاریک", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(self.theme_action)
        
        toolbar.addSeparator()
        
        # Commands action
        commands_action = QAction("⌘ دستورات", self)
        commands_action.triggered.connect(self.open_command_palette)
        toolbar.addAction(commands_action)
        
    def create_sidebar(self):
        """Create right-to-left safe sidebar"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMaximumWidth(250)
        sidebar.setMinimumWidth(200)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)
        
        # System status section
        status_group = QGroupBox("وضعیت سیستم")
        status_layout = QVBoxLayout(status_group)
        
        self.cpu_label = QLabel("پردازنده: 0%")
        self.memory_label = QLabel("حافظه: 0%")
        self.disk_label = QLabel("دیسک: 0%")
        
        for label in [self.cpu_label, self.memory_label, self.disk_label]:
            label.setFont(QFont("Vazir", 9))
            status_layout.addWidget(label)
        
        layout.addWidget(status_group)
        
        # Quick toggles section
        toggles_group = QGroupBox("تنظیمات سریع")
        toggles_layout = QVBoxLayout(toggles_group)
        
        self.auto_listen_btn = QPushButton("گوش دادن خودکار")
        self.auto_listen_btn.setCheckable(True)
        self.auto_listen_btn.clicked.connect(self.toggle_auto_listen)
        
        self.notifications_btn = QPushButton("اعلان‌ها")
        self.notifications_btn.setCheckable(True)
        self.notifications_btn.setChecked(True)
        self.notifications_btn.clicked.connect(self.toggle_notifications)
        
        self.rtl_btn = QPushButton("راست به چپ")
        self.rtl_btn.setCheckable(True)
        self.rtl_btn.setChecked(True)
        self.rtl_btn.clicked.connect(self.toggle_rtl)
        
        for btn in [self.auto_listen_btn, self.notifications_btn, self.rtl_btn]:
            btn.setFont(QFont("Vazir", 9))
            toggles_layout.addWidget(btn)
        
        layout.addWidget(toggles_group)
        
        # Connection status
        connection_group = QGroupBox("وضعیت اتصال")
        connection_layout = QVBoxLayout(connection_group)
        
        self.backend_status = QLabel("Backend: قطع شده")
        self.api_status = QLabel("API: قطع شده")
        
        for label in [self.backend_status, self.api_status]:
            label.setFont(QFont("Vazir", 9))
            connection_layout.addWidget(label)
        
        layout.addWidget(connection_group)
        
        layout.addStretch()
        
        return sidebar
        
    def create_content_area(self):
        """Create main content area with tabs"""
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # Voice Control Tab
        voice_tab = self.create_voice_tab()
        self.tab_widget.addTab(voice_tab, "🎤 کنترل صوتی")
        
        # Conversation Tab
        conversation_tab = self.create_conversation_tab()
        self.tab_widget.addTab(conversation_tab, "💬 گفتگو")
        
        # System Info Tab
        system_tab = self.create_system_tab()
        self.tab_widget.addTab(system_tab, "📊 سیستم")
        
        return self.tab_widget
        
    def create_voice_tab(self):
        """Create voice control tab"""
        voice_widget = QWidget()
        voice_layout = QVBoxLayout(voice_widget)
        voice_layout.setContentsMargins(20, 20, 20, 20)
        voice_layout.setSpacing(20)
        
        # Voice control widget
        self.voice_widget = VoiceControlWidget()
        voice_layout.addWidget(self.voice_widget)
        
        # Voice visualizer
        visualizer_group = QGroupBox("نمایش صوتی")
        visualizer_layout = QVBoxLayout(visualizer_group)
        
        self.voice_visualizer = VoiceVisualizer()
        visualizer_layout.addWidget(self.voice_visualizer)
        
        voice_layout.addWidget(visualizer_group)
        
        # Quick commands
        commands_group = self.create_quick_commands()
        voice_layout.addWidget(commands_group)
        
        voice_layout.addStretch()
        
        return voice_widget
        
    def create_conversation_tab(self):
        """Create conversation history tab"""
        conversation_widget = QWidget()
        conversation_layout = QVBoxLayout(conversation_widget)
        conversation_layout.setContentsMargins(20, 20, 20, 20)
        conversation_layout.setSpacing(15)
        
        # Conversation display
        self.conversation_display = PersianTextWidget()
        self.conversation_display.setMinimumHeight(300)
        self.conversation_display.setReadOnly(True)
        
        conversation_layout.addWidget(QLabel("تاریخچه گفتگو"))
        conversation_layout.addWidget(self.conversation_display)
        
        # Current response display
        response_group = QGroupBox("آخرین پاسخ")
        response_layout = QVBoxLayout(response_group)
        
        self.response_display = PersianTextWidget()
        self.response_display.setMaximumHeight(150)
        self.response_display.setReadOnly(True)
        self.response_display.setPlaceholderText("پاسخ استیو اینجا نمایش داده می‌شود...")
        
        response_layout.addWidget(self.response_display)
        
        conversation_layout.addWidget(response_group)
        
        # Response actions
        actions_layout = QHBoxLayout()
        
        play_button = QPushButton("🔊 پخش صوتی")
        play_button.clicked.connect(self.play_last_response)
        
        copy_button = QPushButton("📋 کپی متن")
        copy_button.clicked.connect(self.copy_response)
        
        clear_button = QPushButton("🗑️ پاک کردن")
        clear_button.clicked.connect(self.clear_conversation)
        
        actions_layout.addWidget(play_button)
        actions_layout.addWidget(copy_button)
        actions_layout.addStretch()
        actions_layout.addWidget(clear_button)
        
        conversation_layout.addLayout(actions_layout)
        
        return conversation_widget
        
    def create_system_tab(self):
        """Create system information tab"""
        system_widget = QWidget()
        system_layout = QVBoxLayout(system_widget)
        system_layout.setContentsMargins(20, 20, 20, 20)
        system_layout.setSpacing(15)
        
        # System status group
        status_group = QGroupBox("وضعیت سیستم")
        status_layout = QVBoxLayout(status_group)
        
        self.cpu_progress = self.create_progress_item("پردازنده:", "0%")
        self.memory_progress = self.create_progress_item("حافظه:", "0%")
        self.disk_progress = self.create_progress_item("دیسک:", "0%")
        
        status_layout.addWidget(self.cpu_progress)
        status_layout.addWidget(self.memory_progress)
        status_layout.addWidget(self.disk_progress)
        
        system_layout.addWidget(status_group)
        
        # Voice assistant status
        assistant_group = QGroupBox("وضعیت دستیار صوتی")
        assistant_layout = QVBoxLayout(assistant_group)
        
        self.assistant_status = QLabel("در حال بارگذاری...")
        self.assistant_status.setFont(QFont("Vazir", 10))
        
        self.tts_engines = QLabel("موتورهای TTS: در حال بارگذاری...")
        self.tts_engines.setFont(QFont("Vazir", 9))
        self.tts_engines.setStyleSheet("color: #718096;")
        
        assistant_layout.addWidget(self.assistant_status)
        assistant_layout.addWidget(self.tts_engines)
        
        system_layout.addWidget(assistant_group)
        
        system_layout.addStretch()
        
        return system_widget
        
    def create_quick_commands(self):
        """Create quick command buttons"""
        commands_group = QGroupBox("دستورات سریع")
        commands_layout = QVBoxLayout(commands_group)
        
        # First row
        row1_layout = QHBoxLayout()
        
        time_btn = QPushButton("🕐 ساعت چنده؟")
        time_btn.clicked.connect(lambda: self.send_quick_command("ساعت چنده؟"))
        
        weather_btn = QPushButton("🌤️ هوا چطوره؟")
        weather_btn.clicked.connect(lambda: self.send_quick_command("هوا چطوره؟"))
        
        news_btn = QPushButton("📰 چه خبر؟")
        news_btn.clicked.connect(lambda: self.send_quick_command("چه خبر؟"))
        
        row1_layout.addWidget(time_btn)
        row1_layout.addWidget(weather_btn)
        row1_layout.addWidget(news_btn)
        
        # Second row
        row2_layout = QHBoxLayout()
        
        music_btn = QPushButton("🎵 موسیقی پخش کن")
        music_btn.clicked.connect(lambda: self.send_quick_command("موسیقی پخش کن"))
        
        calc_btn = QPushButton("🧮 ماشین حساب")
        calc_btn.clicked.connect(lambda: self.send_quick_command("ماشین حساب"))
        
        help_btn = QPushButton("❓ راهنما")
        help_btn.clicked.connect(lambda: self.send_quick_command("راهنمایی بده"))
        
        row2_layout.addWidget(music_btn)
        row2_layout.addWidget(calc_btn)
        row2_layout.addWidget(help_btn)
        
        commands_layout.addLayout(row1_layout)
        commands_layout.addLayout(row2_layout)
        
        return commands_group
        
    def create_progress_item(self, label: str, value: str):
        """Create a progress bar item"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Vazir", 9))
        label_widget.setMinimumWidth(80)
        
        progress = QProgressBar()
        progress.setMaximumHeight(20)
        progress.setValue(0)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Vazir", 9))
        value_label.setMinimumWidth(50)
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(label_widget)
        layout.addWidget(progress, 1)
        layout.addWidget(value_label)
        
        # Store references
        container.progress = progress
        container.value_label = value_label
        
        return container
        
    def create_status_bar(self):
        """Create status bar"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Connection indicator
        self.connection_indicator = QLabel("🔴 قطع شده")
        self.connection_indicator.setFont(QFont("Vazir", 9))
        status_bar.addWidget(self.connection_indicator)
        
        # Voice status
        self.voice_status_indicator = QLabel("🎤 آماده")
        self.voice_status_indicator.setFont(QFont("Vazir", 9))
        status_bar.addWidget(self.voice_status_indicator)
        
        # Time
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Vazir", 9))
        status_bar.addPermanentWidget(self.time_label)
        
        # Update time
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Command palette shortcut
        self.cmd_palette_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        self.cmd_palette_shortcut.activated.connect(self.open_command_palette)
        
    def apply_styling(self):
        """Apply custom styling from stylesheet"""
        stylesheet_path = Path(__file__).parent.parent / "assets" / "style.qss"
        if stylesheet_path.exists():
            with open(stylesheet_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        
    def load_settings(self):
        """Load settings from backend"""
        try:
            response = requests.get(f"{self.backend_url}/api/settings", timeout=5)
            if response.status_code == 200:
                settings = response.json()
                self.current_theme = settings.get("theme", "light")
                self.apply_theme()
                self.show_notification("تنظیمات بارگذاری شد", "success")
        except Exception as e:
            self.show_notification(f"خطا در بارگذاری تنظیمات: {str(e)}", "error")
            
    def apply_theme(self):
        """Apply current theme"""
        if self.current_theme == "dark":
            self.setProperty("darkTheme", True)
            self.theme_action.setText("☀️ تم روشن")
        else:
            self.setProperty("darkTheme", False)
            self.theme_action.setText("🌙 تم تاریک")
        self.style().unpolish(self)
        self.style().polish(self)
        
    def show_notification(self, message: str, notification_type: str = "info"):
        """Show non-blocking notification"""
        notification = NotificationWidget(message, notification_type, self)
        notification.move(self.width() - notification.width() - 20, 50)
        notification.show()
        
        # Auto-remove after animation
        QTimer.singleShot(3000, notification.deleteLater)
        
    # Toolbar Actions
    def toggle_listen(self):
        """Toggle listening state"""
        try:
            if self.listen_action.isChecked():
                response = requests.post(f"{self.backend_url}/api/intent", 
                                       json={"text": "listen"}, timeout=5)
                if response.status_code == 200:
                    self.show_notification("گوش دادن شروع شد", "success")
                    self.voice_visualizer.start_listening()
                else:
                    self.show_notification("خطا در شروع گوش دادن", "error")
                    self.listen_action.setChecked(False)
            else:
                response = requests.post(f"{self.backend_url}/api/intent", 
                                       json={"text": "mute"}, timeout=5)
                if response.status_code == 200:
                    self.show_notification("گوش دادن متوقف شد", "info")
                    self.voice_visualizer.stop_listening()
        except Exception as e:
            self.show_notification(f"خطا: {str(e)}", "error")
            self.listen_action.setChecked(False)
            
    def mute_listening(self):
        """Mute listening"""
        try:
            response = requests.post(f"{self.backend_url}/api/intent", 
                                   json={"text": "mute"}, timeout=5)
            if response.status_code == 200:
                self.show_notification("صدا قطع شد", "info")
                self.listen_action.setChecked(False)
                self.voice_visualizer.stop_listening()
        except Exception as e:
            self.show_notification(f"خطا: {str(e)}", "error")
            
    def open_logs(self):
        """Open logs in browser"""
        import webbrowser
        webbrowser.open(f"{self.backend_url}/api/logs")
        
    def open_models(self):
        """Open models in browser"""
        import webbrowser
        webbrowser.open(f"{self.backend_url}/api/models")
        
    def open_settings(self):
        """Open settings in browser"""
        import webbrowser
        webbrowser.open(f"{self.backend_url}/settings")
        
    def toggle_theme(self):
        """Toggle theme"""
        try:
            new_theme = "dark" if self.current_theme == "light" else "light"
            response = requests.put(f"{self.backend_url}/api/settings", 
                                  json={"theme": new_theme}, timeout=5)
            if response.status_code == 200:
                self.current_theme = new_theme
                self.apply_theme()
                self.show_notification(f"تم به {new_theme} تغییر کرد", "success")
            else:
                self.show_notification("خطا در تغییر تم", "error")
        except Exception as e:
            self.show_notification(f"خطا: {str(e)}", "error")
            
    def open_command_palette(self):
        """Open command palette"""
        palette = CommandPalette(self)
        palette.exec()
        
    # Sidebar Actions
    def toggle_auto_listen(self):
        """Toggle auto listen"""
        if self.auto_listen_btn.isChecked():
            self.show_notification("گوش دادن خودکار فعال شد", "info")
        else:
            self.show_notification("گوش دادن خودکار غیرفعال شد", "info")
            
    def toggle_notifications(self):
        """Toggle notifications"""
        if self.notifications_btn.isChecked():
            self.show_notification("اعلان‌ها فعال شد", "info")
        else:
            self.show_notification("اعلان‌ها غیرفعال شد", "info")
            
    def toggle_rtl(self):
        """Toggle RTL layout"""
        if self.rtl_btn.isChecked():
            self.setLayoutDirection(Qt.RightToLeft)
            self.show_notification("راست به چپ فعال شد", "info")
        else:
            self.setLayoutDirection(Qt.LeftToRight)
            self.show_notification("چپ به راست فعال شد", "info")
            
    # Public Methods
    def set_status(self, status: str):
        """Set application status"""
        self.current_status = status
        self.status_changed.emit(status)
        
    def display_response(self, response: str):
        """Display assistant response"""
        self.response_display.setText(response)
        self.add_to_conversation("استیو", response)
        self.response_displayed.emit(response)
        
    def add_to_conversation(self, speaker: str, message: str):
        """Add message to conversation history"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M")
        formatted_message = f"[{timestamp}] {speaker}: {message}\n\n"
        
        current_text = self.conversation_display.toPlainText()
        self.conversation_display.setText(current_text + formatted_message)
        
        # Scroll to bottom
        cursor = self.conversation_display.textCursor()
        cursor.movePosition(cursor.End)
        self.conversation_display.setTextCursor(cursor)
        
        # Store in history
        self.conversation_history.append({
            'timestamp': timestamp,
            'speaker': speaker,
            'message': message
        })
        
    def update_system_info(self, info: Dict[str, Any]):
        """Update system information display"""
        self.system_info = info
        
        # Update progress bars
        system_info = info.get('system', {})
        
        if 'cpu_usage' in system_info:
            cpu_value = int(system_info['cpu_usage'].replace('%', ''))
            self.cpu_progress.progress.setValue(cpu_value)
            self.cpu_progress.value_label.setText(system_info['cpu_usage'])
            self.cpu_label.setText(f"پردازنده: {system_info['cpu_usage']}")
            
        if 'memory_usage' in system_info:
            memory_value = int(system_info['memory_usage'].replace('%', ''))
            self.memory_progress.progress.setValue(memory_value)
            self.memory_progress.value_label.setText(system_info['memory_usage'])
            self.memory_label.setText(f"حافظه: {system_info['memory_usage']}")
            
        if 'disk_usage' in system_info:
            disk_value = int(system_info['disk_usage'].replace('%', ''))
            self.disk_progress.progress.setValue(disk_value)
            self.disk_progress.value_label.setText(system_info['disk_usage'])
            self.disk_label.setText(f"دیسک: {system_info['disk_usage']}")
            
        # Update assistant status
        voice_assistant = info.get('voice_assistant', {})
        if 'status' in voice_assistant:
            status_text = "فعال" if voice_assistant['status'] == 'ready' else "غیرفعال"
            self.assistant_status.setText(f"وضعیت: {status_text}")
            
        if 'tts_engines' in voice_assistant:
            engines = ", ".join(voice_assistant['tts_engines'])
            self.tts_engines.setText(f"موتورهای TTS: {engines}")
            
        # Update connection status
        if info.get('status') == 'running':
            self.backend_status.setText("Backend: متصل")
            self.backend_status.setStyleSheet("color: #4CAF50;")
            self.connection_indicator.setText("🟢 متصل")
        else:
            self.backend_status.setText("Backend: قطع شده")
            self.backend_status.setStyleSheet("color: #F44336;")
            self.connection_indicator.setText("🔴 قطع شده")
            
    # Slot Methods
    def send_quick_command(self, command: str):
        """Send quick command to voice widget"""
        if self.voice_widget:
            self.voice_widget.send_text_command(command)
            self.add_to_conversation("شما", command)
            
    def play_last_response(self):
        """Play last audio response"""
        if self.voice_widget:
            self.voice_widget.play_last_audio()
            
    def copy_response(self):
        """Copy response text to clipboard"""
        text = self.response_display.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.show_notification("متن کپی شد", "success")
            
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_display.clear()
        self.conversation_history.clear()
        self.show_notification("تاریخچه پاک شد", "info")
        
    def update_time(self):
        """Update time display"""
        from datetime import datetime
        
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y/%m/%d")
        
        # Convert to Persian digits
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        for i, digit in enumerate("0123456789"):
            time_str = time_str.replace(digit, persian_digits[i])
            date_str = date_str.replace(digit, persian_digits[i])
            
        self.time_label.setText(f"{time_str} - {date_str}")
        
    # Properties
    @property
    def voice_widget(self):
        """Get voice control widget"""
        return getattr(self, '_voice_widget', None)
        
    @voice_widget.setter
    def voice_widget(self, widget):
        """Set voice control widget"""
        self._voice_widget = widget