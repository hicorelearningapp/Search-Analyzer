# sources/retriever.py
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class VectorRetriever:
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):

        self.embed_model = SentenceTransformer(model_name)
        self.indices: Dict[str, Dict[str, Any]] = {
            "pdf": {"chunks": [], "index": None},
            "video": {"chunks": [], "index": None}
        }
    
    def build_index(self, text: str, source: str, chunk_size: int = 500) -> None:

        if source not in self.indices:
            raise ValueError("Source must be 'pdf' or 'video'")

        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        if not chunks:
            self.indices[source] = {"chunks": [], "index": None}
            return

        embeddings = self.embed_model.encode(chunks, show_progress_bar=False)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings).astype("float32"))

        self.indices[source] = {"chunks": chunks, "index": index}
    
    def get_top_chunks(self, query: str, source: str, top_k: int = 3) -> List[str]:

        if source not in self.indices:
            return []

        chunks = self.indices[source]["chunks"]
        index = self.indices[source]["index"]

        if not chunks or index is None:
            return []

        q_emb = self.embed_model.encode([query]).astype("float32")
        distances, idxs = index.search(np.array(q_emb), top_k)

        selected = [chunks[i] for i in idxs[0] if 0 <= i < len(chunks)]
        return selected
    
    def clear_index(self) -> None:
        
        for source in self.indices:
            self.indices[source] = {"chunks": [], "index": None}
