# RAG applications

This repository contains 4 notebooks showcasing various aspects of building RAG application.

* 01-rag_app.ipynb
    * This is a basic RAG application 
* 02-dive_deep.ipynb
    * Dive deep on tokens, tokenizers, embeddings, and vector stores
* 03-multimodal_rag.ipynb
    * A more advanced RAG application using vision
* 04-advanced_rag.ipynb
    * RAG application incorporating techniques like hybrid search and reranking

Some of the examples assume you have access to OpenAI with an API key.

The vector database used for all examples is Qdrant running locally in Docker. You can start Qrant by running 
``` bash
docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    qdrant/qdrant:v1.13.4
```

The basic RAG application is also using DeepSeek in the r1:1.5b version. For this I use
Ollama running locally. Pull the model using
``` bash
ollama pull deepseek-r1:1.5b
```
and start it with
``` bash
ollama run deepseek-r1:1.5b
```

Have fun!

az login


## Change these four parameters as needed
ACI_PERS_RESOURCE_GROUP=sparse-embedding-rg
ACI_PERS_STORAGE_ACCOUNT_NAME=vecdbstorageaccount$RANDOM
ACI_PERS_STORAGE_ACCOUNT_NAME=vecdbstorageaccount15014
ACI_PERS_LOCATION=swedencentral
ACI_PERS_SHARE_NAME=acishare
ACI_RESOURCE_GROUP=sparse-embedding-rg


az group create \
    --name $ACI_RESOURCE_GROUP \
    --location $ACI_PERS_LOCATION


# Create the storage account with the parameters
az storage account create \
    --resource-group $ACI_PERS_RESOURCE_GROUP \
    --name $ACI_PERS_STORAGE_ACCOUNT_NAME \
    --location $ACI_PERS_LOCATION \
    --sku Standard_LRS

# Create the file share
az storage share create \
  --name $ACI_PERS_SHARE_NAME \
  --account-name $ACI_PERS_STORAGE_ACCOUNT_NAME

Get storage credentials
STORAGE_KEY=$(az storage account keys list --resource-group $ACI_PERS_RESOURCE_GROUP --account-name $ACI_PERS_STORAGE_ACCOUNT_NAME --query "[0].value" --output tsv)

echo $STORAGE_KEY


az container create --resource-group $ACI_RESOURCE_GROUP --file deploy-aci.yaml


http://myfastapi-qdrant-demo.swedencentral.azurecontainer.io


az monitor log-analytics workspace create --resource-group $ACI_PERS_RESOURCE_GROUP \
       --workspace-name embeddingworkspace

az container attach --resource-group sparse-embedding-rg --name fastapi       