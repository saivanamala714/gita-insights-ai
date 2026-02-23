#!/bin/bash
# Update Firestore database ID in .env file

ENV_FILE=".env"

echo "Updating Firestore database ID in $ENV_FILE..."

# Check if the line exists and update it, or add it if it doesn't exist
if grep -q "^FIRESTORE_DATABASE_ID=" "$ENV_FILE"; then
    # Update existing line
    sed -i '' 's/^FIRESTORE_DATABASE_ID=.*/FIRESTORE_DATABASE_ID=bg-ai-chat-history/' "$ENV_FILE"
    echo "✓ Updated FIRESTORE_DATABASE_ID to bg-ai-chat-history"
else
    # Add new line after GOOGLE_CLOUD_PROJECT
    sed -i '' '/^GOOGLE_CLOUD_PROJECT=/a\
FIRESTORE_DATABASE_ID=bg-ai-chat-history
' "$ENV_FILE"
    echo "✓ Added FIRESTORE_DATABASE_ID=bg-ai-chat-history"
fi

echo ""
echo "✓ Configuration updated!"
echo ""
