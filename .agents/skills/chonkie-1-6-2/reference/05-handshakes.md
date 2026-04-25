# Vector Database Handshakes

## Overview

Handshakes allow you to easily connect Chonkie to vector databases. Embed your chunks and write them to your database in just a few lines of code using the Pipeline API.

## Quick Start

### Basic Usage with Pipelines

```python
from chonkie import Pipeline

# Chunk and store in Qdrant
docs = (Pipeline()
    .fetch_from("file", dir="./documents", ext=[".txt"])
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("qdrant", 
              collection_name="documents",
              url="http://localhost:6333")
    .run())

print(f"Stored {len(docs)} documents in Qdrant")
```

## ChromaDB Handshake

Connect to ephemeral or persistent ChromaDB instances.

**Installation:**
```bash
pip install "chonkie[chroma]"
```

**Basic Usage:**
```python
from chonkie import Pipeline

# In-memory ChromaDB
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("chroma", collection_name="documents")
    .run(texts="Your document..."))

# Persistent ChromaDB
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("chroma", 
              collection_name="documents",
              persist_directory="./chroma_db")
    .run(texts="Your document..."))
```

**Parameters:**
- `collection_name` (str): Name of the ChromaDB collection
- `persist_directory` (str): Directory for persistent storage (optional)
- `embedding_model` (str): Embedding model name (if not using refinery)

## Qdrant Handshake

Connect to Qdrant vector database (local or cloud).

**Installation:**
```bash
pip install "chonkie[qdrant]"
```

**Basic Usage:**
```python
from chonkie import Pipeline

# Local Qdrant
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("qdrant", 
              collection_name="documents",
              url="http://localhost:6333")
    .run(texts="Your document..."))

# Qdrant Cloud
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("qdrant",
              collection_name="documents",
              url="https://your-cluster.qdrant.tech",
              api_key=os.environ["QDRANT_API_KEY"])
    .run(texts="Your document..."))

# In-memory Qdrant
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("qdrant", collection_name="documents")
    .run(texts="Your document..."))
```

**Parameters:**
- `collection_name` (str): Name of the Qdrant collection
- `url` (str): Qdrant server URL (optional, defaults to in-memory)
- `api_key` (str): API key for Qdrant Cloud (optional)
- `embedding_model` (str): Embedding model name (if not using refinery)

**Advanced Usage:**
```python
from chonkie import QdrantHandshake

# Custom configuration
handshake = QdrantHandshake(
    collection_name="documents",
    url="http://localhost:6333",
    distance_metric="Cosine",  # or "Euclid", "Dot"
    vector_size=512,
    payload_fields=["source", "metadata"]
)

# Use in pipeline
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in(handshake)
    .run(texts="Your document..."))
```

## Pinecone Handshake

Connect to Pinecone vector database.

**Installation:**
```bash
pip install "chonkie[pinecone]"
```

**Basic Usage:**
```python
import os
from chonkie import Pipeline

# Connect to Pinecone
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("pinecone",
              index_name="documents",
              api_key=os.environ["PINECONE_API_KEY"])
    .run(texts="Your document..."))

# With custom namespace
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("pinecone",
              index_name="documents",
              api_key=os.environ["PINECONE_API_KEY"],
              namespace="my-namespace")
    .run(texts="Your document..."))
```

**Parameters:**
- `index_name` (str): Name of the Pinecone index
- `api_key` (str): Pinecone API key
- `namespace` (str): Namespace for namespacing vectors (optional)
- `environment` (str): Pinecone environment (optional, for legacy setups)

**Note:** Ensure index exists before storing:
```python
from pinecone import Pinecone

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

# Create index if not exists
if "documents" not in pc.list_indexes().names():
    pc.create_index(
        name="documents",
        dimension=1536,  # Match your embedding dimension
        metric="cosine"
    )
```

## MongoDB Atlas Handshake

Connect to MongoDB Atlas with vector search.

**Installation:**
```bash
pip install "chonkie[mongodb]"
```

**Basic Usage:**
```python
import os
from chonkie import Pipeline

# Connect to MongoDB Atlas
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("mongodb",
              collection_name="documents",
              connection_string=os.environ["MONGODB_URI"])
    .run(texts="Your document..."))

# With custom index
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("mongodb",
              collection_name="documents",
              connection_string=os.environ["MONGODB_URI"],
              index_name="vector_index",
              vector_path="embedding")
    .run(texts="Your document..."))
```

