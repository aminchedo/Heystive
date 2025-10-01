import time, threading, queue, requests, numpy as np
import sounddevice as sd
import webrtcvad
from openwakeword import Model

BASE = "http://127.0.0.1:8765"
CFG = {"enabled": True, "keyword": "hey steve", "sensitivity": 0.5, "device": None}
RUN = True

def fetch_settings():
    try:
        r = requests.get(f"{BASE}/api/settings", timeout=3)
        s = r.json()
        CFG["enabled"] = bool(s.get("wakeword_enabled", True))
        CFG["keyword"] = s.get("wakeword_keyword", "hey steve")
        CFG["sensitivity"] = float(s.get("wakeword_sensitivity", 0.5))
        CFG["device"] = s.get("wakeword_device_index", None)
    except Exception:
        pass

def pick_label(scores: dict, key_hint: str):
    kh = key_hint.strip().lower()
    best = None
    bestv = 0.0
    for k, v in scores.items():
        if kh in k.lower():
            if v > bestv:
                best, bestv = k, v
    if best is None:
        for k, v in scores.items():
            if v > bestv:
                best, bestv = k, v
    return best, bestv

def audio_stream(q, device):
    sr = 16000
    bs = 8000
    def cb(indata, frames, time_info, status):
        try:
            q.put(indata.copy())
        except Exception:
            pass
    with sd.InputStream(callback=cb, channels=1, samplerate=sr, blocksize=bs, dtype="float32", device=device):
        while RUN:
            time.sleep(0.05)

def main():
    fetch_settings()
    vad = webrtcvad.Vad(2)
    mdl = Model(trigger_level=CFG["sensitivity"])
    last = 0.0
    q = queue.Queue(maxsize=8)
    t = threading.Thread(target=audio_stream, args=(q, CFG["device"]), daemon=True)
    t.start()
    buf = bytes()
    sr = 16000
    frame_ms = 20
    frame_bytes = int(sr/1000*frame_ms)*2
    while RUN:
        try:
            fetch_settings()
            if not CFG["enabled"]:
                time.sleep(0.5)
                continue
            chunk = q.get(timeout=1)
            pcm16 = np.clip(chunk[:,0]*32767, -32768, 32767).astype(np.int16).tobytes()
            buf += pcm16
            while len(buf) >= frame_bytes:
                frame = buf[:frame_bytes]
                buf = buf[frame_bytes:]
                if not vad.is_speech(frame, sr):
                    continue
                y = np.frombuffer(frame, dtype=np.int16).astype(np.float32)/32767.0
                scores = mdl.predict(y)
                label, score = pick_label(scores, CFG["keyword"])
                if score >= CFG["sensitivity"]:
                    now = time.time()
                    if now - last > 5.0:
                        try:
                            requests.post(f"{BASE}/api/intent", json={"text":"listen"}, timeout=2)
                        except Exception:
                            pass
                        last = now
        except Exception:
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        RUN = False