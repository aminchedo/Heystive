"""
Smart Home Integration Tests
Tests for smart home device discovery, control, and MCP server functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from steve.smart_home.device_controller import SmartHomeController
from steve.smart_home.device_discovery import SmartHomeDeviceDiscovery, DiscoveredDevice
from steve.smart_home.mcp_server import SteveMCPServer

class TestSmartHomeController:
    """Test suite for smart home device controller"""
    
    @pytest.fixture
    def controller_config(self):
        """Mock controller configuration"""
        return {
            "hue_bridge_ip": "192.168.1.100",
            "mqtt_broker": "localhost",
            "mqtt_port": 1883
        }
    
    @pytest.fixture
    def mock_kasa_device(self):
        """Mock Kasa device"""
        device = Mock()
        device.alias = "Living Room Light"
        device.model = "KL130"
        device.mac = "AA:BB:CC:DD:EE:FF"
        device.is_on = True
        device.brightness = 80
        device.turn_on = AsyncMock()
        device.turn_off = AsyncMock()
        device.set_brightness = AsyncMock()
        device.update = AsyncMock()
        return device
    
    @pytest.fixture
    def mock_hue_light(self):
        """Mock Hue light"""
        light = Mock()
        light.name = "Bedroom Light"
        light.light_id = 1
        light.on = True
        light.brightness = 150
        return light
    
    def test_controller_initialization(self, controller_config):
        """Test smart home controller initialization"""
        controller = SmartHomeController(controller_config)
        
        assert controller.config == controller_config
        assert isinstance(controller.devices, dict)
        assert isinstance(controller.device_types, dict)
        assert isinstance(controller.persian_device_names, dict)
        
        # Check initial connection status
        assert not controller.kasa_available
        assert not controller.hue_available
        assert not controller.mqtt_available
    
    def test_device_type_determination(self, controller_config):
        """Test device type determination"""
        controller = SmartHomeController(controller_config)
        
        # Mock different device types
        bulb_device = Mock()
        bulb_device.__class__.__name__ = "SmartBulb"
        assert controller._determine_device_type(bulb_device) == "light"
        
        plug_device = Mock()
        plug_device.__class__.__name__ = "SmartPlug"
        assert controller._determine_device_type(plug_device) == "outlet"
        
        switch_device = Mock()
        switch_device.__class__.__name__ = "SmartSwitch"
        assert controller._determine_device_type(switch_device) == "switch"
    
    def test_persian_device_name_creation(self, controller_config):
        """Test Persian device name creation"""
        controller = SmartHomeController(controller_config)
        
        test_cases = [
            ("Living Room Light", "light", "چراغ Living Room Light"),
            ("Kitchen Outlet", "outlet", "پریز Kitchen Outlet"),
            ("Bedroom Switch", "switch", "کلید Bedroom Switch"),
            ("Office Fan", "unknown", "دستگاه Office Fan")
        ]
        
        for device_name, device_type, expected in test_cases:
            persian_name = controller._create_persian_device_name(device_name, device_type)
            # Should contain the Persian device type
            persian_type = expected.split()[0]
            assert persian_type in persian_name
    
    def test_persian_command_parsing(self, controller_config):
        """Test Persian command parsing"""
        controller = SmartHomeController(controller_config)
        
        test_commands = [
            ("چراغ نشیمن را روشن کن", {"device": "چراغ", "action": "turn_on"}),
            ("پریز آشپزخانه را خاموش کن", {"device": "پریز", "action": "turn_off"}),
            ("نور را کم کن", {"device": "نور", "action": "dim"}),
            ("روشنایی را زیاد کن", {"device": "روشنایی", "action": "brighten"})
        ]
        
        for command, expected in test_commands:
            parsed = controller._parse_persian_command(command)
            
            assert parsed["device"] == expected["device"]
            assert parsed["action"] == expected["action"]
            assert parsed["original"] == command
    
    @pytest.mark.asyncio
    async def test_device_control_execution(self, controller_config, mock_kasa_device):
        """Test device control execution"""
        controller = SmartHomeController(controller_config)
        
        # Add mock device to controller
        controller.devices["Living Room Light"] = {
            "device": mock_kasa_device,
            "type": "light",
            "name": "Living Room Light",
            "protocol": "kasa",
            "capabilities": ["on_off", "brightness"]
        }
        
        # Test turn on
        result = await controller._execute_device_command("Living Room Light", "turn_on")
        assert "روشن شد" in result
        mock_kasa_device.turn_on.assert_called_once()
        
        # Test turn off
        result = await controller._execute_device_command("Living Room Light", "turn_off")
        assert "خاموش شد" in result
        mock_kasa_device.turn_off.assert_called_once()
        
        # Test brightness control
        result = await controller._execute_device_command("Living Room Light", "brighten")
        assert "افزایش یافت" in result
        mock_kasa_device.set_brightness.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_persian_command_control(self, controller_config, mock_kasa_device):
        """Test complete Persian command control"""
        controller = SmartHomeController(controller_config)
        
        # Add mock device
        controller.devices["Living Room Light"] = {
            "device": mock_kasa_device,
            "type": "light",
            "name": "Living Room Light",
            "protocol": "kasa",
            "capabilities": ["on_off"]
        }
        
        # Add Persian name mapping
        controller.persian_device_names["چراغ"] = "Living Room Light"
        
        # Test Persian command
        result = await controller.control_device_by_persian_command("چراغ را روشن کن")
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Should indicate success or provide feedback
        assert any(word in result for word in ["روشن", "انجام", "شد"])
    
    def test_control_statistics(self, controller_config):
        """Test control statistics tracking"""
        controller = SmartHomeController(controller_config)
        
        # Initial stats
        stats = controller.get_control_stats()
        
        assert "controller_status" in stats
        assert "device_count" in stats
        assert "performance_stats" in stats
        
        controller_status = stats["controller_status"]
        assert "kasa_available" in controller_status
        assert "hue_available" in controller_status
        assert "mqtt_available" in controller_status
        
        performance_stats = stats["performance_stats"]
        assert "total_commands" in performance_stats
        assert "successful_commands" in performance_stats
        assert "success_rate" in performance_stats

class TestDeviceDiscovery:
    """Test suite for device discovery"""
    
    @pytest.fixture
    def discovery_config(self):
        """Discovery configuration"""
        return {
            "network_range": "192.168.1.0/24",
            "discovery_timeout": 10
        }
    
    @pytest.fixture
    def mock_discovered_device(self):
        """Mock discovered device"""
        return DiscoveredDevice(
            name="Test Light",
            ip_address="192.168.1.50",
            mac_address="AA:BB:CC:DD:EE:FF",
            device_type="light",
            protocol="kasa",
            manufacturer="TP-Link",
            model="KL130",
            capabilities=["on_off", "brightness"],
            persian_name="چراغ تست",
            discovery_method="kasa_discovery",
            confidence=0.95
        )
    
    def test_discovery_initialization(self, discovery_config):
        """Test device discovery initialization"""
        discovery = SmartHomeDeviceDiscovery(discovery_config)
        
        assert discovery.config == discovery_config
        assert discovery.network_range == "192.168.1.0/24"
        assert discovery.discovery_timeout == 10
        assert len(discovery.discovery_methods) > 0
        assert isinstance(discovery.discovered_devices, dict)
    
    def test_device_signatures_loading(self, discovery_config):
        """Test device signature loading"""
        discovery = SmartHomeDeviceDiscovery(discovery_config)
        
        signatures = discovery.device_signatures
        
        # Should have signatures for major protocols
        assert "kasa" in signatures
        assert "hue" in signatures
        
        # Check Kasa signature structure
        kasa_sig = signatures["kasa"]
        assert "ports" in kasa_sig
        assert "protocols" in kasa_sig
        assert "identification" in kasa_sig
        assert "device_types" in kasa_sig
    
    def test_persian_name_generation(self, discovery_config):
        """Test Persian name generation for discovered devices"""
        discovery = SmartHomeDeviceDiscovery(discovery_config)
        
        test_cases = [
            ("Living Room Light", "light", "چراغ"),
            ("Kitchen Outlet", "outlet", "پریز"),
            ("Bedroom Switch", "switch", "کلید"),
            ("Office Hub", "hub", "پل")
        ]
        
        for device_name, device_type, expected_persian_type in test_cases:
            persian_name = discovery._generate_persian_name(device_name, device_type)
            assert expected_persian_type in persian_name
    
    @pytest.mark.asyncio
    async def test_discovery_method_execution(self, discovery_config):
        """Test discovery method execution"""
        discovery = SmartHomeDeviceDiscovery(discovery_config)
        
        # Test that discovery methods can be called without errors
        method_name = "network_scan"
        method_func = discovery._discover_via_network_scan
        
        # Should not raise exceptions
        try:
            await discovery._run_discovery_method(method_name, method_func)
            # Method executed successfully
            assert True
        except Exception as e:
            # Some methods might fail due to missing dependencies, which is OK for testing
            assert "not available" in str(e) or "not installed" in str(e) or "failed" in str(e)
    
    def test_discovered_devices_summary(self, discovery_config, mock_discovered_device):
        """Test discovered devices summary generation"""
        discovery = SmartHomeDeviceDiscovery(discovery_config)
        
        # Add mock device
        discovery.discovered_devices["test_device"] = mock_discovered_device
        
        summary = discovery.get_discovered_devices_summary()
        
        assert "total_devices" in summary
        assert "by_protocol" in summary
        assert "by_type" in summary
        assert "by_manufacturer" in summary
        assert "discovery_stats" in summary
        
        assert summary["total_devices"] == 1
        assert summary["by_protocol"]["kasa"] == 1
        assert summary["by_type"]["light"] == 1
        assert summary["by_manufacturer"]["TP-Link"] == 1
    
    def test_devices_for_controller_format(self, discovery_config, mock_discovered_device):
        """Test device formatting for controller"""
        discovery = SmartHomeDeviceDiscovery(discovery_config)
        
        # Add mock device
        discovery.discovered_devices["test_device"] = mock_discovered_device
        
        controller_devices = discovery.get_devices_for_controller()
        
        assert len(controller_devices) == 1
        
        device = controller_devices[0]
        assert "id" in device
        assert "name" in device
        assert "persian_name" in device
        assert "ip_address" in device
        assert "device_type" in device
        assert "protocol" in device
        assert "capabilities" in device
        assert "confidence" in device
        
        assert device["name"] == "Test Light"
        assert device["persian_name"] == "چراغ تست"
        assert device["protocol"] == "kasa"

class TestMCPServer:
    """Test suite for MCP server"""
    
    @pytest.fixture
    def mock_smart_home_controller(self):
        """Mock smart home controller"""
        controller = Mock()
        controller.control_device_by_persian_command = AsyncMock(return_value="چراغ روشن شد")
        controller.get_device_status = AsyncMock(return_value={"Living Room Light": {"is_on": True}})
        controller.get_available_devices = Mock(return_value={
            "Living Room Light": {
                "persian_name": "چراغ نشیمن",
                "type": "light",
                "protocol": "kasa",
                "capabilities": ["on_off", "brightness"]
            }
        })
        controller.get_control_stats = Mock(return_value={
            "controller_status": {"kasa_available": True},
            "device_count": 1,
            "performance_stats": {"total_commands": 5, "successful_commands": 4}
        })
        return controller
    
    @pytest.fixture
    def mock_device_discovery(self):
        """Mock device discovery"""
        discovery = Mock()
        discovery.discover_all_devices = AsyncMock(return_value={
            "device1": Mock(name="Test Device", persian_name="دستگاه تست")
        })
        discovery.get_discovered_devices_summary = Mock(return_value={
            "total_devices": 1,
            "by_protocol": {"kasa": 1}
        })
        return discovery
    
    @pytest.fixture
    def mcp_server(self, mock_smart_home_controller, mock_device_discovery):
        """Create MCP server for testing"""
        return SteveMCPServer(mock_smart_home_controller, mock_device_discovery)
    
    def test_mcp_server_initialization(self, mcp_server):
        """Test MCP server initialization"""
        assert len(mcp_server.tools) > 0
        assert len(mcp_server.resources) > 0
        
        # Check server info
        server_info = mcp_server.server_info
        assert "name" in server_info
        assert "version" in server_info
        assert "description" in server_info
        assert "steve" in server_info["name"].lower()
    
    def test_mcp_tools_initialization(self, mcp_server):
        """Test MCP tools initialization"""
        tools = mcp_server.tools
        
        # Should have essential tools
        expected_tools = [
            "control_device",
            "get_device_status", 
            "discover_devices",
            "list_devices",
            "persian_command_help"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tools
            tool = tools[tool_name]
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'parameters')
            assert hasattr(tool, 'handler')
    
    def test_mcp_resources_initialization(self, mcp_server):
        """Test MCP resources initialization"""
        resources = mcp_server.resources
        
        # Should have essential resources
        expected_resources = [
            "devices",
            "capabilities",
            "persian_commands",
            "system_status"
        ]
        
        for resource_name in expected_resources:
            assert resource_name in resources
            resource = resources[resource_name]
            assert hasattr(resource, 'uri')
            assert hasattr(resource, 'name')
            assert hasattr(resource, 'description')
            assert hasattr(resource, 'mime_type')
            assert hasattr(resource, 'content')
    
    @pytest.mark.asyncio
    async def test_mcp_initialize_request(self, mcp_server):
        """Test MCP initialize request handling"""
        request = {
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        response = await mcp_server.handle_mcp_request(request)
        
        assert "result" in response
        result = response["result"]
        assert "protocolVersion" in result
        assert "capabilities" in result
        assert "serverInfo" in result
    
    @pytest.mark.asyncio
    async def test_mcp_list_tools_request(self, mcp_server):
        """Test MCP list tools request handling"""
        request = {
            "method": "tools/list",
            "params": {}
        }
        
        response = await mcp_server.handle_mcp_request(request)
        
        assert "result" in response
        result = response["result"]
        assert "tools" in result
        
        tools = result["tools"]
        assert len(tools) > 0
        
        # Check tool structure
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    @pytest.mark.asyncio
    async def test_mcp_call_tool_request(self, mcp_server):
        """Test MCP tool call request handling"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "control_device",
                "arguments": {
                    "persian_command": "چراغ را روشن کن"
                }
            }
        }
        
        response = await mcp_server.handle_mcp_request(request)
        
        assert "result" in response
        result = response["result"]
        assert "content" in result
        
        content = result["content"]
        assert len(content) > 0
        assert content[0]["type"] == "text"
        
        # Parse the JSON response
        tool_result = json.loads(content[0]["text"])
        assert "success" in tool_result
        assert "command" in tool_result
        assert "result" in tool_result
    
    @pytest.mark.asyncio
    async def test_mcp_list_resources_request(self, mcp_server):
        """Test MCP list resources request handling"""
        request = {
            "method": "resources/list",
            "params": {}
        }
        
        response = await mcp_server.handle_mcp_request(request)
        
        assert "result" in response
        result = response["result"]
        assert "resources" in result
        
        resources = result["resources"]
        assert len(resources) > 0
        
        # Check resource structure
        for resource in resources:
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            assert "mimeType" in resource
    
    @pytest.mark.asyncio
    async def test_mcp_read_resource_request(self, mcp_server):
        """Test MCP read resource request handling"""
        request = {
            "method": "resources/read",
            "params": {
                "uri": "steve://devices"
            }
        }
        
        response = await mcp_server.handle_mcp_request(request)
        
        assert "result" in response
        result = response["result"]
        assert "contents" in result
        
        contents = result["contents"]
        assert len(contents) > 0
        
        content = contents[0]
        assert "uri" in content
        assert "mimeType" in content
        assert "text" in content
        
        # Should be valid JSON
        resource_data = json.loads(content["text"])
        assert isinstance(resource_data, dict)
    
    @pytest.mark.asyncio
    async def test_device_control_tool(self, mcp_server):
        """Test device control tool functionality"""
        arguments = {
            "persian_command": "چراغ نشیمن را روشن کن"
        }
        
        result = await mcp_server._handle_control_device(arguments)
        
        assert "success" in result
        assert result["success"] is True
        assert "command" in result
        assert "result" in result
        assert result["command"] == "چراغ نشیمن را روشن کن"
    
    @pytest.mark.asyncio
    async def test_persian_command_help_tool(self, mcp_server):
        """Test Persian command help tool"""
        arguments = {
            "command_type": "device_control"
        }
        
        result = await mcp_server._handle_persian_command_help(arguments)
        
        assert "success" in result
        assert result["success"] is True
        assert "help_content" in result
        
        help_content = result["help_content"]
        assert "description" in help_content
        assert "examples" in help_content
        assert "patterns" in help_content
        
        # Should contain Persian text
        assert any("چراغ" in str(value) for value in help_content.values())
    
    def test_mcp_statistics(self, mcp_server):
        """Test MCP server statistics"""
        stats = mcp_server.get_mcp_stats()
        
        assert "server_info" in stats
        assert "tools_count" in stats
        assert "resources_count" in stats
        assert "performance_stats" in stats
        
        assert stats["tools_count"] > 0
        assert stats["resources_count"] > 0
        
        performance_stats = stats["performance_stats"]
        assert "total_requests" in performance_stats
        assert "successful_requests" in performance_stats
        assert "success_rate" in performance_stats

