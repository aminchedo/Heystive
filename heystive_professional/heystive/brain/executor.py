from .planner import plan
from .tools import tool_search_memory, tool_list_whitelist_root
def run(user_text: str):
    p = plan(user_text)
    a = "reply"; q = ""
    for line in p.splitlines():
        if line.lower().startswith("action:"):
            a = line.split(":",1)[1].strip()
        if line.lower().startswith("query:"):
            q = line.split(":",1)[1].strip()
    if a == "memory.search" and q:
        res = tool_search_memory(q=q, k=5)
        return {"type":"memory","data":res}
    if a == "os.list":
        res = tool_list_whitelist_root()
        return {"type":"os","data":res}
    return {"type":"reply","data":p}