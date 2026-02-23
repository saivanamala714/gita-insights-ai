"""Analytics service for generating insights and statistics."""
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import Counter
from src.services.firestore_service import firestore_service

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Generate analytics and insights from chat data."""
    
    def __init__(self):
        self.firestore = firestore_service
    
    def get_admin_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics for admin dashboard.
        
        Returns:
            Dict with various analytics metrics
        """
        # Get global stats
        global_stats = self.firestore.get_global_stats() or {}
        
        # Get today's stats
        today = datetime.utcnow().date().isoformat()
        today_stats = self.firestore.get_daily_stats(today) or {}
        
        # Get this week's stats
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Get recent conversations for analysis
        recent_conversations = self.firestore.get_all_conversations(
            limit=1000,
            start_date=week_ago
        )
        
        # Analyze recent data
        chapter_counter = Counter()
        topic_counter = Counter()
        total_messages_week = 0
        active_users = set()
        
        for conv in recent_conversations:
            active_users.add(conv.get('user_id'))
            total_messages_week += conv.get('message_count', 0)
            
            for chapter in conv.get('chapters_referenced', []):
                chapter_counter[chapter] += 1
            
            for topic in conv.get('topics', []):
                topic_counter[topic] += 1
        
        # Get top questions (from recent messages)
        top_questions = self._get_top_questions(limit=10)
        
        return {
            'total_users': global_stats.get('total_users', 0),
            'total_conversations': global_stats.get('total_conversations', 0),
            'total_messages': global_stats.get('total_messages', 0),
            'messages_today': today_stats.get('total_messages', 0),
            'messages_this_week': total_messages_week,
            'active_users_today': today_stats.get('unique_users', 0),
            'active_users_this_week': len(active_users),
            'top_questions': top_questions,
            'popular_chapters': [
                {'chapter': ch, 'count': count}
                for ch, count in chapter_counter.most_common(10)
            ],
            'popular_topics': [
                {'topic': topic, 'count': count}
                for topic, count in topic_counter.most_common(10)
            ],
            'avg_response_time_ms': global_stats.get('avg_response_time_ms', 0)
        }
    
    def _get_top_questions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently asked questions."""
        # Get recent messages
        messages = self.firestore.db.collection_group('messages')\
            .order_by('timestamp', direction=firestore_service.db.Query.DESCENDING)\
            .limit(1000)\
            .stream()
        
        question_counter = Counter()
        question_details = {}
        
        for doc in messages:
            data = doc.to_dict()
            question = data.get('user_query', '').strip()
            
            if question:
                # Normalize question for counting
                question_lower = question.lower()
                question_counter[question_lower] += 1
                
                # Store original question
                if question_lower not in question_details:
                    question_details[question_lower] = {
                        'question': question,
                        'count': 0,
                        'chapters': set(),
                        'themes': set()
                    }
                
                question_details[question_lower]['count'] += 1
                question_details[question_lower]['chapters'].update(
                    data.get('chapter_references', [])
                )
                question_details[question_lower]['themes'].update(
                    data.get('themes', [])
                )
        
        # Get top questions
        top_questions = []
        for question_lower, count in question_counter.most_common(limit):
            details = question_details[question_lower]
            top_questions.append({
                'question': details['question'],
                'count': count,
                'chapters': sorted(list(details['chapters'])),
                'themes': sorted(list(details['themes']))
            })
        
        return top_questions
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for a specific user."""
        profile = self.firestore.get_user_profile(user_id)
        if not profile:
            return None
        
        conversations = self.firestore.get_user_conversations(
            user_id=user_id,
            limit=1000,
            include_archived=True
        )
        
        # Analyze user's conversations
        chapter_counter = Counter()
        topic_counter = Counter()
        character_counter = Counter()
        
        for conv in conversations:
            for chapter in conv.get('chapters_referenced', []):
                chapter_counter[chapter] += 1
            for topic in conv.get('topics', []):
                topic_counter[topic] += 1
            for character in conv.get('characters_mentioned', []):
                character_counter[character] += 1
        
        return {
            'user_id': user_id,
            'total_conversations': len(conversations),
            'total_messages': profile.get('total_messages', 0),
            'member_since': profile.get('created_at'),
            'last_active': profile.get('last_active'),
            'favorite_chapters': [
                {'chapter': ch, 'count': count}
                for ch, count in chapter_counter.most_common(5)
            ],
            'favorite_topics': [
                {'topic': topic, 'count': count}
                for topic, count in topic_counter.most_common(5)
            ],
            'characters_explored': [
                {'character': char, 'count': count}
                for char, count in character_counter.most_common(5)
            ]
        }
    
    def update_daily_stats(self):
        """Update daily statistics (run this as a scheduled job)."""
        today = datetime.utcnow().date().isoformat()
        
        # Get today's conversations
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        conversations = self.firestore.get_all_conversations(
            limit=10000,
            start_date=today_start
        )
        
        # Calculate stats
        unique_users = set()
        total_messages = 0
        chapter_counter = Counter()
        
        for conv in conversations:
            unique_users.add(conv.get('user_id'))
            total_messages += conv.get('message_count', 0)
            
            for chapter in conv.get('chapters_referenced', []):
                chapter_counter[chapter] += 1
        
        stats = {
            'date': today,
            'total_messages': total_messages,
            'unique_users': len(unique_users),
            'total_conversations': len(conversations),
            'top_chapters': [
                {'chapter': ch, 'count': count}
                for ch, count in chapter_counter.most_common(5)
            ],
            'updated_at': datetime.utcnow().isoformat()
        }
        
        self.firestore.update_daily_stats(today, stats)
        logger.info(f"Updated daily stats for {today}")
    
    def update_global_stats(self):
        """Update global statistics (run this periodically)."""
        # Count total users
        all_users = self.firestore.get_all_users(limit=100000)
        total_users = len(all_users)
        
        # Count total conversations and messages
        total_conversations = 0
        total_messages = 0
        
        for user in all_users:
            total_conversations += user.get('total_conversations', 0)
            total_messages += user.get('total_messages', 0)
        
        stats = {
            'total_users': total_users,
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        self.firestore.update_global_stats(stats)
        logger.info(f"Updated global stats: {stats}")


# Global instance
analytics_service = AnalyticsService()
