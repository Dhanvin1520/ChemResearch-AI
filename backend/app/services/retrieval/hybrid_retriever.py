from typing import Optional
from app.config import settings
from app.services.retrieval.vector_store import VectorStore
from app.services.retrieval.bm25_search import BM25Search
from app.services.retrieval.embedding_service import EmbeddingService


class HybridRetriever:
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStore] = None,
        bm25_search: Optional[BM25Search] = None,
        semantic_weight: float = settings.semantic_weight,
        keyword_weight: float = settings.keyword_weight,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.bm25_search = bm25_search
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight

    def search(
        self,
        query: str,
        top_k: int = settings.retrieval_top_k,
        catalyst_filter: Optional[str] = None,
        solvent_filter: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> list[dict]:
        semantic_results = []
        if self.embedding_service and self.vector_store:
            query_embedding = self.embedding_service.encode_query(query)
            semantic_results = self.vector_store.search(query_embedding, top_k=top_k * 2)

        keyword_results = []
        if self.bm25_search:
            keyword_results = self.bm25_search.search_with_filters(
                query,
                top_k=top_k * 2,
                catalyst=catalyst_filter,
                solvent=solvent_filter,
                year_from=year_from,
                year_to=year_to,
            )

        fused = self._reciprocal_rank_fusion(semantic_results, keyword_results, top_k)
        return fused

    def _reciprocal_rank_fusion(
        self,
        semantic_results: list[dict],
        keyword_results: list[dict],
        top_k: int,
        k: int = 60,
    ) -> list[dict]:
        scores = {}
        sources = {}

        for rank, result in enumerate(semantic_results):
            chunk_id = result["chunk_id"]
            rrf_score = self.semantic_weight * (1.0 / (k + rank + 1))
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            if chunk_id not in sources:
                sources[chunk_id] = {"semantic_score": result["score"], "keyword_score": 0.0}
            else:
                sources[chunk_id]["semantic_score"] = result["score"]

        for rank, result in enumerate(keyword_results):
            chunk_id = result["chunk_id"]
            rrf_score = self.keyword_weight * (1.0 / (k + rank + 1))
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            if chunk_id not in sources:
                sources[chunk_id] = {"semantic_score": 0.0, "keyword_score": result["score"]}
            else:
                sources[chunk_id]["keyword_score"] = result["score"]

        sorted_chunks = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        for chunk_id, rrf_score in sorted_chunks[:top_k]:
            source_info = sources.get(chunk_id, {})
            result = {
                "chunk_id": chunk_id,
                "score": rrf_score,
                "semantic_score": source_info.get("semantic_score", 0.0),
                "keyword_score": source_info.get("keyword_score", 0.0),
                "source": "hybrid",
            }

            if source_info.get("semantic_score", 0) > 0 and source_info.get("keyword_score", 0) > 0:
                result["source"] = "both"
            elif source_info.get("semantic_score", 0) > 0:
                result["source"] = "semantic"
            elif source_info.get("keyword_score", 0) > 0:
                result["source"] = "keyword"

            results.append(result)

        return results
