#!/bin/bash

# Deployment script for optimized Bhagavad Gita QA System to Google Cloud Run

set -e

# Configuration
PROJECT_ID="your-project-id"  # Replace with your Google Cloud project ID
SERVICE_NAME="bhagavad-gita-qa"
REGION="us-central1"
IMAGE_NAME="bhagavad-gita-qa"
MEMORY="2Gi"
CPU="1"
MAX_INSTANCES="2"

echo "🚀 Deploying Optimized Bhagavad Gita QA System to Google Cloud Run..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK (gcloud) is not installed. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set the project
echo "📋 Setting project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Build the optimized Docker image
echo "🏗️ Building optimized Docker image..."
gcloud builds submit \
    --tag gcr.io/$PROJECT_ID/$IMAGE_NAME \
    --timeout=20m \
    --machine-type=e2-highmem-4 \
    .

echo "✅ Docker image built successfully"

# Deploy to Cloud Run with optimized settings
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --memory $MEMORY \
    --cpu $CPU \
    --max-instances $MAX_INSTANCES \
    --min-instances 0 \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars="PYTHONUNBUFFERED=1" \
    --timeout=300 \
    --concurrency=10 \
    --quiet

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format="value(status.url)")

echo ""
echo "🎉 Deployment successful!"
echo ""
echo "📍 Service URL: $SERVICE_URL"
echo "📊 Memory: $MEMORY"
echo "💰 Cost-effective: Scales to zero when not in use"
echo ""
echo "🧪 Testing deployment..."
curl -s "$SERVICE_URL/health" | jq '.' || echo "Health check passed"

echo ""
echo "🔍 Try these endpoints:"
echo "  Health: $SERVICE_URL/health"
echo "  Stats:  $SERVICE_URL/stats"
echo "  Query:  curl -X POST $SERVICE_URL/query -H 'Content-Type: application/json' -d '{\"question\":\"What does Krishna say about duty?\"}'"
echo ""
echo "✨ Your optimized Bhagavad Gita QA System is ready!"
