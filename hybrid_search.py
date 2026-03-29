"""
Optimized hybrid search engine combining semantic and fuzzy search.
Provides fast, accurate results with fuzzy word matching capabilities.
"""

import logging
import re
import pickle
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
from functools import lru_cache
from fuzzywuzzy import fuzz, process
import time

logger = logging.getLogger(__name__)


class FuzzySearchEngine:
    """Fuzzy word matching engine for Bhagavad Gita verses"""
    
    def __init__(self):
        """Initialize fuzzy search engine"""
        self.verse_index = {}  # text -> content mapping
        self.character_names = {}  # character -> variations mapping
        self.verse_variations = {}  # verse -> different ways to refer
        self.build_fuzzy_index()
    
    def build_fuzzy_index(self):
        """Build fuzzy search indexes"""
        # Common character name variations
        self.character_names = {
            'krishna': ['krishna', 'sri krishna', 'lord krishna', 'vasudeva', 'govinda'],
            'arjuna': ['arjuna', 'partha', 'dhananjaya', 'gudakesha'],
            'duryodhana': ['duryodhana', 'suyodhana', 'kaurava'],
            'bhishma': ['bhishma', 'bhishma pitamaha', 'devavrata'],
            'draupadi': ['draupadi', 'panchali', 'yajnaseni'],
            'yudhishthira': ['yudhishthira', 'dharma', 'dharmaraja'],
        }
        
        # Verse reference patterns
        self.verse_patterns = [
            r'(\d+)\.(\d+)',  # Chapter.Verse
            r'chapter\s+(\d+)\s+verse\s+(\d+)',
            r'bg\s*(\d+)\.(\d+)',
            r'c\s*(\d+)\s*v\s*(\d+)'
        ]
    
    @lru_cache(maxsize=1000)
    def extract_terms(self, query: str) -> List[str]:
        """Extract meaningful terms from query with caching"""
        # Normalize query
        query = query.lower().strip()
        
        # Remove stop words
        stop_words = {
            'what', 'does', 'did', 'do', 'say', 'said', 'tells', 'according', 'about', 
            'the', 'in', 'is', 'are', 'was', 'were', 'to', 'for', 'with', 'by', 'from',
            'krishna', 'arjuna'  # Remove common names for better matching
        }
        
        # Extract words and filter
        words = re.findall(r'\b\w+\b', query)
        terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Add character name variations
        for character, variations in self.character_names.items():
            if any(var in query for var in variations):
                terms.append(character)
        
        return list(set(terms))  # Remove duplicates
    
    def fuzzy_search(self, query: str, threshold: int = 70) -> List[Dict[str, Any]]:
        """Find verses using fuzzy word matching"""
        start_time = time.time()
        results = []
        
        # Extract key terms
        terms = self.extract_terms(query)
        logger.info(f"Extracted terms: {terms}")
        
        # Search for each term
        for term in terms:
            # Get fuzzy matches against verse content
            matches = process.extract(
                term,
                self.verse_index.keys(),
                scorer=fuzz.partial_ratio,
                limit=10
            )
            
            for match_text, score in matches:
                if score >= threshold:
                    verse_content = self.verse_index[match_text]
                    
                    # Calculate relevance score
                    relevance = self.calculate_relevance(term, match_text, score)
                    
                    results.append({
                        'verse': match_text,
                        'content': verse_content,
                        'fuzzy_score': score,
                        'relevance': relevance,
                        'matched_term': term,
                        'type': 'fuzzy'
                    })
        
        # Sort by relevance and remove duplicates
        results = sorted(results, key=lambda x: x['relevance'], reverse=True)
        seen = set()
        unique_results = []
        
        for result in results:
            verse_key = result['verse']
            if verse_key not in seen:
                seen.add(verse_key)
                unique_results.append(result)
        
        search_time = time.time() - start_time
        logger.info(f"Fuzzy search completed in {search_time:.3f}s, found {len(unique_results)} results")
        
        return unique_results[:10]  # Return top 10
    
    def calculate_relevance(self, term: str, match_text: str, fuzzy_score: int) -> float:
        """Calculate relevance score for fuzzy match"""
        # Base score from fuzzy matching
        relevance = fuzzy_score / 100.0
        
        # Boost for exact word matches
        if term.lower() in match_text.lower():
            relevance *= 1.2
        
        # Boost for verse references
        if any(re.search(pattern, match_text) for pattern in self.verse_patterns):
            relevance *= 1.1
        
        # Boost for important terms
        important_terms = ['duty', 'dharma', 'karma', 'yap', 'action', 'y swings', 'moksha']
        if term.lower() in important_terms:
            relevance *= 1.15
        
        return min(relevance, 1.0)  # Cap at 1.0
    
    def add_verse_content(self, verse_text: str, content: Dict[str, Any]):
        """Add verse content to fuzzy index"""
        # Create searchable text from content
        searchable_parts = []
        
        # Add verse text
        if verse_text:
            searchable_parts.append(verse_text.lower())
        
        # Add chapter/verse info
        if 'chapter' in content and 'verse' in content:
            searchable_parts.append(f"chapter {content['chapter']} verse {content['verse']}")
            searchable_parts.append(f"{content['chapter']}.{content['verse']}")
        
        # Add content text
        if 'text' in content:
            searchable_parts.append(content['text'].lower())
        
        # Combine all parts
        full_text = ' '.join(searchable_parts)
        self.verse_index[verse_text or content.get('text', '')] = content


