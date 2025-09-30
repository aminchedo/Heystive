import json, subprocess, time, os, signal, sys
def start():
    p = subprocess.Popen([sys.executable, "heystive_professional/backend_min.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1.0)
    return p
def stop(p):
    try: p.terminate()
    except Exception: pass
def test_ping_and_settings():
    p = start()
    try:
        import urllib.request
        j=json.loads(urllib.request.urlopen("http://127.0.0.1:8000/ping").read().decode())
        assert j["status"]=="healthy"
        html=urllib.request.urlopen("http://127.0.0.1:8000/settings").read().decode()
        assert "<h1>Heystive Settings</h1>" in html
        req=urllib.request.Request("http://127.0.0.1:8000/api/settings", data=json.dumps({"web":{"theme":"dark"}}).encode(), headers={"Content-Type":"application/json"})
        r=json.loads(urllib.request.urlopen(req).read().decode())
        assert r["ok"] is True
    finally:
        stop(p)