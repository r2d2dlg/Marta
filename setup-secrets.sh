#!/bin/bash

# This script sets up the necessary secrets in Google Secret Manager

# Enable the Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Function to create or update a secret
create_or_update_secret() {
  local secret_name=$1
  local secret_value=$2
  
  if gcloud secrets describe $secret_name --project=martamaria >/dev/null 2>&1; then
    echo "Updating secret $secret_name"
    echo -n "$secret_value" | gcloud secrets versions add $secret_name --data-file=-
  else
    echo "Creating secret $secret_name"
    echo -n "$secret_value" | gcloud secrets create $secret_name --data-file=-
  fi
}

# Read values from .env.local
# Note: This is just an example. You should replace these with your actual values
# or read them from your .env.local file
GOOGLE_CLIENT_ID="235918859899-h51umodmt3moovpcljvifpfgpj086q5l.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
NEXTAUTH_SECRET="o6wggHHYI5EyMlJrh31g_AkL4qyUB"
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
NEXTAUTH_URL="https://marta-webapp-235918859899.us-south1.run.app"

# Create/update secrets
create_or_update_secret "marta-google-client-id" "$GOOGLE_CLIENT_ID"
create_or_update_secret "marta-google-client-secret" "$GOOGLE_CLIENT_SECRET"
create_or_update_secret "marta-nextauth-secret" "$NEXTAUTH_SECRET"
create_or_update_secret "marta-google-api-key" "$GOOGLE_API_KEY"

# Grant the Cloud Build service account permission to access the secrets
PROJECT_NUMBER=$(gcloud projects describe martamaria --format='value(projectNumber)')

gcloud secrets add-iam-policy-binding marta-google-client-id \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding marta-google-client-secret \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding marta-nextauth-secret \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding marta-google-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "Secrets have been set up successfully!"
