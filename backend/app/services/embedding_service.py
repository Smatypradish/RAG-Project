from sentence_transformers import SentenceTransformer
from typing import List
from app.config import get_settings

class EmbeddingService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance.model = None
        return cls._instance
        
    def _load_model(self):
        if self.model is None:
            settings = get_settings()
            self.model = SentenceTransformer(settings.embedding_model)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        self._load_model()
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding.tolist()
