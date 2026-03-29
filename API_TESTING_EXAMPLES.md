# API Testing Examples - Chat History & Admin Dashboard

Complete collection of API calls to test all chat history and admin features.

---

## 🔧 Setup

```bash
# Set your base URL
export BASE_URL="http://localhost:8000"

# Set your admin API key (from .env)
export ADMIN_KEY="your-admin-api-key"

# Set a test user ID
export USER_ID="test_user_$(date +%s)"
```

---

## 📝 User Endpoints

### 1. Ask Question with Chat History

```bash
# First question (creates new conversation)
curl -X POST $BASE_URL/ask \
  -H "Content-Type: application/json" \
  -d "{
    \"question\": \"What is dharma according to the Bhagavad Gita?\",
    \"user_id\": \"$USER_ID\",
    \"save_to_history\": true
  }" | jq

# Save the conversation_id from response
export CONV_ID="<paste-conversation-id>"

# Follow-up question (same conversation)
curl -X POST $BASE_URL/ask \
  -H "Content-Type: application/json" \
  -d "{
    \"question\": \"Can you explain more about karma yoga?\",
    \"user_id\": \"$USER_ID\",
    \"conversation_id\": \"$CONV_ID\",
    \"save_to_history\": true
  }" | jq
```

### 2. Create Conversation

```bash
curl -X POST $BASE_URL/api/chat/conversations \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"title\": \"My Gita Study Session\"
  }" | jq
```

### 3. Get Conversation History

```bash
curl "$BASE_URL/api/chat/conversations/$CONV_ID?user_id=$USER_ID&limit=50" | jq
```

### 4. Get User's Conversations

```bash
curl "$BASE_URL/api/chat/users/$USER_ID/conversations?limit=20" | jq
```

### 5. Get User Statistics

```bash
curl "$BASE_URL/api/chat/users/$USER_ID/stats" | jq
```

### 6. Delete Conversation

```bash
curl -X DELETE "$BASE_URL/api/chat/conversations/$CONV_ID?user_id=$USER_ID" | jq
```

---

## 🔐 Admin Endpoints

### 1. Admin Login

```bash
curl -X POST $BASE_URL/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-password"
  }' | jq
```

### 2. Get All Conversations

```bash
# All conversations
curl "$BASE_URL/api/admin/conversations?limit=100" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq

# Filter by user
curl "$BASE_URL/api/admin/conversations?user_id=$USER_ID" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq

# Filter by date range
curl "$BASE_URL/api/admin/conversations?start_date=2024-01-01&end_date=2024-12-31" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq

# Filter by topic
curl "$BASE_URL/api/admin/conversations?topic=dharma" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq

# Filter by chapter
curl "$BASE_URL/api/admin/conversations?chapter=2" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq
```

### 3. Get Conversation Details

```bash
curl "$BASE_URL/api/admin/conversations/$USER_ID/$CONV_ID" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq
```

### 4. Search Conversations

```bash
# Search in both questions and answers
curl -X POST $BASE_URL/api/admin/search \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -d '{
    "query": "dharma",
    "search_in": "both",
    "limit": 50
  }' | jq

# Search only in questions
curl -X POST $BASE_URL/api/admin/search \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -d '{
    "query": "karma",
    "search_in": "question",
    "limit": 20
  }' | jq

# Search only in answers
curl -X POST $BASE_URL/api/admin/search \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -d '{
    "query": "Krishna",
    "search_in": "answer",
    "limit": 30
  }' | jq
```

### 5. Get All Users

```bash
curl "$BASE_URL/api/admin/users?limit=100&offset=0" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq
```

### 6. Get User Details

```bash
curl "$BASE_URL/api/admin/users/$USER_ID" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq
```

### 7. Get Analytics

```bash
# System-wide analytics
curl "$BASE_URL/api/admin/analytics" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq

# User-specific analytics
curl "$BASE_URL/api/admin/analytics/user/$USER_ID" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq
```

### 8. System Health

```bash
curl "$BASE_URL/api/admin/health" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq
```

### 9. Update Statistics

```bash
# Update daily stats
curl -X POST "$BASE_URL/api/admin/analytics/update-daily" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq

# Update global stats
curl -X POST "$BASE_URL/api/admin/analytics/update-global" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq
```

### 10. Export Conversation

```bash
curl "$BASE_URL/api/admin/export/conversation/$USER_ID/$CONV_ID?format=json" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq
```

### 11. Delete User (GDPR)

```bash
curl -X DELETE "$BASE_URL/api/admin/users/$USER_ID" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq
```

---

## 🧪 Complete Test Workflow

Run this complete test to verify everything works:

