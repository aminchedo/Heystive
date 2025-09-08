"""
Heystive Service Installation and Management
REAL IMPLEMENTATION - Production Ready
Cross-platform service management with Windows service support
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class HeystiveServiceManager:
    """Cross-platform service manager for Heystive"""
    
    def __init__(self):
        self.service_name = "HeystiveVoiceService"
        self.service_path = Path(__file__).parent
        self.service_script = self.service_path / "heystive_service.py"
        self.is_windows = os.name == 'nt'
        
        # Try to import Windows service utilities
        self.win32_available = False
        if self.is_windows:
            try:
                import win32serviceutil
                import win32service
                self.win32serviceutil = win32serviceutil
                self.win32service = win32service
                self.win32_available = True
            except ImportError:
                print("⚠️ Windows service utilities not available - using cross-platform mode")
                
    def is_service_installed(self) -> bool:
        """Check if the service is installed"""
        if self.is_windows and self.win32_available:
            try:
                self.win32serviceutil.QueryServiceStatus(self.service_name)
                return True
            except Exception:
                return False
        else:
            # For cross-platform, check if process is running
            return self.is_service_running()
            
    def is_service_running(self) -> bool:
        """Check if the service is currently running"""
        if self.is_windows and self.win32_available:
            try:
                status = self.win32serviceutil.QueryServiceStatus(self.service_name)[1]
                return status == self.win32service.SERVICE_RUNNING
            except Exception:
                return False
        else:
            # Check for running process
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "heystive_service.py"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0 and result.stdout.strip()
            except Exception:
                return False
                
    def install_service(self) -> bool:
        """Install Heystive as a service"""
        try:
            print("Installing Heystive Service...")
            
            # Verify service script exists
            if not self.service_script.exists():
                raise FileNotFoundError(f"Service script not found: {self.service_script}")
            
            if self.is_windows and self.win32_available:
                # Windows service installation
                self.win32serviceutil.InstallService(
                    pythonClassString=f"{self.service_script.stem}.HeystiveWindowsService",
                    serviceName=self.service_name,
                    displayName="Heystive Persian Voice Assistant Service",
                    startType=self.win32service.SERVICE_AUTO_START,
                    description="Always-running background service for Persian voice activation"
                )
                
                print("✓ Windows service installed successfully")
                
                # Configure service recovery
                self._configure_service_recovery()
                
            else:
                # Cross-platform installation (systemd, init.d, etc.)
                self._install_cross_platform_service()
                
            return True
            
        except Exception as e:
            print(f"✗ Service installation failed: {e}")
            return False
            
    def _configure_service_recovery(self):
        """Configure Windows service to restart automatically on failure"""
        try:
            # Use sc command to configure service recovery
            cmd = [
                'sc', 'failure', self.service_name, 
                'reset=', '86400',  # Reset failure count after 1 day
                'actions=', 'restart/60000/restart/60000/restart/60000'  # Restart after 1 minute
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Service recovery configured")
            else:
                print(f"⚠️ Service recovery configuration warning: {result.stderr}")
                
        except Exception as e:
            print(f"⚠️ Could not configure service recovery: {e}")
            
    def _install_cross_platform_service(self):
        """Install service on Unix-like systems"""
        try:
            # Create systemd service file
            if self._has_systemd():
                self._create_systemd_service()
                print("✓ Systemd service created")
            else:
                # Create startup script
                self._create_startup_script()
                print("✓ Startup script created")
                
        except Exception as e:
            print(f"⚠️ Cross-platform service installation: {e}")
            
    def _has_systemd(self) -> bool:
        """Check if systemd is available"""
        try:
            result = subprocess.run(['systemctl', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
            
    def _create_systemd_service(self):
        """Create systemd service file"""
        service_content = f"""[Unit]
