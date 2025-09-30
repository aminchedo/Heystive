import sqlite3, time, json
from typing import List, Dict
from .store import DB_PATH

def conn():
    c = sqlite3.connect(DB_PATH)
    c.execute("CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, text TEXT, tags TEXT)")
    return c

def upsert(text: str, tags: List[str]):
    c = conn()
    cur = c.execute("INSERT INTO memory (ts, text, tags) VALUES (?, ?, ?)", (time.time(), text, json.dumps(tags or [])))
    c.commit()
    i = cur.lastrowid
    c.close()
    return i

def search(q: str, limit: int):
    c = conn()
    like = f"%{q}%"
    cur = c.execute("SELECT id, ts, text, tags FROM memory WHERE text LIKE ? ORDER BY id DESC LIMIT ?", (like, limit))
    rows = [{"id":r[0], "ts":r[1], "text":r[2], "tags": json.loads(r[3] or "[]")} for r in cur.fetchall()]
    c.close()
    return rows