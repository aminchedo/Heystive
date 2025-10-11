"""
Command System for Heystive
Registry and execution with allowlists
"""

from pydantic import BaseModel, Field
from typing import Callable, Dict, Any, List, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import subprocess
import shutil
import os
import platform
import time
import psutil

router = APIRouter()
REGISTRY: Dict[str, Dict[str, Any]] = {}

class Command(BaseModel):
    name: str
    title: str
    description: str
    params: List[Dict[str, Any]] = Field(default_factory=list)

def register(name: str, title: str, description: str):
    """Decorator to register a command"""
    def deco(fn: Callable[..., Any]):
        REGISTRY[name] = {"meta": Command(name=name, title=title, description=description), "fn": fn}
        return fn
    return deco

def ok(payload=None):
    """Return success response"""
    return {"ok": True, "data": payload}

def fail(msg: str, code: int = 400):
    """Return error response"""
    return JSONResponse(status_code=code, content={"ok": False, "error": msg})

@router.get("/list")
def list_commands():
    """List all available commands"""
    return {"ok": True, "commands": [v["meta"].model_dump() for v in REGISTRY.values()]}

@router.post("/run")
def run_command(payload: Dict[str, Any]):
    """Execute a command"""
    name = payload.get("name")
    args = payload.get("args", {})
    
    if name not in REGISTRY:
        return fail("Command not found", 404)
    
    fn = REGISTRY[name]["fn"]
    try:
        res = fn(**args) if isinstance(args, dict) else fn()
        return ok(res)
    except Exception as e:
        return fail(str(e), 500)

# Core Commands

@register("system.status", "System Status", "Show CPU/MEM/Platform information")
def cmd_system_status():
    """Get system status information"""
    try:
        mem = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=None)
        return {
            "cpu": cpu_percent,
            "mem_percent": mem.percent,
            "mem_available": mem.available,
            "mem_total": mem.total,
            "platform": platform.platform(),
            "ts": int(time.time())
        }
    except Exception as e:
        return {"error": str(e)}

@register("memory.search", "Search Memory", "Search local knowledge base")
def cmd_memory_search(q: str, k: int = 5):
    """Search in memory/knowledge base"""
    try:
        from server.rag_lite import search as rag_search
        return rag_search(q=q, k=k)
    except Exception as e:
        return {"error": str(e)}

@register("os.list", "List Whitelist Roots", "List files in whitelisted roots")
def cmd_os_list():
    """List files in whitelisted directories"""
    try:
        from server.settings_store import load
        from server.os_skills import fs_list as os_fs_list
        
        s = load()
        roots = s.os_whitelist_paths
        out = []
        
        for r in roots:
            try:
                res = os_fs_list(p=r)
                if isinstance(res, dict) and res.get("items"):
                    out.append({"root": r, "items": res["items"]})
            except Exception:
                pass
                
        return {"roots": out}
    except Exception as e:
        return {"error": str(e)}

@register("app.open", "Open Allowed App", "Open an app from whitelist")
def cmd_app_open(name: str):
    """Open an application from whitelist"""
    try:
        from server.settings_store import load
        
        s = load()
        if name not in s.os_whitelist_apps:
            return fail("Application not in whitelist", 403)
            
        subprocess.Popen([name])
        return {"opened": name}
    except Exception as e:
        return fail(str(e), 400)

@register("theme.toggle", "Toggle Theme", "Toggle between light/dark theme")
def cmd_theme_toggle():
    """Toggle application theme"""
    try:
        from server.settings_store import save, load, Settings
        
        s = load()
        cur = s.theme
        nxt = "dark" if cur == "light" else "light"
        s.theme = nxt
        save(s)
        return {"theme": nxt}
    except Exception as e:
        return {"error": str(e)}

@register("files.search", "Search Files", "Search filenames in whitelist roots")
def cmd_files_search(q: str):
    """Search for files in whitelisted directories"""
    try:
        from server.settings_store import load
        
        s = load()
        roots = s.os_whitelist_paths
        hits = []
        
        for root in roots:
            for dirpath, dirnames, filenames in os.walk(root):
                for f in filenames:
                    if q.lower() in f.lower():
                        hits.append(os.path.join(dirpath, f))
                        
        return {"matches": hits[:200]}  # Limit to 200 results
    except Exception as e:
        return {"error": str(e)}

