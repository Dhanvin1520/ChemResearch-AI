# ChemResearch AI

Autonomous Chemical Literature Intelligence & Research Assistant.

## Overview
ChemResearch AI is a full-stack application that helps researchers investigate chemistry questions by searching scientific literature, retrieving relevant evidence, extracting structured chemical information, and generating citation-grounded answers.

## Architecture
- **Backend:** FastAPI, SQLAlchemy (PostgreSQL), Neo4j driver
- **Machine Learning:** Sentence-Transformers (FAISS), Cross-Encoders, LangChain (OpenAI)
- **Chemistry Engine:** RDKit (Molecules, Properties, SVG generation, Reactions)
- **Frontend:** React, TypeScript, Vite, custom premium dark theme CSS

## Features
1. **Literature Ingestion Pipeline:** Processes PDFs into semantic chunks, avoiding mid-reaction splits.
2. **Hybrid Search Architecture:** FAISS Semantic Search + BM25 Keyword Search + Cross-Encoder Reranking.
3. **Agentic Workflow (LangGraph):** Planner -> Literature Agent -> Chemistry Agent -> Evidence Extractor -> Reasoning Agent -> Citation Verifier.
4. **Chemistry Toolkit:** RDKit-powered molecule validation, property computation, functional group detection, and SVG rendering.
5. **Knowledge Graph (Neo4j):** Tracks relationships between papers, molecules, reactions, and conditions.
6. **Built-in Evaluation:** 50 chemistry research benchmarks to evaluate extraction F1, citation accuracy, and retrieval metrics.

## Running Locally

### Using Docker Compose
```bash
docker-compose up --build
```
The frontend will be available at http://localhost:5173, the backend API at http://localhost:8000.

### Native Development
1. **Database:** Ensure PostgreSQL (port 5432) and Neo4j (port 7687) are running.
2. **Backend:** 
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   # Set OPENAI_API_KEY environment variable for LLM features
   uvicorn app.main:app --reload
   ```
3. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Workflow Guide
1. Go to the "Papers" tab and upload PDF research papers.
2. Go to the "Research" tab and ask chemistry questions.
3. Use the "Evaluation" tab to run benchmarks.
4. Check the "Graph" tab to see the Neo4j knowledge network.
