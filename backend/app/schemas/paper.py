from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PaperBase(BaseModel):
    title: str
    authors: Optional[list[str]] = None
    year: Optional[int] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    source: Optional[str] = None
    journal: Optional[str] = None
    keywords: Optional[list[str]] = None


class PaperCreate(PaperBase):
    full_text: Optional[str] = None
    chemical_entities: Optional[list[str]] = None
    reactions: Optional[list[str]] = None


class PaperResponse(PaperBase):
    id: int
    chemical_entities: Optional[list[str]] = None
    reactions: Optional[list[str]] = None
    chunk_count: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChunkBase(BaseModel):
    section: Optional[str] = None
    content: str
    chemical_entities: Optional[list[str]] = None
    reactions: Optional[list[str]] = None
    catalyst: Optional[str] = None
    solvent: Optional[str] = None
    temperature: Optional[str] = None
    yield_value: Optional[str] = None


class ChunkResponse(ChunkBase):
    id: int
    paper_id: int
    chunk_index: Optional[int] = None
    embedding_id: Optional[int] = None
    token_count: Optional[int] = None

    class Config:
        from_attributes = True


class PaperDetailResponse(PaperResponse):
    chunks: list[ChunkResponse] = []

    class Config:
        from_attributes = True


class PaperListResponse(BaseModel):
    papers: list[PaperResponse]
    total: int


class IngestRequest(BaseModel):
    title: Optional[str] = None
    doi: Optional[str] = None
    source: Optional[str] = None


class IngestResponse(BaseModel):
    paper_id: int
    title: str
    chunk_count: int
    chemical_entities: list[str]
    reactions: list[str]
    message: str
