# Pipeline Components

Deep dive into the four stages of the tokenization pipeline: Normalizers, Pre-tokenizers, Models, Post-processors, and Decoders.

## The Tokenization Pipeline

```
Raw Text → [Normalizer] → [PreTokenizer] → [Model] → [PostProcessor] → Output
                    ↓                                          ↓
              (Unicode norm)                          (Add special tokens)
              (lowercase)                              (format for model)
              (strip accents)
```

Each component is optional and can be customized or replaced.

## Normalizers

Normalizers clean and standardize input text before tokenization. They maintain character-level alignment tracking throughout transformations.

### Unicode Normalization

```python
from tokenizers.normalizers import NFD, NFKD, NFC, NFKC

# NFD: Canonical decomposition
tokenizer.normalizer = NFD()

# NFKD: Compatibility decomposition  
tokenizer.normalizer = NFKD()

# NFC: Canonical composition
tokenizer.normalizer = NFC()

# NFKC: Compatibility composition (most common)
tokenizer.normalizer = NFKC()
```

**Example**: NFKC normalizes "ﬁ" (ligature) to "fi" and handles full-width characters.

### Text Cleaning

```python
from tokenizers.normalizers import Lowercase, Strip, StripAccents

# Convert to lowercase
tokenizer.normalizer = Lowercase()

# Remove leading/trailing whitespace
tokenizer.normalizer = Strip()

# Remove accent marks (use with NFD for consistency)
tokenizer.normalizer = StripAccents()
```

### BertNormalizer

BERT-specific normalization matching the original implementation:

```python
from tokenizers.normalizers import BertNormalizer

# Default BERT normalization (clean_text + handle_chinese_chars)
tokenizer.normalizer = BertNormalizer(
    clean_text=True,              # Remove unwanted characters
    handle_chinese_chars=True,    # Add whitespace around Chinese chars
    strip_accents=False,          # Keep accents
    lowercase=True                # Convert to lowercase
)
```

### Replace Normalizer

Custom string/regex replacement:

```python
from tokenizers.normalizers import Replace

# Simple string replacement
tokenizer.normalizer = Replace(pattern="a", content="e")
# "banana" → "benene"

# Regex replacement
tokenizer.normalizer = Replace(pattern=r"\s+", content=" ")
# Multiple spaces → single space

# Case-insensitive replacement
tokenizer.normalizer = Replace(pattern="hello", content="hi", regex_flags="i")
```

### Sequence Normalizer

Chain multiple normalizers:

```python
from tokenizers.normalizers import Sequence, NFKC, Lowercase, StripAccents

tokenizer.normalizer = Sequence([
    NFKC(),           # 1. Unicode normalization
    StripAccents(),   # 2. Remove accents
    Lowercase()       # 3. Convert to lowercase
])
```

**Execution order**: Normalizers run in the order specified, left to right.

## Pre-tokenizers

Pre-tokenizers split input text into initial units before the main tokenization model processes them. They ensure tokens don't span across arbitrary boundaries (e.g., multiple words).

### Basic Pre-tokenizers

```python
from tokenizers.pre_tokenizers import Whitespace, WhitespaceSplit, Character

# Split on whitespace (default for many models)
tokenizer.pre_tokenizer = Whitespace()

# Alternative whitespace splitting
tokenizer.pre_tokenizer = WhitespaceSplit()

# Split into individual characters
tokenizer.pre_tokenizer = Character()
```

### ByteLevel Pre-tokenizer

OpenAI's GPT-2 approach - maps bytes to visible characters, enabling 256-token vocabulary:

```python
from tokenizers.pre_tokenizers import ByteLevel

# Basic byte-level encoding
tokenizer.pre_tokenizer = ByteLevel()

# With prefix space (required for GPT-2 compatibility)
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=True)

# Control special behavior
tokenizer.pre_tokenizer = ByteLevel(
    add_prefix_space=True,
    use_regex=False,              # Use simple split instead of regex
    byte_fallback=True            # Handle UTF-8 decoding errors
)
```

**Example**: "Hello" with `add_prefix_space=True` → "ĠHello" (each word gets prefix space)

### Punctuation Pre-tokenizer

Split on punctuation marks:

```python
from tokenizers.pre_tokenizers import Punctuation

tokenizer.pre_tokenizer = Punctuation()
# "Hello, world!" → ["Hello", ",", "world", "!"]
```

