import re
def plan_text(text: str):
    t = (text or "").strip()
    low = t.lower()
    plan = []
    m = re.match(r"^(note|remember)[: ]+(.*)$", t, re.I)
    if m:
        body = m.group(2).strip()
        plan.append({"skill":"note","args":{"text":"note "+body}})
    urlm = re.search(r"(https?://[\w\.-]+[\w\-/\.?=#%&+]*)", t, re.I)
    if urlm:
        plan.append({"skill":"open_url","args":{"text":t}})
    if ("time" in low) or ("what time" in low) or ("clock" in low):
        plan.append({"skill":"time","args":{"text":t}})
    s = t.replace(" ", "")
    if s and any(c in s for c in "+-*/") and all(c in "0123456789+-*/().%^" for c in s):
        plan.append({"skill":"calc","args":{"text":t}})
    msg = "demo planner"
    return "demo", plan, msg