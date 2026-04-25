# API Reference

Complete API documentation for the tokenizers library v0.22.3.

## Tokenizer Class

Main class for all tokenization operations.

### Constructor

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE

# Initialize with a model
tokenizer = Tokenizer(BPE(unk_token="[UNK]"))

# Initialize empty (add model later)
tokenizer = Tokenizer()
tokenizer.model = BPE()
```

### Core Methods

#### encode()

Encode a single text or text pair.

```python
# Single text
encoding = tokenizer.encode("Hello, world!")

# Text pair
encoding = tokenizer.encode("Question?", "Answer.")

# With options
encoding = tokenizer.encode(
    "Hello",
    pair=None,
    add_special_tokens=True,
    is_pretokenized=False
)
```

**Returns**: `Encoding` object with tokens, ids, offsets, attention_mask, type_ids

#### encode_batch()

Encode multiple texts efficiently.

```python
# List of single texts
encodings = tokenizer.encode_batch(["Text 1", "Text 2", "Text 3"])

# List of text pairs
encodings = tokenizer.encode_batch([
    ("Question 1", "Answer 1"),
    ("Question 2", "Answer 2")
])

# With options
encodings = tokenizer.encode_batch(
    texts,
    is_pretokenized=False,
    add_special_tokens=True
)
```

**Returns**: List of `Encoding` objects

**Performance**: 10-50x faster than looping over `encode()`

#### decode()

Decode token IDs back to text.

```python
# Basic decoding
text = tokenizer.decode([12345, 67, 8901])

# Skip special tokens
text = tokenizer.decode([12345, 0, 8901], skip_special_tokens=True)

