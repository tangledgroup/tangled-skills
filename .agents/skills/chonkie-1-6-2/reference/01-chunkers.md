# Chunkers

All chunkers share a consistent interface:

- `chunk(text)` — chunk a single text
- `chunk_batch(texts)` — chunk multiple texts (Python only)
- `chunk_document(doc)` — chunk a Document object
- `__call__(text)` — direct callable syntax
- Async variants: `achunk()`, `achunk_batch()`, `achunk_document()`

All return the unified `Chunk` dataclass:

```python
@dataclass
class Chunk:
    text: str
    start_index: int
    end_index: int
    token_count: int
    context: Optional[Context] = None
    embedding: Union[list[float], "np.ndarray", None] = None
```

## TokenChunker

Splits text into fixed-size token chunks with configurable overlap. The simplest and most predictable chunker.

**Installation**: Included in base install.

```python
from chonkie import TokenChunker

chunker = TokenChunker(
    tokenizer="character",   # "character" (default), "word", "byte", or "gpt2"
    chunk_size=2048,         # Max tokens per chunk
    chunk_overlap=128        # Overlap between chunks (int or float for percentage)
)

chunks = chunker("Your text here...")
```

**Use when**: You need consistent, predictable chunk sizes and are working with token-based models.

## FastChunker

SIMD-accelerated byte-based chunking at 100+ GB/s throughput via `chonkie-core` Rust extension. Uses **byte size** limits instead of token counts for extreme performance.

**Installation**: Included in base install (Python only, not available in JS).

```python
from chonkie import FastChunker

chunker = FastChunker(
    chunk_size=4096,          # Target size in BYTES (not tokens)
    delimiters="\n.?",        # Single-byte delimiter characters
    pattern=None,             # Multi-byte pattern (overrides delimiters if set)
    prefix=False,             # Keep delimiter at start of next chunk
    consecutive=False,        # Split at START of consecutive delimiter runs
    forward_fallback=False    # Search forward when no backward delimiter found
)

chunks = chunker("Your text here...")
```

**Use when**: High-throughput pipelines where byte-size limits are acceptable and raw speed is critical.

## SentenceChunker

Splits text at sentence boundaries, grouping sentences into chunks up to a max token size. Maintains semantic completeness at the sentence level.

**Installation**: Included in base install.

```python
from chonkie import SentenceChunker

chunker = SentenceChunker(
    tokenizer="gpt2",
    chunk_size=512,
    chunk_overlap=0,
    min_sentences_per_chunk=1,
    min_characters_per_sentence=24,
    delim=[". ", "! ", "? ", "\n"],
    include_delim="prev"  # "prev", "next", or None
)

chunks = chunker("Your text here...")

# Recipe-based initialization for language-specific splitting
chunker = SentenceChunker.from_recipe(lang="hi")  # Hindi
```

**Use when**: Text is well-formatted with clear sentence boundaries and you want to preserve sentence integrity.

## RecursiveChunker

Recursively splits text using hierarchical rules (delimiters at different levels). Best for long, well-structured documents like books or research papers.

**Installation**: Included in base install. Available in JavaScript too.

```python
from chonkie import RecursiveChunker, RecursiveRules, RecursiveLevel

# Default initialization
chunker = RecursiveChunker(
    tokenizer="character",
    chunk_size=2048,
    rules=RecursiveRules(),
    min_characters_per_chunk=24
)

# Custom rules
rules = RecursiveRules(levels=[
    RecursiveLevel(delimiters=["\n\n"], include_delim="prev"),
    RecursiveLevel(delimiters=["."], include_delim="prev"),
    RecursiveLevel(whitespace=True),
])
chunker = RecursiveChunker(rules=rules, chunk_size=512)

# Recipe-based initialization
chunker = RecursiveChunker.from_recipe("markdown", lang="en")
chunker = RecursiveChunker.from_recipe(lang="ko")  # Korean
```

**RecursiveRules**: A list of `RecursiveLevel` objects defining delimiters and whitespace behavior at each hierarchical level. Delimiters should not include whitespace; set `whitespace=True` for space-based splitting instead.

**Use when**: Documents have well-defined structure with headings, paragraphs, or sections. The go-to general-purpose chunker.

## SemanticChunker

Groups content based on semantic similarity using embeddings. Inspired by Greg Kamradt's work. Includes Savitzky-Golay filtering for smoother boundary detection and skip-window merging for connecting related non-consecutive content.

**Installation**: `pip install "chonkie[semantic]"`

