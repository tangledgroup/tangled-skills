# Processor Details

This reference covers each processor in Stanza's neural pipeline with detailed examples and configuration options.

## Tokenize Processor

Segments raw text into sentences and tokens.

### Output Annotations

- Sentence boundaries
- Token boundaries within sentences
- Multi-word token (MWT) predictions

### Usage

```python
nlp = stanza.Pipeline('en', processors='tokenize')
doc = nlp("Hello world! How are you? I'm fine, thanks.")

for sent in doc.sentences:
    print(f"Sentence: {sent.text}")
    for token in sent.tokens:
        print(f"  Token {token.id}: {token.text}")
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `tokenize_pretokenized` | `False` | Use pretokenized input (space-separated) |
| `tokenize_omit_spaces` | `False` | Omit spaces from token text |
| `tokenize_language_specific_rules` | `True` | Apply language-specific tokenization rules |

### Pre-tokenized Input

```python
nlp = stanza.Pipeline(
    'en',
    processors='tokenize,pos',
    tokenize_pretokenized=True
)

# Input: sentences separated by ". ", tokens by spaces
text = "Hello world . How are you ?"
doc = nlp(text)
```

## MWT (Multi-Word Token) Processor

Expands multi-word tokens into constituent words.

### When MWTs Occur

- French: "au" → "à le", "du" → "de le"
- German: compound verbs, particle verbs
- Arabic: definite article attachments
- Many languages: contractions, clitics

### Usage

```python
nlp = stanza.Pipeline('fr', processors='tokenize,mwt')
doc = nlp("Je vais au marché.")

for token in doc.sentences[0].tokens:
    if len(token.words) > 1:
        print(f"MWT: {token.text} → {' '.join(w.text for w in token.words)}")
        # Output: MWT: au → à le
```

### Language Support

MWT processor is not implemented for languages without multi-word tokens (e.g., Chinese).

## POS (Part-of-Speech) Processor

Tags words with universal and treebank-specific POS tags, plus morphological features.

### Output Annotations

| Property | Description | Example |
|----------|-------------|---------|
| `word.upos` | Universal POS tag | 'NOUN', 'VERB', 'ADJ' |
| `word.xpos` | Treebank-specific POS | 'NNP', 'VBZ', 'JJ' |
| `word.feats` | Morphological features | 'Gender=Fem\|Number=Sing' |

### Universal POS Tags (UPOS)

17 universal categories: ADJ, ADP, ADV, AUX, CCONJ, DET, INTJ, NOUN, NUM, PART, PRON, PUNCT, VERB, PROPN, SCONJ, SYM, X

### Usage

```python
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos')
doc = nlp("The quick brown fox jumps over the lazy dog.")

for word in doc.sentences[0].words:
    print(f"{word.text:10s} UPOS: {word.upos:8s} XPOS: {word.xpos or '_':4s} FEATS: {word.feats or '_'}")
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `pos_batch_size` | 512 | Batch size for inference |
| `pos_iter` | 10 | Number of training iterations (for fine-tuning) |
| `pos_pretrain_path` | None | Path to word vector file |
| `pos_charlm` | `False` | Use character language model |

## Lemma Processor

Generates base forms (lemmas) for all words.

### Usage

```python
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos,lemma')
doc = nlp("The cats were running quickly.")

for word in doc.sentences[0].words:
    print(f"{word.text:15s} → {word.lemma}")
# Output:
# The               → the
# cats              → cat
# were              → be
# running           → run
# quickly           → quickly
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `lemma_batch_size` | 512 | Batch size for inference |
| `lemma_pretrain_path` | None | Path to word vector file |

## Depparse (Dependency Parsing) Processor

Determines syntactic head and dependency relation for each word.

### Output Annotations

| Property | Description | Example |
|----------|-------------|---------|
| `word.head` | ID of syntactic head | 4 |
| `word.deprel` | Dependency relation | 'nsubj', 'obj', 'nmod' |

### Universal Dependency Relations

Common relations: root, nsubj, obj, iobj, nmod, appos, advcl, acl, obl, aux, ccomp, xcomp, cc, conj, punct, etc.

### Usage

```python
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos,lemma,depparse')
doc = nlp("The cat sat on the mat.")

