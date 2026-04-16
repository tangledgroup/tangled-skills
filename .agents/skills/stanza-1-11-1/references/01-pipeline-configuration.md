# Pipeline Configuration

## Pipeline Options Reference

When instantiating `stanza.Pipeline()`, you can customize behavior through these options:

### Core Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `lang` | str | `'en'` | Language code (e.g., "en") or language name (e.g., "English") |
| `dir` | str | `~/stanza_resources` | Directory for storing downloaded models |
| `package` | dict or str | `'default'` | Package name(s) for processors. Use dict to specify per-processor packages |
| `processors` | dict or str | `dict()` | Comma-separated list (e.g., `'tokenize,pos'`) or dict mapping processor names to packages |
| `logging_level` | str | `'INFO'` | Log level: `'DEBUG'`, `'INFO'`, `'WARN'`, `'ERROR'`, `'CRITICAL'`, `'FATAL'` |
| `verbose` | bool | `None` | Simplified logging: `True` → INFO, `False` → ERROR |
| `use_gpu` | bool | `True` | Attempt to use GPU if available |
| `device` | str | `None` | Specific device (e.g., `'cuda:1'` instead of default `'cuda:0'`) |

### Processor-Specific Model Paths

Override default models with custom paths:

```python
nlp = stanza.Pipeline(
    'en',
    tokenize_model_path='./custom_tokenizer.pt',
    pos_model_path='./custom_pos.pt',
    pos_pretrain_path='./custom_pretrain.pt',  # Word vectors
    pos_forward_charlm_path='./forward_charlm.pt',  # Forward character LM
    pos_backward_charlm_path='./backward_charlm.pt'  # Backward character LM
)
```

Pattern: `{processor}_model_path`, `{processor}_pretrain_path`, `{processor}_forward_charlm_path`, `{processor}_backward_charlm_path`

## Building Pipeline from Config Dictionary

For complex configurations, use a config dictionary:

```python
import stanza

config = {
    'processors': 'tokenize,mwt,pos',
    'lang': 'fr',
    'tokenize_model_path': './fr_gsd_models/fr_gsd_tokenizer.pt',
    'mwt_model_path': './fr_gsd_models/fr_gsd_mwt_expander.pt',
    'pos_model_path': './fr_gsd_models/fr_gsd_tagger.pt',
    'pos_pretrain_path': './fr_gsd_models/fr_gsd.pretrain.pt',
    'tokenize_pretokenized': True,  # Use pretokenized input
    'use_gpu': False,
    'logging_level': 'WARN'
}

nlp = stanza.Pipeline(**config)
doc = nlp("Van Gogh grandit au sein d'une famille de l'ancienne bourgeoisie.")
```

## Processor Selection Strategies

### Minimal Pipeline (Fastest)

```python
# Only tokenization and sentence splitting
nlp = stanza.Pipeline('en', processors='tokenize')
```

### Syntax Analysis Pipeline

```python
# Full syntactic analysis without NER
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos,lemma,depparse')
```

### Entity Extraction Pipeline

```python
# Tokenization + NER only
nlp = stanza.Pipeline('en', processors='tokenize,mwt,ner')
```

### Custom Package Per Processor

```python
nlp = stanza.Pipeline(
    'en',
    package=None,  # Disable default package fallback
    processors={
        'tokenize': 'default',
        'pos': 'combined',  # Use combined models for POS
        'depparse': 'combined',
        'ner': 'ontonotes'  # Use OntoNotes NER model
    }
)
```

## GPU and Device Control

### Automatic GPU Detection (Default)

```python
nlp = stanza.Pipeline('en')  # Uses GPU if available
```

### Force CPU Mode

```python
nlp = stanza.Pipeline('en', use_gpu=False)
```

### Specific CUDA Device

```python
nlp = stanza.Pipeline('en', device='cuda:1')  # Use second GPU
```

### Multi-GPU Considerations

Stanza uses a single GPU per pipeline instance. For multi-GPU setups, create multiple pipeline instances:

