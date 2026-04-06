#!/bin/bash
set -euo pipefail

# ============================================================
# Cloud Build Setup Script
# Run this once to prepare your GCP project for CI/CD.
# ============================================================

# === CONFIGURABLE VARIABLES (edit these) ===
PROJECT_ID="your-project-id"
REGION="us-central1"
REPO_NAME="vertex-repo"
GITHUB_OWNER="your-github-username"
GITHUB_REPO="your-repo-name"

# ============================================================
# Step 1: Enable required GCP APIs
# ============================================================
echo "==> Enabling GCP APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    run.googleapis.com \
    --project="$PROJECT_ID"

# ============================================================
# Step 2: Create Artifact Registry Docker repository
# ============================================================
echo "==> Creating Artifact Registry repository '${REPO_NAME}'..."
gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --project="$PROJECT_ID" \
    --description="Docker images for Vertex AI / Cloud Run" \
    2>/dev/null || echo "    (repository already exists, skipping)"

# ============================================================
# Step 3: Create a dedicated service account for Cloud Build
# ============================================================
CB_SA_NAME="cloud-build-deployer"
CB_SA_EMAIL="${CB_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "==> Creating service account '${CB_SA_NAME}'..."
gcloud iam service-accounts create "$CB_SA_NAME" \
    --display-name="Cloud Build CI/CD Service Account" \
    --project="$PROJECT_ID" \
    2>/dev/null || echo "    (service account already exists, skipping)"

echo "==> Granting roles to ${CB_SA_EMAIL}..."

ROLES=(
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
    "roles/artifactregistry.writer"
    "roles/logging.logWriter"
)

for ROLE in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${CB_SA_EMAIL}" \
        --role="$ROLE" \
        --quiet
done

# ============================================================
# Step 4: Connect GitHub repository (manual step)
# ============================================================
echo ""
echo "============================================================"
echo " MANUAL STEP: Connect your GitHub repository to Cloud Build"
echo "============================================================"
echo ""
echo " 1. Go to: https://console.cloud.google.com/cloud-build/triggers;region=${REGION}?project=${PROJECT_ID}"
echo " 2. Click 'CONNECT REPOSITORY' (2nd gen)"
echo " 3. Select GitHub and authenticate"
echo " 4. Choose repository: ${GITHUB_OWNER}/${GITHUB_REPO}"
echo " 5. Complete the connection"
echo ""
read -p "Press Enter once the repository is connected..."

# ============================================================
# Step 5: Create CI trigger (Pull Requests)
# ============================================================
echo "==> Creating CI trigger (Pull Requests → lint + build)..."
gcloud builds triggers create github \
    --name="ci-lint-and-build" \
    --repo-name="$GITHUB_REPO" \
    --repo-owner="$GITHUB_OWNER" \
    --pull-request-pattern="^main$" \
    --build-config="model-servers/fast-api-vertex-cloud-build-SOLUTION/cloudbuild-ci.yaml" \
    --included-files="model-servers/fast-api-vertex-cloud-build-SOLUTION/**" \
    --service-account="projects/${PROJECT_ID}/serviceAccounts/${CB_SA_EMAIL}" \
    --region="$REGION" \
    --project="$PROJECT_ID"

# ============================================================
# Step 6: Create CD trigger (Push to main)
# ============================================================
echo "==> Creating CD trigger (Push to main → build + push + deploy)..."
gcloud builds triggers create github \
    --name="cd-build-and-deploy" \
    --repo-name="$GITHUB_REPO" \
    --repo-owner="$GITHUB_OWNER" \
    --branch-pattern="^main$" \
    --build-config="model-servers/fast-api-vertex-cloud-build-SOLUTION/cloudbuild-cd.yaml" \
    --included-files="model-servers/fast-api-vertex-cloud-build-SOLUTION/**" \
    --service-account="projects/${PROJECT_ID}/serviceAccounts/${CB_SA_EMAIL}" \
    --region="$REGION" \
    --project="$PROJECT_ID"

echo ""
echo "==> Setup complete!"
echo "    CI trigger: runs on Pull Requests to main (lint + build)"
echo "    CD trigger: runs on Push to main (build + push + deploy)"
echo ""
echo "    Artifact Registry: ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}"
echo "    Cloud Run service will be created on first deploy."
