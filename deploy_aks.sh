#!/bin/bash

# Set variables
RESOURCE_GROUP_NAME="happymeter"
LOCATION="westeurope"
ACR_NAME="happyregistry"
AKS_NAME="happymeter"
BACKEND_NAME="happymeter-backend"
FRONTEND_NAME="happymeter-frontend"
TAG=1

#####################################################################################################

# Create resource group
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

# Read .env file into key-value pairs
if [ -f .env ]; then export $(grep -v '^#' .env | xargs); fi

#####################################################################################################

# Create an Azure Container Registry (ACR)
az acr create --resource-group $RESOURCE_GROUP_NAME --name $ACR_NAME --sku Basic

# Build and push container images to ACR
az acr build --registry $ACR_NAME --image $BACKEND_NAME:$TAG --file Dockerfile.backend .
az acr build --registry $ACR_NAME --image $FRONTEND_NAME:$TAG --file Dockerfile.frontend .

# Inject env variables into docker-compose.yml
sed -e "s/\${POSTGRES_HOST}/$POSTGRES_HOST/g" \
    -e "s/\${POSTGRES_USER}/$POSTGRES_USER/g" \
    -e "s/\${POSTGRES_PASSWORD}/$POSTGRES_PASSWORD/g" \
    -e "s/\${POSTGRES_DB}/$POSTGRES_DB/g" \
    -e "s/\${TAG}/$TAG/g" \
    docker-compose-azure.yml > docker-compose-aks.yml

# Convert docker-compose to k8s equivalent (CMD)
mkdir k8s; cd k8s
kompose convert -f ../docker-compose-aks.yml

# Install the Kubernetes CLI
az aks install-cli

# Create an AKS cluster
az aks create --resource-group $RESOURCE_GROUP_NAME --name $AKS_NAME \
    --location $LOCATION --node-count 2 --enable-app-routing \
    --generate-ssh-keys --attach-acr $ACR_NAME

# Connect to cluster using kubectl
az aks get-credentials --resource-group $RESOURCE_GROUP_NAME --name $AKS_NAME

# Ingress controller
# https://learn.microsoft.com/en-us/azure/aks/app-routing

# Change in all service YAML (enables external IPs)
# spec:
#   type: LoadBalancer
#   ports:
#     - port: XXXX
#       targetPort: XXXX

# Deploy application
kubectl create namespace happymeter
kubectl apply --filename . --namespace happymeter

# Enable / disable approuting
# az aks approuting enable --resource-group $RESOURCE_GROUP_NAME --name $AKS_NAME
# az aks approuting disable --resource-group $RESOURCE_GROUP_NAME --name $AKS_NAME

# k8s postgres endpoint: postgres.happymeter.svc.cluster.local

##################################################################################################

# Delete deployment
# kubectl delete --filename . --namespace happymeter

# Delete the resource group and all its associated resources
# az group delete --name $RESOURCE_GROUP_NAME --yes --no-wait