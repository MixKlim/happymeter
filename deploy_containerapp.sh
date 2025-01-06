#!/bin/bash

# Create a resource group named 'happymeter' in the 'westeurope' location
az group create --name happymeter --location westeurope

# Create an Azure Container Registry (ACR) named 'happyregistry' in the 'happymeter' resource group with 'Basic' SKU and admin user enabled
az acr create --resource-group happymeter --name happyregistry --sku Basic --admin-enabled true

# Obtain password from ACR
acr_password=$(az acr credential show --name happyregistry --query "passwords[0].value" -o tsv)

# Log in to the Azure Container Registry (ACR) to interact with it (authenticate using Azure CLI credentials)
az acr login --name happyregistry

# Tag and push docker images to ACR
TAG=1

docker build -t happymeter-backend:$TAG -f Dockerfile.backend .
docker build -t happymeter-frontend:$TAG -f Dockerfile.frontend .
docker build -t happymeter-database:$TAG -f Dockerfile.database .

docker tag happymeter-backend:$TAG happyregistry.azurecr.io/happymeter-backend:$TAG
docker tag happymeter-frontend:$TAG happyregistry.azurecr.io/happymeter-frontend:$TAG
docker tag postgres:$TAG happyregistry.azurecr.io/postgres:$TAG

docker push happyregistry.azurecr.io/happymeter-backend:$TAG
docker push happyregistry.azurecr.io/happymeter-frontend:$TAG
docker push happyregistry.azurecr.io/postgres:$TAG

# Create Log Analytics Workspace
az monitor log-analytics workspace create --resource-group happymeter \
  --workspace-name happymeter --location westeurope

# Get LAW ID
law_id=$(az monitor log-analytics workspace show --resource-group happymeter \
  --workspace-name happymeter --query "customerId" -o tsv)

# Get LAW Primary Key
law_primary_key=$(az monitor log-analytics workspace get-shared-keys \
  --resource-group happymeter --workspace-name happymeter \
  --query "primarySharedKey" -o tsv)

# Create a Container Apps environment
az containerapp env create --name happymeter --resource-group happymeter \
  --logs-workspace-id $law_id --logs-workspace-key $law_primary_key \
  --location westeurope

# Create base container app for backend
az containerapp create --name happymeter-backend --resource-group happymeter \
    --environment happymeter --ingress external --system-assigned --allow-insecure true

# Get the subscription ID of the Azure subscription
subscription_id=$(az account list --query "[?name=='KM'].id" -o tsv)

# Retrieve the principal ID of the system-assigned identity for the container app 'happymeter'
principal_id=$(az containerapp identity show --name happymeter-backend --resource-group happymeter --query principalId -o tsv)

# Assign the 'AcrPull' role to the system-assigned identity of the web app, granting it pull access to the container registry 'happyregistry'
# The scope is limited to the specific registry resource under the subscription and resource group
az role assignment create \
  --assignee $principal_id \
  --role AcrPull \
  --scope subscriptions/$subscription_id/resourceGroups/happymeter/providers/Microsoft.ContainerRegistry/registries/happyregistry

# Deploy docker image to container app
az containerapp up --name happymeter-backend --resource-group happymeter \
    --environment happymeter --image happyregistry.azurecr.io/happymeter-backend:$TAG \
    --target-port 8080 --registry-server happyregistry.azurecr.io --registry-username happyregistry \
    --registry-password $acr_password

##################################################################################################

# Add Azure Files volume mount in Azure Container Apps

# Create an Azure Storage account
az storage account create --resource-group happymeter --name happyst --location westeurope \
  --kind StorageV2 --sku Standard_LRS --enable-large-file-share

# Create the Azure Storage file share
az storage share-rm create --resource-group happymeter --storage-account happyst --name happyshare \
  --quota 1024 --enabled-protocols SMB

# Get the storage account key
STORAGE_ACCOUNT_KEY=$(az storage account keys list --resource-group happymeter --account-name happyst --query [0].value --output tsv)

# Create the storage mount
az containerapp env storage set --access-mode ReadWrite --azure-file-account-name happyst \
  --azure-file-account-key $STORAGE_ACCOUNT_KEY --azure-file-share-name happyshare \
  --storage-name happymount --name happymeter --resource-group happymeter

# Export the container app's configuration
az containerapp show --name happymeter-backend --resource-group happymeter --output yaml > containerapp.yaml

# Update the container app with the new storage mount configuration
az containerapp update --name happymeter-backend --resource-group happymeter --yaml containerapp.yaml

# Open an interactive shell inside the container app
az containerapp exec --name happymeter-backend --resource-group happymeter

# Get the URL of the container app
az containerapp show --name happymeter-backend --resource-group happymeter \
  --query "properties.configuration.ingress.fqdn" -o tsv

# Delete the 'happymeter' resource group and all its associated resources
az group delete --name happymeter --yes
