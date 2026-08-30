from fastapi import APIRouter, HTTPException
from app.services.graph.knowledge_graph import knowledge_graph

router = APIRouter()


@router.get("/status")
async def graph_status():
    stats = knowledge_graph.get_graph_stats()
    return {
        "connected": True,
        "stats": stats,
    }


@router.get("/reactions")
async def get_reactions(catalyst: str = None, molecule: str = None):
    if catalyst:
        results = knowledge_graph.find_reactions_by_catalyst(catalyst)
    elif molecule:
        results = knowledge_graph.find_reactions_for_molecule(molecule)
    else:
        results = []

    return {"reactions": results}


@router.get("/molecules/{name}")
async def get_molecule_context(name: str):
    context = knowledge_graph.get_molecule_context(name)
    return context


@router.get("/stats")
async def get_graph_stats():
    stats = knowledge_graph.get_graph_stats()
    return {
        "connected": True,
        **stats,
    }


@router.post("/initialize")
async def initialize_graph():
    knowledge_graph.initialize_schema()
    return {"message": "Graph schema initialized successfully"}
