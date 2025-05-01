#!/usr/bin/env bash
set -euo pipefail

# Get the resource group name and base name from parameters
RESOURCE_GROUP=${1:-"rg-regulaite"}
BASE_NAME=${2:-"regulaite"}
SUFFIX="hackathon"

# Build the React app
echo "Building React app..."
cd ../src/web
npm install
npm run build

# Upload to the Static Web App
echo "Uploading to Static Web App..."
az login
az staticwebapp upload \
  --name "${BASE_NAME}-web-${SUFFIX}" \
  --resource-group "${RESOURCE_GROUP}" \
  --distribution-dir "dist"

echo "Deployment complete! Your app is available at:"
az staticwebapp show \
  --name "${BASE_NAME}-web-${SUFFIX}" \
  --resource-group "${RESOURCE_GROUP}" \
  --query "defaultHostname" \
  --output tsv