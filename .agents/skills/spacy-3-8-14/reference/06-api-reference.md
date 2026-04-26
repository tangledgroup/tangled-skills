# API Reference

## Container Objects

### Doc

The `Doc` object owns the sequence of tokens and all annotations:

```python
doc = nlp("Hello world")
print(len(doc))           # Number of tokens
print(doc.text)           # Full text
print(doc[0].text)        # First token
print(doc[0:2].text)      # Span of first two tokens
print(doc.vocab)          # Shared vocabulary
```

**Key attributes:**

- `doc.text` — Original text
- `doc[len]` — Number of tokens
- `doc.ents` — Named entity spans
- `doc.sents` — Sentence spans
- `doc.noun_chunks` — Noun phrase spans
- `doc.cats` — Text category scores (dict)
- `doc.tensor` — NumPy array of token vectors
- `doc.spans` — Named SpanGroup collections
- `doc.user_data` — Custom user data (serialized with DocBin)
- `doc.is_nered` — Whether NER has been run

**Methods:**

- `doc.similarity(other_doc)` — Similarity score
- `doc.to_array(attrs)` — Extract attributes as numpy array
- `doc.to_bytes()` — Serialize to bytes
- `doc.from_bytes(data)` — Deserialize from bytes
- `doc.retokenize()` — Context manager for merging/splitting tokens
- `doc.user_hooks` — Custom formatting hooks

### Token

A `Token` is a view into a `Doc` (not standalone):

```python
doc = nlp("The cat sat")
token = doc[1]  # "cat"
print(token.text)      # "cat"
print(token.lemma_)    # "cat"
print(token.pos_)      # "NOUN"
print(token.tag_)      # "NN"
print(token.dep_)      # "nsubj"
print(token.head)      # Head token
print(token.children)  # Child tokens
print(token.idx)       # Character index in text
print(token.i)         # Token index
print(token.sent)      # Sentence span
```

**Key attributes:**

- `token.text` — Token text
- `token.lemma_` — Lemma
- `token.pos_` / `token.tag_` — POS tags (coarse/fine)
- `token.dep_` — Dependency label
- `token.head` — Head token
- `token.ent_type_` / `token.ent_iob_` — Entity annotation
- `token.morph` — Morphological features
- `token.is_alpha`, `token.is_stop`, `token.is_punct`, etc. — Flags
- `token.vector` — Word vector (if available)
- `token.similarity(other)` — Similarity to another token

### Span

A `Span` is a slice of a `Doc`:

```python
doc = nlp("The big cat sat on the mat")
span = doc[0:3]  # "The big cat"
print(span.text)       # "The big cat"
print(span.root)       # Root token of the span
print(span.label_)     # Label (if set)
print(list(span.tokens))  # Individual tokens
```

**Creating Spans with labels:**

```python
from spacy.tokens import Span
entity = Span(doc, 0, 2, label="GPE")
```

**Key attributes:**

- `span.text` — Span text
- `span.root` — Root token (most dependent on others)
- `span.label_` — Label (for entities)
- `span.start` / `span.end` — Token indices
- `span.start_char` / `span.end_char` — Character offsets
- `span.similarity(other)` — Similarity score

**Methods:**

- `span.as_doc()` — Copy span as standalone Doc

### SpanGroup

Named collections of spans belonging to a Doc:

```python
doc.spans["my_key"] = [span1, span2, span3]
for group in doc.spans.get("my_key", []):
    print(group.text, group.label_)
```

### Vocab

The shared vocabulary storing strings, vectors, and lexical data:

```python
vocab = nlp.vocab
print(vocab["hello"])         # Lexeme
print(vocab.strings[12345])   # String from hash
print(len(vocab))             # Number of entries
```

**Key attributes:**

- `vocab.strings` — StringStore (hash ↔ string mapping)
- `vocab.vectors` — Word vectors
- `vocab.lookups` — Lookup tables (lemmatization, etc.)
- `vocab.lengths` — Token length cache

### Lexeme

A word type with no context:

```python
lexeme = nlp.vocab["running"]
print(lexeme.text)      # "running"
print(lexeme.is_alpha)  # True
print(lexeme.shape_)    # "xxxx"
```

### DocBin

Efficient binary serialization for collections of Docs:

```python
from spacy.tokens import DocBin
import srsly

# Serialize
docs = [nlp(text) for text in texts]
docbin = DocBin(docs=docs)
docbin.to_disk("corpus.spacy")

# Deserialize
docbin = DocBin().from_disk("corpus.spacy")
restored_docs = docbin.get_docs(nlp.vocab)
```

## Serialization

