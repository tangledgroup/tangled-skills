# Pipeline Components

## Overview

The processing pipeline consists of one or more **pipeline components** called on the `Doc` in order. The tokenizer runs before the components. Pipeline components can be added using `Language.add_pipe()`. They can contain a statistical model and trained weights, or only make rule-based modifications to the Doc.

### Component Order

The statistical components (tagger, parser, NER) are typically independent and don't share data between each other. You can swap or remove them without affecting others. However:

- Components may share a **token-to-vector** component like `Tok2Vec` or `Transformer`
- Custom components may depend on annotations set by other components (e.g., a lemmatizer needing POS tags)
- The parser respects pre-defined sentence boundaries from earlier components
- `EntityRuler` before `EntityRecognizer` — the recognizer will take existing entities into account
- `EntityLinker` should be preceded by a component that recognizes entities

## Built-in Components

### Tokenizer (`tokenizer`)

- **Creates**: `Doc`
- Segments raw text into tokens (words, punctuation, whitespace)
- Special: takes a string and produces a Doc (not part of regular pipeline)
- `nlp.tokenizer` is writable — replace with custom class or function

### Tagger (`tagger`)

- **Creates**: `Token.tag_`
- Predicts fine-grained part-of-speech tags
- Statistical model trained on labeled data

### DependencyParser (`parser`)

- **Creates**: `Token.head`, `Token.dep_`, `Doc.sents`, `Doc.noun_chunks`
- Predicts syntactic dependency labels describing relations between tokens
- Also sets sentence boundaries and noun chunks as a side effect

### EntityRecognizer (`ner`)

- **Creates**: `Doc.ents`, `Token.ent_iob_`, `Token.ent_type_`
- Detects and labels named entities (persons, organizations, locations, etc.)
- Statistical model

### Lemmatizer (`lemmatizer`)

- **Creates**: `Token.lemma_`
- Determines base forms of words using rules and lookups
- Rule-based (not trainable) — uses data from `spacy-lookups-data`

### EditTreeLemmatizer (`edittreelemmatizer`)

- **Creates**: `Token.lemma_`
- Predicts base forms of words
- Trainable statistical lemmatizer using edit trees

### Morphologizer (`morphologizer`)

- **Creates**: `Token.morph`, `Token.pos_`
- Predicts morphological features and coarse-grained POS tags
- Statistical model (v3.0+)

### TextCategorizer (`textcat`)

- **Creates**: `Doc.cats`
- Predicts categories or labels over the whole document
- Supports single-label and multi-label classification

### SpanCategorizer (`spancat`)

- Predicts categories for spans within a document
- Useful when you need to classify specific text regions

### Sentencizer (`sentencizer`)

- Rule-based sentence boundary detection
- Does not require dependency parse
- Use when parser is disabled but sentence boundaries are needed

### SentenceRecognizer (`sentencerecognizer`)

- Predicts sentence boundaries statistically
- More accurate than sentencizer for complex text

### EntityLinker (`entitylinker`)

- Disambiguates named entities to nodes in a knowledge base
- Requires `InMemoryLookupKB` or custom `KnowledgeBase`
- Must be preceded by an entity recognizer

### EntityRuler (`entityruler`)

- Adds entity spans using token-based rules or exact phrase matches
- Rule-based, no training needed
- Can merge with statistical NER

### SpanRuler (`spanruler`)

- Matches patterns and creates `SpanGroup` collections
- More flexible than EntityRuler — doesn't require entity labels
- Supports custom attributes on matched spans

### AttributeRuler (`attributeruler`)

- Sets token attributes using matcher rules
- Useful for overriding or adding annotations based on patterns

### Tok2Vec (`tok2vec`)

- Applies a token-to-vector model and sets its outputs
- Can be shared across multiple downstream components
- Key to multi-task learning efficiency

### Transformer (`transformer`)

- Uses a transformer model (BERT, RoBERTa, etc.) and sets its outputs
- Requires `spacy-transformers` package
- Provides contextual embeddings for downstream components

### CoreferenceResolver (`coref`)

- Resolves coreferences (pronouns to their referents)
- Experimental component
- Creates `SpanGroup` with coreferent spans

### SpanFinder (`spanfinder`)

- Finds candidate spans for entity linking or other span-based tasks

### SpanResolver (`spanresolver`)

- Resolves spans to canonical representations

## Custom Components

You can add custom pipeline components:

```python
def my_component(doc):
    # Modify doc in place
    return doc

nlp.add_pipe(my_component, name="my_component")
```

Or use the decorator pattern:

```python
@Language.component
def lower_all_tokens(doc):
    for token in doc:
        token._.lower = token.text.lower()
    return doc

nlp.add_pipe("lower_all_tokens")
```

For trainable custom components, inherit from `TrainablePipe`:

```python
from spacy.pipeline import TrainablePipe

class MyComponent(TrainablePipe):
    def __init__(self, nlp, name="my_component"):
        super().__init__(nlp=nlp, name=name)

    def __call__(self, doc):
        return doc

    def initialize(self, examples=None, **kwargs):
        pass
```

## Extension Attributes

Add custom attributes to `Doc`, `Token`, and `Span`:

```python
from spacy.tokens import Doc, Token, Span

# Attribute setter
Doc.set_extension("source", default="unknown")
Token.set_extension("is_keyword", default=False)
Span.set_extension("confidence", default=0.0)

# Usage
doc._.source = "twitter"
token._.is_keyword = True
span._.confidence = 0.95
```

With methods and properties:

```python
Token.set_extension("has_exclamation", getter=lambda t: t.text.endswith("!"))
Span.set_extension("word_count", getter=lambda s: len(list(s.tokens)))
```

## Disabling Components

Disable components during processing or loading:

```python
# At load time
nlp = spacy.load("en_core_web_sm", disable=["ner", "tagger"])

# During processing
for doc in nlp.pipe(texts, disable=["parser"]):
    pass
```

## Serialization

Pipeline components are serialized via `nlp.to_disk()` and `nlp.from_disk()`:

```python
# Save
nlp.to_disk("./model")

# Load
nlp.from_disk("./model")
```

The config (`config.cfg`) must also be saved to fully restore the pipeline:

```python
import json
with open("meta.json", "w") as f:
    json.dump(nlp.meta, f)
```

## The `doc_cleaner` Component

Added in v3.8 — cleans up intermediate Doc attributes (Transformer tensors, Tok2Vec data) to prevent GPU memory exhaustion:

```python
nlp.add_pipe("doc_cleaner", last=True)
```

By default cleans `Doc._.trf_data` and `Doc.tensor`. Can be configured to clean custom extension attributes.
