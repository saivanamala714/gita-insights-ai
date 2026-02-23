"""
RAG Orchestrator
Coordinates the end-to-end RAG pipeline
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

from ..config.settings import Settings, get_settings
from ..models.schemas import AnswerResponse, SourceCitation
from .chunker import TextChunker
from .embeddings import EmbeddingService
from .llm_service import LLMService
from .pdf_processor import PDFProcessor
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGOrchestrator:
    """Orchestrates the complete RAG pipeline"""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        
        # Initialize services
        self.pdf_processor = PDFProcessor()
        self.chunker = TextChunker(self.settings)
        self.embedding_service = EmbeddingService(self.settings)
        self.vector_store = VectorStore(self.settings)
        self.llm_service = LLMService(self.settings)
        
        self._indexed = False
    
    def index_pdf(self, pdf_path: Optional[Path] = None) -> Dict:
        """
        Index a PDF file into the vector store
        
        Args:
            pdf_path: Path to PDF file (uses default if not provided)
            
        Returns:
            Dictionary with indexing statistics
        """
        start_time = time.time()
        pdf_path = pdf_path or self.settings.full_pdf_path
        
        logger.info(f"Starting PDF indexing: {pdf_path}")
        
        # Step 1: Extract text from PDF
        logger.info("Step 1: Extracting text from PDF")
        documents = self.pdf_processor.extract_text_from_pdf(pdf_path)
        
        # Step 2: Chunk documents
        logger.info("Step 2: Chunking documents")
        chunks = self.chunker.chunk_documents(documents)
        
        # Step 3: Generate embeddings
        logger.info("Step 3: Generating embeddings")
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_service.embed_texts(texts)
        
        # Step 4: Initialize and populate vector store
        logger.info("Step 4: Building vector index")
        dimension = self.embedding_service.get_embedding_dimension()
        self.vector_store.initialize(dimension)
        self.vector_store.add_documents(chunks, embeddings)
        
        # Step 5: Save vector store
        logger.info("Step 5: Saving vector store")
        self.vector_store.save()
        
        self._indexed = True
        processing_time = (time.time() - start_time) * 1000
        
        stats = {
            "success": True,
            "message": "PDF indexed successfully",
            "chunks_created": len(chunks),
            "embeddings_generated": len(embeddings),
            "processing_time_ms": processing_time
        }
        
        logger.info(f"Indexing complete: {stats}")
        return stats
    
    def load_index(self) -> bool:
        """
        Load existing vector store from disk
        
        Returns:
            True if loaded successfully
        """
        logger.info("Loading existing vector index")
        success = self.vector_store.load()
        
        if success:
            self._indexed = True
            # Ensure embedding service is loaded
            self.embedding_service.load_model()
            logger.info("Vector index loaded successfully")
        else:
            logger.warning("Failed to load vector index")
        
        return success
    
    def answer_question(
        self,
        question: str,
        top_k: Optional[int] = None,
        include_sources: bool = True
    ) -> AnswerResponse:
        """
        Answer a question using RAG pipeline
        
        Args:
            question: User's question
            top_k: Number of sources to retrieve
            include_sources: Include source citations in response
            
        Returns:
            AnswerResponse object
        """
        start_time = time.time()
        
        # Ensure index is loaded
        if not self._indexed:
            if not self.load_index():
                # Try to index if no index exists
                logger.info("No index found, indexing PDF")
                self.index_pdf()
        
        top_k = top_k or self.settings.vector_top_k
        
        logger.info(f"Answering question: {question[:100]}...")
        
        # Step 1: Generate query embedding
        logger.info("Step 1: Generating query embedding")
        query_embedding = self.embedding_service.embed_single(question)
        
        # Step 2: Retrieve relevant sources
        logger.info("Step 2: Retrieving relevant sources")
        sources = self.vector_store.search_and_retrieve(
            query_embedding,
            top_k=top_k,
            use_mmr=self.settings.use_mmr
        )
        
        if not sources:
            logger.warning("No relevant sources found")
            return AnswerResponse(
                answer="I couldn't find relevant information in the Bhagavad Gita to answer this question.",
                sources=[],
                confidence=0.0,
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        # Step 3: Generate answer using LLM
        logger.info("Step 3: Generating answer with LLM")
        answer = self.llm_service.generate_answer(question, sources)
        
        # Calculate confidence based on source similarity scores
        avg_similarity = sum(s.similarity_score or 0 for s in sources) / len(sources)
        confidence = min(avg_similarity, 1.0)
        
        processing_time = (time.time() - start_time) * 1000
        
        response = AnswerResponse(
            answer=answer,
            sources=sources if include_sources else [],
            confidence=confidence,
            processing_time_ms=processing_time
        )
        
        logger.info(f"Answer generated in {processing_time:.2f}ms")
        return response
    
    def get_sources_only(self, query: str, top_k: int = 5) -> List[SourceCitation]:
        """
        Retrieve sources without generating an answer
        
        Args:
            query: Search query
            top_k: Number of sources
            
        Returns:
            List of source citations
        """
        if not self._indexed:
            self.load_index()
        
        query_embedding = self.embedding_service.embed_single(query)
        sources = self.vector_store.search_and_retrieve(
            query_embedding,
            top_k=top_k,
            use_mmr=self.settings.use_mmr
        )
        
        return sources
    
    def clear_index(self) -> None:
        """Clear the vector store"""
        self.vector_store.clear()
        self._indexed = False
        logger.info("Vector index cleared")
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        vector_stats = self.vector_store.get_stats()
        
        return {
            "indexed": self._indexed,
            "embedding_model": self.embedding_service.get_model_name(),
            "embedding_dimension": vector_stats.get("dimension"),
            "total_chunks": vector_stats.get("total_chunks", 0),
            "llm_provider": self.settings.llm_provider,
            "llm_model": self.settings.openai_model if self.settings.llm_provider == "openai" else self.settings.ollama_model
        }
    
    def check_health(self) -> Dict:
        """
        Check health of all RAG components
        
        Returns:
            Health status dictionary
        """
        health = {
            "vector_store": "healthy" if self._indexed else "not_indexed",
            "embedding_service": "healthy",
            "llm_service": "unknown"
        }
        
        # Check LLM connectivity
        try:
            if self.llm_service.check_connection():
                health["llm_service"] = "healthy"
            else:
                health["llm_service"] = "unhealthy"
        except Exception as e:
            health["llm_service"] = f"error: {str(e)[:100]}"
        
        return health
