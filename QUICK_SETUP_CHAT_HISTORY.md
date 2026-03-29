# Quick Setup Guide: Chat History & Admin Dashboard

## 🚀 5-Minute Setup

### Step 1: Install Dependencies (1 min)
```bash
pip install google-cloud-firestore firebase-admin pyjwt passlib python-jose bcrypt python-dateutil
```

### Step 2: Enable Firestore (2 min)
1. Go to https://console.cloud.google.com
2. Select your project
3. Navigate to **Firestore Database**
4. Click **Create Database** → Choose **Native mode** → Select region
5. Click **Create**

### Step 3: Generate Admin Credentials (1 min)
```bash
python scripts/generate_admin_key.py
```

Copy the output and add to your `.env` file:
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
ADMIN_API_KEY=<generated-key>
ADMIN_PASSWORD_HASH=<generated-hash>
ADMIN_USERNAME=admin
FIRESTORE_COLLECTION_PREFIX=prod
```

### Step 4: Initialize Firestore (1 min)
```bash
python scripts/init_firestore.py
```

Type `y` when asked to create test data.

### Step 5: Test It! (30 sec)
```bash
# Start the server
python app.py

# In another terminal, test the chat history
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is dharma?",
    "user_id": "test_user",
    "save_to_history": true
  }'
```

You should see `conversation_id` and `message_id` in the response!

---

## 🎯 What You Get

### For Users:
- ✅ Chat history saved automatically
- ✅ Continue conversations across sessions
- ✅ View past conversations
- ✅ Delete conversations

### For Admins:
- ✅ View all user conversations
- ✅ Search across all chats
- ✅ Analytics dashboard
- ✅ User management
- ✅ Export data

---

## 📊 Test Admin Dashboard

```bash
# Get your admin API key from .env
export ADMIN_KEY="your-admin-api-key"

# Get analytics
curl http://localhost:8000/api/admin/analytics \
  -H "X-Admin-Key: $ADMIN_KEY"

# Search all conversations
curl -X POST http://localhost:8000/api/admin/search \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -d '{"query": "dharma", "search_in": "both", "limit": 10}'

# Get all users
curl http://localhost:8000/api/admin/users \
  -H "X-Admin-Key: $ADMIN_KEY"
```

---

## 🔧 Common Commands

### View User's Conversations
```bash
curl "http://localhost:8000/api/chat/users/test_user/conversations"
```

### Get Specific Conversation
```bash
curl "http://localhost:8000/api/chat/conversations/{conversation_id}?user_id=test_user"
```

### Delete Conversation
```bash
curl -X DELETE "http://localhost:8000/api/chat/conversations/{conversation_id}?user_id=test_user"
```

### Get User Stats
```bash
curl "http://localhost:8000/api/chat/users/test_user/stats"
```

---

## 💰 Cost Estimate

**Free Tier (Firestore):**
- 1GB storage
- 50K reads/day
- 20K writes/day

**For 1000 users:** ~$5/month

**For 100 users:** FREE (within free tier)

---

## 🚀 Deploy to Cloud Run

Your existing deployment process works as-is! Just:

1. Add environment variables to Cloud Run:
   ```bash
   gcloud run services update YOUR_SERVICE \
     --set-env-vars GOOGLE_CLOUD_PROJECT=your-project-id \
     --set-env-vars ADMIN_API_KEY=your-key \
     --set-env-vars ADMIN_PASSWORD_HASH=your-hash
   ```

2. Deploy:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

That's it! Chat history is now enabled in production.

---

## 📚 Full Documentation

See [CHAT_HISTORY_README.md](CHAT_HISTORY_README.md) for complete documentation.

---

## ❓ Troubleshooting

**Chat history not saving?**
- Check logs for errors
- Verify Firestore is enabled
- Check `GOOGLE_CLOUD_PROJECT` is set

**Admin endpoints not working?**
- Verify `X-Admin-Key` header
- Check admin credentials in .env
- Regenerate credentials if needed

**Firestore permission denied?**
- Check service account has Firestore access
- Verify project ID is correct
- Enable Firestore API in GCP Console

---

## 🎉 You're Done!

Your Bhagavad Gita Q&A app now has:
- ✅ Persistent chat history
- ✅ Admin dashboard
- ✅ Analytics
- ✅ User management
- ✅ GDPR compliance

Enjoy! 🙏
