import os
import json
import pickle
import numpy as np
from typing import Optional
from app.config import settings


class VectorStore:
    def __init__(self, index_path: Optional[str] = None, dimension: int = 384):
        self.index_path = index_path or settings.faiss_index_path
        self.dimension = dimension
        self.embeddings = []
        self.chunk_ids = []
        
        self._load_or_create()

    def _load_or_create(self):
        vectors_file = os.path.join(self.index_path, "vectors.pkl")
        ids_file = os.path.join(self.index_path, "ids.json")

        if os.path.exists(vectors_file) and os.path.exists(ids_file):
            with open(vectors_file, "rb") as f:
                self.embeddings = pickle.load(f)
            with open(ids_file, "r") as f:
                self.chunk_ids = json.load(f)
        else:
            self.embeddings = []
            self.chunk_ids = []

    def _normalize(self, v):
        norm = np.linalg.norm(v, axis=1, keepdims=True)
        norm[norm == 0] = 1e-10
        return v / norm

    def add_embeddings(self, embeddings: np.ndarray, chunk_ids: list[int]):
        if len(embeddings) == 0:
            return

        embeddings = np.array(embeddings, dtype=np.float32)
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)

        embeddings = self._normalize(embeddings)

        if len(self.embeddings) == 0:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])
            
        self.chunk_ids.extend(chunk_ids)
        self._save()

    def search(self, query_embedding: np.ndarray, top_k: int = 20) -> list[dict]:
        if len(self.embeddings) == 0:
            return []

        query_embedding = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        query_embedding = self._normalize(query_embedding)

        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "chunk_id": self.chunk_ids[idx],
                "score": float(similarities[idx]),
                "source": "semantic",
            })

        return results

    def remove_embeddings(self, chunk_ids_to_remove: list[int]):
        if not self.embeddings.size:
            return

        keep_indices = [i for i, cid in enumerate(self.chunk_ids) if cid not in chunk_ids_to_remove]
        
        if len(keep_indices) == len(self.chunk_ids):
            return

        self.embeddings = self.embeddings[keep_indices]
        self.chunk_ids = [self.chunk_ids[i] for i in keep_indices]
        
        self._save()

    def get_total_vectors(self) -> int:
        return len(self.chunk_ids)

    def _save(self):
        os.makedirs(self.index_path, exist_ok=True)
        vectors_file = os.path.join(self.index_path, "vectors.pkl")
        ids_file = os.path.join(self.index_path, "ids.json")

        with open(vectors_file, "wb") as f:
            pickle.dump(self.embeddings, f)
            
        with open(ids_file, "w") as f:
            json.dump(self.chunk_ids, f)

    def clear(self):
        self.embeddings = []
        self.chunk_ids = []
        self._save()
