from .model_llm import generate
SYSTEM = "You are a local offline assistant. Use short answers. If user requests files or knowledge, prefer local search."
def plan(user_text: str):
    prompt = f"User: {user_text}\nDecide one action: reply | memory.search | os.list. Respond as: ACTION: <action>\nQUERY: <optional>"
    out = generate(SYSTEM, prompt)
    return out