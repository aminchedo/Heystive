from typing import Tuple, List, Dict

def plan_text(text: str) -> Tuple[str, List[dict], str]:
    engine = "simple"
    plan = [{"skill": "fallback", "args": {"text": text}}]
    message = f"Processed: {text}"
    return engine, plan, message