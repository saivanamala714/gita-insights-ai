"""
Google ADK Agent for Bhagavad Gita Q&A System
Enhanced agent with tool usage, validation, and context management
"""

import os
import json
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

# Import existing functions
from name_corrector import correct_text_names
from simple_vector_search import get_vector_store
from gita_qa_pairs import get_qa_pairs, search_qa
from gemini_embeddings import get_gemini_embeddings

# ADK imports (will be installed separately)
try:
    from google.adk.agents import Agent
    from google.adk.tools.function_tool import FunctionTool
    from google.adk.tools import google_search
    from google.adk import Runner
    from google.adk.sessions import InMemorySessionService
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    logging.warning("Google ADK not installed. Install with: pip install google-adk")

load_dotenv()
logger = logging.getLogger(__name__)

# ==================== TOOL 1: Search Bhagavad Gita (PDF + FAISS) ====================
def search_gita(query: str, top_k: int = 5) -> str:
    """Search the Bhagavad Gita PDF using existing FAISS/hybrid search."""
    try:
        # Use existing vector search
        vector_store = get_vector_store()
        if vector_store.embeddings is not None:
            # Generate query embedding
            embeddings_service = get_gemini_embeddings()
            query_embedding = embeddings_service.embed_query(query)
            
            # Search for similar documents
            results = vector_store.search(query_embedding, top_k=top_k)
            
            if results:
                # Format results nicely
                formatted_results = []
                for idx, score, doc_data in results:
                    formatted_results.append({
                        "content": doc_data['text'][:200] + "...",
                        "page": doc_data.get('metadata', {}).get('page', 'Unknown'),
                        "score": float(score)
                    })
                
                return json.dumps({
                    "results": formatted_results,
                    "query": query,
                    "total_found": len(formatted_results)
                }, indent=2)
        
        return json.dumps({"results": [], "query": query, "total_found": 0}, indent=2)
        
    except Exception as e:
        logger.error(f"Error in search_gita: {e}")
        return json.dumps({"error": str(e), "results": []}, indent=2)

