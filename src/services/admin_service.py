"""Admin service for managing all users and conversations."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from src.services.firestore_service import firestore_service
from src.services.metadata_extractor import metadata_extractor

logger = logging.getLogger(__name__)


class AdminService:
    """Admin operations for viewing and managing all user data."""
    
    def __init__(self):
        self.firestore = firestore_service
        self.metadata_extractor = metadata_extractor
    
    def get_all_conversations(
        self,
        limit: int = 100,
        offset: int = 0,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        topic: Optional[str] = None,
        chapter: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get all conversations with filtering options.
        
        Returns:
            Dict with conversations list and metadata
        """
        if user_id:
            # Get conversations for specific user
            conversations = self.firestore.get_user_conversations(
                user_id=user_id,
                limit=limit,
                offset=offset,
                include_archived=True
            )
        else:
            # Get all conversations across all users
            conversations = self.firestore.get_all_conversations(
                limit=limit,
                offset=offset,
                start_date=start_date,
                end_date=end_date
            )
        
        # Apply additional filters
        filtered_conversations = conversations
        
        if topic:
            filtered_conversations = [
                c for c in filtered_conversations
                if topic.lower() in [t.lower() for t in c.get('topics', [])]
            ]
        
        if chapter:
            filtered_conversations = [
                c for c in filtered_conversations
                if chapter in c.get('chapters_referenced', [])
            ]
        
        return {
            'conversations': filtered_conversations,
            'total': len(filtered_conversations),
            'limit': limit,
            'offset': offset
        }
    
    def get_conversation_details(
        self,
        user_id: str,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed conversation information including all messages."""
        conversation = self.firestore.get_conversation(user_id, conversation_id)
        if not conversation:
            return None
        
        messages = self.firestore.get_conversation_messages(
            user_id=user_id,
            conversation_id=conversation_id,
            limit=1000  # Get all messages
        )
        
        return {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'metadata': conversation,
            'messages': messages,
            'total_messages': len(messages)
        }
    
    def search_all_conversations(
        self,
        query: str,
        search_in: str = 'both',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search across all conversations.
        
        Args:
            query: Search query
            search_in: Where to search - 'question', 'answer', or 'both'
            limit: Maximum results
        
        Returns:
            List of matching messages with context
        """
        results = self.firestore.search_messages(
            query=query,
            search_in=search_in,
            limit=limit
        )
        
        # Enrich results with conversation context
        enriched_results = []
        for result in results:
            conversation = self.firestore.get_conversation(
                result['user_id'],
                result['conversation_id']
            )
            
            result['conversation_title'] = conversation.get('title') if conversation else 'Untitled'
            enriched_results.append(result)
        
        return enriched_results
    
    def get_all_users(
        self,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = 'created_at'
    ) -> Dict[str, Any]:
        """
        Get all users with their statistics.
        
        Args:
            limit: Maximum users to return
            offset: Offset for pagination
            sort_by: Field to sort by
        
        Returns:
            Dict with users list and metadata
        """
        users = self.firestore.get_all_users(limit=limit, offset=offset)
        
        return {
            'users': users,
            'total': len(users),
            'limit': limit,
            'offset': offset
        }
    
    def get_user_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed user information."""
        profile = self.firestore.get_user_profile(user_id)
        if not profile:
            return None
        
        conversations = self.firestore.get_user_conversations(
            user_id=user_id,
            limit=1000,
            include_archived=True
        )
        
        # Aggregate statistics
        all_topics = set()
        all_chapters = set()
        total_messages = 0
        
        for conv in conversations:
            all_topics.update(conv.get('topics', []))
            all_chapters.update(conv.get('chapters_referenced', []))
            total_messages += conv.get('message_count', 0)
        
        return {
            'user_id': user_id,
            'profile': profile,
            'total_conversations': len(conversations),
            'total_messages': total_messages,
            'topics_explored': sorted(list(all_topics)),
            'chapters_studied': sorted(list(all_chapters)),
            'conversations': conversations[:10]  # Recent 10
        }
    
    def delete_user_data(self, user_id: str):
        """Delete all data for a user (GDPR compliance)."""
        # Get all conversations
        conversations = self.firestore.get_user_conversations(
            user_id=user_id,
            limit=1000,
            include_archived=True
        )
        
        # Delete each conversation
        for conv in conversations:
            self.firestore.delete_conversation(user_id, conv['conversation_id'])
        
        # Delete user profile
        user_ref = self.firestore.db.collection(
            self.firestore.users_collection
        ).document(user_id)
        user_ref.delete()
        
        logger.info(f"Deleted all data for user {user_id}")
    
    def export_conversation(
        self,
        user_id: str,
        conversation_id: str,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """Export a conversation in specified format."""
        conversation = self.get_conversation_details(user_id, conversation_id)
        
        if not conversation:
            return None
        
        if format == 'json':
            return conversation
        
        # Add other formats as needed (CSV, PDF, etc.)
        return conversation
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics."""
        try:
            # Test Firestore connection
            firestore_healthy = self.firestore.db is not None
            
            # Get basic stats
            global_stats = self.firestore.get_global_stats() or {}
            
            return {
                'status': 'healthy' if firestore_healthy else 'unhealthy',
                'firestore_connected': firestore_healthy,
                'total_users': global_stats.get('total_users', 0),
                'total_conversations': global_stats.get('total_conversations', 0),
                'total_messages': global_stats.get('total_messages', 0),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Global instance
admin_service = AdminService()
