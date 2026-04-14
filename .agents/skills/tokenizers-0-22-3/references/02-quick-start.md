# Quick Start Guide

Learn the basics of training and using tokenizers with practical examples.

## Training Your First Tokenizer

### Step 1: Prepare Training Data

Tokenizers can be trained from text files or Python iterators:

```python
# Using text files (simplest)
files = ["train_data.txt", "more_data.txt"]

# Using a list of strings
training_data = [
    "The quick brown fox jumps over the lazy dog.",
    "Natural language processing is fascinating.",
    "Machine learning models need good tokenization."
]

# Using an iterator (memory efficient for large datasets)
def text_iterator(file_paths):
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                yield line.strip()
```

### Step 2: Initialize Tokenizer and Trainer

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace

# Create tokenizer with BPE model
tokenizer = Tokenizer(BPE(unk_token="[UNK]"))

# Set pre-tokenizer to split on whitespace
tokenizer.pre_tokenizer = Whitespace()

# Configure trainer
trainer = BpeTrainer(
    vocab_size=30000,              # Target vocabulary size
    min_frequency=2,               # Minimum token frequency
    special_tokens=[               # Reserved tokens (inserted at start of vocab)
        "[UNK]",                   # ID 0: Unknown token
        "[CLS]",                   # ID 1: Classification token
        "[SEP]",                   # ID 2: Separator token
        "[PAD]",                   # ID 3: Padding token
        "[MASK]"                   # ID 4: Mask token (for MLM tasks)
    ]
)
```

### Step 3: Train the Tokenizer

```python
# Train from files
tokenizer.train(files=["wiki.train.raw", "wiki.valid.raw"], trainer=trainer)

# Train from iterator
tokenizer.train(files=text_iterator(["large_file1.txt", "large_file2.txt"]), trainer=trainer)

# Training time varies by corpus size:
# - 50MB text: ~5 seconds
# - 500MB text: ~30 seconds
# - 5GB text: ~5 minutes
```

### Step 4: Save the Tokenizer

```python
# Save to JSON file (portable format)
tokenizer.save("my_tokenizer.json")

# Save with model-specific configuration
tokenizer.save_pretrained("./my_tokenizer_model/")
# Creates: my_tokenizer_model/tokenizer.json and config files
```

## Using a Trained Tokenizer

### Loading a Tokenizer

```python
from tokenizers import Tokenizer

# Load from JSON file
tokenizer = Tokenizer.from_file("my_tokenizer.json")

# Load from pretrained model (requires transformers)
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
```

### Basic Encoding

```python
# Encode single text
encoding = tokenizer.encode("Hello, world!")

print(encoding.tokens)  # ["Hello", ",", "world", "!"]
print(encoding.ids)     # [12345, 67, 8901, 23]
print(encoding.offsets) # [(0, 5), (5, 6), (7, 12), (12, 13)]

# Access original text using offsets
original = "Hello, world!"
for token, (start, end) in zip(encoding.tokens, encoding.offsets):
    print(f"{token} -> {original[start:end]}")
```

### Encoding Text Pairs

```python
# Encode sequence pair (e.g., question-answering)
encoding = tokenizer.encode("What is the capital of France?", "Paris")

print(encoding.tokens)   # Tokens from both sequences
print(encoding.type_ids) # [0, 0, 0, ...] for first seq, [1, 1, 1, ...] for second
```

### Batch Encoding

```python
# Encode multiple texts efficiently
texts = [
    "First sentence to encode.",
    "Second sentence here.",
    "Third one too."
]

encodings = tokenizer.encode_batch(texts)

for i, encoding in enumerate(encodings):
    print(f"Text {i}: {encoding.tokens}")

# Batch encoding is 10-50x faster than looping over encode()
```

### Padding and Truncation

```python
# Enable automatic padding
tokenizer.enable_padding(
    length=128,              # Target sequence length
    pad_id=3,                # ID of padding token
    pad_token="[PAD]"        # Padding token string
)

# Enable truncation
tokenizer.enable_truncation(
    length=512,                          # Maximum length
    strategy="longest_first"             # Truncate longest sequence first in pairs
)

# Now batch encoding applies padding/truncation automatically
encodings = tokenizer.encode_batch([
    "Short text",
    "This is a much longer text that will be padded or truncated"
])

print(encodings[0].attention_mask)  # Shows which tokens are real vs padding
```

## Working with Encoded Output

### Extracting Token Information

```python
encoding = tokenizer.encode("Hello, world!")

# Get token strings
tokens = encoding.tokens

# Get token IDs (vocabulary indices)
ids = encoding.ids

# Get attention mask (1 for real tokens, 0 for padding)
attention_mask = encoding.attention_mask

# Get type IDs (0 for first sequence, 1 for second)
type_ids = encoding.type_ids

# Get character offsets in original text
offsets = encoding.offsets
```

### Decoding Tokens Back to Text

```python
# Decode IDs back to string
text = tokenizer.decode([12345, 67, 8901])
print(text)  # "Hello,world" (may need post-processing)

