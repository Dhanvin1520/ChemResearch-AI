from typing import Optional
from sentence_transformers import CrossEncoder
from app.config import settings


class Reranker:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.reranker_model
        self._model = None

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = settings.rerank_top_k,
        content_key: str = "content",
    ) -> list[dict]:
        if not documents:
            return []

        pairs = [(query, doc[content_key]) for doc in documents]
        scores = self.model.predict(pairs)

        for i, doc in enumerate(documents):
            doc["rerank_score"] = float(scores[i])

        ranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
        return ranked[:top_k]

    def score_pair(self, query: str, document: str) -> float:
        return float(self.model.predict([(query, document)])[0])

    def batch_score(self, query: str, documents: list[str]) -> list[float]:
        if not documents:
            return []

        pairs = [(query, doc) for doc in documents]
        scores = self.model.predict(pairs)
        return [float(s) for s in scores]
