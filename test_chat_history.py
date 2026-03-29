#!/usr/bin/env python3
"""Simple test script for chat history functionality."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("Testing Firestore Chat History")
print("=" * 60)
print(f"Project ID: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
print(f"Database ID: {os.getenv('FIRESTORE_DATABASE_ID')}")
print()

try:
    from src.services.chat_history_manager import chat_history_manager
    
    # Test 1: Create a conversation
    print("Test 1: Creating conversation...")
    user_id = "test_user_123"
    conversation_id = chat_history_manager.create_or_get_conversation(
        user_id=user_id,
        title="Test Conversation"
    )
    print(f"✓ Conversation created: {conversation_id}")
    
    # Test 2: Add a message
    print("\nTest 2: Adding message to conversation...")
    message_id = chat_history_manager.add_qa_to_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
        question="What is dharma?",
        answer="Dharma refers to one's duty and righteousness in the Bhagavad Gita.",
        sources=[],
        response_time_ms=500
    )
    print(f"✓ Message added: {message_id}")
    
    # Test 3: Retrieve conversation
    print("\nTest 3: Retrieving conversation history...")
    history = chat_history_manager.get_conversation_history(
        user_id=user_id,
        conversation_id=conversation_id
    )
    print(f"✓ Retrieved {history['total_messages']} message(s)")
    print(f"  Conversation ID: {history['conversation_id']}")
    print(f"  User ID: {history['user_id']}")
    
    # Test 4: Get user stats
    print("\nTest 4: Getting user statistics...")
    stats = chat_history_manager.get_user_stats(user_id)
    if stats:
        print(f"✓ User stats retrieved:")
        print(f"  Total conversations: {stats['total_conversations']}")
        print(f"  Total messages: {stats['total_messages']}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Chat history is working!")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Start your app: python app.py")
    print("2. Test with /ask endpoint")
    print("3. View conversations in Firestore console")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
