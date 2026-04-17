"""
Real Google ADK Agent for Bhagavad Gita Insights AI
Proper LlmAgent with dynamic tool calling, tracing support, and validation
"""

import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Import existing project modules
from name_corrector import correct_text_names
from simple_vector_search import get_vector_store
from gita_qa_pairs import get_qa_pairs, search_qa
from gemini_embeddings import get_gemini_embeddings

# Google ADK imports
try:
    from google.adk.agents import LlmAgent
    from google.adk.tools import google_search
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    logging.warning("Google ADK not installed. Run: pip install google-adk")

load_dotenv()
logger = logging.getLogger(__name__)

# ====================== TOOL 1: Search Bhagavad Gita ======================
def search_gita(query: str, top_k: int = 5) -> str:
    """Search the Bhagavad Gita using vector store and return relevant verses."""
    try:
        vector_store = get_vector_store()
        embeddings_service = get_gemini_embeddings()
        query_embedding = embeddings_service.embed_query(query)

        results = vector_store.search(query_embedding, top_k=top_k)

        if not results:
            return "No relevant verses found in the Bhagavad Gita for this query."

        formatted = []
        for idx, score, doc_data in results:
            text = doc_data.get('text', '')
            metadata = doc_data.get('metadata', {})
            chapter = metadata.get('chapter', 'Unknown')
            verse = metadata.get('verse', 'Unknown')
            
            formatted.append(
                f"**Chapter {chapter}, Verse {verse}** (Relevance: {score:.3f})\n"
                f"{text}\n"
            )

        return "\n---\n".join(formatted)

    except Exception as e:
        logger.error(f"Error in search_gita: {e}")
        return f"Error searching Gita: {str(e)}"


# ====================== TOOL 2: Fuzzy Word Fix ======================
def fuzzy_word_fix(text: str) -> str:
    """Correct misspelled names and words (e.g., 'krishn' → 'Krishna')."""
    try:
        corrected, corrections = correct_text_names(text)
        if corrections:
            return f"Corrected '{text}' to '{corrected}'. Corrections made: {corrections}"
        return f"No corrections needed. Text is already clear: '{text}'"
    except Exception as e:
        logger.error(f"Error in fuzzy_word_fix: {e}")
        return f"Error correcting text: {str(e)}"


# ====================== TOOL 3: NLP / Emotion Analysis ======================
def analyze_emotion_nlp(text: str) -> str:
    """Analyze devotional mood and emotional tone in text or verses."""
    try:
        text_lower = text.lower()
        devotional_keywords = ['krishna', 'govinda', 'hare', 'bhakti', 'devotion', 'surrender', 'lord']
        emotional_keywords = ['suffering', 'fear', 'confusion', 'peace', 'joy', 'anxiety', 'duty']

        emotions = []

        if any(word in text_lower for word in devotional_keywords):
            emotions.append("Devotional / Bhakti")
        if any(word in text_lower for word in ['duty', 'karma', 'action']):
            emotions.append("Philosophical / Duty-based")
        if any(word in text_lower for word in emotional_keywords):
            emotions.append("Emotional")

        if not emotions:
            emotions.append("Neutral / Inquiring")

        return f"Emotional Analysis: {', '.join(emotions)}. The text shows a primarily {emotions[0].lower()} tone."
    
    except Exception as e:
        logger.error(f"Error in analyze_emotion_nlp: {e}")
        return "Could not perform emotion analysis."


# ====================== TOOL 4: Google Search (Built-in) ======================
# google_search is provided by ADK — no need to define it


# ====================== TOOL 5: Validate Answer ======================
def validate_gita_answer(question: str, draft_answer: str) -> str:
    """Validate the answer for accuracy, spiritual tone, and fidelity to Gita As It Is."""
    try:
        issues = []
        draft_lower = draft_answer.lower()

        # Check for spiritual tone
        if not any(word in draft_lower for word in ['hare krishna', 'krishna', 'lord', 'prabhupada', 'bhagavad gita']):
            issues.append("Answer lacks devotional or spiritual tone.")

        # Check for verse reference
        if not any(word in draft_lower for word in ['chapter', 'verse', 'text ', 'bg ']):
            issues.append("No specific verse or chapter reference found.")

        # Check for potential hallucinations
        modern_terms = ['internet', 'technology', 'science', 'psychology', 'modern', 'today\'s world']
        found = [term for term in modern_terms if term in draft_lower]
        if found:
            issues.append(f"Contains modern concepts not directly from Gita: {found}")

        # Check answer quality
        if len(draft_answer) < 80:
            issues.append("Answer is too brief.")

        is_valid = len(issues) == 0

        result = {
            "valid": is_valid,
            "issues": issues,
            "suggestion": "Improve by adding verse references and devotional tone." if issues else "Answer is good and aligned with Gita teachings."
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error in validate_gita_answer: {e}")
        return json.dumps({"valid": False, "issues": [str(e)], "suggestion": "Validation error occurred."}, indent=2)


# ====================== MAIN GITA AGENT ======================
def create_gita_agent():
    """Create and return the real Google ADK LlmAgent."""
    if not ADK_AVAILABLE:
        logger.error("Google ADK is not installed. Cannot create agent.")
        return None

    agent = LlmAgent(
        model="gemini-2.0-flash-latest",          # Change to "gemini-2.5-pro" for higher quality
        name="gita_insights_agent",
        description="Devotional and accurate spiritual guide based on Bhagavad Gita As It Is",
        instruction="""You are a humble, respectful, and knowledgeable spiritual guide based strictly on 
        'Bhagavad Gita As It Is' by His Divine Grace A.C. Bhaktivedanta Swami Prabhupada.

        Guidelines:
        - Always try to support your answer with relevant verses from the Gita.
        - Maintain a devotional, humble, and clear tone.
        - Use the available tools when needed (especially search_gita and validate_gita_answer).
        - If the user misspells names, use fuzzy_word_fix first.
        - Before giving the final answer, consider using the validation tool for important questions.
        - Never add modern interpretations not present in the book.""",
        tools=[
            search_gita,
            fuzzy_word_fix,
            analyze_emotion_nlp,
            google_search,
            validate_gita_answer,
        ],
    )
    return agent


# Global agent instance
gita_agent = create_gita_agent()


# ====================== MAIN ASYNC FUNCTION ======================
async def ask_gita_adk_agent(question: str) -> Dict[str, Any]:
    """
    Main function to ask the REAL Gita ADK Agent a question.
    """
    try:
        if gita_agent is None:
            return {
                "error": "ADK Agent not available",
                "answer": "Hare Krishna! The ADK agent is not properly initialized. Please check installation."
            }

        # Run the agent with proper ADK execution
        result = await gita_agent.run_async({"question": question})

        final_answer = result.final_response.text if hasattr(result, 'final_response') else str(result)

        return {
            "answer": final_answer,
            "trace_id": getattr(result, 'trace_id', None),
            "agent_name": "gita_insights_agent",
            "model": "gemini-2.0-flash-latest",
            "tool_calls": getattr(result, 'tool_calls', []),
            "adk_version": "real"
        }

    except Exception as e:
        logger.error(f"Error in ask_gita_adk_agent: {e}")
        return {
            "error": str(e),
            "answer": "Hare Krishna! I encountered an error while processing your question. Please try again."
        }
