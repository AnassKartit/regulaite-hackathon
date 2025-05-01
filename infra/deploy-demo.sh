#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="rg-regulaite"
LOCATION="swedencentral"

az group create -g "$RESOURCE_GROUP" -l "$LOCATION"

az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file demoAssets.bicep \
  --parameters location="$LOCATION" \
  --name demo-assets-deployment