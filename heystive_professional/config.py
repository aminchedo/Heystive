import os

class Settings:
    def __init__(self):
        self.vosk_model_dir = os.environ.get("VOSK_MODEL_DIR", "models/vosk-fa")
        self.tts_tmp_dir = os.environ.get("TTS_TMP_DIR", "/tmp")

settings = Settings()