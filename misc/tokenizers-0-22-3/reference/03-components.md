# Components Reference

## Normalizers

A `Normalizer` preprocesses input text to normalize it. Alignment is tracked through normalization so tokens always map back to original text.

### Unicode Normalization

- **NFC** — Canonical composition
- **NFD** — Canonical decomposition
- **NFKC** — Compatibility composition
- **NFKD** — Compatibility decomposition

### Text Transformation

- **Lowercase** — Convert to lowercase
- **Strip** — Remove whitespace (left, right, or both sides)
- **StripAccents** — Remove accent marks (use after NFD)
- **Replace** — Replace custom string or regex pattern

### Specialized

- **BertNormalizer** — BERT's original normalization with options: `clean_text`, `handle_chinese_chars`, `strip_accents`, `lowercase`
- **ByteLevel** — Byte-level normalization
- **Nmt** — NMT normalizer

### Composing Normalizers

```python
from tokenizers import normalizers
from tokenizers.normalizers import NFD, Lowercase, StripAccents

normalizer = normalizers.Sequence([NFD(), Lowercase(), StripAccents()])
tokenizer.normalizer = normalizer
```

## Pre-tokenizers

A `PreTokenizer` splits normalized text into sub-units that define upper bounds for tokens.

### Basic Splitters

- **Whitespace** — Split on word boundaries (`\w+|[^\w\s]+`)
- **WhitespaceSplit** — Split on any whitespace character
- **Punctuation** — Isolate all punctuation characters
- **CharDelimiterSplit** — Split on a given delimiter character

### Advanced

- **ByteLevel** — Byte-level splitting with visible character remapping. Options: `add_prefix_space`, `trim_offsets`, `use_regex`
- **Metaspace** — Split on whitespace, replace with `▁` (U+2581). Options: `replacement`, `add_prefix_space`
- **Digits** — Separate numbers from text. Option: `individual_digits`
- **BertPreTokenizer** — BERT-style: split on spaces and isolate punctuation
- **Split** — Custom pattern with behaviors: `removed`, `isolated`, `merged_with_previous`, `merged_with_next`, `contiguous`. Supports regex and `invert` flag

### Composing Pre-tokenizers

```python
from tokenizers import pre_tokenizers
from tokenizers.pre_tokenizers import Whitespace, Digits

pre_tokenizer = pre_tokenizers.Sequence([Whitespace(), Digits(individual_digits=True)])
tokenizer.pre_tokenizer = pre_tokenizer
```

## Post-processors

A `PostProcessor` transforms the Encoding before return — typically adding special tokens.

### TemplateProcessing

Flexible template-based post-processing:

```python
from tokenizers.processors import TemplateProcessing

tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[("[CLS]", 1), ("[SEP]", 2)],
)
```

Template syntax: `$A` (first sequence), `$B` (second sequence), `$0`/`$1` (by index), `:N` suffix for type_id.

### Model-specific Post-processors

- **BertProcessing** — Adds `[CLS]` and `[SEP]` tokens
- **RobertaProcessing** — RoBERTa special tokens + ByteLevel offset trimming
- **ByteLevel** — Trims whitespace from offsets for ByteLevel BPE

## Decoders

A `Decoder` converts token IDs back to readable text, reversing model-specific markers.

- **ByteLevel** — Reverts ByteLevel encoding
- **Metaspace** — Reverts `▁` markers back to spaces
- **WordPiece** — Removes `##` subword prefix

```python
from tokenizers import decoders

tokenizer.decoder = decoders.WordPiece()
text = tokenizer.decode([101, 7592, 1037, 2466, 102])
# "hello world"
```

## Trainers

Each model has a corresponding Trainer class.

### BpeTrainer

```python
from tokenizers.trainers import BpeTrainer

trainer = BpeTrainer(
    vocab_size=30000,
    min_frequency=2,
    special_tokens=["[UNK]", "[CLS]", "[SEP]"],
    limit_alphabet=1000,
    initial_alphabet=[],
    continuing_subword_prefix=None,
    end_of_word_suffix=None,
    max_token_length=25,
)
```

### UnigramTrainer

```python
from tokenizers.trainers import UnigramTrainer

trainer = UnigramTrainer(
    vocab_size=8000,
    special_tokens=["<PAD>", "<BOS>", "<EOS>"],
    initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
    shrinking_factor=0.75,
    unk_token=None,
    max_piece_length=16,
    n_sub_iterations=2,
)
```

### WordPieceTrainer

```python
from tokenizers.trainers import WordPieceTrainer

trainer = WordPieceTrainer(
    vocab_size=30000,
    min_frequency=2,
    special_tokens=["[UNK]", "[CLS]", "[SEP]"],
    continuing_subword_prefix="##",
)
```

### WordLevelTrainer

```python
from tokenizers.trainers import WordLevelTrainer

trainer = WordLevelTrainer(
    vocab_size=30000,
    min_frequency=2,
    special_tokens=["[UNK]", "[CLS]", "[SEP]"],
)
```

## AddedTokens

`AddedToken` represents a token that can be added to a Tokenizer with special matching behavior:

```python
from tokenizers import AddedToken

token = AddedToken(
    content="[MASK]",
    single_word=False,   # Match inside words (False) or only standalone (True)
    lstrip=False,        # Greedily match whitespace on left
    rstrip=False,        # Greedily match whitespace on right
    normalized=True,     # Match against normalized text
    special=False,       # Skip during decoding if True
)
```

### Adding tokens to a tokenizer

```python
# Add regular tokens
tokenizer.add_tokens(["[SPECIAL_1]", "[SPECIAL_2]"])

# Add special tokens (skipped during decode)
tokenizer.add_special_tokens([AddedToken("[PAD]", special=True)])
```

### AddedToken Options

- `single_word` — If True, token only matches as a standalone word (respects word boundaries)
- `lstrip` — If True, greedily consumes whitespace on the left
- `rstrip` — If True, greedily consumes whitespace on the right
- `normalized` — If True, matches against normalized text; if False, matches raw text
- `special` — If True, token is skipped during decoding

## Padding and Truncation

### Padding

```python
# Enable padding to longest in batch
tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")

# Pad to fixed length
tokenizer.enable_padding(length=128)

# Pad to specific length with specific token
tokenizer.enable_padding(
    length=512,
    pad_id=3,
    pad_token="[PAD]",
    direction="right"  # or "left"
)

# Disable padding
tokenizer.disable_padding()
```

### Truncation

```python
# Enable truncation to max length
tokenizer.enable_truncation(max_length=512)

# Truncate with strategy
tokenizer.enable_truncation(
    max_length=512,
    strategy="longest_first"  # or "only_first", "only_second"
)

# Disable truncation
tokenizer.disable_truncation()
```
