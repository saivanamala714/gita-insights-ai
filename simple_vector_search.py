"""
Simple vector search using cosine similarity.
Lightweight alternative to FAISS for production deployment.
"""

import logging
import pickle
from typing import List, Tuple, Dict, Any
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    """Simple vector store using numpy for cosine similarity search"""
    
    def __init__(self):
        """Initialize vector store"""
        self.embeddings = None
        self.documents = []
        self.dimension = None
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Add documents and their embeddings to the store.
        
        Args:
            documents: List of document dictionaries with 'text' and 'metadata'
            embeddings: List of embedding vectors
        """
        if len(documents) != len(embeddings):
            raise ValueError(f"Mismatch: {len(documents)} documents but {len(embeddings)} embeddings")
        
        self.documents = documents
        self.embeddings = np.array(embeddings, dtype=np.float32)
        self.dimension = self.embeddings.shape[1]
        
        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        self.embeddings = self.embeddings / (norms + 1e-10)
        
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        Search for similar documents using cosine similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (index, similarity_score, document) tuples
        """
        if self.embeddings is None or len(self.embeddings) == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Normalize query embedding
        query_vec = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        query_norm = np.linalg.norm(query_vec)
        query_vec = query_vec / (query_norm + 1e-10)
        
        # Compute cosine similarity
        similarities = np.dot(self.embeddings, query_vec.T).flatten()
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return results
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.3:  # Minimum similarity threshold
                results.append((int(idx), score, self.documents[idx]))
        
        logger.info(f"Found {len(results)} results above threshold")
        return results
    
    def save(self, path: str):
        """Save vector store to disk"""
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'embeddings': self.embeddings,
            'documents': self.documents,
            'dimension': self.dimension
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"Vector store saved to {save_path}")
    
    def load(self, path: str) -> bool:
        """Load vector store from disk"""
        load_path = Path(path)
        
        if not load_path.exists():
            logger.warning(f"Vector store file not found: {load_path}")
            return False
        
        try:
            with open(load_path, 'rb') as f:
                data = pickle.load(f)
            
            self.embeddings = data['embeddings']
            self.documents = data['documents']
            self.dimension = data['dimension']
            
            logger.info(f"Vector store loaded from {load_path} with {len(self.documents)} documents")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_documents": len(self.documents),
            "dimension": self.dimension,
            "has_embeddings": self.embeddings is not None
        }


# Global instance
vector_store = None

def get_vector_store():
    """Get or create global vector store instance"""
    global vector_store
    if vector_store is None:
        vector_store = SimpleVectorStore()
        # Try to load the saved index
        vector_store.load('data/gemini_vector_index.pkl')
    return vector_store
