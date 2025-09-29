import re
import sqlite3
import time
from .base import Skill
from heystive_professional.store import DB_PATH
pat = re.compile(r"^(note|remember)[: ]+(.*)$", re.I)
class NoteSkill(Skill):
    name = "note"
    def can_handle(self, text: str) -> bool:
        return bool(pat.match(text.strip()))
    def handle(self, text: str, context: dict) -> dict:
        m = pat.match(text.strip())
        if not m:
            return {"saved": False}
        body = m.group(2).strip()
        con = sqlite3.connect(DB_PATH)
        cur = con.execute("INSERT INTO messages (ts, role, text, skill, result) VALUES (?, ?, ?, ?, ?)", (time.time(), "user", body, "note", "{}"))
        note_id = cur.lastrowid
        con.commit()
        con.close()
        return {"saved": True, "id": note_id, "text": body}