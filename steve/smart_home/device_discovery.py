"""
Smart Home Device Discovery
Automatic discovery and configuration of smart home devices
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set
import socket
import json
import time
from dataclasses import dataclass
import ipaddress
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class DiscoveredDevice:
    """Represents a discovered smart home device"""
    name: str
    ip_address: str
    mac_address: str
    device_type: str
    protocol: str
    manufacturer: str
    model: str
    capabilities: List[str]
    persian_name: str
    discovery_method: str
    confidence: float

class SmartHomeDeviceDiscovery:
    """
    Advanced smart home device discovery system
    Supports multiple protocols and automatic device identification
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.discovered_devices: Dict[str, DiscoveredDevice] = {}
        self.discovery_methods = []
        
        # Network configuration
        self.network_range = self.config.get("network_range", "192.168.1.0/24")
        self.discovery_timeout = self.config.get("discovery_timeout", 30)
        
        # Device signatures for identification
        self.device_signatures = self._load_device_signatures()
        
        # Discovery statistics
        self.discovery_stats = {
            "total_scans": 0,
            "devices_found": 0,
            "discovery_time": 0.0,
            "methods_used": []
        }
        
        # Initialize discovery methods
        self._initialize_discovery_methods()
    
    def _initialize_discovery_methods(self):
        """Initialize available discovery methods"""
        self.discovery_methods = [
            ("kasa_discovery", self._discover_kasa_devices),
            ("hue_discovery", self._discover_hue_devices),
            ("upnp_discovery", self._discover_upnp_devices),
            ("mdns_discovery", self._discover_mdns_devices),
            ("network_scan", self._discover_via_network_scan)
        ]
        
        logger.info(f"Initialized {len(self.discovery_methods)} discovery methods")
    
    def _load_device_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Load device signatures for identification"""
        return {
            "kasa": {
                "ports": [9999],
                "protocols": ["tcp"],
                "identification": {
                    "method": "json_query",
                    "query": '{"system":{"get_sysinfo":{}}}',
                    "response_contains": ["alias", "model"]
                },
                "device_types": {
                    "KL": "light_bulb",
                    "HS": "smart_plug", 
                    "KP": "smart_plug",
                    "EP": "smart_plug"
                }
            },
            "hue": {
                "ports": [80, 443],
                "protocols": ["http"],
                "identification": {
                    "method": "http_get",
                    "path": "/api/config",
                    "response_contains": ["bridgeid", "name"]
                },
                "device_types": {
                    "bridge": "hue_bridge"
                }
            },
            "shelly": {
                "ports": [80],
                "protocols": ["http"],
                "identification": {
                    "method": "http_get", 
                    "path": "/shelly",
                    "response_contains": ["type", "mac"]
                },
                "device_types": {
                    "SHSW": "switch",
                    "SHDM": "dimmer"
                }
            }
        }
    
    async def discover_all_devices(self, force_rescan: bool = False) -> Dict[str, DiscoveredDevice]:
        """
        Discover all smart home devices on the network
        
        Args:
            force_rescan: Force a complete rescan even if devices are cached
            
        Returns:
            Dictionary of discovered devices
        """
        start_time = time.time()
        
        try:
            logger.info("Starting comprehensive device discovery...")
            self.discovery_stats["total_scans"] += 1
            
            if not force_rescan and self.discovered_devices:
                logger.info(f"Using cached devices: {len(self.discovered_devices)} found")
                return self.discovered_devices
            
            # Clear previous discoveries if force rescan
            if force_rescan:
                self.discovered_devices.clear()
            
            # Run all discovery methods in parallel
            discovery_tasks = []
            for method_name, method_func in self.discovery_methods:
                task = asyncio.create_task(self._run_discovery_method(method_name, method_func))
                discovery_tasks.append(task)
            
            # Wait for all discovery methods to complete
            results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                method_name = self.discovery_methods[i][0]
                if isinstance(result, Exception):
                    logger.warning(f"Discovery method {method_name} failed: {result}")
                else:
                    logger.info(f"Discovery method {method_name} completed successfully")
            
            # Update statistics
            discovery_time = time.time() - start_time
            self.discovery_stats["discovery_time"] = discovery_time
            self.discovery_stats["devices_found"] = len(self.discovered_devices)
            
            logger.info(f"Device discovery completed in {discovery_time:.2f}s. Found {len(self.discovered_devices)} devices.")
            
            return self.discovered_devices
            
        except Exception as e:
            logger.error(f"Device discovery failed: {e}")
            return self.discovered_devices
    
    async def _run_discovery_method(self, method_name: str, method_func):
        """Run a single discovery method with error handling"""
        try:
            logger.info(f"Running discovery method: {method_name}")
            await method_func()
            self.discovery_stats["methods_used"].append(method_name)
        except Exception as e:
            logger.error(f"Discovery method {method_name} failed: {e}")
            raise
    
    async def _discover_kasa_devices(self):
        """Discover TP-Link Kasa devices"""
        try:
            from kasa import Discover
            
            logger.info("Discovering Kasa devices...")
            devices = await Discover.discover(timeout=10)
            
            for addr, dev in devices.items():
                try:
                    await dev.update()
                    
                    # Determine device type
                    device_type = self._classify_kasa_device(dev)
                    
                    # Create Persian name
                    persian_name = self._generate_persian_name(dev.alias, device_type)
                    
                    # Get capabilities
                    capabilities = self._get_kasa_capabilities(dev)
                    
                    discovered_device = DiscoveredDevice(
                        name=dev.alias,
                        ip_address=addr,
                        mac_address=dev.mac,
                        device_type=device_type,
                        protocol="kasa",
                        manufacturer="TP-Link",
                        model=dev.model,
                        capabilities=capabilities,
                        persian_name=persian_name,
                        discovery_method="kasa_discovery",
                        confidence=0.95
                    )
                    
                    self.discovered_devices[f"kasa_{dev.mac}"] = discovered_device
                    logger.info(f"Discovered Kasa device: {dev.alias} at {addr}")
                    
                except Exception as e:
                    logger.warning(f"Failed to process Kasa device at {addr}: {e}")
            
        except ImportError:
            logger.warning("python-kasa not available for Kasa discovery")
        except Exception as e:
            logger.error(f"Kasa discovery failed: {e}")
    
    async def _discover_hue_devices(self):
        """Discover Philips Hue devices"""
        try:
            # First discover Hue bridge
            bridge_ip = await self._discover_hue_bridge()
            
            if bridge_ip:
                from phue import Bridge
                
                try:
                    bridge = Bridge(bridge_ip)
                    bridge.connect()
                    
                    # Add bridge as a device
                    bridge_device = DiscoveredDevice(
                        name="Hue Bridge",
                        ip_address=bridge_ip,
                        mac_address="",  # Would need to get from bridge
                        device_type="hub",
                        protocol="hue",
                        manufacturer="Philips",
                        model="Hue Bridge",
                        capabilities=["device_management", "lighting_control"],
                        persian_name="پل هوشمند فیلیپس",
                        discovery_method="hue_discovery",
                        confidence=0.95
                    )
                    
                    self.discovered_devices[f"hue_bridge_{bridge_ip}"] = bridge_device
                    
                    # Discover connected lights
                    lights = bridge.lights
                    
                    for light in lights:
                        persian_name = self._generate_persian_name(light.name, "light")
                        
                        light_device = DiscoveredDevice(
                            name=light.name,
                            ip_address=bridge_ip,  # Lights connect through bridge
                            mac_address="",
                            device_type="light",
                            protocol="hue",
                            manufacturer="Philips",
                            model="Hue Light",
                            capabilities=["on_off", "brightness", "color"],
                            persian_name=persian_name,
                            discovery_method="hue_discovery",
                            confidence=0.90
                        )
                        
                        self.discovered_devices[f"hue_light_{light.light_id}"] = light_device
                        logger.info(f"Discovered Hue light: {light.name}")
                    
                except Exception as e:
                    logger.warning(f"Hue bridge connection failed: {e}")
            
        except ImportError:
            logger.warning("phue not available for Hue discovery")
        except Exception as e:
            logger.error(f"Hue discovery failed: {e}")
    
    async def _discover_hue_bridge(self) -> Optional[str]:
        """Discover Hue bridge IP address"""
        try:
            import requests
            
            # Try Philips discovery service
            response = requests.get("https://discovery.meethue.com/", timeout=5)
            if response.status_code == 200:
                bridges = response.json()
                if bridges:
                    return bridges[0]["internalipaddress"]
            
            # Fallback: scan local network for Hue bridge
            return await self._scan_for_hue_bridge()
            
        except Exception as e:
            logger.warning(f"Hue bridge discovery failed: {e}")
            return None
    
    async def _scan_for_hue_bridge(self) -> Optional[str]:
        """Scan local network for Hue bridge"""
        try:
            network = ipaddress.IPv4Network(self.network_range, strict=False)
            
            for ip in network.hosts():
                try:
                    # Check if device responds to Hue API
                    import requests
                    response = requests.get(f"http://{ip}/api/config", timeout=2)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "bridgeid" in data and "name" in data:
                            logger.info(f"Found Hue bridge at {ip}")
                            return str(ip)
                            
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Hue bridge network scan failed: {e}")
            return None
    
    async def _discover_upnp_devices(self):
        """Discover devices using UPnP/SSDP"""
        try:
            import socket
            
            # SSDP multicast message
            ssdp_request = (
                "M-SEARCH * HTTP/1.1\r\n"
                "HOST: 239.255.255.250:1900\r\n"
                "MAN: \"ssdp:discover\"\r\n"
                "ST: upnp:rootdevice\r\n"
                "MX: 3\r\n\r\n"
            )
            
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # Send SSDP request
            sock.sendto(ssdp_request.encode(), ("239.255.255.250", 1900))
            
            # Collect responses
            responses = []
            try:
                while True:
                    data, addr = sock.recvfrom(1024)
                    responses.append((data.decode(), addr[0]))
            except socket.timeout:
                pass
            finally:
                sock.close()
            
            # Process UPnP responses
            for response, ip in responses:
                device_info = self._parse_upnp_response(response, ip)
                if device_info:
                    self.discovered_devices[f"upnp_{ip}"] = device_info
                    logger.info(f"Discovered UPnP device at {ip}")
            
        except Exception as e:
            logger.error(f"UPnP discovery failed: {e}")
    
    def _parse_upnp_response(self, response: str, ip: str) -> Optional[DiscoveredDevice]:
        """Parse UPnP SSDP response"""
        try:
            lines = response.split('\r\n')
            headers = {}
            
            for line in lines[1:]:  # Skip first line (HTTP status)
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().upper()] = value.strip()
            
            # Extract device information
            server = headers.get('SERVER', '')
            location = headers.get('LOCATION', '')
            
            # Try to identify device type from server string
            device_type = "unknown"
            manufacturer = "Unknown"
            
            if "kasa" in server.lower() or "tplink" in server.lower():
                device_type = "smart_plug"
                manufacturer = "TP-Link"
            elif "hue" in server.lower() or "philips" in server.lower():
                device_type = "hub"
                manufacturer = "Philips"
            
            persian_name = self._generate_persian_name(f"Device_{ip}", device_type)
            
            return DiscoveredDevice(
                name=f"UPnP Device {ip}",
                ip_address=ip,
                mac_address="",
                device_type=device_type,
                protocol="upnp",
                manufacturer=manufacturer,
                model="",
                capabilities=["upnp"],
                persian_name=persian_name,
                discovery_method="upnp_discovery",
                confidence=0.6
            )
            
        except Exception as e:
            logger.warning(f"UPnP response parsing failed: {e}")
            return None
    
    async def _discover_mdns_devices(self):
        """Discover devices using mDNS/Bonjour"""
        try:
            # This would require python-zeroconf
            # For now, we'll use a simple implementation
            logger.info("mDNS discovery not fully implemented yet")
            
            # Placeholder for mDNS discovery
            # In a full implementation, you would:
            # 1. Use zeroconf library to browse for services
            # 2. Look for _hap._tcp, _googlecast._tcp, etc.
            # 3. Parse service information
            # 4. Add discovered devices
            
        except Exception as e:
            logger.error(f"mDNS discovery failed: {e}")
    
    async def _discover_via_network_scan(self):
        """Discover devices via network port scanning"""
        try:
            logger.info("Starting network scan for smart home devices...")
            
            network = ipaddress.IPv4Network(self.network_range, strict=False)
            scan_tasks = []
            
            # Limit concurrent scans to avoid overwhelming the network
            semaphore = asyncio.Semaphore(20)
            
            for ip in list(network.hosts())[:50]:  # Limit to first 50 IPs for demo
                task = asyncio.create_task(self._scan_ip_for_devices(str(ip), semaphore))
                scan_tasks.append(task)
            
            # Wait for all scans to complete
            await asyncio.gather(*scan_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Network scan failed: {e}")
    
    async def _scan_ip_for_devices(self, ip: str, semaphore: asyncio.Semaphore):
        """Scan a single IP for smart home devices"""
        async with semaphore:
            try:
                # Check common smart home ports
                common_ports = [80, 443, 9999, 8080, 8443]
                
                for port in common_ports:
                    if await self._check_port(ip, port):
                        # Try to identify device
                        device_info = await self._identify_device(ip, port)
                        if device_info:
                            self.discovered_devices[f"scan_{ip}_{port}"] = device_info
                            logger.info(f"Discovered device via scan: {ip}:{port}")
                            break
                
            except Exception as e:
                logger.debug(f"Scan failed for {ip}: {e}")
    
    async def _check_port(self, ip: str, port: int, timeout: float = 2.0) -> bool:
        """Check if a port is open on an IP address"""
        try:
            future = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(future, timeout=timeout)
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False
    
    async def _identify_device(self, ip: str, port: int) -> Optional[DiscoveredDevice]:
        """Try to identify device type by probing"""
        try:
            # Try Kasa identification
            if port == 9999:
                device_info = await self._identify_kasa_device(ip, port)
                if device_info:
                    return device_info
            
            # Try HTTP-based identification
            if port in [80, 443, 8080, 8443]:
                device_info = await self._identify_http_device(ip, port)
                if device_info:
                    return device_info
            
            return None
            
        except Exception as e:
            logger.debug(f"Device identification failed for {ip}:{port}: {e}")
            return None
    
    async def _identify_kasa_device(self, ip: str, port: int) -> Optional[DiscoveredDevice]:
        """Identify Kasa device by querying system info"""
        try:
            import socket
            import json
            
            # Kasa protocol query
            query = '{"system":{"get_sysinfo":{}}}'
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((ip, port))
            
            # Send query (Kasa uses a simple encryption)
            encrypted_query = self._kasa_encrypt(query)
            sock.send(encrypted_query)
            
            # Receive response
            response = sock.recv(4096)
            sock.close()
            
            # Decrypt response
            decrypted = self._kasa_decrypt(response[4:])  # Skip length header
            data = json.loads(decrypted)
            
            if "system" in data and "get_sysinfo" in data["system"]:
                sysinfo = data["system"]["get_sysinfo"]
                
                device_type = self._classify_kasa_device_by_model(sysinfo.get("model", ""))
                persian_name = self._generate_persian_name(sysinfo.get("alias", "Kasa Device"), device_type)
                
                return DiscoveredDevice(
                    name=sysinfo.get("alias", "Kasa Device"),
                    ip_address=ip,
                    mac_address=sysinfo.get("mac", ""),
                    device_type=device_type,
                    protocol="kasa",
                    manufacturer="TP-Link",
                    model=sysinfo.get("model", ""),
                    capabilities=["on_off"],
                    persian_name=persian_name,
                    discovery_method="network_scan",
                    confidence=0.85
                )
            
            return None
            
        except Exception as e:
            logger.debug(f"Kasa identification failed for {ip}: {e}")
            return None
    
    def _kasa_encrypt(self, plaintext: str) -> bytes:
        """Encrypt data for Kasa protocol"""
        key = 171
        result = bytearray()
        result.extend(len(plaintext).to_bytes(4, byteorder='big'))
        
        for char in plaintext:
            a = key ^ ord(char)
            key = a
            result.append(a)
        
        return bytes(result)
    
    def _kasa_decrypt(self, ciphertext: bytes) -> str:
        """Decrypt data from Kasa protocol"""
        key = 171
        result = ""
        
        for byte in ciphertext:
            a = key ^ byte
            key = byte
            result += chr(a)
        
        return result
    
    async def _identify_http_device(self, ip: str, port: int) -> Optional[DiscoveredDevice]:
        """Identify device via HTTP probing"""
        try:
            import aiohttp
            
            protocol = "https" if port in [443, 8443] else "http"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                # Try common smart home endpoints
                endpoints = ["/", "/api/config", "/shelly", "/status"]
                
                for endpoint in endpoints:
                    try:
                        url = f"{protocol}://{ip}:{port}{endpoint}"
                        async with session.get(url, ssl=False) as response:
                            if response.status == 200:
                                text = await response.text()
                                
                                # Check for device signatures
                                if "bridgeid" in text and "hue" in text.lower():
                                    return self._create_hue_bridge_device(ip)
                                elif "shelly" in text.lower():
                                    return self._create_shelly_device(ip, text)
                                
                    except:
                        continue
            
            return None
            
        except Exception as e:
            logger.debug(f"HTTP identification failed for {ip}: {e}")
            return None
    
    def _create_hue_bridge_device(self, ip: str) -> DiscoveredDevice:
        """Create Hue bridge device info"""
        return DiscoveredDevice(
            name="Hue Bridge",
            ip_address=ip,
            mac_address="",
            device_type="hub",
            protocol="hue",
            manufacturer="Philips",
            model="Hue Bridge",
            capabilities=["device_management", "lighting_control"],
            persian_name="پل هوشمند فیلیپس",
            discovery_method="network_scan",
            confidence=0.80
        )
    
    def _create_shelly_device(self, ip: str, response_text: str) -> DiscoveredDevice:
        """Create Shelly device info"""
        device_type = "switch"  # Default for Shelly devices
        
        return DiscoveredDevice(
            name=f"Shelly Device {ip}",
            ip_address=ip,
            mac_address="",
            device_type=device_type,
            protocol="shelly",
            manufacturer="Shelly",
            model="Shelly Device",
            capabilities=["on_off", "http_control"],
            persian_name=self._generate_persian_name(f"Shelly {ip}", device_type),
            discovery_method="network_scan",
            confidence=0.75
        )
    
    def _classify_kasa_device(self, device) -> str:
        """Classify Kasa device type"""
        try:
            device_type = str(type(device).__name__).lower()
            model = getattr(device, 'model', '').upper()
            
            return self._classify_kasa_device_by_model(model)
            
        except Exception as e:
            logger.warning(f"Kasa device classification failed: {e}")
            return "unknown"
    
    def _classify_kasa_device_by_model(self, model: str) -> str:
        """Classify Kasa device by model string"""
        model_upper = model.upper()
        
        if model_upper.startswith(('KL', 'LB')):
            return "light"
        elif model_upper.startswith(('HS', 'KP', 'EP')):
            return "outlet"
        elif model_upper.startswith('KS'):
            return "switch"
        else:
            return "unknown"
    
    def _get_kasa_capabilities(self, device) -> List[str]:
        """Get Kasa device capabilities"""
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
    
    def _generate_persian_name(self, device_name: str, device_type: str) -> str:
        """Generate Persian name for device"""
        type_persian = {
            "light": "چراغ",
            "outlet": "پریز",
            "switch": "کلید", 
            "hub": "پل",
            "unknown": "دستگاه"
        }.get(device_type, "دستگاه")
        
        # Extract location from device name
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
    
    def get_discovered_devices_summary(self) -> Dict[str, Any]:
        """Get summary of discovered devices"""
        summary = {
            "total_devices": len(self.discovered_devices),
            "by_protocol": {},
            "by_type": {},
            "by_manufacturer": {},
            "discovery_stats": self.discovery_stats
        }
        
        for device in self.discovered_devices.values():
            # Count by protocol
            protocol = device.protocol
            summary["by_protocol"][protocol] = summary["by_protocol"].get(protocol, 0) + 1
            
            # Count by type
            device_type = device.device_type
            summary["by_type"][device_type] = summary["by_type"].get(device_type, 0) + 1
            
            # Count by manufacturer
            manufacturer = device.manufacturer
            summary["by_manufacturer"][manufacturer] = summary["by_manufacturer"].get(manufacturer, 0) + 1
        
        return summary
    
    def get_devices_for_controller(self) -> List[Dict[str, Any]]:
        """Get devices formatted for smart home controller"""
        controller_devices = []
        
        for device_id, device in self.discovered_devices.items():
            controller_device = {
                "id": device_id,
                "name": device.name,
                "persian_name": device.persian_name,
                "ip_address": device.ip_address,
                "device_type": device.device_type,
                "protocol": device.protocol,
                "manufacturer": device.manufacturer,
                "model": device.model,
                "capabilities": device.capabilities,
                "confidence": device.confidence
            }
            
            controller_devices.append(controller_device)
        
        return controller_devices
    
    async def cleanup(self):
        """Clean up discovery resources"""
        try:
            self.discovered_devices.clear()
            logger.info("Device discovery cleanup completed")
            
        except Exception as e:
            logger.error(f"Discovery cleanup error: {e}")