#!/bin/bash
# Script to add Firestore chat history configuration to .env file

ENV_FILE=".env"

echo "Adding Firestore Chat History configuration to $ENV_FILE..."

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating new .env file..."
    touch "$ENV_FILE"
fi

# Add configuration
cat >> "$ENV_FILE" << 'EOF'

# ============================================
# Firestore Chat History Configuration
# ============================================

# Google Cloud Project (REPLACE WITH YOUR PROJECT ID)
GOOGLE_CLOUD_PROJECT=your-gcp-project-id

# Firestore Configuration
FIRESTORE_DATABASE_ID=(default)
FIRESTORE_COLLECTION_PREFIX=prod

# Admin Credentials (Generated)
ADMIN_API_KEY=clFWP1so0abPxUqOqQpygvbX7DgifnaCq7iMiDtOWdM
ADMIN_PASSWORD_HASH=b47760323043d06f48be5abcf8c6c9547f82b2e6dd0d0c31d1a6effb0ac7f675
ADMIN_USERNAME=admin

# Admin Password (for reference - remove after saving elsewhere):
# 79mjw-CKoJQsaysTdG_dgA

# Chat History Settings
MAX_CONVERSATION_HISTORY=50
CONVERSATION_CONTEXT_SIZE=10
AUTO_ARCHIVE_DAYS=90
SESSION_TIMEOUT_MINUTES=60

# Analytics
ENABLE_ANALYTICS=true
ANALYTICS_UPDATE_INTERVAL=3600

EOF

echo ""
echo "✅ Configuration added to $ENV_FILE"
echo ""
echo "⚠️  IMPORTANT: Edit .env and replace 'your-gcp-project-id' with your actual Google Cloud Project ID"
echo ""
echo "Your admin password is: 79mjw-CKoJQsaysTdG_dgA"
echo "Save this password somewhere safe!"
echo ""
