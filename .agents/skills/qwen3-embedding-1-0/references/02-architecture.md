# Qwen3 Embedding Architecture

Technical deep-dive into the Qwen3 Embedding model architecture, tokenization, and internal mechanisms.

## Base Architecture

Qwen3 Embedding models are built on the **Qwen3-Base** causal language model architecture with modifications for embedding generation.

### Core Components

```
Input Text
    ↓
[Token Embeddings] ← Qwen3 Tokenizer (151K vocab)
    ↓
[Position Embeddings] ← RoPE (Rotary Positional Encoding)
    ↓
[Transformer Layers] × N (24-32 layers depending on variant)
    ↓
[Pooling Layer] ← Mean/CLS/Max pooling
    ↓
[Projection Layer] ← Optional dimension reduction
    ↓
Embedding Vector (1024-4096 dimensions)
```

### Model-Specific Configurations

| Component | 0.6B | 4B | 8B |
|-----------|------|----|----|
| **Hidden Size** | 1024 | 2560 | 4096 |
| **Attention Heads** | 16 | 32 | 40 |
| **Layers** | 24 | 36 | 40 |
| **Vocabulary Size** | 151,936 | 151,936 | 151,936 |
| **Embedding Dim** | 1024 | 1024 | 1024 |

## Tokenization

### Qwen3 Tokenizer

Qwen3 uses a sophisticated tokenizer with the following characteristics:

- **Vocabulary Size**: ~151,936 tokens
- **Algorithm**: Byte-level BPE (Byte-Pair Encoding)
- **Special Tokens**: `<|endoftext|>`, `<|im_start|>`, `<|im_end|>`
- **Language Coverage**: Optimized for English and Chinese with good multilingual support

### Tokenization Examples

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-Embedding-4B")

# English text
text_en = "The quick brown fox jumps over the lazy dog."
tokens_en = tokenizer(text_en, return_tensors="pt")
print(f"English: {len(text_en)} chars → {tokens_en['input_ids'].shape[1]} tokens")
# Output: English: 46 chars → 13 tokens

# Chinese text
text_zh = "这是一段测试文本。"
tokens_zh = tokenizer(text_zh, return_tensors="pt")
print(f"Chinese: {len(text_zh)} chars → {tokens_zh['input_ids'].shape[1]} tokens")
# Output: Chinese: 10 chars → 12 tokens

# Code
text_code = "def hello_world():\n    print('Hello, World!')"
tokens_code = tokenizer(text_code, return_tensors="pt")
print(f"Code: {len(text_code)} chars → {tokens_code['input_ids'].shape[1]} tokens"
