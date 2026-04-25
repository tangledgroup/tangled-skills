# Special Tokens Guide

Complete guide to managing special tokens in tokenizers, including adding, configuring, and using them for different model architectures.

## Special Tokens Overview

Special tokens are reserved vocabulary entries that serve specific purposes in model input formatting:

| Token | Purpose | Common Models |
|-------|---------|---------------|
| `[UNK]` | Unknown/out-of-vocabulary tokens | All models |
| `[PAD]` | Padding for batch processing | All models |
| `[CLS]` | Classification token (sentence representation) | BERT, DistilBERT |
| `[SEP]` | Separator between sequence pairs | BERT, RoBERTa |
| `[MASK]` | Masked tokens for MLM training | BERT, RoBERTa |
| `<s>` | Beginning of sequence | GPT-2, T5, LLaMA |
| `</s>` | End of sequence | GPT-2, T5, LLaMA |
| `<pad>` | Padding token (alternative) | T5, BART |

## Adding Special Tokens During Training

### Basic Configuration

Special tokens must be declared during training to reserve IDs:

```python
from tokenizers.trainers import BpeTrainer

trainer = BpeTrainer(
    vocab_size=30000,
    special_tokens=[
        "[UNK]",   # ID 0
        "[PAD]",   # ID 1
        "[CLS]",   # ID 2
        "[SEP]",   # ID 3
        "[MASK]"   # ID 4
    ]
)
```

**Important**: The order of special tokens determines their IDs. `[UNK]` should typically be first (ID 0).

### Token Type Configuration

Specify token types for proper handling:

```python
from tokenizers import AddedToken

trainer = BpeTrainer(
    special_tokens=[
        "[UNK]",
        AddedToken("[PAD]", single_word=False, normalized=False),
        AddedToken("[CLS]", single_word=True, normalized=True),
        AddedToken("[SEP]", single_word=True, normalized=True)
    ]
)
```

**AddedToken parameters**:
- `single_word`: Token should be treated as single word (not split)
- `normalized`: Token should undergo normalization

## Adding Special Tokens After Training

### Using add_tokens()

Add tokens to an existing tokenizer:

```python
from tokenizers import Tokenizer

tokenizer = Tokenizer.from_file("trained_tokenizer.json")

# Add single token
new_token_id = tokenizer.add_tokens(["[NEW_TOKEN]"])
print(f"Added [NEW_TOKEN] with ID: {new_token_id[0]}")

# Add multiple tokens
new_ids = tokenizer.add_tokens(["[TOKEN1]", "[TOKEN2]", "[TOKEN3]"])
print(f"Added tokens with IDs: {new_ids}")
```

### Using AddedToken for Advanced Control

```python
from tokenizers import AddedToken

# Token that shouldn't be split
special_token = AddedToken("<s>", single_word=True, normalized=False)

# Token with specific behavior
pad_token = AddedToken(
    "[PAD]",
    single_word=False,    # Can appear anywhere
    normalized=False      # Don't apply normalization
)

tokenizer.add_tokens([special_token, pad_token])
```

### Updating Model Weights After Adding Tokens

When adding tokens to a tokenizer used with a model, you must also resize the model's embedding layer:

```python
from transformers import AutoTokenizer, AutoModel

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

# Add new tokens
num_added = tokenizer.add_tokens(["<custom_token_1>", "<custom_token_2>"])
print(f"Added {num_added} tokens")

# Resize model embeddings to match new vocabulary
model.resize_token_embeddings(len(tokenizer))

# Save updated model and tokenizer
tokenizer.save_pretrained("./updated_model/")
model.save_pretrained("./updated_model/")
```

## Template Processing with Special Tokens

### BERT-style Formatting

Add `[CLS]` and `[SEP]` tokens automatically:

```python
from tokenizers.processors import TemplateProcessing

tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",                    # Single sequence template
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",         # Pair template
    special_tokens=[
        ("[CLS]", tokenizer.token_to_id("[CLS]")),
        ("[SEP]", tokenizer.token_to_id("[SEP]"))
    ]
)

# Encode single sequence
encoding = tokenizer.encode("Hello, world!")
print(encoding.tokens)  # ["[CLS]", "hello", ",", "world", "!", "[SEP]"]

# Encode sequence pair
encoding = tokenizer.encode("Question?", "Answer.")
print(encoding.tokens)   # ["[CLS]", "question", "?", "[SEP]", "answer", ".", "[SEP]"]
print(encoding.type_ids) # [0, 0, 0, 0, 1, 1, 1]
```

