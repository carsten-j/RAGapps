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