# With cleanup (remove artifacts from tokenization)
text = tokenizer.decode(ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
```

**Parameters**:
- `ids`: List of token IDs
- `skip_special_tokens`: Whether to exclude special tokens from output
- `clean_up_tokenization_spaces`: Remove extra spaces added during tokenization

#### save()

Save tokenizer to file.

```python
# Save to JSON file
tokenizer.save("tokenizer.json")

# Save with truncation
tokenizer.save("tokenizer.json", pretty_print=True)
```

#### from_file()

Load tokenizer from file.

```python
tokenizer = Tokenizer.from_file("tokenizer.json")
```

#### from_pretrained()

Load pretrained tokenizer from Hugging Face Hub or local directory.

```python
# From Hugging Face Hub
tokenizer = Tokenizer.from_pretrained("bert-base-uncased")

# From local directory
tokenizer = Tokenizer.from_pretrained("./path/to/tokenizer/")

# With cache control
tokenizer = Tokenizer.from_pretrained(
    "bert-base-uncased",
    cache_dir="./cache"
)
```

### Training Methods

#### train()

Train tokenizer on text files or iterators.

```python
from tokenizers.trainers import BpeTrainer

trainer = BpeTrainer(vocab_size=30000)

# Train from files
tokenizer.train(files=["train.txt", "valid.txt"], trainer=trainer)

# Train from iterator
def text_iterator():
    with open("train.txt") as f:
        for line in f:
            yield line

tokenizer.train(files=text_iterator(), trainer=trainer)
```

#### train_from_file()

Train directly from a single file (convenience method).

```python
trainer = BpeTrainer(vocab_size=30000)
tokenizer.train_from_file("train.txt", trainer=trainer)
```

### Vocabulary Methods

#### get_vocab_size()

Get vocabulary size including special tokens.

```python
vocab_size = tokenizer.get_vocab_size()
print(f"Vocabulary has {vocab_size} tokens")
```

#### get_vocab()

Get full vocabulary as dictionary.

```python
# Without special tokens
vocab = tokenizer.get_vocab(return_special_tokens=False)

# With special tokens
vocab = tokenizer.get_vocab(return_special_tokens=True)

# Returns: {"token": id, ...}
```

#### token_to_id()

Convert token string to ID.

```python
id_ = tokenizer.token_to_id("[UNK]")
id_ = tokenizer.token_to_id("hello")

# With fallback for unknown tokens
id_ = tokenizer.token_to_id("unknown_word", add_special_tokens=False)
```

#### id_to_token()

Convert ID to token string.

```python
token = tokenizer.id_to_token(0)  # "[UNK]"
token = tokenizer.id_to_token(12345)  # Some vocabulary token
```

### Token Management Methods

#### add_tokens()

Add new tokens to vocabulary.

```python
# Add single token
new_id = tokenizer.add_tokens(["<custom_token>"])[0]

# Add multiple tokens
new_ids = tokenizer.add_tokens(["<token1>", "<token2>"])

# With AddedToken for advanced control
from tokenizers import AddedToken
token = AddedToken("<s>", single_word=True, normalized=False)
new_id = tokenizer.add_tokens([token])[0]
```

**Returns**: List of IDs for added tokens

#### num_special_tokens()

Count special tokens in vocabulary.

```python
count = tokenizer.num_special_tokens()
print(f"Tokenizer has {count} special tokens")
```

### Configuration Methods

#### enable_padding()

Enable automatic padding during encoding.

```python
# Pad to fixed length
tokenizer.enable_padding(length=128, pad_id=3, pad_token="[PAD]")

# Pad to longest in batch
tokenizer.enable_padding(length=None)

# With pair padding
tokenizer.enable_padding(
    length=512,
    pad_id=3,
    pad_token="[PAD]",
    pair_pad_id=3
)
```

#### enable_truncation()

Enable automatic truncation during encoding.

```python
from tokenizers import TruncationStrategy

tokenizer.enable_truncation(
    length=512,
    strategy=TruncationStrategy.LongestFirst,
    max_length=512
)

# Truncate only first sequence in pairs
tokenizer.enable_truncation(
    length=256,
    strategy=TruncationStrategy.OnlyFirst
)
```

#### with_processors()

Set post-processor and decoder.

```python
from tokenizers.processors import TemplateProcessing

tokenizer.with_processors(
    post_processor=TemplateProcessing(...),
    decoder=ByteLevelDecoder()
)
```

### Utility Methods

#### to_json()

Serialize tokenizer to JSON string.

```python
json_str = tokenizer.to_json()
with open("tokenizer.json", "w") as f:
    f.write(json_str)
```

#### clone()

Create a copy of the tokenizer.

```python
tokenizer_copy = tokenizer.clone()
```

## Encoding Class

Represents the result of tokenization.

### Properties

```python
encoding = tokenizer.encode("Hello, world!")

# Token strings
tokens = encoding.tokens  # ["Hello", ",", "world", "!"]

# Token IDs
ids = encoding.ids  # [12345, 67, 8901, 23]

# Character offsets in original text
offsets = encoding.offsets  # [(0, 5), (5, 6), (7, 12), (12, 13)]

# Attention mask (1 for real tokens, 0 for padding)
attention_mask = encoding.attention_mask  # [1, 1, 1, 1]

# Type IDs (0 for first sequence, 1 for second)
type_ids = encoding.type_ids  # [0, 0, 0, 0] or [0, 0, 1, 1] for pairs

# Word IDs (maps tokens to words in pre-tokenized input)
word_ids = encoding.word_ids
```

### Methods

#### word_to_tokens()

Get token range for a specific word.

```python
start, end = encoding.word_to_tokens(0)  # First word's token indices
```

#### get_sequence()

Get specific sequence from pair encoding.

```python
# Get first sequence tokens
first_seq = encoding.get_sequence(0)

# Get second sequence tokens
second_seq = encoding.get_sequence(1)
```

## Models

### BPE

Byte-Pair Encoding model.

```python
from tokenizers.models import BPE

model = BPE(
    unk_token="[UNK]",
    continuing_subword_prefix="",
    end_of_subword_suffix="",
    fuse_unk=False
)
```

### WordPiece

WordPiece model (BERT-style).

```python
from tokenizers.models import WordPiece

model = WordPiece(
    unk_token="[UNK]",
    continuing_subword_prefix="##",
    max_input_chars_per_word=100
)
```

### Unigram

Unigram model (probabilistic).

```python
from tokenizers.models import Unigram

model = Unigram(
    unk_token="<unk>",
    blank_token="",
    tie_word_piece=False,
    drop_unknowns=False
)
```

### WordLevel

Word-level tokenization.

```python
from tokenizers.models import WordLevel

model = WordLevel(
    unk_token="<unk>",
    pad_token=None,
    cls_token=None,
    sep_token=None
)
```

### SentencePiece

SentencePiece model.

```python
from tokenizers.models import SentencePiece

model = SentencePiece()
```

## Normalizers

### Basic Normalizers

```python
from tokenizers.normalizers import (
    NFD,      # Unicode NFD normalization
    NFKD,     # Unicode NFKD normalization
    NFC,      # Unicode NFC normalization
    NFKC,     # Unicode NFKC normalization
    Lowercase,  # Convert to lowercase
    Strip,      # Strip whitespace
    StripAccents  # Remove accent marks
)

tokenizer.normalizer = NFKC()
tokenizer.normalizer = Lowercase()
```

### BertNormalizer

BERT-specific normalization.

```python
from tokenizers.normalizers import BertNormalizer

tokenizer.normalizer = BertNormalizer(
    clean_text=True,
    handle_chinese_chars=True,
    strip_accents=False,
    lowercase=True
)
```

### Replace

String/regex replacement.

```python
from tokenizers.normalizers import Replace

# Simple replacement
tokenizer.normalizer = Replace(pattern="a", content="e")

# Regex replacement
tokenizer.normalizer = Replace(
    pattern=r"\s+",
    content=" ",
    regex_flags="i"
)
```

### Sequence

Chain multiple normalizers.

```python
from tokenizers.normalizers import Sequence, NFKC, Lowercase

tokenizer.normalizer = Sequence([
    NFKC(),
    StripAccents(),
    Lowercase()
])
```

## Pre-tokenizers

### Basic Pre-tokenizers

```python
from tokenizers.pre_tokenizers import (
    Whitespace,       # Split on whitespace
    WhitespaceSplit,  # Alternative whitespace splitting
    Character,        # Split into characters
    Punctuation       # Split on punctuation
)

tokenizer.pre_tokenizer = Whitespace()
```

### ByteLevel

Byte-level pre-tokenization (GPT-2 style).

```python
from tokenizers.pre_tokenizers import ByteLevel

tokenizer.pre_tokenizer = ByteLevel(
    add_prefix_space=True,
    use_regex=True,
    byte_fallback=True
)
```

### DelimiterSplit

Custom delimiter splitting.

```python
from tokenizers.pre_tokenizers import DelimiterSplit
from tokenizers import SplitDelimiterBehavior

tokenizer.pre_tokenizer = DelimiterSplit(
    delimiter="|",
    behavior=SplitDelimiterBehavior.Isolated
)
```

### Regex

Regex-based pre-tokenization.

```python
from tokenizers.pre_tokenizers import Regex

tokenizer.pre_tokenizer = Regex(pattern=r"\w+|[^\w\s]+")
```

### BertPreTokenizer

BERT-specific pre-tokenization.

```python
from tokenizers.pre_tokenizers import BertPreTokenizer

tokenizer.pre_tokenizer = BertPreTokenizer()
```

## Post-processors

### TemplateProcessing

Template-based post-processing.

```python
from tokenizers.processors import TemplateProcessing

tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[
        ("[CLS]", tokenizer.token_to_id("[CLS]")),
        ("[SEP]", tokenizer.token_to_id("[SEP]"))
    ]
)
```

### RobertaProcessing

RoBERTa-specific post-processing.

```python
from tokenizers.processors import RobertaProcessing