### RoBERTa-style Formatting

Use `<s>` and `</s>` tokens:

```python
from tokenizers.processors import RobertaProcessing

tokenizer.post_processor = RobertaProcessing(
    bos="<s>",
    eos="</s>",
    add_prefix_space=True
)

encoding = tokenizer.encode("Hello, world!")
print(encoding.tokens)  # ["<s>", "hello", ",", "world", "!", "</s>"]
```

### T5-style Formatting

Add task prefix and sequence markers:

```python
from tokenizers.processors import TemplateProcessing

tokenizer.post_processor = TemplateProcessing(
    single="<pad> $A </s>",
    pair="<pad> $A </s> $B:1 </s>:1",
    special_tokens=[
        ("<pad>", tokenizer.token_to_id("<pad>")),
        ("</s>", tokenizer.token_to_id("</s>"))
    ]
)
```

## Padding and Truncation with Special Tokens

### Enable Padding

Configure automatic padding with special tokens:

```python
tokenizer.enable_padding(
    length=128,              # Target sequence length
    pad_id=1,                # ID of padding token
    pad_token="[PAD]"        # Padding token string
)

# Now batch encoding pads to length 128
encodings = tokenizer.encode_batch([
    "Short text",
    "This is a longer text that will still be padded to 128 tokens"
])

print(encodings[0].attention_mask)  # [1, 1, 1, ..., 0, 0, 0] (1s for real tokens, 0s for padding)
```

### Padding Strategies

Different padding strategies for different use cases:

```python
# Pad to longest sequence in batch
tokenizer.enable_padding(length=None)  # Automatic

# Pad to fixed length
tokenizer.enable_padding(length=512)

# Pad with specific token and ID
tokenizer.enable_padding(
    length=128,
    pad_id=3,
    pad_token="[PAD]",
    pair_pad_id=3
)
```

### Enable Truncation

Configure truncation while preserving special tokens:

```python
from tokenizers import TruncationStrategy

tokenizer.enable_truncation(
    length=512,
    strategy=TruncationStrategy.LongestFirst,  # Options: LongestFirst, ShortestFirst, OnlyFirst, OnlySecond
    max_length=512
)

# For sequence pairs, truncate longest sequence first
encoding = tokenizer.encode("Very long question...", "Answer.")
print(len(encoding.ids))  # ≤ 512
```

## Working with Special Token IDs

### Getting Token IDs

```python
# Get ID of specific token
unk_id = tokenizer.token_to_id("[UNK]")
pad_id = tokenizer.token_to_id("[PAD]")
cls_id = tokenizer.token_to_id("[CLS]")

# Get token from ID
token = tokenizer.id_to_token(0)  # "[UNK]"
token = tokenizer.id_to_token(1000)  # Some vocabulary token
```

### Checking for Special Tokens

```python
# Check if token is special
def is_special_token(tokenizer, token_id):
    special_ids = [
        tokenizer.token_to_id("[UNK]"),
        tokenizer.token_to_id("[PAD]"),
        tokenizer.token_to_id("[CLS]"),
        tokenizer.token_to_id("[SEP]")
    ]
    return token_id in special_ids

# Filter out special tokens from encoding
encoding = tokenizer.encode("Hello, world!")
non_special_tokens = [
    token for token, id_ in zip(encoding.tokens, encoding.ids)
    if not is_special_token(tokenizer, id_)
]
```

### Creating Attention Masks

Manually create attention masks that ignore special tokens:

```python
def create_attention_mask(encoding, special_ids_to_ignore):
    """Create attention mask excluding specified special token IDs."""
    return [1 if id_ not in special_ids_to_ignore else 0 for id_ in encoding.ids]

# Ignore padding tokens
pad_id = tokenizer.token_to_id("[PAD]")
attention_mask = create_attention_mask(encoding, [pad_id])
```

## Model-Specific Special Token Configurations

### BERT Configuration

```python
from tokenizers import Tokenizer
from tokenizers.models import WordPiece
from tokenizers.trainers import WordPieceTrainer
from tokenizers.processors import TemplateProcessing

tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))

trainer = WordPieceTrainer(
    vocab_size=30522,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"]
)

tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[
        ("[CLS]", tokenizer.token_to_id("[CLS]")),
        ("[SEP]", tokenizer.token_to_id("[SEP]"))
    ]
)

# Token IDs after training:
# [UNK] = 0, [CLS] = 1, [SEP] = 2, [PAD] = 3, [MASK] = 4
```

