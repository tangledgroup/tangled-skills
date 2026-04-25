# Chunkers Deep Dive

## Overview

Chonkie provides 10+ chunking strategies, each designed for specific use cases. All chunkers share a consistent interface and support async operations out of the box.

## Common Interface

### Python

```python
# Single text chunking
chunks = chunker.chunk(text)

# Batch processing
chunks = chunker.chunk_batch(texts)

# Direct calling (Python only)
chunks = chunker(text)  # or chunker([text1, text2])

# Async variants (all chunkers support these)
chunks = await chunker.achunk(text)
chunks = await chunker.achunk_batch(texts)
```

### JavaScript

```javascript
// Single text chunking
const chunks = await chunker.chunk(text);
```

## TokenChunker

Splits text into fixed-size token chunks with configurable overlap.

**Best for**: Maintaining consistent chunk sizes for LLM context windows.

```python
from chonkie import TokenChunker

chunker = TokenChunker(
    tokenizer="gpt2",      # Options: "character", "word", "byte", "gpt2", or custom
    chunk_size=2048,       # Maximum tokens per chunk
    chunk_overlap=128      # Overlap between chunks
)

chunks = chunker.chunk("Your text here...")
```

**Parameters:**
- `tokenizer` (str/Any): Tokenizer identifier or custom tokenizer instance
- `chunk_size` (int): Maximum tokens per chunk (default: 2048)
- `chunk_overlap` (int/float): Overlap in tokens or as percentage (default: 0)

**Tokenizer Options:**
```python
# Built-in tokenizers
TokenChunker(tokenizer="character")  # Default
TokenChunker(tokenizer="word")
TokenChunker(tokenizer="byte")
TokenChunker(tokenizer="gpt2")

# Custom tokenizer (tiktoken)
import tiktoken
tokenizer = tiktoken.get_encoding("cl100k_base")
chunker = TokenChunker(tokenizer=tokenizer, chunk_size=2048)

# Custom tokenizer (Hugging Face)
from transformers import AutoTokenizer
hf_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
chunker = TokenChunker(tokenizer=hf_tokenizer, chunk_size=512)
```

## FastChunker

SIMD-accelerated byte-based chunking at 100+ GB/s throughput.

**Best for**: High-throughput pipelines where byte size limits are acceptable.

```python
from chonkie import FastChunker

chunker = FastChunker(
    chunk_size=4096,       # Bytes per chunk
    chunk_overlap=256      # Byte overlap
)

chunks = chunker.chunk("High-throughput text processing...")
```

**Parameters:**
- `chunk_size` (int): Maximum bytes per chunk (default: 4096)
- `chunk_overlap` (int): Byte overlap between chunks (default: 0)

## SentenceChunker

Splits text at sentence boundaries using NLP-based sentence detection.

**Best for**: Maintaining semantic completeness at the sentence level.

```python
from chonkie import SentenceChunker

chunker = SentenceChunker(
    language="en",         # ISO 639-1 language code
    chunk_size=5,          # Maximum sentences per chunk
    chunk_overlap=1        # Overlapping sentences
)

chunks = chunker.chunk("This is sentence one. This is sentence two. And three.")
```

**Parameters:**
- `language` (str): Language code for sentence detection (default: "en")
- `chunk_size` (int): Maximum sentences per chunk (default: 5)
- `chunk_overlap` (int): Overlapping sentences between chunks (default: 0)

## RecursiveChunker

Recursively splits text using hierarchical rules (paragraphs → sentences → words → characters).

**Best for**: Long documents with well-defined structure.

```python
from chonkie import RecursiveChunker

chunker = RecursiveChunker(
    tokenizer="gpt2",              # Tokenizer for counting
    chunk_size=512,                # Maximum tokens per chunk
    chunk_overlap=50,              # Overlap in tokens
    min_characters_per_chunk=30,   # Minimum characters to keep a chunk
    separators=["\n\n", "\n", " ", ""]  # Split hierarchy
)

chunks = chunker.chunk("Your structured document...")
```

**Parameters:**
- `tokenizer` (str/Any): Tokenizer for token counting
- `chunk_size` (int): Maximum tokens per chunk (default: 4000)
- `chunk_overlap` (int/float): Overlap in tokens or percentage (default: 200)
- `min_characters_per_chunk` (int): Minimum characters to keep a chunk (default: 30)
- `separators` (list[str]): Hierarchy of separators to try (default: ["\n\n", "\n", " ", ""])

**Custom Separators:**
```python
# For code chunking
code_separators = [
    "\nclass ",
    "\ndef ",
    "\nasync def ",
    "\n#",
    "\n",
    " ",
    ""
]
chunker = RecursiveChunker(separators=code_separators, chunk_size=512)

# For markdown
md_separators = [
    "\n\n## ",
    "\n\n### ",
    "\n\n",
    "\n",
    " ",
    ""
]
chunker = RecursiveChunker(separators=md_separators, chunk_size=1024)
```

