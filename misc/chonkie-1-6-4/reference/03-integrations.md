# Integrations

Chonkie provides 32+ integrations across tokenizers, embedding providers, LLM genies, vector database handshakes, porters, chefs, and fetchers.

## Tokenizers

Choose from supported tokenizers or provide a custom token counting function:

- **`character`** — Basic character-level tokenizer. **Default.**
- **`word`** — Basic word-level tokenizer.
- **`byte`** — Byte-level tokenizer on UTF-8 encoded bytes.
- **`tokenizers`** — Load any tokenizer from HuggingFace `tokenizers` library (`chonkie[tokenizers]`).
- **`tiktoken`** — OpenAI's `tiktoken` library (e.g., `"gpt2"`, `"cl100k_base"`) (`chonkie[tiktoken]`).
- **`transformers`** — Load via `AutoTokenizer` from HF `transformers` (`chonkie[neural]`).

Custom token counter:

```python
def custom_token_counter(text: str) -> int:
    return len(text)

chunker = RecursiveChunker(tokenizer=custom_token_counter)
```

## Embedding Providers

Seamlessly works with various embedding model providers via `AutoEmbeddings`:

**Provider availability:**

- **`model2vec`** — `Model2VecEmbeddings`. Ultra-fast static embeddings. Install: `chonkie[model2vec]` or `chonkie[semantic]`.
- **`sentence-transformers`** — `SentenceTransformerEmbeddings`. Any sentence-transformers model. Install: `chonkie[st]`.
- **`openai`** — `OpenAIEmbeddings`. OpenAI embedding API. Install: `chonkie[openai]`.
- **`azure-openai`** — `AzureOpenAIEmbeddings`. Azure OpenAI service. Install: `chonkie[azure-openai]`.
- **`cohere`** — `CohereEmbeddings`. Cohere embedding API. Install: `chonkie[cohere]`.
- **`gemini`** — `GeminiEmbeddings`. Google Gemini embedding API. Install: `chonkie[gemini]`.
- **`jina`** — `JinaEmbeddings`. Jina AI embedding API. Install: `chonkie[jina]`.
- **`voyageai`** — `VoyageAIEmbeddings`. Voyage AI embedding API. Install: `chonkie[voyageai]`.
- **`litellm`** — `LiteLLMEmbeddings`. 100+ models via LiteLLM proxy. Install: `chonkie[litellm]`.

All embeddings share a common interface:

```python
# Single text
emb = embeddings.embed(text)

# Batch
emb = embeddings.embed_batch(texts)

# Direct calling
emb = embeddings(text)
```

## LLM Genies

Genies provide interfaces to Large Language Models for advanced chunking (SlumberChunker):

- **`GeminiGenie`** — Google Gemini APIs. Install: `chonkie[genie]`.
- **`OpenAIGenie`** — OpenAI APIs (also works with any OpenAI-compatible provider). Install: `chonkie[openai]`.
- **`AzureOpenAIGenie`** — Azure OpenAI APIs. Install: `chonkie[azure-openai]`.
- **`GroqGenie`** — Fast inference on Groq hardware. Install: `chonkie[groq]`.
- **`CerebrasGenie`** — Fastest inference on Cerebras hardware. Install: `chonkie[cerebras]`.

Using OpenAIGenie with OpenRouter:

```python
from chonkie import OpenAIGenie

genie = OpenAIGenie(
    model="meta-llama/llama-4-maverick",
    base_url="https://openrouter.ai/api/v1",
    api_key="your_api_key"
)
```

## Vector Database Handshakes

Handshakes provide a unified interface to ingest chunks directly into vector databases:

- **`chroma`** — `ChromaHandshake`. Ingest into ChromaDB. Install: `chonkie[chroma]`.
- **`elastic`** — `ElasticHandshake`. Ingest into Elasticsearch. Install: `chonkie[elastic]`.
- **`lancedb`** — `LanceDBHandshake`. Local or cloud LanceDB. Install: `chonkie[lancedb]`.
- **`milvus`** — `MilvusHandshake`. Milvus collection. Install: `chonkie[milvus]`.
- **`mongodb`** — `MongoDBHandshake`. MongoDB Atlas. Install: `chonkie[mongodb]`.
- **`pgvector`** — `PgvectorHandshake`. PostgreSQL with pgvector. Install: `chonkie[pgvector]`.
- **`pinecone`** — `PineconeHandshake`. Pinecone index. Install: `chonkie[pinecone]`.
- **`qdrant`** — `QdrantHandshake`. Qdrant database. Install: `chonkie[qdrant]`.
- **`turbopuffer`** — `TurbopufferHandshake`. Turbopuffer. Install: `chonkie[tpuf]`.
- **`weaviate`** — `WeaviateHandshake`. Weaviate database. Install: `chonkie[weaviate]`.

Usage in pipeline:

```python
docs = (Pipeline()
    .fetch_from("file", dir="./docs", ext=[".txt"])
    .chunk_with("semantic", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("qdrant", collection_name="docs", url="http://localhost:6333")
    .run())
```

## Porters

Export chunks to file formats:

- **`json`** — `JSONPorter`. Export chunks to a JSON file. Included in default install.
- **`datasets`** — `DatasetsPorter`. Export to HuggingFace Datasets format. Install: `chonkie[datasets]`.

```python
from chonkie import JSONPorter, DatasetsPorter

json_porter = JSONPorter()
json_porter.export(chunks)

datasets_porter = DatasetsPorter()
dataset = datasets_porter.export(chunks)
dataset = datasets_porter(chunks, save_to_disk=True, path="my_chunks")
```

## Chefs

Text preprocessing components (Python only):

- **`TextChef`** — Processes plain text files into structured `Document` objects. Included in default install.
- **`MarkdownChef`** — Processes markdown files, extracting tables, code blocks, and images into a `MarkdownDocument`. Included in default install.
- **`TableChef`** — Extracts tables from CSV/Excel files or markdown text. Install: `chonkie[table]`.

```python
from chonkie import TextChef, MarkdownChef

text_chef = TextChef()
doc = text_chef.process("article.txt")
print(doc.content)

md_chef = MarkdownChef(tokenizer="gpt2")
md_doc = md_chef.process("README.md")
print(f"Found {len(md_doc.tables)} tables, {len(md_doc.code)} code blocks")
```

## Fetchers

Connect data sources to the pipeline:

- **`FileFetcher`** — Retrieves files from local filesystem. Supports single file and directory modes with extension filtering. Included in default install.

```python
from chonkie import FileFetcher

fetcher = FileFetcher()
file_path = fetcher.fetch(path="document.txt")
file_paths = fetcher.fetch(dir="./docs", ext=[".txt", ".md"])
```

## Utilities

- **`Visualizer`** — Rich console and HTML visualizations for chunks. Install: `chonkie[viz]`.
- **`Hubbie`** — Simple wrapper for HuggingFace Hub operations. Install: `chonkie[hub]`.

```python
from chonkie import Visualizer

viz = Visualizer()
viz.print(chunks)       # Terminal output
viz.save("chunks.html", chunks)  # HTML file
```

## Installation Dependency Map

**Default** (`pip install chonkie`):
tqdm, numpy, chonkie-core, tenacity

**Optional extras and their dependencies:**

- `hub`: + huggingface-hub, jsonschema
- `viz`: + rich
- `model2vec`: + tokenizers, model2vec, numpy
- `st`: + tokenizers, sentence-transformers, accelerate
- `openai`: + openai, tiktoken, pydantic
- `cohere`: + tokenizers, cohere
- `jina`: + tokenizers
- `semantic`: + tokenizers, model2vec
- `code`: + tree-sitter, tree-sitter-language-pack, magika
- `neural`: + transformers, torch
- `genie`: + pydantic, google-genai
- `groq`: + pydantic, groq
- `cerebras`: + pydantic, cerebras-cloud-sdk
- `litellm`: + litellm, tiktoken, tokenizers
- `datasets`: + datasets
- `table`: + pandas
