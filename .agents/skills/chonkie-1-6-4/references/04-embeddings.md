# Embeddings

> **Source:** https://docs.chonkie.ai/oss/embeddings/overview
> **Loaded from:** SKILL.md (via progressive disclosure)

Chonkie provides embedding handlers for 10+ providers, used with SemanticChunker, LateChunker, and EmbeddingsRefinery.

## Common Interface

All embeddings handlers share the same API:

```python
# Single text
emb = embeddings.embed(text)

# Batch
emb = embeddings.embed_batch(texts)

# Direct calling
emb = embeddings(text)
```

## Available Providers

### Model2VecEmbeddings (`model2vec`)

Ultra-fast static embeddings. Default for semantic chunking. Pre-computed and stored in lookup tables — no model inference at query time.

```bash
pip install "chonkie[semantic]"
```

```python
from chonkie import Model2VecEmbeddings
embeddings = Model2VecEmbeddings()
```

### SentenceTransformerEmbeddings (`st`)

Any HuggingFace sentence-transformers model. Required by LateChunker.

```bash
pip install "chonkie[st]"
```

```python
from chonkie import SentenceTransformerEmbeddings
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
```

### OpenAIEmbeddings (`openai`)

OpenAI text-embedding models (text-embedding-3-small, text-embedding-3-large).

```bash
pip install "chonkie[openai]"
```

```python
from chonkie import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
```

### AzureOpenAIEmbeddings (`azure-openai`)

Azure-hosted OpenAI embeddings.

```bash
pip install "chonkie[azure-openai]"
```

### CohereEmbeddings (`cohere`)

Cohere embedding models.

```bash
pip install "chonkie[cohere]"
```

### GeminiEmbeddings (`gemini`)

Google Gemini embeddings.

```bash
pip install "chonkie[gemini]"
```

### JinaEmbeddings (`jina`)

Jina AI embeddings.

```bash
pip install "chonkie[jina]"
```

### VoyageAIEmbeddings (`voyageai`)

Voyage AI embeddings.

```bash
pip install "chonkie[voyageai]"
```

### LiteLLMEmbeddings (`litellm`)

Access 100+ embedding models through LiteLLM unified interface.

```bash
pip install "chonkie[litellm]"
```

### AutoEmbeddings

Automatically selects the best available embeddings handler based on installed dependencies:

```python
from chonkie import AutoEmbeddings
embeddings = AutoEmbeddings()  # picks best available
```

### Custom Embeddings

Bring your own embedding model by implementing the `BaseEmbeddings` interface:

```python
from chonkie.types import BaseEmbeddings

class MyEmbeddings(BaseEmbeddings):
    def embed(self, text: str) -> list[float]:
        # Your embedding logic
        return [...]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]
```

## EmbeddingsRefinery

Attach embeddings directly to chunks after chunking:

```python
from chonkie import RecursiveChunker, EmbeddingsRefinery, Model2VecEmbeddings

chunker = RecursiveChunker(chunk_size=512)
embeddings = Model2VecEmbeddings()
refinery = EmbeddingsRefinery(embeddings)

chunks = chunker(text)
chunks = refinery(chunks)

# Each chunk now has .embedding
for chunk in chunks:
    if chunk.embedding is not None:
        print(f"Shape: {len(chunk.embedding)}")
```

## Usage With Chunkers

Embeddings are required by:
- **SemanticChunker** — uses embeddings to detect topic boundaries
- **LateChunker** — generates document-level then chunk-level embeddings
- **NeuralChunker** — uses BERT-based model internally

They are optional with:
- **EmbeddingsRefinery** — attaches embeddings to any chunks post-chunking
- **Handshakes** — some vector databases require embeddings for storage
