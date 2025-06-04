#!/bin/bash
set -e  # Exit on error

# This script sets up the necessary secrets in Google Secret Manager

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed. Please install Google Cloud SDK first."
    exit 1
fi

# Get the project ID from gcloud config
PROJECT_ID=$(gcloud config get-value project 2> /dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "Error: Could not determine Google Cloud project. Please run 'gcloud init' or 'gcloud config set project PROJECT_ID'"
    exit 1
fi

echo "Using Google Cloud project: $PROJECT_ID"

# Enable the Secret Manager API if not already enabled
echo "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

# Function to create or update a secret
create_or_update_secret() {
  local secret_name=$1
  local secret_value=$2
  
  if [ -z "$secret_value" ]; then
    echo "Error: No value provided for secret $secret_name"
    return 1
  fi
  
  if gcloud secrets describe $secret_name --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "Updating secret: $secret_name"
    echo -n "$secret_value" | gcloud secrets versions add $secret_name --data-file=-
  else
    echo "Creating secret: $secret_name"
    echo -n "$secret_value" | gcloud secrets create $secret_name --data-file=--project=$PROJECT_ID
  fi
}

# Read values from environment variables or prompt for them
echo "Setting up secrets for the application..."

# Prompt for secrets if not set in environment
if [ -z "$GOOGLE_CLIENT_ID" ]; then
    read -p "Enter Google OAuth Client ID: " GOOGLE_CLIENT_ID
fi

if [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    read -s -p "Enter Google OAuth Client Secret: " GOOGLE_CLIENT_SECRET
    echo ""  # New line after password prompt
fi

if [ -z "$NEXTAUTH_SECRET" ]; then
    # Generate a random secret if not provided
    NEXTAUTH_SECRET=$(openssl rand -base64 32)
    echo "Generated NEXTAUTH_SECRET"
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    read -p "Enter Google API Key: " GOOGLE_API_KEY
fi

# Set the NEXTAUTH_URL based on the project
NEXTAUTH_URL="https://marta-webapp-$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)').uc.run.app"

# Create/update secrets
create_or_update_secret "marta-google-client-id" "$GOOGLE_CLIENT_ID"
create_or_update_secret "marta-google-client-secret" "$GOOGLE_CLIENT_SECRET"
create_or_update_secret "marta-nextauth-secret" "$NEXTAUTH_SECRET"
create_or_update_secret "marta-google-api-key" "$GOOGLE_API_KEY"

# Get the project number for IAM bindings
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
if [ -z "$PROJECT_NUMBER" ]; then
    echo "Error: Could not determine project number for project $PROJECT_ID"
    exit 1
fi

# Grant the Cloud Build service account permission to access the secrets
echo "Configuring IAM permissions for Cloud Build service account..."

SECRETS=(
    "marta-google-client-id"
    "marta-google-client-secret"
    "marta-nextauth-secret"
    "marta-google-api-key"
)

for secret in "${SECRETS[@]}"; do
    echo "Granting access to $secret..."
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor" \
        --project=$PROJECT_ID
    
    # Also grant access to the Cloud Run service account
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor" \
        --project=$PROJECT_ID
done

echo "\nSecrets have been configured successfully!"
echo "NEXTAUTH_URL: $NEXTAUTH_URL"

gcloud secrets add-iam-policy-binding marta-google-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "Secrets have been set up successfully!"
