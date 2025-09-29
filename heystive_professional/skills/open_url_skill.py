import re
from .base import Skill
url_re = re.compile(r"(https?://[\w\.-]+[\w\-/\.?=#%&+]*)", re.I)
class OpenUrlSkill(Skill):
    name = "open_url"
    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return t.startswith("open ") and bool(url_re.search(t))
    def handle(self, text: str, context: dict) -> dict:
        m = url_re.search(text)
        if not m: return {"accepted": False}
        url = m.group(1)
        return {"accepted": True, "action": "open_url", "url": url}