@register("intent.listen", "Start Listening", "Start STT listening loop")
def cmd_intent_listen():
    """Start voice listening"""
    return {"intent": "listen"}

@register("intent.mute", "Mute Listening", "Stop STT listening loop")
def cmd_intent_mute():
    """Stop voice listening"""
    return {"intent": "mute"}

# Additional Commands

@register("note.add", "Add Note", "Append a note to knowledge/notes.md")
def cmd_note_add(text: str):
    """Add a note to the knowledge base"""
    try:
        p = "knowledge/notes.md"
        os.makedirs("knowledge", exist_ok=True)
        
        with open(p, "a", encoding="utf-8") as f:
            f.write(text.strip() + "\n")
            
        return {"ok": True, "message": "Note added successfully"}
    except Exception as e:
        return {"error": str(e)}

@register("note.search", "Search Notes", "Search in notes")
def cmd_note_search(q: str):
    """Search in notes"""
    try:
        p = "knowledge/notes.md"
        if not os.path.exists(p):
            return {"matches": []}
            
        hits = []
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                if q.lower() in line.lower():
                    hits.append({"line": i, "text": line.strip()})
                    
        return {"matches": hits[:200]}
    except Exception as e:
        return {"error": str(e)}

@register("system.open_path", "Open Path", "Open path in file manager if whitelisted")
def cmd_open_path(path: str):
    """Open a path in the system file manager"""
    try:
        from server.settings_store import load
        
        s = load()
        ok = False
        
        for r in s.os_whitelist_paths:
            if str(os.path.abspath(path)).startswith(str(os.path.abspath(r))):
                ok = True
                break
                
        if not ok:
            return fail("Path not in whitelist", 403)
            
        if platform.system() == "Windows":
            subprocess.Popen(["explorer", path])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
            
        return {"opened": path}
    except Exception as e:
        return fail(str(e), 400)

@register("files.move_safe", "Move File", "Move a file within whitelist")
def cmd_files_move_safe(src: str, dst: str):
    """Safely move a file within whitelisted paths"""
    try:
        from server.settings_store import load
        
        s = load()
        
        def allowed(p):
            for r in s.os_whitelist_paths:
                if str(os.path.abspath(p)).startswith(str(os.path.abspath(r))):
                    return True
            return False
            
        if not allowed(src) or not allowed(dst):
            return fail("Path not in whitelist", 403)
            
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        return {"moved": {"src": src, "dst": dst}}
    except Exception as e:
        return fail(str(e), 400)

@register("system.info", "System Info", "Get detailed system information")
def cmd_system_info():
    """Get detailed system information"""
    try:
        return {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "boot_time": psutil.boot_time(),
            "users": [user._asdict() for user in psutil.users()],
            "disk_usage": {partition.device: {
                "total": psutil.disk_usage(partition.mountpoint).total,
                "used": psutil.disk_usage(partition.mountpoint).used,
                "free": psutil.disk_usage(partition.mountpoint).free,
                "percent": psutil.disk_usage(partition.mountpoint).percent
            } for partition in psutil.disk_partitions()}
        }
    except Exception as e:
        return {"error": str(e)}

@register("process.list", "List Processes", "List running processes")
def cmd_process_list(limit: int = 20):
    """List running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        # Sort by CPU usage
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        return {"processes": processes[:limit]}
    except Exception as e:
        return {"error": str(e)}

@register("network.info", "Network Info", "Get network information")
def cmd_network_info():
    """Get network information"""
    try:
        return {
            "interfaces": {interface: {
                "addresses": [addr._asdict() for addr in addrs],
                "is_up": psutil.net_if_stats()[interface].isup if interface in psutil.net_if_stats() else False
            } for interface, addrs in psutil.net_if_addrs().items()},
            "connections": len(psutil.net_connections()),
            "io_counters": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
        }
    except Exception as e:
        return {"error": str(e)}