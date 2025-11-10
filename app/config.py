from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # RAG & LLM
    EMBEDDING_MODEL: str = Field("BAAI/bge-m3")
    # LLM (OpenAI-compatible; point to your vLLM server)
    OPENAI_API_KEY: str = Field("ollama")
    OPENAI_BASE_URL: str = Field("http://localhost:11434/v1")
    LLM_MODEL: str = Field("llama3.1")
    
    # Postgres
    PG_HOST: str = Field("localhost")
    PG_PORT: str = Field("5432")
    PG_USER: str = Field("rag")
    PG_PASSWORD: str = Field("ragpass")
    PG_DB: str = Field("expro_ai_dev_db")
    PG_SCHEMA: str = Field("rag") 
    # Cloud SQL (Postgres) via Connector
    INSTANCE_CONNECTION_NAME: str = Field('use your own', description="project:region:instance")
    ADC_FILE_PATH: str = Field("~/.config/gcloud/application_default_credentials.json")

    # Retrieval
    TOP_K: int = Field(6)
    # Server
    PORT: int = Field(8010)

    class Config:
        env_file = ".env"

settings = Settings()

