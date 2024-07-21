# WikiSpeaks - A Scalable RAG-based Wikipedia Assistant

A highly scalable chat assistant that provides real-time Wikipedia information using the `Llama-2-7b-chat` LLM, inferenced
with Kserve for high concurrency, monitored using Prometheus and implemented on a user-friendly Streamlit interface

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

## Demo


## Prerequisites

- Kubernetes Cluster (recommend 16 cpu x 64 Gb RAM x 1 Nvidia GPU per worker node )
- Python 3.9+

## Installation

### KServe

Install KServe on your cluster using the KServe Quick installation script - 

```
curl -s "https://raw.githubusercontent.com/kserve/kserve/release-0.13/hack/quick_install.sh" | bash
```

Deploy the the Llama2 Chat model for text generation from HuggingFace by deploying the InferenceService resource on your cluster -

```
kubectl apply -f deployments/kserve-llama.yaml
```

Note - The KServe HuggingFace runtime by default uses vLLM to serve the LLM models for faster time-to-first-token(TTFT) and higher token generation throughput than the HuggingFace API. If the model is not supported by vLLM, KServe falls back to HuggingFace backend as a failsafe.

Check InferenceService status - 

```
kubectl get inferenceservices huggingface-llama2
```