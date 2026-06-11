# API Reference

## Tokenizer Class

The main entry point for the library.

### Construction

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE

tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
```

### Properties

- `tokenizer.model` — The core tokenization model
- `tokenizer.normalizer` — Optional normalizer (None by default)
- `tokenizer.pre_tokenizer` — Optional pre-tokenizer
- `tokenizer.post_processor` — Optional post-processor
- `tokenizer.decoder` — Optional decoder

### Encoding Methods

```python
# Single sequence
encoding = tokenizer.encode("Hello world")

# Sequence pair
encoding = tokenizer.encode("Hello", "world")

# Batch of single sequences
encodings = tokenizer.encode_batch(["Hello", "World"])

# Batch of pairs
encodings = tokenizer.encode_batch([
    ("Hello", "World"),
    ("Foo", "Bar"),
])

# With padding and truncation
encoding = tokenizer.encode("Long text...", truncation=True, padding=True)
```

### Decoding Methods

```python
# Decode single sequence
text = tokenizer.decode([101, 7592, 1037, 102])

# Decode with options
text = tokenizer.decode([101, 7592, 1037, 102], skip_special_tokens=True)

# Batch decode
texts = tokenizer.decode_batch([[101, 7592], [102, 7592]])
```

### Vocabulary Methods

```python
# Token to ID
id = tokenizer.token_to_id("[CLS]")

# ID to token
token = tokenizer.id_to_token(101)

# Vocabulary size
size = tokenizer.get_vocab_size()

# Full vocabulary (dict of token -> id)
vocab = tokenizer.get_vocab()

# Add tokens
tokenizer.add_tokens(["[NEW_1]", "[NEW_2]"])

# Add special tokens
tokenizer.add_special_tokens([AddedToken("[SPECIAL]", special=True)])
```

### Serialization

```python
# Save to file (JSON format)
tokenizer.save("tokenizer.json")

# Load from file
tokenizer = Tokenizer.from_file("tokenizer.json")

# Load from Hugging Face Hub
tokenizer = Tokenizer.from_pretrained("bert-base-uncased")

# Serialize to JSON string
json_str = tokenizer.to_str()

# Deserialize from JSON string
tokenizer = Tokenizer.from_str(json_str)
```

### Padding and Truncation

```python
# Enable/disable padding
tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=512, direction="right")
tokenizer.disable_padding()

# Enable/disable truncation
tokenizer.enable_truncation(max_length=512, strategy="longest_first")
tokenizer.disable_truncation()
```

## Encoding Object

The output of `Tokenizer.encode()`. Contains all information needed for model input.

### Attributes

```python
encoding = tokenizer.encode("Hello world")

encoding.tokens         # List[str] — Token strings
encoding.ids            # List[int] — Token IDs
encoding.type_ids       # List[int] — Sequence type IDs (0 or 1)
encoding.attention_mask # List[int] — Attention mask (1 for real tokens, 0 for padding)
encoding.offsets        # List[Tuple[int, int]] — Character (start, end) positions in original text
```

### Offsets and Alignment

Each token's offset maps back to the original input text:

```python
encoding = tokenizer.encode("Hello, world!")
for token, (start, end) in zip(encoding.tokens, encoding.offsets):
    print(f"{token}: '{original_text[start:end]}'")
```

## Input Types

### TextEncodeInput

Raw text input for `encode_batch()`:

- Single string: `"Hello world"`
- Pair of strings: `("Hello", "world")`
- List of either: `["Hello", ("Hi", "there")]`

### PreTokenizedEncodeInput

Pre-tokenized input (list of tokens instead of raw text):

- List of tokens: `["Hello", "world"]`
- Pair of token lists: `(["Hello"], ["world"])`

## Encode Inputs Union

```python
from tokenizers import Encoding

# encode() accepts EncodeInput = TextEncodeInput | PreTokenizedEncodeInput
encoding = tokenizer.encode("Hello world", is_pretokenized=False)
encoding = tokenizer.encode(["Hello", "world"], is_pretokenized=True)
```

## Provided Tokenizers

Convenience classes that combine model + common configuration:

```python
from tokenizers import BertWordPieceTokenizer, CharBPETokenizer

# BERT WordPiece from vocabulary file
tokenizer = BertWordPieceTokenizer("bert-base-uncased-vocab.txt", lowercase=True)

# Character-level BPE from vocab and merges files
tokenizer = CharBPETokenizer("./vocab.json", "./merges.txt")
```

## Visualizer Tool

The `EncodingVisualizer` provides an HTML visualization of tokenization results:

```python
from tokenizers.tools import EncodingVisualizer

visualizer = EncodingVisualizer(tokenizer)

# Generate HTML visualization
html = visualizer("Hello, how are you today?", default_to_notebook=False)

# With annotations (e.g., NER spans)
from tokenizers.tools import Annotation
annotations = [
    Annotation(start=0, end=5, label="GREETING"),
]
html = visualizer("Hello world", annotations=annotations)
```

### Annotation

```python
Annotation(
    start: int,     # Start character index in original text
    end: int,       # End character index
    label: str      # Label for the annotation
)
```

## DecodeStream

For streaming decode operations (converting model output IDs to text incrementally):

```python
from tokenizers.decoders import DecodeStream

stream = DecodeStream(ids=[101, 7592, 1037, 102], skip_special_tokens=True)
for text_chunk in stream:
    print(text_chunk)
```

DecodeStream supports `__copy__` and `__deepcopy__` as of 0.23.

## Version Notes (0.23.1)

- **Python 3.10+ required** — Python 3.9 dropped
- **Python 3.14 support** including free-threaded (`3.14t`) wheels with `Py_MOD_GIL_NOT_USED`
- **Full type hints** — every class has `.pyi` stubs; `mypy --strict`, `ty`, and `pyright` now see real signatures
- **Stub layout changed** — from `tokenizers/<sub>/__init__.pyi` to `tokenizers/<sub>.pyi`
- **Node.js multi-platform bindings** — 13 platforms (macOS x64/arm64/universal, Windows x64/i686/arm64, Linux x64/arm64/armv7 glibc+musl, Android arm64/armv7)
- **Unigram sampling** — `alpha` and `nbest_size` parameters for subword regularization
- **Weakref support** on `Tokenizer` for long-lived caches
- **Truncation early exit** — right-direction truncation skips pre-tokenization past `max_length`
- **add_tokens normalizes content at insertion** — re-saved `tokenizer.json` may differ in `added_tokens` block
- **Performance gains** — added-vocabulary deserialize up to 96% faster, BPE encode batch 16% faster
- **EncodingVisualizer** — unclosed annotation span fixed, HTML escape applied to output
- **DecodeStream** — `__copy__` / `__deepcopy__` support added