sentence = doc.sentences[0]

# Print dependency tree
sentence.print_dependencies()
# Output:
# ('The', '3', 'det')
# ('cat', '3', 'nsubj')
# ('sat', '0', 'root')
# ('on', '3', 'case')
# ('the', '6', 'det')
# ('mat', '3', 'obl')
# ('.', '3', 'punct')

# Access dependencies programmatically
for head_word, deprel, dep_word in sentence.dependencies:
    print(f"{dep_word.text} --{deprel}--> {head_word.text}")
```

### Enhanced Dependencies

Access enhanced (implicit) dependencies:

```python
from stanza.models.depparse import evaluate

# Enhanced dependencies include implicit relations
for word in doc.sentences[0].words:
    print(f"{word.id}: head={word.head}, deprel={word.deprel}, deps={word.deps}")
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `depparse_batch_size` | 64 | Batch size for inference |
| `depparse_iter` | 100 | Training iterations |
| `depparse_pretrain_path` | None | Path to word vector file |
| `depparse_charlm` | `False` | Use character LM |
| `depparse_eager` | `True` | Eager parsing mode |

## NER (Named Entity Recognition) Processor

Recognizes named entities and assigns BIOES tags.

### Entity Types

Common types: PERSON, ORGANIZATION (ORG), LOCATION (LOC), GPE (geopolitical entity), DATE, TIME, MONEY, PERCENT, FACILITY, PRODUCT, EVENT, WORK_OF_ART, LAW

### Usage

```python
nlp = stanza.Pipeline('en', processors='tokenize,mwt,ner')
doc = nlp("Barack Obama was born in Hawaii and became president in 2008.")

# Access entities as Spans
for entity in doc.entities:
    print(f"{entity.type}: {entity.text}")
# Output:
# PERSON: Barack Obama
# GPE: Hawaii
# DATE: 2008

# Access token-level BIOES tags
for token in doc.sentences[0].tokens:
    if token.ner:
        print(f"{token.text}: {token.ner}")
# Output:
# Barack: B-PERSON
# Obama: I-PERSON
# Hawaii: B-GPE
```

### BIOES Tag Format

- **B-TYPE**: Begin entity
- **I-TYPE**: Inside entity
- **E-TYPE**: End entity (for single-token entities in some schemes)
- **S-TYPE**: Single-token entity
- **O**: Outside any entity

### Package Selection

```python
# Use OntoNotes model (default for English)
nlp = stanza.Pipeline('en', processors='ner', package='ontonotes')

# Use CoNLL 2000 model
nlp = stanza.Pipeline('en', processors='ner', package='conll2000')

# Use OntoNotes 14.0
nlp = stanza.Pipeline('en', processors='ner', package='ontonotes14')
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `ner_batch_size` | 64 | Batch size for inference |
| `ner_pretrain_path` | None | Path to word vector file |
| `ner_charlm` | `False` | Use character LM |

## Sentiment Processor

Assigns sentiment scores to sentences.

### Sentiment Labels

- **0**: Negative
- **1**: Neutral
- **2**: Positive

### Usage

```python
nlp = stanza.Pipeline('en', processors='tokenize,mwt,sentiment')
doc = nlp("I love this product! It's terrible. Maybe it's okay.")

for sent in doc.sentences:
    sentiment_label = {'0': 'Negative', '1': 'Neutral', '2': 'Positive'}[sent.sentiment]
    print(f"{sent.text} → {sentiment_label}")
# Output:
# I love this product! → Positive
# It's terrible. → Negative
# Maybe it's okay. → Neutral
```

### Language Support

Sentiment models available for limited languages: English, Arabic, Persian, and a few others. Check available packages before use.

## Constituency Processor

Parses sentences into phrase structure trees.

### Usage

```python
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos,constituency')
doc = nlp("The quick brown fox jumps.")

