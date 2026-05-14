# Translation & Language Models

## IBM Alignment Models

NLTK implements IBM Models 1–5 for word alignment in statistical machine translation.

### IBM Model 1

The simplest model — assumes uniform alignment probabilities:

```python
from nltk.translate.ibm1 import IBMModel1

# Aligned sentences: list of (source, target) pairs
aligned_sents = [
    AlignedSent(['ich', 'bin', 'glücklich'], ['I', 'am', 'happy']),
    AlignedSent(['er', 'ist', 'klug'], ['he', 'is', 'smart']),
]

model = IBMModel1(aligned_sents)
model.burn_in(10)  # initial iterations
for i in range(20):
    model.train()

# Get alignment for a sentence pair
alignment = model.align(aligned_sents[0])
print(alignment)
```

### IBM Models 2–5

Progressively more sophisticated models incorporating position, fertility, and distortion:

```python
from nltk.translate.ibm2 import IBMModel2
from nltk.translate.ibm3 import IBMModel3
from nltk.translate.ibm4 import IBMModel4
from nltk.translate.ibm5 import IBMModel5

model = IBMModel2(aligned_sents)
for i in range(20):
    model.train()
```

- **IBM Model 2**: Adds positional alignment probabilities
- **IBM Model 3**: Adds fertility distribution (how many target words a source word generates)
- **IBM Model 4**: Adds distortion model (reordering probability)
- **IBM Model 5**: Adds vacancy/hubbiness (multiple words at same position)

### AlignedSent

Represents a parallel sentence pair with alignment information:

```python
from nltk.translate.api import AlignedSent

aligned = AlignedSent(
    source=['ich', 'bin'],
    target=['I', 'am'],
    alignment={(0, 0), (1, 1)}  # source_idx -> target_idx
)

print(aligned.words)   # source sentence
print(aligned.mots)    # target sentence
print(aligned.alignment)  # set of (source, target) pairs
```

### Phrase Extraction

Extract translation equivalents from aligned data:

```python
from nltk.translate.phrase_based import extract

phrase_table = extract(aligned_sents)
```

## Language Modeling

NLTK's language modeling package provides n-gram models with various smoothing techniques.

### Vocabulary and Counter

```python
from nltk.lm import Vocabulary
from nltk.lm.models import MLE
from nltk.lm.preprocessing import padded_everygram_pipeline

# Training data: list of token lists (sentences)
train_data = [
    ['the', 'cat', 'sat'],
    ['the', 'dog', 'ran'],
    ['the', 'cat', 'chased', 'the', 'dog'],
]

# Create vocabulary
vocab = Vocabulary(train_data)

# Prepare data pipeline (generates n-grams with padding)
data = padded_everygram_pipeline(order=3, sentences=train_data)
```

### Maximum Likelihood Estimation (MLE)

Unsmoothed n-gram model:

```python
from nltk.lm.models import MLE

lm = MLE(order=3, vocabulary=vocab)
lm.update(data)

# Score a sequence
score = lm.score('cat', ['the'])  # P('cat' | 'the')
print(score)

# Log probability
log_prob = lm.log_prob('cat', ['the'])
```

### Laplace Smoothing (Add-1)

```python
from nltk.lm.models import Laplace

lm = Laplace(order=3, vocabulary=vocab)
lm.update(data)
```

### Lidstone Smoothing (Add-alpha)

```python
from nltk.lm.models import Lidstone

lm = Lidstone(order=3, alpha=0.1, vocabulary=vocab)
lm.update(data)
```

### Witten-Bell Interpolation

```python
from nltk.lm.models import WittenBellInterpolated

lm = WittenBellInterpolated(order=3, vocabulary=vocab)
lm.update(data)
```

### Kneser-Ney Smoothing

State-of-the-art smoothing for n-gram models:

```python
from nltk.lm.models import KneserNeyInterpolated

lm = KneserNeyInterpolated(order=3, vocabulary=vocab)
lm.update(data)
```

### Absolute Discounting Interpolation

```python
from nltk.lm.models import AbsoluteDiscountingInterpolated

lm = AbsoluteDiscountingInterpolated(order=3, alpha=0.75, vocabulary=vocab)
lm.update(data)
```

### Stupid Backoff

Simple backoff without interpolation:

```python
from nltk.lm.models import StupidBackoff

lm = StupidBackoff(order=3, discount=0.4, vocabulary=vocab)
lm.update(data)
```

### Scoring and Perplexity

```python
# Score individual tokens
score = lm.score('happy', ['I', 'am'])  # P('happy' | 'I', 'am')

# Log probability of a sequence
log_prob = sum(lm.log_prob(w, context) for w, context in ...)

# Perplexity on test data
test_data = [['the', 'cat', 'ran'], ['a', 'dog', 'sat']]
test_pipeline = padded_everygram_pipeline(order=3, sentences=test_data)
perplexity = lm.perplexity(test_pipeline)
```

### Language Model Counter

Efficient counting for large corpora:

```python
from nltk.lm import NgramCounter

counter = NgramCounter(max_order=3)
for sent in train_data:
    counter.update(sent)

print(counter.N())  # total count
```

## Gale-Church Word Alignment

Statistical word alignment using the IBM models framework:

```python
from nltk.translate.gale_church import align_texts, parse_token_stream

# Align parallel texts
aligned = align_texts(
    source_text,
    target_text,
    iterations=20
)
```

## Grow-Diagonal-Final Alignment (GDFA)

Heuristic alignment algorithm:

```python
from nltk.translate.gdfa import grow_diag_final_and

alignment = grow_diag_final_and(source, target)
```

## Text Tiling

Document segmentation using the TextTiling algorithm:

```python
from nltk.tokenize import TextTilingTokenizer

tokenizer = TextTilingTokenizer()
segments = tokenizer.tokenize(text)
```
