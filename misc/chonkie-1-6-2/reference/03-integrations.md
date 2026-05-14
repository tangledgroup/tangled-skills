# Integrations

Chonkie provides 32+ integrations across tokenizers, embedding providers, LLM genies, vector database handshakes, porters, chefs, and fetchers.

## Tokenizers

Choose from built-in tokenizers or provide custom token counting functions:

- **`character`**: Basic character-level tokenizer (default)
- **`word`**: Word-level tokenizer
- **`byte`**: Byte-level tokenizer on UTF-8 encoded bytes
- **`gpt2`**: GPT-2 tokenizer via HuggingFace `tokenizers` library (`chonkie[tokenizers]`)
- **Custom callable**: Any function `(text: str) -> int`

```python
# Custom token counter
def custom_token_counter(text: str) -> int:
    return len(text.split())

chunker = RecursiveChunker(tokenizer=custom_token_counter)
```

### Tokenizer Installation Options

- `tokenizers` library (HuggingFace): `chonkie[tokenizers]`
- `tiktoken` (OpenAI): `chonkie[tiktoken]` or `chonkie[openai]`
- `transformers` AutoTokenizer: `chonkie[neural]`

## Embeddings Providers

Seamlessly works with various embedding model providers. Use `AutoEmbeddings` to load models easily.

### Provider List

- **Model2VecEmbeddings** (`model2vec`): Ultra-fast static embeddings. Install: `chonkie[model2vec]` or `chonkie[semantic]`
- **SentenceTransformerEmbeddings** (`sentence-transformers`): Any sentence-transformers model. Install: `chonkie[st]`
- **OpenAIEmbeddings** (`openai`): OpenAI embedding API (text-embedding-3-small, etc.). Install: `chonkie[openai]`
- **AzureOpenAIEmbeddings** (`azure-openai`): Azure OpenAI service. Install: `chonkie[azure-openai]`
- **CohereEmbeddings** (`cohere`): Cohere embedding API. Install: `chonkie[cohere]`
- **GeminiEmbeddings** (`gemini`): Google Gemini embedding API. Install: `chonkie[gemini]`
- **JinaEmbeddings** (`jina`): Jina AI embedding API. Install: `chonkie[jina]`
- **VoyageAIEmbeddings** (`voyageai`): Voyage AI models. Install: `chonkie[voyageai]`
- **LiteLLMEmbeddings** (`litellm`): 100+ embedding models via LiteLLM proxy. Install: `chonkie[litellm]`

### Usage in Chunkers

```python
from chonkie import SemanticChunker, SentenceTransformerEmbeddings

# String model identifier (auto-detected)
chunker = SemanticChunker(embedding_model="minishlab/potion-base-32M")

# Explicit embedding instance
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
chunker = SemanticChunker(embedding_model=embeddings)
```

### Usage in EmbeddingsRefinery

```python
from chonkie import EmbeddingsRefinery, OpenAIEmbeddings

refinery = EmbeddingsRefinery(
    embedding_model=OpenAIEmbeddings(model="text-embedding-3-small")
)
```

## Genies (LLM Interfaces)

Genies provide interfaces to LLM providers for advanced chunking strategies (SlumberChunker) and other generative tasks.

### Provider List

- **GeminiGenie** (`gemini`): Google Gemini APIs. Install: `chonkie[genie]`
- **OpenAIGenie** (`openai`): OpenAI APIs. Install: `chonkie[openai]`
- **AzureOpenAIGenie** (`azure-openai`): Azure OpenAI. Install: `chonkie[azure-openai]`
- **GroqGenie** (`groq`): Fast inference on Groq hardware. Install: `chonkie[groq]`
- **CerebrasGenie** (`cerebras`): Ultra-fast inference on Cerebras wafer-scale engines. Install: `chonkie[cerebras]`

### Usage

```python
from chonkie import GeminiGenie, OpenAIGenie

# Gemini
genie = GeminiGenie(api_key="YOUR_API_KEY")
response = genie.generate("Hello!")
json_response = genie.generate_json("Extract data", schema)

# OpenAI (works with any OpenAI-compatible API)
genie = OpenAIGenie(
    model="meta-llama/llama-3.3-70b",
    base_url="https://openrouter.ai/api/v1",
    api_key="your_api_key"
)
```

