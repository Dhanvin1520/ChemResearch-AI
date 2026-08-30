from typing import Optional

from app.services.retrieval.hybrid_retriever import HybridRetriever
from app.services.retrieval.reranker import Reranker
from app.config import settings


class LiteratureAgent:
    def __init__(
        self,
        hybrid_retriever: Optional[HybridRetriever] = None,
        reranker: Optional[Reranker] = None,
    ):
        self.hybrid_retriever = hybrid_retriever
        self.reranker = reranker

    def search(
        self,
        query: str,
        query_plan: dict,
        db,
        top_k: int = settings.rerank_top_k,
    ) -> list[dict]:
        search_query = self._build_search_query(query, query_plan)

        catalyst_filter = None
        solvent_filter = None
        year_from = None
        year_to = None

        if "conditions_of_interest" in query_plan:
            from app.services.chemistry.entity_extractor import entity_extractor
            conditions = entity_extractor.extract_experimental_conditions(query)
            catalyst_filter = conditions.get("catalyst")
            solvent_filter = conditions.get("solvent")

        if query_plan.get("time_range"):
            year_from = query_plan["time_range"].get("from")
            year_to = query_plan["time_range"].get("to")

        retrieval_results = []
        if self.hybrid_retriever:
            retrieval_results = self.hybrid_retriever.search(
                search_query,
                top_k=settings.retrieval_top_k,
                catalyst_filter=catalyst_filter,
                solvent_filter=solvent_filter,
                year_from=year_from,
                year_to=year_to,
            )

        chunk_ids = [r["chunk_id"] for r in retrieval_results]
        if not chunk_ids:
            return []

        chunks = list(db.chunks.find({"$or": [{"id": {"$in": chunk_ids}}, {"chunk_id": {"$in": chunk_ids}}]}))
        chunk_map = {}
        for c in chunks:
            cid = c.get("id", c.get("chunk_id"))
            if cid is not None:
                chunk_map[cid] = c

        paper_ids = list(set(c.get("paper_id") for c in chunks if c.get("paper_id") is not None))
        papers = list(db.papers.find({"$or": [{"id": {"$in": paper_ids}}, {"paper_id": {"$in": paper_ids}}]}))
        paper_map = {}
        for p in papers:
            pid = p.get("id", p.get("paper_id"))
            if pid is not None:
                paper_map[pid] = p

        enriched_results = []
        for result in retrieval_results:
            chunk_id = result["chunk_id"]
            chunk = chunk_map.get(chunk_id)
            if not chunk:
                continue

            pid = chunk.get("paper_id")
            paper = paper_map.get(pid)
            if not paper:
                continue

            if year_from and paper.get("year") and paper["year"] < year_from:
                continue
            if year_to and paper.get("year") and paper["year"] > year_to:
                continue

            enriched_results.append({
                "chunk_id": chunk.get("id", chunk.get("chunk_id", chunk_id)),
                "paper_id": paper.get("id", paper.get("paper_id", pid)),
                "paper_title": paper.get("title"),
                "paper_year": paper.get("year"),
                "paper_doi": paper.get("doi"),
                "paper_authors": paper.get("authors", []),
                "section": chunk.get("section"),
                "content": chunk.get("content"),
                "catalyst": chunk.get("catalyst"),
                "solvent": chunk.get("solvent"),
                "temperature": chunk.get("temperature"),
                "yield_value": chunk.get("yield_value"),
                "chemical_entities": chunk.get("chemical_entities", []),
                "reactions": chunk.get("reactions", []),
                "retrieval_score": result["score"],
                "semantic_score": result.get("semantic_score", 0),
                "keyword_score": result.get("keyword_score", 0),
                "source": result.get("source", "hybrid"),
            })

        if self.reranker and enriched_results:
            enriched_results = self.reranker.rerank(
                query,
                enriched_results,
                top_k=top_k,
                content_key="content",
            )

        return enriched_results

    def _build_search_query(self, query: str, query_plan: dict) -> str:
        parts = [query]

        if query_plan.get("target_molecules"):
            parts.extend(query_plan["target_molecules"][:3])

        if query_plan.get("target_reactions"):
            parts.extend(query_plan["target_reactions"][:2])

        return " ".join(parts)


literature_agent = LiteratureAgent()
