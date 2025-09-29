import sqlite3
import os
from .base import Skill

DB_PATH = os.environ.get("HEYSTIVE_DB", "heystive.db")

class NoteSkill(Skill):
    name = "note"
    
    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return "note" in t or "یادداشت" in t or "نوت" in t
    
    def handle(self, text: str, context: dict) -> dict:
        try:
            note_text = self._extract_note_text(text)
            if not note_text:
                return {"saved": False, "error": "no note content found"}
            
            note_id = self._save_note(note_text)
            return {"saved": True, "id": note_id, "text": note_text}
        except Exception as e:
            return {"saved": False, "error": str(e)}
    
    def _extract_note_text(self, text: str) -> str:
        t = text.lower()
        if "note" in t:
            parts = text.split("note", 1)
            if len(parts) > 1:
                return parts[1].strip()
        elif "یادداشت" in t:
            parts = text.split("یادداشت", 1)
            if len(parts) > 1:
                return parts[1].strip()
        elif "نوت" in t:
            parts = text.split("نوت", 1)
            if len(parts) > 1:
                return parts[1].strip()
        return text.strip()
    
    def _save_note(self, note_text: str) -> int:
        con = sqlite3.connect(DB_PATH)
        con.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, created_at REAL)")
        cursor = con.execute("INSERT INTO notes (text, created_at) VALUES (?, ?)", (note_text, __import__('time').time()))
        note_id = cursor.lastrowid
        con.commit()
        con.close()
        return note_id