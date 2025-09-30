from typing import Tuple, Dict, List
from .skills.time_skill import TimeSkill
from .skills.calc_skill import CalcSkill
from .skills.open_url_skill import OpenUrlSkill
from .skills.note_skill import NoteSkill
skills = [NoteSkill(), TimeSkill(), CalcSkill(), OpenUrlSkill()]
skill_map = {s.name: s for s in skills}
def route_intent(text: str, context: dict) -> Tuple[str, Dict]:
    for s in skills:
        if s.can_handle(text):
            return s.name, s.handle(text, context)
    return "fallback", {"message": "no matching skill"}
def execute_plan(plan: List[dict], context: dict) -> List[dict]:
    out = []
    for step in plan or []:
        name = step.get("skill")
        args = step.get("args") or {}
        txt = args.get("text","")
        s = skill_map.get(name)
        if not s:
            out.append({"skill": name, "error": "unknown_skill"})
        else:
            res = s.handle(txt, context)
            out.append({"skill": name, "result": res})
    return out