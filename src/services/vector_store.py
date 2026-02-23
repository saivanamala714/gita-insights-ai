"""
Vector Store Service using FAISS
Manages document indexing and similarity search
"""

import logging
import pickle
from pathlib import Path
from typing import List, Optional, Tuple

import faiss
import numpy as np

from ..config.settings import Settings, get_settings
from ..models.schemas import SourceCitation

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for semantic search"""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        self.index: Optional[faiss.Index] = None
        self.chunks: List = []  # Store chunk objects
        self.dimension: Optional[int] = None
        self._initialized = False
    
    def initialize(self, dimension: int) -> None:
        """
        Initialize FAISS index
        
        Args:
            dimension: Embedding dimension
        """
        logger.info(f"Initializing FAISS index with dimension {dimension}")
        self.dimension = dimension
        
        # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(dimension)
        self._initialized = True
        logger.info("FAISS index initialized")
    
    def add_documents(self, chunks: List, embeddings: np.ndarray) -> None:
        """
        Add documents to the vector store
        
        Args:
            chunks: List of Chunk objects
            embeddings: Numpy array of embeddings
        """
        if not self._initialized:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings")
        
        logger.info(f"Adding {len(chunks)} documents to vector store")
        
        # Ensure embeddings are float32 and normalized
        embeddings = embeddings.astype('float32')
        faiss.normalize_L2(embeddings)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store chunks
        self.chunks.extend(chunks)
        
        logger.info(f"Vector store now contains {len(self.chunks)} documents")
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        similarity_threshold: float = 0.0
    ) -> List[Tuple[int, float]]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of (index, score) tuples
        """
        if not self._initialized or self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Ensure query is float32 and normalized
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        # Filter by threshold and return results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score >= similarity_threshold:
                results.append((int(idx), float(score)))
        
        logger.info(f"Found {len(results)} results above threshold {similarity_threshold}")
        return results
    
    def search_with_mmr(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5
    ) -> List[Tuple[int, float]]:
        """
        Search using Maximal Marginal Relevance for diversity
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of final results
            fetch_k: Number of initial candidates
            lambda_mult: Diversity parameter (0=max diversity, 1=max relevance)
            
        Returns:
            List of (index, score) tuples
        """
        if not self._initialized or self.index.ntotal == 0:
            return []
        
        # Get initial candidates
        initial_results = self.search(query_embedding, top_k=fetch_k)
        if not initial_results:
            return []
        
        # Extract indices and scores
        candidate_indices = [idx for idx, _ in initial_results]
        candidate_scores = [score for _, score in initial_results]
        
        # Get embeddings for candidates
        candidate_embeddings = np.array([
            self._get_embedding_by_index(idx) for idx in candidate_indices
        ])
        
        # MMR algorithm
        selected_indices = []
        selected_scores = []
        
        while len(selected_indices) < min(top_k, len(candidate_indices)):
            remaining_indices = [
                i for i in range(len(candidate_indices))
                if i not in selected_indices
            ]
            
            if not remaining_indices:
                break
            
            # Calculate MMR scores
            mmr_scores = []
            for i in remaining_indices:
                # Relevance to query
                relevance = candidate_scores[i]
                
                # Max similarity to already selected
                if selected_indices:
                    selected_embeddings = candidate_embeddings[selected_indices]
                    similarities = np.dot(
                        selected_embeddings,
                        candidate_embeddings[i]
                    )
                    max_sim = np.max(similarities)
                else:
                    max_sim = 0
                
                # MMR score
                mmr_score = lambda_mult * relevance - (1 - lambda_mult) * max_sim
                mmr_scores.append((i, mmr_score))
            
            # Select best MMR score
            best_idx = max(mmr_scores, key=lambda x: x[1])[0]
            selected_indices.append(best_idx)
            selected_scores.append(candidate_scores[best_idx])
        
        # Return results
        results = [
            (candidate_indices[i], selected_scores[j])
            for j, i in enumerate(selected_indices)
        ]
        
        logger.info(f"MMR search returned {len(results)} diverse results")
        return results
    
    def _get_embedding_by_index(self, idx: int) -> np.ndarray:
        """Get embedding vector by index"""
        embedding = self.index.reconstruct(int(idx))
        return embedding
    
    def get_chunks_by_indices(self, indices: List[int]) -> List:
        """
        Get chunk objects by their indices
        
        Args:
            indices: List of chunk indices
            
        Returns:
            List of Chunk objects
        """
        return [self.chunks[idx] for idx in indices if idx < len(self.chunks)]
    
    def search_and_retrieve(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        use_mmr: bool = True
    ) -> List[SourceCitation]:
        """
        Search and return formatted source citations
        
        Args:
            query_embedding: Query embedding
            top_k: Number of results
            use_mmr: Use MMR for diversity
            
        Returns:
            List of SourceCitation objects
        """
        # Search
        if use_mmr:
            results = self.search_with_mmr(
                query_embedding,
                top_k=top_k,
                lambda_mult=1 - self.settings.mmr_diversity_score
            )
        else:
            results = self.search(
                query_embedding,
                top_k=top_k,
                similarity_threshold=self.settings.similarity_threshold
            )
        
        # Convert to SourceCitation objects
        citations = []
        for idx, score in results:
            chunk = self.chunks[idx]
            metadata = chunk.metadata
            
            citation = SourceCitation(
                page=metadata.get("page"),
                chapter=metadata.get("chapter"),
                verse=metadata.get("verse"),
                verse_reference=metadata.get("verse_reference"),
                excerpt=chunk.text[:500],  # Limit excerpt length
                similarity_score=score
            )
            citations.append(citation)
        
        return citations
    
    def save(self, path: Optional[Path] = None) -> None:
        """
        Save vector store to disk
        
        Args:
            path: Directory path to save to
        """
        if not self._initialized:
            logger.warning("Cannot save uninitialized vector store")
            return
        
        save_path = path or self.settings.full_vector_store_path
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_file = save_path / "index.faiss"
        faiss.write_index(self.index, str(index_file))
        
        # Save chunks and metadata
        metadata_file = save_path / "metadata.pkl"
        with open(metadata_file, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'dimension': self.dimension
            }, f)
        
        logger.info(f"Vector store saved to {save_path}")
    
    def load(self, path: Optional[Path] = None) -> bool:
        """
        Load vector store from disk
        
        Args:
            path: Directory path to load from
            
        Returns:
            True if loaded successfully
        """
        load_path = path or self.settings.full_vector_store_path
        index_file = load_path / "index.faiss"
        metadata_file = load_path / "metadata.pkl"
        
        if not index_file.exists() or not metadata_file.exists():
            logger.warning(f"Vector store files not found at {load_path}")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))
            
            # Load metadata
            with open(metadata_file, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.dimension = data['dimension']
            
            self._initialized = True
            logger.info(f"Vector store loaded from {load_path} with {len(self.chunks)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def clear(self) -> None:
        """Clear the vector store"""
        if self.dimension:
            self.initialize(self.dimension)
        self.chunks = []
        logger.info("Vector store cleared")
    
    def get_stats(self) -> dict:
        """Get vector store statistics"""
        return {
            "total_chunks": len(self.chunks),
            "dimension": self.dimension,
            "initialized": self._initialized,
            "index_size": self.index.ntotal if self.index else 0
        }