# Decode with skipping special tokens
text = tokenizer.decode([12345, 67, 8901], skip_special_tokens=True)
```

### Handling Special Tokens

```python
# Check if token is special
print(tokenizer.token_to_id("[UNK]"))  # Returns ID of [UNK]
print(tokenizer.id_to_token(0))        # Returns "[UNK]"

# Get all special tokens
special_tokens = tokenizer.get_special_tokens()
for token in special_tokens:
    print(f"{token['id']}: {token['content']}")
```

## Common Tokenizer Configurations

### BERT-style Configuration

```python
from tokenizers import Tokenizers
from tokenizers.models import WordPiece
from tokenizers.trainers import WordPieceTrainer
from tokenizers.pre_tokenizers import BertPreTokenizer
from tokenizers.processors import TemplateProcessing

tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))
tokenizer.pre_tokenizer = BertPreTokenizer()
tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[
        ("[CLS]", tokenizer.token_to_id("[CLS]")),
        ("[SEP]", tokenizer.token_to_id("[SEP]"))
    ]
)

trainer = WordPieceTrainer(
    vocab_size=30522,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"]
)
```

### GPT-2 / ByteLevel Configuration

```python
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder

tokenizer = Tokenizer(BPE())
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=True)
tokenizer.decoder = ByteLevelDecoder(add_prefix_space=True)

trainer = BpeTrainer(
    vocab_size=50257,
    special_tokens=["<|endoftext|>"]
)
```

### RoBERTa Configuration

```python
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder
from tokenizers.processors import TemplateProcessing

tokenizer = Tokenizer(BPE())
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=True)
tokenizer.decoder = ByteLevelDecoder(add_prefix_space=True)
tokenizer.post_processor = TemplateProcessing(
    single="<s> $A </s>",
    pair="<s> $A </s> $B:1 </s>:1",
    special_tokens=[
        ("<s>", tokenizer.token_to_id("<s>")),
        ("</s>", tokenizer.token_to_id("</s>"))
    ]
)

trainer = BpeTrainer(
    vocab_size=50265,
    special_tokens=["<s>", "</s>", "<pad>"]
)
```

## Performance Tips

### Batch Processing

```python
# ❌ Slow: Loop over encode()
for text in texts:
    encoding = tokenizer.encode(text)

# ✅ Fast: Use encode_batch()
encodings = tokenizer.encode_batch(texts)
```

### Parallel Training

```python
from multiprocessing import Pool

def train_on_shard(args):
    files, trainer = args
    tokenizer = Tokenizer(BPE())
    tokenizer.train(files=files, trainer=trainer)
    return tokenizer

# Split data into shards and train in parallel
shards = [["part1.txt"], ["part2.txt"], ["part3.txt"]]
with Pool(4) as pool:
    tokenizers = pool.map(train_on_shard, [(s, trainer) for s in shards])
```

### Memory-Efficient Training

```python
# For very large corpora (>10GB), use iterators
def batch_iterator(file_paths, batch_size=1024):
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            batch = []
            for line in f:
                batch.append(line)
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch

tokenizer.train(files=batch_iterator(large_files), trainer=trainer)
```

## Debugging Tips

### Visualize Tokenization

```python
from tokenizers import EncodingVisualizer

visualizer = EncodingVisualizer()
visualization = visualizer(tokenizer.encode("Hello, world!"))
print(visualization)
# Shows: ┌────────┬─────────┐
#        │ Token  │ Offset  │
#        ├────────┼─────────┤
#        │ Hello  │ 0-5     │
#        │ ,      │ 5-6     │
#        │ world  │ 7-12    │
#        │ !      │ 12-13   │
#        └────────┴─────────┘
```

### Check Vocabulary Statistics

```python
# Get vocabulary size
vocab_size = tokenizer.get_vocab_size()
print(f"Vocabulary size: {vocab_size}")

# Get most frequent tokens
freqs = tokenizer.get_vocab(return_special_tokens=True)
most_common = sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:20]
for token, id_ in most_common:
    print(f"{token}: {id_}")
```

### Inspect Tokenizer Configuration

```python
# Get tokenizer as JSON config
config = tokenizer.to_json()
print(config[:500])  # First 500 chars of config

# Check individual components
print(f"Model: {tokenizer.model}")
print(f"Pre-tokenizer: {tokenizer.pre_tokenizer}")
print(f"Normalizer: {tokenizer.normalizer}")
print(f"Post-processor: {tokenizer.post_processor}")
print(f"Decoder: {tokenizer.decoder}")
```

## Next Steps

After mastering the basics, explore:
- [Pipeline Components](references/03-pipeline-components.md) - Deep dive into normalizers, pre-tokenizers, models
- [Training Guide](references/05-training-guide.md) - Advanced training strategies and optimization
- [Models Reference](references/04-models.md) - Complete guide to BPE, WordPiece, Unigram, and other algorithms
