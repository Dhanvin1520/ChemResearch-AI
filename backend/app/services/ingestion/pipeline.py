import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from app.config import settings
from app.services.ingestion.pdf_processor import pdf_processor
from app.services.ingestion.paper_parser import paper_parser
from app.services.ingestion.chunker import chunker


def get_next_sequence_value(db, sequence_name):
    seq = db.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return seq["sequence_value"]


class IngestionPipeline:
    def __init__(self):
        self.upload_dir = settings.upload_dir

    def ingest_pdf(
        self,
        filepath: str,
        db,
        embedding_service=None,
        vector_store=None,
        bm25_search=None,
        title_override: Optional[str] = None,
        doi_override: Optional[str] = None,
        source: Optional[str] = None,
    ) -> dict:
        full_text = pdf_processor.extract_text(filepath)
        if not full_text:
            raise ValueError(f"Could not extract text from {filepath}")

        sections = pdf_processor.parse_sections(full_text)
        tables = pdf_processor.extract_tables(filepath)
        metadata = paper_parser.extract_metadata(full_text, filename=os.path.basename(filepath))

        if title_override:
            metadata["title"] = title_override
        if doi_override:
            metadata["doi"] = doi_override

        stored_path = self._store_file(filepath)

        paper_id = get_next_sequence_value(db, "paper_id")

        paper = {
            "id": paper_id,
            "title": metadata["title"],
            "authors": metadata["authors"],
            "year": metadata["year"],
            "abstract": metadata["abstract"],
            "doi": metadata["doi"],
            "source": source or "uploaded",
            "filepath": stored_path,
            "journal": metadata["journal"],
            "keywords": metadata["keywords"],
            "full_text": full_text,
            "created_at": datetime.utcnow()
        }

        chunks_data = chunker.chunk_sections(sections)

        for table in tables:
            table_chunk = {
                "content": table["text"],
                "section": f"table_{table['page']}_{table['table_index']}",
                "chunk_index": len(chunks_data),
                "token_count": len(table["text"].split()) * 4 // 3,
                "chemical_entities": [],
                "catalyst": None,
                "solvent": None,
                "temperature": None,
                "yield_value": None,
                "conditions": {},
                "reactions": [],
            }
            chunks_data.append(table_chunk)

        all_entities = set()
        all_reactions = set()
        db_chunks = []

        for chunk_data in chunks_data:
            chunk_id = get_next_sequence_value(db, "chunk_id")
            chunk = {
                "id": chunk_id,
                "paper_id": paper_id,
                "section": chunk_data["section"],
                "content": chunk_data["content"],
                "chunk_index": chunk_data["chunk_index"],
                "chemical_entities": chunk_data.get("chemical_entities", []),
                "reactions": chunk_data.get("reactions", []),
                "catalyst": chunk_data.get("catalyst"),
                "solvent": chunk_data.get("solvent"),
                "temperature": chunk_data.get("temperature"),
                "yield_value": chunk_data.get("yield_value"),
                "conditions": chunk_data.get("conditions", {}),
                "token_count": chunk_data.get("token_count", 0),
            }
            db_chunks.append(chunk)

            for entity in chunk_data.get("chemical_entities", []):
                all_entities.add(entity)
            for reaction in chunk_data.get("reactions", []):
                all_reactions.add(reaction)

        paper["chemical_entities"] = list(all_entities)
        paper["reactions"] = list(all_reactions)

        db.papers.insert_one(paper)
        if db_chunks:
            db.chunks.insert_many(db_chunks)

        try:
            from app.services.graph.knowledge_graph import knowledge_graph
            paper_data_for_graph = {
                "paper_id": paper["id"],
                "title": paper["title"],
                "year": paper["year"],
                "doi": paper["doi"],
                "authors": paper["authors"],
                "journal": paper["journal"],
                "chemical_entities": paper["chemical_entities"],
            }
            knowledge_graph.populate_from_paper(paper_data_for_graph, db_chunks)
        except Exception as e:
            pass

        if embedding_service and vector_store:
            texts = [c["content"] for c in db_chunks]
            embeddings = embedding_service.encode(texts)

            chunk_ids = [c["id"] for c in db_chunks]
            vector_store.add_embeddings(embeddings, chunk_ids)

            for i, chunk in enumerate(db_chunks):
                db.chunks.update_one({"id": chunk["id"]}, {"$set": {"embedding_id": chunk_ids[i]}})

        if bm25_search:
            for chunk in db_chunks:
                bm25_search.add_document(chunk["id"], chunk["content"])

        return {
            "paper_id": paper_id,
            "title": paper["title"],
            "authors": paper["authors"] or [],
            "year": paper["year"],
            "doi": paper["doi"],
            "chunk_count": len(db_chunks),
            "chemical_entities": list(all_entities),
            "reactions": list(all_reactions),
            "sections": list(sections.keys()),
            "table_count": len(tables),
        }

    def ingest_text(
        self,
        text: str,
        db,
        title: str = "Untitled",
        authors: Optional[list[str]] = None,
        year: Optional[int] = None,
        doi: Optional[str] = None,
        source: Optional[str] = None,
        embedding_service=None,
        vector_store=None,
        bm25_search=None,
    ) -> dict:
        metadata = paper_parser.extract_metadata(text)
        sections = pdf_processor.parse_sections(text)

        if not sections:
            sections = {"full_text": text}

        paper_id = get_next_sequence_value(db, "paper_id")

        paper = {
            "id": paper_id,
            "title": title or metadata.get("title", "Untitled"),
            "authors": authors or metadata.get("authors", []),
            "year": year or metadata.get("year"),
            "abstract": metadata.get("abstract"),
            "doi": doi or metadata.get("doi"),
            "source": source or "text_input",
            "journal": metadata.get("journal"),
            "keywords": metadata.get("keywords", []),
            "full_text": text,
            "created_at": datetime.utcnow()
        }

        chunks_data = chunker.chunk_sections(sections)
        all_entities = set()
        all_reactions = set()
        db_chunks = []

        for chunk_data in chunks_data:
            chunk_id = get_next_sequence_value(db, "chunk_id")
            chunk = {
                "id": chunk_id,
                "paper_id": paper_id,
                "section": chunk_data["section"],
                "content": chunk_data["content"],
                "chunk_index": chunk_data["chunk_index"],
                "chemical_entities": chunk_data.get("chemical_entities", []),
                "reactions": chunk_data.get("reactions", []),
                "catalyst": chunk_data.get("catalyst"),
                "solvent": chunk_data.get("solvent"),
                "temperature": chunk_data.get("temperature"),
                "yield_value": chunk_data.get("yield_value"),
                "conditions": chunk_data.get("conditions", {}),
                "token_count": chunk_data.get("token_count", 0),
            }
            db_chunks.append(chunk)

            for entity in chunk_data.get("chemical_entities", []):
                all_entities.add(entity)
            for reaction in chunk_data.get("reactions", []):
                all_reactions.add(reaction)

        paper["chemical_entities"] = list(all_entities)
        paper["reactions"] = list(all_reactions)

        db.papers.insert_one(paper)
        if db_chunks:
            db.chunks.insert_many(db_chunks)

        try:
            from app.services.graph.knowledge_graph import knowledge_graph
            paper_data_for_graph = {
                "paper_id": paper["id"],
                "title": paper["title"],
                "year": paper["year"],
                "doi": paper["doi"],
                "authors": paper["authors"],
                "journal": paper["journal"],
                "chemical_entities": paper["chemical_entities"],
            }
            knowledge_graph.populate_from_paper(paper_data_for_graph, db_chunks)
        except Exception as e:
            pass

        if embedding_service and vector_store:
            texts = [c["content"] for c in db_chunks]
            embeddings = embedding_service.encode(texts)
            chunk_ids = [c["id"] for c in db_chunks]
            vector_store.add_embeddings(embeddings, chunk_ids)
            for i, chunk in enumerate(db_chunks):
                db.chunks.update_one({"id": chunk["id"]}, {"$set": {"embedding_id": chunk_ids[i]}})

        if bm25_search:
            for chunk in db_chunks:
                bm25_search.add_document(chunk["id"], chunk["content"])

        return {
            "paper_id": paper_id,
            "title": paper["title"],
            "chunk_count": len(db_chunks),
            "chemical_entities": list(all_entities),
            "reactions": list(all_reactions),
        }

    def _store_file(self, filepath: str) -> str:
        os.makedirs(self.upload_dir, exist_ok=True)
        filename = os.path.basename(filepath)
        dest = os.path.join(self.upload_dir, filename)

        counter = 1
        base, ext = os.path.splitext(filename)
        while os.path.exists(dest):
            dest = os.path.join(self.upload_dir, f"{base}_{counter}{ext}")
            counter += 1

        shutil.copy2(filepath, dest)
        return dest


ingestion_pipeline = IngestionPipeline()
