# Tokenization Pipeline

## Overview

When calling `Tokenizer.encode()` or `Tokenizer.encode_batch()`, input text goes through a four-stage pipeline:

```
Raw Text → Normalizer → PreTokenizer → Model → PostProcessor → Encoding
```

Each stage is customizable. Changing the normalizer, pre-tokenizer, or model requires retraining. Changing the post-processor does not.

## Normalization

Normalization applies operations to raw text to make it "cleaner" and more consistent. The library tracks alignment through normalization so tokens can always be mapped back to original text spans.

### Available Normalizers

- **NFD** — NFD Unicode normalization
- **NFKD** — NFKD Unicode normalization
- **NFC** — NFC Unicode normalization
- **NFKC** — NFKC Unicode normalization
- **Lowercase** — Convert all uppercase to lowercase
- **Strip** — Remove whitespace from specified sides (left, right, or both)
- **StripAccents** — Remove accent symbols (use with NFD for consistency)
- **Replace** — Replace custom string or regex pattern
- **BertNormalizer** — BERT's original normalizer (clean_text, handle_chinese_chars, strip_accents, lowercase options)
- **ByteLevel** — Byte-level normalization
- **Nmt** — NMT normalizer
- **Sequence** — Compose multiple normalizers in order

### Example

```python
from tokenizers import normalizers
from tokenizers.normalizers import NFD, StripAccents

normalizer = normalizers.Sequence([NFD(), StripAccents()])
normalizer.normalize_str("Héllò hôw are ü?")
# "Hello how are u?"

tokenizer.normalizer = normalizer
```

## Pre-tokenization

Pre-tokenization splits normalized text into sub-units that define upper bounds for final tokens. Think of it as splitting into "words" — the model then decides whether each word stays whole or splits further.

### Available Pre-tokenizers

- **ByteLevel** — Splits on whitespace while remapping bytes to visible characters. Introduced by OpenAI with GPT-2. Requires only 256 initial alphabet characters (no `[UNK]` needed). Spaces are encoded as `Ġ`.
- **Whitespace** — Splits on word boundaries using `\w+|[^\w\s]+`
- **WhitespaceSplit** — Splits on any whitespace character
- **Punctuation** — Isolates all punctuation characters
- **Metaspace** — Splits on whitespace, replaces with `▁` (U+2581)
- **CharDelimiterSplit** — Splits on a given delimiter character
- **Digits** — Separates numbers from other characters
- **BertPreTokenizer** — Splits on spaces and isolates punctuation
- **Split** — Versatile pre-tokenizer with custom pattern, behavior (removed/isolated/merged_with_previous/merged_with_next/contiguous), and invert flag
- **Sequence** — Compose multiple pre-tokenizers in order

### Example

```python
from tokenizers.pre_tokenizers import Whitespace

pre_tokenizer = Whitespace()
pre_tokenizer.pre_tokenize_str("Hello! How are you?")
# [("Hello", (0, 5)), ("!", (5, 6)), ("How", (7, 10)), ...]
```

Combined pre-tokenizer (whitespace + digit separation):

```python
from tokenizers import pre_tokenizers
from tokenizers.pre_tokenizers import Digits

pre_tokenizer = pre_tokenizers.Sequence([Whitespace(), Digits(individual_digits=True)])
pre_tokenizer.pre_tokenize_str("Call 911!")
# [("Call", (0, 4)), ("9", (5, 6)), ("1", (6, 7)), ("1", (7, 8)), ("!", (8, 9))]
```

## Model

The model is the core algorithm that splits pre-tokens into vocabulary tokens and maps them to integer IDs. This is the only mandatory component of a Tokenizer.

See [Models Reference](reference/02-models.md) for details on BPE, WordPiece, Unigram, and WordLevel.

## Post-processing

Post-processing transforms the Encoding before it's returned — typically adding special tokens required by the target model.

### Available Post-processors

