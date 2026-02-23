"""
Gemini-based embedding service for lightweight production deployment.
Uses Google's Gemini API instead of sentence-transformers to avoid heavy ML dependencies.
"""

import os
import logging
from typing import List
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiEmbeddingService:
    """Generate embeddings using Gemini API"""
    
    def __init__(self):
        """Initialize Gemini embedding service"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model_name = "models/gemini-embedding-001"  # Correct model name for Gemini embeddings
        logger.info(f"Initialized Gemini embedding service with model: {self.model_name}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query.
        
        Args:
            query: Query text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        # Gemini text-embedding-004 produces 768-dimensional embeddings
        return 768


# Global instance
gemini_embeddings = None

def get_gemini_embeddings():
    """Get or create global Gemini embedding service instance"""
    global gemini_embeddings
    if gemini_embeddings is None:
        gemini_embeddings = GeminiEmbeddingService()
    return gemini_embeddings
