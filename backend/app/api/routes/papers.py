import os
import tempfile
from fastapi import APIRouter, Depends, Request, UploadFile, File, Form, HTTPException
from app.models.database import get_db
from app.schemas.paper import (
    PaperResponse,
    PaperDetailResponse,
    PaperListResponse,
    ChunkResponse,
    IngestRequest,
    IngestResponse,
)
from app.services.ingestion.pipeline import ingestion_pipeline

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_paper(
    req: Request,
    file: UploadFile = File(None),
    text_content: str = Form(None),
    title: str = Form(None),
    doi: str = Form(None),
    source: str = Form(None),
    db=Depends(get_db),
):
    embedding_service = getattr(req.app.state, "embedding_service", None)
    vector_store = getattr(req.app.state, "vector_store", None)
    bm25_search = getattr(req.app.state, "bm25_search", None)

    if file and file.filename:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            result = ingestion_pipeline.ingest_pdf(
                filepath=tmp_path,
                db=db,
                embedding_service=embedding_service,
                vector_store=vector_store,
                bm25_search=bm25_search,
                title_override=title,
                doi_override=doi,
                source=source,
            )
        finally:
            os.unlink(tmp_path)

    elif text_content:
        result = ingestion_pipeline.ingest_text(
            text=text_content,
            db=db,
            title=title or "Untitled",
            doi=doi,
            source=source,
            embedding_service=embedding_service,
            vector_store=vector_store,
            bm25_search=bm25_search,
        )
    else:
        raise HTTPException(status_code=400, detail="Either file or text_content must be provided")

    return IngestResponse(
        paper_id=result["paper_id"],
        title=result["title"],
        chunk_count=result["chunk_count"],
        chemical_entities=result.get("chemical_entities", []),
        reactions=result.get("reactions", []),
        message=f"Successfully ingested paper with {result['chunk_count']} chunks",
    )


@router.get("", response_model=PaperListResponse)
async def list_papers(
    skip: int = 0,
    limit: int = 20,
    year: int = None,
    search: str = None,
    db=Depends(get_db),
):
    query = {}
    if year:
        query["year"] = year
    if search:
        query["title"] = {"$regex": search, "$options": "i"}

    total = db.papers.count_documents(query)
    papers_cursor = db.papers.find(query).sort("created_at", -1).skip(skip).limit(limit)

    paper_responses = []
    for paper in papers_cursor:
        chunk_count = db.chunks.count_documents({"paper_id": paper["id"]})
        paper_responses.append(
            PaperResponse(
                id=paper["id"],
                title=paper["title"],
                authors=paper.get("authors"),
                year=paper.get("year"),
                abstract=paper.get("abstract"),
                doi=paper.get("doi"),
                source=paper.get("source"),
                journal=paper.get("journal"),
                keywords=paper.get("keywords"),
                chemical_entities=paper.get("chemical_entities"),
                reactions=paper.get("reactions"),
                chunk_count=chunk_count,
                created_at=paper.get("created_at"),
            )
        )

    return PaperListResponse(papers=paper_responses, total=total)


@router.get("/{paper_id}", response_model=PaperDetailResponse)
async def get_paper(paper_id: int, db=Depends(get_db)):
    paper = db.papers.find_one({"id": paper_id})
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    chunks_cursor = db.chunks.find({"paper_id": paper_id}).sort("chunk_index", 1)

    chunk_responses = [
        ChunkResponse(
            id=chunk["id"],
            paper_id=chunk["paper_id"],
            section=chunk.get("section"),
            content=chunk["content"],
            chunk_index=chunk.get("chunk_index"),
            chemical_entities=chunk.get("chemical_entities"),
            reactions=chunk.get("reactions"),
            catalyst=chunk.get("catalyst"),
            solvent=chunk.get("solvent"),
            temperature=chunk.get("temperature"),
            yield_value=chunk.get("yield_value"),
            embedding_id=chunk.get("embedding_id"),
            token_count=chunk.get("token_count"),
        )
        for chunk in chunks_cursor
    ]

    return PaperDetailResponse(
        id=paper["id"],
        title=paper["title"],
        authors=paper.get("authors"),
        year=paper.get("year"),
        abstract=paper.get("abstract"),
        doi=paper.get("doi"),
        source=paper.get("source"),
        journal=paper.get("journal"),
        keywords=paper.get("keywords"),
        chemical_entities=paper.get("chemical_entities"),
        reactions=paper.get("reactions"),
        chunk_count=len(chunk_responses),
        created_at=paper.get("created_at"),
        chunks=chunk_responses,
    )


@router.delete("/{paper_id}")
async def delete_paper(paper_id: int, req: Request, db=Depends(get_db)):
    paper = db.papers.find_one({"id": paper_id})
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    chunks = list(db.chunks.find({"paper_id": paper_id}))
    chunk_ids = [c["id"] for c in chunks]

    vector_store = getattr(req.app.state, "vector_store", None)
    if vector_store and chunk_ids:
        vector_store.remove_embeddings(chunk_ids)

    bm25_search = getattr(req.app.state, "bm25_search", None)
    if bm25_search:
        for chunk_id in chunk_ids:
            bm25_search.remove_document(chunk_id)

    db.papers.delete_one({"id": paper_id})
    db.chunks.delete_many({"paper_id": paper_id})

    return {"message": f"Paper '{paper['title']}' deleted successfully", "chunks_removed": len(chunk_ids)}