### Delimiter Split Pre-tokenizer

Custom delimiter-based splitting:

```python
from tokenizers.pre_tokenizers import DelimiterSplit

# Split on custom character
tokenizer.pre_tokenizer = DelimiterSplit(delimiter="|")
# "a|b|c" → ["a", "b", "c"]

# Control what happens with delimiter
from tokenizers import SplitDelimiterBehavior

tokenizer.pre_tokenizer = DelimiterSplit(
    delimiter=" ",
    behavior=SplitDelimiterBehavior.Isolated  # Delimiter becomes separate token
)
```

### Regex Pre-tokenizer

Custom regex-based splitting:

```python
from tokenizers.pre_tokenizers import Regex

# Custom pattern
tokenizer.pre_tokenizer = Regex(pattern=r"\w+|[^\w\s]+")
# Matches: word characters OR non-word-non-space characters

# Unicode-aware pattern
tokenizer.pre_tokenizer = Regex(pattern=r"[\p{L}\p{N}]+|[^\s]+", regex_flags="u")
```

### BertPreTokenizer

BERT-specific pre-tokenization:

```python
from tokenizers.pre_tokenizers import BertPreTokenizer

tokenizer.pre_tokenizer = BertPreTokenizer()
# Handles Chinese characters and punctuation per BERT spec
```

### Sequence Pre-tokenizer

Chain multiple pre-tokenizers:

```python
from tokenizers.pre_tokenizers import Sequence, Whitespace, Punctuation

tokenizer.pre_tokenizer = Sequence([
    Whitespace(),     # 1. Split on whitespace
    Punctuation()     # 2. Then split punctuation
])
```

## Post-processors

Post-processors format the final output, adding special tokens and handling sequence pairs for specific models.

### TemplateProcessing

Most common post-processor - uses templates to add special tokens:

```python
from tokenizers.processors import TemplateProcessing

# BERT-style formatting
tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",                    # Single sequence template
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",         # Pair template (:1 indicates type ID)
    special_tokens=[                            # Required special tokens with IDs
        ("[CLS]", tokenizer.token_to_id("[CLS]")),
        ("[SEP]", tokenizer.token_to_id("[SEP]"))
    ]
)
```

**Template variables**:
- `$A`: First sequence tokens
- `$B`: Second sequence tokens (in pairs)
- `:0`, `:1`: Type ID markers for attention masks

### RobertaProcessing

RoBERTa-specific formatting:

```python
from tokenizers.processors import RobertaProcessing

tokenizer.post_processor = RobertaProcessing(
    bos="<s>",
    eos="</s>",
    add_prefix_space=True  # Match pre-tokenizer configuration
)
```

### DialoGPTProcessing

DialoGPT formatting:

```python
from tokenizers.processors import DialoGPTProcessing

tokenizer.post_processor = DialoGPTProcessing()
# Adds no special tokens (uses raw input)
```

### NoPostProcessor

Disable post-processing:

```python
from tokenizers.processors import NoPostProcessor

tokenizer.post_processor = NoPostProcessor()
```

## Decoders

Decoders convert token IDs back to text, reversing pre-tokenization transformations.

### ByteLevel Decoder

Reverse ByteLevel pre-tokenization:

```python
from tokenizers.decoders import ByteLevel

tokenizer.decoder = ByteLevel()

# With prefix space handling
tokenizer.decoder = ByteLevel(add_prefix_space=True)
```

### WordPiece Decoder

Handle WordPiece subword tokens:

```python
from tokenizers.decoders import WordPiece

tokenizer.decoder = WordPiece()
# Removes "##" prefix from continued tokens
# ["##ing", "##s"] → "ings"
```

### BPE Decoder

Standard BPE decoding (simple concatenation):

```python
from tokenizers.decoders import BPE

tokenizer.decoder = BPE(
    ignore_eos=True  # Ignore end-of-sequence token during decoding
)
```

### Sequence Decoder

Chain multiple decoders:

```python
from tokenizers.decoders import Sequence, ByteLevel, WordPiece

tokenizer.decoder = Sequence([
    ByteLevel(),      # 1. Reverse byte encoding
    WordPiece()       # 2. Handle subword pieces
])
```

## Component Interaction Examples

### Complete BERT Pipeline