```python
nlp_gpu0 = stanza.Pipeline('en', device='cuda:0')
nlp_gpu1 = stanza.Pipeline('en', device='cuda:1')

doc1 = nlp_gpu0(text_batch_1)
doc2 = nlp_gpu1(text_batch_2)
```

## Performance Optimization

### Batching Documents

Concatenate documents with blank lines for maximum throughput:

```python
# Slow: Process one sentence at a time
for sentence in sentences:
    doc = nlp(sentence)

# Fast: Batch all sentences together
text = '\n\n'.join(sentences)
doc = nlp(text)
```

### Pre-download Models

Avoid auto-download delays by pre-downloading:

```python
stanza.download('en')  # Download once, reuse
nlp = stanza.Pipeline('en')  # Instant initialization
```

### Reduce Logging for Production

```python
nlp = stanza.Pipeline('en', logging_level='ERROR')  # Minimal output
# or
nlp = stanza.Pipeline('en', verbose=False)
```

### Use Combined Models

Combined models offer better performance on mixed-domain text:

```python
nlp = stanza.Pipeline('en', package='combined')
```

## Pre-tokenization Support

Process already-tokenized text (useful for integrating with other tokenizers):

```python
config = {
    'lang': 'en',
    'processors': 'pos,lemma,depparse',
    'tokenize_pretokenized': True  # Skip tokenization
}

nlp = stanza.Pipeline(**config)

# Input format: space-separated tokens, sentences separated by ". "
pretok_text = "Barack Obama /was/ born in Hawaii . He /was/ elected president in 2008 ."
doc = nlp(pretok_text)
```

## Multilingual Pipeline

Process multiple languages with separate pipelines:

```python
# Create pipelines for different languages
nlp_en = stanza.Pipeline('en')
nlp_fr = stanza.Pipeline('fr')
nlp_de = stanza.Pipeline('de')

# Route text to appropriate pipeline
def process_multilingual(texts_with_lang):
    """texts_with_lang: list of (language_code, text) tuples"""
    pipelines = {
        'en': nlp_en,
        'fr': nlp_fr,
        'de': nlp_de
    }
    
    results = []
    for lang, text in texts_with_lang:
        doc = pipelines[lang](text)
        results.append(doc)
    
    return results

# Usage
docs = process_multilingual([
    ('en', 'Hello world'),
    ('fr', 'Bonjour le monde'),
    ('de', 'Hallo Welt')
])
```

## Error Handling

### Model Download Failures

```python
import stanza

try:
    nlp = stanza.Pipeline('xx')  # Non-existent language
except RuntimeError as e:
    print(f"Model error: {e}")
    # Fallback to available language
    nlp = stanza.Pipeline('en')
```

### GPU Memory Issues

```python
try:
    nlp = stanza.Pipeline('en', use_gpu=True)
except RuntimeError as e:
    if "CUDA" in str(e):
        print("GPU unavailable, falling back to CPU")
        nlp = stanza.Pipeline('en', use_gpu=False)
    else:
        raise
```

## Pipeline Inspection

Check loaded processors and configuration:

```python
nlp = stanza.Pipeline('en', processors='tokenize,pos,ner')

# List active processors
print(nlp.processors)  # {'tokenize': ..., 'pos': ..., 'ner': ...}

# Check if specific processor is loaded
has_ner = 'ner' in nlp.processors
```

## Advanced: Processor Options

Pass additional options to individual processors:

```python
nlp = stanza.Pipeline(
    'en',
    processors='tokenize,pos,depparse',
    # Tokenizer options
    tokenize_pretokenized=False,
    tokenize_omit_spaces=False,
    # POS tagger options
    pos_batch_size=512,
    pos_iter=10,
    # Dependency parser options
    depparse_batch_size=64,
    depparse_iter=100,
    depparse_pretrain_path='./custom.pretrain.pt'
)
```

See individual processor documentation for available options.
