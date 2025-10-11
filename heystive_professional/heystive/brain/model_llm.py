from llama_cpp import Llama
from pathlib import Path
from ..core.orchestrator import choose_stt, choose_tts
from server.settings_store import load
LLM_SINGLETON = {"llm": None, "path": None}
def get_llm():
    s = load()
    p = s.llm_model_path
    if LLM_SINGLETON["llm"] is None or LLM_SINGLETON["path"] != p:
        LLM_SINGLETON["llm"] = Llama(model_path=p, n_threads=4)
        LLM_SINGLETON["path"] = p
    return LLM_SINGLETON["llm"]
def generate(system: str, user: str):
    llm = get_llm()
    prompt = f"<|system|>\n{system}\n<|user|>\n{user}\n<|assistant|>\n"
    out = llm(prompt, max_tokens=256, stop=["<|user|>","<|system|>"])
    txt = out["choices"][0]["text"]
    return txt.strip()