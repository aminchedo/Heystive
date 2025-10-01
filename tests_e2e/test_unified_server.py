import requests, time
BASE = "http://127.0.0.1:8765"
def wait_health():
    for _ in range(60):
        try:
            if requests.get(f"{BASE}/healthz", timeout=2).status_code==200:
                return
        except Exception:
            time.sleep(1)
    raise SystemExit(1)
def test_health_ready_metrics():
    wait_health()
    assert requests.get(f"{BASE}/readyz", timeout=5).status_code==200
    assert requests.get(f"{BASE}/metrics", timeout=5).status_code==200
def test_index():
    wait_health()
    assert requests.get(f"{BASE}/", timeout=5).status_code==200