# Processing Pipelines and Components

This guide covers spaCy's processing pipeline architecture, component types, and how to customize pipelines for your needs.

## Pipeline Architecture

A spaCy pipeline is a sequence of components that process text in order. Each component adds annotations to the `Doc` object.

```python
import spacy

nlp = spacy.load("en_core_web_sm")

# View pipeline components
print(nlp.pipe_names)
# ['tagger', 'parser', 'attribute_ruler', 'lemmatizer']

# Process text through all components
doc = nlp("The company announced record profits today.")
```

### Pipeline Execution Order

Components execute in order and can depend on previous components:

1. **Tokenizer** - Splits text into tokens (always first)
2. **Tagger** - Assigns POS tags (required by parser, lemmatizer)
3. **Parser** - Dependency parsing (requires tagger)
4. **Lemmatizer** - Lemmatization (can use parser or tagger)
5. **EntityRuler** - Rule-based NER
6. **NER** - Neural network NER
7. **TextCategorizer** - Document classification

```python
# Check component dependencies
for name, component in nlp.items():
    print(name, "requires:", component.requires)
```

## Component Types

### Built-in Components

spaCy includes these trainable components:

| Component | Factory Name | Description |
|-----------|--------------|-------------|
| Tagger | `tagger` | Part-of-speech tagging |
| Parser | `parser` | Dependency parsing |
| NER | `ner` | Named entity recognition |
| TextCategorizer | `textcat` | Document classification |
| Lemmatizer | `lemmatizer` | Word lemmatization |
| Morphologizer | `morphologizer` | Morphological analysis |
| Sentencizer | `sentencizer` | Rule-based sentence segmentation |
| Senter | `senter` | Neural sentence boundary detection |
| EntityRuler | `entity_ruler` | Rule-based entity extraction |
| AttributeRuler | `attribute_ruler` | Rule-based attribute assignment |
| SpanCatClassifier | `spancat` | Span classification |

### Adding Components

```python
import spacy

nlp = spacy.blank("en")

# Add a component
ner = nlp.add_pipe("ner")

# Add with specific name
textcat = nlp.add_pipe("textcat", name="sentiment")

# Insert at specific position
parser = nlp.add_pipe("parser", before="ner")

# Check pipeline
print(nlp.pipe_names)  # ['parser', 'ner', 'sentiment']
```

### Removing Components

```python
# Remove by name
nlp.remove_pipe("lemmatizer")

# Load without specific components
nlp = spacy.load("en_core_web_sm", exclude=["parser", "lemmatizer"])
```

## Custom Components

### Creating a Simple Component

A custom component must:
1. Process a `Doc` object and return it
2. Optionally have a `.model` attribute for trainable components
3. Optionally have `.labels` attribute if it assigns labels

```python
from spacy.language import Language
from spacy.tokens import Doc

@Language.component("uppercase_detector")
def uppercase_detector(doc):
    """Find sequences of uppercase words"""
    uppercase_sequences = []
    
    for token in doc:
        if token.is_upper and not token.like_num:
            uppercase_sequences.append(token.text)
    
    # Store in doc._.custom attribute
    doc._.uppercase_words = uppercase_sequences
    
    return doc

# Register and use
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("uppercase_detector")

doc = nlp("I bought an iPhone from APPLE today.")
print(doc._.uppercase_words)  # ['APPLE']
```

### Extending Doc with Custom Attributes

```python
from spacy.tokens import Doc

# Register custom attribute
Doc.set_extension("uppercase_words", default=[])

# Now you can use doc._.uppercase_words anywhere
```

### Trainable Custom Components

For trainable components, you need to implement:
- `__init__`: Initialize the component
- `__call__`: Process documents
- `update`: Update weights during training
- `.model`: The neural network model

```python
import srsly
from spacy.language import Language
from spacy.tokens import Doc
from spacy.training import Example
from spacy.ml.models import TransformerModel

@Language.component("custom_textcat")
class CustomTextCategorizer:
    def __init__(self, nlp, labels):
        self.labels = labels
        self.nlp = nlp
        
    def __call__(self, doc):
        # Process the document
        return doc
    
    def add_label(self, label):
        if label not in self.labels:
            self.labels.append(label)
    
    def update(self, examples, weights, losses, **kwargs):
        # Update model weights
        pass

# Register and use
nlp = spacy.blank("en")
textcat = nlp.add_pipe("custom_textcat")
textcat.add_label("POSITIVE")
textcat.add_label("NEGATIVE")
```

## Pipeline Configuration

### Using Config Files

spaCy 3.x uses `.cfg` files for configuration:

