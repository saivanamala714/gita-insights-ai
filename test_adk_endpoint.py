#!/usr/bin/env python3
"""
Test script for the new /ask-agent endpoint
Tests both the regular /ask and the new /ask-agent endpoints
"""

import asyncio
import json
import time
import requests

# Test configuration
BASE_URL = "https://bhagavad-gita-api-669294246288.us-central1.run.app"
TEST_QUESTIONS = [
    "What is karma?",
    "Who is Arjuna?",
    "Explain dharma",
    "What is the purpose of life?"
]

async def test_endpoints():
    """Test both /ask and /ask-agent endpoints"""
    
    print("🚀 Testing Bhagavad Gita API Endpoints")
    print("=" * 50)
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n📝 Question {i}: {question}")
        print("-" * 40)
        
        # Test regular /ask endpoint
        print("\n🔹 Testing /ask endpoint:")
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/ask",
                json={"question": question, "user_id": "test_user"}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"⏱️  Response Time: {response_time:.2f}s")
                print(f"📄 Answer Length: {len(data.get('answer', ''))} chars")
                print(f"📚 Sources: {len(data.get('sources', []))}")
                print(f"💬 Preview: {data.get('answer', '')[:100]}...")
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test new /ask-agent endpoint
        print("\n🔹 Testing /ask-agent endpoint:")
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/ask-agent",
                json={"question": question, "user_id": "test_user"}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"⏱️  Response Time: {response_time:.2f}s")
                print(f"📄 Answer Length: {len(data.get('answer', ''))} chars")
                print(f"📚 Sources: {len(data.get('sources', []))}")
                print(f"🤖 Agent: {data.get('agent_name', 'unknown')}")
                print(f"🛠️  Tool Calls: {len(data.get('tool_calls', []))}")
                print(f"💬 Preview: {data.get('answer', '')[:100]}...")
                
                # Check if ADK is available
                if data.get('error') and 'ADK agent not available' in data.get('error', ''):
                    print("⚠️  ADK not installed - this is expected")
                elif data.get('error'):
                    print(f"⚠️  Agent Error: {data.get('error')}")
                    
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 50)

def test_health():
    """Test the health endpoint"""
    print("\n🏥 Testing Health Endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service Status: {data.get('status', 'unknown')}")
            print(f"🔧 Version: {data.get('version', 'unknown')}")
            print(f"📊 Dependencies: {list(data.get('dependencies', {}).keys())}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    print("🧪 Starting API Tests...")
    test_health()
    asyncio.run(test_endpoints())
    print("\n✨ Testing Complete!")
