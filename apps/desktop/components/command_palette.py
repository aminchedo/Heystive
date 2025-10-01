"""
Command Palette Component for Heystive Desktop
Searchable command interface with server integration
"""

import requests
import json
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, 
    QPushButton, QLabel, QFrame, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer, pyqtSignal
from PySide6.QtGui import QFont, QKeySequence, QShortcut

class CommandPalette(QDialog):
    """Command palette dialog for executing server commands"""
    
    # Signals
    command_executed = Signal(str, dict)  # command_name, result
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("دستورات - Command Palette")
        self.setObjectName("commandPalette")
        self.setMinimumSize(600, 400)
        
        # State
        self.commands = []
        self.backend_url = "http://127.0.0.1:8765"
        
        # Initialize UI
        self.init_ui()
        self.setup_shortcuts()
        self.load_commands()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("دستورات در دسترس")
        title_label.setFont(QFont("Vazir", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("جستجو در دستورات... (Ctrl+F)")
        self.search_edit.setFont(QFont("Vazir", 11))
        self.search_edit.textChanged.connect(self.filter_commands)
        layout.addWidget(self.search_edit)
        
        # Commands list
        self.commands_list = QListWidget()
        self.commands_list.setFont(QFont("Vazir", 10))
        self.commands_list.itemDoubleClicked.connect(self.run_selected_command)
        layout.addWidget(self.commands_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("اجرا (Enter)")
        self.run_button.clicked.connect(self.run_selected_command)
        self.run_button.setDefault(True)
        
        self.refresh_button = QPushButton("تازه‌سازی (F5)")
        self.refresh_button.clicked.connect(self.load_commands)
        
        self.close_button = QPushButton("بستن (Esc)")
        self.close_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("آماده")
        self.status_label.setFont(QFont("Vazir", 9))
        self.status_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.status_label)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Enter to run
        self.run_shortcut = QShortcut(QKeySequence("Return"), self)
        self.run_shortcut.activated.connect(self.run_selected_command)
        
        # Escape to close
        self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.close_shortcut.activated.connect(self.reject)
        
        # F5 to refresh
        self.refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        self.refresh_shortcut.activated.connect(self.load_commands)
        
        # Ctrl+F to focus search
        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(self.search_edit.setFocus)
        
    def load_commands(self):
        """Load commands from server"""
        self.status_label.setText("در حال بارگذاری دستورات...")
        self.status_label.setStyleSheet("color: #FF9800;")
        
        try:
            response = requests.get(f"{self.backend_url}/api/commands/list", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    self.commands = data.get("commands", [])
                    self.render_commands(self.commands)
                    self.status_label.setText(f"{len(self.commands)} دستور بارگذاری شد")
                    self.status_label.setStyleSheet("color: #4CAF50;")
                else:
                    self.status_label.setText("خطا در دریافت دستورات")
                    self.status_label.setStyleSheet("color: #F44336;")
            else:
                self.status_label.setText("خطا در اتصال به سرور")
                self.status_label.setStyleSheet("color: #F44336;")
        except Exception as e:
            self.status_label.setText(f"خطا: {str(e)}")
            self.status_label.setStyleSheet("color: #F44336;")
            
    def render_commands(self, commands: List[Dict[str, Any]]):
        """Render commands in the list"""
        self.commands_list.clear()
        
        for cmd in commands:
            name = cmd.get("name", "")
            title = cmd.get("title", "")
            description = cmd.get("description", "")
            
            # Create display text
            display_text = f"{name} — {title}"
            if description:
                display_text += f"\n  {description}"
                
            # Create list item
            item = self.commands_list.addItem(display_text)
            item.setData(Qt.UserRole, cmd)  # Store command data
            
    def filter_commands(self, search_text: str):
        """Filter commands based on search text"""
        if not search_text.strip():
            self.render_commands(self.commands)
            return
            
        search_lower = search_text.strip().lower()
        filtered_commands = []
        
        for cmd in self.commands:
            name = cmd.get("name", "").lower()
            title = cmd.get("title", "").lower()
            description = cmd.get("description", "").lower()
            
            if (search_lower in name or 
                search_lower in title or 
                search_lower in description):
                filtered_commands.append(cmd)
                
        self.render_commands(filtered_commands)
        
    def run_selected_command(self):
        """Run the selected command"""
        current_item = self.commands_list.currentItem()
        if not current_item:
            self.status_label.setText("لطفاً یک دستور انتخاب کنید")
            self.status_label.setStyleSheet("color: #FF9800;")
            return
            
        command_data = current_item.data(Qt.UserRole)
        if not command_data:
            self.status_label.setText("خطا در داده‌های دستور")
            self.status_label.setStyleSheet("color: #F44336;")
            return
            
        command_name = command_data.get("name")
        if not command_name:
            self.status_label.setText("نام دستور یافت نشد")
            self.status_label.setStyleSheet("color: #F44336;")
            return
            
        # Execute command
        self.execute_command(command_name, {})
        
    def execute_command(self, command_name: str, args: Dict[str, Any]):
        """Execute a command on the server"""
        self.status_label.setText(f"در حال اجرای {command_name}...")
        self.status_label.setStyleSheet("color: #FF9800;")
        
        try:
            payload = {
                "name": command_name,
                "args": args
            }
            
            response = requests.post(
                f"{self.backend_url}/api/commands/run", 
                json=payload, 
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    self.status_label.setText(f"دستور {command_name} با موفقیت اجرا شد")
                    self.status_label.setStyleSheet("color: #4CAF50;")
                    self.command_executed.emit(command_name, result.get("data", {}))
                    
                    # Auto-close after successful execution
                    QTimer.singleShot(1000, self.accept)
                else:
                    error_msg = result.get("error", "خطای نامشخص")
                    self.status_label.setText(f"خطا: {error_msg}")
                    self.status_label.setStyleSheet("color: #F44336;")
            else:
                self.status_label.setText(f"خطای HTTP {response.status_code}")
                self.status_label.setStyleSheet("color: #F44336;")
                
        except requests.exceptions.Timeout:
            self.status_label.setText("زمان اتصال به سرور تمام شد")
            self.status_label.setStyleSheet("color: #F44336;")
        except Exception as e:
            self.status_label.setText(f"خطا: {str(e)}")
            self.status_label.setStyleSheet("color: #F44336;")
            
    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        self.search_edit.setFocus()
        self.search_edit.selectAll()
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down:
            # Let the list widget handle navigation
            super().keyPressEvent(event)
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.run_selected_command()
        elif event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)