```python
# Create a custom pipeline programmatically
import spacy
from spacy.training import Example

nlp = spacy.blank("en")

# Add components with configuration
ner = nlp.add_pipe("ner", config={})
ner.add_label("PERSON")
ner.add_label("ORG")

textcat = nlp.add_pipe("textcat", config={
    "arch": "tok2vec",
    "labels": ["POSITIVE", "NEGATIVE"]
})

# Save the pipeline
nlp.to_disk("my_custom_pipeline")
```

### Loading from Config

```python
import spacy

# Load from config file
nlp = spacy.load_config("config.cfg")

# Or create from dictionary
config = {
    "lang": "en",
    "pipeline": ["ner", "textcat"],
    "components": {
        "ner": {"labels": ["PERSON", "ORG"]},
        "textcat": {"labels": ["POS", "NEG"]}
    }
}
nlp = spacy.blank("en")
nlp.update_config(config)
```

## Pipeline Optimization

### Selective Loading

Load only the components you need:

```python
# Exclude unused components for faster processing
nlp = spacy.load("en_core_web_sm", exclude=["parser", "lemmatizer"])

# Or create a blank pipeline and add only what you need
nlp = spacy.blank("en")
nlp.add_pipe("ner")
nlp.add_pipe("textcat")
```

### Batch Processing

Use `nlp.pipe()` for efficient batch processing:

```python
texts = ["Document 1", "Document 2", "Document 3"]

# Efficient batch processing
for doc in nlp.pipe(texts, batch_size=32):
    process(doc)

# With progress bar (requires tqdm)
from spacy.util import compounding
for doc in nlp.pipe(texts, batch_size=32, n_threads=4):
    process(doc)
```

### Multi-Processing

For very large datasets, use multi-processing:

```python
from spacy.util import minibatch

def process_batch(batches):
    for docs in minibatch(batches, size=32):
        yield from nlp.pipe(docs, batch_size=32)

# Process with multiple workers
import multiprocessing as mp
with mp.Pool(4) as pool:
    results = list(pool.map(process_function, texts, chunksize=32))
```

## Component State and Serialization

### Saving and Loading

```python
# Save pipeline to disk
nlp.to_disk("./my_model")

# Load from disk
nlp = spacy.load("./my_model")

# Save to bytes
bytes_data = nlp.to_bytes()

# Load from bytes
nlp.from_bytes(bytes_data)

# Save to JSON (for config only)
import json
config = nlp.meta
with open("meta.json", "w") as f:
    json.dump(config, f)
```

### Freezing Components

Prevent component weights from being updated during training:

```python
# Freeze a specific component
nlp.get_pipe("ner").is_training = False

# Or freeze the entire pipeline
nlp.freeze()

# Unfreeze later if needed
nlp.unfreeze()
```

## Debugging Pipelines

### Inspecting Component Output

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple is looking at buying U.K. startup")

# Check which annotations are available
print(doc.has_annotation("POS"))   # True
print(doc.has_annotation("DEP"))   # True
print(doc.has_annotation("ENT"))   # True

# Inspect specific component output
for token in doc:
    print(token.text, token.pos_, token.dep_, token.ent_type_)
```

### Component Debugging Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Process and see component details
doc = nlp("Test sentence")
```

## Common Pipeline Patterns

### NER-Only Pipeline

```python
nlp = spacy.load("en_core_web_sm", exclude=["parser", "lemmatizer", "attribute_ruler"])
doc = nlp("John works at Google")
for ent in doc.ents:
    print(ent.text, ent.label_)
```

### Text Classification Pipeline

```python
nlp = spacy.load("en_core_web_md", exclude=["parser", "lemmatizer"])
doc = nlp("This product is amazing!")
print(doc.cats["POSITIVE"])
```

### Multi-Task Pipeline

```python
# Load full pipeline for multiple tasks
nlp = spacy.load("en_core_web_lg")
doc = nlp("The quick brown fox jumps over the lazy dog.")

# Access all annotations
for token in doc:
    print({
        "text": token.text,
        "pos": token.pos_,
        "dep": token.dep_,
        "lemma": token.lemma_,
        "morph": token.morph_
    })
```

## Best Practices

1. **Load pipelines once**: Reuse the `nlp` object across your application
2. **Exclude unused components**: Don't load components you don't need
3. **Use batch processing**: `nlp.pipe()` is more efficient than looping
4. **Choose appropriate model size**: Balance speed vs. accuracy needs
5. **Test component order**: Some components depend on others' output
6. **Validate pipelines**: Use `python -m spacy validate` to check compatibility

## References

- [Pipeline Documentation](https://spacy.io/usage/processing-pipelines)
- [Component Factory](https://spacy.io/api/factory)
- [Training Guide](https://spacy.io/usage/training)
- [Performance Tips](https://spacy.io/usage/facts-figures)
