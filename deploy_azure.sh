#!/bin/bash

# Set variables
RESOURCE_GROUP_NAME="happymeter"
LOCATION="westeurope"
ENVIRONMENT_NAME="happymeter"
LAW_NAME="happymeter"
ACR_NAME="happyregistry"
BACKEND_NAME="happymeter-backend"
FRONTEND_NAME="happymeter-frontend"
STORAGE_ACCOUNT_NAME="happymeterdb$(date +%s | tail -c 6)"
STORAGE_SHARE_NAME="duckdb-data"
TAG=1

#####################################################################################################

# Create resource group
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

#####################################################################################################

# Create an Azure Container Registry (ACR)
az acr create --resource-group $RESOURCE_GROUP_NAME --name $ACR_NAME --sku Basic --admin-enabled true

# Obtain password from ACR
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Create Log Analytics Workspace
az monitor log-analytics workspace create --resource-group $RESOURCE_GROUP_NAME \
  --workspace-name $LAW_NAME --location $LOCATION

# Get LAW ID
LAW_ID=$(az monitor log-analytics workspace show --resource-group $RESOURCE_GROUP_NAME \
  --workspace-name $LAW_NAME --query "customerId" -o tsv)

# Get LAW Primary Key
LAW_PRIMARY_KEY=$(az monitor log-analytics workspace get-shared-keys \
  --resource-group $RESOURCE_GROUP_NAME --workspace-name $LAW_NAME \
  --query "primarySharedKey" -o tsv)

# Create a Container Apps environment
az containerapp env create --name $ENVIRONMENT_NAME --resource-group $RESOURCE_GROUP_NAME \
  --logs-workspace-id $LAW_ID --logs-workspace-key $LAW_PRIMARY_KEY --location $LOCATION

##################################################################################################

# Create base container app for backend with persistent storage for DuckDB
az containerapp create --name $BACKEND_NAME --resource-group $RESOURCE_GROUP_NAME \
    --environment $ENVIRONMENT_NAME \
    --storage-mounts duckdb-volume=/app/database \
    --storage-type AzureFile \
    --storage-account-name $STORAGE_ACCOUNT_NAME \
    --storage-account-key "$STORAGE_ACCOUNT_KEY" \
    --storage-share-name $STORAGE_SHAREersistent data storage
echo "Creating Storage Account for DuckDB persistence..."
az storage account create --resource-group $RESOURCE_GROUP_NAME --name $STORAGE_ACCOUNT_NAME \
  --location $LOCATION --sku Standard_LRS --kind StorageV2

# Get storage account connection string
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --resource-group $RESOURCE_GROUP_NAME --name $STORAGE_ACCOUNT_NAME --query connectionString -o tsv)

# Get storage account key
STORAGE_ACCOUNT_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP_NAME \
  --name $STORAGE_ACCOUNT_NAME --query "[0].value" -o tsv)

# Create file share for DuckDB data
az storage share create --name $STORAGE_SHARE_NAME --account-name $STORAGE_ACCOUNT_NAME \
  --account-key $STORAGE_ACCOUNT_KEY --quota 1

#####################################################################################################
az containerapp create --name $BACKEND_NAME --resource-group $RESOURCE_GROUP_NAME \
    --environment $ENVIRONMENT_NAME

# Log in to the ACR to interact with it (authenticate using Azure CLI credentials)
az acr login --name $ACR_NAME

# Tag and push backend docker image to ACR
# docker build -t $BACKEND_NAME:$TAG -f Dockerfile.backend .
# docker tag $BACKEND_NAME:$TAG happyregistry.azurecr.io/happymeter-backend:$TAG
# docker push happyregistry.azurecr.io/happymeter-backend:$TAG
az acr build --image $BACKEND_NAME:$TAG --registry $ACR_NAME --file Dockerfile.backend .

# Deploy docker image to backend container app
az containerapp up --name $BACKEND_NAME --resource-group $RESOURCE_GROUP_NAME \
    --environment $ENVIRONMENT_NAME --image $ACR_NAME.azurecr.io/$BACKEND_NAME:$TAG \
    --target-port 8080 --registry-server $ACR_NAME.azurecr.io --registry-username $ACR_NAME \
    --registry-password $ACR_PASSWORD --ingress external

# Get the URL of the backend container app
BACKEND_HOST=$(az containerapp show --name $BACKEND_NAME --resource-group $RESOURCE_GROUP_NAME \
  --query "properties.configuration.ingress.fqdn" -o tsv)

##################################################################################################

# Create base container app for frontend
az containerapp create --name $FRONTEND_NAME --resource-group $RESOURCE_GROUP_NAME \
    --environment $ENVIRONMENT_NAME --system-assigned

# Tag and push docker images to ACR
# docker build -t happymeter-frontend:$TAG -f Dockerfile.frontend .
# docker tag happymeter-frontend:$TAG happyregistry.azurecr.io/happymeter-frontend:$TAG
# docker push happyregistry.azurecr.io/happymeter-frontend:$TAG
az acr build --image $FRONTEND_NAME:$TAG --registry $ACR_NAME --file Dockerfile.frontend .

# Deploy docker image to frontend container app
az containerapp up --name $FRONTEND_NAME --resource-group $RESOURCE_GROUP_NAME \
    --environment $ENVIRONMENT_NAME --image $ACR_NAME.azurecr.io/$FRONTEND_NAME:$TAG \
    --target-port 8501 --registry-server $ACR_NAME.azurecr.io --registry-username $ACR_NAME \
    --registry-password $ACR_PASSWORD --ingress external --env-vars "BACKEND_HOST=$BACKEND_HOST"

##################################################################################################

# Delete the resource group and all its associated resources
# az group delete --name $RESOURCE_GROUP_NAME --yes --no-wait
