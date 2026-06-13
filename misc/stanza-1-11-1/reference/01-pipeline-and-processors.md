# Pipeline and Processors

## Building a Pipeline

The `Pipeline` is the central Stanza object. It pre-loads and chains processors, each performing a specific NLP task.

```python
import stanza
nlp = stanza.Pipeline('en')  # default English pipeline with all processors
```

### Pipeline Options

- `lang` (str): Language code or name, e.g., `'en'`, `'English'`
- `dir` (str): Model directory, default `'~/stanza_resources'`
- `package` (str or dict): Package name for models, default `'default'`. Can be a dict mapping processor names to packages.
- `processors` (str or dict): Comma-separated processor names or dict of `{processor: package}`. Unspecified processors fall back to `package`.
- `logging_level` (str): `'DEBUG'`, `'INFO'`, `'WARN'`, `'ERROR'`, `'CRITICAL'`, `'FATAL'`
- `verbose` (bool): Shortcut — `True` sets INFO, `False` sets ERROR
- `use_gpu` (bool): Default `True`. Set to `False` to force CPU.
- `device` (str): Specific device, e.g., `'cuda:1'`
- `download_method`: Controls auto-download behavior. Set to `None` to disable. Use `DownloadMethod.REUSE_RESOURCES` to only download missing packages.

### Per-Processor Model Paths

Override individual model files:

```python
nlp = stanza.Pipeline('en',
    pos_model_path='custom_pos.pt',
    pos_pretrain_path='custom_vectors.pt',
    pos_forward_charlm_path='forward_charlm.pt',
    pos_backward_charlm_path='backward_charlm.pt')
```

## Processor Dependencies

Each processor has requirements that must be satisfied by earlier processors:

- `tokenize` — no dependencies (always first)
- `mwt` — requires `tokenize`
- `pos` — requires `tokenize`, `mwt`
- `lemma` — requires `tokenize`, `mwt`, `pos`
- `depparse` — requires `tokenize`, `mwt`, `pos`, `lemma`
- `ner` — requires `tokenize`, `mwt`
- `sentiment` — requires `tokenize`
- `constituency` — requires `tokenize`, `mwt`, `pos`
- `coref` — requires `tokenize`

## Processor Variants

Register custom implementations to replace or augment existing processors:

```python
from stanza.pipeline.processor import ProcessorVariant, register_processor_variant

@register_processor_variant('tokenize', 'spacy')
class SpacyTokenizer(ProcessorVariant):
    def __init__(self, config):
        # initialize spacy
        pass
    def process(self, text):
        # tokenize text with spacy
        pass
```

Use it in the pipeline:

```python
nlp = stanza.Pipeline('en', processors={"tokenize": "spacy"})
```

For full replacement (OVERRIDE mode):

```python
@register_processor_variant("lemma", "cool")
class CoolLemmatizer(ProcessorVariant):
    OVERRIDE = True
    def __init__(self, lang):
        pass
    def process(self, document):
        for sentence in document.sentences:
            for word in sentence.words:
                word.lemma = "cool"
        return document
```

## Custom Processors

Implement entirely new annotation capabilities:

```python
from stanza.pipeline.processor import Processor, register_processor

@register_processor("lowercase")
class LowercaseProcessor(Processor):
    _requires = set(['tokenize'])
    _provides = set(['lowercase'])

    def __init__(self, device, config, pipeline):
        pass

    def _set_up_model(self, config):
        pass

    def process(self, document):
        for sentence in document.sentences:
            for token in sentence.tokens:
                token.text = token.text.lower()
        return document
```

## Pretagged Documents

When you already have tokenized/tagged data, skip earlier processors:

```python
import stanza
from stanza.models.common.doc import Document

nlp = stanza.Pipeline('en', processors='depparse', depparse_pretagged=True)
pretagged_doc = Document([[{'id': 1, 'text': 'Hello', 'upos': 'INTJ'}]])
doc = nlp(pretagged_doc)
```

## Batching for Performance

For maximum speed, batch multiple documents together separated by blank lines (`\n\n`):

```python
nlp = stanza.Pipeline('en')
text = "First document text.\n\nSecond document text.\n\nThird document."
doc = nlp(text)
```

Running one sentence at a time in a loop is significantly slower.
