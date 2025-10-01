import time, platform
import psutil
from fastapi.responses import JSONResponse
def metrics_handler():
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    try:
        import os
        load = os.getloadavg()
    except Exception:
        load = (0,0,0)
    return JSONResponse({
        "ts": int(time.time()),
        "cpu": cpu,
        "mem_total": mem.total,
        "mem_used": mem.used,
        "mem_percent": mem.percent,
        "load": list(load),
        "platform": platform.platform(),
    })