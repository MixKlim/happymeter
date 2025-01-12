#!/bin/bash

# Set variables
SUBSCRIPTION_NAME="<>"
RESOURCE_GROUP_NAME="happymeter"
LOCATION="westeurope"
ACR_NAME="happyregistry"
APP_PLAN_NAME="happyplan"
APP_NAME="happymeter"
TAG=1

#####################################################################################################

# Create resource group
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

# Read .env file into key-value pairs
if [ -f .env ]; then export $(grep -v '^#' .env | xargs); fi

#####################################################################################################

# Create an Azure Container Registry (ACR)
az acr create --resource-group $RESOURCE_GROUP_NAME --name $ACR_NAME --sku Basic

# Build local docker images
docker compose build

# Log in to the Azure Container Registry (ACR) to interact with it (authenticate using Azure CLI credentials)
az acr login --name $ACR_NAME

# Tag and push docker images to ACR
docker tag postgres:$TAG happyregistry.azurecr.io/postgres:$TAG
docker tag happymeter-backend:$TAG happyregistry.azurecr.io/happymeter-backend:$TAG
docker tag happymeter-frontend:$TAG happyregistry.azurecr.io/happymeter-frontend:$TAG

docker push happyregistry.azurecr.io/postgres:$TAG
docker push happyregistry.azurecr.io/happymeter-backend:$TAG
docker push happyregistry.azurecr.io/happymeter-frontend:$TAG

# Create an Azure App Service plan with the F1 (Free) pricing tier, specifying that it's a Linux-based plan
az appservice plan create --name $APP_PLAN_NAME --resource-group $RESOURCE_GROUP_NAME --sku F1 --is-linux

# Create a web app
# Enable the web app with a managed identity and HTTPS only
az webapp create --resource-group $RESOURCE_GROUP_NAME --plan $APP_PLAN_NAME --name $APP_NAME \
  --assign-identity --https-only true

# Get the subscription ID of the Azure subscription
SUBSCRIPTION_ID=$(az account list --query "[?name=='$SUBSCRIPTION_NAME'].id" -o tsv)

# Retrieve the principal ID of the system-assigned identity for the web app
APP_PRINCIPAL_ID=$(az webapp identity show --name $APP_NAME --resource-group $RESOURCE_GROUP_NAME --query principalId -o tsv)

# Assign the 'AcrPull' role to the system-assigned identity of the web app, granting it pull access to ACR
az role assignment create \
  --assignee $APP_PRINCIPAL_ID \
  --role AcrPull \
  --scope subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP_NAME/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME

# Configure environment variables or settings for the web app
az webapp config appsettings set --resource-group $RESOURCE_GROUP_NAME --name $APP_NAME \
  --settings POSTGRES_HOST=$POSTGRES_HOST POSTGRES_USER=$POSTGRES_USER POSTGRES_PASSWORD=$POSTGRES_PASSWORD POSTGRES_DB=$POSTGRES_DB

# Update the web app to use the Docker containers defined in 'docker-compose-azure.yml' for multi-container deployment
az webapp config container set --resource-group $RESOURCE_GROUP_NAME --name $APP_NAME \
    --multicontainer-config-type compose --multicontainer-config-file docker-compose-azure.yml

# Open the web app in the default browser
# az webapp browse --resource-group $RESOURCE_GROUP_NAME --name $APP_NAME

# Tail the logs from the web app, displaying logs in real-time
# az webapp log tail --resource-group $RESOURCE_GROUP_NAME --name $APP_NAME

# Delete web app without deleting App Service Plan
# az webapp delete --resource-group $RESOURCE_GROUP_NAME --name $APP_NAME --keep-empty-plan

##################################################################################################

# Delete the resource group and all its associated resources
# az group delete --name $RESOURCE_GROUP_NAME --yes --no-wait
