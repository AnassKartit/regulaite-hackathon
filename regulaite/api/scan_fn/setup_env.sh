#!/bin/bash
# Script to set up local development environment using azd outputs

# Make sure we're in the right directory
cd "$(dirname "$0")"

echo "Fetching environment variables from azd..."
eval "$(azd env get-values | sed 's/^/export /')"

# Create local.settings.json using environment variables
cat > local.settings.json << EOL
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_OPENAI_ENDPOINT": "${AZURE_OPENAI_ENDPOINT}",
    "AZURE_OPENAI_KEY": "${AZURE_OPENAI_KEY}",
    "AZURE_OPENAI_MODEL": "${AZURE_OPENAI_MODEL}",
    "AZURE_EMBED_MODEL": "${AZURE_EMBED_MODEL}",
    "AZURE_SEARCH_ENDPOINT": "${AZURE_SEARCH_ENDPOINT}",
    "AZURE_SEARCH_KEY": "${AZURE_SEARCH_KEY}",
    "AZURE_SEARCH_INDEX": "${AZURE_SEARCH_INDEX}",
    "STORAGE_ACC": "${STORAGE_ACC}"
  },
  "Host": {
    "CORS": "*"
  }
}
EOL

echo "Created local.settings.json with azd environment values"
echo "You can now run 'func start' to start the function app"