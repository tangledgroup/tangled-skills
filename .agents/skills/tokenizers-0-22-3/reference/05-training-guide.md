# Training Guide

Advanced strategies for training tokenizers efficiently on various data sources and configurations.

## Training Data Preparation

### File-Based Training

Most straightforward approach - provide list of text files:

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer

tokenizer = Tokenizer(BPE())
trainer = BpeTrainer(vocab_size=30000)

# Single file
tokenizer.train(files=["corpus.txt"], trainer=trainer)

# Multiple files
tokenizer.train(
    files=[
        "train_part1.txt",
        "train_part2.txt",
        "validation.txt"
    ],
    trainer=trainer
)

# Files matching pattern (use glob)
import glob
files = glob.glob("data/*.txt")
tokenizer.train(files=files, trainer=trainer)
```

### Iterator-Based Training

For memory-efficient training on large corpora:

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer

def file_iterator(file_paths, batch_size=1024):
    """Yield batches of text from files."""
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            batch = []
            for line in f:
                batch.append(line.strip())
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch

tokenizer = Tokenizer(BPE())
trainer = BpeTrainer(vocab_size=30000)

# Train from iterator
tokenizer.train(
    files=file_iterator(["large1.txt", "large2.txt"]),
    trainer=trainer
)
```

### Generator-Based Training

Using Python generators for on-the-fly data processing:

```python
def text_generator(dataset_func, batch_size=512):
    """Generator that batches results from a dataset function."""
    batch = []
    for item in dataset_func():
        batch.append(item["text"])
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

# Example with Hugging Face Datasets
from datasets import load_dataset

dataset = load_dataset("wikitext", "wikitext-103-raw", split="train")

def wikitext_iterator():
    for item in dataset:
        yield item["text"]

tokenizer.train(
    files=text_generator(wikitext_iterator),
    trainer=trainer
)
```

### Gzip File Training

Direct training from compressed files:

```python
import gzip

def gzip_iterator(file_paths):
    """Iterate over gzip-compressed files."""
    for file_path in file_paths:
        with gzip.open(file_path, "rt", encoding="utf-8") as f:
            for line in f:
                yield line.strip()

tokenizer.train(
    files=gzip_iterator(["corpus1.txt.gz", "corpus2.txt.gz"]),
    trainer=trainer
)
```

## Training Configuration

### Vocabulary Size Selection

Choose vocabulary size based on use case:

| Use Case | Recommended Size | Rationale |
|----------|-----------------|-----------|
| General NLP | 30,000-32,000 | Good balance of coverage and efficiency |
| Large Language Models | 50,000-64,000 | Better coverage for diverse domains |
| Small/Medium Models | 16,000-24,000 | Efficient inference, adequate coverage |
| Multilingual | 25,000-32,000 per language | Balance across languages |
| Domain-Specific | 10,000-20,000 | Focused vocabulary reduces noise |

```python
trainer = BpeTrainer(
    vocab_size=30000,  # Adjust based on use case
    min_frequency=2    # Minimum token frequency
)
```

### Minimum Frequency Setting

Control vocabulary quality with `min_frequency`:

```python
# Strict: Only common tokens
trainer = BpeTrainer(vocab_size=30000, min_frequency=10)

# Moderate: Balance coverage and quality
trainer = BpeTrainer(vocab_size=30000, min_frequency=2)

# Permissive: Include rare tokens
trainer = BpeTrainer(vocab_size=30000, min_frequency=0)  # Default
```

**Effect**: Higher `min_frequency` reduces vocabulary size but increases quality.

### Special Tokens Configuration

Order matters - special tokens are assigned IDs in order specified:

```python
trainer = BpeTrainer(
    special_tokens=[
        "[UNK]",   # ID 0: Unknown token (required for most models)
        "[PAD]",   # ID 1: Padding token
        "[CLS]",   # ID 2: Classification token
        "[SEP]",   # ID 3: Separator token
        "[MASK]"   # ID 4: Mask token (for MLM tasks)
    ]
)

# Check token IDs after training
print(tokenizer.token_to_id("[UNK]"))  # 0
print(tokenizer.token_to_id("[PAD]"))  # 1
```

### Initial Alphabet Control

Control the starting vocabulary for BPE/Unigram:

```python
# Default: All Unicode characters (large initial vocab)
trainer = BpeTrainer(vocab_size=30000)

# Limited: ASCII only (faster training, smaller model)
import string
initial_alphabet = list(string.printable) + ["\n", "\t"]
trainer = BpeTrainer(
    vocab_size=30000,
    initial_alphabet=initial_alphabet
)

# Custom: Domain-specific characters
initial_alphabet = [chr(i) for i in range(256)]  # Extended ASCII
trainer = BpeTrainer(
    vocab_size=30000,
    initial_alphabet=initial_alphabet
)
```

## Advanced Training Strategies

### Progressive Training

Train in stages to build vocabulary incrementally:

```python
# Stage 1: Train base tokenizer on general corpus
base_tokenizer = Tokenizer(BPE())
base_trainer = BpeTrainer(
    vocab_size=20000,
    special_tokens=["[UNK]", "[PAD]"]
)
base_tokenizer.train(files=["general_corpus.txt"], trainer=base_trainer)

# Stage 2: Continue training on domain-specific data
domain_tokenizer = base_tokenizer.clone()
domain_trainer = BpeTrainer(
    vocab_size=30000,  # Increase vocabulary
    special_tokens=["[UNK]", "[PAD]", "[CLS]", "[SEP]"]
)
domain_tokenizer.train(files=["domain_corpus.txt"], trainer=domain_trainer)
```

### Multi-Corpus Training

Train on multiple domains with balanced sampling:

```python
def multi_corpus_iterator(corpus_paths, samples_per_corpus=10000):
    """Sample equally from multiple corpora."""
    for corpus_path in corpus_paths:
        count = 0
        with open(corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                if count >= samples_per_corpus:
                    break
                yield line.strip()
                count += 1

# Train on balanced mix of domains
tokenizer.train(
    files=multi_corpus_iterator([
        "news_corpus.txt",
        "technical_docs.txt",
        "social_media.txt"
    ]),
    trainer=trainer
)
```

### Incremental Vocabulary Expansion

Add tokens to existing vocabulary:

```python
# Load existing tokenizer
tokenizer = Tokenizer.from_file("base_tokenizer.json")

# Get current vocabulary
current_vocab = tokenizer.get_vocab()
print(f"Current vocab size: {len(current_vocab)}")

# Train new tokenizer with larger vocabulary
new_tokenizer = Tokenizer(BPE())
new_trainer = BpeTrainer(
    vocab_size=50000,  # Larger than base
    special_tokens=["[UNK]", "[PAD]"]
)
new_tokenizer.train(files=["additional_corpus.txt"], trainer=new_trainer)

# Merge vocabularies (keep all tokens from both)
merged_vocab = {**current_vocab, **new_tokenizer.get_vocab()}

# Create merged tokenizer
merged_tokenizer = Tokenizer(BPE())
merged_tokenizer.vocab = merged_vocab
merged_tokenizer.save("merged_tokenizer.json")
```

## Training Performance Optimization

### Parallel Training

Train multiple tokenizers in parallel for hyperparameter tuning:

```python
from multiprocessing import Pool
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer

def train_with_config(args):
    vocab_size, min_freq, files = args
    tokenizer = Tokenizer(BPE())
    trainer = BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=min_freq,
        special_tokens=["[UNK]", "[PAD]"]
    )
    tokenizer.train(files=files, trainer=trainer)
    return vocab_size, min_freq, tokenizer.get_vocab_size()

# Train with different configurations
configs = [
    (20000, 2, ["corpus.txt"]),
    (30000, 2, ["corpus.txt"]),
    (30000, 5, ["corpus.txt"]),
    (40000, 2, ["corpus.txt"])
]

with Pool(4) as pool:
    results = pool.map(train_with_config, configs)

for vocab_size, min_freq, actual_size in results:
    print(f"Config (vocab={vocab_size}, min_freq={min_freq}): {actual_size} tokens")
```

### Batch Size Optimization

Adjust batch size for memory vs speed tradeoff:

```python
def batched_file_iterator(file_path, batch_size=8192):
    """Optimized iterator with configurable batch size."""
    with open(file_path, "r", encoding="utf-8") as f:
        batch = []
        for line in f:
            batch.append(line.strip())
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

# Larger batches = faster training but more memory
tokenizer.train(
    files=batched_file_iterator("large_corpus.txt", batch_size=16384),
    trainer=trainer
)
```

### Progress Tracking

Monitor training progress:

```python
trainer = BpeTrainer(
    vocab_size=30000,
    show_progress=True  # Enable progress bar
)

# Training will show:
# Training tokenizer:   0%|          | 0/1000000 [00:00<?, ?examples/s]
# Training tokenizer: 100%|██████████| 1000000/1000000 [00:30<00:00, 33333ex/s]
```

