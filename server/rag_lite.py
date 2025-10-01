from pathlib import Path
from typing import List
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
router = APIRouter()
INDEX = {"files": [], "texts": [], "vecs": None, "model": None}
def load_corpus():
    base = Path("knowledge")
    files = []
    texts = []
    for p in base.rglob("*"):
        if p.suffix.lower() in [".txt",".md"]:
            try:
                t = p.read_text(encoding="utf-8")
            except:
                t = p.read_text(errors="ignore")
            files.append(str(p))
            texts.append(t)
    return files, texts
@router.post("/index")
def build_index():
    files, texts = load_corpus()
    if not texts:
        INDEX.update({"files": [], "texts": [], "vecs": None, "model": None})
        return {"ok": True, "count": 0}
    vec = TfidfVectorizer(max_features=20000)
    X = vec.fit_transform(texts)
    INDEX.update({"files": files, "texts": texts, "vecs": X, "model": vec})
    return {"ok": True, "count": len(files)}
@router.get("/search")
def search(q: str = Query(...), k: int = 5):
    if INDEX["vecs"] is None or INDEX["model"] is None:
        return JSONResponse(status_code=400, content={"ok": False, "error": "no_index"})
    qv = INDEX["model"].transform([q])
    sims = cosine_similarity(qv, INDEX["vecs"]).ravel()
    idx = sims.argsort()[::-1][:k]
    results = [{"file": INDEX["files"][i], "score": float(sims[i])} for i in idx]
    return {"ok": True, "results": results}