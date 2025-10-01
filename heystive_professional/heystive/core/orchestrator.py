import os
def choose_stt():
    prefer = os.environ.get("HEYSTIVE_STT","auto")
    if prefer == "vosk": return "vosk"
    if prefer == "whisper": return "whisper"
    return "vosk"
def choose_tts():
    prefer = os.environ.get("HEYSTIVE_TTS","auto")
    if prefer == "pyttsx3": return "pyttsx3"
    return "pyttsx3"