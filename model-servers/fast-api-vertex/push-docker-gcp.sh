#!/bin/bash

# gcloud auth login
# gcloud auth configure-docker
# gcloud config set project YOUR_PROJECT_ID
# gcloud services enable artifactregistry.googleapis.com aiplatform.googleapis.com

# === CONFIGURABLE VARIABLES ===
PROJECT_ID="your-project-id"  # Replace with your Google Cloud project ID
REGION="us-central1"  # Change if deploying to a different region
REPO_NAME="vertex-repo"  # Artifact Registry repository name
IMAGE_NAME="fastapi-app-vertex"
TAG="latest"

# === BUILD & TAG DOCKER IMAGE ===
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:${TAG} .

# Authenticate Docker to Google Cloud
#echo "Authenticating with Google Cloud..."
#gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Tag image for Artifact Registry (recommended)
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG}"
echo "Tagging image as: ${IMAGE_URI}"
docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_URI}

# Push image to Artifact Registry
echo "Pushing image to Google Cloud Artifact Registry..."
docker push ${IMAGE_URI}

# Deploy model to Vertex AI
echo "Creating Vertex AI Model..."
gcloud ai models upload \
  --region=${REGION} \
  --display-name=${IMAGE_NAME} \
  --container-image-uri=${IMAGE_URI}

echo "Docker image uploaded and model registered in Vertex AI!"

# Create the endpoint
gcloud ai endpoints create \
  --region=us-central1 \
  --display-name=fastapi-endpoint

# Get endpoint ID after creation
ENDPOINT_ID=$(gcloud ai endpoints list --region=us-central1 --filter="displayName=fastapi-endpoint" --format="value(name)")

# Deploy model to endpoint
gcloud ai endpoints deploy-model $ENDPOINT_ID \
  --model=${MODEL_ID} \
  --region=us-central1 \
  --machine-type=n1-standard-4 \
  --display-name=fastapi-deployment
