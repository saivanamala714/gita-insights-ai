"""
Bhagavad Gita RAG API - Version 2.0
Modern RAG implementation with vector search and LLM integration
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router, set_rag_orchestrator
from src.config.settings import get_settings
from src.services.rag_orchestrator import RAGOrchestrator

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    settings = get_settings()
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if settings.log_format == "json":
        # For production, use JSON logging
        import json
        
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(log_format))
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        handlers=[handler]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

setup_logging()
logger = logging.getLogger(__name__)

# Initialize RAG orchestrator
rag_orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    global rag_orchestrator
    settings = get_settings()
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Embedding Model: {settings.embedding_model_name}")
    
    # Initialize RAG orchestrator
    rag_orchestrator = RAGOrchestrator(settings)
    set_rag_orchestrator(rag_orchestrator)
    
    # Try to load existing index
    logger.info("Attempting to load existing vector index...")
    if rag_orchestrator.load_index():
        logger.info("✓ Vector index loaded successfully")
    else:
        logger.warning("No existing index found. Will index on first request or manual trigger.")
        logger.info("To index the PDF, send a POST request to /upload-pdf")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RAG-based Q&A system for the Bhagavad Gita",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Include routes
app.include_router(router, prefix="", tags=["RAG"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "endpoints": {
            "ask": "POST /ask - Ask a question",
            "sources": "GET /sources/{query} - Get relevant sources",
            "stats": "GET /stats - Get system statistics",
            "health": "GET /health - Health check",
            "upload": "POST /upload-pdf - Re-index PDF",
            "clear": "DELETE /clear-index - Clear vector index"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_v2:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
