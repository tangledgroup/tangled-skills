# Models Reference

Complete guide to tokenization models: BPE, WordPiece, Unigram, ByteLevel, WordLevel, SentencePiece, and LLaMA.

## Model Overview

The model is the core component that performs actual tokenization. Each model implements a different algorithm for converting pre-tokenized units into vocabulary tokens.

| Model | Best For | Vocabulary Size | Key Feature |
|-------|----------|-----------------|-------------|
| BPE | General purpose | 30K-50K | Incremental merging, robust |
| WordPiece | BERT-style models | 30K-35K | Prefix-based subword splitting |
| Unigram | T5, modern transformers | 32K-64K | Probabilistic, better quality |
| ByteLevel | GPT-2, small vocab | 256-50K | No unknown tokens, byte-based |
| WordLevel | Small domains | 10K-50K | Whole-word tokenization |
| SentencePiece | Multilingual | 8K-50K | Character-level, language-agnostic |
| LLaMA | LLaMA models | 32K | Specialized for LLaMA architecture |

## Byte-Pair Encoding (BPE)

BPE iteratively merges the most frequent token pairs until reaching target vocabulary size.

### Basic Usage

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE

# Initialize with BPE model
tokenizer = Tokenizer(BPE(unk_token="[UNK]"))

# Configure and train
from tokenizers.trainers import BpeTrainer
trainer = BpeTrainer(
    vocab_size=30000,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"]
)
tokenizer.train(files=["train.txt"], trainer=trainer)
```

### BPE Configuration Options

```python
# Standard BPE
BPE(unk_token="[UNK]")

# With continuing subword marker (like WordPiece)
BPE(
    unk_token="[UNK]",
    continuing_subword_prefix="",      # No prefix for continued tokens
    end_of_subword_suffix=""           # No suffix for end of subword
)

# WordPiece-style BPE (## prefix for continuations)
BPE(
    unk_token="[UNK]",
    continuing_subword_prefix="##",    # Prefix for non-initial subwords
    end_of_subword_suffix=""
)
```

### BPE Training Options

```python
from tokenizers.trainers import BpeTrainer

trainer = BpeTrainer(
    vocab_size=30000,                  # Target vocabulary size
    min_frequency=2,                   # Minimum token frequency (0 = ignore)
    initial_alphabet=None,             # Use all bytes by default (256 chars)
    special_tokens=["[UNK]", "[PAD]"], # Reserved tokens
    show_progress=True,                # Show training progress bar
    limit_alphabet=300,                # Limit initial alphabet size
    end_of_word_suffix="</w>",         # Mark end of word
    continue_subword_factor=1.0        # Weight for continuing subwords
)
```

**Training algorithm**:
1. Start with all characters in text as initial vocabulary
2. Find most frequent adjacent token pair
3. Merge pair into new token
4. Repeat until vocab_size reached or no more merges possible

## WordPiece

WordPiece is Google's variant of BPE used in BERT, using "##" prefix for continued subwords.

### Basic Usage

```python
from tokenizers import Tokenizer
from tokenizers.models import WordPiece

tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))

from tokenizers.trainers import WordPieceTrainer
trainer = WordPieceTrainer(
    vocab_size=30522,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"]
)
```

### WordPiece Configuration

```python
WordPiece(
    unk_token="[UNK]",
    continuing_subword_prefix="##",    # Required for WordPiece behavior
    max_input_chars_per_word=100,      # Maximum characters per word before splitting
    unk_id=0                           # ID of unknown token
)
```

### WordPiece vs BPE

| Feature | BPE | WordPiece |
|---------|-----|-----------|
| Subword marker | None (configurable) | "##" prefix |
| Merge strategy | Frequency-based | Probability-based |
| Unknown handling | Can have no UNK | Requires UNK token |
| Use cases | General purpose | BERT, DistilBERT |

**Example**: "playing" → ["play", "##ing"] in WordPiece

## Unigram

Unigram uses probabilistic subword segmentation, often producing higher-quality tokenization than BPE.

### Basic Usage

```python
from tokenizers import Tokenizer
from tokenizers.models import Unigram

tokenizer = Tokenizer(Unigram())

from tokenizers.trainers import UnigramTrainer
trainer = UnigramTrainer(
    vocab_size=32000,
    initial_alphabet=None,  # Use Unicode characters
    special_tokens=["<unk>", "<s>", "</s>"]
)
```

### Unigram Training Options

```python
from tokenizers.trainers import UnigramTrainer