tokenizer.post_processor = RobertaProcessing(
    bos="<s>",
    eos="</s>",
    add_prefix_space=True
)
```

## Decoders

### Basic Decoders

```python
from tokenizers.decoders import (
    BPE,          # BPE decoder
    WordPiece,    # WordPiece decoder
    ByteLevel     # Byte-level decoder
)

tokenizer.decoder = ByteLevel()
```

### ByteLevel Decoder

```python
from tokenizers.decoders import ByteLevel

tokenizer.decoder = ByteLevel(
    add_prefix_space=True,
    utf8_cleaning=True
)
```

## Trainers

### BpeTrainer

Train BPE tokenizers.

```python
from tokenizers.trainers import BpeTrainer

trainer = BpeTrainer(
    vocab_size=30000,
    min_frequency=2,
    initial_alphabet=None,
    special_tokens=["[UNK]", "[PAD]"],
    show_progress=True,
    limit_alphabet=300,
    end_of_word_suffix="</w>"
)
```

### WordPieceTrainer

Train WordPiece tokenizers.

```python
from tokenizers.trainers import WordPieceTrainer

trainer = WordPieceTrainer(
    vocab_size=30522,
    min_frequency=2,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
    max_word_length=50
)
```

### UnigramTrainer

Train Unigram tokenizers.

```python
from tokenizers.trainers import UnigramTrainer