```python
from chonkie import SemanticChunker

chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-32M",  # Default model
    threshold=0.8,                                 # Similarity threshold (0-1)
    chunk_size=2048,                               # Max tokens per chunk
    similarity_window=3,                           # Sentences for similarity calc
    skip_window=0,                                 # Non-consecutive merge window (0=disabled)
    filter_window=5,                               # Savitzky-Golay filter window
    filter_polyorder=3,                            # Polynomial order for filter
    filter_tolerance=0.2,                          # Filter boundary tolerance
    min_sentences_per_chunk=1,
    min_characters_per_sentence=24,
)

chunks = chunker("Your text here...")

# With skip-and-merge for alternating topics
chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-32M",
    threshold=0.65,
    skip_window=2  # Merge similar groups up to 2 apart
)
```

**Key parameters**:
- `threshold`: Lower values create larger, more diverse chunks. Higher values create smaller, more focused chunks.
- `skip_window`: Set to 1+ to merge semantically similar groups that are not consecutive (replaces legacy SDPMChunker).
- Savitzky-Golay filter parameters smooth the similarity signal for better boundary detection.

**Use when**: Preserving topical coherence and context is more important than fixed chunk sizes. Best for documents with multiple distinct topics.

## LateChunker

Embeds text first, then splits it to produce chunks with better embedding quality. Designed for higher recall in RAG applications.

**Installation**: `pip install "chonkie[semantic]"` (requires sentence-transformers)

```python
from chonkie import LateChunker

chunker = LateChunker(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    chunk_size=512,
)

chunks = chunker("Your text here...")
# Each chunk has .embedding populated automatically
```

**Use when**: You need higher-quality chunk embeddings for retrieval. The late chunking approach produces embeddings that better represent the full chunk content.

## CodeChunker

Splits code into structurally meaningful chunks using AST parsing via tree-sitter. Supports 100+ programming languages with auto-detection.

**Installation**: `pip install "chonkie[code]"` (installs tree-sitter, tree-sitter-language-pack, magika)

```python
from chonkie import CodeChunker

# Auto-detect language
chunker = CodeChunker()

# Specify language explicitly
chunker = CodeChunker(language="python", chunk_size=512)

chunks = chunker("def hello():\n    print('world')")
```

**Use when**: Chunking source code files for RAG. Understands function boundaries, class definitions, and code structure.

## NeuralChunker

Uses a fine-tuned BERT-like model for fast, high-quality semantic chunking. Fully neural approach without requiring external embedding APIs.

**Installation**: `pip install "chonkie[neural]"` (installs transformers, torch)

```python
from chonkie import NeuralChunker

chunker = NeuralChunker()
chunks = chunker("Your text here...")
```

**Use when**: You want semantic chunking quality without depending on external embedding models or APIs. Runs entirely locally.

## SlumberChunker

Agentic chunking using generative LLMs via the Genie interface. Produces S-tier chunk quality by leveraging LLM understanding of document structure and semantics.

**Installation**: `pip install "chonkie[genie]"` (requires GEMINI_API_KEY or other LLM API key)

```python
from chonkie import SlumberChunker

chunker = SlumberChunker(verbose=True)
chunks = chunker("Your text here...")
```

**Use when**: Maximum chunk quality is needed and LLM API costs are acceptable. Best for critical documents where chunk boundaries matter significantly.

## TableChunker

Splits large markdown tables into smaller, manageable chunks by row while preserving headers.

**Installation**: Included in base install.

```python
from chonkie import TableChunker

chunker = TableChunker()
chunks = chunker("| Header1 | Header2 |\n|---|---|\n| A | B |\n| C | D |")
```

**Use when**: Processing markdown documents with large tabular data for RAG pipelines.

## TeraflopAIChunker

Segments text using the TeraflopAI Segmentation API. Ideal for domain-specific segmentation such as legal documents.

**Installation**: `pip install "chonkie[all]"` or via API.

```python
from chonkie import TeraflopAIChunker

chunker = TeraflopAIChunker()
chunks = chunker("Legal document text...")
```

**Use when**: Domain-specific segmentation is needed, particularly for legal or highly structured professional documents.

## SDPMChunker (Legacy)

Deprecated as of v1.2.0. Its functionality has been integrated into `SemanticChunker` via the `skip_window` parameter.

```python
# Old way (deprecated)
from chonkie.legacy import SDPMChunker
chunker = SDPMChunker(skip_window=1)

# New way (recommended)
from chonkie import SemanticChunker
chunker = SemanticChunker(skip_window=1)
```