trainer = UnigramTrainer(
    vocab_size=32000,                    # Target vocabulary size
    min_frequency=2,                     # Minimum frequency for keeping tokens
    initial_alphabet=None,               # Unicode characters by default
    special_tokens=["<unk>", "<s>"],     # Reserved tokens
    show_progress=True,
    num_iterations=60,                   # Number of pruning iterations
    shuffle=True                         # Shuffle during training
)
```

### Unigram Configuration

```python
Unigram(
    unk_token="<unk>",
    blank_token="",                      # Blank token for joining
    tie_word_piece=False,                # Don't tie word pieces
    drop_unknowns=False                  # Keep unknown tokens in output
)
```

**Training algorithm**:
1. Start with large vocabulary (all possible subwords)
2. Iteratively prune least useful tokens
3. Use forward-backward algorithm to compute token probabilities
4. Select best segmentation based on probability

## ByteLevel

ByteLevel operates at byte level, enabling small vocabularies and no unknown tokens.

### Basic Usage

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE  # ByteLevel is a pre-tokenizer, not model

# ByteLevel is typically used with BPE model
tokenizer = Tokenizer(BPE())

from tokenizers.pre_tokenizers import ByteLevel
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=True)

from tokenizers.decoders import ByteLevel as ByteLevelDecoder
tokenizer.decoder = ByteLevelDecoder(add_prefix_space=True)
```

### Byte-Level Tokenization Benefits

1. **No unknown tokens**: All Unicode can be represented as bytes
2. **Small vocabulary**: Start with 256 base tokens (all byte values)
3. **Robust**: Handles typos and rare characters gracefully
4. **Used by**: GPT-2, RoBERTa, DistilGPT2

### ByteLevel Configuration

```python
from tokenizers.pre_tokenizers import ByteLevel

ByteLevel(
    add_prefix_space=False,              # Add space before each word
    use_regex=True,                      # Use regex for splitting
    byte_fallback=True                   # Fallback to bytes on decode error
)
```

**Example**: "Hello" with `add_prefix_space=True` → b"\xc3\x85Hello" → encoded as byte tokens

## WordLevel

WordLevel tokenizes at word level, suitable for small domains with controlled vocabulary.

### Basic Usage

```python
from tokenizers import Tokenizer
from tokenizers.models import WordLevel

tokenizer = Tokenizer(WordLevel(unk_token="<unk>"))

from tokenizers.trainers import WordLevelTrainer
trainer = WordLevelTrainer(
    special_tokens=["<unk>", "<s>", "</s>"]
)
```

### WordLevel Configuration

```python
WordLevel(
    unk_token="<unk>",
    unk_id=0,
    pad_token=None,                      # Optional padding token
    pad_id=None,
    cls_token=None,                      # Optional classification token
    cls_id=None,
    sep_token=None,                      # Optional separator token
    sep_id=None
)
```

**Use cases**: Small domains, controlled vocabularies, educational purposes

## SentencePiece

SentencePiece operates at character level, making it language-agnostic and suitable for multilingual models.

### Basic Usage

```python
from tokenizers import Tokenizer
from tokenizers.models import SentencePiece

tokenizer = Tokenizer(SentencePiece())

from tokenizers.trainers import SentencePieceTrainer
trainer = SentencePieceTrainer(
    vocab_size=8000,
    special_tokens=["<unk>", "<s>", "</s>"]
)
```

### SentencePiece Training Options

```python
from tokenizers.trainers import SentencePieceTrainer

trainer = SentencePieceTrainer(
    vocab_size=8000,
    model_type="bpe",                   # "bpe" or "unigram"
    max_sentence_length=1024,           # Maximum sentence length
    input_formatter="{{txt}}",          # Input text formatter
    pad_id=1,                           # Padding token ID
    bos_id=0,                           # Beginning-of-sequence ID
    eos_id=2,                           # End-of-sequence ID
    unk_id=3                            # Unknown token ID
)
```

### SentencePiece Features

- **Language-agnostic**: Works without language-specific tokenization
- **Character-level**: Handles any Unicode character
- **Multilingual**: Single model for multiple languages
- **Used by**: mBART, T5 (variants), many multilingual models

## LLaMA Tokenizer

Specialized tokenizer for LLaMA architecture using ByteLevel with BPE.

### Basic Usage

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder

# LLaMA uses ByteLevel pre-tokenization with BPE model
tokenizer = Tokenizer(BPE())
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=True)
tokenizer.decoder = ByteLevelDecoder(add_prefix_space=True)

# Load pretrained LLaMA tokenizer
from transformers import AutoTokenizer
llama_tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

### LLaMA Tokenization Characteristics

- **Vocabulary size**: 32,000 tokens
- **Byte-level encoding**: No unknown tokens
- **Prefix space**: Each word gets prefix space during tokenization
- **Special tokens**: `<s>`, `</s>`, `<unk>`

## Model Comparison

### Training Speed

| Model | Training Time (500MB) | Memory Usage |
|-------|----------------------|--------------|
| BPE | ~30 seconds | Low |
| WordPiece | ~35 seconds | Low |
| Unigram | ~2 minutes | Medium |
| WordLevel | ~10 seconds | Very Low |
| SentencePiece | ~45 seconds | Medium |

### Tokenization Quality

| Model | Out-of-Vocabulary | Subword Quality | Language Support |
|-------|-------------------|-----------------|------------------|
| BPE | Low (with UNK) | Good | Excellent |
| WordPiece | Low (with UNK) | Good | Excellent |
| Unigram | Low (with UNK) | Best | Excellent |
| ByteLevel | None | Very Good | Universal |
| WordLevel | High | N/A | Language-specific |
| SentencePiece | Low | Very Good | Universal |

### Use Case Recommendations

**For new projects**:
- **General purpose**: BPE (best balance of speed and quality)
- **High quality**: Unigram (better tokenization, slower training)
- **Multilingual**: SentencePiece or ByteLevel
- **Small vocabulary**: ByteLevel (256 base tokens)

**For compatibility**:
- **BERT models**: WordPiece
- **GPT-2/RoBERTa**: BPE + ByteLevel
- **T5**: Unigram
- **LLaMA**: BPE + ByteLevel with prefix space

## Custom Model Training Example

### Training BPE from Scratch

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace

# 1. Initialize tokenizer
tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
tokenizer.pre_tokenizer = Whitespace()

# 2. Configure trainer
trainer = BpeTrainer(
    vocab_size=30000,
    min_frequency=5,                    # Only keep tokens appearing ≥5 times
    special_tokens=["[UNK]", "[PAD]", "[CLS]", "[SEP]", "[MASK]"],
    show_progress=True
)

# 3. Train on corpus
tokenizer.train(files=["corpus/train.txt", "corpus/valid.txt"], trainer=trainer)

# 4. Save tokenizer
tokenizer.save("custom_bpe_tokenizer.json")

# 5. Verify vocabulary size
print(f"Vocabulary size: {tokenizer.get_vocab_size()}")
```

### Training Unigram with Custom Alphabet

```python
from tokenizers import Tokenizer
from tokenizers.models import Unigram
from tokenizers.trainers import UnigramTrainer
from tokenizers.pre_tokenizers import Whitespace

# Create custom initial alphabet (ASCII only)
initial_alphabet = [chr(i) for i in range(32, 127)] + ["\n", "\t"]

tokenizer = Tokenizer(Unigram())
tokenizer.pre_tokenizer = Whitespace()

trainer = UnigramTrainer(
    vocab_size=32000,
    initial_alphabet=initial_alphabet,
    special_tokens=["<unk>", "<s>", "</s>"],
    num_iterations=60
)

tokenizer.train(files=["train.txt"], trainer=trainer)
```

## Loading Pretrained Models

### From Hugging Face Hub

```python
from transformers import AutoTokenizer

# Load BERT tokenizer (WordPiece)
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Load GPT-2 tokenizer (BPE + ByteLevel)
gpt2_tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Load T5 tokenizer (Unigram)
t5_tokenizer = AutoTokenizer.from_pretrained("t5-base")

# Load LLaMA tokenizer
llama_tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

### From Local Files

```python
from tokenizers import Tokenizer

# Load from JSON file
tokenizer = Tokenizer.from_file("path/to/tokenizer.json")

# Load from directory (with config files)
tokenizer = Tokenizer.from_pretrained("./path/to/tokenizer/dir")
```

## Next Steps

- [Training Guide](references/05-training-guide.md) - Advanced training strategies
- [Special Tokens](references/06-special-tokens.md) - Managing special tokens across models
- [API Reference](references/07-api-reference.md) - Complete API documentation
