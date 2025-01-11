#!/bin/bash

# Set variables
RESOURCE_GROUP_NAME="happymeter"
LOCATION="westeurope"
POSTGRES_DB_SERVER_NAME="happymeter"
ENVIRONMENT_NAME="happymeter"
LAW_NAME="happymeter"
ACR_NAME="happyregistry"
BACKEND_NAME="happymeter-backend"
FRONTEND_NAME="happymeter-frontend"
TAG=1

#####################################################################################################

# Create resource group
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

# Read .env file into key-value pairs
if [ -f .env ]; then export $(grep -v '^#' .env | xargs); fi

#####################################################################################################

# Create Postgres server + database
az postgres flexible-server create --resource-group $RESOURCE_GROUP_NAME --name $POSTGRES_DB_SERVER_NAME \
  --location $LOCATION --admin-user $POSTGRES_USER --admin-password $POSTGRES_PASSWORD --sku-name Standard_B1ms \
  --tier Burstable --storage-size 32 --version 16 --public-access 0.0.0.0 \
  --database-name $POSTGRES_DB --create-default-database Disabled

# Get Postgres server URL
POSTGRES_DB_SERVER_URL=$(az postgres flexible-server show --resource-group $RESOURCE_GROUP_NAME \
  --name $POSTGRES_DB_SERVER_NAME --query "fullyQualifiedDomainName" --output tsv)

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

# Create base container app for backend
az containerapp create --name $BACKEND_NAME --resource-group $RESOURCE_GROUP_NAME \
    --environment $ENVIRONMENT_NAME --secrets "postgres-password=$POSTGRES_PASSWORD"

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
    --registry-password $ACR_PASSWORD --ingress external \
    --env-vars "POSTGRES_USER=$POSTGRES_USER" "POSTGRES_PASSWORD=secretref:postgres-password" \
    "POSTGRES_HOST=$POSTGRES_DB_SERVER_URL" "POSTGRES_DB=$POSTGRES_DB"

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
