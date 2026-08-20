import chromadb
from typing import List, Dict, Any
from app.config import get_settings

class VectorStoreService:
    def __init__(self):
        settings = get_settings()
        self.client = chromadb.PersistentClient(path=settings.chromadb_path)
        self.collection = self.client.get_or_create_collection(name="documents")

    def add_chunks(self, doc_id: int, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        if not chunks:
            return
        ids = [f"{doc_id}_{c['metadata']['chunk_index']}" for c in chunks]
        texts = [c['chunk_text'] for c in chunks]
        metadatas = [c['metadata'] for c in chunks]
        
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if self.collection.count() == 0:
            return []
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count())
        )
        
        formatted_results = []
        if results['ids']:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "distance": results['distances'][0][i],
                    "metadata": results['metadatas'][0][i]
                })
        return formatted_results

    def delete_document(self, doc_id: int):
        try:
            self.collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            print(f"Error deleting from ChromaDB: {e}")

    def get_collection_stats(self) -> Dict[str, int]:
        return {"count": self.collection.count()}
