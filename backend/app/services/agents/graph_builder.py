import time
from typing import Optional, TypedDict, Annotated
from sqlalchemy.orm import Session
from app.config import settings
from app.services.agents.query_planner import query_planner
from app.services.agents.literature_agent import LiteratureAgent
from app.services.agents.chemistry_agent import chemistry_agent
from app.services.agents.evidence_extractor import evidence_extractor
from app.services.agents.reasoning_agent import reasoning_agent
from app.services.agents.citation_verifier import citation_verifier
from app.services.retrieval.hybrid_retriever import HybridRetriever
from app.services.retrieval.reranker import Reranker


class ResearchState(TypedDict, total=False):
    question: str
    query_plan: dict
    retrieved_chunks: list
    chemical_info: dict
    evidence: list
    answer: str
    citations: list
    citation_score: float
    total_claims: int
    supported_claims: int
    structured_data: list
    molecule_info: dict
    processing_time_ms: int
    error: Optional[str]


class ResearchPipeline:
    def __init__(
        self,
        embedding_service=None,
        vector_store=None,
        bm25_search=None,
        reranker=None,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.bm25_search = bm25_search
        self.reranker_instance = reranker

    def run(self, question: str, db: Session, max_results: int = 8) -> dict:
        start_time = time.time()
        state: ResearchState = {"question": question}

        state = self._plan_query(state)
        if state.get("error"):
            return state

        state = self._search_literature(state, db, max_results)

        if state["query_plan"].get("requires_chemistry_tools", False):
            state = self._run_chemistry(state)

        state = self._extract_evidence(state)

        state = self._reason(state)

        state = self._verify_citations(state)

        elapsed_ms = int((time.time() - start_time) * 1000)
        state["processing_time_ms"] = elapsed_ms

        return state

    def _plan_query(self, state: ResearchState) -> ResearchState:
        plan = query_planner.plan(state["question"])
        state["query_plan"] = plan
        return state

    def _search_literature(self, state: ResearchState, db: Session, max_results: int) -> ResearchState:
        hybrid_retriever = HybridRetriever(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
            bm25_search=self.bm25_search,
        )

        lit_agent = LiteratureAgent(
            hybrid_retriever=hybrid_retriever,
            reranker=self.reranker_instance,
        )

        results = lit_agent.search(
            query=state["question"],
            query_plan=state["query_plan"],
            db=db,
            top_k=max_results,
        )

        state["retrieved_chunks"] = results
        return state

    def _run_chemistry(self, state: ResearchState) -> ResearchState:
        chem_result = chemistry_agent.process(state["query_plan"])
        state["chemical_info"] = chem_result

        molecule_info = {}
        for name, info in chem_result.get("molecules", {}).items():
            if info:
                molecule_info[name] = {
                    "smiles": info.get("smiles"),
                    "formula": info.get("molecular_formula"),
                    "molecular_weight": info.get("molecular_weight"),
                    "functional_groups": info.get("functional_groups", []),
                    "svg": info.get("svg"),
                }
        state["molecule_info"] = molecule_info
        return state

    def _extract_evidence(self, state: ResearchState) -> ResearchState:
        evidence = evidence_extractor.extract(
            state.get("retrieved_chunks", []),
            state["query_plan"],
        )
        state["evidence"] = evidence

        structured_data = []
        for ev in evidence:
            if any([ev.get("catalyst"), ev.get("solvent"), ev.get("temperature"), ev.get("yield_value")]):
                structured_data.append({
                    "catalyst": ev.get("catalyst"),
                    "solvent": ev.get("solvent"),
                    "temperature": ev.get("temperature"),
                    "yield_value": ev.get("yield_value"),
                    "reaction": ", ".join(ev.get("reactions", [])) if ev.get("reactions") else None,
                    "conditions": {
                        "reaction_time": ev.get("reaction_time"),
                        "pressure": ev.get("pressure"),
                    },
                    "source_paper": ev.get("paper_title"),
                    "source_section": ev.get("section"),
                })
        state["structured_data"] = structured_data
        return state

    def _reason(self, state: ResearchState) -> ResearchState:
        result = reasoning_agent.reason(
            question=state["question"],
            evidence=state.get("evidence", []),
            query_plan=state["query_plan"],
            chemistry_info=state.get("chemical_info"),
        )

        state["answer"] = result["answer"]
        state["citations"] = result["citations"]
        return state

    def _verify_citations(self, state: ResearchState) -> ResearchState:
        verification = citation_verifier.verify(
            answer=state.get("answer", ""),
            evidence=state.get("evidence", []),
            citations=state.get("citations", []),
        )

        state["answer"] = verification.get("verified_answer", state.get("answer", ""))
        state["citation_score"] = verification.get("citation_score", 0.0)
        state["total_claims"] = verification.get("total_claims", 0)
        state["supported_claims"] = verification.get("supported_claims", 0)
        return state
