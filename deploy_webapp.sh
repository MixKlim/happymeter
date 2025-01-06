#!/bin/bash

# Create a resource group named 'happymeter' in the 'westeurope' location
az group create --name happymeter --location westeurope

# Create an Azure Container Registry (ACR) named 'happyregistry' in the 'happymeter' resource group with 'Basic' SKU (Standard storage, etc.)
az acr create --resource-group happymeter --name happyregistry --sku Basic

# Build local docker images
docker compose build

# Log in to the Azure Container Registry (ACR) to interact with it (authenticate using Azure CLI credentials)
az acr login --name happyregistry

# Tag and push docker images to ACR
docker tag postgres:latest happyregistry.azurecr.io/postgres:latest
docker tag happymeter-backend:latest happyregistry.azurecr.io/happymeter-backend:latest
docker tag happymeter-frontend:latest happyregistry.azurecr.io/happymeter-frontend:latest

docker push happyregistry.azurecr.io/postgres:latest
docker push happyregistry.azurecr.io/happymeter-backend:latest
docker push happyregistry.azurecr.io/happymeter-frontend:latest

# Create an Azure App Service plan named 'happyplan' with the F1 (Free) pricing tier, specifying that it's a Linux-based plan
az appservice plan create --name happyplan --resource-group happymeter --sku F1 --is-linux

# Create a web app in the 'happymeter' resource group, using the 'happyplan' service plan.
# Enable the web app with a managed identity and HTTPS only
az webapp create --resource-group happymeter --plan happyplan --name happymeter --assign-identity --https-only true

# Get the subscription ID of the Azure subscription
subscription_id=$(az account list --query "[?name=='<SUBSCRIPTION_NAME>'].id" -o tsv)

# Retrieve the principal ID of the system-assigned identity for the web app 'happymeter' (stored in the variable)
principal_id=$(az webapp identity show --name happymeter --resource-group happymeter --query principalId -o tsv)

# Assign the 'AcrPull' role to the system-assigned identity of the web app, granting it pull access to the container registry 'happyregistry'
# The scope is limited to the specific registry resource under the subscription and resource group
az role assignment create \
  --assignee $principal_id \
  --role AcrPull \
  --scope subscriptions/$subscription_id/resourceGroups/happymeter/providers/Microsoft.ContainerRegistry/registries/happyregistry

# Configure environment variables or settings for the web app (commented out in your script)
az webapp config appsettings set --resource-group happymeter --name happymeter \
  --settings AZURE=True POSTGRES_USER=user POSTGRES_PASSWORD=password POSTGRES_DB=predictions REMOTE=True WEBSITES_PORT=8080

# Update the web app to use the Docker containers defined in 'docker-compose-azure.yml' for multi-container deployment
az webapp config container set --resource-group happymeter --name happymeter \
    --multicontainer-config-type compose --multicontainer-config-file docker-compose-azure.yml

# Open the web app in the default browser
# az webapp browse --resource-group happymeter --name happymeter

# Tail the logs from the 'happymeter' web app, displaying logs in real-time
# az webapp log tail --resource-group happymeter --name happymeter

# Delete web app without deleting App Service Plan
# az webapp delete --resource-group happymeter --name happymeter --keep-empty-plan

# Delete the 'happymeter' resource group and all its associated resources
# az group delete --name happymeter
