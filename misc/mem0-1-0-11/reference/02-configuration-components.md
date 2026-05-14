# Configuration and Components

## Overview

Mem0 OSS allows full customization of its pipeline components. Override any default with `Memory.from_config()` or `Memory.from_config_file()`. The Platform manages these automatically.

## Configuration Methods

### Python Dictionary

```python
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": 6333},
    },
    "llm": {
        "provider": "openai",
        "config": {"model": "gpt-4.1-mini", "temperature": 0.1},
    },
    "embedder": {
        "provider": "vertexai",
        "config": {"model": "textembedding-gecko@003"},
    },
    "reranker": {
        "provider": "cohere",
        "config": {"model": "rerank-english-v3.0"},
    },
}

memory = Memory.from_config(config)
```

### YAML Configuration File

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

```python
from mem0 import Memory
memory = Memory.from_config_file("config.yaml")
```

## Supported LLMs (18+)

All supported in Python. TypeScript supports: **OpenAI**, **Anthropic**, **Groq**.

- **OpenAI** — Default. Models: `gpt-4.1-nano-2025-04-14`, `gpt-4.1-mini`, etc.
- **Anthropic** — Claude models with advanced reasoning
- **Azure OpenAI** — Enterprise Azure-hosted OpenAI models
- **Ollama** — Local model deployment for privacy
- **Together** — Open-source model inference platform
- **Groq** — High-performance LPU optimized models
- **LiteLLM** — Unified LLM interface and proxy
- **Mistral AI** — Mistral model integration
- **Google AI** — Gemini models
- **AWS Bedrock** — Enterprise AWS managed models
- **DeepSeek** — Advanced reasoning models
- **MiniMax** — MiniMax model integration
- **xAI** — Grok models
- **Sarvam** — Indian language models
- **LM Studio** — Local model management
- **LangChain** — LangChain LLM wrapper
- **vLLM** — High-performance inference framework

### OpenAI Configuration

```python
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-mini",
            "temperature": 0.1,
            "api_key": "sk-..."
        }
    }
}
```

### Ollama Configuration

```python
config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.1",
            "base_url": "http://localhost:11434"
        }
    }
}
```

### Structured vs Unstructured Outputs

Mem0 supports two OpenAI output formats:

- **Structured outputs** — Optimized for returning JSON objects. Ideal for data extraction.
- **Unstructured outputs** — Free-form text responses with `response_format` parameter.

## Supported Vector Databases (24+)

All supported in Python. TypeScript supports: **Qdrant**, **Redis**, **Valkey**, **Vectorize**, and in-memory.

- **Qdrant** — Default for OSS. High-performance vector search
- **Chroma** — AI-native open-source database
- **PGVector** — PostgreSQL extension
- **Milvus** — Scalable open-source
- **Pinecone** — Managed serverless
- **MongoDB** — Document DB with vector search
- **Azure AI Search** — Enterprise Microsoft search
- **Redis** — Real-time vector storage
- **Valkey** — Open-source Redis alternative
- **Elasticsearch** — Distributed search engine
- **OpenSearch** — Open-source search platform
- **Supabase** — Firebase alternative with vectors
- **Upstash Vector** — Serverless vector DB
- **Vertex AI** — Google Cloud vector search
- **Weaviate** — Open-source with ML
- **FAISS** — Facebook AI Similarity Search
- **Databricks** — Delta Lake integration
- **Turbopuffer** — Serverless high-performance
- And more: Azure MySQL, Cassandra, S3 Vectors, Neptune Analytics, Baidu, Vectorize, LangChain

### Qdrant Configuration

```python
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "my_memories"
        }
    }
}
```

### PGVector Configuration

```python
config = {
    "vector_store": {
        "provider": "pgvector",
        "config": {
            "connection": "postgresql://user:pass@localhost:5432/dbname"
        }
    }
}
```

### Dimension Mismatch

If using a model with different embedding dimensions (e.g., 768 instead of default 1536):

```python
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 768
        }
    }
}
```

## Supported Embedding Models (10+)

All supported in Python. TypeScript supports: **OpenAI** only.

- **OpenAI** — Default. `text-embedding-3-small`
- **Azure OpenAI** — Enterprise Azure-hosted
- **Ollama** — Local embeddings (e.g., `nomic-embed-text`)
- **Hugging Face** — Open-source models
- **Google AI** — Gemini embeddings
- **Vertex AI** — Google Cloud enterprise
- **Together** — Open-source model embeddings
- **LM Studio** — Local model embeddings
- **LangChain** — LangChain embedder wrapper
- **AWS Bedrock** — Amazon managed embeddings

### Embedder Configuration

```python
config = {
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",
            "dimensions": 512  # Optional: reduce dimensions
        }
    }
}
```

## Supported Rerankers (5)

Reranking adds a second scoring pass after vector retrieval for better precision.

- **Cohere** — Multilingual hosted reranker
- **Sentence Transformer** — Local cross-encoders (GPU or CPU)
- **Hugging Face** — Any hosted or on-prem model
- **LLM Reranker** — Prompt-driven scoring via any LLM
- **Zero Entropy** — Neural reranking tuned for retrieval

### Provider Comparison

- **Cohere**: Medium latency, high quality, API cost, no local deploy
- **Sentence Transformer**: Low latency, good quality, free, local deploy
- **Hugging Face**: Low-medium latency, variable quality, free, local deploy
- **LLM Reranker**: High latency, very high quality, API cost, depends on model

### Reranker Configuration

```python
# Cohere
config = {
    "reranker": {
        "provider": "cohere",
        "config": {
            "model": "rerank-english-v3.0",
            "api_key": "your-cohere-api-key",
            "top_k": 10
        }
    }
}

# Sentence Transformer (local)
config = {
    "reranker": {
        "provider": "sentence_transformer",
        "config": {
            "model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
            "device": "cuda",
            "max_length": 512
        }
    }
}

# Hugging Face
config = {
    "reranker": {
        "provider": "huggingface",
        "config": {
            "model": "BAAI/bge-reranker-base",
            "device": "cuda",
            "batch_size": 32
        }
    }
}
```

## Tuning Tips

- **LLM extraction temperature**: Keep ≤0.2 for deterministic memory extraction. Raise only when facts are missing.
- **Reranker depth**: Limit `top_k` to 10–20. Larger pools add latency without meaningful gains.
- **Vector store collections**: Name explicitly (`collection_name`) in production to isolate tenants.
- **Secrets management**: Store API keys as environment variables, not in config files.
