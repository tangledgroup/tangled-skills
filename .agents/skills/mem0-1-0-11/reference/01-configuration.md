# Mem0 Configuration Guide

Configure Mem0 OSS components including LLMs, vector stores, embedders, and rerankers.

## Configuration Methods

### Python Dictionary

```python
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "api_key": "${QDRANT_API_KEY}"
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-mini",
            "temperature": 0.1,
            "api_key": "${OPENAI_API_KEY}"
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small"
        }
    },
    "reranker": {
        "provider": "cohere",
        "config": {
            "model": "rerank-english-v3.0",
            "api_key": "${COHERE_API_KEY}"
        }
    }
}

memory = Memory.from_config(config)
```

### YAML Configuration File

```yaml
# config.yaml
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
    api_version: "2024-02-01"

embedder:
  provider: ollama
  config:
    model: nomic-embed-text
    base_url: http://localhost:11434

reranker:
  provider: zero_entropy
  config:
    api_key: ${ZERO_ENTROPY_KEY}
```

```python
from mem0 import Memory

memory = Memory.from_config_file("config.yaml")
```

## Supported LLM Providers

### OpenAI

```python
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-nano-2025-04-14",  # Default
            "temperature": 0.1,  # Keep ≤0.2 for deterministic extraction
            "api_key": "${OPENAI_API_KEY}"
        }
    }
}
```

**Available models:** `gpt-4.1-nano`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4-turbo`

### Anthropic

```python
config = {
    "llm": {
        "provider": "anthropic",
        "config": {
            "model": "claude-3-5-sonnet-latest",
            "temperature": 0.1,
            "api_key": "${ANTHROPIC_API_KEY}"
        }
    }
}
```

### Ollama (Local)

```python
config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.1",
            "base_url": "http://localhost:11434",
            "temperature": 0.1
        }
    }
}
```

### Azure OpenAI

```python
config = {
    "llm": {
        "provider": "azure_openai",
        "config": {
            "deployment_name": "gpt-4.1-mini",
            "api_key": "${AZURE_OPENAI_KEY}",
            "api_version": "2024-02-01",
            "azure_endpoint": "https://your-resource.openai.azure.com"
        }
    }
}
```

### AWS Bedrock

```python
config = {
    "llm": {
        "provider": "aws_bedrock",
        "config": {
            "model": "anthropic.claude-3-sonnet-20240229-v1:0",
            "region": "us-east-1"
            # Uses AWS credentials chain
        }
    }
}
```

### Google AI / Vertex AI

```python
# Google AI Studio
config = {
    "llm": {
        "provider": "google_AI",
        "config": {
            "model": "gemini-1.5-pro-002",
            "api_key": "${GEMINI_API_KEY}"
        }
    }
}