Both Genies support `generate()` for text generation and `generate_json()` for structured JSON output.

## Handshakes (Vector Database Integrations)

Handshakes provide a unified interface to ingest chunks directly into vector databases with embedding and storage in one step.

### Available Handshakes

- **ChromaHandshake** (`chroma`): ChromaDB (ephemeral or persistent). Install: `chonkie[chroma]`
- **ElasticHandshake** (`elastic`): Elasticsearch. Install: `chonkie[elastic]`
- **MilvusHandshake** (`milvus`): Milvus collections. Install: `chonkie[milvus]`
- **MongoDBHandshake** (`mongodb`): MongoDB Atlas with vector search. Install: `chonkie[mongodb]`
- **PgvectorHandshake** (`pgvector`): PostgreSQL with pgvector extension. Install: `chonkie[pgvector]`
- **PineconeHandshake** (`pinecone`): Pinecone indexes. Install: `chonkie[pinecone]`
- **QdrantHandshake** (`qdrant`): Qdrant database. Install: `chonkie[qdrant]`
- **TurbopufferHandshake** (`tpuf`): Turbopuffer. Install: `chonkie[tpuf]`
- **WeaviateHandshake** (`weaviate`): Weaviate. Install: `chonkie[weaviate]`

### Pipeline Usage

```python
from chonkie import Pipeline

# Store in Qdrant
docs = (Pipeline()
    .fetch_from("file", dir="./docs", ext=[".txt"])
    .chunk_with("semantic", threshold=0.8, chunk_size=1024)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("qdrant", collection_name="docs", url="http://localhost:6333")
    .run())

# Store in ChromaDB
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("chroma", collection_name="documents")
    .run(texts="Your text here..."))
```

## Porters

Porters export chunks to file formats or external platforms.

### JSONPorter

Exports chunks to a JSON file. Included in base install.

```python
from chonkie import Pipeline

docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .export_with("json", file="chunks.json")
    .run(texts="Your text here..."))
```

### DatasetsPorter

Exports chunks to HuggingFace Datasets format. Install: `chonkie[datasets]`.

```python
from chonkie import Pipeline

docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .export_with("datasets", name="my-dataset")
    .run(texts="Your text here..."))
```

## Chefs

Chefs preprocess and transform raw data before chunking.

- **TextChef** (`text`): Basic text cleaning and normalization. Included in base install.
- **MarkdownChef** (`markdown`): Extracts tables and code blocks from markdown documents, preserving metadata.
- **TableChef** (`table`): Specialized table processing.

```python
from chonkie import Pipeline

doc = (Pipeline()
    .fetch_from("file", path="README.md")
    .process_with("markdown")  # MarkdownChef
    .chunk_with("recursive", chunk_size=512)
    .run())

# Access markdown metadata
print(f"Found {len(doc.tables)} tables")
print(f"Found {len(doc.code)} code blocks")
```

## Fetchers

Fetchers load data from various sources.

- **FileFetcher** (`file`): Load text from files and directories with extension filtering. Included in base install.

```python
from chonkie import Pipeline

# Single file
doc = (Pipeline()
    .fetch_from("file", path="document.txt")
    .chunk_with("recursive")
    .run())

# Directory with filters
docs = (Pipeline()
    .fetch_from("file", dir="./documents", ext=[".md", ".txt"])
    .chunk_with("recursive")
    .run())
```

## Hubbie (HuggingFace Hub)

Simple wrapper for HuggingFace Hub operations, used by `from_recipe()` methods. Install: `chonkie[hub]`.

## Visualizer

Rich console visualizations and HTML output for debugging chunk quality. Install: `chonkie[viz]`.

```python
from chonkie import TokenChunker, Visualizer

chunker = TokenChunker(chunk_size=512)
chunks = chunker("Your text here...")

viz = Visualizer()
viz.print(chunks)           # Rich terminal output
viz.save("chonkie.html", chunks)  # Save highlighted HTML
```
