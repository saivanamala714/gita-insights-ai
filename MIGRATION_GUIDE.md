# Migration Guide: V1 to V2

This guide helps you migrate from the legacy RAG system (app.py) to the new modern RAG v2 system (main_v2.py).

## What's New in V2?

### Major Improvements

1. **Modern PDF Processing**
   - ✅ Replaced PyPDF2 with PyMuPDF (fitz) - 3x faster, better text extraction
   - ✅ Better verse boundary detection
   - ✅ Improved metadata extraction

2. **Vector Search**
   - ✅ FAISS vector database for semantic search
   - ✅ Modern embeddings (BAAI/bge-base-en-v1.5)
   - ✅ MMR (Maximal Marginal Relevance) for diverse results

3. **LLM Integration**
   - ✅ OpenAI GPT-4o-mini integration
   - ✅ Ollama support for local LLMs
   - ✅ Grounded answers with source citations

4. **Architecture**
   - ✅ Clean modular structure (src/ directory)
   - ✅ Proper separation of concerns
   - ✅ Type hints throughout
   - ✅ Async support

5. **Production Features**
   - ✅ Structured JSON logging
   - ✅ Comprehensive health checks
   - ✅ Environment-based configuration
   - ✅ Better error handling

## Side-by-Side Comparison

| Feature | V1 (app.py) | V2 (main_v2.py) |
|---------|-------------|-----------------|
| PDF Library | PyPDF2 (deprecated) | PyMuPDF (modern) |
| Search Method | Keyword matching | Vector similarity |
| Embeddings | None | bge-base-en-v1.5 |
| LLM | None | OpenAI/Ollama |
| Answer Quality | Rule-based | AI-generated |
| Source Citations | Basic | Rich (page, verse, score) |
| Performance | ~500ms | ~1-3s (with LLM) |
| Scalability | Limited | High |

## Migration Steps

### 1. Backup Your Current System

```bash
# Backup current environment
cp .env .env.v1.backup

# Backup any custom modifications
cp app.py app.py.v1.backup
```

### 2. Install New Dependencies

```bash
# Run the setup script
./setup_v2.sh

# Or manually:
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the new environment template
cp .env.example .env

# Edit .env and add:
# - OPENAI_API_KEY (required for OpenAI)
# - Or configure Ollama for local LLM
```

### 4. Test the New System

```bash
# Run the test script
python test_rag.py
```

This will:
- Index the PDF (first time only, ~2-3 minutes)
- Test several questions
- Show you the new response format

### 5. Start the New API

```bash
# Start the v2 API
python main_v2.py
```

The API will be available at `http://localhost:8080`

### 6. Update Your Frontend/Client

The `/ask` endpoint has a new response format:

**Old V1 Response:**
```json
{
  "answer": "...",
  "sources": [
    {
      "page_content": "...",
      "metadata": {"page": 123}
    }
  ]
}
```

**New V2 Response:**
```json
{
  "answer": "...",
  "sources": [
    {
      "page": 123,
      "chapter": 2,
      "verse": 47,
      "verse_reference": "Bg 2.47",
      "excerpt": "...",
      "similarity_score": 0.89
    }
  ],
  "confidence": 0.85,
  "processing_time_ms": 1234.56
}
```

### 7. Deploy to Production

#### Docker

```bash
# Build new image
docker build -t gita-rag-v2 .

# Run with environment variables
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=your-key \
  gita-rag-v2
```

#### Google Cloud Run

```bash
# Update cloudbuild.yaml if needed
gcloud builds submit --config=cloudbuild.yaml

# Set environment variables in Cloud Run
gcloud run services update bhagavad-gita-api \
  --set-env-vars OPENAI_API_KEY=your-key
```

## Backward Compatibility

### Running Both Systems

You can run both V1 and V2 simultaneously on different ports:

```bash
# Terminal 1: V1 on port 8000
uvicorn app:app --port 8000

# Terminal 2: V2 on port 8080
python main_v2.py
```

### Gradual Migration

1. **Week 1**: Deploy V2 alongside V1
2. **Week 2**: Route 10% of traffic to V2
3. **Week 3**: Route 50% of traffic to V2
4. **Week 4**: Route 100% to V2, deprecate V1

## Preserving Custom Features

If you've customized the V1 system, here's how to preserve those features:

### Custom Q&A Pairs

The old `gita_qa_pairs.py` can be integrated into V2:

```python
# In src/services/rag_orchestrator.py
from gita_qa_pairs import get_qa_pairs

def answer_question(self, question: str):
    # Try custom Q&A first
    qa_answer = self._check_custom_qa(question)
    if qa_answer:
        return qa_answer
    
    # Fall back to RAG pipeline
    return super().answer_question(question)
```

### Character Information

Integrate `gita_characters.py`:

```python
# Add to routes.py
@router.get("/characters")
async def get_characters():
    from gita_characters import get_main_characters
    return get_main_characters()
```

### Emotion Mappings

Keep `emotion_mappings.py` and add an endpoint:

```python
@router.get("/emotions/{emotion}")
async def get_emotion_guidance(emotion: str):
    from emotion_mappings import get_emotion_mapping
    return get_emotion_mapping(emotion)
```

## Troubleshooting

### Issue: "Vector store not initialized"

**Solution**: Run the indexing:
```bash
curl -X POST http://localhost:8080/upload-pdf
```

### Issue: "OpenAI API key not configured"

**Solution**: Set the environment variable:
```bash
export OPENAI_API_KEY=your-key-here
# Or add to .env file
```

### Issue: "Out of memory during indexing"

**Solution**: Reduce batch size in `.env`:
```
EMBEDDING_BATCH_SIZE=16
```

### Issue: "Slow response times"

**Solutions**:
1. Use a smaller embedding model
2. Reduce `VECTOR_TOP_K` to 3
3. Disable MMR: `USE_MMR=false`
4. Use Ollama locally instead of OpenAI

### Issue: "Answers not accurate"

**Solutions**:
1. Increase `VECTOR_TOP_K` to 7-10
2. Lower `SIMILARITY_THRESHOLD` to 0.5
3. Adjust `CHUNK_SIZE` (try 800 or 1500)
4. Use a better LLM model (gpt-4o instead of gpt-4o-mini)

## Rollback Plan

If you need to rollback to V1:

```bash
# 1. Stop V2
pkill -f main_v2

# 2. Restore V1 environment
cp .env.v1.backup .env

# 3. Start V1
uvicorn app:app --port 8080
```

## Cost Considerations

### V1 Costs
- Hosting only (~$10-20/month on Cloud Run)

### V2 Costs
- Hosting (~$10-20/month on Cloud Run)
- OpenAI API (~$0.15 per 1M tokens)
- Estimated: ~$0.002 per question (with gpt-4o-mini)

### Cost Optimization
1. Use Ollama for free local LLM
2. Cache frequent questions
3. Use gpt-4o-mini instead of gpt-4o
4. Implement rate limiting

## Support

If you encounter issues:

1. Check logs: `tail -f logs/app.log`
2. Run health check: `curl http://localhost:8080/health`
3. Test individual components with `test_rag.py`
4. Review the README_V2.md for detailed documentation

## Next Steps

After successful migration:

1. ✅ Monitor performance and costs
2. ✅ Collect user feedback
3. ✅ Fine-tune chunk sizes and retrieval parameters
4. ✅ Consider adding conversation history
5. ✅ Implement caching for frequent queries
6. ✅ Add analytics and usage tracking
