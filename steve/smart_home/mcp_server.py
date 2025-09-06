"""
MCP (Model Context Protocol) Server Implementation
Provides structured interface for LLM integration with smart home devices
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
import time
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """Represents an MCP tool/function"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable

@dataclass
class MCPResource:
    """Represents an MCP resource"""
    uri: str
    name: str
    description: str
    mime_type: str
    content: Any

class SteveMCPServer:
    """
    MCP Server for Steve Voice Assistant
    Provides structured interface for LLM to interact with smart home devices
    """
    
    def __init__(self, smart_home_controller, device_discovery=None):
        self.smart_home_controller = smart_home_controller
        self.device_discovery = device_discovery
        
        # MCP server state
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.server_info = {
            "name": "steve-smart-home-mcp",
            "version": "1.0.0",
            "description": "MCP server for Steve Persian voice assistant smart home control"
        }
        
        # Performance tracking
        self.mcp_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "tool_usage": {},
            "resource_access": {},
            "average_response_time": 0.0
        }
        
        # Initialize MCP tools and resources
        self._initialize_mcp_tools()
        self._initialize_mcp_resources()
    
    def _initialize_mcp_tools(self):
        """Initialize MCP tools for smart home control"""
        try:
            # Device control tool
            self.tools["control_device"] = MCPTool(
                name="control_device",
                description="Control smart home devices using Persian commands",
                parameters={
                    "type": "object",
                    "properties": {
                        "persian_command": {
                            "type": "string",
                            "description": "Persian command to control device (e.g., 'چراغ نشیمن را روشن کن')"
                        },
                        "device_name": {
                            "type": "string",
                            "description": "Optional specific device name"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["turn_on", "turn_off", "brighten", "dim"],
                            "description": "Action to perform on device"
                        }
                    },
                    "required": ["persian_command"]
                },
                handler=self._handle_control_device
            )
            
            # Device status tool
            self.tools["get_device_status"] = MCPTool(
                name="get_device_status",
                description="Get current status of smart home devices",
                parameters={
                    "type": "object",
                    "properties": {
                        "device_name": {
                            "type": "string",
                            "description": "Specific device name, or 'all' for all devices"
                        }
                    },
                    "required": []
                },
                handler=self._handle_get_device_status
            )
            
            # Device discovery tool
            self.tools["discover_devices"] = MCPTool(
                name="discover_devices",
                description="Discover new smart home devices on the network",
                parameters={
                    "type": "object",
                    "properties": {
                        "force_rescan": {
                            "type": "boolean",
                            "description": "Force a complete rescan of the network",
                            "default": False
                        }
                    },
                    "required": []
                },
                handler=self._handle_discover_devices
            )
            
            # List available devices tool
            self.tools["list_devices"] = MCPTool(
                name="list_devices",
                description="List all available smart home devices with Persian names",
                parameters={
                    "type": "object",
                    "properties": {
                        "device_type": {
                            "type": "string",
                            "enum": ["light", "outlet", "switch", "hub", "all"],
                            "description": "Filter by device type",
                            "default": "all"
                        }
                    },
                    "required": []
                },
                handler=self._handle_list_devices
            )
            
            # Persian command help tool
            self.tools["persian_command_help"] = MCPTool(
                name="persian_command_help",
                description="Get help with Persian voice commands for smart home control",
                parameters={
                    "type": "object",
                    "properties": {
                        "command_type": {
                            "type": "string",
                            "enum": ["device_control", "examples", "all"],
                            "description": "Type of help needed",
                            "default": "all"
                        }
                    },
                    "required": []
                },
                handler=self._handle_persian_command_help
            )
            
            logger.info(f"Initialized {len(self.tools)} MCP tools")
            
        except Exception as e:
            logger.error(f"MCP tools initialization failed: {e}")
    
    def _initialize_mcp_resources(self):
        """Initialize MCP resources"""
        try:
            # Device list resource
            self.resources["devices"] = MCPResource(
                uri="steve://devices",
                name="Smart Home Devices",
                description="List of all discovered smart home devices",
                mime_type="application/json",
                content=self._get_devices_resource_content
            )
            
            # Device capabilities resource
            self.resources["capabilities"] = MCPResource(
                uri="steve://capabilities",
                name="Device Capabilities",
                description="Capabilities of all smart home devices",
                mime_type="application/json",
                content=self._get_capabilities_resource_content
            )
            
            # Persian commands resource
            self.resources["persian_commands"] = MCPResource(
                uri="steve://persian_commands",
                name="Persian Voice Commands",
                description="Guide to Persian voice commands for smart home control",
                mime_type="text/markdown",
                content=self._get_persian_commands_resource_content
            )
            
            # System status resource
            self.resources["system_status"] = MCPResource(
                uri="steve://system_status",
                name="System Status",
                description="Current status of Steve voice assistant and smart home system",
                mime_type="application/json",
                content=self._get_system_status_resource_content
            )
            
            logger.info(f"Initialized {len(self.resources)} MCP resources")
            
        except Exception as e:
            logger.error(f"MCP resources initialization failed: {e}")
    
    async def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP request from LLM
        
        Args:
            request: MCP request object
            
        Returns:
            MCP response object
        """
        start_time = time.time()
        
        try:
            self.mcp_stats["total_requests"] += 1
            
            request_type = request.get("method", "")
            
            if request_type == "tools/list":
                response = await self._handle_list_tools()
            elif request_type == "tools/call":
                response = await self._handle_call_tool(request)
            elif request_type == "resources/list":
                response = await self._handle_list_resources()
            elif request_type == "resources/read":
                response = await self._handle_read_resource(request)
            elif request_type == "initialize":
                response = await self._handle_initialize(request)
            else:
                response = {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {request_type}"
                    }
                }
            
            # Update performance stats
            response_time = time.time() - start_time
            self._update_mcp_stats(response_time, "error" not in response)
            
            return response
            
        except Exception as e:
            logger.error(f"MCP request handling failed: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialization"""
        return {
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": self.server_info
            }
        }
    
    async def _handle_list_tools(self) -> Dict[str, Any]:
        """Handle list tools request"""
        tools_list = []
        
        for tool_name, tool in self.tools.items():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.parameters
            })
        
        return {
            "result": {
                "tools": tools_list
            }
        }
    
    async def _handle_call_tool(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request"""
        try:
            params = request.get("params", {})
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            
            if tool_name not in self.tools:
                return {
                    "error": {
                        "code": -32602,
                        "message": f"Tool not found: {tool_name}"
                    }
                }
            
            tool = self.tools[tool_name]
            
            # Update tool usage stats
            if tool_name in self.mcp_stats["tool_usage"]:
                self.mcp_stats["tool_usage"][tool_name] += 1
            else:
                self.mcp_stats["tool_usage"][tool_name] = 1
            
            # Call tool handler
            result = await tool.handler(arguments)
            
            return {
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False, indent=2)
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    async def _handle_list_resources(self) -> Dict[str, Any]:
        """Handle list resources request"""
        resources_list = []
        
        for resource_uri, resource in self.resources.items():
            resources_list.append({
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type
            })
        
        return {
            "result": {
                "resources": resources_list
            }
        }
    
    async def _handle_read_resource(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle read resource request"""
        try:
            params = request.get("params", {})
            uri = params.get("uri", "")
            
            # Find resource by URI
            resource = None
            for res in self.resources.values():
                if res.uri == uri:
                    resource = res
                    break
            
            if not resource:
                return {
                    "error": {
                        "code": -32602,
                        "message": f"Resource not found: {uri}"
                    }
                }
            
            # Update resource access stats
            if uri in self.mcp_stats["resource_access"]:
                self.mcp_stats["resource_access"][uri] += 1
            else:
                self.mcp_stats["resource_access"][uri] = 1
            
            # Get resource content
            if callable(resource.content):
                content = await resource.content()
            else:
                content = resource.content
            
            return {
                "result": {
                    "contents": [
                        {
                            "uri": resource.uri,
                            "mimeType": resource.mime_type,
                            "text": content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, indent=2)
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Resource read failed: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Resource read failed: {str(e)}"
                }
            }
    
    async def _handle_control_device(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle device control tool call"""
        try:
            persian_command = arguments.get("persian_command", "")
            
            if not persian_command:
                return {"error": "Persian command is required"}
            
            if not self.smart_home_controller:
                return {"error": "Smart home controller not available"}
            
            # Execute device control
            result = await self.smart_home_controller.control_device_by_persian_command(persian_command)
            
            return {
                "success": True,
                "command": persian_command,
                "result": result,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Device control failed: {e}")
            return {"error": f"Device control failed: {str(e)}"}
    
    async def _handle_get_device_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get device status tool call"""
        try:
            device_name = arguments.get("device_name", "all")
            
            if not self.smart_home_controller:
                return {"error": "Smart home controller not available"}
            
            # Get device status
            if device_name == "all":
                status = await self.smart_home_controller.get_device_status()
            else:
                status = await self.smart_home_controller.get_device_status(device_name)
            
            return {
                "success": True,
                "device_name": device_name,
                "status": status,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Get device status failed: {e}")
            return {"error": f"Get device status failed: {str(e)}"}
    
    async def _handle_discover_devices(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle device discovery tool call"""
        try:
            force_rescan = arguments.get("force_rescan", False)
            
            if not self.device_discovery:
                return {"error": "Device discovery not available"}
            
            # Discover devices
            discovered = await self.device_discovery.discover_all_devices(force_rescan)
            
            # Convert to serializable format
            devices_info = {}
            for device_id, device in discovered.items():
                devices_info[device_id] = {
                    "name": device.name,
                    "persian_name": device.persian_name,
                    "ip_address": device.ip_address,
                    "device_type": device.device_type,
                    "protocol": device.protocol,
                    "manufacturer": device.manufacturer,
                    "capabilities": device.capabilities,
                    "confidence": device.confidence
                }
            
            return {
                "success": True,
                "devices_found": len(discovered),
                "devices": devices_info,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Device discovery failed: {e}")
            return {"error": f"Device discovery failed: {str(e)}"}
    
    async def _handle_list_devices(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list devices tool call"""
        try:
            device_type_filter = arguments.get("device_type", "all")
            
            if not self.smart_home_controller:
                return {"error": "Smart home controller not available"}
            
            # Get available devices
            devices = self.smart_home_controller.get_available_devices()
            
            # Filter by type if specified
            if device_type_filter != "all":
                filtered_devices = {}
                for name, info in devices.items():
                    if info["type"] == device_type_filter:
                        filtered_devices[name] = info
                devices = filtered_devices
            
            return {
                "success": True,
                "device_type_filter": device_type_filter,
                "device_count": len(devices),
                "devices": devices,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"List devices failed: {e}")
            return {"error": f"List devices failed: {str(e)}"}
    
    async def _handle_persian_command_help(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Persian command help tool call"""
        try:
            command_type = arguments.get("command_type", "all")
            
            help_content = {
                "device_control": {
                    "description": "دستورات کنترل دستگاه‌های خانه هوشمند",
                    "examples": [
                        "چراغ نشیمن را روشن کن",
                        "پریز آشپزخانه را خاموش کن",
                        "چراغ اتاق خواب را کم کن",
                        "نور راهرو را زیاد کن"
                    ],
                    "patterns": {
                        "devices": ["چراغ", "پریز", "کلید", "لامپ"],
                        "actions": ["روشن کن", "خاموش کن", "کم کن", "زیاد کن"],
                        "locations": ["نشیمن", "آشپزخانه", "اتاق خواب", "راهرو", "حمام"]
                    }
                },
                "examples": {
                    "basic_commands": [
                        "چراغ را روشن کن",
                        "پریز را خاموش کن",
                        "نور را کم کن"
                    ],
                    "location_specific": [
                        "چراغ نشیمن را روشن کن",
                        "پریز آشپزخانه را خاموش کن"
                    ],
                    "brightness_control": [
                        "چراغ را زیاد کن",
                        "نور را کم کن",
                        "روشنایی را افزایش بده"
                    ]
                }
            }
            
            if command_type == "all":
                result = help_content
            else:
                result = help_content.get(command_type, {"error": f"Help type '{command_type}' not found"})
            
            return {
                "success": True,
                "command_type": command_type,
                "help_content": result,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Persian command help failed: {e}")
            return {"error": f"Persian command help failed: {str(e)}"}
    
    async def _get_devices_resource_content(self) -> Dict[str, Any]:
        """Get devices resource content"""
        try:
            if not self.smart_home_controller:
                return {"error": "Smart home controller not available"}
            
            devices = self.smart_home_controller.get_available_devices()
            
            return {
                "devices": devices,
                "device_count": len(devices),
                "last_updated": time.time()
            }
            
        except Exception as e:
            logger.error(f"Devices resource content failed: {e}")
            return {"error": str(e)}
    
    async def _get_capabilities_resource_content(self) -> Dict[str, Any]:
        """Get capabilities resource content"""
        try:
            if not self.smart_home_controller:
                return {"error": "Smart home controller not available"}
            
            devices = self.smart_home_controller.get_available_devices()
            capabilities_summary = {}
            
            for device_name, device_info in devices.items():
                capabilities_summary[device_name] = {
                    "type": device_info["type"],
                    "capabilities": device_info["capabilities"],
                    "protocol": device_info["protocol"]
                }
            
            return {
                "device_capabilities": capabilities_summary,
                "supported_protocols": list(set(info["protocol"] for info in devices.values())),
                "supported_device_types": list(set(info["type"] for info in devices.values())),
                "last_updated": time.time()
            }
            
        except Exception as e:
            logger.error(f"Capabilities resource content failed: {e}")
            return {"error": str(e)}
    
    async def _get_persian_commands_resource_content(self) -> str:
        """Get Persian commands resource content"""
        return """# راهنمای دستورات صوتی فارسی استیو

## دستورات کنترل دستگاه‌ها

### چراغ‌ها و نور
- چراغ را روشن کن
- لامپ را خاموش کن
- نور را کم کن
- روشنایی را زیاد کن
- چراغ نشیمن را روشن کن

### پریزها و وسایل برقی
- پریز را روشن کن
- پریز آشپزخانه را خاموش کن
- برق را قطع کن

### مکان‌ها
- نشیمن (اتاق نشیمن)
- آشپزخانه
- اتاق خواب
- حمام
- راهرو
- دفتر

### الگوهای دستور
```
[دستگاه] + [مکان] + را + [عمل] + کن

مثال:
چراغ نشیمن را روشن کن
پریز آشپزخانه را خاموش کن
```

## نکات مهم
- دستورات را واضح و آهسته بگویید
- از کلمات فارسی استاندارد استفاده کنید
- نام مکان را مشخص کنید تا دقت بیشتر باشد
"""
    
    async def _get_system_status_resource_content(self) -> Dict[str, Any]:
        """Get system status resource content"""
        try:
            status = {
                "mcp_server": {
                    "status": "active",
                    "tools_count": len(self.tools),
                    "resources_count": len(self.resources),
                    "stats": self.mcp_stats
                },
                "smart_home_controller": {
                    "available": self.smart_home_controller is not None,
                    "stats": self.smart_home_controller.get_control_stats() if self.smart_home_controller else None
                },
                "device_discovery": {
                    "available": self.device_discovery is not None,
                    "stats": self.device_discovery.get_discovered_devices_summary() if self.device_discovery else None
                },
                "timestamp": time.time()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"System status resource content failed: {e}")
            return {"error": str(e)}
    
    def _update_mcp_stats(self, response_time: float, success: bool):
        """Update MCP performance statistics"""
        if success:
            self.mcp_stats["successful_requests"] += 1
        
        # Update average response time
        total_requests = self.mcp_stats["total_requests"]
        current_avg = self.mcp_stats["average_response_time"]
        self.mcp_stats["average_response_time"] = (current_avg * (total_requests - 1) + response_time) / total_requests
    
    def get_mcp_stats(self) -> Dict[str, Any]:
        """Get MCP server statistics"""
        stats = self.mcp_stats.copy()
        
        # Calculate success rate
        if stats["total_requests"] > 0:
            stats["success_rate"] = stats["successful_requests"] / stats["total_requests"]
        else:
            stats["success_rate"] = 0.0
        
        return {
            "server_info": self.server_info,
            "tools_count": len(self.tools),
            "resources_count": len(self.resources),
            "performance_stats": stats
        }
    
    async def cleanup(self):
        """Clean up MCP server resources"""
        try:
            self.tools.clear()
            self.resources.clear()
            
            logger.info("MCP server cleanup completed")
            
        except Exception as e:
            logger.error(f"MCP server cleanup error: {e}")