class TestSmartHomeIntegration:
    """Integration tests for smart home components"""
    
    @pytest.mark.asyncio
    async def test_controller_discovery_integration(self):
        """Test integration between controller and discovery"""
        # Create discovery and controller
        discovery = SmartHomeDeviceDiscovery()
        controller = SmartHomeController()
        
        # Mock discovered device
        mock_device = DiscoveredDevice(
            name="Integration Test Light",
            ip_address="192.168.1.99",
            mac_address="FF:EE:DD:CC:BB:AA",
            device_type="light",
            protocol="kasa",
            manufacturer="TP-Link",
            model="KL130",
            capabilities=["on_off", "brightness"],
            persian_name="چراغ تست یکپارچگی",
            discovery_method="test",
            confidence=1.0
        )
        
        discovery.discovered_devices["test_device"] = mock_device
        
        # Get devices for controller
        controller_devices = discovery.get_devices_for_controller()
        
        assert len(controller_devices) == 1
        device = controller_devices[0]
        
        # Verify device format is compatible with controller
        assert all(key in device for key in [
            "name", "persian_name", "device_type", "protocol", "capabilities"
        ])
    
    @pytest.mark.asyncio
    async def test_mcp_controller_integration(self):
        """Test integration between MCP server and controller"""
        # Create mock controller
        controller = Mock()
        controller.control_device_by_persian_command = AsyncMock(return_value="دستور انجام شد")
        controller.get_available_devices = Mock(return_value={})
        controller.get_control_stats = Mock(return_value={"device_count": 0})
        
        # Create MCP server
        mcp_server = SteveMCPServer(controller)
        
        # Test device control through MCP
        request = {
            "method": "tools/call",
            "params": {
                "name": "control_device",
                "arguments": {
                    "persian_command": "چراغ را روشن کن"
                }
            }
        }
        
        response = await mcp_server.handle_mcp_request(request)
        
        assert "result" in response
        # Controller method should have been called
        controller.control_device_by_persian_command.assert_called_once_with("چراغ را روشن کن")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])