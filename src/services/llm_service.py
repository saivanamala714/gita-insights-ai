"""
LLM Integration Service
Supports OpenAI and Ollama for answer generation
"""

import logging
from typing import List, Optional

from openai import OpenAI

from ..config.settings import Settings, get_settings
from ..models.schemas import SourceCitation

logger = logging.getLogger(__name__)


class LLMService:
    """LLM service for generating answers from context"""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        self.client: Optional[OpenAI] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize LLM client"""
        if self._initialized:
            return
        
        if self.settings.llm_provider == "openai":
            if not self.settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            
            logger.info("Initializing OpenAI client")
            self.client = OpenAI(api_key=self.settings.openai_api_key)
            self._initialized = True
        
        elif self.settings.llm_provider == "ollama":
            logger.info("Initializing Ollama client")
            self.client = OpenAI(
                base_url=self.settings.ollama_base_url,
                api_key="ollama"  # Ollama doesn't need real API key
            )
            self._initialized = True
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.settings.llm_provider}")
    
    def generate_answer(
        self,
        question: str,
        sources: List[SourceCitation],
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate answer from question and source context
        
        Args:
            question: User's question
            sources: List of source citations
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated answer
        """
        if not self._initialized:
            self.initialize()
        
        # Build context from sources
        context = self._build_context(sources)
        
        # Build prompt
        prompt = self._build_prompt(question, context)
        
        # Generate answer
        try:
            if self.settings.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.settings.openai_temperature,
                    max_tokens=max_tokens or self.settings.openai_max_tokens
                )
                answer = response.choices[0].message.content
            
            elif self.settings.llm_provider == "ollama":
                response = self.client.chat.completions.create(
                    model=self.settings.ollama_model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.settings.openai_temperature
                )
                answer = response.choices[0].message.content
            
            else:
                raise ValueError(f"Unsupported provider: {self.settings.llm_provider}")
            
            logger.info(f"Generated answer of length {len(answer)}")
            return answer.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the LLM"""
        return """You are a knowledgeable assistant specializing in the Bhagavad Gita.

Your role is to answer questions based EXCLUSIVELY on the provided context from the Bhagavad Gita PDF.

STRICT RULES:
1. Answer ONLY using information from the provided context
2. If the context doesn't contain enough information to answer, say: "I don't have enough information in the provided text to answer this question."
3. Be accurate and faithful to the source material
4. Include verse references (e.g., Bg 2.47) when relevant
5. Be clear, concise, and respectful
6. Do not add information from your general knowledge
7. Do not make assumptions beyond what's in the context

When answering:
- Quote relevant verses when appropriate
- Explain concepts clearly
- Maintain the spiritual and philosophical tone of the Gita
- Be helpful and educational"""
    
    def _build_context(self, sources: List[SourceCitation]) -> str:
        """
        Build context string from sources
        
        Args:
            sources: List of source citations
            
        Returns:
            Formatted context string
        """
        if not sources:
            return "No relevant context found."
        
        context_parts = []
        for i, source in enumerate(sources, 1):
            # Build source header
            header_parts = [f"Source {i}"]
            if source.verse_reference:
                header_parts.append(f"({source.verse_reference})")
            elif source.chapter and source.verse:
                header_parts.append(f"(Bg {source.chapter}.{source.verse})")
            if source.page:
                header_parts.append(f"[Page {source.page}]")
            
            header = " ".join(header_parts)
            
            # Add to context
            context_parts.append(f"{header}:\n{source.excerpt}\n")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build the full prompt for the LLM
        
        Args:
            question: User's question
            context: Context from sources
            
        Returns:
            Formatted prompt
        """
        # Truncate context if too long
        max_context = self.settings.max_context_length
        if len(context) > max_context:
            context = context[:max_context] + "\n...[context truncated]"
        
        prompt = f"""Context from the Bhagavad Gita:

{context}

Question: {question}

Please answer the question based on the context provided above. If the context doesn't contain enough information to answer the question, please say so."""
        
        return prompt
    
    def check_connection(self) -> bool:
        """
        Check if LLM service is accessible
        
        Returns:
            True if connection successful
        """
        try:
            if not self._initialized:
                self.initialize()
            
            # Try a simple completion
            response = self.client.chat.completions.create(
                model=self.settings.openai_model if self.settings.llm_provider == "openai" else self.settings.ollama_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"LLM connection check failed: {e}")
            return False
