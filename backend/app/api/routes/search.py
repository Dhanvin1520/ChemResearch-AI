import time
from fastapi import APIRouter, Depends, Request
from app.models.database import get_db
from app.schemas.query import SearchRequest, SearchResponse, Citation, Evidence, StructuredData
from app.services.agents.graph_builder import ResearchPipeline

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, req: Request, db=Depends(get_db)):
    pipeline = ResearchPipeline(
        embedding_service=getattr(req.app.state, "embedding_service", None),
        vector_store=getattr(req.app.state, "vector_store", None),
        bm25_search=getattr(req.app.state, "bm25_search", None),
        reranker=getattr(req.app.state, "reranker", None),
    )

    result = pipeline.run(
        question=request.question,
        db=db,
        max_results=request.max_results,
    )

    citations = [
        Citation(
            citation_id=c.get("citation_id", i + 1),
            paper_title=c.get("paper_title", "Unknown"),
            paper_id=c.get("paper_id", 0),
            section=c.get("section", ""),
            evidence_text=c.get("evidence_text", ""),
            doi=c.get("doi"),
            year=c.get("year"),
            relevance_score=c.get("relevance_score", 0.0),
        )
        for i, c in enumerate(result.get("citations", []))
    ]

    evidence_list = [
        Evidence(
            chunk_id=e.get("chunk_id", 0),
            paper_id=e.get("paper_id", 0),
            paper_title=e.get("paper_title", "Unknown"),
            section=e.get("section", ""),
            content=e.get("content", ""),
            catalyst=e.get("catalyst"),
            solvent=e.get("solvent"),
            temperature=e.get("temperature"),
            yield_value=e.get("yield_value"),
            relevance_score=e.get("relevance_score", 0.0),
            chemical_entities=e.get("chemical_entities", []),
        )
        for e in result.get("evidence", [])
    ]

    structured_data = [
        StructuredData(
            catalyst=s.get("catalyst"),
            solvent=s.get("solvent"),
            temperature=s.get("temperature"),
            yield_value=s.get("yield_value"),
            reaction=s.get("reaction"),
            conditions=s.get("conditions"),
            source_paper=s.get("source_paper"),
            source_section=s.get("source_section"),
        )
        for s in result.get("structured_data", [])
    ]

    query_log = {
        "question": request.question,
        "query_plan": result.get("query_plan"),
        "answer": result.get("answer", ""),
        "citations": [c.model_dump() for c in citations],
        "citation_score": result.get("citation_score", 0.0),
        "evidence_count": len(evidence_list),
        "processing_time_ms": result.get("processing_time_ms", 0),
        "model_used": result.get("query_plan", {}).get("query_type", "unknown"),
    }
    db.query_logs.insert_one(query_log)

    return SearchResponse(
        question=request.question,
        answer=result.get("answer", "No results found. Please ingest papers first."),
        citations=citations,
        evidence=evidence_list,
        structured_data=structured_data,
        citation_score=result.get("citation_score", 0.0),
        total_claims=result.get("total_claims", 0),
        supported_claims=result.get("supported_claims", 0),
        processing_time_ms=result.get("processing_time_ms", 0),
        query_plan=result.get("query_plan"),
        molecule_info=result.get("molecule_info"),
    )
