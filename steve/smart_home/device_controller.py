"""
Smart Home Device Controller
Real implementation for controlling smart home devices via Persian commands
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
import json
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class SmartHomeController:
    """
    Complete smart home device controller
    Supports Kasa, Philips Hue, and other smart home protocols
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.devices = {}
        self.device_types = {}
        
        # Persian device name mappings
        self.persian_device_names = {}
        
        # Connection status
        self.kasa_available = False
        self.hue_available = False
        self.mqtt_available = False
        
        # Performance tracking
        self.control_stats = {
            "total_commands": 0,
            "successful_commands": 0,
            "device_response_times": {},
            "error_count": 0
        }
        
        # Initialize device controllers
        asyncio.create_task(self._initialize_controllers())
    
    async def _initialize_controllers(self):
        """Initialize all smart home device controllers"""
        try:
            logger.info("Initializing smart home controllers...")
            
            # Initialize Kasa (TP-Link) devices
            await self._initialize_kasa_devices()
            
            # Initialize Philips Hue devices
            await self._initialize_hue_devices()
            
            # Initialize MQTT devices
            await self._initialize_mqtt_devices()
            
            logger.info(f"Smart home initialization complete. Found {len(self.devices)} devices.")
            
        except Exception as e:
            logger.error(f"Smart home initialization failed: {e}")
    
    async def _initialize_kasa_devices(self):
        """Initialize TP-Link Kasa smart devices"""
        try:
            from kasa import Discover
            
            logger.info("Discovering Kasa devices...")
            devices = await Discover.discover()
            
            for addr, dev in devices.items():
                try:
                    await dev.update()
                    
                    device_info = {
                        "device": dev,
                        "type": self._determine_device_type(dev),
                        "name": dev.alias,
                        "ip": addr,
                        "protocol": "kasa",
                        "capabilities": self._get_device_capabilities(dev)
                    }
                    
                    self.devices[dev.alias] = device_info
                    self.device_types[dev.alias] = device_info["type"]
                    
                    # Create Persian name mapping
                    persian_name = self._create_persian_device_name(dev.alias, device_info["type"])
                    self.persian_device_names[persian_name] = dev.alias
                    
                    logger.info(f"Added Kasa device: {dev.alias} ({device_info['type']}) at {addr}")
                    
                except Exception as e:
                    logger.warning(f"Failed to initialize Kasa device at {addr}: {e}")
            
            if devices:
                self.kasa_available = True
                logger.info(f"Kasa controller initialized with {len(devices)} devices")
            
        except ImportError:
            logger.warning("python-kasa not installed. Install with: pip install python-kasa")
        except Exception as e:
            logger.error(f"Kasa initialization failed: {e}")
    
    async def _initialize_hue_devices(self):
        """Initialize Philips Hue smart devices"""
        try:
            from phue import Bridge
            
            # Try to find Hue bridge
            bridge_ip = self.config.get("hue_bridge_ip")
            if not bridge_ip:
                # Auto-discover bridge
                bridge_ip = await self._discover_hue_bridge()
            
            if bridge_ip:
                bridge = Bridge(bridge_ip)
                
                # Connect to bridge (may require button press on first run)
                try:
                    bridge.connect()
                    
                    # Get all lights
                    lights = bridge.lights
                    
                    for light in lights:
                        device_info = {
                            "device": light,
                            "type": "light",
                            "name": light.name,
                            "bridge_ip": bridge_ip,
                            "protocol": "hue",
                            "capabilities": ["on_off", "brightness", "color"]
                        }
                        
                        self.devices[light.name] = device_info
                        self.device_types[light.name] = "light"
                        
                        # Create Persian name mapping
                        persian_name = self._create_persian_device_name(light.name, "light")
                        self.persian_device_names[persian_name] = light.name
                        
                        logger.info(f"Added Hue light: {light.name}")
                    
                    self.hue_available = True
                    logger.info(f"Hue controller initialized with {len(lights)} lights")
                    
                except Exception as e:
                    logger.warning(f"Hue bridge connection failed: {e}")
                    logger.info("Press the button on your Hue bridge and restart Steve")
            
        except ImportError:
            logger.warning("phue not installed. Install with: pip install phue")
        except Exception as e:
            logger.error(f"Hue initialization failed: {e}")
    
    async def _initialize_mqtt_devices(self):
        """Initialize MQTT-based smart devices"""
        try:
            import paho.mqtt.client as mqtt
            
            mqtt_broker = self.config.get("mqtt_broker", "localhost")
            mqtt_port = self.config.get("mqtt_port", 1883)
            
            # This is a placeholder for MQTT device discovery
            # In a real implementation, you would:
            # 1. Connect to MQTT broker
            # 2. Subscribe to device discovery topics
            # 3. Parse device announcements
            # 4. Add discovered devices to self.devices
            
            logger.info("MQTT device discovery not implemented yet")
            
        except ImportError:
            logger.warning("paho-mqtt not installed. Install with: pip install paho-mqtt")
        except Exception as e:
            logger.error(f"MQTT initialization failed: {e}")
    
    async def _discover_hue_bridge(self) -> Optional[str]:
        """Auto-discover Philips Hue bridge on network"""
        try:
            import requests
            
            # Use Philips discovery service
            response = requests.get("https://discovery.meethue.com/", timeout=5)
            if response.status_code == 200:
                bridges = response.json()
                if bridges:
                    return bridges[0]["internalipaddress"]
            
            return None
            
        except Exception as e:
            logger.warning(f"Hue bridge discovery failed: {e}")
            return None
    
    def _determine_device_type(self, device) -> str:
        """Determine device type from device object"""
        try:
            device_type = str(type(device).__name__).lower()
            
            if "bulb" in device_type or "light" in device_type:
                return "light"
            elif "plug" in device_type or "outlet" in device_type:
                return "outlet"
            elif "switch" in device_type:
                return "switch"
            elif "strip" in device_type:
                return "power_strip"
            else:
                return "unknown"
                
        except Exception as e:
            logger.warning(f"Device type determination failed: {e}")
            return "unknown"
    
    def _get_device_capabilities(self, device) -> List[str]:
        """Get device capabilities"""
        capabilities = ["on_off"]
        
        try:
            if hasattr(device, 'brightness'):
                capabilities.append("brightness")
            if hasattr(device, 'color_temp'):
                capabilities.append("color_temperature")
            if hasattr(device, 'hsv'):
                capabilities.append("color")
            if hasattr(device, 'emeter'):
                capabilities.append("energy_monitoring")
                
        except Exception as e:
            logger.warning(f"Capability detection failed: {e}")
        
        return capabilities
    
    def _create_persian_device_name(self, device_name: str, device_type: str) -> str:
        """Create Persian name for device"""
        # Simple Persian naming based on device type and location
        type_persian = {
            "light": "چراغ",
            "outlet": "پریز", 
            "switch": "کلید",
            "power_strip": "چندراهی"
        }.get(device_type, "دستگاه")
        
        # Extract location from device name if possible
        location_mappings = {
            "living": "نشیمن",
            "bedroom": "اتاق خواب",
            "kitchen": "آشپزخانه",
            "bathroom": "حمام",
            "office": "دفتر",
            "hall": "راهرو"
        }
        
        device_lower = device_name.lower()
        location_persian = ""
        
        for eng, persian in location_mappings.items():
            if eng in device_lower:
                location_persian = persian
                break
        
        if location_persian:
            return f"{type_persian} {location_persian}"
        else:
            return f"{type_persian} {device_name}"
    
    async def control_device_by_persian_command(self, persian_command: str) -> str:
        """
        Control devices using Persian voice commands
        
        Args:
            persian_command: Persian command like "چراغ نشیمن را روشن کن"
            
        Returns:
            Persian response message
        """
        start_time = time.time()
        
        try:
            self.control_stats["total_commands"] += 1
            
            # Parse Persian command
            parsed_command = self._parse_persian_command(persian_command)
            
            if not parsed_command["device"] or not parsed_command["action"]:
                return "متوجه دستور نشدم. لطفاً واضح‌تر بگویید."
            
            # Find matching device
            target_device = self._find_device_by_persian_name(parsed_command["device"])
            
            if not target_device:
                return f"دستگاه '{parsed_command['device']}' پیدا نشد."
            
            # Execute command
            result = await self._execute_device_command(
                target_device, 
                parsed_command["action"],
                parsed_command.get("value")
            )
            
            # Update performance stats
            response_time = time.time() - start_time
            self._update_control_stats(target_device, response_time, True)
            
            return result
            
        except Exception as e:
            logger.error(f"Device control failed: {e}")
            self.control_stats["error_count"] += 1
            return f"خطا در کنترل دستگاه: {str(e)}"
    
    def _parse_persian_command(self, command: str) -> Dict[str, Any]:
        """Parse Persian command to extract device, action, and value"""
        command_lower = command.lower()
        
        parsed = {
            "device": "",
            "action": "",
            "value": None,
            "original": command
        }
        
        # Find device type
        device_keywords = {
            "چراغ": "light",
            "لامپ": "light", 
            "نور": "light",
            "پریز": "outlet",
            "برق": "outlet",
            "کلید": "switch",
            "چندراهی": "power_strip"
        }
        
        for persian_word, device_type in device_keywords.items():
            if persian_word in command_lower:
                parsed["device"] = persian_word
                break
        
        # Find action
        action_keywords = {
            "روشن": "turn_on",
            "باز": "turn_on",
            "فعال": "turn_on",
            "خاموش": "turn_off",
            "بسته": "turn_off",
            "غیرفعال": "turn_off",
            "کم": "dim",
            "زیاد": "brighten",
            "بیشتر": "brighten",
            "کمتر": "dim"
        }
        
        for persian_word, action in action_keywords.items():
            if persian_word in command_lower:
                parsed["action"] = action
                break
        
        # Extract location/room if present
        location_keywords = {
            "نشیمن": "living",
            "اتاق خواب": "bedroom", 
            "آشپزخانه": "kitchen",
            "حمام": "bathroom",
            "دفتر": "office",
            "راهرو": "hall"
        }
        
        for persian_location, eng_location in location_keywords.items():
            if persian_location in command_lower:
                parsed["location"] = persian_location
                break
        
        return parsed
    
    def _find_device_by_persian_name(self, persian_device: str) -> Optional[str]:
        """Find device by Persian name or type"""
        # Direct Persian name match
        if persian_device in self.persian_device_names:
            return self.persian_device_names[persian_device]
        
        # Fuzzy match by device type
        device_type_map = {
            "چراغ": "light",
            "لامپ": "light",
            "پریز": "outlet",
            "کلید": "switch"
        }
        
        target_type = device_type_map.get(persian_device)
        if target_type:
            # Find first device of this type
            for device_name, device_info in self.devices.items():
                if device_info["type"] == target_type:
                    return device_name
        
        # Partial name match
        for device_name in self.devices.keys():
            if persian_device in device_name.lower():
                return device_name
        
        return None
    
    async def _execute_device_command(self, device_name: str, action: str, value: Any = None) -> str:
        """Execute command on specific device"""
        try:
            device_info = self.devices.get(device_name)
            if not device_info:
                return f"دستگاه {device_name} پیدا نشد."
            
            device = device_info["device"]
            protocol = device_info["protocol"]
            
            if protocol == "kasa":
                return await self._execute_kasa_command(device, action, value)
            elif protocol == "hue":
                return await self._execute_hue_command(device, action, value)
            else:
                return f"پروتکل {protocol} پشتیبانی نمی‌شود."
                
        except Exception as e:
            logger.error(f"Device command execution failed: {e}")
            return f"خطا در اجرای دستور: {str(e)}"
    
    async def _execute_kasa_command(self, device, action: str, value: Any = None) -> str:
        """Execute command on Kasa device"""
        try:
            if action == "turn_on":
                await device.turn_on()
                return f"{device.alias} روشن شد."
            
            elif action == "turn_off":
                await device.turn_off()
                return f"{device.alias} خاموش شد."
            
            elif action == "brighten" and hasattr(device, 'brightness'):
                current_brightness = device.brightness
                new_brightness = min(100, current_brightness + 20)
                await device.set_brightness(new_brightness)
                return f"روشنایی {device.alias} افزایش یافت."
            
            elif action == "dim" and hasattr(device, 'brightness'):
                current_brightness = device.brightness
                new_brightness = max(1, current_brightness - 20)
                await device.set_brightness(new_brightness)
                return f"روشنایی {device.alias} کاهش یافت."
            
            else:
                return f"دستور {action} برای {device.alias} پشتیبانی نمی‌شود."
                
        except Exception as e:
            logger.error(f"Kasa command execution failed: {e}")
            return f"خطا در کنترل {device.alias}: {str(e)}"
    
    async def _execute_hue_command(self, device, action: str, value: Any = None) -> str:
        """Execute command on Hue device"""
        try:
            if action == "turn_on":
                device.on = True
                return f"{device.name} روشن شد."
            
            elif action == "turn_off":
                device.on = False
                return f"{device.name} خاموش شد."
            
            elif action == "brighten":
                current_brightness = device.brightness
                new_brightness = min(254, current_brightness + 50)
                device.brightness = new_brightness
                return f"روشنایی {device.name} افزایش یافت."
            
            elif action == "dim":
                current_brightness = device.brightness
                new_brightness = max(1, current_brightness - 50)
                device.brightness = new_brightness
                return f"روشنایی {device.name} کاهش یافت."
            
            else:
                return f"دستور {action} برای {device.name} پشتیبانی نمی‌شود."
                
        except Exception as e:
            logger.error(f"Hue command execution failed: {e}")
            return f"خطا در کنترل {device.name}: {str(e)}"
    
    def _update_control_stats(self, device_name: str, response_time: float, success: bool):
        """Update control performance statistics"""
        if success:
            self.control_stats["successful_commands"] += 1
        
        # Update device response times
        if device_name not in self.control_stats["device_response_times"]:
            self.control_stats["device_response_times"][device_name] = []
        
        self.control_stats["device_response_times"][device_name].append(response_time)
        
        # Keep only recent response times
        if len(self.control_stats["device_response_times"][device_name]) > 10:
            self.control_stats["device_response_times"][device_name] = \
                self.control_stats["device_response_times"][device_name][-10:]
    
    async def get_device_status(self, device_name: str = None) -> Dict[str, Any]:
        """Get status of devices"""
        try:
            if device_name:
                # Get specific device status
                device_info = self.devices.get(device_name)
                if not device_info:
                    return {"error": f"دستگاه {device_name} پیدا نشد"}
                
                device = device_info["device"]
                protocol = device_info["protocol"]
                
                if protocol == "kasa":
                    await device.update()
                    return {
                        "name": device.alias,
                        "type": device_info["type"],
                        "is_on": device.is_on,
                        "brightness": getattr(device, 'brightness', None),
                        "protocol": protocol
                    }
                elif protocol == "hue":
                    return {
                        "name": device.name,
                        "type": device_info["type"],
                        "is_on": device.on,
                        "brightness": getattr(device, 'brightness', None),
                        "protocol": protocol
                    }
            else:
                # Get all devices status
                all_status = {}
                for name, info in self.devices.items():
                    device_status = await self.get_device_status(name)
                    all_status[name] = device_status
                
                return all_status
                
        except Exception as e:
            logger.error(f"Device status retrieval failed: {e}")
            return {"error": str(e)}
    
    def get_available_devices(self) -> Dict[str, Any]:
        """Get list of available devices with Persian names"""
        devices_list = {}
        
        for device_name, device_info in self.devices.items():
            # Find Persian name
            persian_name = None
            for p_name, eng_name in self.persian_device_names.items():
                if eng_name == device_name:
                    persian_name = p_name
                    break
            
            devices_list[device_name] = {
                "persian_name": persian_name or device_name,
                "type": device_info["type"],
                "protocol": device_info["protocol"],
                "capabilities": device_info["capabilities"]
            }
        
        return devices_list
    
    def get_control_stats(self) -> Dict[str, Any]:
        """Get smart home control statistics"""
        stats = self.control_stats.copy()
        
        # Calculate success rate
        if stats["total_commands"] > 0:
            stats["success_rate"] = stats["successful_commands"] / stats["total_commands"]
        else:
            stats["success_rate"] = 0.0
        
        # Calculate average response times
        avg_response_times = {}
        for device, times in stats["device_response_times"].items():
            if times:
                avg_response_times[device] = sum(times) / len(times)
        
        stats["average_response_times"] = avg_response_times
        
        return {
            "controller_status": {
                "kasa_available": self.kasa_available,
                "hue_available": self.hue_available,
                "mqtt_available": self.mqtt_available
            },
            "device_count": len(self.devices),
            "performance_stats": stats
        }
    
    async def cleanup(self):
        """Clean up smart home controller resources"""
        try:
            # Close any persistent connections
            self.devices.clear()
            self.device_types.clear()
            self.persian_device_names.clear()
            
            logger.info("Smart home controller cleanup completed")
            
        except Exception as e:
            logger.error(f"Smart home cleanup error: {e}")
    
    def get_all_devices(self) -> Dict[str, Any]:
        """Get all discovered devices with their status"""
        try:
            devices_status = {}
            
            for device_name, device_info in self.devices.items():
                # Find Persian name
                persian_name = None
                for p_name, eng_name in self.persian_device_names.items():
                    if eng_name == device_name:
                        persian_name = p_name
                        break
                
                # Get device status
                device_status = "unknown"
                try:
                    if device_info["protocol"] == "kasa":
                        device = device_info["device"]
                        device_status = "on" if device.is_on else "off"
                    elif device_info["protocol"] == "hue":
                        device = device_info["device"]
                        device_status = "on" if device.on else "off"
                except:
                    device_status = "unknown"
                
                devices_status[device_name] = {
                    "persian_name": persian_name or device_name,
                    "type": device_info["type"],
                    "status": device_status,
                    "protocol": device_info["protocol"],
                    "capabilities": device_info["capabilities"]
                }
            
            return devices_status
            
        except Exception as e:
            logger.error(f"Get all devices failed: {e}")
            return {}
    
    async def execute_persian_command(self, persian_command: str) -> Dict[str, Any]:
        """Execute Persian command and return structured result"""
        try:
            result = await self.control_device_by_persian_command(persian_command)
            
            return {
                'success': True,
                'response': result,
                'command': persian_command
            }
            
        except Exception as e:
            logger.error(f"Persian command execution failed: {e}")
            return {
                'success': False,
                'response': f'خطا در اجرای دستور: {str(e)}',
                'command': persian_command
            }
    
    def get_all_devices(self) -> Dict[str, Any]:
        """Get all discovered devices with their status"""
        try:
            devices_status = {}
            
            for device_name, device_info in self.devices.items():
                # Find Persian name
                persian_name = None
                for p_name, eng_name in self.persian_device_names.items():
                    if eng_name == device_name:
                        persian_name = p_name
                        break
                
                # Get device status
                device_status = "unknown"
                try:
                    if device_info["protocol"] == "kasa":
                        device = device_info["device"]
                        device_status = "on" if device.is_on else "off"
                    elif device_info["protocol"] == "hue":
                        device = device_info["device"]
                        device_status = "on" if device.on else "off"
                except:
                    device_status = "unknown"
                
                devices_status[device_name] = {
                    "persian_name": persian_name or device_name,
                    "type": device_info["type"],
                    "status": device_status,
                    "protocol": device_info["protocol"],
                    "capabilities": device_info["capabilities"]
                }
            
            return devices_status
            
        except Exception as e:
            logger.error(f"Get all devices failed: {e}")
            return {}
    
    async def execute_persian_command(self, persian_command: str) -> Dict[str, Any]:
        """Execute Persian command and return structured result"""
        try:
            result = await self.control_device_by_persian_command(persian_command)
            
            return {
                'success': True,
                'response': result,
                'command': persian_command
            }
            
        except Exception as e:
            logger.error(f"Persian command execution failed: {e}")
            return {
                'success': False,
                'response': f'خطا در اجرای دستور: {str(e)}',
                'command': persian_command
            }