```python
from tokenizers import Tokenizer
from tokenizers.models import WordPiece
from tokenizers.normalizers import BertNormalizer
from tokenizers.pre_tokenizers import BertPreTokenizer
from tokenizers.processors import TemplateProcessing

tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))

# 1. Normalize: lowercase, handle Chinese, clean text
tokenizer.normalizer = BertNormalizer(
    clean_text=True,
    handle_chinese_chars=True,
    strip_accents=False,
    lowercase=True
)

# 2. Pre-tokenize: split on whitespace and punctuation
tokenizer.pre_tokenizer = BertPreTokenizer()

# 3. Post-process: add [CLS] and [SEP] tokens
tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[
        ("[CLS", tokenizer.token_to_id("[CLS]")),
        ("[SEP]", tokenizer.token_to_id("[SEP]"))
    ]
)

# Tokenize
encoding = tokenizer.encode("Hello, world!")
print(encoding.tokens)  # ["[CLS]", "hello", ",", "world", "!", "[SEP]"]
```

### Complete GPT-2 Pipeline

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder

tokenizer = Tokenizer(BPE())

# Pre-tokenize: byte-level encoding with prefix space
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=True)

# Decode: reverse byte-level encoding
tokenizer.decoder = ByteLevelDecoder(add_prefix_space=True)

# Note: GPT-2 doesn't use post-processing for special tokens
```

### Custom Pipeline Example

```python
from tokenizers import Tokenizer
from tokenizers.models import Unigram
from tokenizers.normalizers import Sequence, NFKC, Lowercase
from tokenizers.pre_tokenizers import Sequence as PreSeq, Whitespace, Punctuation
from tokenizers.processors import TemplateProcessing

tokenizer = Tokenizer(Unigram())

# Custom normalization pipeline
tokenizer.normalizer = Sequence([
    NFKC(),           # Unicode normalization
    Lowercase()       # Convert to lowercase
])

# Custom pre-tokenization pipeline
tokenizer.pre_tokenizer = PreSeq([
    Whitespace(),     # Split on whitespace first
    Punctuation()     # Then split punctuation
])

# Custom post-processing
tokenizer.post_processor = TemplateProcessing(
    single="<s> $A </s>",
    pair="<s> $A </s> $B:1 </s>:1",
    special_tokens=[
        ("<s>", tokenizer.token_to_id("<s>")),
        ("</s>", tokenizer.token_to_id("</s>"))
    ]
)
```

## Component Selection Guide

| Use Case | Normalizer | Pre-tokenizer | Model | Post-processor |
|----------|------------|---------------|-------|----------------|
| BERT | BertNormalizer | BertPreTokenizer | WordPiece | TemplateProcessing |
| GPT-2 | None | ByteLevel | BPE | None |
| RoBERTa | NFKC + Lowercase | ByteLevel | BPE | RobertaProcessing |
| T5 | NFKC | ByteLevel | Unigram | TemplateProcessing |
| XLNet | NFC + Lowercase | Whitespace | WordPiece | TemplateProcessing |
| Custom Domain | NFKC | Whitespace + Punctuation | BPE/Unigram | TemplateProcessing |

## Debugging Components

### Test Individual Components

```python
from tokenizers import Tokenizer
from tokenizers.normalizers import Lowercase
from tokenizers.pre_tokenizers import Whitespace

# Test normalizer in isolation
normalizer = Lowercase()
normalized = normalizer.normalize_str("HELLO World")
print(normalized)  # "hello world"

# Test pre-tokenizer in isolation
pre_tokenizer = Whitespace()
pretokens = pre_tokenizer.pre_tokenize_str("Hello world")
print(pretokens)  # [("Hello", (0, 5)), ("world", (6, 11))]
```

### Inspect Pipeline State

```python
tokenizer = Tokenizer.from_file("tokenizer.json")

# Check each component
print(f"Normalizer: {tokenizer.normalizer}")
print(f"Pre-tokenizer: {tokenizer.pre_tokenizer}")
print(f"Model: {tokenizer.model}")
print(f"Post-processor: {tokenizer.post_processor}")
print(f"Decoder: {tokenizer.decoder}")
```

## Next Steps

- [Models Reference](references/04-models.md) - Deep dive into BPE, WordPiece, Unigram algorithms
- [Training Guide](references/05-training-guide.md) - How to train with different component configurations
- [API Reference](references/07-api-reference.md) - Complete API documentation
