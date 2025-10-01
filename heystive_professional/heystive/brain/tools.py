from server.settings_store import load
from server.rag_lite import search as rag_search
from server.os_skills import fs_list as os_fs_list
def tool_search_memory(q: str, k: int = 5):
    return rag_search(q=q, k=k)
def tool_list_whitelist_root():
    s = load()
    roots = s.os_whitelist_paths
    items = []
    for r in roots:
        try:
            res = os_fs_list(p=r)
            if isinstance(res, dict) and res.get("items"):
                items.append({"root": r, "items": res["items"]})
        except:
            pass
    return {"roots": items}