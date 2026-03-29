# Bhagavad Gita RAG API - Version 2.0

Modern RAG (Retrieval-Augmented Generation) system for answering questions about the Bhagavad Gita using vector search and LLM integration.

## 🎯 Features

- **Modern PDF Processing**: PyMuPDF (fitz) for superior text extraction
- **Semantic Search**: FAISS vector database with embedding-based retrieval
- **Advanced Embeddings**: BAAI/bge-base-en-v1.5 for high-quality semantic understanding
- **LLM Integration**: OpenAI GPT-4o-mini or local Ollama support
- **Verse-Aware Chunking**: Preserves verse boundaries and references
- **Source Citations**: Every answer includes page numbers and verse references
- **Production Ready**: Async API, structured logging, health checks

## 🏗️ Architecture

```
┌─────────────┐
│   User      │
│  Question   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Endpoint            │
│           (/ask)                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      RAG Orchestrator               │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌──────────────┐
│  Embedding  │  │ Vector Store │
│  Service    │  │   (FAISS)    │
└─────────────┘  └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │   Retrieve   │
                 │   Top-K      │
                 │   Sources    │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ LLM Service  │
                 │  (OpenAI/    │
                 │   Ollama)    │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │   Answer +   │
                 │   Sources    │
                 └──────────────┘
```

## 📦 Installation

### Prerequisites

- Python 3.12+
- OpenAI API key (or Ollama for local LLM)

### Setup

1. **Clone and navigate to project**:
```bash
cd /Users/ramyam/Documents/BG
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. **Run the application**:
```bash
python main_v2.py
```

The API will be available at `http://localhost:8080`

## 🚀 API Endpoints

### POST /ask
Ask a question about the Bhagavad Gita

**Request**:
```json
{
  "question": "What does Krishna say about duty?",
  "top_k": 5,
  "include_sources": true
}
```

**Response**:
```json
{
  "answer": "Krishna emphasizes the importance of performing one's duty...",
  "sources": [
    {
      "page": 123,
      "chapter": 2,
      "verse": 47,
      "verse_reference": "Bg 2.47",
      "excerpt": "You have a right to perform your prescribed duty...",
      "similarity_score": 0.89
    }
  ],
  "confidence": 0.85,
  "processing_time_ms": 1234.56
}
```

### GET /sources/{query}
Get relevant sources without generating an answer

**Example**: `GET /sources/karma%20yoga?top_k=3`

### POST /upload-pdf
Re-index the PDF (useful after updates)

### GET /stats
Get system statistics

### GET /health
Comprehensive health check

### DELETE /clear-index
Clear the vector database

## 🔧 Configuration

All settings can be configured via environment variables or `.env` file:

### Key Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Your OpenAI API key |
| `LLM_PROVIDER` | `openai` | `openai` or `ollama` |
| `EMBEDDING_MODEL_NAME` | `BAAI/bge-base-en-v1.5` | Embedding model |
| `CHUNK_SIZE` | `1200` | Text chunk size |
| `VECTOR_TOP_K` | `5` | Number of sources to retrieve |
| `USE_MMR` | `true` | Use MMR for diversity |

See `.env.example` for all available settings.

## 🐳 Docker Deployment

### Build and Run Locally

```bash
docker build -t gita-rag-api .
docker run -p 8080:8080 -e OPENAI_API_KEY=your-key gita-rag-api
```

### Deploy to Google Cloud Run

```bash
gcloud builds submit --config=cloudbuild.yaml
```

Make sure to set the `OPENAI_API_KEY` as a secret in Cloud Run.

## 📊 Performance

- **Indexing**: ~2-3 minutes for full Bhagavad Gita PDF
- **Query Response**: ~1-3 seconds (including LLM generation)
- **Memory Usage**: ~2-3 GB (with embeddings loaded)

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Test a single question:

```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is karma yoga?"}'
```

## 📁 Project Structure

```
BG/
├── src/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── config/
│   │   └── settings.py        # Configuration
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── pdf_processor.py   # PDF extraction
│   │   ├── chunker.py         # Text chunking
│   │   ├── embeddings.py      # Embedding generation
│   │   ├── vector_store.py    # FAISS vector DB
│   │   ├── llm_service.py     # LLM integration
│   │   └── rag_orchestrator.py # RAG pipeline
│   └── utils/
├── data/
│   └── vector_store/          # Persisted index
├── logs/                      # Application logs
├── main_v2.py                 # Main application
├── requirements.txt           # Dependencies
├── Dockerfile                 # Container config
└── .env                       # Environment variables
```

## 🔄 Migration from V1

The new V2 system coexists with the old system. To switch:

1. Use `main_v2.py` instead of `app.py`
2. Update your `.env` with new settings
3. The old endpoints are still available for backward compatibility

## 🛠️ Development

### Adding a New Embedding Model

Edit `src/config/settings.py`:
```python
embedding_model_name: str = "nomic-ai/nomic-embed-text-v1.5"
```

### Using Local LLM (Ollama)

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3.1:8b`
3. Update `.env`:
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
```

## 📝 License

This project is for educational purposes.

## 🙏 Acknowledgments

- Bhagavad Gita As It Is by A.C. Bhaktivedanta Swami Prabhupada
- BAAI for bge-base-en-v1.5 embeddings
- FAISS by Facebook Research
- OpenAI for GPT models
