"""High-level chat history management with business logic."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.services.firestore_service import firestore_service
from src.services.metadata_extractor import metadata_extractor

logger = logging.getLogger(__name__)


class ChatHistoryManager:
    """Manage chat history with business logic and metadata extraction."""
    
    def __init__(self):
        self.firestore = firestore_service
        self.metadata_extractor = metadata_extractor
    
    def create_or_get_conversation(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Create a new conversation or return existing one.
        
        Args:
            user_id: User identifier
            conversation_id: Optional existing conversation ID
            title: Optional conversation title
        
        Returns:
            Conversation ID
        """
        if conversation_id:
            # Verify conversation exists
            conv = self.firestore.get_conversation(user_id, conversation_id)
            if conv:
                return conversation_id
            logger.warning(f"Conversation {conversation_id} not found, creating new one")
        
        # Create new conversation
        return self.firestore.create_conversation(user_id, title)
    
    def add_qa_to_conversation(
        self,
        user_id: str,
        conversation_id: str,
        question: str,
        answer: str,
        sources: List[Dict[str, Any]] = None,
        response_time_ms: Optional[int] = None
    ) -> str:
        """
        Add a Q&A pair to a conversation with automatic metadata extraction.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation ID
            question: User's question
            answer: AI's answer
            sources: Source documents used
            response_time_ms: Response time in milliseconds
        
        Returns:
            Message ID
        """
        # Extract metadata from question and answer
        metadata = self.metadata_extractor.extract_metadata(question, answer)
        
        # Add response time if provided
        if response_time_ms is not None:
            metadata['response_time_ms'] = response_time_ms
        
        # Save to Firestore
        message_id = self.firestore.add_message(
            user_id=user_id,
            conversation_id=conversation_id,
            user_query=question,
            ai_response=answer,
            sources=sources or [],
            metadata=metadata
        )
        
        logger.info(f"Added Q&A to conversation {conversation_id}, extracted metadata: "
                   f"{len(metadata.get('chapter_references', []))} chapters, "
                   f"{len(metadata.get('themes', []))} themes")
        
        return message_id
    
    def get_conversation_context(
        self,
        user_id: str,
        conversation_id: str,
        context_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent messages for conversation context.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation ID
            context_size: Number of recent messages to retrieve
        
        Returns:
            List of recent messages
        """
        return self.firestore.get_recent_messages(
            user_id=user_id,
            conversation_id=conversation_id,
            count=context_size
        )
    
    def get_conversation_history(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get full conversation history with metadata.
        
        Returns:
            Dict with conversation metadata and messages
        """
        # Get conversation metadata
        conversation = self.firestore.get_conversation(user_id, conversation_id)
        if not conversation:
            return None
        
        # Get messages
        messages = self.firestore.get_conversation_messages(
            user_id=user_id,
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
        )
        
        return {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'metadata': conversation,
            'messages': messages,
            'total_messages': conversation.get('message_count', 0)
        }
    
    def get_user_conversations(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a user."""
        return self.firestore.get_user_conversations(
            user_id=user_id,
            limit=limit,
            offset=offset,
            include_archived=include_archived
        )
    
    def delete_conversation(self, user_id: str, conversation_id: str):
        """Delete a conversation."""
        self.firestore.delete_conversation(user_id, conversation_id)
        logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
    
    def format_context_for_rag(
        self,
        messages: List[Dict[str, Any]],
        max_messages: int = 5
    ) -> str:
        """
        Format conversation context for RAG system.
        
        Args:
            messages: List of recent messages
            max_messages: Maximum number of messages to include
        
        Returns:
            Formatted context string
        """
        if not messages:
            return ""
        
        # Take only the most recent messages
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
        
        context_parts = ["Previous conversation context:"]
        for msg in recent_messages:
            context_parts.append(f"Q: {msg.get('user_query', '')}")
            # Include a shortened version of the answer
            answer = msg.get('ai_response', '')
            if len(answer) > 200:
                answer = answer[:200] + "..."
            context_parts.append(f"A: {answer}")
        
        return "\n".join(context_parts)
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a user."""
        profile = self.firestore.get_user_profile(user_id)
        if not profile:
            return None
        
        conversations = self.firestore.get_user_conversations(user_id, limit=1000)
        
        # Aggregate topics and chapters
        all_topics = set()
        all_chapters = set()
        
        for conv in conversations:
            all_topics.update(conv.get('topics', []))
            all_chapters.update(conv.get('chapters_referenced', []))
        
        return {
            'user_id': user_id,
            'total_conversations': profile.get('total_conversations', 0),
            'total_messages': profile.get('total_messages', 0),
            'favorite_topics': sorted(list(all_topics)),
            'favorite_chapters': sorted(list(all_chapters)),
            'created_at': profile.get('created_at'),
            'last_active': profile.get('last_active')
        }


# Global instance
chat_history_manager = ChatHistoryManager()
