from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class VectorRetriever:
    def __init__(self, qdrant_client, embedding_model):
        self.qdrant = qdrant_client
        self.model = embedding_model

    def search(self, query, top_k=3):
        query_vector = self.model.encode(query).tolist()
        results = self.qdrant.search(
            collection_name="documents",
            query_vector=query_vector,
            limit=top_k
        )
        return [
            {
                "text": r.payload.get("text", ""),
                "score": r.score
            }
            for r in results
        ] 