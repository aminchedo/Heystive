import json
try:
    from vosk import Model, KaldiRecognizer
except Exception:
    Model = None
    KaldiRecognizer = None

class StreamingSTTEngine:
    def __init__(self, model_dir: str, sample_rate: int):
        self.sample_rate = sample_rate
        self.enabled = False
        self._acc = bytearray()
        if Model and KaldiRecognizer:
            try:
                self.model = Model(model_dir)
                self.rec = KaldiRecognizer(self.model, sample_rate)
                self.enabled = True
            except Exception:
                self.model = None
                self.rec = None
                self.enabled = False
        else:
            self.model = None
            self.rec = None
            self.enabled = False

    def accept(self, pcm_s16le: bytes):
        if self.enabled and self.rec:
            ok = self.rec.AcceptWaveform(pcm_s16le)
            if ok:
                res = json.loads(self.rec.Result())
                txt = res.get("text", "").strip()
                return "", txt
            else:
                part = json.loads(self.rec.PartialResult()).get("partial", "").strip()
                return part, ""
        else:
            self._acc.extend(pcm_s16le)
            return "", ""

    def finalize(self):
        if self.enabled and self.rec:
            res = json.loads(self.rec.FinalResult())
            txt = res.get("text", "").strip()
            return txt
        return ""