#!/bin/bash

# GCP Deployment Script for Airbnb Python API
# This script helps deploy the Docker container to a GCP VM

set -e

# Configuration
PROJECT_ID="your-gcp-project-id"
ZONE="us-central1-a"
VM_NAME="airbnb-python-api"
IMAGE_NAME="airbnb-python-api"
CONTAINER_NAME="airbnb-python-api"

echo "🚀 Starting GCP deployment..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Set GCP project
echo "📋 Setting GCP project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME:latest .

# Tag image for GCP Container Registry
echo "🏷️  Tagging image for GCP Container Registry..."
docker tag $IMAGE_NAME:latest gcr.io/$PROJECT_ID/$IMAGE_NAME:latest

# Push to GCP Container Registry
echo "📤 Pushing image to GCP Container Registry..."
gcloud auth configure-docker
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:latest

# Create VM if it doesn't exist
echo "🖥️  Checking if VM exists..."
if ! gcloud compute instances describe $VM_NAME --zone=$ZONE &> /dev/null; then
    echo "Creating new VM instance..."
    gcloud compute instances create $VM_NAME \
        --zone=$ZONE \
        --machine-type=e2-small \
        --image-family=cos-stable \
        --image-project=cos-cloud \
        --boot-disk-size=10GB \
        --tags=http-server,https-server
else
    echo "VM already exists, skipping creation..."
fi

# Allow HTTP traffic
echo "🔓 Configuring firewall rules..."
gcloud compute firewall-rules create allow-http-5000 \
    --allow tcp:5000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP traffic on port 5000" \
    --target-tags http-server 2>/dev/null || echo "Firewall rule may already exist"

# Deploy container to VM
echo "📦 Deploying container to VM..."
gcloud compute instances update-container $VM_NAME \
    --zone=$ZONE \
    --container-image=gcr.io/$PROJECT_ID/$IMAGE_NAME:latest \
    --container-env="MONGODB_URI=$MONGODB_URI,NEXTJS_API_URL=$NEXTJS_API_URL,PYTHON_API_URL=http://0.0.0.0:5000" \
    --container-restart-policy=always \
    --container-privileged

echo "✅ Deployment complete!"
echo "🌐 Your API should be available at: http://$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)'):5000"

