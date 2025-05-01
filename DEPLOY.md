# Deployment Guide

## Deploy with Demo Assets

The project includes optional demo assets that can be deployed to showcase compliance scanning functionality. These assets are intentionally non-compliant Cognitive Services accounts that can be used for testing.

### Prerequisites

1. Install Azure CLI:
```bash
# macOS
brew install azure-cli

# Windows
winget install -e --id Microsoft.AzureCLI
```

2. Login to Azure:
```bash
az login
```

### Managing Demo Assets

The project includes a script to manage demo assets deployment:

```bash
cd infra

# Deploy demo assets
./demo-manager.sh deploy

# Remove demo assets
./demo-manager.sh remove
```

Demo assets include:
- cityCCTV (CognitiveServices) - Simulated public surveillance system
- loanAI (OpenAI) - Simulated credit scoring system
- prodTracker (CognitiveServices) - Simulated employee monitoring system

These assets are tagged with `demo=demo` and have intentionally non-compliant configurations for testing the compliance scanner.

### Deployment Alternatives

If you prefer using Azure Developer CLI (azd):

1. Deploy all infrastructure including demo assets:
```bash
azd up
```

2. Deploy without demo assets by using the alternate parameter file:
```bash
azd up --params-file infra/main.parameters.nodemo.json
```

### Clean Up

To remove only demo assets:
```bash
cd infra
./demo-manager.sh remove
```

To remove all resources:
```bash
azd down