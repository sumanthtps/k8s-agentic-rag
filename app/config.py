import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Groq Reasoning Engine (Llama 3.3)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME = "llama-3.3"
    GROQ_FALLBACK_API_KEY = os.getenv("GROQ_FALLBACK_API_KEY")

    # Portkey LLM Gateway
    PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")

    # Qdrant Vector DB Settings 
    QDRANT_URL = os.getenv("QDRANT_CLUSTER_ENDPOINT")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME = "prod-rag"

    # === Observability
    JUDGE_GROQ = os.getenv("JUDGE_GROQ")

    # === Gemini API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

settings = Settings()