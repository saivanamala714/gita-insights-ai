"""Core Firestore operations for chat history."""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.cloud import firestore
from src.config.firestore_config import firestore_config

logger = logging.getLogger(__name__)


class FirestoreService:
    """Core Firestore database operations."""
    
    def __init__(self):
        self.db = firestore_config.client
        self.users_collection = firestore_config.get_collection_name('users')
        self.analytics_collection = firestore_config.get_collection_name('analytics')
    
    # ========== User Operations ==========
    
    def create_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Create a new user profile."""
        user_ref = self.db.collection(self.users_collection).document(user_id)
        
        profile_data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_active': firestore.SERVER_TIMESTAMP,
            'total_conversations': 0,
            'total_messages': 0,
            'favorite_topics': []
        }
        
        user_ref.set(profile_data)
        logger.info(f"Created user profile for {user_id}")
        return profile_data
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile."""
        user_ref = self.db.collection(self.users_collection).document(user_id)
        doc = user_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    def update_user_activity(self, user_id: str):
        """Update user's last active timestamp."""
        user_ref = self.db.collection(self.users_collection).document(user_id)
        user_ref.update({'last_active': firestore.SERVER_TIMESTAMP})
    
    # ========== Conversation Operations ==========
    
    def create_conversation(self, user_id: str, title: Optional[str] = None) -> str:
        """Create a new conversation."""
        # Ensure user profile exists
        if not self.get_user_profile(user_id):
            self.create_user_profile(user_id)
        
        # Create conversation
        conv_ref = self.db.collection(self.users_collection)\
            .document(user_id)\
            .collection('conversations')\
            .document()
        
        metadata = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'message_count': 0,
            'title': title,
            'topics': [],
            'chapters_referenced': [],
            'characters_mentioned': [],
            'is_archived': False
        }
        
        conv_ref.set(metadata)
        
        # Update user stats
        user_ref = self.db.collection(self.users_collection).document(user_id)
        user_ref.update({
            'total_conversations': firestore.Increment(1),
            'last_active': firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Created conversation {conv_ref.id} for user {user_id}")
        return conv_ref.id
    
    def get_conversation(self, user_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation metadata."""
        conv_ref = self.db.collection(self.users_collection)\
            .document(user_id)\
            .collection('conversations')\
            .document(conversation_id)
        
        doc = conv_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data['conversation_id'] = conversation_id
            return data
        return None
    
    def get_user_conversations(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a user."""
        query = self.db.collection(self.users_collection)\
            .document(user_id)\
            .collection('conversations')\
            .order_by('updated_at', direction=firestore.Query.DESCENDING)
        
        if not include_archived:
            query = query.where('is_archived', '==', False)
        
        query = query.limit(limit).offset(offset)
        
        conversations = []
        for doc in query.stream():
            data = doc.to_dict()
            data['conversation_id'] = doc.id
            data['user_id'] = user_id
            conversations.append(data)
        
        return conversations
    
    def delete_conversation(self, user_id: str, conversation_id: str):
        """Delete a conversation and all its messages."""
        conv_ref = self.db.collection(self.users_collection)\
            .document(user_id)\
            .collection('conversations')\
            .document(conversation_id)
        
        # Delete all messages first
        messages_ref = conv_ref.collection('messages')
        batch = self.db.batch()
        
        for msg_doc in messages_ref.stream():
            batch.delete(msg_doc.reference)
        
        # Delete conversation
        batch.delete(conv_ref)
        batch.commit()
        
        logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
    
    # ========== Message Operations ==========
    
    def add_message(
        self,
        user_id: str,
        conversation_id: str,
        user_query: str,
        ai_response: str,
        sources: List[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Add a message to a conversation."""
        conv_ref = self.db.collection(self.users_collection)\
            .document(user_id)\
            .collection('conversations')\
            .document(conversation_id)
        
        # Create message
        message_ref = conv_ref.collection('messages').document()
        
        message_data = {
            'timestamp': firestore.SERVER_TIMESTAMP,
            'user_query': user_query,
            'ai_response': ai_response,
            'sources': sources or [],
            'chapter_references': metadata.get('chapter_references', []) if metadata else [],
            'verse_references': metadata.get('verse_references', []) if metadata else [],
            'themes': metadata.get('themes', []) if metadata else [],
            'characters_mentioned': metadata.get('characters_mentioned', []) if metadata else [],
            'response_time_ms': metadata.get('response_time_ms') if metadata else None,
            'metadata': metadata or {}
        }
        
        message_ref.set(message_data)
        
        # Update conversation metadata
        update_data = {
            'updated_at': firestore.SERVER_TIMESTAMP,
            'message_count': firestore.Increment(1)
        }
        
        # Auto-generate title from first message
        conv_doc = conv_ref.get()
        if conv_doc.exists and conv_doc.to_dict().get('message_count', 0) == 0:
            update_data['title'] = user_query[:100]  # First 100 chars
        
        # Update topics, chapters, characters
        if metadata:
            if metadata.get('themes'):
                update_data['topics'] = firestore.ArrayUnion(metadata['themes'])
            if metadata.get('chapter_references'):
                update_data['chapters_referenced'] = firestore.ArrayUnion(metadata['chapter_references'])
            if metadata.get('characters_mentioned'):
                update_data['characters_mentioned'] = firestore.ArrayUnion(metadata['characters_mentioned'])
        
        conv_ref.update(update_data)
        
        # Update user stats
        user_ref = self.db.collection(self.users_collection).document(user_id)
        user_ref.update({
            'total_messages': firestore.Increment(1),
            'last_active': firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Added message {message_ref.id} to conversation {conversation_id}")
        return message_ref.id
    
    def get_conversation_messages(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get messages from a conversation."""
        messages_ref = self.db.collection(self.users_collection)\
            .document(user_id)\
            .collection('conversations')\
            .document(conversation_id)\
            .collection('messages')\
            .order_by('timestamp', direction=firestore.Query.ASCENDING)\
            .limit(limit)\
            .offset(offset)
        
        messages = []
        for doc in messages_ref.stream():
            data = doc.to_dict()
            data['message_id'] = doc.id
            data['conversation_id'] = conversation_id
            messages.append(data)
        
        return messages
    
    def get_recent_messages(
        self,
        user_id: str,
        conversation_id: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent messages for context."""
        messages_ref = self.db.collection(self.users_collection)\
            .document(user_id)\
            .collection('conversations')\
            .document(conversation_id)\
            .collection('messages')\
            .order_by('timestamp', direction=firestore.Query.DESCENDING)\
            .limit(count)
        
        messages = []
        for doc in messages_ref.stream():
            data = doc.to_dict()
            data['message_id'] = doc.id
            messages.append(data)
        
        return list(reversed(messages))  # Return in chronological order
    
    # ========== Admin Operations ==========
    
    def get_all_conversations(
        self,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get all conversations across all users (admin only)."""
        query = self.db.collection_group('conversations')\
            .order_by('created_at', direction=firestore.Query.DESCENDING)
        
        if start_date:
            query = query.where('created_at', '>=', start_date)
        if end_date:
            query = query.where('created_at', '<=', end_date)
        
        query = query.limit(limit).offset(offset)
        
        conversations = []
        for doc in query.stream():
            data = doc.to_dict()
            data['conversation_id'] = doc.id
            # Extract user_id from document path
            data['user_id'] = doc.reference.parent.parent.id
            conversations.append(data)
        
        return conversations
    
    def search_messages(
        self,
        query: str,
        search_in: str = 'both',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search across all messages (admin only)."""
        # Note: Firestore doesn't support full-text search natively
        # This is a basic implementation. For production, consider Algolia or Elasticsearch
        
        messages_query = self.db.collection_group('messages')\
            .limit(limit * 5)  # Get more to filter
        
        results = []
        query_lower = query.lower()
        
        for doc in messages_query.stream():
            data = doc.to_dict()
            
            match = False
            match_type = None
            
            if search_in in ['question', 'both']:
                if query_lower in data.get('user_query', '').lower():
                    match = True
                    match_type = 'question'
            if search_in in ['answer', 'both']:
                if query_lower in data.get('ai_response', '').lower():
                    match = True
                    match_type = 'answer' if match_type is None else 'both'
            
            if match:
                data['message_id'] = doc.id
                data['match_type'] = match_type
                # Extract conversation_id and user_id from path
                data['conversation_id'] = doc.reference.parent.parent.id
                data['user_id'] = doc.reference.parent.parent.parent.parent.id
                results.append(data)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users (admin only)."""
        users_ref = self.db.collection(self.users_collection)\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(limit)\
            .offset(offset)
        
        users = []
        for doc in users_ref.stream():
            data = doc.to_dict()
            data['user_id'] = doc.id
            users.append(data)
        
        return users
    
    # ========== Analytics Operations ==========
    
    def update_daily_stats(self, date: str, stats: Dict[str, Any]):
        """Update daily statistics."""
        stats_ref = self.db.collection(self.analytics_collection)\
            .document('daily_stats')\
            .collection('dates')\
            .document(date)
        
        stats_ref.set(stats, merge=True)
    
    def get_daily_stats(self, date: str) -> Optional[Dict[str, Any]]:
        """Get daily statistics."""
        stats_ref = self.db.collection(self.analytics_collection)\
            .document('daily_stats')\
            .collection('dates')\
            .document(date)
        
        doc = stats_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def update_global_stats(self, stats: Dict[str, Any]):
        """Update global statistics."""
        stats_ref = self.db.collection(self.analytics_collection)\
            .document('global_stats')
        
        stats_ref.set(stats, merge=True)
    
    def get_global_stats(self) -> Optional[Dict[str, Any]]:
        """Get global statistics."""
        stats_ref = self.db.collection(self.analytics_collection)\
            .document('global_stats')
        
        doc = stats_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None


# Global instance
firestore_service = FirestoreService()
