import json, os, sqlite3, subprocess, tempfile, time, shlex, pathlib
from typing import List, Dict, Tuple
from .store import DB_PATH

REG_DIR = "skills_registry"
pathlib.Path(REG_DIR).mkdir(parents=True, exist_ok=True)

def list_manifests() -> List[Dict]:
    items = []
    for name in os.listdir(REG_DIR):
        d = os.path.join(REG_DIR, name)
        m = os.path.join(d, "skill.json")
        if os.path.isdir(d) and os.path.isfile(m):
            try:
                data = json.loads(open(m, "r", encoding="utf-8").read())
                data["name"] = name
                items.append(data)
            except Exception:
                pass
    return items

def permissions_conn():
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS permissions (perm TEXT PRIMARY KEY, granted INTEGER)")
    return con

def is_granted(perm: str) -> bool:
    con = permissions_conn()
    cur = con.execute("SELECT granted FROM permissions WHERE perm=?", (perm,))
    row = cur.fetchone()
    con.close()
    return bool(row and row[0])

def request_permission(perm: str) -> Dict:
    return {"permission": perm, "granted": is_granted(perm)}

def grant_permission(perm: str) -> Dict:
    con = permissions_conn()
    con.execute("INSERT OR REPLACE INTO permissions (perm, granted) VALUES (?, ?)", (perm, 1))
    con.commit()
    con.close()
    return {"permission": perm, "granted": True}

def exec_sandbox(cmd: List[str], payload: Dict, timeout_s: int = 3, skill_name: str = None) -> Tuple[int, str]:
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False))
        inpath = f.name
    try:
        if skill_name:
            skill_dir = os.path.join(REG_DIR, skill_name)
            if os.path.exists(skill_dir):
                p = subprocess.run(cmd + [inpath], capture_output=True, text=True, timeout=timeout_s, cwd=skill_dir)
            else:
                p = subprocess.run(cmd + [inpath], capture_output=True, text=True, timeout=timeout_s)
        else:
            p = subprocess.run(cmd + [inpath], capture_output=True, text=True, timeout=timeout_s)
        code = p.returncode
        out = p.stdout.strip() if p.stdout else ""
        if code != 0:
            return code, out or p.stderr.strip()
        return 0, out
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    finally:
        try:
            os.remove(inpath)
        except Exception:
            pass