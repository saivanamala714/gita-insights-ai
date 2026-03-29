Instruction Set: Modify gita-insights-ai for Google Cloud Deployment
Goal:
Make the app production-ready on Google Cloud (Cloud Run + Firestore) with better accuracy, reliable chat logging, and controlled costs. Keep the spiritual tone respectful and answers grounded in the Gita PDF.
Target Stack on GCP:

Compute: Cloud Run (serverless containers)
Vector Store: Switch from FAISS → Vertex AI Vector Search or Firestore + Vector Embeddings (cheaper & native)
Chat History: Firestore (you already started this)
Embeddings: Local BAAI/bge-m3 (one-time) + Gemini Embedding API for queries (native to GCP)
LLM: Google Gemini 1.5 Flash or Pro (fast + cost-effective on GCP)
Deployment: Cloud Build + Cloud Run

Step 1: Project Cleanup (Do This First)

Delete or archive duplicate/confusing files:
Keep only one main file: app.py (make it the single source of truth)
Delete or move to archive/ folder: app_optimized.py, main.py, main_v2.py, app_backup.py

Create a clean folder structure:textgita-insights-ai/
├── app/
│   ├── main.py                 # Main FastAPI app
│   ├── routers/
│   │   └── gita.py             # /ask endpoint
│   ├── services/
│   │   ├── rag_service.py
│   │   ├── embedding_service.py
│   │   └── response_processor.py
│   └── core/
│       └── config.py
├── local_ingest/
│   └── ingest.py               # Generate embeddings with BGE-M3
├── Dockerfile
├── cloudbuild.yaml
├── requirements.txt
└── .env.example

Step 2: Key Technical Improvements
A. Change Vector Store

Remove FAISS dependency
Use Firestore with vector embeddings (or Vertex AI Vector Search for better performance)
Store chunks with embedding field (array of floats)

B. Improve Embeddings

Update local_ingest/ingest.py to use BAAI/bge-m3 (1024 dim) instead of all-MiniLM or Gemini for document embeddings.
For query embeddings: Use Gemini Embedding API (embedding-001) – native and cheaper on GCP.

C. LLM Integration

Replace any direct Gemini calls with proper Gemini SDK (google-generativeai)
Use gemini-1.5-flash for fast responses (cheaper) and gemini-1.5-pro for complex questions (configurable)

D. Chat Logging

Use Firestore collection chat_logs to store:
session_id, question, answer, context_used, verse_references, timestamp, metadata


E. Strong System Prompt
Update the prompt to be respectful and accurate:
"You are a knowledgeable assistant on Bhagavad Gita As It Is by Srila Prabhupada. Answer only using the provided verses and context. Be respectful, accurate, and spiritual. If the answer is not in the context, say: 'I could not find a direct reference in the Bhagavad Gita for this question.'"
Step 3: Google Cloud Specific Setup

Environment Variables (add to Cloud Run):
PROJECT_ID
GEMINI_API_KEY (or use Application Default Credentials)
FIRESTORE_COLLECTION_CHUNKS
FIRESTORE_COLLECTION_LOGS

Update cloudbuild.yaml:
Make sure it builds the Docker image and deploys to Cloud Run with proper service account.

Service Account Permissions:
Give the Cloud Run service account:
Firestore access
Vertex AI User (if using Vector Search)
Secret Manager access (for API keys)


Dockerfile Improvements:
Use python:3.12-slim
Multi-stage build to reduce image size
Set PORT environment variable for Cloud Run


Step 4: Implementation Priority Order
Phase 1 (High Priority - This Week)

Clean up duplicate files and organize into app/ structure
Update local_ingest/ingest.py to use BAAI/bge-m3
Modify /ask endpoint to use Gemini 1.5 Flash + strong system prompt
Fix streaming + reliable logging to Firestore

Phase 2

Replace FAISS with Firestore vector search
Add batch upload for 2573+ chunks
Add rate limiting
Improve hybrid search (vector + keyword on verse text)

Phase 3

Add feedback system (thumbs up/down)
Create training data export endpoint
Add caching for common questions

Step 5: Testing & Deployment Checklist

Test with 5–10 spiritual questions (normal, fuzzy, out-of-context)
Verify answers cite correct chapter/verse
Deploy using gcloud builds submit --config cloudbuild.yaml
Monitor costs in Google Cloud Billing (especially Gemini API usage)