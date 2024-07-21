# WikiSpeaks - A Scalable RAG-based Wikipedia Assistant

## Architecture Overview

This Project consists of 3 main components - 

### 1. Model Inferencing 

The `llama-2-7b-chat-hf` model is inferenced using KServe, a standard, cloud agnostic Model Inference Platform on Kubernetes.

### 2. Application - 

- **Data Source**: The Wikipedia python library scrapes text data from Wikipedia Pages based on the user's question.

- **Vector Database**: The data from Wikipedia is stored as a FAISS index with the help of Ray, significantly improving the speed of generating and persisting vector embeddings 

- **Prompt**: By utilizing the Langchain wrapper for OpenAI chat completion models, we can infer the hosted Llama model in our Retrieval Augmented Generation (RAG) approach using the context from the stored FAISS index and the user's question.

### 3. Monitoring 
To enable prometheus metrics, add the annotation `serving.kserve.io/enable-prometheus-scraping` to the InferenceService YAML. With the exported metrics (inference latency, explain request latency etc.), they can now be visualised on Grafana.