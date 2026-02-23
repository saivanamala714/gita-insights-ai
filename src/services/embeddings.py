"""
Embedding Service using Sentence Transformers
Generates vector embeddings for text chunks
"""

import logging
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from ..config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings using modern sentence transformers"""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        self.model: Optional[SentenceTransformer] = None
        self._model_loaded = False
    
    def load_model(self) -> None:
        """Load the embedding model"""
        if self._model_loaded:
            return
        
        logger.info(f"Loading embedding model: {self.settings.embedding_model_name}")
        try:
            self.model = SentenceTransformer(self.settings.embedding_model_name)
            self._model_loaded = True
            logger.info(f"Model loaded successfully. Dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed_texts(self, texts: List[str], show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
            show_progress: Show progress bar
            
        Returns:
            Numpy array of embeddings (n_texts, embedding_dim)
        """
        if not self._model_loaded:
            self.load_model()
        
        if not texts:
            return np.array([])
        
        logger.info(f"Generating embeddings for {len(texts)} texts")
        
        try:
            # Generate embeddings in batches
            embeddings = self.model.encode(
                texts,
                batch_size=self.settings.embedding_batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2 normalization for cosine similarity
            )
            
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def embed_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string
            
        Returns:
            Numpy array embedding (embedding_dim,)
        """
        embeddings = self.embed_texts([text], show_progress=False)
        return embeddings[0]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        if not self._model_loaded:
            self.load_model()
        return self.model.get_sentence_embedding_dimension()
    
    def get_model_name(self) -> str:
        """Get the name of the embedding model"""
        return self.settings.embedding_model_name
