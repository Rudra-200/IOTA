import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Legal RAG API"
    VERSION: str = "1.0.0"
    
    # Model Config
    GEMINI_API_KEY: str  # Required! App will fail if missing
    EMBEDDING_MODEL: str = "jinaai/jina-embeddings-v2-base-en"
    
    # Paths (Defaults work for Docker)
    ARTIFACT_DIR: str = "./artifacts"
    DB_PATH: str = "./artifacts/chunks.db"
    INDEX_PATH: str = "./artifacts/faiss_index.bin"
    CACHE_PATH: str = "./artifacts/statute_cache.json"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()