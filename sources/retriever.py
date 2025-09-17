# sources/retriever.py
from typing import List, Optional, Dict
import numpy as np

try:
    # optional high-quality embeddings
    from sentence_transformers import SentenceTransformer
    _HAS_SENT_TRANS = True
except Exception:
    _HAS_SENT_TRANS = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


class VectorRetriever:
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        if _HAS_SENT_TRANS:
            self.embed_model = SentenceTransformer(model_name)
        else:
            self.embed_model = None

        self.chunks: List[str] = []
        self._use_embeddings = _HAS_SENT_TRANS
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.nn: Optional[NearestNeighbors] = None
        self.embeddings: Optional[np.ndarray] = None

    def build_index(self, text: str, chunk_size: int = 500):
        """Split text into chunks and build index."""
        text = text or ""
        self.chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)] if text else []

        if not self.chunks:
            self.tfidf_vectorizer = None
            self.nn = None
            self.embeddings = None
            return

        if self._use_embeddings:
            embs = self.embed_model.encode(self.chunks, show_progress_bar=False)
            self.embeddings = np.array(embs).astype("float32")
            # use sklearn NearestNeighbors on embeddings
            self.nn = NearestNeighbors(n_neighbors=min(10, len(self.chunks)), metric="euclidean")
            self.nn.fit(self.embeddings)
        else:
            self.tfidf_vectorizer = TfidfVectorizer(max_features=20000)
            X = self.tfidf_vectorizer.fit_transform(self.chunks)
            self.nn = NearestNeighbors(n_neighbors=min(10, X.shape[0]), metric="cosine")
            self.nn.fit(X)

    def get_top_chunks(self, query: str, top_k: int = 5) -> List[str]:
        if not self.chunks or self.nn is None:
            return []

        if self._use_embeddings:
            q_emb = self.embed_model.encode([query]).astype("float32")
            dists, idxs = self.nn.kneighbors(q_emb, n_neighbors=min(top_k, len(self.chunks)))
            idxs = idxs[0].tolist()
        else:
            q_vec = self.tfidf_vectorizer.transform([query])
            dists, idxs = self.nn.kneighbors(q_vec, n_neighbors=min(top_k, len(self.chunks)))
            idxs = idxs[0].tolist()

        selected = [self.chunks[i] for i in idxs if 0 <= i < len(self.chunks)]
        return selected

    def clear_index(self):
        self.chunks = []
        self.tfidf_vectorizer = None
        self.nn = None
        self.embeddings = None
