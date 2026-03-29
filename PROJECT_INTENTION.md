the primary object of this project is to provide a chat interface to the Bhagavad Gita UI and all the answers should be based on the pdf /Users/ramyam/Documents/BG/11-Bhagavad-gita_As_It_Is.pdf. Please let me know how you can achieve this.

Notes

# PDF-Only RAG Chatbot Project Summary
## Project Goal (strict rule – never break this)
Build a Python-based REST API chatbot (using FastAPI) that answers **questions exclusively from the content of one or more provided PDF files**.  
No external knowledge, no hallucination outside the PDF(s).  
Answers must be grounded → return sources (page numbers, excerpts) whenever possible.

Current date: February 21, 2026

## Current Tech Stack & Dependencies (as provided)
Core / API layer:
- fastapi >= 0.109.0
- uvicorn[standard] >= 0.27.0
- gunicorn >= 21.2.0
- pydantic >= 2.0.0
- python-multipart >= 0.0.6

PDF extraction:
- pypdf2 >= 3.0.1   ← legacy / should be replaced

Environment:
- python-dotenv >= 1.0.0

NLP / text utils:
- numpy >= 1.24.0, < 2.0.0   ← upper bound should be removed or raised
- language-tool-python >= 1.0.0   ← optional (grammar)
- nltk >= 3.8.1                   ← optional
- psutil >= 5.9.0                 ← for health checks / monitoring
- jellyfish >= 1.0.0              ← fuzzy matching / optional

ML / Embeddings:
- torch >= 2.0.0
- sentence-transformers >= 2.2.2
- transformers >= 4.30.0
- tokenizers >= 0.13.0
- huggingface-hub >= 0.16.0
- requests >= 2.28.0
- tqdm >= 4.64.0

Dev / testing:
- pytest, pytest-cov, black, isort, flake8, mypy

## Recommended / Suggested Improvements (2026 best practices – you can decide which to adopt)
PDF extraction upgrade priorities (pick ONE main library):
1. **pymupdf** (fitz) ≥ 1.24.0 → fastest + best general text/layout preservation
2. **pdfplumber** ≥ 0.11.0     → strongest native table extraction
3. **pypdf** ≥ 5.0.0           → lightweight pure-Python successor to pypdf2
4. Advanced (if tables/images/scanned PDFs are common): unstructured[pdf], docling, marker-pdf, or llama-parse (paid tier available)

Embedding model upgrade recommendations (sentence-transformers):
- Current default (all-MiniLM-L6-v2) is outdated (2021–2022)
- Strong 2025–2026 open-source choices (MTEB leaderboard leaders):
  - BAAI/bge-m3                 → multilingual, dense + sparse + ColBERT, very strong
  - nomic-ai/nomic-embed-text-v1.5 or v2 → excellent English, long context
  - BAAI/bge-large-en-v1.5 or bge-base-en-v1.5
  - jinaai/jina-embeddings-v3
  - intfloat/e5-mistral-7b-instruct (heavier but top-tier)
  - Qwen/Qwen3-Embedding-* family (very recent leaders in multilingual)

