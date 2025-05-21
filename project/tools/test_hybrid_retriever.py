from project.retrievers.sql import SQLRetriever
from project.retrievers.vector import VectorRetriever
from project.tools.router import Router
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import os
import uuid

# Paths
duckdb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'data/test_data/day1_structured/output/enterprise.db')

# Initialize Qdrant and embedding model
qdrant = QdrantClient(":memory:")
model = SentenceTransformer('all-MiniLM-L6-v2')

# ONLY IF NOT THERE, Ensure Qdrant collection and sample docs exist BEFORE using retrievers
if "documents" not in [c.name for c in qdrant.get_collections().collections]:
    qdrant.recreate_collection(
        collection_name="documents",
        vectors_config=models.VectorParams(
            size=model.get_sentence_embedding_dimension(),
            distance=models.Distance.COSINE
        )
    )

# Insert multiple sample documents for semantic search
docs = [
    "Alice Brown is a valued customer who frequently orders laptops.",
    "John Doe recently purchased a smartphone and a tablet.",
    "Jane Smith is interested in accessories for her devices.",
    "Bob Johnson had issues with his last order.",
]
for doc_text in docs:
    embedding = model.encode(doc_text).tolist()
    qdrant.upsert(
        collection_name="documents",
        points=[models.PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": doc_text}
        )]
    )

# Initialize retrievers
sql_retriever = SQLRetriever(duckdb_path)
vector_retriever = VectorRetriever(qdrant, model)
router = Router(sql_retriever, vector_retriever)

# Test queries
test_queries = [
    "Alice",
    "John",
    "accessories",
    "order issues",
    "Nonexistent Customer"
]

for query in test_queries:
    print(f"\n=== Query: '{query}' ===")
    results = router.search(query)
    print("Structured (SQL) results:")
    for r in results["structured"]:
        print(r)
    print("Semantic (Vector) results:")
    for r in results["semantic"]:
        print(r) 