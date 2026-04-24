# Chunkers

> **Source:** https://docs.chonkie.ai/oss/chunkers/overview
> **Loaded from:** SKILL.md (via progressive disclosure)

Chonkie provides 12 chunkers, each optimized for different content types and use cases.

## TokenChunker (`token`)

Splits text into fixed-size token chunks with configurable overlap. The most straightforward and reliable strategy.

**Best for:** General-purpose chunking, consistent chunk sizes, token-based models.

```python
from chonkie import TokenChunker

chunker = TokenChunker(
    tokenizer="gpt2",        # or "character" (default), "word", "byte"
    chunk_size=512,          # max tokens per chunk
    chunk_overlap=50         # overlap between chunks
)

chunks = chunker(text)
```

**Parameters:**

- `tokenizer` — string identifier (`"character"`, `"word"`, `"byte"`, `"gpt2"`, `"cl100k_base"`) or tokenizer instance
- `chunk_size` — max tokens per chunk (default: 2048)
- `chunk_overlap` — number or percentage of overlapping tokens (default: 0)

## SentenceChunker (`sentence`)

Chunks at sentence boundaries while respecting token limits. Sentences are never split mid-thought.

**Best for:** Q&A systems, maintaining complete thoughts.

```python
from chonkie import SentenceChunker

chunker = SentenceChunker(
    tokenizer="character",
    chunk_size=512,
    min_sentences_per_chunk=1,
    min_characters_per_sentence=12,
    delim=["\n", ". ", "! ", "? "],
    include_delim="prev"
)

chunks = chunker(text)
```

## RecursiveChunker (`recursive`)

Hierarchically chunks using multiple delimiters — paragraphs, then sentences, then words. Preserves document structure naturally.

**Best for:** Markdown, structured documents, hierarchical content, long well-structured texts.

```python
from chonkie import RecursiveChunker

chunker = RecursiveChunker(
    tokenizer="character",
    chunk_size=512,
    min_characters_per_chunk=24
)

# Use pre-configured recipes
chunker_md = RecursiveChunker.from_recipe("markdown", lang="en")
chunker_hi = RecursiveChunker.from_recipe(lang="hi")  # Hindi

chunks = chunker(text)
```

**Recipes:** `default`, `markdown`, `python`, `js`. Languages: `en`, `hi`, `zh`, `jp`, `ko`.

## FastChunker (`fast`)

SIMD-accelerated byte-based chunking at 100+ GB/s throughput. Uses byte-size limits instead of token counts for extreme performance.

**Best for:** High-throughput pipelines, large-scale document processing where byte size is acceptable.

```python
from chonkie import FastChunker

chunker = FastChunker(
    chunk_size=4096,          # bytes (not tokens)
    delimiters="\n.?",        # split at newlines, periods, question marks
)

# Pattern-based splitting (e.g., SentencePiece)
chunker = FastChunker(
    chunk_size=4096,
    pattern="▁",              # metaspace character
    prefix=True               # keep pattern at start of next chunk
)

chunks = chunker(text)
```

**Parameters:**

- `chunk_size` — target size in **bytes** (default: 4096)
- `delimiters` — single-byte delimiter characters (default: `"\n.?"`)
- `pattern` — multi-byte pattern to split on (overrides delimiters)
- `prefix` — keep delimiter at start of next chunk (default: False)
- `consecutive` — split at start of consecutive delimiter runs (default: False)
- `forward_fallback` — search forward for delimiter when none found backward (default: False)

## SemanticChunker (`semantic`)

Groups content based on semantic similarity using embeddings. Includes Savitzky-Golay filtering and skip-window merging for advanced boundary detection. Inspired by Greg Kamradt's work.

**Best for:** Multi-topic documents, maintaining topical coherence, preserving context.

```python
from chonkie import SemanticChunker

chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-32M",  # default model
    threshold=0.8,                                  # similarity threshold (0-1)
    chunk_size=2048,                               # max tokens per chunk
    similarity_window=3,                           # sentences for similarity calc
    skip_window=0                                  # 0=disabled, 1+=merge non-consecutive groups
)

chunks = chunker(text)
```

**Parameters:**

- `embedding_model` — model identifier or `BaseEmbeddings` instance
- `threshold` — cosine similarity for grouping (default: 0.8). Lower = larger groups.
- `chunk_size` — max tokens per chunk (default: 2048)
- `similarity_window` — sentences to consider for similarity (default: 3)
- `min_sentences_per_chunk` — minimum sentences per chunk (default: 1)
- `min_characters_per_sentence` — minimum chars per sentence (default: 24)
- `skip_window` — groups to skip when looking for similar content to merge (default: 0)
- `filter_window` — Savitzky-Golay filter window length (default: 5)
- `filter_polyorder` — polynomial order for the filter (default: 3)

## CodeChunker (`code`)

Language-aware chunking using Abstract Syntax Trees (AST). Preserves function and class boundaries. Supports 165+ languages via tree-sitter-language-pack with auto-detection via Magika.

**Best for:** Source code, API documentation, technical content.

```python
from chonkie import CodeChunker

# Auto language detection
chunker = CodeChunker()

# Specify language explicitly
chunker = CodeChunker(language="python")

chunks = chunker(code_text)
```

Supported languages include Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, Ruby, HTML, CSS, SQL, Bash, Dockerfile, and 150+ more.

## LateChunker (`late`)

Implements the Late Chunking algorithm. Generates document-level embeddings first, then derives chunk embeddings for richer contextual representation.

**Best for:** Retrieval optimization, higher recall RAG systems.

```python
from chonkie import LateChunker

chunker = LateChunker(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    chunk_size=512
)

chunks = chunker(text)
```

## NeuralChunker (`neural`)

Uses a fine-tuned BERT model to detect semantic shifts in text. ML-powered boundary detection for topic-coherent chunks.

**Best for:** Maximum quality, complex documents with subtle topic shifts.

```python
from chonkie import NeuralChunker

chunker = NeuralChunker()
chunks = chunker(text)
```

## SlumberChunker (`slumber`)

Agentic chunking powered by LLMs via the Genie interface. Uses generative models (Gemini, OpenAI, etc.) to intelligently determine optimal chunk boundaries.

**Best for:** Books, research papers, when quality matters most.

```python
from chonkie import SlumberChunker

chunker = SlumberChunker(verbose=True)
chunks = chunker(text)
```

Requires `genie` optional install and a Gemini API key (or other Genie provider).

## TableChunker (`table`)

Splits large markdown/HTML tables into manageable chunks by rows while preserving headers.

**Best for:** Markdown tables, tabular data, structured documents with tables.

```python
from chonkie import TableChunker

chunker = TableChunker(
    chunk_size=512
)

chunks = chunker(table_text)
```

## SDPMChunker (`sdpm`)

Semantic Document Partitioning and Merging. Groups semantically similar content, then merges related non-consecutive groups.

**Best for:** Documents where related topics are separated by other content.

## TeraflopAIChunker (`teraflopai`)

Segments text using the TeraflopAI Segmentation API. Ideal for domain-specific segmentation such as legal documents.

```python
from chonkie import TeraflopAIChunker

chunker = TeraflopAIChunker(api_key="your_api_key")
chunks = chunker(text)
```

## Async Support

All chunkers support async out of the box:

```python
import asyncio
from chonkie import RecursiveChunker

async def main():
    chunker = RecursiveChunker(chunk_size=512)

    # Single text
    chunks = await chunker.achunk("Document text...")

    # Batch
    all_chunks = await chunker.achunk_batch(["Doc 1", "Doc 2"])

    # Concurrent
    results = await asyncio.gather(
        *[chunker.achunk(text) for text in texts]
    )

asyncio.run(main())
```

Async methods use `asyncio.to_thread` under the hood, safe for FastAPI, Starlette, aiohttp, and other async frameworks.

## Thread Safety

All chunkers are thread-safe. Sharing a single instance across concurrent `asyncio.gather` calls is fine and avoids redundant initialization costs.
