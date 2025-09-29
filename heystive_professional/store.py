import os, time, json, sqlite3
DB_PATH = os.environ.get("HEYSTIVE_DB", "heystive.db")
def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, role TEXT, text TEXT, skill TEXT, result TEXT)")
    con.commit(); con.close()
def log_message(role: str, text: str, skill: str, result: dict):
    con = sqlite3.connect(DB_PATH)
    con.execute("INSERT INTO messages (ts, role, text, skill, result) VALUES (?, ?, ?, ?, ?)", (time.time(), role, text, skill, json.dumps(result, ensure_ascii=False)))
    con.commit(); con.close()
init_db()