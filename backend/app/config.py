import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "ChemResearch AI"
    app_version: str = "1.0.0"
    debug: bool = Field(default=True)

    mongodb_uri: str = Field(
        default="mongodb://localhost:27017/"
    )
    mongodb_db_name: str = Field(default="chemresearch")

    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o-mini")

    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    reranker_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")

    faiss_index_path: str = Field(default="data/faiss_index")
    bm25_index_path: str = Field(default="data/bm25_index")
    upload_dir: str = Field(default="data/uploads")

    retrieval_top_k: int = Field(default=20)
    rerank_top_k: int = Field(default=8)
    chunk_size: int = Field(default=512)
    chunk_overlap: int = Field(default=50)

    semantic_weight: float = Field(default=0.6)
    keyword_weight: float = Field(default=0.4)

    cors_origins: list[str] = Field(default=["http://localhost:5173", "http://localhost:3000"])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()

os.makedirs(settings.faiss_index_path, exist_ok=True)
os.makedirs(settings.upload_dir, exist_ok=True)
