"""
Optimized Bhagavad Gita QA System with Hybrid Search
Combines semantic and fuzzy search for fast, accurate responses.
"""

import os
import re
import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI imports
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import optimized search engine
try:
    from hybrid_search import get_hybrid_search_engine
    from gemini_embeddings import get_gemini_embeddings
    import google.generativeai as genai
    HYBRID_SEARCH_ENABLED = True
    logging.info("✅ Hybrid search engine loaded successfully")
except Exception as e:
    HYBRID_SEARCH_ENABLED = False
    logging.warning(f"⚠️ Hybrid search engine not available: {e}")

# Import existing modules
from name_corrector import correct_text_names, correct_character_name
from response_processor import get_processor
from gita_qa_pairs import get_qa_pairs, get_qa_by_category

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Optimized Bhagavad Gita QA System",
    description="Fast, accurate answers with fuzzy word matching",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
qa_system = None
hybrid_engine = None
gemini_embeddings = None


class QueryRequest(BaseModel):
    question: str
    max_results: int = 5
    use_fuzzy: bool = True


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    search_type: str
    response_time: float
    confidence: float


class OptimizedQASystem:
    """Optimized QA system with hybrid search capabilities"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.verse_index = {}
        self.documents = []
        self.hybrid_engine = get_hybrid_search_engine() if HYBRID_SEARCH_ENABLED else None
        self.gemini_embeddings = get_gemini_embeddings() if HYBRID_SEARCH_ENABLED else None
        self._cache = {}
        self._max_cache_size = 1000
        
    def initialize(self) -> bool:
        """Initialize the QA system with optimized loading"""
        try:
            start_time = time.time()
            logger.info("🚀 Initializing optimized QA system...")
            
            # Load verse data
            self.load_verse_data()
            
            # Initialize embeddings and vector store
            if self.hybrid_engine and self.gemini_embeddings:
                self.initialize_vector_store()
            
            # Load pre-built indexes if available
            self.load_prebuilt_indexes()
            
            init_time = time.time() - start_time
            logger.info(f"✅ QA system initialized in {init_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize QA system: {e}")
            return False
    
    def load_verse_data(self):
        """Load verse data from JSON or build from PDF"""
        # Try to load pre-processed data first
        json_file = "bhagavad_gita_summaries.json"
        if os.path.exists(json_file):
            logger.info("Loading pre-processed verse data...")
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.verse_index = data
                logger.info(f"Loaded {len(self.verse_index)} verses from JSON")
        else:
            logger.info("Building verse index from PDF...")
            self.build_verse_index()
    
    def build_verse_index(self):
        """Build verse index from PDF (optimized version)"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(self.pdf_path)
            
            verse_pattern = re.compile(r'(?:Bg\s*)?(\d+)\.(\d+)(?:\s|$)')
            current_chapter = None
            current_verse = None
            verse_text = []
            
            start_page = 10  # Skip front matter
            
            for page_num in range(start_page, len(reader.pages)):
                try:
                    text = reader.pages[page_num].extract_text()
                    if not text:
                        continue
                    
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    
                    for i, line in enumerate(lines):
                        # Special handling for Bg references
                        if 'TEXT ' in line and 'Bg' in line:
                            parts = line.split()
                            for part in parts:
                                if 'Bg' in part and '.' in part:
                                    try:
                                        ref = part.split('Bg')[-1]
                                        chapter, verse = ref.split('.')
                                        current_chapter = int(chapter)
                                        current_verse = int(verse)
                                        if i + 1 < len(lines):
                                            verse_text = [lines[i+1].strip()]
                                        break
                                    except (ValueError, IndexError):
                                        continue
                        
                        # Standard verse pattern
                        match = verse_pattern.search(line)
                        if match and current_chapter and current_verse and verse_text:
                            # Save previous verse
                            verse_ref = f"{current_chapter}.{current_verse}"
                            self.verse_index[verse_ref] = {
                                "text": " ".join(verse_text).strip(),
                                "chapter": current_chapter,
                                "verse": current_verse,
                                "page": page_num + 1
                            }
                            
                            # Start new verse
                            current_chapter = int(match.group(1))
                            current_verse = int(match.group(2))
                            if i + 1 < len(lines):
                                verse_text = [lines[i+1].strip()]
                        elif current_chapter and current_verse:
                            if line and not line.startswith('TEXT'):
                                verse_text.append(line)
                
                except Exception as e:
                    logger.warning(f"Error processing page {page_num + 1}: {e}")
            
            # Save last verse
            if current_chapter and current_verse and verse_text:
                verse_ref = f"{current_chapter}.{current_verse}"
                self.verse_index[verse_ref] = {
                    "text": " ".join(verse_text).strip(),
                    "chapter": current_chapter,
                    "verse": current_verse,
                    "page": page_num + 1
                }
            
            logger.info(f"Built index with {len(self.verse_index)} verses")
            
        except Exception as e:
            logger.error(f"Error building verse index: {e}")
    
    def initialize_vector_store(self):
        """Initialize vector store with embeddings"""
        try:
            logger.info("Initializing vector store with embeddings...")
            
            # Prepare documents
            documents = []
            verses = []
            
            for verse_ref, verse_data in self.verse_index.items():
                doc = {
                    'text': verse_data['text'],
                    'verse_ref': verse_ref,
                    'chapter': verse_data['chapter'],
                    'verse': verse_data['verse'],
                    'page': verse_data['page']
                }
                documents.append(doc)
                verses.append(verse_data['text'])
            
            # Generate embeddings in batches
            embeddings = []
            batch_size = 10
            
            for i in range(0, len(verses), batch_size):
                batch = verses[i:i + batch_size]
                batch_embeddings = self.gemini_embeddings.embed_batch(batch)
                embeddings.extend(batch_embeddings)
                
                if (i // batch_size + 1) % 10 == 0:
                    logger.info(f"Processed {min(i + batch_size, len(verses))}/{len(verses)} verses")
            
            # Add to hybrid engine
            self.hybrid_engine.add_documents(documents, embeddings)
            logger.info(f"Added {len(documents)} documents to hybrid search engine")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
    
    def load_prebuilt_indexes(self):
        """Load pre-built indexes if available"""
        try:
            vector_path = "data/vector_store.pkl"
            fuzzy_path = "data/fuzzy_index.pkl"
            
            if self.hybrid_engine:
                loaded = self.hybrid_engine.load(vector_path, fuzzy_path)
                if loaded:
                    logger.info("Loaded pre-built indexes successfully")
                    return
            
            logger.info("No pre-built indexes found, will build on first query")
            
        except Exception as e:
            logger.warning(f"Error loading pre-built indexes: {e}")
    
    @lru_cache(maxsize=500)
    def cached_query(self, question: str) -> str:
        """Cache query results to improve performance"""
        return question  # Simple cache key
    
    def search_verses(self, question: str, max_results: int = 5, use_fuzzy: bool = True) -> Tuple[List[Dict], str, float]:
        """Search verses using hybrid search"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"{question}_{max_results}_{use_fuzzy}"
            if cache_key in self._cache:
                logger.info("Returning cached result")
                return self._cache[cache_key]
            
            # Generate query embedding
            query_embedding = self.gemini_embeddings.embed_text(question) if self.gemini_embeddings else None
            
            # Perform hybrid search
            if self.hybrid_engine and query_embedding:
                results = self.hybrid_engine.search(question, query_embedding, max_results)
                search_type = "hybrid"
            else:
                # Fallback to simple text search
                results = self.simple_text_search(question, max_results)
                search_type = "text"
            
            # Calculate confidence
            confidence = self.calculate_confidence(results)
            
            # Cache results
            search_data = (results, search_type, confidence)
            if len(self._cache) < self._max_cache_size:
                self._cache[cache_key] = search_data
            
            search_time = time.time() - start_time
            logger.info(f"Search completed in {search_time:.3f}s using {search_type}")
            
            return results, search_type, confidence
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return [], "error", 0.0
    
    def simple_text_search(self, question: str, max_results: int) -> List[Dict]:
        """Simple text search as fallback"""
        results = []
        question_lower = question.lower()
        
        for verse_ref, verse_data in self.verse_index.items():
            text = verse_data['text'].lower()
            
            # Simple keyword matching
            words = question_lower.split()
            matches = sum(1 for word in words if word in text)
            
            if matches > 0:
                score = matches / len(words)
                results.append({
                    'verse_ref': verse_ref,
                    'content': verse_data,
                    'relevance': score,
                    'type': 'text'
                })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:max_results]
    
    def calculate_confidence(self, results: List[Dict]) -> float:
        """Calculate confidence score for search results"""
        if not results:
            return 0.0
        
        # Weight by relevance and result type
        total_score = 0
        type_weights = {'hybrid': 1.0, 'semantic': 0.8, 'fuzzy': 0.6, 'text': 0.4}
        
        for result in results:
            relevance = result.get('relevance', 0)
            result_type = result.get('type', 'text')
            weight = type_weights.get(result_type, 0.5)
            total_score += relevance * weight
        
        return min(total_score / len(results), 1.0)
    
    def generate_answer(self, question: str, search_results: List[Dict]) -> str:
        """Generate answer using search results"""
        try:
            if not search_results:
                return "I couldn't find relevant information in the Bhagavad Gita for your question."
            
            # Prepare context from search results
            context_parts = []
            for result in search_results[:3]:  # Use top 3 results
                content = result['content']
                if isinstance(content, dict):
                    verse_text = content.get('text', '')
                    verse_ref = f"Chapter {content.get('chapter', '?')}, Verse {content.get('verse', '?')}"
                    context_parts.append(f"{verse_ref}: {verse_text}")
                else:
                    context_parts.append(str(content))
            
            context = "\n\n".join(context_parts)
            
            # Generate answer using Gemini
            if HYBRID_SEARCH_ENABLED:
                prompt = f"""
                Based on the following Bhagavad Gita verses, answer the question: "{question}"
                
                Context:
                {context}
                
                Provide a clear, accurate answer referencing the specific verses when relevant.
                """
                
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                return response.text
            else:
                # Fallback to simple response
                return f"Based on the Bhagavad Gita: {context_parts[0] if context_parts else 'No specific verse found.'}"
                
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return "I encountered an error while generating the answer. Please try again."


# Initialize QA system
def initialize_qa_system():
    """Initialize the QA system"""
    global qa_system
    try:
        pdf_path = "11-Bhagavad-gita_As_It_Is.pdf"
        qa_system = OptimizedQASystem(pdf_path)
        success = qa_system.initialize()
        if success:
            logger.info("✅ QA system ready")
        else:
            logger.error("❌ QA system initialization failed")
    except Exception as e:
        logger.error(f"❌ Error initializing QA system: {e}")


# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    initialize_qa_system()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Optimized Bhagavad Gita QA System",
        "version": "2.0.0",
        "features": ["hybrid_search", "fuzzy_matching", "cached_results"],
        "status": "ready" if qa_system else "initializing"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "qa_system": qa_system is not None,
        "hybrid_search": HYBRID_SEARCH_ENABLED,
        "cache_size": len(qa_system._cache) if qa_system else 0,
        "total_verses": len(qa_system.verse_index) if qa_system else 0
    }


@app.post("/query", response_model=QueryResponse)
async def query_question(request: QueryRequest):
    """Main query endpoint with optimized search"""
    if not qa_system:
        raise HTTPException(status_code=503, detail="QA system not initialized")
    
    try:
        start_time = time.time()
        
        # Search for relevant verses
        search_results, search_type, confidence = qa_system.search_verses(
            request.question, 
            request.max_results, 
            request.use_fuzzy
        )
        
        # Generate answer
        answer = qa_system.generate_answer(request.question, search_results)
        
        # Prepare sources
        sources = []
        for result in search_results:
            content = result['content']
            if isinstance(content, dict):
                sources.append({
                    "verse_ref": f"{content.get('chapter', '?')}.{content.get('verse', '?')}",
                    "text": content.get('text', ''),
                    "relevance": result.get('relevance', 0),
                    "type": result.get('type', 'unknown')
                })
        
        response_time = time.time() - start_time
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            search_type=search_type,
            response_time=response_time,
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    if not qa_system:
        raise HTTPException(status_code=503, detail="QA system not initialized")
    
    return {
        "total_verses": len(qa_system.verse_index),
        "cache_size": len(qa_system._cache),
        "hybrid_search_enabled": HYBRID_SEARCH_ENABLED,
        "search_engine_type": "hybrid" if HYBRID_SEARCH_ENABLED else "text",
        "system_uptime": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
