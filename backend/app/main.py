from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.database import Database
from app.api.routes import search, papers, chemistry, graph, evaluation


@asynccontextmanager
async def lifespan(app: FastAPI):
    Database.connect_db()
    from app.services.retrieval.embedding_service import EmbeddingService
    from app.services.retrieval.vector_store import VectorStore
    from app.services.retrieval.bm25_search import BM25Search
    from app.services.retrieval.reranker import Reranker
    from app.services.ingestion.seed_data import seed_default_papers

    app.state.embedding_service = EmbeddingService()
    app.state.vector_store = VectorStore()
    app.state.bm25_search = BM25Search()
    app.state.reranker = Reranker()

    db = Database.get_db()
    seed_default_papers(
        db,
        embedding_service=app.state.embedding_service,
        vector_store=app.state.vector_store,
        bm25_search=app.state.bm25_search,
    )

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Autonomous Chemical Literature Intelligence & Research Assistant",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(papers.router, prefix="/api/papers", tags=["Papers"])
app.include_router(chemistry.router, prefix="/api/chemistry", tags=["Chemistry"])
app.include_router(graph.router, prefix="/api/graph", tags=["Graph"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["Evaluation"])


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "endpoints": {
            "search": "/api/search",
            "papers": "/api/papers",
            "chemistry": "/api/chemistry",
            "graph": "/api/graph",
            "evaluation": "/api/evaluation",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}
