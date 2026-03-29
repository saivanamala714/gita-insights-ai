# Pre-Generated Embeddings Setup

## Overview

To avoid regenerating embeddings on the server every time you deploy (which takes 25-30 minutes), we now **pre-generate embeddings locally** and include them in the Docker image.

## How It Works

### 1. Local Generation
- Embeddings are generated once on your local machine
- Saved to `data/vector_store/` directory
- Contains two files:
  - `index.faiss` (~5.4 MB) - FAISS vector index
  - `metadata.pkl` (~1.7 MB) - Chunk metadata and text

### 2. Docker Image Inclusion
- The `.dockerignore` file is configured to **include** the `data/vector_store/` directory
- The `Dockerfile` copies the pre-generated vector store into the image
- When the container starts, it loads the existing embeddings instead of regenerating them

### 3. Server Deployment
- Server starts immediately without embedding generation
- Application is ready to serve requests in seconds instead of minutes
- No computational overhead for embedding generation

## Current Status

✅ **Vector store already exists** at `data/vector_store/`
- Generated from: `11-Bhagavad-gita_As_It_Is.pdf`
- Total chunks: ~1,751
- Embedding model: (check `src/config/settings.py` for model name)

## When to Regenerate Embeddings

You need to regenerate embeddings locally when:

1. **PDF content changes** - If you update the Bhagavad Gita PDF
2. **Chunking strategy changes** - If you modify chunk size or overlap settings
3. **Embedding model changes** - If you switch to a different embedding model
4. **Processing logic changes** - If you update document processing code

## How to Regenerate Embeddings Locally

### Option 1: Using the Script (Recommended)

```bash
# From the project root directory
python generate_embeddings_local.py
```

This script will:
- Check if embeddings already exist
- Ask for confirmation before regenerating
- Process the PDF and create chunks
- Generate embeddings with progress bar
- Save to `data/vector_store/`
- Display statistics

### Option 2: Manual Python Commands

```python
from src.services.document_processor import DocumentProcessor
from src.services.embeddings import EmbeddingService
from src.services.vector_store import VectorStore
from src.config.settings import get_settings

settings = get_settings()

# Process PDF
doc_processor = DocumentProcessor(settings)
chunks = doc_processor.process_pdf(settings.pdf_path)

# Generate embeddings
embedding_service = EmbeddingService(settings)
texts = [chunk.text for chunk in chunks]
embeddings = embedding_service.embed_texts(texts)

# Save to vector store
vector_store = VectorStore(settings)
vector_store.initialize(embedding_service.get_embedding_dimension())
vector_store.add_documents(chunks, embeddings)
vector_store.save()
```

## Deployment Workflow

### First Time Setup (Already Done ✅)
1. Generate embeddings locally
2. Commit `data/vector_store/` to git (if desired) OR just keep locally
3. Build Docker image (embeddings will be included)
4. Deploy to server

### Subsequent Deployments
1. Build Docker image
2. Deploy to server
3. Server starts immediately with pre-loaded embeddings

### If PDF Changes
1. Update the PDF file locally
2. Run `python generate_embeddings_local.py`
3. Rebuild Docker image
4. Redeploy

## Performance Comparison

| Scenario | Time to Ready |
|----------|---------------|
| **Without pre-generated embeddings** | ~25-30 minutes |
| **With pre-generated embeddings** | ~10-30 seconds |

## File Sizes

- `index.faiss`: ~5.4 MB
- `metadata.pkl`: ~1.7 MB
- **Total**: ~7.1 MB added to Docker image

This is a small price to pay for saving 25-30 minutes on every deployment!

## Configuration Files Modified

### `.dockerignore`
```
# Data directory (exclude by default)
data/
# But include the pre-generated vector store
!data/vector_store/
!data/vector_store/*.faiss
!data/vector_store/*.pkl
```

### `Dockerfile`
```dockerfile
# Copy pre-generated vector store (embeddings) to avoid regenerating on server
COPY data/vector_store/ ./data/vector_store/
```

## Troubleshooting

### Embeddings not loading on server
- Check that `data/vector_store/` exists in the Docker image
- Verify `.dockerignore` has the correct exclusion rules
- Ensure `Dockerfile` copies the vector store directory

### Need to regenerate embeddings
- Run `python generate_embeddings_local.py`
- Wait for completion (25-30 minutes)
- Rebuild and redeploy

### Vector store corrupted
- Delete `data/vector_store/` directory
- Run `python generate_embeddings_local.py`
- Rebuild Docker image

## Git Considerations

You have two options for version control:

### Option 1: Commit Vector Store (Recommended)
```bash
# Remove data/ from .gitignore for vector_store
git add data/vector_store/
git commit -m "Add pre-generated embeddings"
```

**Pros**: Team members get embeddings automatically
**Cons**: ~7 MB added to repository

### Option 2: Keep Local Only
Keep `data/` in `.gitignore` and generate locally before each build.

**Pros**: Smaller repository
**Cons**: Each developer must generate embeddings locally

## Notes

- The current embeddings are based on the `11-Bhagavad-gita_As_It_Is.pdf` file
- Embedding model and settings are defined in `src/config/settings.py`
- Vector store uses FAISS for efficient similarity search
- Embeddings are normalized for cosine similarity
