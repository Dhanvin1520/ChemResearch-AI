import json
import os
import time
from typing import Optional
from pathlib import Path
from sqlalchemy.orm import Session
from app.services.agents.graph_builder import ResearchPipeline
from app.services.evaluation.metrics import (
    entity_precision_recall_f1,
    faithfulness_score,
    citation_accuracy,
    aggregate_metrics,
)
from app.config import settings, DATA_DIR


class BenchmarkRunner:
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
        self.reranker = reranker
        self.results_dir = DATA_DIR / "evaluation_results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def load_benchmark_data(self) -> list[dict]:
        benchmark_path = Path(__file__).parent / "benchmark_data.json"
        with open(benchmark_path, "r") as f:
            return json.load(f)

    def run(self, db: Session) -> dict:
        benchmark_data = self.load_benchmark_data()
        pipeline = ResearchPipeline(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
            bm25_search=self.bm25_search,
            reranker=self.reranker,
        )

        all_results = []
        total_start = time.time()

        for item in benchmark_data:
            question = item["question"]
            expected = item.get("expected_entities", {})

            result = pipeline.run(question=question, db=db)

            extracted_catalysts = []
            extracted_solvents = []
            extracted_molecules = []
            extracted_reactions = []

            for ev in result.get("evidence", []):
                if ev.get("catalyst"):
                    extracted_catalysts.append(ev["catalyst"])
                if ev.get("solvent"):
                    extracted_solvents.append(ev["solvent"])
                extracted_molecules.extend(ev.get("chemical_entities", []))
                extracted_reactions.extend(ev.get("reactions", []))

            catalyst_metrics = entity_precision_recall_f1(
                extracted_catalysts,
                expected.get("catalysts", []),
            )
            solvent_metrics = entity_precision_recall_f1(
                extracted_solvents,
                expected.get("solvents", []),
            )
            molecule_metrics = entity_precision_recall_f1(
                extracted_molecules,
                expected.get("molecules", []),
            )
            reaction_metrics = entity_precision_recall_f1(
                extracted_reactions,
                expected.get("reactions", []),
            )

            verification = result.get("citation_score", 0.0)
            citation_acc = citation_accuracy(
                result.get("citations", []),
                result.get("evidence", []),
            )

            question_result = {
                "question_id": item["id"],
                "question": question,
                "catalyst_f1": catalyst_metrics["f1"],
                "solvent_f1": solvent_metrics["f1"],
                "molecule_f1": molecule_metrics["f1"],
                "reaction_f1": reaction_metrics["f1"],
                "citation_score": verification,
                "citation_accuracy": citation_acc,
                "evidence_count": len(result.get("evidence", [])),
                "processing_time_ms": result.get("processing_time_ms", 0),
                "has_answer": bool(result.get("answer")),
            }

            all_results.append(question_result)

        total_time = time.time() - total_start

        aggregated = aggregate_metrics(all_results)

        summary = {
            "total_questions": len(all_results),
            "total_time_seconds": round(total_time, 2),
            "avg_time_per_question_ms": round(total_time * 1000 / len(all_results), 2) if all_results else 0,
            "metrics": aggregated,
            "individual_results": all_results,
        }

        results_file = self.results_dir / f"benchmark_{int(time.time())}.json"
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2)

        return summary

    def get_latest_results(self) -> dict:
        if not self.results_dir.exists():
            return {"message": "No evaluation results found. Run a benchmark first."}

        result_files = sorted(self.results_dir.glob("benchmark_*.json"), reverse=True)
        if not result_files:
            return {"message": "No evaluation results found. Run a benchmark first."}

        with open(result_files[0], "r") as f:
            return json.load(f)
