# Firestore Chat History & Admin Dashboard

Complete implementation of chat history storage and admin dashboard for the Bhagavad Gita Q&A application.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Admin Dashboard](#admin-dashboard)
- [Cost Optimization](#cost-optimization)
- [Testing](#testing)

---

## ✨ Features

### User Features
- ✅ Persistent chat history across sessions
- ✅ Conversation management (create, view, delete)
- ✅ Automatic metadata extraction (chapters, themes, characters)
- ✅ Context-aware responses using conversation history
- ✅ User statistics and insights

### Admin Features
- ✅ View all conversations across all users
- ✅ Search functionality across all chats
- ✅ Comprehensive analytics dashboard
- ✅ User management and GDPR compliance
- ✅ Data export capabilities
- ✅ Real-time system health monitoring

---

## 🏗️ Architecture

### Data Model

```
Firestore Structure:
├── prod_users/{user_id}
│   ├── profile (document)
│   │   ├── created_at
│   │   ├── last_active
│   │   ├── total_conversations
│   │   └── total_messages
│   │
│   └── conversations/{conversation_id}
│       ├── metadata (document)
│       │   ├── created_at
│       │   ├── updated_at
│       │   ├── message_count
│       │   ├── title
│       │   ├── topics: []
│       │   ├── chapters_referenced: []
│       │   └── characters_mentioned: []
│       │
│       └── messages/{message_id}
│           ├── timestamp
│           ├── user_query
│           ├── ai_response
│           ├── chapter_references: []
│           ├── themes: []
│           └── characters_mentioned: []
│
└── prod_analytics
    ├── global_stats
    └── daily_stats/{date}
```

### Components

1. **Firestore Service** (`src/services/firestore_service.py`)
   - Core database operations
   - CRUD for users, conversations, messages

2. **Chat History Manager** (`src/services/chat_history_manager.py`)
   - Business logic layer
   - Metadata extraction integration
   - Context formatting for RAG

3. **Metadata Extractor** (`src/services/metadata_extractor.py`)
   - Automatic extraction of chapters, verses, themes, characters
   - Conversation summarization

4. **Admin Service** (`src/services/admin_service.py`)
   - Admin operations
   - Cross-user queries
   - Data export

5. **Analytics Service** (`src/services/analytics_service.py`)
   - Statistics generation
   - Insights and trends

---

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `google-cloud-firestore>=2.14.0`
- `firebase-admin>=6.4.0`
- `pyjwt>=2.8.0`
- `passlib>=1.7.4`
- `python-jose[cryptography]>=3.3.0`
- `bcrypt>=4.0.1`
- `python-dateutil>=2.8.2`

### 2. Enable Firestore in GCP

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Navigate to Firestore
4. Click "Create Database"
5. Choose "Native mode"
6. Select your region (same as Cloud Run)

### 3. Configure Environment Variables

Generate admin credentials:
```bash
python scripts/generate_admin_key.py
```

Add to your `.env` file:
```bash
# Firestore Configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
FIRESTORE_DATABASE_ID=(default)
FIRESTORE_COLLECTION_PREFIX=prod

# Admin Authentication (from generate_admin_key.py output)
ADMIN_API_KEY=your-generated-api-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your-generated-hash

# Chat History Settings
MAX_CONVERSATION_HISTORY=50
CONVERSATION_CONTEXT_SIZE=10
AUTO_ARCHIVE_DAYS=90
SESSION_TIMEOUT_MINUTES=60

# Analytics
ENABLE_ANALYTICS=true
ANALYTICS_UPDATE_INTERVAL=3600
```

### 4. Initialize Firestore

```bash
python scripts/init_firestore.py
```

This will:
- Create analytics collections
- Set up initial statistics
- Optionally create test data

### 5. Test the Implementation

Start the server:
```bash
python app.py
```

Test the `/ask` endpoint with chat history:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is dharma?",
    "user_id": "user123",
    "save_to_history": true
  }'
```

---

## 📚 API Documentation

### User Endpoints

#### 1. Ask Question (with Chat History)
```http
POST /ask
Content-Type: application/json

{
  "question": "What is the main message of the Gita?",
  "user_id": "user123",
  "conversation_id": "optional-conversation-id",
  "save_to_history": true
}
```

Response:
```json
{
  "answer": "The main message...",
  "sources": [...],
  "conversation_id": "abc123",
  "message_id": "msg456",
  "user_id": "user123"
}
```

#### 2. Create Conversation
```http
POST /api/chat/conversations
Content-Type: application/json

{
  "user_id": "user123",
  "title": "My Gita Study"
}
```

#### 3. Get Conversation History
```http
GET /api/chat/conversations/{conversation_id}?user_id=user123&limit=50
```

#### 4. Get User's Conversations
```http
GET /api/chat/users/{user_id}/conversations?limit=50
```

#### 5. Delete Conversation
```http
DELETE /api/chat/conversations/{conversation_id}?user_id=user123
```

#### 6. Get User Statistics
```http
GET /api/chat/users/{user_id}/stats
```

### Admin Endpoints

All admin endpoints require the `X-Admin-Key` header:

```http
X-Admin-Key: your-admin-api-key
```

#### 1. Admin Login
```http
POST /api/admin/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your-password"
}
```

#### 2. Get All Conversations
```http
GET /api/admin/conversations?limit=100&offset=0&user_id=optional&start_date=2024-01-01
```

#### 3. Search Conversations
```http
POST /api/admin/search
Content-Type: application/json
X-Admin-Key: your-key

{
  "query": "dharma",
  "search_in": "both",
  "limit": 50
}
```

#### 4. Get Analytics
```http
GET /api/admin/analytics
X-Admin-Key: your-key
```

Response:
```json
{
  "total_users": 150,
  "total_conversations": 500,
  "total_messages": 2000,
  "messages_today": 50,
  "messages_this_week": 300,
  "active_users_today": 25,
  "top_questions": [...],
  "popular_chapters": [...],
  "popular_topics": [...]
}
```

#### 5. Get All Users
```http
GET /api/admin/users?limit=100&offset=0
X-Admin-Key: your-key
```

#### 6. Get User Details
```http
GET /api/admin/users/{user_id}
X-Admin-Key: your-key
```

#### 7. Delete User (GDPR)
```http
DELETE /api/admin/users/{user_id}
X-Admin-Key: your-key
```

#### 8. Export Conversation
```http
GET /api/admin/export/conversation/{user_id}/{conversation_id}?format=json
X-Admin-Key: your-key
```

#### 9. System Health
```http
GET /api/admin/health
X-Admin-Key: your-key
```

---

## 🎛️ Admin Dashboard

### Accessing the Dashboard

The admin dashboard provides a web interface for managing the system.

**Endpoints:**
- Analytics: `GET /api/admin/analytics`
- Search: `POST /api/admin/search`
- Users: `GET /api/admin/users`
- Conversations: `GET /api/admin/conversations`

### Key Metrics

1. **User Metrics**
   - Total users
   - Active users (today/week)
   - User growth trends

2. **Conversation Metrics**
   - Total conversations
   - Messages per day/week
   - Average response time

3. **Content Metrics**
   - Most asked questions
   - Popular chapters
   - Trending topics
   - Character mentions

### Admin Operations

1. **View All Conversations**
   - Filter by user, date, topic, chapter
   - Pagination support
   - Full conversation details

2. **Search Functionality**
   - Search in questions, answers, or both
   - Full-text search across all users
   - Export search results

3. **User Management**
   - View user profiles
   - User activity history
   - Delete user data (GDPR)

4. **Analytics**
   - Real-time statistics
   - Historical trends
   - Export reports

---

## 💰 Cost Optimization

### Firestore Free Tier
- **Storage**: 1GB
- **Reads**: 50K/day
- **Writes**: 20K/day
- **Deletes**: 20K/day

### Estimated Costs (1000 users)

**Monthly Usage:**
- Storage: ~2GB → $0.18/GB = **$0.36**
- Reads: ~100K/day → $0.06/100K = **$1.80**
- Writes: ~50K/day → $0.18/100K = **$2.70**

**Total: ~$5/month** for 1000 active users

### Optimization Strategies

1. **Pagination**
   ```python
   # Load messages in batches
   messages = get_messages(limit=20, offset=0)
   ```

2. **Caching**
   ```python
   # Cache recent conversations in memory
   # Reduce repeated Firestore reads
   ```

3. **Archiving**
   ```python
   # Move old conversations to Cloud Storage
   # Conversations older than 90 days
   ```

4. **Batch Operations**
   ```python
   # Group multiple writes together
   batch = db.batch()
   # ... add operations
   batch.commit()
   ```

5. **Selective Indexing**
   - Only index frequently queried fields
   - Avoid indexing large text fields

---

## 🧪 Testing

### Manual Testing

1. **Test Chat History**
   ```bash
   # Ask a question
   curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is karma?", "user_id": "test_user"}'
   
   # Get conversation history
   curl http://localhost:8000/api/chat/users/test_user/conversations
   ```

2. **Test Admin Access**
   ```bash
   # Get analytics
   curl http://localhost:8000/api/admin/analytics \
     -H "X-Admin-Key: your-admin-key"
   
   # Search conversations
   curl -X POST http://localhost:8000/api/admin/search \
     -H "Content-Type: application/json" \
     -H "X-Admin-Key: your-admin-key" \
     -d '{"query": "dharma", "search_in": "both"}'
   ```

### Automated Tests

Create test file `tests/test_chat_history.py`:

```python
import pytest
from src.services.chat_history_manager import chat_history_manager

def test_create_conversation():
    conv_id = chat_history_manager.create_or_get_conversation(
        user_id="test_user",
        title="Test Conversation"
    )
    assert conv_id is not None

def test_add_message():
    conv_id = chat_history_manager.create_or_get_conversation("test_user")
    msg_id = chat_history_manager.add_qa_to_conversation(
        user_id="test_user",
        conversation_id=conv_id,
        question="What is dharma?",
        answer="Dharma means duty and righteousness."
    )
    assert msg_id is not None
```

Run tests:
```bash
pytest tests/test_chat_history.py
```

---

## 🔒 Security

### Authentication
- Admin endpoints protected by API key
- User data isolated by user_id
- HTTPS required in production

### Data Privacy
- User conversations are private
- Admin access is logged
- GDPR compliance (delete user data)

### Best Practices
1. Store API keys in environment variables
2. Use HTTPS in production
3. Rotate admin credentials regularly
4. Monitor admin access logs
5. Implement rate limiting

---

## 📊 Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Admin health (Firestore status)
curl http://localhost:8000/api/admin/health \
  -H "X-Admin-Key: your-key"
```

### Logs
- Application logs: `app.log`
- Firestore operations logged with `logging` module
- Monitor Cloud Logging in GCP Console

---

## 🚀 Deployment

### Cloud Run Deployment

The chat history feature works seamlessly with your existing Cloud Run deployment:

1. **Build and Deploy**
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

2. **Firestore Permissions**
   - Cloud Run service account automatically has Firestore access
   - No additional configuration needed

3. **Environment Variables**
   - Set in Cloud Run console or via `gcloud`
   - Use Secret Manager for sensitive values

---

## 📝 Troubleshooting

### Common Issues

1. **"Firestore client not initialized"**
   - Check `GOOGLE_CLOUD_PROJECT` is set
   - Verify Firestore is enabled in GCP
   - Check service account permissions

2. **"Invalid admin credentials"**
   - Verify `ADMIN_API_KEY` in .env
   - Check `X-Admin-Key` header format
   - Regenerate credentials if needed

3. **"Chat history not saving"**
   - Check `CHAT_HISTORY_ENABLED` flag
   - Verify Firestore permissions
   - Check application logs

4. **Slow queries**
   - Add indexes in Firestore console
   - Reduce query limits
   - Implement caching

---

## 🎯 Next Steps

1. **Enable Firestore** in your GCP project
2. **Generate admin credentials** using the script
3. **Update .env file** with configuration
4. **Initialize Firestore** with the init script
5. **Test the implementation** locally
6. **Deploy to Cloud Run**
7. **Monitor usage** and optimize costs

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Firestore logs in GCP Console
3. Check application logs
4. Verify environment configuration

---

## 📄 License

This implementation is part of the Bhagavad Gita Q&A application.
