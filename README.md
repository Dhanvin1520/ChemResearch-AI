# ChemResearch AI

**Autonomous chemical-literature intelligence.** Upload research papers, ask questions in natural language, and get **citation-grounded answers** — every claim is verified against the source before it reaches you.

ChemResearch AI is a full-stack, agentic RAG system built for scientific R&D. It ingests chemistry PDFs, retrieves the right evidence with a hybrid search stack, runs a multi-agent reasoning pipeline, and refuses to state anything it can't attribute to a source. It ships with a 50-item evaluation harness so answer quality is measured, not assumed.

---

## Why it's different

Most literature tools do embed-and-retrieve. ChemResearch AI adds the two things that actually matter for research use:

- **Citation verification / anti-hallucination** — a dedicated agent checks every claim in the generated answer against the retrieved evidence and flags unsupported statements, with a per-claim confidence score. No silent hallucinations.
- **Measured quality** — a built-in benchmark of 50 chemistry research questions scores retrieval (Recall@k, Precision@k, MAP, MRR, nDCG@k), extraction (entity precision/recall/F1), and answer faithfulness + citation accuracy.

---

## Architecture

**Retrieval — hybrid, then reranked**
- Semantic search (Sentence-Transformers `all-MiniLM-L6-v2` → FAISS)
- Keyword search (BM25) with catalyst / solvent / year filters
- Fused via **Reciprocal Rank Fusion**, then reranked with a cross-encoder (`ms-marco-MiniLM-L-6-v2`)

**Agentic reasoning pipeline**
```
Query Planner → Literature Agent → Chemistry Agent → Evidence Extractor → Reasoning Agent → Citation Verifier
```

**Chemistry engine (RDKit)**
- Molecule validation, property computation, functional-group detection, SVG rendering
- Reaction parsing and entity extraction (molecules, catalysts, solvents, conditions)

**Knowledge graph (MongoDB)**
- Links papers ↔ molecules ↔ reactions ↔ conditions; surfaces co-mentioned compounds and relationships

**Ingestion**
- PDF parsing with chemistry-aware chunking that avoids splitting mid-reaction

**Stack**
- Backend: FastAPI, MongoDB, LangGraph, LangChain
- ML: Sentence-Transformers, FAISS, cross-encoder reranking
- Chemistry: RDKit
- Frontend: React, TypeScript, Vite

---

## Running locally

### Docker Compose
```bash
docker-compose up --build
```
Frontend: http://localhost:5173 · API: http://localhost:8000 · API docs: http://localhost:8000/docs

### Native
**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=...   # optional: enables LLM reasoning + LLM-based citation verification
uvicorn app.main:app --reload
```
Requires a running MongoDB (default `mongodb://localhost:27017/`). Without an API key the system falls back to heuristic reasoning and citation checks, so it runs end-to-end offline.

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## Configuration

Key settings (`backend/app/config.py`, overridable via `.env`):

| Setting | Default | Purpose |
|---|---|---|
| `retrieval_top_k` | 20 | Candidates pulled before reranking |
| `rerank_top_k` | 8 | Passages kept after cross-encoder |
| `semantic_weight` / `keyword_weight` | 0.6 / 0.4 | Hybrid fusion balance |
| `chunk_size` / `chunk_overlap` | 512 / 50 | Ingestion chunking |
| `embedding_model` | `all-MiniLM-L6-v2` | Dense retrieval |
| `reranker_model` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Reranking |

---

## Using it

1. **Papers** — upload PDF research papers to ingest them.
2. **Research** — ask a chemistry question; get a cited answer with an evidence panel.
3. **Evaluation** — run the 50-question benchmark and view retrieval / extraction / faithfulness metrics.
4. **Graph** — explore the molecule–reaction–paper knowledge network.
