"""
API Routes for RAG System
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from ..config.settings import get_settings
from ..models.schemas import (
    AnswerResponse,
    ErrorResponse,
    HealthResponse,
    IndexStats,
    QuestionRequest,
    SourcesResponse,
    PDFUploadResponse
)
from ..services.rag_orchestrator import RAGOrchestrator
from ..utils.conversation_logger import ConversationLogger
from ..services.notification_service import NotificationService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize RAG orchestrator (will be set by main app)
rag: Optional[RAGOrchestrator] = None

# Initialize conversation logger
conversation_logger = ConversationLogger("CONVERSATION_HISTORY.md")

# Initialize notification service
notification_service = NotificationService()


def set_rag_orchestrator(orchestrator: RAGOrchestrator):
    """Set the RAG orchestrator instance"""
    global rag
    rag = orchestrator


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Answer a question using RAG pipeline
    
    - **question**: The question to answer
    - **top_k**: Number of source documents to retrieve (optional)
    - **include_sources**: Whether to include source citations (optional)
    """
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        logger.info(f"Received question: {request.question[:100]}")
        
        # Send notification about new question
        try:
            notification_service.send_question_alert(
                question=request.question,
                user_info=None  # Can add IP, user agent, etc. if needed
            )
        except Exception as notif_error:
            logger.warning(f"Failed to send notification: {notif_error}")
        
        response = rag.answer_question(
            question=request.question,
            top_k=request.top_k,
            include_sources=request.include_sources
        )
        
        # Automatically log the conversation
        try:
            conversation_logger.log_conversation(
                question=request.question,
                answer=response.answer,
                sources=response.sources,
                confidence=response.confidence,
                processing_time_ms=response.processing_time_ms,
                metadata={
                    "top_k": request.top_k,
                    "include_sources": request.include_sources
                }
            )
        except Exception as log_error:
            logger.warning(f"Failed to log conversation: {log_error}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error answering question: {e}", exc_info=True)
        # Log the error
        try:
            conversation_logger.log_error(request.question, str(e))
        except Exception as log_error:
            logger.warning(f"Failed to log error: {log_error}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and index a PDF file
    
    Note: Currently uses the default Bhagavad Gita PDF.
    This endpoint will re-index the existing PDF.
    """
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        logger.info("Re-indexing PDF")
        stats = rag.index_pdf()
        
        return PDFUploadResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error indexing PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/{query}", response_model=SourcesResponse)
async def get_sources(query: str, top_k: int = 5):
    """
    Get relevant source documents without generating an answer
    
    - **query**: Search query
    - **top_k**: Number of sources to retrieve
    """
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        sources = rag.get_sources_only(query, top_k=top_k)
        
        return SourcesResponse(
            query=query,
            sources=sources,
            total_found=len(sources)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving sources: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=IndexStats)
async def get_stats():
    """Get indexing and system statistics"""
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        stats = rag.get_stats()
        settings = get_settings()
        
        return IndexStats(
            total_chunks=stats.get("total_chunks", 0),
            embedding_model=stats.get("embedding_model", "unknown"),
            vector_dimension=stats.get("embedding_dimension", 0),
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear-index")
async def clear_index():
    """Clear the vector database"""
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        rag.clear_index()
        return {"message": "Vector index cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing index: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check endpoint
    
    Returns system status, component health, and statistics
    """
    try:
        settings = get_settings()
        
        # Get RAG health if available
        vector_store_status = "not_initialized"
        llm_status = "not_initialized"
        index_stats = None
        
        if rag:
            health = rag.check_health()
            vector_store_status = health.get("vector_store", "unknown")
            llm_status = health.get("llm_service", "unknown")
            
            # Get stats
            stats = rag.get_stats()
            index_stats = IndexStats(
                total_chunks=stats.get("total_chunks", 0),
                embedding_model=stats.get("embedding_model", "unknown"),
                vector_dimension=stats.get("embedding_dimension", 0),
                last_updated=datetime.utcnow()
            )
        
        # System info
        import sys
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        system_info = {
            "python_version": ".".join(map(str, sys.version_info[:3])),
            "platform": sys.platform,
            "memory_usage_mb": round(memory_info.rss / (1024 * 1024), 2),
            "port": settings.port
        }
        
        return HealthResponse(
            status="healthy",
            service=settings.app_name,
            version=settings.app_version,
            timestamp=datetime.utcnow(),
            vector_store_status=vector_store_status,
            llm_status=llm_status,
            index_stats=index_stats,
            system=system_info
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        # Return 200 with error info to avoid marking service as down
        return JSONResponse(
            status_code=200,
            content={
                "status": "unhealthy",
                "error": str(e)[:500],
                "timestamp": datetime.utcnow().isoformat()
            }
        )
