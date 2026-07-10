import time
import logfire
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sentence_transformers import SentenceTransformer
from app.config import settings
from typing import TYPE_CHECKING

BATCH_SIZE = 50
_GEMINI_DIM = 3072
_FALLBACK_DIM = 768

_active_model: GoogleGenerativeAIEmbeddings | SentenceTransformer  | None = None
_model_type: str | None = None # gemini or fallback

def _probe_gemini():
    """
    Try one embed call to verify Gemini is reachable. Returns model or None
    """
    try:
        model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2-preview",
            api_key=settings.GEMINI_API_KEY, # type: ignore
        )
        # Test call to verify connectivity
        model.embed_query("probetest")
        logfire.info("✅ Gemini embedding model is reachable (gemini-embedding-2-preview).")
        return model
    except Exception as e:
        logfire.warning(f"⚠️ Gemini probe failed, embedding model is not reachable: {e}. Will use sentence-transformers fallback.")
        return None
    
def _load_fallback():
    logfire.info("✅ Fallback embedding model loaded (all-mpnet-base-v2, 768 dim).")
    model = SentenceTransformer("all-mpnet-base-v2")
    return model

def _init():
    global _active_model, _model_type
    if _active_model is not None:
        return
    gemini = _probe_gemini()
    if gemini:
        _active_model = gemini
        _model_type = "gemini"
    else:
        _active_model = _load_fallback()
        _model_type = "fallback"

def get_embedding_dim():
    """
    Returns the vector dimension for the active embedding model. Call after _init().
    """
    _init()
    return _GEMINI_DIM if _model_type == "gemini" else _FALLBACK_DIM

def _embed_batch(batch: list[str]) -> list[list[float]]:
    if _active_model is None:
        raise RuntimeError("Embedding model is not initialized.")

    if _model_type == "gemini":
        for attempt in range(4):
            try:
                return _active_model.embed_documents(batch)  # type: ignore[attr-defined]
            except Exception as e:
                err = str(e).lower()
                is_rate_limit = any(x in err for x in ("429", "rate", "quota", "resource_exhausted"))
                if is_rate_limit and attempt < 3:
                    wait_time = 2 ** attempt
                    logfire.warning(f"⚠️ Gemini embedding rate limit hit, retrying in {wait_time}s (attempt {attempt + 1}/4).")
                    time.sleep(wait_time)
                else:
                    logfire.error(f"❌ Gemini embedding failed: {e}")
                    raise e
        raise RuntimeError("Gemini embedding failed after 4 attempts.")

    else:
        # Fallback model (sentence-transformers)
        assert isinstance(_active_model, SentenceTransformer)
        return _active_model.encode(batch, show_progress_bar=False).tolist()


def embed_query(query: str) -> list[float]:
    """
    Embeds a single query string using the active embedding model.
    """
    _init()
    if _model_type == "gemini":
        return _active_model.embed_query(query)  # type: ignore[attr-defined]
    else:
        assert isinstance(_active_model, SentenceTransformer)
        return _active_model.encode(query, show_progress_bar=False).tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embeds a list of texts using the active embedding model.
    """
    _init()
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        with logfire.span(f"🧩 Embedding batch {i // BATCH_SIZE + 1}/{(len(texts) + BATCH_SIZE - 1) // BATCH_SIZE}"):
            embeddings = _embed_batch(batch)
            all_embeddings.extend(embeddings)  
    return all_embeddings
