"""
User Feedback Service for Bhagavad Gita Q&A System

This module handles user feedback (thumbs up/down) for answers,
storing feedback in Firestore for analytics and improvement.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


class FeedbackService:
    """Service for managing user feedback in Firestore."""
    
    def __init__(self, database_id: str = None, collection_prefix: str = "prod"):
        """
        Initialize the Feedback Service.
        
        Args:
            database_id: Firestore database ID (default from env)
            collection_prefix: Collection prefix for environment separation
        """
        self.database_id = database_id or os.getenv("FIRESTORE_DATABASE_ID", "(default)")
        self.collection_prefix = collection_prefix
        self.collection_name = f"{collection_prefix}_user_feedback"
        
        # Initialize Firestore client
        if self.database_id == "(default)":
            self.db = firestore.Client()
        else:
            self.db = firestore.Client(database=self.database_id)
        
        print(f"✅ FeedbackService initialized with collection: {self.collection_name}")
    
    def save_feedback(
        self,
        question: str,
        answer: str,
        liked: bool,
        user_id: str,
        conversation_id: Optional[str] = None,
        message_id: Optional[str] = None,
        sources: Optional[List[Dict[str, Any]]] = None,
        feedback_text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save user feedback to Firestore.
        
        Args:
            question: The user's question
            answer: The answer provided by the system
            liked: True for thumbs up, False for thumbs down
            user_id: User identifier
            conversation_id: Optional conversation ID
            message_id: Optional message ID
            sources: Optional list of source references
            feedback_text: Optional text feedback from user
            metadata: Optional additional metadata (IP, user agent, etc.)
        
        Returns:
            feedback_id: The ID of the created feedback document
        """
        try:
            # Create feedback document
            feedback_ref = self.db.collection(self.collection_name).document()
            feedback_id = feedback_ref.id
            
            now = datetime.utcnow()
            
            feedback_data = {
                "feedback_id": feedback_id,
                "question": question,
                "answer": answer,
                "liked": liked,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message_id": message_id,
                "sources": sources or [],
                "feedback_text": feedback_text,
                "created_at": now,
                "updated_at": now,
                "metadata": metadata or {}
            }
            
            # Remove None values to keep documents clean
            feedback_data = {k: v for k, v in feedback_data.items() if v is not None}
            
            # Save to Firestore
            feedback_ref.set(feedback_data)
            
            print(f"✅ Feedback saved: {feedback_id} (liked={liked})")
            return feedback_id
            
        except Exception as e:
            print(f"❌ Error saving feedback: {e}")
            raise
    
    def get_feedback(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific feedback by ID.
        
        Args:
            feedback_id: The feedback document ID
        
        Returns:
            Feedback data or None if not found
        """
        try:
            doc = self.db.collection(self.collection_name).document(feedback_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"❌ Error retrieving feedback: {e}")
            return None
    
    def get_user_feedback(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all feedback from a specific user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of results
        
        Returns:
            List of feedback documents
        """
        try:
            query = (
                self.db.collection(self.collection_name)
                .where(filter=FieldFilter("user_id", "==", user_id))
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)
            )
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            print(f"❌ Error retrieving user feedback: {e}")
            return []
    
    def get_conversation_feedback(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all feedback for a specific conversation.
        
        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of results
        
        Returns:
            List of feedback documents
        """
        try:
            query = (
                self.db.collection(self.collection_name)
                .where(filter=FieldFilter("conversation_id", "==", conversation_id))
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)
            )
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            print(f"❌ Error retrieving conversation feedback: {e}")
            return []
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Get aggregated feedback statistics.
        
        Returns:
            Dictionary with feedback statistics
        """
        try:
            # Get all feedback (limited to recent 1000 for performance)
            all_feedback = (
                self.db.collection(self.collection_name)
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(1000)
                .stream()
            )
            
            total = 0
            thumbs_up = 0
            thumbs_down = 0
            recent_feedback = []
            
            for doc in all_feedback:
                data = doc.to_dict()
                total += 1
                
                if data.get("liked"):
                    thumbs_up += 1
                else:
                    thumbs_down += 1
                
                # Keep last 10 for recent feedback
                if len(recent_feedback) < 10:
                    recent_feedback.append({
                        "feedback_id": data.get("feedback_id"),
                        "question": data.get("question", "")[:100],  # Truncate
                        "liked": data.get("liked"),
                        "created_at": data.get("created_at").isoformat() if data.get("created_at") else None
                    })
            
            satisfaction_rate = (thumbs_up / total * 100) if total > 0 else 0
            
            return {
                "total_feedback": total,
                "thumbs_up": thumbs_up,
                "thumbs_down": thumbs_down,
                "satisfaction_rate": round(satisfaction_rate, 2),
                "recent_feedback": recent_feedback
            }
            
        except Exception as e:
            print(f"❌ Error calculating feedback stats: {e}")
            return {
                "total_feedback": 0,
                "thumbs_up": 0,
                "thumbs_down": 0,
                "satisfaction_rate": 0,
                "recent_feedback": [],
                "error": str(e)
            }
    
    def update_feedback(
        self,
        feedback_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update an existing feedback document.
        
        Args:
            feedback_id: The feedback document ID
            updates: Dictionary of fields to update
        
        Returns:
            True if successful, False otherwise
        """
        try:
            updates["updated_at"] = datetime.utcnow()
            
            self.db.collection(self.collection_name).document(feedback_id).update(updates)
            print(f"✅ Feedback updated: {feedback_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating feedback: {e}")
            return False
    
    def delete_feedback(self, feedback_id: str) -> bool:
        """
        Delete a feedback document.
        
        Args:
            feedback_id: The feedback document ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.collection(self.collection_name).document(feedback_id).delete()
            print(f"✅ Feedback deleted: {feedback_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting feedback: {e}")
            return False
