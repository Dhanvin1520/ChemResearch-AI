from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Citation(BaseModel):
    citation_id: int
    paper_title: str
    paper_id: int
    section: str
    evidence_text: str
    doi: Optional[str] = None
    year: Optional[int] = None
    relevance_score: float = 0.0


class Evidence(BaseModel):
    chunk_id: int
    paper_id: int
    paper_title: str
    section: str
    content: str
    catalyst: Optional[str] = None
    solvent: Optional[str] = None
    temperature: Optional[str] = None
    yield_value: Optional[str] = None
    relevance_score: float = 0.0
    chemical_entities: list[str] = []


class StructuredData(BaseModel):
    catalyst: Optional[str] = None
    solvent: Optional[str] = None
    temperature: Optional[str] = None
    yield_value: Optional[str] = None
    reaction: Optional[str] = None
    conditions: Optional[dict] = None
    source_paper: Optional[str] = None
    source_section: Optional[str] = None


class SearchRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000)
    max_results: int = Field(default=8, ge=1, le=20)
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    catalyst_filter: Optional[str] = None
    reaction_filter: Optional[str] = None


class SearchResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
    evidence: list[Evidence]
    structured_data: list[StructuredData]
    citation_score: float
    total_claims: int
    supported_claims: int
    processing_time_ms: int
    query_plan: Optional[dict] = None
    molecule_info: Optional[dict] = None


class QueryPlan(BaseModel):
    query_type: str
    target_molecules: list[str] = []
    target_reactions: list[str] = []
    conditions_of_interest: list[str] = []
    time_range: Optional[dict] = None
    search_keywords: list[str] = []
    requires_chemistry_tools: bool = False
    requires_literature_search: bool = True