Description=Heystive Persian Voice Assistant Service
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={self.service_path.parent.parent}
ExecStart={sys.executable} {self.service_script}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path("/etc/systemd/system/heystive.service")
        
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
                
            # Reload systemd and enable service
            subprocess.run(['systemctl', 'daemon-reload'], check=True)
            subprocess.run(['systemctl', 'enable', 'heystive'], check=True)
            
        except PermissionError:
            print("⚠️ Need sudo privileges to install systemd service")
            print(f"Please run: sudo cp {service_file} /etc/systemd/system/")
            
    def _create_startup_script(self):
        """Create startup script for systems without systemd"""
        startup_script = Path.home() / ".heystive_service_startup.sh"
        
        script_content = f"""#!/bin/bash
# Heystive Service Startup Script
cd {self.service_path.parent.parent}
{sys.executable} {self.service_script} &
echo $! > ~/.heystive_service.pid
"""
        
        with open(startup_script, 'w') as f:
            f.write(script_content)
            
        startup_script.chmod(0o755)
        print(f"✓ Startup script created at {startup_script}")
        
    def start_service(self) -> bool:
        """Start the Heystive service"""
        try:
            print("Starting Heystive service...")
            
            if self.is_windows and self.win32_available:
                # Windows service start
                self.win32serviceutil.StartService(self.service_name)
                
                # Wait for service to start
                time.sleep(3)
                
                # Verify service is running
                status = self.win32serviceutil.QueryServiceStatus(self.service_name)[1]
                if status == self.win32service.SERVICE_RUNNING:
                    print("✓ Windows service started successfully")
                    return True
                else:
                    print(f"✗ Service start failed - Status: {status}")
                    return False
                    
            else:
                # Cross-platform start
                if self._has_systemd():
                    result = subprocess.run(['systemctl', 'start', 'heystive'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✓ Systemd service started")
                        return True
                else:
                    # Direct process start
                    subprocess.Popen([sys.executable, str(self.service_script)], 
                                   start_new_session=True)
                    time.sleep(2)
                    if self.is_service_running():
                        print("✓ Service process started")
                        return True
                        
            return False
            
        except Exception as e:
            print(f"✗ Failed to start service: {e}")
            return False
            
    def stop_service(self) -> bool:
        """Stop the Heystive service"""
        try:
            print("Stopping Heystive service...")
            
            if self.is_windows and self.win32_available:
                # Windows service stop
                self.win32serviceutil.StopService(self.service_name)
                time.sleep(3)
                print("✓ Windows service stopped successfully")
                return True
                
            else:
                # Cross-platform stop
                if self._has_systemd():
                    result = subprocess.run(['systemctl', 'stop', 'heystive'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✓ Systemd service stopped")
                        return True
                else:
                    # Kill process directly
                    try:
                        result = subprocess.run(['pkill', '-f', 'heystive_service.py'], 
                                              capture_output=True, text=True)
                        print("✓ Service process stopped")
                        return True
                    except Exception:
                        pass
                        
            return False
            
        except Exception as e:
            print(f"✗ Failed to stop service: {e}")
            return False
            
    def uninstall_service(self) -> bool:
        """Uninstall the Heystive service"""
        try:
            print("Uninstalling Heystive service...")
            
            # Stop service first
            self.stop_service()
            
            if self.is_windows and self.win32_available:
                # Windows service removal
                self.win32serviceutil.RemoveService(self.service_name)
                print("✓ Windows service uninstalled successfully")
                
            else:
                # Cross-platform removal
                if self._has_systemd():
                    subprocess.run(['systemctl', 'disable', 'heystive'], 
                                 capture_output=True)
                    service_file = Path("/etc/systemd/system/heystive.service")
                    if service_file.exists():
                        try:
                            service_file.unlink()
                            subprocess.run(['systemctl', 'daemon-reload'])
                            print("✓ Systemd service removed")
                        except PermissionError:
                            print("⚠️ Need sudo to remove systemd service file")
                            
                # Remove startup script
                startup_script = Path.home() / ".heystive_service_startup.sh"
                if startup_script.exists():
                    startup_script.unlink()
                    
            return True
            
        except Exception as e:
            print(f"✗ Failed to uninstall service: {e}")
            return False
            
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        status = {
            'installed': self.is_service_installed(),
            'running': self.is_service_running(),
            'platform': 'Windows' if self.is_windows else 'Unix',
            'win32_available': self.win32_available,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.is_windows and self.win32_available and status['installed']:
            try:
                win_status = self.win32serviceutil.QueryServiceStatus(self.service_name)[1]
                status_map = {
                    self.win32service.SERVICE_STOPPED: "Stopped",
                    self.win32service.SERVICE_START_PENDING: "Starting",
                    self.win32service.SERVICE_STOP_PENDING: "Stopping", 
                    self.win32service.SERVICE_RUNNING: "Running",
                    self.win32service.SERVICE_CONTINUE_PENDING: "Continuing",
                    self.win32service.SERVICE_PAUSE_PENDING: "Pausing",
                    self.win32service.SERVICE_PAUSED: "Paused"
                }
                status['detailed_status'] = status_map.get(win_status, f"Unknown ({win_status})")
            except Exception as e:
                status['detailed_status'] = f"Error: {e}"
                
        return status
        
    def create_startup_shortcut(self) -> bool:
        """Create startup shortcut for manual activation"""
        try:
            if self.is_windows:
                # Windows startup folder
                import win32com.client
                
                startup_folder = os.path.join(
                    os.environ['APPDATA'], 
                    'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
                )
                
                shortcut_path = os.path.join(startup_folder, 'Heystive Voice Assistant.lnk')
                
                # Create shortcut
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = str(self.service_path.parent.parent / "main.py")
                shortcut.WorkingDirectory = str(self.service_path.parent.parent)
                shortcut.save()
                
                print(f"✓ Windows startup shortcut created: {shortcut_path}")
                
            else:
                # Unix autostart
                autostart_dir = Path.home() / ".config" / "autostart"
                autostart_dir.mkdir(parents=True, exist_ok=True)
                
                desktop_file = autostart_dir / "heystive.desktop"
                
                desktop_content = f"""[Desktop Entry]
Type=Application
Name=Heystive Voice Assistant
Comment=Persian Voice Assistant
Exec={sys.executable} {self.service_path.parent.parent / "main.py"}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
                
                with open(desktop_file, 'w') as f:
                    f.write(desktop_content)
                    
                print(f"✓ Unix autostart entry created: {desktop_file}")
                
            return True
            
        except Exception as e:
            print(f"✗ Failed to create startup shortcut: {e}")
            return False

def main():
    """Main service management interface"""
    if len(sys.argv) < 2:
        print("Heystive Service Manager")
        print("Usage:")
        print("  python service_manager.py install    - Install service")
        print("  python service_manager.py start      - Start service") 
        print("  python service_manager.py stop       - Stop service")
        print("  python service_manager.py status     - Check service status")
        print("  python service_manager.py uninstall  - Uninstall service")
        print("  python service_manager.py shortcut   - Create startup shortcut")
        return
        
    manager = HeystiveServiceManager()
    command = sys.argv[1].lower()
    
    if command == "install":
        if manager.install_service():
            print("✓ Service installation completed successfully")
            print("Use 'python service_manager.py start' to start the service")
        else:
            print("✗ Service installation failed")
            sys.exit(1)
            
    elif command == "start":
        if manager.start_service():
            print("✓ Service is now running and listening for wake words")
        else:
            print("✗ Failed to start service")
            sys.exit(1)
            
    elif command == "stop":
        if manager.stop_service():
            print("✓ Service stopped successfully")
        else:
            print("✗ Failed to stop service")
            sys.exit(1)
            
    elif command == "status":
        status = manager.get_service_status()
        print("Service Status:")
        print(f"  Installed: {status['installed']}")
        print(f"  Running: {status['running']}")
        print(f"  Platform: {status['platform']}")
        if 'detailed_status' in status:
            print(f"  Detailed Status: {status['detailed_status']}")
        print(f"  Last Check: {status['timestamp']}")
        
    elif command == "uninstall":
        if manager.uninstall_service():
            print("✓ Service uninstalled successfully")
        else:
            print("✗ Failed to uninstall service")
            sys.exit(1)
            
    elif command == "shortcut":
        if manager.create_startup_shortcut():
            print("✓ Startup shortcut created successfully")
        else:
            print("✗ Failed to create startup shortcut")
            sys.exit(1)
            
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()