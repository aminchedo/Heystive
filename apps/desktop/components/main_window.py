"""
Modern Main Window Component for Heystive Desktop
Material Design interface with Persian RTL support
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame,
    QLabel, QPushButton, QTextEdit, QScrollArea, QSplitter,
    QGroupBox, QProgressBar, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPixmap, QIcon

from .voice_control_widget import VoiceControlWidget
from .persian_text_widget import PersianTextWidget
from .voice_visualizer import VoiceVisualizer

class ModernMainWindow(QWidget):
    """
    Modern main window with Material Design and Persian support
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
        
        # Animations
        self.status_animation = None
        
        # Initialize UI
        self.init_ui()
        self.setup_animations()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create header
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Create main content area with tabs
        content_widget = self.create_content_area()
        main_layout.addWidget(content_widget, 1)
        
        # Create status bar
        status_widget = self.create_status_bar()
        main_layout.addWidget(status_widget)
        
        # Apply styling
        self.apply_styling()
        
    def create_header(self):
        """Create application header"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_frame.setMaximumHeight(80)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Logo and title
        logo_label = QLabel()
        logo_pixmap = QPixmap(str(Path(__file__).parent.parent / "resources" / "icons" / "heystive_logo.png"))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("🎤")
            logo_label.setFont(QFont("Arial", 24))
        
        title_label = QLabel("دستیار صوتی استیو")
        title_label.setFont(QFont("Vazir", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("رابط کاربری مدرن")
        subtitle_label.setFont(QFont("Vazir", 10))
        subtitle_label.setStyleSheet("color: #718096;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        # Title container
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Status indicator
        self.status_label = QLabel(self.current_status)
        self.status_label.setFont(QFont("Vazir", 10))
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Layout
        header_layout.addWidget(logo_label)
        header_layout.addSpacing(15)
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        
        return header_frame
        
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
        
        # Connection status
        connection_group = QGroupBox("وضعیت اتصال")
        connection_layout = QVBoxLayout(connection_group)
        
        self.backend_status = QLabel("Backend: قطع شده")
        self.backend_status.setFont(QFont("Vazir", 10))
        
        self.api_status = QLabel("API: قطع شده")
        self.api_status.setFont(QFont("Vazir", 10))
        
        connection_layout.addWidget(self.backend_status)
        connection_layout.addWidget(self.api_status)
        
        system_layout.addWidget(connection_group)
        
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
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_frame.setMaximumHeight(40)
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 5, 15, 5)
        
        # Connection indicator
        self.connection_indicator = QLabel("🔴 قطع شده")
        self.connection_indicator.setFont(QFont("Vazir", 9))
        
        # Voice status
        self.voice_status_indicator = QLabel("🎤 آماده")
        self.voice_status_indicator.setFont(QFont("Vazir", 9))
        
        # Time
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Vazir", 9))
        
        # Update time
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()
        
        status_layout.addWidget(self.connection_indicator)
        status_layout.addSpacing(20)
        status_layout.addWidget(self.voice_status_indicator)
        status_layout.addStretch()
        status_layout.addWidget(self.time_label)
        
        return status_frame
        
    def setup_animations(self):
        """Setup UI animations"""
        # Status label animation
        self.status_animation = QPropertyAnimation(self.status_label, b"geometry")
        self.status_animation.setDuration(300)
        self.status_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def apply_styling(self):
        """Apply custom styling"""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
            }
            
            QTabWidget::tab-bar {
                alignment: center;
            }
            
            QTabBar::tab {
                background-color: #F5F5F5;
                color: #333333;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
                font-family: 'Vazir';
                font-size: 10pt;
            }
            
            QTabBar::tab:selected {
                background-color: #1565C0;
                color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #E3F2FD;
            }
            
            QGroupBox {
                font-family: 'Vazir';
                font-size: 11pt;
                font-weight: bold;
                color: #333333;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin: 10px 0px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
            }
            
            QPushButton {
                font-family: 'Vazir';
                font-size: 10pt;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                background-color: #1565C0;
                color: white;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #0D47A1;
                transform: translateY(-1px);
            }
            
            QPushButton:pressed {
                background-color: #0A3D91;
            }
            
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                text-align: center;
                font-family: 'Vazir';
                font-size: 9pt;
            }
            
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
    # Public Methods
    def set_status(self, status: str):
        """Set application status"""
        self.current_status = status
        self.status_label.setText(status)
        
        # Update status color based on content
        if "خطا" in status:
            color = "#F44336"  # Red
        elif "پردازش" in status or "ضبط" in status:
            color = "#FF9800"  # Orange
        else:
            color = "#4CAF50"  # Green
            
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
                font-weight: bold;
            }}
        """)
        
        self.status_changed.emit(status)
        
    def display_response(self, response: str):
        """Display assistant response"""
        self.response_display.setText(response)
        
        # Add to conversation history
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
            
        if 'memory_usage' in system_info:
            memory_value = int(system_info['memory_usage'].replace('%', ''))
            self.memory_progress.progress.setValue(memory_value)
            self.memory_progress.value_label.setText(system_info['memory_usage'])
            
        if 'disk_usage' in system_info:
            disk_value = int(system_info['disk_usage'].replace('%', ''))
            self.disk_progress.progress.setValue(disk_value)
            self.disk_progress.value_label.setText(system_info['disk_usage'])
            
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
            self.set_status("متن کپی شد")
            
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_display.clear()
        self.conversation_history.clear()
        self.set_status("تاریخچه پاک شد")
        
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