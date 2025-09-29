from datetime import datetime, timezone
from .base import Skill
class TimeSkill(Skill):
    name = "time"
    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return "time" in t or "what time" in t or "clock" in t
    def handle(self, text: str, context: dict) -> dict:
        now = datetime.now(timezone.utc)
        return {"time_iso": now.isoformat(), "time_human": now.strftime("%Y-%m-%d %H:%M:%S %Z")}