**Parameters:**
- `collection_name` (str): Name of the MongoDB collection
- `connection_string` (str): MongoDB connection URI
- `database_name` (str): Database name (optional, extracted from URI)
- `index_name` (str): Atlas vector search index name (optional)
- `vector_path` (str): Field path for embeddings (optional)

## Pgvector Handshake

Connect to PostgreSQL with pgvector extension.

**Installation:**
```bash
pip install "chonkie[pgvector]"
```

**Basic Usage:**
```python
import os
from chonkie import Pipeline

# Connect to PostgreSQL with pgvector
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("pgvector",
              collection_name="documents",
              connection_string=os.environ["DATABASE_URL"])
    .run(texts="Your document..."))

# With custom schema
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("pgvector",
              collection_name="documents",
              connection_string=os.environ["DATABASE_URL"],
              schema="rag")
    .run(texts="Your document..."))
```

**Parameters:**
- `collection_name` (str): Name of the PostgreSQL table
- `connection_string` (str): PostgreSQL connection URI
- `schema` (str): Database schema (optional, defaults to "public")
- `embedding_dimension` (int): Dimension of embeddings (auto-detected if not specified)

**Prerequisites:**
```sql
-- Enable pgvector extension in your PostgreSQL database
CREATE EXTENSION IF NOT EXISTS vector;
```

## Elasticsearch Handshake

Connect to Elasticsearch with vector search.

**Installation:**
```bash
pip install "chonkie[elastic]"
```

**Basic Usage:**
```python
import os
from chonkie import Pipeline

# Connect to Elasticsearch
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("elastic",
              index_name="documents",
              url="http://localhost:9200")
    .run(texts="Your document..."))

# With authentication
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("elastic",
              index_name="documents",
              url="https://your-elasticsearch.es.azurewebsites.net",
              username=os.environ["ES_USERNAME"],
              password=os.environ["ES_PASSWORD"])
    .run(texts="Your document..."))
```

**Parameters:**
- `index_name` (str): Name of the Elasticsearch index
- `url` (str): Elasticsearch server URL
- `username` (str): Username for authentication (optional)
- `password` (str): Password for authentication (optional)
- `embedding_dimension` (int): Dimension of embeddings (auto-detected if not specified)

## Weaviate Handshake

Connect to Weaviate vector database.

**Installation:**
```bash
pip install "chonkie[weaviate]"
```

**Basic Usage:**
```python
import os
from chonkie import Pipeline

# Connect to local Weaviate
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("weaviate",
              class_name="Documents",
              url="http://localhost:8080")
    .run(texts="Your document..."))

# Connect to Weaviate Cloud
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("weaviate",
              class_name="Documents",
              url=os.environ["WEAVIATE_URL"],
              api_key=os.environ["WEAVIATE_API_KEY"])
    .run(texts="Your document..."))
```

**Parameters:**
- `class_name` (str): Name of the Weaviate class (capitalized)
- `url` (str): Weaviate server URL
- `api_key` (str): API key for Weaviate Cloud (optional)
- `embedding_model` (str): Embedding model name (if not using refinery)

## Turbopuffer Handshake

Connect to Turbopuffer vector database.

**Installation:**
```bash
pip install "chonkie[tpuf]"
```

**Basic Usage:**
```python
import os
from chonkie import Pipeline

# Connect to Turbopuffer
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("turbopuffer",
              table_name="documents",
              api_key=os.environ["TURBOPUFFER_API_KEY"])
    .run(texts="Your document..."))
```

**Parameters:**
- `table_name` (str): Name of the Turbopuffer table
- `api_key` (str): Turbopuffer API key
- `namespace` (str): Namespace for organizing tables (optional)

## Milvus Handshake

Connect to Milvus vector database.

**Installation:**
```bash
pip install "chonkie[milvus]"
```

**Basic Usage:**
```python
import os
from chonkie import Pipeline

# Connect to local Milvus
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("milvus",
              collection_name="documents",
              uri="http://localhost:19530")
    .run(texts="Your document..."))

# Connect to Milvus Cloud (Zilliz)
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("milvus",
              collection_name="documents",
              uri=os.environ["MILVUS_URI"],
              token=os.environ["MILVUS_TOKEN"])
    .run(texts="Your document..."))
```

**Parameters:**
- `collection_name` (str): Name of the Milvus collection
- `uri` (str): Milvus server URI
- `token` (str): Authentication token for Milvus Cloud (optional)
- `embedding_dimension` (int): Dimension of embeddings (auto-detected if not specified)

