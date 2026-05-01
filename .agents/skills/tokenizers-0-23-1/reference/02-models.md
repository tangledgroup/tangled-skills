# Models Reference

Models are the core tokenization algorithms. They are the only mandatory component of a `Tokenizer`.

## BPE (Byte-Pair Encoding)

```python
from tokenizers.models import BPE

tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
```

BPE starts with all individual characters as tokens, then iteratively merges the most frequently co-occurring pairs. This creates a vocabulary that can represent unseen words through subword composition.

### Parameters

- `vocab` — Dict mapping token strings to IDs (`{"am": 0, ...}`)
- `merges` — List of merge pairs: `[("a", "b"), ...]`
- `cache_capacity` — Number of words to cache merge results for (speeds up tokenization)
- `dropout` — Float 0-1 for BPE dropout (randomly removes merges at inference time for robustness)
- `unk_token` — Token used for out-of-vocabulary items
- `continuing_subword_prefix` — Prefix for subwords that don't start a word (e.g., `##`)
- `end_of_word_suffix` — Suffix for subwords that end a word
- `fuse_unk` — Whether to fuse subsequent unknown tokens into one
- `byte_fallback` — Use SPM byte-fallback trick (defaults to False)
- `ignore_merges` — Match tokens with vocab before using merges

### Training

```python
from tokenizers.trainers import BpeTrainer

trainer = BpeTrainer(
    vocab_size=30000,           # Target vocabulary size
    min_frequency=2,            # Minimum pair frequency to merge
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
    limit_alphabet=1000,        # Max different characters in alphabet
    initial_alphabet=[],        # Characters to include even if not seen
    continuing_subword_prefix=None,
    end_of_word_suffix=None,
    max_token_length=25,        # Prevent overly long tokens
)
```

### BPE with ByteLevel Pre-tokenizer

The ByteLevel pre-tokenizer is the standard pairing with BPE for GPT-2 style tokenization:

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.trainers import BpeTrainer

tokenizer = Tokenizer(BPE())
tokenizer.pre_tokenizer = ByteLevel()

trainer = BpeTrainer(
    vocab_size=50000,
    initial_alphabet=ByteLevel.alphabet(),
)
```

Key properties of ByteLevel BPE:
- Only needs 256 characters as initial alphabet (one per byte value)
- No `[UNK]` token needed — any byte sequence can be represented
- Non-ASCII characters become unreadable but work correctly

## WordPiece

```python
from tokenizers.models import WordPiece

tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))
```

WordPiece is a greedy longest-match algorithm. It tries the full word first, then progressively shorter prefixes until finding a vocabulary match. Uses `##` prefix to mark continuing subwords. Used by BERT and many Google models.

### Training

```python
from tokenizers.trainers import WordPieceTrainer

trainer = WordPieceTrainer(
    vocab_size=30000,
    min_frequency=2,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
    limit_alphabet=None,
    initial_alphabet=[],
    continuing_subword_prefix="##",  # Default for WordPiece
    end_of_word_suffix=None,
)
```

### Importing Legacy BERT Tokenizer

```python
from tokenizers import BertWordPieceTokenizer

tokenizer = BertWordPieceTokenizer("bert-base-uncased-vocab.txt", lowercase=True)
```

## Unigram

```python
from tokenizers.models import Unigram

tokenizer = Tokenizer(Unigram())
```

Unigram is a probabilistic model that selects the tokenization maximizing the joint probability of all tokens. Unlike BPE and WordPiece (which are deterministic rule-based), Unigram can evaluate multiple possible segmentations and choose the most probable one. Used by mBART, XLM-R, and other multilingual models.

### Subword Regularization (0.23+)

Version 0.23 adds `alpha` and `nbest_size` parameters for subword regularization, bringing parity with Google's implementation:

```python
from tokenizers.models import Unigram

# Enable subword regularization
tokenizer = Tokenizer(Unigram(
    vocab=vocab_dict,
    scores=scores_dict,
    alpha=0.1,           # Smoothing parameter (0.0 = deterministic greedy)
    nbest_size=10,       # Number of candidates to consider for sampling
))
```

- `alpha` — Controls randomness: 0.0 gives deterministic greedy tokenization, higher values increase stochasticity
- `nbest_size` — Number of candidate segmentations to sample from (larger = more diverse but slower)

### Training

```python
from tokenizers.trainers import UnigramTrainer

trainer = UnigramTrainer(
    vocab_size=8000,
    special_tokens=["<PAD>", "<BOS>", "<EOS>"],
    initial_alphabet=ByteLevel.alphabet(),
    shrinking_factor=0.75,     # Pruning factor at each training step
    unk_token=None,
    max_piece_length=16,       # Max length of a single token
    n_sub_iterations=2,        # EM iterations before pruning
)
```

### Unigram with ByteLevel (GPT-style)

```python
from tokenizers import Tokenizer, decoders
from tokenizers.models import Unigram
from tokenizers.normalizers import NFKC
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.trainers import UnigramTrainer

tokenizer = Tokenizer(Unigram())
tokenizer.normalizer = NFKC()
tokenizer.pre_tokenizer = ByteLevel()
tokenizer.decoder = decoders.ByteLevel()

trainer = UnigramTrainer(
    vocab_size=20000,
    initial_alphabet=ByteLevel.alphabet(),
    special_tokens=["<PAD>", "<BOS>", "<EOS>"],
)
```

## WordLevel

```python
from tokenizers.models import WordLevel

tokenizer = Tokenizer(WordLevel())
```

WordLevel is the simplest model — it maps whole words to IDs with no subword splitting. Requires a pre-tokenizer (the model itself makes no splitting decisions). Needs very large vocabularies for good coverage.

### Training

```python
from tokenizers.trainers import WordLevelTrainer

trainer = WordLevelTrainer(
    vocab_size=30000,
    min_frequency=2,
    special_tokens=["[UNK]", "[CLS]", "[SEP]"],
)
```

## Model Comparison

- **BPE** — Best general-purpose choice. Good balance of vocabulary size and coverage. Used by GPT-2, RoBERTa, T5.
- **WordPiece** — Greedy longest-match, slightly different behavior from BPE. Standard for BERT-family models.
- **Unigram** — Probabilistic, handles ambiguity better. Best for multilingual. Now supports subword regularization (0.23+). Used by XLM-R, mBART.
- **WordLevel** — Simplest, no subword splitting. Only when you have a manageable vocabulary of complete words.