Vector store (local / lightweight – you don't have one yet):
- **FAISS** (faiss-cpu ≥ 1.8.0)     → fastest retrieval, GPU option, very lightweight
- **Chroma** (chromadb)             → easiest API, great developer experience, persistent
- **Qdrant** (local mode)           → excellent filtering + payload, modern

Chunking & retrieval best practices to follow:
- Chunk size: 800–1800 characters (test different values)
- Chunk overlap: 15–25% (120–400 chars)
- Splitter: RecursiveCharacterTextSplitter or semantic chunking
- Retrieval: top-k = 3–8 + optional MMR reranking for diversity
- Add source citation (page number + short excerpt)

LLM integration options (you don't have one yet):
- Local → Ollama (llama3.1:8b, qwen2.5:14b, deepseek-r1, mistral-nemo, phi-4, etc.)
- API   → OpenAI (gpt-4o-mini), Grok, Anthropic Claude 3.5 Haiku, DeepSeek, etc.
- Prompt must enforce: "Answer only using the provided context. If not present → say 'I don't have information about that in the document.'"

Expected API Endpoints (suggested – you can confirm/modify):
- POST /upload-pdf    → upload one or multiple PDFs → index them (ingest + embed + store)
- POST /ask           → { "question": str, "pdf_id?": optional } → retrieve + generate answer
- GET  /health        → status + loaded PDFs count / memory usage
- DELETE /clear-index → reset vector store (useful in dev)

Constraints / Non-functional requirements:
- All answers **must** come from the uploaded PDF(s) only.
- Support for tables is desirable but not mandatory yet.
- Prefer local/offline execution when possible (privacy).
- FastAPI should be production-ready (gunicorn + uvicorn workers).
- Keep dependencies reasonably minimal and modern.

Current status:
- You have a FastAPI skeleton + PDF upload capability (likely).
- PDF text extraction is still using deprecated pypdf2.
- No vector database or embeddings pipeline implemented yet.
- No LLM calling layer yet.
- Goal = build a minimal working RAG → then improve quality (better chunks, embeddings, citation, table support, scanned PDF OCR, etc.)

Task for the LLM:
You are an expert Python/RAG/FastAPI developer.
Use the above information as full context.
When I give you a specific request (implement endpoint X, fix bug Y, optimize Z, add feature A, refactor module B, suggest better prompt, etc.),
follow modern 2026 best practices, write clean/type-hinted code, include error handling, logging, and comments.
Prefer composition over inheritance. Use async where it makes sense.

---

# Full RAG Modernization - Complete Checklist

## 📋 PHASE 1: Dependencies & Infrastructure Update

### 1.1 Update `requirements.txt`
- [ ] Replace `pypdf2` with `pymupdf` (PyMuPDF/fitz) for better PDF extraction
- [ ] Add `faiss-cpu>=1.8.0` for vector database
- [ ] Update `sentence-transformers` to latest version
- [ ] Add modern embedding model dependencies
- [ ] Remove numpy upper bound restriction (< 2.0.0)
- [ ] Add `langchain-community` for text splitting utilities
- [ ] Add `openai` or `ollama` client for LLM integration
- [ ] Keep existing FastAPI, uvicorn, gunicorn versions
- [ ] Ensure all dependencies are compatible

### 1.2 Project Structure Reorganization
- [ ] Create `src/` directory for better organization
- [ ] Create `src/config/` for configuration management
- [ ] Create `src/services/` for business logic
- [ ] Create `src/models/` for Pydantic models
- [ ] Create `src/utils/` for utilities
- [ ] Create `data/` directory for vector store persistence
- [ ] Create `logs/` directory for application logs

## 📋 PHASE 2: Core RAG Components

### 2.1 PDF Processing Module (`src/services/pdf_processor.py`)
- [ ] Implement PyMuPDF-based PDF text extraction
- [ ] Extract text with page number tracking
- [ ] Handle text cleaning and normalization
- [ ] Preserve verse references (Bg X.Y format)
- [ ] Extract metadata (chapter, verse, page numbers)
- [ ] Add error handling for corrupted PDFs
- [ ] Add logging for extraction process

### 2.2 Text Chunking Module (`src/services/chunker.py`)
- [ ] Implement semantic chunking strategy
- [ ] Configure chunk size: 1000-1500 characters
- [ ] Configure chunk overlap: 200-300 characters (20%)
- [ ] Preserve verse boundaries (don't split verses)
- [ ] Add metadata to each chunk (page, chapter, verse)
- [ ] Implement RecursiveCharacterTextSplitter
- [ ] Add custom splitter for Gita-specific structure

### 2.3 Embedding Service (`src/services/embeddings.py`)
- [ ] Implement embedding generation using `sentence-transformers`
- [ ] Use modern model: `BAAI/bge-base-en-v1.5` or `nomic-ai/nomic-embed-text-v1.5`
- [ ] Add batch processing for efficiency
- [ ] Implement caching mechanism
- [ ] Add error handling and retry logic
- [ ] Support async operations
- [ ] Add progress tracking for large documents

### 2.4 Vector Store Service (`src/services/vector_store.py`)
- [ ] Implement FAISS vector database integration
- [ ] Create index initialization
- [ ] Implement document ingestion (embed + store)
- [ ] Implement similarity search (top-k retrieval)
- [ ] Add metadata filtering capabilities
- [ ] Implement index persistence (save/load)
- [ ] Add index clearing functionality
- [ ] Implement MMR (Maximal Marginal Relevance) for diversity

### 2.5 LLM Integration Service (`src/services/llm_service.py`)
- [ ] Implement LLM client (OpenAI/Ollama/both)
- [ ] Create RAG-specific prompt templates
- [ ] Implement context injection
- [ ] Add source citation formatting
- [ ] Implement streaming responses (optional)
- [ ] Add fallback mechanisms
- [ ] Implement response validation
- [ ] Add token counting and cost tracking

### 2.6 RAG Orchestrator (`src/services/rag_orchestrator.py`)
- [ ] Implement end-to-end RAG pipeline
- [ ] Query processing and enhancement
- [ ] Vector retrieval (top-k chunks)
- [ ] Context assembly and ranking
- [ ] LLM answer generation
- [ ] Source attribution and citation
- [ ] Response post-processing
- [ ] Add hybrid search (combine with existing Q&A pairs)

## 📋 PHASE 3: API Layer Modernization

### 3.1 Pydantic Models (`src/models/schemas.py`)
- [ ] `PDFUploadRequest` model
- [ ] `QuestionRequest` model (enhanced)
- [ ] `AnswerResponse` model with sources
- [ ] `SourceCitation` model (page, verse, excerpt)
- [ ] `HealthResponse` model
- [ ] `IndexStats` model
- [ ] Error response models

### 3.2 API Endpoints (`src/api/routes.py` or updated `app.py`)
- [ ] **POST /upload-pdf** - Upload and index PDF
  - Accept PDF file upload
  - Extract text and create chunks
  - Generate embeddings
  - Store in vector database
  - Return indexing stats
  
- [ ] **POST /ask** - Enhanced question answering
  - Accept question + optional filters
  - Retrieve relevant chunks from vector store
  - Generate answer using LLM
  - Return answer with source citations
  - Include confidence scores
  
- [ ] **GET /health** - Enhanced health check
  - System status
  - Vector store stats (document count, index size)
  - LLM connectivity status
  - Memory usage
  
- [ ] **DELETE /clear-index** - Clear vector database
  - Remove all indexed documents
  - Reset vector store
  - Return confirmation
  
- [ ] **GET /sources/{query}** - Get relevant sources without LLM
  - Retrieve top-k chunks for a query
  - Return raw sources with metadata
  
- [ ] **GET /stats** - Get indexing statistics
  - Total chunks indexed
  - Embedding model info
  - Last update timestamp

### 3.3 Configuration Management (`src/config/settings.py`)
- [ ] Environment variable management
- [ ] LLM API keys configuration
- [ ] Embedding model selection
- [ ] Vector store parameters
- [ ] Chunking parameters
- [ ] Retrieval parameters (top-k, similarity threshold)
- [ ] Logging configuration

## 📋 PHASE 4: Migration & Compatibility

### 4.1 Preserve Existing Features
- [ ] Keep existing verse lookup functionality
- [ ] Preserve character information endpoints
- [ ] Maintain FAQ/Q&A pairs as fallback
- [ ] Keep modern life advice mapping
- [ ] Implement hybrid retrieval (vector + keyword)

### 4.2 Backward Compatibility
- [ ] Ensure existing `/ask` endpoint still works
- [ ] Maintain response format compatibility
- [ ] Add deprecation warnings for old features
- [ ] Create migration guide

## 📋 PHASE 5: Quality & Production Readiness

### 5.1 Error Handling & Validation
- [ ] Add comprehensive try-catch blocks
- [ ] Implement custom exception classes
- [ ] Add input validation for all endpoints
- [ ] Add rate limiting (optional)
- [ ] Add request timeout handling

### 5.2 Logging & Monitoring
- [ ] Structured logging with JSON format
- [ ] Log all API requests/responses
- [ ] Log embedding generation
- [ ] Log LLM calls and tokens
- [ ] Add performance metrics
- [ ] Add error tracking

### 5.3 Testing
- [ ] Unit tests for PDF processing
- [ ] Unit tests for chunking
- [ ] Unit tests for embeddings
- [ ] Integration tests for RAG pipeline
- [ ] API endpoint tests
- [ ] Test with sample Gita questions

### 5.4 Documentation
- [ ] Update README.md with new architecture
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Create deployment guide
- [ ] Add configuration guide
- [ ] Document embedding model selection
- [ ] Add troubleshooting guide

### 5.5 Docker & Deployment
- [ ] Update Dockerfile for new dependencies
- [ ] Optimize Docker image size
- [ ] Add health check in Docker
- [ ] Update cloudbuild.yaml
- [ ] Add environment variable configuration
- [ ] Test Cloud Run deployment

## 📋 PHASE 6: Optimization & Enhancement

### 6.1 Performance Optimization
- [ ] Implement caching for frequent queries
- [ ] Add async/await throughout
- [ ] Optimize embedding batch processing
- [ ] Add connection pooling for LLM
- [ ] Implement lazy loading

### 6.2 Advanced Features (Optional)
- [ ] Add query expansion/rewriting
- [ ] Implement re-ranking with cross-encoder
- [ ] Add conversation history support
- [ ] Implement multi-turn dialogue
- [ ] Add verse reference auto-detection
- [ ] Support for Sanskrit text (if in PDF)

---

## 🎯 Execution Order

1. **First**: Update dependencies and create new project structure
2. **Second**: Build core services (PDF → Chunking → Embeddings → Vector Store)
3. **Third**: Implement LLM integration and RAG orchestrator
4. **Fourth**: Update API endpoints
5. **Fifth**: Test and validate
6. **Sixth**: Update Docker and deploy

---

## ⏱️ Estimated Timeline

- **Phase 1-2**: Core infrastructure (1-2 hours of development)
- **Phase 3**: API layer (1 hour)
- **Phase 4**: Migration (30 mins)
- **Phase 5**: Quality & testing (1 hour)
- **Phase 6**: Optimization (ongoing)