- **TemplateProcessing** — Template-based post-processing with custom token placement and type IDs
- **BertProcessing** — BERT-specific: adds `[CLS]` at start, `[SEP]` at end
- **RobertaProcessing** — RoBERTa-specific: adds special tokens + trims ByteLevel offsets
- **ByteLevel** — Trims whitespace from produced offsets for ByteLevel BPE

### TemplateProcessing

The most flexible post-processor. Uses `$A` and `$B` to reference input sequences, `:N` suffix for type IDs:

```python
from tokenizers.processors import TemplateProcessing

tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[
        ("[CLS]", tokenizer.token_to_id("[CLS]")),
        ("[SEP]", tokenizer.token_to_id("[SEP]")),
    ],
)
```

Template syntax:

- `$A` — First sequence (default type_id=0)
- `$B` — Second sequence (default type_id=0)
- `$0`, `$1`, `$2` — Sequences by index
- `$A:1` — Sequence A with type_id=1
- Special tokens in template: `"[SEP]"` or `"[SEP]:1"` for specific type_id

### Example: BERT from Scratch

```python
from tokenizers import Tokenizer, normalizers, decoders
from tokenizers.models import WordPiece
from tokenizers.normalizers import NFD, Lowercase, StripAccents
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.processors import TemplateProcessing
from tokenizers.trainers import WordPieceTrainer

# 1. Initialize with WordPiece model
bert_tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))

# 2. Normalizer: BERT uses NFD + lowercase + strip accents
bert_tokenizer.normalizer = normalizers.Sequence([NFD(), Lowercase(), StripAccents()])

# 3. Pre-tokenizer: split on whitespace and punctuation
bert_tokenizer.pre_tokenizer = Whitespace()

# 4. Post-processor: add [CLS] and [SEP]
bert_tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[("[CLS]", 1), ("[SEP]", 2)],
)

# 5. Decoder: handle ## subword prefix
bert_tokenizer.decoder = decoders.WordPiece()

# 6. Train
trainer = WordPieceTrainer(
    vocab_size=30522,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"]
)
files = [f"data/wikitext-103-raw/wiki.{split}.raw" for split in ["test", "train", "valid"]]
bert_tokenizer.train(files, trainer)
bert_tokenizer.save("data/bert-wiki.json")
```

## Decoding

Decoding converts token IDs back to readable text. The decoder reverses special markers used by the model (like `##` in WordPiece or byte-level encoding).

### Available Decoders

- **ByteLevel** — Reverts ByteLevel pre-tokenizer encoding
- **Metaspace** — Reverts Metaspace `▁` markers back to spaces
- **WordPiece** — Reverts `##` subword prefix

```python
from tokenizers import decoders

bert_tokenizer.decoder = decoders.WordPiece()

output = bert_tokenizer.encode("Welcome to the Tokenizers library.")
print(output.tokens)
# ["[CLS]", "welcome", "to", "the", "tok", "##eni", "##zer", "##s", "library", ".", "[SEP]"]

# Without decoder: "welcome to the tok ##eni ##zer ##s library ."
# With WordPiece decoder: "welcome to the tokenizers library."
bert_tokenizer.decode(output.ids)
```

## Training from Memory

Instead of files, you can train from any Python iterator:

### From a list

```python
data = [
    "Beautiful is better than ugly.",
    "Explicit is better than implicit.",
    "Simple is better than complex.",
]
tokenizer.train_from_iterator(data, trainer=trainer)
```

### From the Datasets library

```python
import datasets

dataset = datasets.load_dataset("wikitext", "wikitext-103-raw-v1", split="train+test+validation")

def batch_iterator(batch_size=1000):
    tok_dataset = dataset.select_columns("text")
    for batch in tok_dataset.iter(batch_size):
        yield batch["text"]

tokenizer.train_from_iterator(batch_iterator(), trainer=trainer, length=len(dataset))
```

### From gzip files

```python
import gzip

files = ["data/my-file.0.gz", "data/my-file.1.gz", "data/my-file.2.gz"]

def gzip_iterator():
    for path in files:
        with gzip.open(path, "rt") as f:
            for line in f:
                yield line

tokenizer.train_from_iterator(gzip_iterator(), trainer=trainer)
```