# Vertex AI
config = {
    "llm": {
        "provider": "vertexai",
        "config": {
            "model": "gemini-1.5-pro-002",
            "project_id": "${GCP_PROJECT}",
            "location": "us-central1"
        }
    }
}
```

### Other Providers

- **Groq** - Ultra-fast inference with Llama3, Mixtral
- **Mistral AI** - Mistral, Mixtral models
- **Together AI** - 50+ open models
- **LM Studio** - Local model server
- **LiteLLM** - Unified API for 100+ providers
- **vLLM** - High-throughput serving
- **xAI** - Grok models

## Supported Vector Stores

### Qdrant (Default)

```python
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "mem0_memories",
            # For cloud:
            # "api_key": "${QDRANT_CLOUD_KEY}",
            # "url": "https://your-cluster.qdrant.tech"
        }
    }
}
```

### Chroma

```python
config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "path": "./chroma_db",  # Local persistence
            # Or cloud:
            # "chroma_cloud_host": "your-host.chromadb.io",
            # "chroma_cloud_api_key": "${CHROMA_KEY}"
        }
    }
}
```

### pgvector (PostgreSQL)

```python
config = {
    "vector_store": {
        "provider": "pgvector",
        "config": {
            "connection_string": "postgresql://user:pass@localhost:5432/dbname",
            "collection_name": "mem0_memories"
        }
    }
}
```

### Pinecone

```python
config = {
    "vector_store": {
        "provider": "pinecone",
        "config": {
            "api_key": "${PINECONE_API_KEY}",
            "environment": "gcp-starter",
            "index_name": "mem0-index"
        }
    }
}
```

### Other Vector Stores

- **Weaviate** - Local or cloud deployment
- **Milvus** - Scalable vector database
- **Elasticsearch/OpenSearch** - Hybrid search
- **Redis** - In-memory with persistence
- **MongoDB Atlas** - Document + vector
- **Supabase** - pgvector wrapper
- **Azure AI Search** - Managed service
- **Databricks** - Vector search on Databricks

## Supported Embedders

### OpenAI (Default)

```python
config = {
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",  # or text-embedding-3-large
            "api_key": "${OPENAI_API_KEY}"
        }
    }
}
```

### Ollama

```python
config = {
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",  # 768 dimensions
            "base_url": "http://localhost:11434"
        }
    }
}
```

### Vertex AI

```python
config = {
    "embedder": {
        "provider": "vertexai",
        "config": {
            "model": "textembedding-gecko@003",
            "project_id": "${GCP_PROJECT}"
        }
    }
}
```

### HuggingFace

```python
config = {
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "api_key": "${HF_API_KEY}"  # For inference API
        }
    }
}
```

### Other Embedders

- **Azure OpenAI** - Managed embeddings
- **AWS Bedrock** - Amazon Titan embeddings
- **Google AI** - Gemini embedding models
- **Together AI** - Multiple embedding models
- **LangChain** - Any LangChain embedder

## Supported Rerankers

Rerankers improve search precision by re-scoring top-k results.

### Cohere

```python
config = {
    "reranker": {
        "provider": "cohere",
        "config": {
            "model": "rerank-english-v3.0",  # or rerank-multilingual-v3.0
            "api_key": "${COHERE_API_KEY}"
        }
    }
}
```

### SentenceTransformer (Local)

```python
config = {
    "reranker": {
        "provider": "sentence_transformer",
        "config": {
            "model": "cross-encoder/ms-marco-MiniLM-L-12-v2"
        }
    }
}
```

### LLM Reranker

Use an LLM to rerank (slower but flexible):

```python
config = {
    "reranker": {
        "provider": "llm",
        "config": {
            "model": "gpt-4.1-mini"  # Uses configured LLM
        }
    }
}
```

### Other Rerankers

- **HuggingFace** - Any cross-encoder model
- **Zero Entropy** - Commercial reranker API
- **Custom** - Implement your own reranker interface

## Graph Memory Configuration

Enable relationship tracking with Neo4j or Memgraph:

```python
config = {
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "${NEO4J_PASSWORD}"
        }
    },
    # Optional: tune graph extraction
    "graph_config": {
        "enable_graph": True,
        "threshold": 0.7  # Confidence threshold for relationships
    }
}

memory = Memory.from_config(config)
```

## Tuning Recommendations

### For Deterministic Extraction

```python
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "temperature": 0.0,  # Maximum determinism
            "model": "gpt-4.1-mini"  # Faster/cheaper for extraction
        }
    }
}
```

### For Production Performance

```python
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "qdrant.internal",  # Internal network
            "port": 6333
        }
    },
    "reranker": {
        "provider": "cohere",
        "config": {
            "model": "rerank-english-v3.0"
        }
    },
    # Limit search scope
    "search_config": {
        "top_k": 10,  # Don't fetch too many
        "threshold": 0.7  # Minimum similarity score
    }
}
```

### For Local/Offline Use

```python
config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.1:8b",
            "base_url": "http://localhost:11434"
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "base_url": "http://localhost:11434"
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "path": "./chroma_db"  # Fully local
        }
    }
}
```

## Environment Variables

Mem0 reads these automatically:

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API authentication |
| `ANTHROPIC_API_KEY` | Anthropic Claude API |
| `COHERE_API_KEY` | Cohere reranker/embeddings |
| `QDRANT_API_KEY` | Qdrant cloud authentication |
| `PINECONE_API_KEY` | Pinecone vector database |
| `AZURE_OPENAI_KEY` | Azure OpenAI authentication |
| `GCP_PROJECT` | Google Cloud project ID |

## Validation

Test your configuration:

```python
from mem0 import Memory

memory = Memory.from_config(config)

# Quick smoke test
test_result = memory.search("test query", user_id="test_user")
print(f"Configuration valid: {test_result is not None}")
```

Common issues:
- **Dimension mismatch** - Ensure embedder dimensions match vector store expectations
- **Connection errors** - Verify network access to vector store
- **API key errors** - Check environment variables are set
- **Model not found** - Confirm model name is correct for provider