# ==================== TOOL 2: Fuzzy Word Fix ====================
def fuzzy_word_fix(text: str) -> str:
    """Correct misspelled names or words using existing name_corrector."""
    try:
        corrected, corrections = correct_text_names(text)
        return json.dumps({
            "original": text,
            "corrected": corrected,
            "corrections": corrections
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in fuzzy_word_fix: {e}")
        return json.dumps({"error": str(e), "original": text}, indent=2)

# ==================== TOOL 3: NLP / Emotion Analysis ====================
def analyze_emotion_nlp(text: str) -> str:
    """Perform basic emotion or devotional mood analysis."""
    try:
        # Simple keyword-based emotion analysis
        devotional_words = ['krishna', 'god', 'lord', 'spiritual', 'devotion', 'faith', 'bhakti']
        question_words = ['what', 'why', 'how', 'when', 'where', 'who']
        
        text_lower = text.lower()
        emotions = []
        
        # Check for devotional tone
        devotional_count = sum(1 for word in devotional_words if word in text_lower)
        if devotional_count > 0:
            emotions.append({"type": "devotional", "confidence": min(devotional_count * 0.2, 1.0)})
        
        # Check for questioning tone
        question_count = sum(1 for word in question_words if word in text_lower)
        if question_count > 0:
            emotions.append({"type": "inquiring", "confidence": min(question_count * 0.3, 1.0)})
        
        # Check for emotional words
        emotional_words = ['confused', 'worried', 'peace', 'happiness', 'suffering', 'joy']
        emotional_found = [word for word in emotional_words if word in text_lower]
        if emotional_found:
            emotions.append({"type": "emotional", "confidence": 0.7, "words": emotional_found})
        
        return json.dumps({
            "text": text,
            "emotions": emotions,
            "analysis_type": "keyword_based"
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error in analyze_emotion_nlp: {e}")
        return json.dumps({"error": str(e), "emotions": []}, indent=2)

# ==================== TOOL 4: Google Search (built-in) ====================
# Use the imported google_search tool directly if ADK is available

# ==================== TOOL 5: Validate Answer ====================
def validate_gita_answer(question: str, draft_answer: str) -> str:
    """Validate the draft answer for accuracy, fidelity to Gita As It Is, tone, and hallucinations."""
    try:
        validation_issues = []
        
        # Check for proper spiritual tone
        if not any(word in draft_answer.lower() for word in ['hare krishna', 'krishna', 'lord', 'bhagavad gita']):
            validation_issues.append("Missing spiritual tone or references")
        
        # Check for verse citations
        if not any(word in draft_answer.lower() for word in ['chapter', 'verse', 'chapter.', 'verse.']):
            validation_issues.append("No verse citations found")
        
        # Check for "I don't know" type responses
        if any(phrase in draft_answer.lower() for phrase in ['i do not know', 'i cannot find', 'not in context']):
            validation_issues.append("Answer indicates inability to find information")
        
        # Check length (too short might be incomplete)
        if len(draft_answer) < 100:
            validation_issues.append("Answer seems too short")
        
        # Check for potential hallucinations (modern concepts not in Gita)
        modern_terms = ['internet', 'computer', 'phone', 'email', 'social media']
        found_modern = [term for term in modern_terms if term in draft_answer.lower()]
        if found_modern:
            validation_issues.append(f"Contains modern terms not in Gita: {found_modern}")
        
        is_valid = len(validation_issues) == 0
        
        return json.dumps({
            "valid": is_valid,
            "issues": validation_issues,
            "suggestion": "Please ensure answer references Bhagavad Gita verses and maintains spiritual tone" if not is_valid else "Answer looks good",
            "question": question,
            "answer_length": len(draft_answer)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error in validate_gita_answer: {e}")
        return json.dumps({"valid": False, "issues": [str(e)], "suggestion": "Validation failed"}, indent=2)

# ==================== MAIN GITA AGENT ====================
def create_gita_agent():
    """Create and return the Gita ADK agent if available."""
    # For now, we'll always return True to enable the enhanced tools
    # even if the full ADK framework isn't available
    return True

# Create global agent instance
gita_agent = create_gita_agent()

async def ask_gita_agent(question: str) -> Dict[str, Any]:
    """
    Ask the Gita ADK agent a question
    
    Args:
        question: User's question
        
    Returns:
        Dictionary with answer, sources, and metadata
    """
    try:
        # Use the enhanced tools pipeline even without full ADK framework
        
        # Step 1: Apply fuzzy name correction
        corrected_result = fuzzy_word_fix(question)
        corrected_data = json.loads(corrected_result)
        corrected_question = corrected_data.get('corrected', question)
        
        # Step 2: Search the Gita
        search_result = search_gita(corrected_question)
        search_data = json.loads(search_result)
        
        # Step 3: Generate a basic answer using the search results
        if search_data.get('results'):
            context = search_data['results'][0]['content']  # Use first result
            answer = f"Hare Krishna! Based on the Bhagavad Gita, here's what I found about {corrected_question}:\n\n{context}\n\nThis answer was generated using the enhanced agent with fuzzy name correction and search tools."
        else:
            answer = f"Hare Krishna! I searched for information about {corrected_question} but couldn't find specific verses. The enhanced agent used fuzzy name correction and search tools to process your question."
        
        # Step 4: Validate the answer
        validation_result = validate_gita_answer(question, answer)
        validation_data = json.loads(validation_result)
        
        return {
            "answer": answer,
            "sources": search_data.get('results', []),
            "agent_name": "gita_insights_agent",
            "model": "enhanced_tools_v1",
            "tool_calls": [
                {"tool": "fuzzy_word_fix", "result": corrected_data},
                {"tool": "search_gita", "result": search_data},
                {"tool": "validate_gita_answer", "result": validation_data}
            ],
            "validation": validation_data
        }
        
    except Exception as e:
        logger.error(f"Error running Gita agent: {e}")
        return {
            "error": str(e),
            "answer": "Hare Krishna! I encountered an error while processing your question. Please try again.",
            "sources": []
        }
