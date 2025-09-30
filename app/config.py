# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    # Embeddings / RAG
    EMBEDDING_MODEL: str = Field("BAAI/bge-m3")
    # Vector Backend
    VECTOR_BACKEND: str = Field("postgres")  # default

    # LLM (OpenAI-compatible; e.g., vLLM)
    OPENAI_API_KEY: str = Field("EMPTY")
    OPENAI_BASE_URL: str = Field("http://localhost:8005/v1")
    LLM_MODEL: str = Field("openai/gpt-oss-120b")

    # Retrieval
    TOP_K: int = Field(6)
    PORT: int = Field(8000)

    # ▶️ NEW: Postgres + pgvector
    PG_HOST: str = Field("localhost")
    PG_PORT: int = Field(5432)
    PG_USER: str = Field("rag")
    PG_PASSWORD: str = Field("ragpass")
    PG_DB: str = Field("ragdb")

    class Config:
        env_file = ".env"

settings = Settings()