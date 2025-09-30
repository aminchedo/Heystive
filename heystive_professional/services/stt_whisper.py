import os, base64, io
try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None
import soundfile as sf
_model = None
def _ensure(model_dir: str):
    global _model
    if _model is None and WhisperModel is not None:
        try:
            _model = WhisperModel(model_dir, device="cpu", compute_type="int8")
        except Exception:
            _model = None
    return _model
def stt_wav_base64_whisper(audio_b64: str, model_dir: str):
    if _ensure(model_dir) is None:
        raise RuntimeError("whisper_unavailable")
    raw = base64.b64decode(audio_b64)
    data, sr = sf.read(io.BytesIO(raw), dtype="float32")
    segments, _ = _model.transcribe(data, language=None)
    txt = " ".join([s.text for s in segments]).strip()
    return txt