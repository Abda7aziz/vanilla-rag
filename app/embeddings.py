
from sentence_transformers import SentenceTransformer
import numpy as np
from .config import settings

_MODEL = None

# bge-m3 tip: normalize embeddings for cosine similarity
def get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _MODEL

def embed_documents(texts: list[str]) -> list[list[float]]:
    model = get_model()
    embs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return embs.tolist() if isinstance(embs, np.ndarray) else embs

def embed_query(query: str) -> list[float]:
    model = get_model()
    # bge-m3 generally works well without special prefixes; adjust if needed
    emb = model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
    return emb.tolist() if hasattr(emb, "tolist") else emb
