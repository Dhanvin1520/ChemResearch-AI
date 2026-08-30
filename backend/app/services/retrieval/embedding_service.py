import numpy as np
from typing import Optional
from sentence_transformers import SentenceTransformer
from app.config import settings


class EmbeddingService:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embedding_model
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: list[str], batch_size: int = 32, show_progress: bool = False) -> np.ndarray:
        if not texts:
            return np.array([])

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embeddings

    def encode_query(self, query: str) -> np.ndarray:
        embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embedding[0]

    def get_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        return float(np.dot(embedding1, embedding2))

    def batch_similarity(self, query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
        return np.dot(doc_embeddings, query_embedding)
