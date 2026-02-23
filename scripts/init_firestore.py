#!/usr/bin/env python3
"""
Initialize Firestore collections and indexes for chat history.

This script sets up the necessary Firestore structure and creates
initial analytics documents.

Usage:
    python scripts/init_firestore.py
"""
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.firestore_service import firestore_service


def init_analytics_collections():
    """Initialize analytics collections with default values."""
    print("Initializing analytics collections...")
    
    # Create global stats document
    global_stats = {
        'total_users': 0,
        'total_conversations': 0,
        'total_messages': 0,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    firestore_service.update_global_stats(global_stats)
    print("✓ Global stats initialized")
    
    # Create today's daily stats
    today = datetime.utcnow().date().isoformat()
    daily_stats = {
        'date': today,
        'total_messages': 0,
        'unique_users': 0,
        'total_conversations': 0,
        'top_chapters': [],
        'created_at': datetime.utcnow().isoformat()
    }
    
    firestore_service.update_daily_stats(today, daily_stats)
    print(f"✓ Daily stats initialized for {today}")


def create_test_user():
    """Create a test user for verification."""
    print("\nCreating test user...")
    
    test_user_id = "test_user_001"
    
    # Create user profile
    firestore_service.create_user_profile(test_user_id)
    print(f"✓ Test user created: {test_user_id}")
    
    # Create a test conversation
    conversation_id = firestore_service.create_conversation(
        user_id=test_user_id,
        title="Test Conversation"
    )
    print(f"✓ Test conversation created: {conversation_id}")
    
    # Add a test message
    message_id = firestore_service.add_message(
        user_id=test_user_id,
        conversation_id=conversation_id,
        user_query="What is the main message of the Bhagavad Gita?",
        ai_response="The main message of the Bhagavad Gita is to perform one's duty without attachment to results, while maintaining devotion to the Supreme.",
        sources=[],
        metadata={
            'chapter_references': [2, 3, 18],
            'themes': ['dharma', 'karma', 'devotion'],
            'characters_mentioned': ['Krishna', 'Arjuna']
        }
    )
    print(f"✓ Test message created: {message_id}")
    
    return test_user_id, conversation_id


def verify_setup():
    """Verify that Firestore is set up correctly."""
    print("\nVerifying Firestore setup...")
    
    # Check global stats
    global_stats = firestore_service.get_global_stats()
    if global_stats:
        print("✓ Global stats accessible")
    else:
        print("✗ Global stats not found")
        return False
    
    # Check daily stats
    today = datetime.utcnow().date().isoformat()
    daily_stats = firestore_service.get_daily_stats(today)
    if daily_stats:
        print("✓ Daily stats accessible")
    else:
        print("✗ Daily stats not found")
        return False
    
    print("\n✓ Firestore setup verified successfully!")
    return True


def main():
    print("=" * 60)
    print("Firestore Chat History Initialization")
    print("=" * 60)
    
    try:
        # Check if Firestore is configured
        if not os.getenv('GOOGLE_CLOUD_PROJECT'):
            print("\n✗ Error: GOOGLE_CLOUD_PROJECT not set in environment")
            print("Please set up your .env file with Firestore configuration")
            return
        
        print(f"\nProject: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
        print(f"Collection Prefix: {os.getenv('FIRESTORE_COLLECTION_PREFIX', 'prod')}")
        
        # Initialize collections
        init_analytics_collections()
        
        # Create test data
        create_test = input("\nCreate test user and conversation? (y/n): ").lower()
        if create_test == 'y':
            test_user_id, conversation_id = create_test_user()
            print(f"\nTest data created:")
            print(f"  User ID: {test_user_id}")
            print(f"  Conversation ID: {conversation_id}")
        
        # Verify setup
        verify_setup()
        
        print("\n" + "=" * 60)
        print("Initialization Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start your application: python app.py")
        print("2. Test the /ask endpoint with save_to_history=true")
        print("3. Access admin dashboard at /api/admin/analytics")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