### to_bytes / from_bytes

```python
# Language object
data = nlp.to_bytes()
nlp.from_bytes(data)

# Doc
data = doc.to_bytes()
doc.from_bytes(data)
```

### to_disk / from_disk

```python
# Save pipeline
nlp.to_disk("./model")

# Load pipeline
nlp.from_disk("./model")
```

### Pickle

```python
import pickle

# Save
with open("model.pkl", "wb") as f:
    pickle.dump(nlp, f)

# Load
with open("model.pkl", "rb") as f:
    nlp = pickle.load(f)
```

**Warning:** Don't unpickle objects from untrusted sources. Pickle executes arbitrary code.

### Saving Meta and Config

```python
import json

# Save metadata
with open("meta.json", "w") as f:
    json.dump(nlp.meta, f)

# Config is saved as config.cfg when using nlp.to_disk()
```

## Extension Attributes

### Attribute Setters

```python
from spacy.tokens import Doc, Token, Span

Doc.set_extension("source", default="unknown")
Token.set_extension("is_keyword", default=False)
Span.set_extension("score", default=0.0)
```

### Getters

```python
Token.set_extension("has_exclamation", getter=lambda t: t.text.endswith("!"))
Span.set_extension("word_count", getter=lambda s: len(list(s)))
```

### Setters

```python
def set_source(value):
    def setter(doc):
        doc._.source = value
    return setter

Doc.set_extension("source", getter=lambda d: getattr(d, "_source", "unknown"), setter=setter("api"))
```

## Memory Management

### Memory Zones (v3.8+)

Free data from internal caches for persistent services:

```python
nlp = spacy.load("en_core_web_sm")

def process_request(text):
    with nlp.memory_zone():
        doc = nlp(text)
        results = extract_entities(doc)
        return results  # Return extracted data, not the doc
    # Memory freed here
```

**Critical:** Don't access Doc/Token/Span/Lexeme objects after the memory zone exits — this causes segmentation faults.

### doc_cleaner Component

Cleans up intermediate attributes to prevent GPU memory exhaustion:

```python
nlp.add_pipe("doc_cleaner", last=True)
```

### Efficient Processing

```python
# Use nlp.pipe for batching
for doc in nlp.pipe(texts, batch_size=500, n_process=4):
    process(doc)

# Disable unused components
for doc in nlp.pipe(texts, disable=["tagger", "parser"]):
    process(doc)
```

## Command Line Interface

### Core Commands

```bash
# Download a model
python -m spacy download en_core_web_sm

# Validate installed pipelines
python -m spacy validate

# Info about spaCy installation
python -m spacy info

# Train a pipeline
python -m spacy train config.cfg --output ./output

# Initialize config
python -m spacy init config base.cfg --lang en --pipeline ner
python -m spacy init fill-config base.cfg filled.cfg

# Debug tools
python -m spacy debug config config.cfg
python -m spacy debug data config.cfg --paths.train train.spacy --paths.dev dev.spacy

# Convert data formats
python -m spacy convert input/ output/ --converter ner

# Package a model
python -m spacy package ./model ./packages --version 1.0.0

# Profile pipeline
python -m spacy profile data.txt --model en_core_web_sm
```

### Project Commands

```bash
# Clone a project
python -m spacy project clone pipelines/tagger_parser_ud

# Download assets
python -m spacy project assets

# Run a command
python -m spacy project run train

# List commands
python -m spacy project list
```

## Top-Level API

```python
import spacy

# Load pipeline
nlp = spacy.load("en_core_web_sm")

# Blank pipeline
nlp = spacy.blank("en")

# Explain labels
spacy.explain("VERB")    # "verb"
spacy.explain("GPE")     # "countries, cities, states"

# GPU management
spacy.prefer_gpu()
spacy.require_gpu()
spacy.util.filter_spans(spans)  # Remove overlapping spans

# Registry
spacy.registry.all()          # List all registered functions
spacy.registry.readers        # Registered data readers
spacy.registry.architectures  # Registered model architectures
```

## Visualizers (displaCy)

```python
from spacy import displacy

# Named entities
displacy.serve(doc, style="ent")       # Web server
displacy.render(doc, style="ent")      # HTML output
displacy.render(doc, style="ent", jupyter=True)  # Jupyter notebook

# Dependency parse
displacy.serve(doc, style="dep")
displacy.render(doc, style="dep", options={"compact": "ROOT"})

# Multiple documents
displacy.serve(docs, style="ent", page_title="NER Results")

# Save to file
html = displacy.render(doc, style="ent")
with open("entities.html", "w") as f:
    f.write(html)
```