## SemanticChunker

Groups content based on semantic similarity using embeddings.

**Best for**: Preserving context and topical coherence in chunks.

```python
from chonkie import SemanticChunker

chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-32M",  # Embedding model
    chunk_size=1024,                               # Max tokens per chunk
    threshold=0.8,                                 # Similarity threshold (0-1)
    similarity_window=3,                           # Lookahead window
    similarity_boundaries=None                     # Specific boundary indices
)

chunks = chunker.chunk("Your document with semantic sections...")
```

**Parameters:**
- `embedding_model` (str/Embeddings): Model name or embeddings instance
- `chunk_size` (int): Maximum tokens per chunk (default: 1024)
- `threshold` (float): Similarity threshold for breaks [0, 1] (default: 0.8)
- `similarity_window` (int): Number of sentences to compare (default: 3)
- `similarity_boundaries` (list[int]): Pre-computed boundary indices

**How it works:**
1. Embeds consecutive sentence pairs
2. Computes cosine similarity between pairs
3. Creates chunk breaks where similarity drops below threshold
4. Higher threshold = more chunks, lower threshold = fewer chunks

```python
# Low threshold (0.5) = fewer, larger chunks
chunker_loose = SemanticChunker(threshold=0.5, chunk_size=2048)

# High threshold (0.9) = more, smaller chunks
chunker_strict = SemanticChunker(threshold=0.9, chunk_size=512)
```

## LateChunker

Implements the Late Chunking algorithm for higher recall in RAG applications.

**Best for**: RAG systems requiring better retrieval performance.

```python
from chonkie import LateChunker

chunker = LateChunker(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    chunk_size=512,              # Base chunk size in tokens
    n_slices=4,                  # Number of slices per chunk
    slice_token_limit=128        # Tokens per slice
)

chunks = chunker.chunk("Document for late chunking...")
```

**Parameters:**
- `embedding_model` (str/Embeddings): Model for embedding slices
- `chunk_size` (int): Base chunk size in tokens (default: 512)
- `n_slices` (int): Number of slices per chunk (default: 4)
- `slice_token_limit` (int): Maximum tokens per slice (default: 128)

**How it works:**
1. Splits text into overlapping slices
2. Embeds each slice individually
3. Averages slice embeddings to create chunk embedding
4. Improves recall by capturing multiple semantic perspectives

## CodeChunker

Splits code based on AST (Abstract Syntax Tree) structure.

**Best for**: Chunking source code files while preserving structural integrity.

```python
from chonkie import CodeChunker

chunker = CodeChunker(
    language="python",           # Auto-detected or specify: "python", "javascript", etc.
    chunk_size=512,              # Maximum tokens per chunk
    chunk_overlap=50,            # Overlap between chunks
    tokenizer="gpt2"             # Tokenizer for counting
)

chunks = chunker.chunk("""
def hello_world():
    print("Hello, World!")

class MyClass:
    def __init__(self):
        self.value = 42
""")
```

**Parameters:**
- `language` (str): Programming language (auto-detected if not specified)
- `chunk_size` (int): Maximum tokens per chunk (default: 512)
- `chunk_overlap` (int): Overlap in tokens (default: 0)
- `tokenizer` (str/Any): Tokenizer for token counting

**Supported Languages:**
Python, JavaScript, TypeScript, Java, C, C++, Go, Rust, Ruby, PHP, and 50+ more via tree-sitter.

## NeuralChunker

Uses a fine-tuned BERT model to detect semantic shifts and split text accordingly.

**Best for**: Topic-coherent chunks where semantic boundaries matter.

```python
from chonkie import NeuralChunker

chunker = NeuralChunker(
    model_name="davish/semantic-chunker",  # BERT-based model
    chunk_size=512,                         # Target chunk size
    chunk_overlap=50,                       # Overlap between chunks
    tokenizer="gpt2"                        # Tokenizer for counting
)

chunks = chunker.chunk("Document with topic shifts...")
```

**Parameters:**
- `model_name` (str): Hugging Face model name (default: "davish/semantic-chunker")
- `chunk_size` (int): Target chunk size in tokens (default: 512)
- `chunk_overlap` (int): Overlap in tokens (default: 0)
- `tokenizer` (str/Any): Tokenizer for token counting

## SlumberChunker

Agentic chunking using LLMs via the Genie interface for S-tier chunk quality.

**Best for**: Maximum quality chunks where LLM understanding is critical.

```python
from chonkie import SlumberChunker, GeminiGenie

# Initialize with a genie (LLM interface)
genie = GeminiGenie(
    model="gemini-1.5-pro",
    api_key="your_api_key"
)

chunker = SlumberChunker(
    genie=genie,
    chunk_size=512,
    instructions="Split text into coherent topics"
)

chunks = chunker.chunk("Document requiring intelligent chunking...")
```

