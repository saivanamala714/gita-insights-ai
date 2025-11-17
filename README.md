# Bhagavad Gita Q&A System

A Retrieval-Augmented Generation (RAG) based question-answering system for the Bhagavad Gita As It Is PDF.

## Features

- Extracts text from the Bhagavad Gita PDF
- Processes and chunks the text for efficient retrieval
- Uses semantic search to find relevant passages
- Provides answers based on the content of the Bhagavad Gita
- Simple REST API interface

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure you have the PDF file `11-Bhagavad-gita_As_It_Is.pdf` in the project directory

## Usage

1. Start the FastAPI server:
   ```bash
   uvicorn app:app --reload
   ```

2. The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /ask` - Submit a question about the Bhagavad Gita
  - Request body: `{"question": "What is the essence of the Bhagavad Gita?"}`
  - Response: `{"answer": "...", "sources": [...]}`

- `GET /health` - Check if the service is running
  - Response: `{"status": "healthy"}`

## Example

```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the main teaching of the Bhagavad Gita?"}'
```

## Implementation Details

This system uses:
- PyPDF2 for PDF text extraction
- LangChain for text processing and document management
- Sentence Transformers (all-MiniLM-L6-v2) for embeddings
- FAISS for efficient similarity search
- FastAPI for the web server

## Note

This is a basic implementation. For production use, consider:
- Adding authentication
- Implementing rate limiting
- Adding more sophisticated error handling
- Using a more powerful embedding model or LLM for better answers
# gita-insights-ai
