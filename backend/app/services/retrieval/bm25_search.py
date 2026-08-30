import os
import json
import pickle
import re
from typing import Optional
from rank_bm25 import BM25Okapi
from app.config import settings


class BM25Search:
    def __init__(self, index_path: Optional[str] = None):
        self.index_path = index_path or settings.bm25_index_path
        self.corpus = {}
        self.tokenized_corpus = {}
        self.bm25 = None
        self.doc_ids = []

        self._load()

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r"[^\w\s\-\.\(\)]", " ", text)
        tokens = text.split()
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "is", "was", "are", "were",
            "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "shall", "should", "may", "might", "can", "could",
            "this", "that", "these", "those", "it", "its", "not", "no", "nor",
            "as", "if", "then", "than", "so", "up", "out", "about", "into",
            "over", "after", "before", "between", "under", "above", "below",
        }
        tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
        return tokens

    def add_document(self, doc_id: int, text: str):
        tokens = self._tokenize(text)
        self.corpus[doc_id] = text
        self.tokenized_corpus[doc_id] = tokens
        self._rebuild_index()

    def add_documents(self, documents: list[dict]):
        for doc in documents:
            tokens = self._tokenize(doc["text"])
            self.corpus[doc["id"]] = doc["text"]
            self.tokenized_corpus[doc["id"]] = tokens
        self._rebuild_index()

    def search(self, query: str, top_k: int = 20) -> list[dict]:
        if self.bm25 is None or not self.doc_ids:
            return []

        tokenized_query = self._tokenize(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    "chunk_id": self.doc_ids[idx],
                    "score": float(scores[idx]),
                    "source": "keyword",
                })

        return results

    def search_with_filters(
        self,
        query: str,
        top_k: int = 20,
        catalyst: Optional[str] = None,
        solvent: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> list[dict]:
        results = self.search(query, top_k=top_k * 3)

        if catalyst:
            catalyst_lower = catalyst.lower()
            results = [r for r in results if catalyst_lower in self.corpus.get(r["chunk_id"], "").lower()]

        if solvent:
            solvent_lower = solvent.lower()
            results = [r for r in results if solvent_lower in self.corpus.get(r["chunk_id"], "").lower()]

        return results[:top_k]

    def _rebuild_index(self):
        self.doc_ids = sorted(self.tokenized_corpus.keys())
        if not self.doc_ids:
            self.bm25 = None
            return

        tokenized_docs = [self.tokenized_corpus[doc_id] for doc_id in self.doc_ids]
        self.bm25 = BM25Okapi(tokenized_docs)
        self._save()

    def remove_document(self, doc_id: int):
        if doc_id in self.corpus:
            del self.corpus[doc_id]
        if doc_id in self.tokenized_corpus:
            del self.tokenized_corpus[doc_id]
        self._rebuild_index()

    def get_total_documents(self) -> int:
        return len(self.corpus)

    def _save(self):
        os.makedirs(self.index_path, exist_ok=True)
        data_file = os.path.join(self.index_path, "bm25_data.pkl")
        with open(data_file, "wb") as f:
            pickle.dump({
                "corpus": self.corpus,
                "tokenized_corpus": self.tokenized_corpus,
            }, f)

    def _load(self):
        data_file = os.path.join(self.index_path, "bm25_data.pkl")
        if os.path.exists(data_file):
            with open(data_file, "rb") as f:
                data = pickle.load(f)
                self.corpus = data.get("corpus", {})
                self.tokenized_corpus = data.get("tokenized_corpus", {})
                self._rebuild_index()

    def clear(self):
        self.corpus = {}
        self.tokenized_corpus = {}
        self.bm25 = None
        self.doc_ids = []
        self._save()
