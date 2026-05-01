# Configuration and Components

## Configure Mem0 OSS

Mem0 OSS lets you wire up your preferred LLM, vector store, embedder, and reranker.

### Python Configuration (Dict)

```python
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        },
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-mini",
            "temperature": 0.1,
        },
    },
    "embedder": {
        "provider": "vertexai",
        "config": {
            "model": "textembedding-gecko@003",
        },
    },
    "reranker": {
        "provider": "cohere",
        "config": {
            "model": "rerank-english-v3.0",
        },
    },
}

memory = Memory.from_config(config)
```

### YAML Configuration

```yaml
vector_store:
  provider: qdrant
  config:
    host: localhost
    port: 6333

llm:
  provider: azure_openai
  config:
    api_key: ${AZURE_OPENAI_KEY}
    deployment_name: gpt-4.1-mini

embedder:
  provider: ollama
  config:
    model: nomic-embed-text

reranker:
  provider: zero_entropy
  config:
    api_key: ${ZERO_ENTROPY_KEY}
```

Load at runtime:

```python
from mem0 import Memory
memory = Memory.from_config_file("config.yaml")
```

### Environment Variables

Store secrets as environment variables:

```bash
export QDRANT_API_KEY="..."
export OPENAI_API_KEY="..."
export COHERE_API_KEY="..."
```

## Tune Component Settings

- **Vector store collections** — Name collections explicitly (`collection_name`) to isolate tenants and enable per-tenant retention policies.
- **LLM extraction temperature** — Keep temperatures ≤0.2 so extracted memories stay deterministic. Raise only when you see missing facts.
- **Reranker depth** — Limit `top_k` to 10–20 results; sending more adds latency without meaningful gains.
- **Managed + self-hosted mix** — Ensure every outbound provider call goes through a secure network path. Managed rerankers often require outbound internet even if your vector store is on-prem.

## LLM Providers (OSS)

Mem0 supports 18+ LLM providers for memory extraction:

- **OpenAI** — Default. `gpt-5-mini` via `OPENAI_API_KEY`.
- **Anthropic** — Claude models via API key.
- **Azure OpenAI** — Azure-hosted deployments.
- **AWS Bedrock** — Managed model services.
- **Google AI** — Gemini models.
- **Groq** — Low-latency inference.
- **DeepSeek** — DeepSeek models.
- **Mistral AI** — Mistral models.
- **MiniMax** — MiniMax models.
- **xAI** — Grok models.
- **Sarvam** — Indian-language models.
- **Together** — Together Inference API.
- **Ollama** — Local models via Ollama server.
- **LM Studio** — Models served from LM Studio.
- **LiteLLM** — Multiplex many providers behind one adapter.
- **vLLM** — Self-hosted inference with vLLM.
- **LangChain LLM** — Wrap any LangChain-compatible LLM.

Configuration schema:

```python
"llm": {
    "provider": "<provider_name>",
    "config": {
        "model": "<model_name>",
        "temperature": 0.1,
        # provider-specific settings...
    }
}
```

## Embedding Providers (OSS)

10+ embedding providers for vector storage:

- **OpenAI** — Default. `text-embedding-3-small`.
- **Azure OpenAI** — Azure-hosted embeddings.
- **AWS Bedrock** — Bedrock-hosted embeddings.
- **Google AI** — Gemini embeddings.
- **Vertex AI** — Google Cloud Vertex AI embeddings.
- **Hugging Face** — Open-source HF embedding models.
- **Ollama** — Local embeddings via Ollama.
- **LM Studio** — Embeddings from LM Studio.
- **Together** — Together-hosted embeddings.
- **LangChain** — Wrap any LangChain-compatible embedder.

For best results with hybrid search (semantic + keyword + entity boosting), use at least Qwen 600M (`gte-Qwen2-1.5B-instruct`) or comparable.

## Vector Databases (OSS)

24+ vector store backends:

- **Qdrant** — Default. Local at `/tmp/qdrant` or remote.
- **Chroma** — Lightweight embedded store.
- **PGVector** — Postgres with pgvector extension.
- **Milvus** — Large-scale deployments.
- **Pinecone** — Managed vector database.
- **MongoDB** — Atlas Vector Search.
- **Azure AI Search** — Azure-hosted search.
- **Redis** — Redis Stack.
- **Valkey** — Redis fork.
- **Elasticsearch** — Elasticsearch-backed search.
- **OpenSearch** — OpenSearch-backed search.
- **Supabase** — Supabase with pgvector.
- **Upstash Vector** — Serverless vector store.
- **Vectorize** — Cloudflare Vectorize.
- **Vertex AI Vector Search** — Google Cloud.
- **Weaviate** — Weaviate-backed search.
- **FAISS** — Local FAISS-based similarity search.
- **LangChain Vector Store** — Wrap any LangChain-compatible store.
- **Baidu** — Baidu Cloud vector service.
- **Cassandra** — Cassandra-backed storage.
- **S3 Vectors** — AWS S3 Vectors.
- **Databricks** — Delta Lake on Databricks.
- **Neptune Analytics** — AWS Neptune (graph + vector).
- **Turbopuffer** — Serverless vector store.

Configuration schema:

```python
"vector_store": {
    "provider": "<provider_name>",
    "config": {
        "host": "localhost",
        "port": 6333,
        # provider-specific settings...
    }
}
```

## Rerankers (OSS)

6+ reranker options for improving search precision:

- **Cohere** — Cohere Rerank API.
- **Sentence Transformer** — Local cross-encoder rerankers.
- **Hugging Face** — HF-hosted reranker models.
- **LLM Reranker (prompt)** — Use a prompted LLM as the reranker.
- **Zero Entropy** — Zero Entropy reranker.

Configuration schema:

```python
"reranker": {
    "provider": "<provider_name>",
    "config": {
        "model": "<model_name>",
        # provider-specific settings...
    }
}
```

## Quick Recovery Guide

- **Qdrant connection errors** — Confirm port 6333 is exposed and API key matches.
- **Empty search results** — Verify the embedder model name; a mismatch causes dimension errors.
- **Unknown reranker** — Update the SDK (`pip install --upgrade mem0ai`) to load the latest provider registry.
- **spaCy model not found** — Run `python -m spacy download en_core_web_sm` after installing `mem0ai[nlp]`.
- **Entity store collection creation fails** — Check vector store connectivity and permissions.