trainer = UnigramTrainer(
    vocab_size=32000,
    min_frequency=2,
    initial_alphabet=None,
    special_tokens=["<unk>", "<s>"],
    num_iterations=60,
    show_progress=True
)
```

### WordLevelTrainer

Train word-level tokenizers.

```python
from tokenizers.trainers import WordLevelTrainer

trainer = WordLevelTrainer(
    special_tokens=["<unk>", "<s>", "</s>"]
)
```

### SentencePieceTrainer

Train SentencePiece tokenizers.

```python
from tokenizers.trainers import SentencePieceTrainer

trainer = SentencePieceTrainer(
    vocab_size=8000,
    model_type="bpe",  # or "unigram"
    max_sentence_length=1024,
    special_tokens=["<unk>", "<s>", "</s>"]
)
```

## Utilities

### AddedToken

Configure token behavior.

```python
from tokenizers import AddedToken

token = AddedToken(
    "<s>",
    single_word=True,      # Treat as single word
    normalized=False       # Don't apply normalization
)
```

### EncodingVisualizer

Visualize tokenization results.

```python
from tokenizers import EncodingVisualizer

visualizer = EncodingVisualizer()
visualization = visualizer(tokenizer.encode("Hello, world!"))
print(visualization)
```

### TruncationStrategy

Truncation strategies for sequence pairs.

```python
from tokenizers import TruncationStrategy

# Options:
TruncationStrategy.LongestFirst    # Truncate longest sequence first
TruncationStrategy.ShortestFirst   # Truncate shortest sequence first
TruncationStrategy.OnlyFirst       # Only truncate first sequence
TruncationStrategy.OnlySecond      # Only truncate second sequence
```

## Input Types

### TextInputSequence

Raw text input.

```python
# Single string
text: str = "Hello, world!"

# List of strings (pre-tokenized)
texts: list[str] = ["Hello", ",", "world", "!"]
```

### EncodeInput

Input for encoding operations.

```python
# Single sequence
input: str = "Hello"

# Sequence pair
input: tuple[str, str] = ("Question?", "Answer.")
```

## Error Handling

### Common Exceptions

```python
from tokenizers import Tokenizer

try:
    tokenizer = Tokenizer.from_file("nonexistent.json")
except FileNotFoundError:
    print("Tokenizer file not found")

try:
    encoding = tokenizer.encode(None)  # Invalid input
except TypeError as e:
    print(f"Invalid input type: {e}")

try:
    token = tokenizer.id_to_token(999999)  # Out of vocabulary
except IndexError:
    print("Token ID out of range")
```

## Configuration Examples

### Complete BERT Setup

```python
from tokenizers import Tokenizer
from tokenizers.models import WordPiece
from tokenizers.normalizers import BertNormalizer
from tokenizers.pre_tokenizers import BertPreTokenizer
from tokenizers.processors import TemplateProcessing
from tokenizers.trainers import WordPieceTrainer

tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))
tokenizer.normalizer = BertNormalizer()
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

tokenizer.train(files=["train.txt"], trainer=trainer)
tokenizer.save("bert_tokenizer.json")
```