### GPT-2 Configuration

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder

tokenizer = Tokenizer(BPE())
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=True)
tokenizer.decoder = ByteLevelDecoder(add_prefix_space=True)

trainer = BpeTrainer(
    vocab_size=50257,
    special_tokens=["<|endoftext|>"]  # GPT-2 uses single special token
)

# GPT-2 doesn't use post-processing for special tokens
```

### RoBERTa Configuration

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder
from tokenizers.processors import RobertaProcessing

tokenizer = Tokenizer(BPE())
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=True)
tokenizer.decoder = ByteLevelDecoder(add_prefix_space=True)

trainer = BpeTrainer(
    vocab_size=50265,
    special_tokens=["<s>", "</s>", "<pad>"]
)

tokenizer.post_processor = RobertaProcessing(
    bos="<s>",
    eos="</s>",
    add_prefix_space=True
)
```

### T5 Configuration

```python
from tokenizers import Tokenizer
from tokenizers.models import Unigram
from tokenizers.trainers import UnigramTrainer
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder
from tokenizers.processors import TemplateProcessing

tokenizer = Tokenizer(Unigram())
tokenizer.pre_tokenizer = ByteLevel()
tokenizer.decoder = ByteLevelDecoder()

trainer = UnigramTrainer(
    vocab_size=32128,
    special_tokens=["<pad>", "</s>", "<unk>"]
)

tokenizer.post_processor = TemplateProcessing(
    single="<pad> $A </s>",
    pair="<pad> $A </s> $B:1 </s>:1",
    special_tokens=[
        ("<pad>", tokenizer.token_to_id("<pad>")),
        ("</s>", tokenizer.token_to_id("</s>"))
    ]
)
```

### LLaMA Configuration

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder

# LLaMA tokenizer configuration
tokenizer = Tokenizer(BPE())
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=True)
tokenizer.decoder = ByteLevelDecoder(add_prefix_space=True)

# Load from Hugging Face (pretrained)
from transformers import AutoTokenizer
llama_tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# Special tokens in LLaMA:
# <s> = BOS token
# </s> = EOS token
# <unk> = Unknown token
```

## Custom Special Tokens

### Adding Domain-Specific Tokens

For domain-specific applications, add custom special tokens:

```python
from tokenizers import AddedToken

# Add medical domain tokens
medical_tokens = [
    AddedToken("<DRUG>", single_word=True),
    AddedToken("<DOSE>", single_word=True),
    AddedToken("<SYMPTOM>", single_word=True)
]

tokenizer.add_tokens(medical_tokens)

# Use in templates
from tokenizers.processors import TemplateProcessing

tokenizer.post_processor = TemplateProcessing(
    single="$A",
    pair="$A:0 $B:1",
    special_tokens=[
        ("<DRUG>", tokenizer.token_to_id("<DRUG>")),
        ("<DOSE>", tokenizer.token_to_id("<DOSE>"))
    ]
)
```

### Reserved Token Ranges

Reserve ID ranges for future tokens:

```python
# Reserve IDs 1000-1999 for custom tokens
reserved_tokens = [f"[RESERVED_{i}]" for i in range(1000)]

trainer = BpeTrainer(
    vocab_size=30000,
    special_tokens=["[UNK]"] + reserved_tokens  # Add to training config
)
```

## Debugging Special Tokens

### Inspecting Special Token Configuration

```python
# Get all special tokens
special_tokens = tokenizer.get_special_tokens()
for token in special_tokens:
    print(f"ID {token['id']}: {token['content']} (type: {token.get('type', 'special')})")

# Check specific token IDs
print(f"[UNK] ID: {tokenizer.token_to_id('[UNK]')}")
print(f"[PAD] ID: {tokenizer.token_to_id('[PAD]')}")
print(f"Vocabulary size: {tokenizer.get_vocab_size()}")
```

### Verifying Special Token Behavior

```python
# Test that special tokens are preserved during encoding
encoding = tokenizer.encode("[CLS] Hello [SEP]")
print(encoding.tokens)  # Should include [CLS] and [SEP] as separate tokens

# Test padding includes correct token
tokenizer.enable_padding(length=20, pad_id=tokenizer.token_to_id("[PAD]"), pad_token="[PAD]")
encoding = tokenizer.encode("Short")
print([t for t in encoding.tokens if t == "[PAD]"])  # Should show padding tokens
```

## Next Steps

- [API Reference](references/07-api-reference.md) - Complete API documentation for all tokenizer methods