## Complete RAG Pipeline Example

```python
import os
from chonkie import Pipeline

# Full RAG ingestion pipeline with Qdrant
def ingest_documents(directory: str, collection_name: str):
    """Ingest documents from directory into vector database."""
    
    docs = (Pipeline()
        .fetch_from("file", dir=directory, ext=[".txt", ".md", ".pdf"])
        .process_with("text")
        .chunk_with("semantic", threshold=0.8, chunk_size=1024)
        .refine_with("overlap", context_size=100)
        .refine_with("embedding", model="minishlab/potion-base-32M")
        .store_in("qdrant",
                  collection_name=collection_name,
                  url="http://localhost:6333")
        .run())
    
    print(f"Ingested {len(docs)} documents with {sum(len(d.chunks) for d in docs)} chunks")
    return docs

# Usage
ingest_documents("./knowledge_base", "rag_collection")
```

## Metadata Preservation

All handshakes preserve chunk metadata:

```python
from chonkie import Pipeline

docs = (Pipeline()
    .fetch_from("file", dir="./documents", ext=[".txt"])
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("qdrant", collection_name="documents", url="http://localhost:6333")
    .run())

# Metadata includes:
# - source: File path or source identifier
# - chunk_index: Index of chunk within document
# - token_count: Number of tokens in chunk
# - start_index, end_index: Character positions in original text
# - Custom metadata from chefs (e.g., tables, code blocks)
```

## Embedding Model Matching

Ensure embedding model matches vector database configuration:

| Embedding Model | Dimensions | Compatible Databases |
|-----------------|------------|---------------------|
| minishlab/potion-base-32M | 512 | All |
| all-MiniLM-L6-v2 | 384 | All |
| text-embedding-3-small | 1536 | All |
| text-embedding-3-large | 3072 | All |

**Important:** When creating vector database collections, specify the correct dimension:

```python
# Qdrant example
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

# Create collection with correct dimension
client.create_collection(
    collection_name="documents",
    vectors_config={"size": 1536, "distance": "Cosine"}  # Match embedding dimension
)
```

## Performance Tips

1. **Batch processing**: Process multiple documents in one pipeline run
2. **Embedding refinery**: Use `.refine_with("embedding")` before `.store_in()` for better control
3. **Async operations**: Use `arun()` for high-throughput ingestion
4. **Connection pooling**: Reuse handshake instances across multiple pipeline runs
5. **Parallel ingestion**: Split documents and ingest in parallel to different collections

## Troubleshooting

### Connection Errors

**Qdrant:**
```python
# Ensure Qdrant is running
docker run -p 6333:6333 qdrant/qdrant

# Or check connection
from qdrant_client import QdrantClient
client = QdrantClient(url="http://localhost:6333")
print(client.get_collections())
```

**ChromaDB:**
```python
# Check ChromaDB is accessible
import chromadb
client = chromadb.Client()
print(client.list_collections())
```

### Dimension Mismatch

Ensure embedding dimensions match database configuration:

```python
from chonkie import Model2VecEmbeddings

# Check embedding dimension
embeddings = Model2VecEmbeddings(model_name="minishlab/potion-base-32M")
emb = embeddings.embed("test")
print(f"Dimension: {len(emb)}")  # Should match database configuration
```

### Missing Dependencies

```bash
# Install required handshake dependencies
pip install "chonkie[qdrant]"      # For Qdrant
pip install "chonkie[chroma]"      # For ChromaDB
pip install "chonkie[pinecone]"    # For Pinecone
pip install "chonkie[mongodb]"     # For MongoDB
pip install "chonkie[pgvector]"    # For PostgreSQL
pip install "chonkie[elastic]"     # For Elasticsearch
pip install "chonkie[weaviate]"    # For Weaviate
pip install "chonkie[tpuf]"        # For Turbopuffer
pip install "chonkie[milvus]"      # For Milvus
```

### Authentication Errors

Ensure API keys are set correctly:

```python
import os

# Set required environment variables
os.environ["PINECONE_API_KEY"] = "your-key"
os.environ["QDRANT_API_KEY"] = "your-key"  # For Qdrant Cloud
os.environ["WEAVIATE_API_KEY"] = "your-key"  # For Weaviate Cloud

# Or pass directly in pipeline
.store_in("pinecone", index_name="docs", api_key="your-key")
```
