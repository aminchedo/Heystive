"""
End-to-end tests for command system
"""

import requests
import time
import pytest

BASE = "http://127.0.0.1:8765"

def wait_health():
    """Wait for server to be healthy"""
    for _ in range(60):
        try:
            if requests.get(f"{BASE}/healthz", timeout=2).status_code == 200:
                return
        except Exception:
            time.sleep(1)
    raise SystemExit(1)

def test_commands_list():
    """Test commands list endpoint"""
    wait_health()
    r = requests.get(f"{BASE}/api/commands/list", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert "commands" in data
    assert isinstance(data["commands"], list)
    assert len(data["commands"]) > 0

def test_command_status():
    """Test system status command"""
    wait_health()
    r = requests.post(f"{BASE}/api/commands/run", 
                     json={"name": "system.status", "args": {}}, 
                     timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert "data" in data
    assert "cpu" in data["data"]
    assert "mem_percent" in data["data"]

def test_command_memory_search():
    """Test memory search command"""
    wait_health()
    r = requests.post(f"{BASE}/api/commands/run", 
                     json={"name": "memory.search", "args": {"q": "test", "k": 3}}, 
                     timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True

def test_command_theme_toggle():
    """Test theme toggle command"""
    wait_health()
    r = requests.post(f"{BASE}/api/commands/run", 
                     json={"name": "theme.toggle", "args": {}}, 
                     timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert "data" in data
    assert "theme" in data["data"]
    assert data["data"]["theme"] in ["light", "dark"]

def test_command_note_add():
    """Test note add command"""
    wait_health()
    r = requests.post(f"{BASE}/api/commands/run", 
                     json={"name": "note.add", "args": {"text": "Test note from e2e"}}, 
                     timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True

def test_command_note_search():
    """Test note search command"""
    wait_health()
    r = requests.post(f"{BASE}/api/commands/run", 
                     json={"name": "note.search", "args": {"q": "test"}}, 
                     timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert "data" in data
    assert "matches" in data["data"]

def test_command_not_found():
    """Test command not found error"""
    wait_health()
    r = requests.post(f"{BASE}/api/commands/run", 
                     json={"name": "nonexistent.command", "args": {}}, 
                     timeout=10)
    assert r.status_code == 404
    data = r.json()
    assert data.get("ok") is False
    assert "error" in data

def test_command_invalid_args():
    """Test command with invalid arguments"""
    wait_health()
    r = requests.post(f"{BASE}/api/commands/run", 
                     json={"name": "note.add", "args": {}},  # Missing required 'text' arg
                     timeout=10)
    assert r.status_code == 500
    data = r.json()
    assert data.get("ok") is False
    assert "error" in data

if __name__ == "__main__":
    # Run tests manually
    try:
        test_commands_list()
        print("✅ test_commands_list passed")
        
        test_command_status()
        print("✅ test_command_status passed")
        
        test_command_memory_search()
        print("✅ test_command_memory_search passed")
        
        test_command_theme_toggle()
        print("✅ test_command_theme_toggle passed")
        
        test_command_note_add()
        print("✅ test_command_note_add passed")
        
        test_command_note_search()
        print("✅ test_command_note_search passed")
        
        test_command_not_found()
        print("✅ test_command_not_found passed")
        
        test_command_invalid_args()
        print("✅ test_command_invalid_args passed")
        
        print("\n🎉 All command tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise