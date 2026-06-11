# Chunkers

Chonkie provides 12 chunking strategies. All share a common interface:

```python
# Single text
chunks = chunker.chunk(text)

# Batch processing
chunks = chunker.chunk_batch(texts)

# Direct calling
chunks = chunker(text)      # single text
batch_chunks = chunker([t1, t2])  # multiple texts

# Async variants (all chunkers support these)
chunks = await chunker.achunk(text)
chunks = await chunker.achunk_batch(texts)
chunks = await chunker.achunk_document(doc)
```

All chunkers return `Chunk` objects with fields: `text`, `start_index`, `end_index`, `token_count`, optional `context`, and optional `embedding`. All chunkers are thread-safe.

## TokenChunker

Splits text into fixed-size token windows. The fastest and most predictable chunker. Included in base install.

```python
from chonkie import TokenChunker

chunker = TokenChunker(
    tokenizer="character",   # "character" (default), "word", "byte", "gpt2", or any HF tokenizer
    chunk_size=2048,         # Maximum tokens per chunk
    chunk_overlap=128        # Overlap between chunks (int or float for percentage)
)

chunks = chunker("Your text here...")
```

**Parameters:**

- `tokenizer` — String identifier (`"character"`, `"word"`, `"byte"`, `"gpt2"`) or tokenizer instance. Default: `"character"`.
- `chunk_size` — Maximum tokens per chunk. Default: `2048`.
- `chunk_overlap` — Number or percentage of overlapping tokens. Default: `0`.

**Best for**: Consistent chunk sizes, token-based models, predictable output.

## FastChunker

SIMD-accelerated byte-based chunking at 100+ GB/s throughput. Uses `chonkie-core` Rust extension for extreme performance. Included in base install.

```python
from chonkie import FastChunker

chunker = FastChunker(
    chunk_size=4096,      # Target size in BYTES (not tokens)
    delimiters="\n.?",    # Split at newlines, periods, question marks
)

# Pattern-based splitting (e.g., for SentencePiece tokenizers)
chunker = FastChunker(
    chunk_size=4096,
    pattern="▁",          # Metaspace character
    prefix=True,          # Keep pattern at start of next chunk
)
```

**Parameters:**

- `chunk_size` — Target chunk size in **bytes** (not tokens). Default: `4096`.
- `delimiters` — Single-byte delimiter characters to split on. Default: `"\n.?"`.
- `pattern` — Multi-byte pattern to split on (overrides delimiters if set).
- `prefix` — Keep delimiter/pattern at start of next chunk instead of end of current. Default: `False`.
- `consecutive` — Split at start of consecutive delimiter runs. Default: `False`.
- `forward_fallback` — Search forward for delimiter when none found backward. Default: `False`.

**Best for**: High-throughput pipelines where byte size limits are acceptable. Not available via API server.

## SentenceChunker

Splits text at sentence boundaries, ensuring each chunk maintains complete sentences. Included in base install.

```python
from chonkie import SentenceChunker

chunker = SentenceChunker(
    tokenizer="character",
    chunk_size=2048,
    chunk_overlap=128,
    min_sentences_per_chunk=1,
    delim=[".", "!", "?", "\n"],
    include_delim="prev"
)

chunks = chunker("First sentence. Second sentence. Third.")
```

**Parameters:**

- `tokenizer` — Tokenizer identifier or instance. Default: `"character"`.
- `chunk_size` — Maximum tokens per chunk. Default: `2048`.
- `chunk_overlap` — Overlap tokens between chunks. Default: `0`.
- `min_sentences_per_chunk` — Minimum sentences per chunk. Default: `1`.
- `min_characters_per_sentence` — Minimum characters to count as a sentence. Default: `12`.
- `delim` — Sentence delimiters. Default: `[".", "!", "?", "\n"]`.
- `include_delim` — Attach delimiter to `"prev"` or `"next"` sentence. Default: `"prev"`.

**Best for**: Maintaining semantic completeness at sentence level, no mid-sentence splits.

## RecursiveChunker

Recursively splits text using a hierarchy of delimiters. Best for structured documents like books or research papers. Included in base install.

```python
from chonkie import RecursiveChunker, RecursiveRules

chunker = RecursiveChunker(
    tokenizer="character",
    chunk_size=2048,
    rules=RecursiveRules(),
    min_characters_per_chunk=24,
)

# Using a recipe (Python only)
chunker = RecursiveChunker.from_recipe("markdown", lang="en")
chunker = RecursiveChunker.from_recipe(lang="hi")  # Hindi
```

**Parameters:**

- `tokenizer` — Tokenizer identifier or instance. Default: `"character"`.
- `chunk_size` — Maximum tokens per chunk. Default: `2048`.
- `rules` — `RecursiveRules` with hierarchical splitting levels. Default: built-in rules.
- `min_characters_per_chunk` — Minimum characters per chunk. Default: `24`.

**RecursiveRules structure:**

```python
@dataclass
class RecursiveLevel:
    delimiters: Optional[Union[str, list[str]]]
    whitespace: bool = False
    include_delim: Optional[Literal["prev", "next"]]

@dataclass
class RecursiveRules:
    rules: list[RecursiveLevel]
```

Recipes are available on HuggingFace Hub at `chonkie-ai/recipes`.

**Best for**: Long documents with well-defined structure, markdown, code-adjacent text.

## SemanticChunker

Groups content based on semantic similarity using embeddings. Inspired by Greg Kamradt's work. Requires `[semantic]` install.

```python
from chonkie import SemanticChunker

chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-32M",  # Default model
    threshold=0.8,                               # Similarity threshold (0-1)
    chunk_size=2048,                             # Maximum tokens per chunk
    similarity_window=3,                         # Window for similarity calculation
    skip_window=0                                # Skip-and-merge window (0=disabled)
)

# With skip-and-merge (similar to legacy SDPM behavior)
chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-32M",
    threshold=0.7,
    chunk_size=2048,
    skip_window=1  # Merge similar non-consecutive groups
)
```

**Parameters:**

- `embedding_model` — Model identifier or `BaseEmbeddings` instance. Default: `"minishlab/potion-base-32M"`.
- `threshold` — Similarity threshold for grouping (0–1). Lower = larger groups. Default: `0.8`.
- `chunk_size` — Maximum tokens per chunk. Default: `2048`.
- `similarity_window` — Sentences to consider for similarity. Default: `3`.
- `min_sentences_per_chunk` — Minimum sentences per chunk. Default: `1`.
- `min_characters_per_sentence` — Minimum characters per sentence. Default: `24`.
- `skip_window` — Groups to skip when looking for similar content to merge. `0` = disabled. Default: `0`.
- `filter_window` — Savitzky-Golay filter window length for boundary detection. Default: `5`.
- `filter_polyorder` — Polynomial order for SG filter. Default: `3`.
- `filter_tolerance` — Tolerance for SG filter boundary detection. Default: `0.2`.
- `delim` — Sentence delimiters. Default: `[". ", "! ", "? ", "\n"]`.
- `include_delim` — `"prev"` or `"next"`. Default: `"prev"`.

**Best for**: Preserving topical coherence, grouping related content together. The `skip_window` feature replaces the legacy SDPM chunker.

## LateChunker

Implements late chunking strategy from the [Late Chunking paper](https://arxiv.org/abs/2409.04701). Encodes entire text into a single embedding, then splits using recursive rules and derives each chunk's embedding by averaging relevant parts. Requires `[st]` install.

```python
from chonkie import LateChunker, RecursiveRules

chunker = LateChunker(
    embedding_model="nomic-ai/modernbert-embed-base",
    chunk_size=2048,
    rules=RecursiveRules(),
    min_characters_per_chunk=24,
)

# Using a recipe
chunker = LateChunker.from_recipe("markdown", lang="en")
```

**Parameters:**

- `embedding_model` — SentenceTransformer model identifier. Default: `"nomic-ai/modernbert-embed-base"`.
- `chunk_size` — Maximum tokens per chunk. Default: `2048`.
- `rules` — RecursiveRules for splitting. Default: `RecursiveRules()`.
- `min_characters_per_chunk` — Minimum characters per chunk. Default: `24`.

**Best for**: Higher recall in RAG applications. Each chunk carries broader contextual information from the full document embedding. Only supports SentenceTransformer models. Not available in JavaScript SDK.

## CodeChunker

Splits code into structurally meaningful chunks using AST parsing via tree-sitter. Supports 165+ languages with auto-detection via Magika. Requires `[code]` install.

```python
from chonkie import CodeChunker

chunker = CodeChunker(
    language="python",      # Specific language or "auto" for Magika detection
    tokenizer="character",
    chunk_size=2048,
    include_nodes=False     # Include AST node metadata in output
)

chunks = chunker("def hello():\n    print('world')")
```

**Parameters:**

- `language` — Programming language key (e.g., `"python"`, `"javascript"`, `"rust"`) or `"auto"` for Magika detection.
- `tokenizer` — Tokenizer identifier or instance. Default: `"character"`.
- `chunk_size` — Maximum tokens per chunk. Default: `2048`.
- `include_nodes` — Include AST node metadata (type, line numbers). Default: `False`.

**Supported language categories**: General-purpose (Python, JavaScript, Rust, Go, Java, C++, etc.), Web/Markup (HTML, CSS, Vue, Svelte, Markdown), Config/DevOps (Bash, Dockerfile, YAML, Make), Systems/GPU (CUDA, GLSL, Verilog, WGSL).

**Best for**: Source code chunking that respects function/class boundaries.

## NeuralChunker

Uses a fine-tuned BERT model to detect semantic shifts and split at topic boundaries. Requires `[neural]` install.

```python
from chonkie import NeuralChunker

chunker = NeuralChunker(
    model="mirth/chonky_modernbert_base_1",  # Default model
    device_map="cpu",                        # "cpu", "cuda", "mps"
    min_characters_per_chunk=10,
)

# GPU inference
chunker = NeuralChunker(model="mirth/chonky_modernbert_base_1", device_map="cuda:0")
```

**Parameters:**

- `model` — Model identifier or path. Default: `"mirth/chonky_modernbert_base_1"`.
- `tokenizer` — Optional tokenizer. Default: `None` (auto-selected for model).
- `device_map` — Device for inference. Default: `"cpu"`.
- `min_characters_per_chunk` — Minimum characters per chunk. Default: `10`.
- `stride` — Stride for processing. Default: `None` (auto-selected).

**Best for**: Topic-coherent chunks, detecting semantic shifts in text. Not available in JavaScript SDK.

## SlumberChunker

Agentic chunker using generative models (LLMs) via the Genie interface for highest quality chunks. Requires `[genie]` install.

```python
from chonkie import SlumberChunker
from chonkie.genie import GeminiGenie

genie = GeminiGenie("gemini-3-pro-preview")

chunker = SlumberChunker(
    genie=genie,
    tokenizer="character",
    chunk_size=1024,
    candidate_size=128,        # Tokens around split point for Genie to examine
    min_characters_per_chunk=24,
    verbose=True               # Show Genie's decision-making process
)

# With OpenAI-compatible providers
from chonkie.genie import OpenAIGenie
genie = OpenAIGenie(
    model="meta-llama/llama-4-maverick",
    base_url="https://openrouter.ai/api/v1",
    api_key="your_api_key"
)
```

**Parameters:**

- `genie` — Genie interface instance. Default: tries global config (`GeminiGenie("gemini-3-pro-preview")`).
- `tokenizer` — Tokenizer for initial splitting. Default: `"character"`.
- `chunk_size` — Target maximum tokens per chunk. Default: `1024`.
- `rules` — Initial recursive rules for candidate split points. Default: `RecursiveRules()`.
- `candidate_size` — Tokens around potential split for Genie to examine. Default: `128`.
- `min_characters_per_chunk` — Minimum characters per chunk. Default: `24`.
- `verbose` — Show Genie's decision process. Default: `True`.

**Best for**: Complex documents with interwoven ideas where traditional chunkers struggle. Slowest but highest quality. Not available in JavaScript SDK.

## TableChunker

Splits large markdown or HTML tables into smaller chunks by row, always preserving headers. Included in base install.

```python
from chonkie import TableChunker

# Row-based chunking
chunker = TableChunker(tokenizer="row", chunk_size=3)  # 3 rows per chunk

# Token-based chunking
chunker = TableChunker(tokenizer="character", chunk_size=16)

table = """
| Name   | Age | City     |
|--------|-----|----------|
| Alice  | 30  | New York |
| Bob    | 25  | London   |
| Carol  | 28  | Paris    |
"""

chunks = chunker.chunk(table)
# Each chunk is a valid markdown table with header preserved
```

**Parameters:**

- `tokenizer` — `"row"` (chunk by rows), `"character"`, or any tokenizer. Default: `"row"`.
- `chunk_size` — Maximum rows per chunk (if `"row"`) or tokens/characters. Default: `3`.

**Best for**: Tabular data in RAG and LLM pipelines, preserving table structure.

## TeraflopAIChunker

Segments text using the TeraflopAI Segmentation API. Especially useful for domain-specific segmentation (legal documents). Requires `[teraflopai]` install.

```python
from chonkie import TeraflopAIChunker

# Using API key
chunker = TeraflopAIChunker(api_key="your_api_key")

# Or from environment variable
import os
os.environ["TERAFLOPAI_API_KEY"] = "your_api_key"
chunker = TeraflopAIChunker()

# With custom URL
chunker = TeraflopAIChunker(
    api_key="your_api_key",
    url="https://api.segmentation.teraflopai.com/v1/segmentation/free"
)
```

**Parameters:**

- `client` — Existing TeraflopAI client instance (overrides url/api_key).
- `url` — API endpoint URL. Default: `"https://api.segmentation.teraflopai.com/v1/segmentation/free"`.
- `api_key` — API key (or read from `TERAFLOPAI_API_KEY` env var).
- `tokenizer` — Tokenizer for computing token counts. Default: `"character"`.

**Best for**: Domain-specific segmentation, legal documents. Requires internet connection and valid API key.

## SDPMChunker (Deprecated)

The legacy Semantic Dual-Phase Merge chunker is deprecated in v1.6.x. Use `SemanticChunker` with `skip_window=1` or higher for equivalent behavior.

## Chunker Availability Matrix

**Default install** (`pip install chonkie`):
TokenChunker, FastChunker, SentenceChunker, RecursiveChunker, TableChunker

**With `[semantic]`**:
+ SemanticChunker, LateChunker, NeuralChunker, SlumberChunker

**With `[code]`**:
+ CodeChunker

**JavaScript SDK** (`@chonkiejs/core`):
TokenChunker, SentenceChunker, RecursiveChunker, FastChunker, TableChunker, SemanticChunker, CodeChunker

**API server**:
All except FastChunker