```bash
#!/bin/bash

# Setup
export BASE_URL="http://localhost:8000"
export ADMIN_KEY="your-admin-api-key"
export USER_ID="test_user_$(date +%s)"

echo "Testing Chat History & Admin Dashboard"
echo "======================================="
echo "User ID: $USER_ID"
echo ""

# Test 1: Ask first question
echo "1. Asking first question..."
RESPONSE=$(curl -s -X POST $BASE_URL/ask \
  -H "Content-Type: application/json" \
  -d "{
    \"question\": \"What is dharma?\",
    \"user_id\": \"$USER_ID\",
    \"save_to_history\": true
  }")

CONV_ID=$(echo $RESPONSE | jq -r '.conversation_id')
echo "   ✓ Conversation created: $CONV_ID"

# Test 2: Ask follow-up question
echo "2. Asking follow-up question..."
curl -s -X POST $BASE_URL/ask \
  -H "Content-Type: application/json" \
  -d "{
    \"question\": \"What is karma yoga?\",
    \"user_id\": \"$USER_ID\",
    \"conversation_id\": \"$CONV_ID\",
    \"save_to_history\": true
  }" > /dev/null
echo "   ✓ Follow-up question saved"

# Test 3: Get conversation history
echo "3. Getting conversation history..."
MSG_COUNT=$(curl -s "$BASE_URL/api/chat/conversations/$CONV_ID?user_id=$USER_ID" | jq '.total_messages')
echo "   ✓ Messages in conversation: $MSG_COUNT"

# Test 4: Get user conversations
echo "4. Getting user conversations..."
CONV_COUNT=$(curl -s "$BASE_URL/api/chat/users/$USER_ID/conversations" | jq '.conversations | length')
echo "   ✓ Total conversations: $CONV_COUNT"

# Test 5: Get user stats
echo "5. Getting user stats..."
TOTAL_MSGS=$(curl -s "$BASE_URL/api/chat/users/$USER_ID/stats" | jq '.total_messages')
echo "   ✓ Total messages: $TOTAL_MSGS"

# Test 6: Admin - Get all conversations
echo "6. Admin: Getting all conversations..."
ADMIN_CONV_COUNT=$(curl -s "$BASE_URL/api/admin/conversations?limit=10" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq '.total')
echo "   ✓ Total conversations (admin view): $ADMIN_CONV_COUNT"

# Test 7: Admin - Search
echo "7. Admin: Searching conversations..."
SEARCH_RESULTS=$(curl -s -X POST $BASE_URL/api/admin/search \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -d '{"query": "dharma", "limit": 10}' | jq '.total')
echo "   ✓ Search results: $SEARCH_RESULTS"

# Test 8: Admin - Analytics
echo "8. Admin: Getting analytics..."
TOTAL_USERS=$(curl -s "$BASE_URL/api/admin/analytics" \
  -H "X-Admin-Key: $ADMIN_KEY" | jq '.total_users')
echo "   ✓ Total users in system: $TOTAL_USERS"

# Test 9: Delete conversation
echo "9. Deleting conversation..."
curl -s -X DELETE "$BASE_URL/api/chat/conversations/$CONV_ID?user_id=$USER_ID" > /dev/null
echo "   ✓ Conversation deleted"

echo ""
echo "======================================="
echo "All tests passed! ✓"
echo "======================================="
```

Save this as `test_chat_history.sh` and run:
```bash
chmod +x test_chat_history.sh
./test_chat_history.sh
```

---

## 📊 Expected Responses

### Successful Question with Chat History

```json
{
  "answer": "Dharma refers to one's duty, righteousness, and moral order...",
  "sources": [
    {
      "page_content": "...",
      "metadata": {
        "page": 42,
        "source": "11-Bhagavad-gita_As_It_Is.pdf"
      }
    }
  ],
  "conversation_id": "abc123xyz",
  "message_id": "msg456def",
  "user_id": "test_user"
}
```

### Analytics Response

```json
{
  "total_users": 150,
  "total_conversations": 500,
  "total_messages": 2000,
  "messages_today": 50,
  "messages_this_week": 300,
  "active_users_today": 25,
  "top_questions": [
    {
      "question": "What is dharma?",
      "count": 45,
      "chapters": [2, 3, 18],
      "themes": ["dharma", "duty"]
    }
  ],
  "popular_chapters": [
    {"chapter": 2, "count": 120},
    {"chapter": 3, "count": 95}
  ],
  "popular_topics": [
    {"topic": "dharma", "count": 200},
    {"topic": "karma", "count": 180}
  ],
  "avg_response_time_ms": 450.5
}
```

### Search Results

```json
{
  "query": "dharma",
  "results": [
    {
      "message_id": "msg123",
      "conversation_id": "conv456",
      "user_id": "user789",
      "timestamp": "2024-01-15T10:30:00Z",
      "user_query": "What is dharma?",
      "ai_response": "Dharma refers to...",
      "match_type": "question",
      "conversation_title": "Understanding Dharma"
    }
  ],
  "total": 15
}
```

---

## 🐛 Troubleshooting

### Error: "Invalid admin credentials"
```bash
# Check your admin key
echo $ADMIN_KEY

# Regenerate if needed
python scripts/generate_admin_key.py
```

### Error: "Conversation not found"
```bash
# Verify conversation exists
curl "$BASE_URL/api/chat/users/$USER_ID/conversations" | jq
```

### Error: "Firestore not initialized"
```bash
# Check environment variables
env | grep GOOGLE_CLOUD_PROJECT
env | grep FIRESTORE

# Initialize Firestore
python scripts/init_firestore.py
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- Pagination uses `limit` and `offset` parameters
- Admin endpoints require `X-Admin-Key` header
- User endpoints use `user_id` query parameter
- All responses are JSON format
- Use `| jq` for pretty-printed output

---

## 🎯 Quick Commands

```bash
# Create test user and conversation
export USER_ID="test_$(date +%s)"
curl -X POST $BASE_URL/ask -H "Content-Type: application/json" \
  -d "{\"question\":\"Test\",\"user_id\":\"$USER_ID\",\"save_to_history\":true}" | jq -r '.conversation_id'

# View all analytics
curl -s $BASE_URL/api/admin/analytics -H "X-Admin-Key: $ADMIN_KEY" | jq

# Search for specific term
curl -s -X POST $BASE_URL/api/admin/search \
  -H "Content-Type: application/json" -H "X-Admin-Key: $ADMIN_KEY" \
  -d '{"query":"YOUR_SEARCH_TERM"}' | jq

# Export all users
curl -s $BASE_URL/api/admin/users?limit=1000 -H "X-Admin-Key: $ADMIN_KEY" | jq > users_export.json
```

---

Happy testing! 🚀
