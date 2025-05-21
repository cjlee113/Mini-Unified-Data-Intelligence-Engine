"""
Uses chunking, embedding, and stores documents using SentenceBert and Qdrant for semantic search.
Lets user search for similar documents based on a query given by the user.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import json
import uuid

# Use all-MiniLM-L6-v2 model for embedding
class DocumentEmbedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.qdrant = QdrantClient(":memory:")
        
        # Create collection
        self.qdrant.recreate_collection(
            collection_name="documents",
            vectors_config=models.VectorParams(
                size=self.model.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            )
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
    # Put the document into the vector store
    def store_document(self, doc_id, text, metadata=None):
        # Create and split document
        doc = Document(page_content=text, metadata=metadata or {})
        chunks = self.text_splitter.split_documents([doc])
        
        # Store chunks with embeddings
        for i, chunk in enumerate(chunks):
            # Generate UUID for point ID
            point_id = str(uuid.uuid4())
            
            self.qdrant.upsert(
                collection_name="documents",
                points=[models.PointStruct(
                    id=point_id,
                    vector=self.model.encode(chunk.page_content).tolist(),
                    payload={
                        "text": chunk.page_content,
                        "doc_id": doc_id,
                        "chunk_id": i,
                        **(metadata or {})
                    }
                )]
            )
    # Finds the relevant documents using SentenceBert from the vector store
    def search(self, query, limit=5):
        results = self.qdrant.search(
            collection_name="documents",
            query_vector=self.model.encode(query).tolist(),
            limit=limit
        )
        return [{"text": r.payload["text"], "doc_id": r.payload["doc_id"], "score": r.score} for r in results]

def main():
    # Initialize embedder
    embedder = DocumentEmbedder()
    
    # Add multiple test documents with different content
    documents = [
        {
            "doc_id": "tech_doc",
            "text": "Python is a high-level programming language. It supports multiple programming paradigms including procedural, object-oriented, and functional programming. Python's design philosophy emphasizes code readability with its notable use of significant indentation.",
            "metadata": {"source": "technical", "category": "programming"}
        },
        {
            "doc_id": "customer_feedback",
            "text": "The product quality is excellent but shipping took longer than expected. Customer service was very responsive when I reached out about the delay. Would recommend improving delivery times.",
            "metadata": {"source": "feedback", "category": "review"}
        },
        {
            "doc_id": "news_article",
            "text": "Recent developments in artificial intelligence have shown promising results in natural language processing. Researchers have achieved new benchmarks in language understanding and generation. However, concerns about AI safety and ethics remain important considerations.",
            "metadata": {"source": "news", "category": "technology"}
        }
    ]
    
    # Store all documents
    print("Storing test documents...")
    for doc in documents:
        embedder.store_document(doc["doc_id"], doc["text"], doc["metadata"])
    
    # Test different types of queries
    test_queries = [
        # Technical query
        "programming language features",
        # Customer service related
        "customer experience and shipping",
        # Conceptual query
        "AI and language processing",
        # Mixed concept query
        "technology safety and quality",
        # Query with no exact matches
        "financial markets and trading"
    ]
    
    # Run searches
    print("\nTesting different queries:")
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = embedder.search(query, limit=2)  # Get top 2 results
        print("Results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Document: {result['doc_id']}")
            print(f"   Score: {result['score']:.3f}")
            print(f"   Text: {result['text'][:150]}...")

if __name__ == "__main__":
    main() 