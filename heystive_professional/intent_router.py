from typing import Tuple, Dict
from .skills.time_skill import TimeSkill
from .skills.calc_skill import CalcSkill
from .skills.open_url_skill import OpenUrlSkill
from .skills.note_skill import NoteSkill
skills = [NoteSkill(), TimeSkill(), CalcSkill(), OpenUrlSkill()]
def route_intent(text: str, context: dict) -> Tuple[str, Dict]:
    for s in skills:
        if s.can_handle(text):
            return s.name, s.handle(text, context)
    return "fallback", {"message": "no matching skill"}