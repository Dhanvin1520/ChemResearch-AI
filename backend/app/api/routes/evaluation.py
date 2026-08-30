from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.models.database import get_db

router = APIRouter()


@router.post("/run")
async def run_evaluation(req: Request, db: Session = Depends(get_db)):
    from app.services.evaluation.benchmark import BenchmarkRunner

    runner = BenchmarkRunner(
        embedding_service=getattr(req.app.state, "embedding_service", None),
        vector_store=getattr(req.app.state, "vector_store", None),
        bm25_search=getattr(req.app.state, "bm25_search", None),
        reranker=getattr(req.app.state, "reranker", None),
    )

    results = runner.run(db)
    return results


@router.get("/results")
async def get_results():
    from app.services.evaluation.benchmark import BenchmarkRunner
    runner = BenchmarkRunner()
    return runner.get_latest_results()


@router.get("/metrics")
async def get_metric_definitions():
    return {
        "retrieval": {
            "recall_at_k": "Fraction of relevant documents retrieved in top K results",
            "precision_at_k": "Fraction of retrieved documents that are relevant",
        },
        "reranking": {
            "mrr": "Mean Reciprocal Rank — average of 1/rank of first relevant result",
            "ndcg": "Normalized Discounted Cumulative Gain — quality of ranking",
        },
        "extraction": {
            "precision": "Fraction of extracted entities that are correct",
            "recall": "Fraction of expected entities that were extracted",
            "f1": "Harmonic mean of precision and recall",
        },
        "answer": {
            "faithfulness": "Fraction of answer claims supported by evidence",
        },
        "citation": {
            "accuracy": "Fraction of citations that correctly support their claims",
        },
    }
