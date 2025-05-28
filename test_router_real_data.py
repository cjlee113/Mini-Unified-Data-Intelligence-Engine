import os
import json
from project.retrievers.sql import SQLRetriever
from project.retrievers.vector import VectorRetriever
from project.tools.router import Router
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LCDocument
import uuid

# Paths
duckdb_path = "project/data/enterprise.db"
parsed_docs_path = "project/data/test_data/day2_unstructured/output/parsed_docs.jsonl"

# Initialize Qdrant and embedding model
qdrant = QdrantClient(":memory:")
model = SentenceTransformer('all-MiniLM-L6-v2')
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

# Create Qdrant collection
qdrant.recreate_collection(
    collection_name="documents",
    vectors_config=models.VectorParams(
        size=model.get_sentence_embedding_dimension(),
        distance=models.Distance.COSINE
    )
)

# Load and index real parsed documents
with open(parsed_docs_path) as f:
    for line in f:
        doc = json.loads(line)
        text = doc["body"]
        doc_id = doc["doc_id"]
        metadata = {k: v for k, v in doc.items() if k not in ("body",)}
        # Chunk and embed
        chunks = splitter.split_documents([LCDocument(page_content=text, metadata=metadata)])
        for i, chunk in enumerate(chunks):
            qdrant.upsert(
                collection_name="documents",
                points=[models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=model.encode(chunk.page_content).tolist(),
                    payload={
                        "text": chunk.page_content,
                        "doc_id": doc_id,
                        "chunk_id": i,
                        **metadata
                    }
                )]
            )

# Initialize retrievers and router
sql_retriever = SQLRetriever(duckdb_path)
vector_retriever = VectorRetriever(qdrant, model)
router = Router(sql_retriever, vector_retriever)

# Test queries
test_queries = [
    "OpenAI acquisition",
    "AI research partnership",
    "PDF parser functionality",
    "customer service email"
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
