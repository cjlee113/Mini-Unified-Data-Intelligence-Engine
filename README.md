# Mini Unified Data Intelligence Engine

A lightweight, end-to-end enterprise data system that combines structured and unstructured data processing with AI-powered querying capabilities.

## Features
- Structured data ingestion (CSV, Google Sheets)
- Unstructured data processing (PDF, Email)
- Hybrid search (SQL + Vector + Graph)
- RAG-powered question answering
- Interactive Streamlit UI
- Feedback collection and analytics
- Observability dashboard

## Tech Stack
- Python (main language)
- DuckDB (structured data storage)
- Qdrant (vector search)
- Neo4j (knowledge graph)
- Streamlit (UI)
- LangChain (LLM orchestration)
- OpenAI/Fireworks.ai (LLM provider)

## Setup
1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Project Structure
```
project/
├── ingest/       # Data loaders for structured and unstructured data
├── retrievers/   # SQL, vector, and graph search implementations
├── tools/        # RAG components and agent tools
├── ui/           # Streamlit web interface
├── feedback/     # User feedback logging and analytics
├── config/       # Configuration and routing rules
└── README.md
```

## Development Timeline
- Day 1: Structured data ingestion
- Day 2: Unstructured data processing
- Day 3: Vector embeddings and indexing
- Day 4: Hybrid retrieval system
- Day 5: Knowledge graph integration
- Day 6: LangChain agent implementation
- Day 7: Streamlit UI development
- Day 8: Feedback system
- Day 9: Observability metrics
- Day 10: Polish and documentation

## License
MIT License