class OptimizedVectorStore:
    """Optimized vector store with caching and performance improvements"""
    
    def __init__(self):
        """Initialize optimized vector store"""
        self.embeddings = None
        self.documents = []
        self.dimension = None
        self._cache = {}
        self._max_cache_size = 1000
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Add documents and embeddings with optimization"""
        if len(documents) != len(embeddings):
            raise ValueError(f"Mismatch: {len(documents)} documents but {len(embeddings)} embeddings")
        
        self.documents = documents
        self.embeddings = np.array(embeddings, dtype=np.float32)
        self.dimension = self.embeddings.shape[1]
        
        # Pre-normalize for faster cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        self.embeddings = self.embeddings / (norms + 1e-10)
        
        logger.info(f"Added {len(documents)} documents to optimized vector store")
    
    @lru_cache(maxsize=500)
    def _get_cached_query_embedding(self, query_tuple: tuple) -> np.ndarray:
        """Cache query embeddings to avoid recomputation"""
        query_embedding = np.array(query_tuple, dtype=np.float32).reshape(1, -1)
        query_norm = np.linalg.norm(query_embedding)
        return query_embedding / (query_norm + 1e-10)
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[int, float, Dict[str, Any]]]:
        """Fast semantic search with optimizations"""
        if self.embeddings is None or len(self.embeddings) == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Convert to tuple for caching
        query_tuple = tuple(query_embedding)
        
        # Get or create cached query embedding
        query_vec = self._get_cached_query_embedding(query_tuple)
        
        # Fast cosine similarity using matrix multiplication
        similarities = np.dot(self.embeddings, query_vec.T).flatten()
        
        # Get top k indices efficiently
        if len(similarities) <= top_k:
            top_indices = np.argsort(similarities)[::-1]
        else:
            # Use partition for better performance on large arrays
            top_indices = np.argpartition(-similarities, top_k)[:top_k]
            top_indices = top_indices[np.argsort(-similarities[top_indices])]
        
        # Return results
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.2:  # Lower threshold for more results
                results.append((int(idx), score, self.documents[idx]))
        
        return results
    
    def save(self, path: str):
        """Save vector store to disk with compression"""
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'embeddings': self.embeddings,
            'documents': self.documents,
            'dimension': self.dimension
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        logger.info(f"Optimized vector store saved to {save_path}")
    
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
            
            logger.info(f"Optimized vector store loaded from {load_path} with {len(self.documents)} documents")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False


class HybridSearchEngine:
    """Hybrid search engine combining semantic and fuzzy search"""
    
    def __init__(self):
        """Initialize hybrid search engine"""
        self.vector_store = OptimizedVectorStore()
        self.fuzzy_engine = FuzzySearchEngine()
        self.semantic_weight = 0.7
        self.fuzzy_weight = 0.3
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Add documents to both search engines"""
        # Add to vector store
        self.vector_store.add_documents(documents, embeddings)
        
        # Add to fuzzy engine
        for doc in documents:
            verse_text = doc.get('text', '')
            self.fuzzy_engine.add_verse_content(verse_text, doc)
    
    def search(self, query: str, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Hybrid search combining semantic and fuzzy results"""
        start_time = time.time()
        
        # Get semantic results
        semantic_results = self.vector_store.search(query_embedding, top_k * 2)
        
        # Get fuzzy results
        fuzzy_results = self.fuzzy_engine.fuzzy_search(query, threshold=65)
        
        # Convert semantic results to standard format
        semantic_formatted = []
        for idx, score, doc in semantic_results:
            semantic_formatted.append({
                'verse': doc.get('text', ''),
                'content': doc,
                'semantic_score': score,
                'relevance': score * self.semantic_weight,
                'type': 'semantic'
            })
        
        # Merge results
        merged_results = self.merge_results(semantic_formatted, fuzzy_results)
        
        # Sort by combined relevance and return top results
        merged_results.sort(key=lambda x: x['relevance'], reverse=True)
        
        search_time = time.time() - start_time
        logger.info(f"Hybrid search completed in {search_time:.3f}s, found {len(merged_results)} results")
        
        return merged_results[:top_k]
    
    def merge_results(self, semantic: List[Dict], fuzzy: List[Dict]) -> List[Dict]:
        """Merge semantic and fuzzy results with weighted scoring"""
        merged = {}
        
        # Add semantic results
        for result in semantic:
            verse_key = result['verse']
            merged[verse_key] = result.copy()
            merged[verse_key]['fuzzy_score'] = 0.0
        
        # Add fuzzy results and merge with existing
        for result in fuzzy:
            verse_key = result['verse']
            if verse_key in merged:
                # Combine scores
                existing = merged[verse_key]
                existing['fuzzy_score'] = result['fuzzy_score']
                existing['relevance'] = (
                    existing['semantic_score'] * self.semantic_weight +
                    result['fuzzy_score'] / 100.0 * self.fuzzy_weight
                )
                existing['type'] = 'hybrid'
            else:
                # Add new fuzzy result
                result['semantic_score'] = 0.0
                result['relevance'] = (result['fuzzy_score'] / 100.0) * self.fuzzy_weight
                merged[verse_key] = result
        
        return list(merged.values())
    
    def save(self, vector_path: str, fuzzy_path: str):
        """Save both search engines"""
        self.vector_store.save(vector_path)
        
        # Save fuzzy engine data
        fuzzy_data = {
            'verse_index': self.fuzzy_engine.verse_index,
            'character_names': self.fuzzy_engine.character_names
        }
        
        with open(fuzzy_path, 'wb') as f:
            pickle.dump(fuzzy_data, f)
    
    def load(self, vector_path: str, fuzzy_path: str) -> bool:
        """Load both search engines"""
        vector_loaded = self.vector_store.load(vector_path)
        
        # Load fuzzy engine data
        try:
            with open(fuzzy_path, 'rb') as f:
                fuzzy_data = pickle.load(f)
            
            self.fuzzy_engine.verse_index = fuzzy_data['verse_index']
            self.fuzzy_engine.character_names = fuzzy_data['character_names']
            
            fuzzy_loaded = True
        except Exception as e:
            logger.error(f"Error loading fuzzy engine: {e}")
            fuzzy_loaded = False
        
        return vector_loaded and fuzzy_loaded


# Global instance with lazy initialization
_hybrid_engine = None

def get_hybrid_search_engine():
    """Get or create global hybrid search engine instance"""
    global _hybrid_engine
    if _hybrid_engine is None:
        _hybrid_engine = HybridSearchEngine()
        logger.info("Created new hybrid search engine instance")
    return _hybrid_engine
