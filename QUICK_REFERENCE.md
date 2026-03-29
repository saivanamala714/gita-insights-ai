# Quick Reference Guide - RAG v2

## 🚀 Common Commands

### Setup & Installation
```bash
# Initial setup
./setup_v2.sh

# Manual setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add OPENAI_API_KEY
```

### Running the Application
```bash
# Development mode
python main_v2.py

# Production mode with uvicorn
uvicorn main_v2:app --host 0.0.0.0 --port 8080 --workers 4

# With Docker
docker build -t gita-rag .
docker run -p 8080:8080 -e OPENAI_API_KEY=sk-... gita-rag
```

### Testing
```bash
# Full test suite
python test_rag.py

# Quick API test
curl http://localhost:8080/health

# Ask a question
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is dharma?"}'
```

## 📝 API Endpoints

### POST /ask
```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does Krishna say about duty?",
    "top_k": 5,
    "include_sources": true
  }'
```

### GET /sources/{query}
```bash
curl http://localhost:8080/sources/karma%20yoga?top_k=3
```

### POST /upload-pdf (Re-index)
```bash
curl -X POST http://localhost:8080/upload-pdf
```

### GET /stats
```bash
curl http://localhost:8080/stats
```

### GET /health
```bash
curl http://localhost:8080/health
```

### DELETE /clear-index
```bash
curl -X DELETE http://localhost:8080/clear-index
```

## ⚙️ Configuration Quick Reference

### Essential Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional but recommended
LLM_PROVIDER=openai              # or "ollama"
EMBEDDING_MODEL_NAME=BAAI/bge-base-en-v1.5
CHUNK_SIZE=1200
VECTOR_TOP_K=5
LOG_LEVEL=INFO
```

### Using Ollama (Free Local LLM)
```bash
# Install Ollama
brew install ollama  # macOS
# or download from https://ollama.ai

# Pull a model
ollama pull llama3.1:8b

# Configure in .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
```

## 🐛 Troubleshooting

### "Vector store not initialized"
```bash
# Re-index the PDF
curl -X POST http://localhost:8080/upload-pdf
```

### "OpenAI API key not configured"
```bash
# Set in environment
export OPENAI_API_KEY=sk-your-key

# Or in .env file
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

### Check logs
```bash
# View logs
tail -f logs/app.log

# Or if using JSON logging
tail -f logs/app.log | jq .
```

### Clear everything and start fresh
```bash
# Clear vector store
curl -X DELETE http://localhost:8080/clear-index

# Remove data directory
rm -rf data/

# Re-index
curl -X POST http://localhost:8080/upload-pdf
```

## 📊 Performance Tuning

### For Faster Responses
```bash
# In .env
VECTOR_TOP_K=3              # Fewer sources
USE_MMR=false               # Disable diversity
OPENAI_MODEL=gpt-3.5-turbo  # Faster model
```

### For Better Quality
```bash
# In .env
VECTOR_TOP_K=8              # More sources
CHUNK_SIZE=1500             # Larger chunks
OPENAI_MODEL=gpt-4o         # Better model
OPENAI_TEMPERATURE=0.0      # More deterministic
```

### For Lower Costs
```bash
# Use Ollama (free)
LLM_PROVIDER=ollama

# Or use cheaper OpenAI model
OPENAI_MODEL=gpt-4o-mini
```

## 🔍 Example Questions

```bash
# Philosophy
"What is the nature of the soul?"
"What does Krishna say about attachment?"
"Explain the concept of dharma"

# Practical guidance
"How should I deal with difficult decisions?"
"What is the path to peace of mind?"
"How to overcome fear?"

# Specific verses
"What is verse 2.47 about?"
"Explain chapter 3 verse 35"

# Characters
"Who is Arjuna?"
"Tell me about Krishna"
```

## 📦 Project Structure

```
BG/
├── src/
│   ├── api/routes.py          # API endpoints
│   ├── config/settings.py     # Configuration
│   ├── models/schemas.py      # Data models
│   └── services/
│       ├── pdf_processor.py   # PDF extraction
│       ├── chunker.py         # Text chunking
│       ├── embeddings.py      # Embeddings
│       ├── vector_store.py    # FAISS DB
│       ├── llm_service.py     # LLM integration
│       └── rag_orchestrator.py # Main pipeline
├── main_v2.py                 # Application entry
├── test_rag.py                # Test script
└── .env                       # Configuration
```

## 🚢 Deployment

### Local Development
```bash
python main_v2.py
```

### Docker
```bash
docker build -t gita-rag .
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  gita-rag
```

### Google Cloud Run
```bash
gcloud builds submit --config=cloudbuild.yaml
gcloud run services update bhagavad-gita-api \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY
```

## 💡 Tips

1. **First run takes time**: Initial indexing takes 2-3 minutes
2. **Index is cached**: Subsequent runs are instant
3. **Use health check**: Monitor system status
4. **Check stats**: See how many chunks are indexed
5. **Experiment**: Try different chunk sizes and top-k values
6. **Monitor costs**: Track OpenAI API usage
7. **Use Ollama**: For free local inference

## 📚 Documentation

- `README_V2.md` - Complete user guide
- `MIGRATION_GUIDE.md` - Migrating from V1
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `PROJECT_INTENTION.md` - Project goals and checklist

## 🆘 Getting Help

1. Check health: `curl http://localhost:8080/health`
2. View logs: `tail -f logs/app.log`
3. Test components: `python test_rag.py`
4. Review docs: See files above