## Training Validation

### Vocabulary Quality Checks

After training, validate vocabulary quality:

```python
# Check vocabulary size
vocab_size = tokenizer.get_vocab_size()
print(f"Vocabulary size: {vocab_size}")

# Check most frequent tokens
vocab = tokenizer.get_vocab()
most_common = sorted(vocab.items(), key=lambda x: x[1], reverse=True)[:20]
print("Most common tokens:")
for token, id_ in most_common:
    print(f"  {id_}: {repr(token)}")

# Check for unexpected tokens
for token, id_ in vocab.items():
    if any(c.isspace() for c in token):  # Tokens with whitespace
        print(f"Warning: Token contains whitespace: {repr(token)}")
```

### Coverage Testing

Test vocabulary coverage on held-out data:

```python
def calculate_coverage(tokenizer, test_file, sample_size=10000):
    """Calculate what percentage of test data is covered by vocabulary."""
    vocab_set = set(tokenizer.get_vocab().keys())
    
    with open(test_file, "r", encoding="utf-8") as f:
        lines = [f.readline() for _ in range(sample_size)]
    
    total_chars = 0
    covered_chars = 0
    
    for line in lines:
        encoding = tokenizer.encode(line)
        for token in encoding.tokens:
            if token in vocab_set or token == "[UNK]":
                covered_chars += len(token)
            total_chars += len(token)
    
    return covered_chars / total_chars if total_chars > 0 else 0

coverage = calculate_coverage(tokenizer, "test_corpus.txt")
print(f"Vocabulary coverage: {coverage:.2%}")
```

### Tokenization Consistency

Verify tokenization is consistent across runs:

```python
def test_consistency(tokenizer, test_sentences):
    """Check that tokenization is deterministic."""
    results = []
    for _ in range(3):  # Run multiple times
        encodings = tokenizer.encode_batch(test_sentences)
        results.append([tuple(e.tokens) for e in encodings])
    
    # All runs should produce identical results
    assert all(r == results[0] for r in results), "Tokenization is not consistent!"
    print("✓ Tokenization is deterministic")

test_sentences = [
    "Hello, world!",
    "This is a test sentence.",
    "Special chars: @#$%"
]
test_consistency(tokenizer, test_sentences)
```

## Troubleshooting Training Issues

### Memory Errors During Training

**Problem**: `MemoryError` when training on large corpus.

**Solution**: Use iterator-based training with smaller batches:

```python
def memory_efficient_iterator(file_paths, batch_size=1024):
    """Process files in small batches to reduce memory usage."""
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            batch = []
            for line in f:
                batch.append(line)
                if len(batch) >= batch_size:
                    yield batch
                    del batch  # Explicitly free memory
                    batch = []
            if batch:
                yield batch
                del batch

tokenizer.train(
    files=memory_efficient_iterator(large_files, batch_size=512),
    trainer=trainer
)
```

### Training Takes Too Long

**Problem**: Training takes hours instead of minutes.

**Solutions**:
1. Reduce vocabulary size
2. Increase minimum frequency
3. Use smaller initial alphabet
4. Enable progress tracking to identify bottlenecks

```python
trainer = BpeTrainer(
    vocab_size=20000,        # Reduced from 50000
    min_frequency=5,         # Increased from 2
    initial_alphabet=[chr(i) for i in range(256)],  # ASCII only
    show_progress=True       # Monitor progress
)
```

### Vocabulary Contains Unexpected Tokens

**Problem**: Vocabulary includes tokens with whitespace or special characters.

**Solution**: Adjust pre-tokenizer configuration:

```python
from tokenizers.pre_tokenizers import Whitespace, BertPreTokenizer

# Ensure proper pre-tokenization
tokenizer.pre_tokenizer = Whitespace()  # Split on whitespace before training

# For BERT-style tokenization
tokenizer.pre_tokenizer = BertPreTokenizer()
```

### Low Vocabulary Coverage

**Problem**: High percentage of [UNK] tokens during inference.

**Solution**: Increase vocabulary size or reduce minimum frequency:

```python
trainer = BpeTrainer(
    vocab_size=40000,        # Increased from 30000
    min_frequency=1          # Reduced from 5
)
```

## Next Steps

- [Special Tokens](references/06-special-tokens.md) - Managing special tokens in trained tokenizers
- [API Reference](references/07-api-reference.md) - Complete API documentation for trainers and models
