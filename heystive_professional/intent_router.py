from typing import Tuple, Dict, List
from skills.time_skill import TimeSkill
from skills.calc_skill import CalcSkill
from skills.open_url_skill import OpenUrlSkill
from skills.note_skill import NoteSkill
skills = [TimeSkill(), CalcSkill(), OpenUrlSkill(), NoteSkill()]
def route_intent(text: str, context: dict) -> Tuple[str, Dict]:
    for s in skills:
        if s.can_handle(text):
            return s.name, s.handle(text, context)
    return "fallback", {"message": "no matching skill"}

def execute_plan(plan: List[dict], context: dict) -> List[dict]:
    results = []
    for step in plan:
        skill_name = step.get("skill", "fallback")
        args = step.get("args", {})
        result = {"skill": skill_name, "args": args}
        for s in skills:
            if s.name == skill_name:
                try:
                    result["result"] = s.handle(str(args), context)
                except Exception as e:
                    result["result"] = {"error": str(e)}
                break
        else:
            result["result"] = {"error": "unknown skill"}
        results.append(result)
    return results