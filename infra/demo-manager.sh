#!/bin/bash
# Manage demo assets deployment and removal

# Set variables
RESOURCE_GROUP="rg-regulaite"
LOCATION="swedencentral"

# Function to show usage
show_usage() {
    echo "Usage: $0 [deploy|remove]"
    echo ""
    echo "Commands:"
    echo "  deploy    Deploy demo assets"
    echo "  remove    Remove demo assets"
    exit 1
}

# Function to deploy demo assets
deploy_demo() {
    echo "🚀 Deploying demo assets..."
    
    az deployment group create \
        --resource-group $RESOURCE_GROUP \
        --template-file demoAssets.bicep \
        --parameters location=$LOCATION \
        --name demo-assets-deployment

    if [ $? -eq 0 ]; then
        echo "✅ Demo assets deployed successfully!"
        
        # List deployed resources
        echo "📋 Deployed resources:"
        az resource list --resource-group $RESOURCE_GROUP --query "[?tags.demo=='demo'].{Name:name, Type:type}" -o table
    else
        echo "❌ Failed to deploy demo assets"
        exit 1
    fi
}

# Function to remove demo assets
remove_demo() {
    echo "🗑️  Removing demo assets..."
    
    # List resources with demo tag before deletion
    echo "📋 Resources to be removed:"
    az resource list --resource-group $RESOURCE_GROUP --query "[?tags.demo=='demo'].{Name:name, Type:type}" -o table
    
    # Delete resources with demo tag
    echo "🔄 Deleting resources..."
    az resource list --resource-group $RESOURCE_GROUP --query "[?tags.demo=='demo'].[id]" -o tsv | while read -r id; do
        echo "   Deleting: $id"
        az resource delete --ids "$id"
    done
    
    if [ $? -eq 0 ]; then
        echo "✅ Demo assets removed successfully!"
    else
        echo "❌ Failed to remove some demo assets"
        exit 1
    fi
}

# Check command line arguments
if [ $# -ne 1 ]; then
    show_usage
fi

# Process command
case "$1" in
    "deploy")
        deploy_demo
        ;;
    "remove")
        remove_demo
        ;;
    *)
        show_usage
        ;;
esac