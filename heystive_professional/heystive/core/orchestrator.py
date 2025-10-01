import os
from server.settings_store import load
def choose_stt():
    s = load()
    return s.stt_engine
def choose_tts():
    s = load()
    return s.tts_engine
def choose_llm():
    s = load()
    return s.llm_engine
def model_path():
    s = load()
    return s.llm_model_path