sentence = doc.sentences[0]
parse_tree = sentence.constituency

# Print tree recursively
def print_tree(node, indent=0):
    print("  " * indent + node.label)
    for child in node.children:
        print_tree(child, indent + 1)

print_tree(parse_tree)
# Output:
# ROOT
#   SENTENCE
#     NP
#       DET The
#       ADJ quick
#       ADJ brown
#       NOUN fox
#     VP
#       VERB jumps
```

### Tree Traversal

```python
# Find all noun phrases
def find_nps(node):
    if node.label == 'NP':
        return [node] + sum([find_nps(child) for child in node.children], [])
    elif node.children:
        return sum([find_nps(child) for child in node.children], [])
    return []

nps = find_nps(parse_tree)
for np in nps:
    # Extract words in NP
    words = extract_words(np)
    print(' '.join(words))
```

### Language Support

Constituency models available for English, Chinese, Arabic, French, and a few other languages.

## LangID (Language Identification) Processor

Identifies the language of input text.

### Usage

```python
# LangID is language-independent
nlp = stanza.Pipeline('langid')

texts = ["Hello world", "Bonjour le monde", "Hallo Welt", "Hola mundo"]
for text in texts:
    doc = nlp(text)
    print(f"{text} → {doc.lang}")
# Output:
# Hello world → en
# Bonjour le monde → fr
# Hallo Welt → de
# Hola mundo → es
```

### Confidence Scores

```python
# Access language probabilities (if available)
doc = nlp("Hello world")
print(f"Detected language: {doc.lang}")
# Some implementations provide confidence scores
```

## Coreference Processor (via CoreNLP)

Resolves coreferences between noun phrases.

**Note:** Coreference resolution is only available through the CoreNLP Java client, not the native neural pipeline.

### Usage via CoreNLP Client

```python
from stanza.server import CoreNLPClient

with CoreNLPClient(annotators='tokenize,ssplit,pos,ner,coref') as client:
    doc = client.annotate("Stephen was in the kitchen. He was cooking.")
    
    # Access coreference chains
    for chain in doc.corefs[0].chains:
        print(f"Chain: {[m.text for m in chain.mentions]}")
    # Output: Chain: ['Stephen', 'He']
```

See [CoreNLP Client](references/07-corenlp-client.md) for setup details.

## Processor Order and Dependencies

Processors must be executed in dependency order:

```
tokenize → mwt → pos → lemma → depparse
    ↓       ↓
    └──→ ner (needs tokenize, mwt)
    ↓
    └──→ sentiment (needs tokenize, mwt)
    ↓
    └──→ constituency (needs tokenize, mwt, pos)
```

### Valid Processor Combinations

```python
# Valid: respects dependencies
nlp = stanza.Pipeline('en', processors='tokenize,pos,depparse')

# Invalid: depparse needs pos and lemma
# nlp = stanza.Pipeline('en', processors='tokenize,depparse')  # Error!

# Stanza auto-adds required dependencies
nlp = stanza.Pipeline('en', processors='depparse')
# Automatically includes: tokenize, mwt, pos, lemma, depparse
```

## Performance Tips

### Batching

Process multiple sentences together for best performance:

```python
# Slow: one sentence at a time
for sentence in sentences:
    doc = nlp(sentence)

# Fast: batch all sentences
text = '\n\n'.join(sentences)
doc = nlp(text)
```

### GPU Acceleration

Enable GPU for faster inference:

```python
nlp = stanza.Pipeline('en', use_gpu=True)
```

### Selective Processing

Only load needed processors:

```python
# Fastest: only tokenization
nlp = stanza.Pipeline('en', processors='tokenize')

# Light syntax analysis
nlp = stanza.Pipeline('en', processors='tokenize,pos')

# Skip expensive depparse if not needed
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos,lemma,ner')
```