**Parameters:**
- `genie` (Genie): LLM interface (GeminiGenie, OpenAIGenie, GroqGenie, etc.)
- `chunk_size` (int): Target chunk size in tokens (default: 512)
- `instructions` (str): Custom instructions for the LLM

**Supported Genies:**
```python
# Google Gemini
genie = GeminiGenie(model="gemini-1.5-pro", api_key="...")

# OpenAI
genie = OpenAIGenie(model="gpt-4", api_key="...")

# Groq (fast inference)
genie = GroqGenie(model="llama3-70b-8192", api_key="...")

# Cerebras (fastest inference)
genie = CerebrasGenie(model="llama3.1-70b", api_key="...")

# Any OpenAI-compatible API
genie = OpenAIGenie(
    model="meta-llama/llama-3-70b",
    base_url="https://openrouter.ai/api/v1",
    api_key="..."
)
```

## TableChunker

Splits large markdown tables into smaller, manageable chunks by row, preserving headers.

**Best for**: Tabular data in RAG and LLM pipelines.

```python
from chonkie import TableChunker

chunker = TableChunker(
    rows_per_chunk=10,      # Maximum rows per chunk
    include_header=True,    # Include header row in each chunk
    chunk_overlap=2         # Overlapping rows between chunks
)

markdown_table = """
| Name | Age | City |
|------|-----|------|
| Alice | 30 | New York |
| Bob | 25 | London |
| Charlie | 35 | Paris |
... (100+ rows)
"""

chunks = chunker.chunk(markdown_table)
```

**Parameters:**
- `rows_per_chunk` (int): Maximum rows per chunk (default: 10)
- `include_header` (bool): Include header in each chunk (default: True)
- `chunk_overlap` (int): Overlapping rows between chunks (default: 0)

## TeraflopAIChunker

Segments text using the TeraflopAI Segmentation API.

**Best for**: Domain-specific segmentation such as legal documents.

```python
from chonkie import TeraflopAIChunker

chunker = TeraflopAIChunker(
    api_key="your_teraflopai_api_key",
    chunk_size=512,
    chunk_overlap=50
)

chunks = chunker.chunk("Legal document or specialized content...")
```

**Parameters:**
- `api_key` (str): TeraflopAI API key
- `chunk_size` (int): Target chunk size (default: 512)
- `chunk_overlap` (int): Overlap between chunks (default: 0)

## Async Support

All chunkers support async operations without extra setup:

```python
import asyncio
from chonkie import SemanticChunker

async def process_documents():
    chunker = SemanticChunker(chunk_size=512, threshold=0.8)
    
    # Single text async
    chunks = await chunker.achunk("Your document...")
    
    # Batch async
    all_chunks = await chunker.achunk_batch([
        "Document 1...",
        "Document 2...",
        "Document 3..."
    ])
    
    # Concurrent processing
    texts = ["doc1", "doc2", "doc3"]
    results = await asyncio.gather(
        *[chunker.achunk(text) for text in texts]
    )
    
    return results

# Run async processing
chunks = asyncio.run(process_documents())
```

**Async Methods:**
- `achunk(text)` - Chunk a single text
- `achunk_batch(texts)` - Chunk multiple texts
- `achunk_document(doc)` - Chunk a Document object with concurrent dispatch

## Thread Safety

All chunkers are thread-safe and can be shared across threads or async tasks:

```python
# Safe to share chunker instance
chunker = RecursiveChunker(chunk_size=512)

# Use in multiple threads or async tasks
results = asyncio.gather(
    chunker.achunk("text1"),
    chunker.achunk("text2"),
    chunker.achunk("text3")
)
```

## Performance Tips

1. **Batch processing**: Use `chunk_batch()` for better throughput
2. **Async for I/O-bound**: Use async methods in web frameworks (FastAPI, aiohttp)
3. **Reuse chunkers**: Initialize once and reuse across calls
4. **Match chunker to content**: Use specialized chunkers (CodeChunker, TableChunker) for structured data
5. **Adjust overlap**: Higher overlap improves context but increases token usage

## Troubleshooting

**"Module not found" errors:**
```bash
# SemanticChunker requires embeddings
pip install "chonkie[semantic]"

# CodeChunker requires tree-sitter
pip install "chonkie[code]"

# NeuralChunker requires transformers
pip install "chonkie[neural]"

# SlumberChunker requires genie
pip install "chonkie[genie]"
```

**Slow chunking:**
- Use `FastChunker` for maximum speed (100+ GB/s)
- Reduce `chunk_size` for faster processing
- Use batch processing for multiple documents
- Consider API-based chunking for resource-intensive operations

**Incorrect chunk boundaries:**
- Adjust `threshold` in SemanticChunker (higher = more chunks)
- Customize `separators` in RecursiveChunker for your document type
- Use specialized chunkers (CodeChunker, TableChunker) for structured content
