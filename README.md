# Mini Unified Data Intelligence Engine

A powerful data intelligence engine that integrates structured and unstructured data for enterprise search and analytics.

## Features

- **Unified Data Integration**: Combines structured (CSV/SQL) and unstructured (text, PDF, email) data sources
- **Knowledge Graph**: Built with Neo4j for relationship-based queries and analytics
- **Intelligent Search**: Uses LangChain for agent-based routing and Qdrant for vector search
- **Natural Language Interface**: Streamlit UI with RAG (Retrieval-Augmented Generation) capabilities
- **Entity Extraction**: Powered by spaCy for extracting entities and relationships

## Tech Stack

- Python 3.11
- DuckDB: For structured data processing
- Neo4j: For knowledge graph storage
- Qdrant: For vector search
- spaCy: For NLP and entity extraction
- LangChain: For agent and tool routing
- Streamlit: For the web interface

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Mini-Unified-Data-Intelligence-Engine.git
cd Mini-Unified-Data-Intelligence-Engine
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with your API keys and credentials:
```
OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=your_neo4j_uri
NEO4J_USER=your_neo4j_user
NEO4J_PASSWORD=your_neo4j_password
```

5. Run the application:
```bash
streamlit run ui/app.py
```

## Project Structure

```
project/
├── agents/         # LangChain agents and tools
├── data/          # Data storage and processing
├── ingest/        # Data ingestion scripts
├── retrievers/    # Search and retrieval components
└── ui/            # Streamlit interface
```

## Usage

1. Start the application using Streamlit
2. Enter your question in natural language
3. The system will:
   - Route your question to the appropriate tool
   - Retrieve relevant data from structured/unstructured sources
   - Generate a natural language response

## License

MIT License 