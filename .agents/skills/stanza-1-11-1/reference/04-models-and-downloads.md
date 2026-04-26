# Models and Downloads

## Model Categories

Stanza provides pretrained models in four categories:

- **Universal Dependencies (UD) models**: Trained on UD v2.12 treebanks. Cover tokenization, MWT expansion, lemmatization, POS/morphological features tagging, and dependency parsing. Available for 80 human languages.
- **NER models**: Named entity recognition for 23 languages, trained on various NER datasets (OntoNotes, CoNLL, WikiNER, etc.).
- **Constituency models**: Phrase structure parsers for English, Chinese, Indonesian, Italian, Japanese, Vietnamese.
- **Sentiment models**: Per-sentence sentiment classification for English, Chinese, German.

Additionally, biomedical and clinical English model packages provide domain-specific NER (disease, chemical, gene entities) and syntactic analysis for medical text.

## Automatic Download

```python
import stanza

# Download default package for a language
stanza.download('en')

# Download specific processors
stanza.download('zh', processors='tokenize,pos')

# Download with custom package
stanza.download('de', processors='tokenize,mwt', package='gsd')

# Download with mixed packages
stanza.download('nl', processors={'ner': 'conll02'})
```

### Download Options

- `lang` (str): Language code or name
- `model_dir` (str, default `'~/stanza_resources'`): Storage directory
- `package` (str, default `'default'`): Model package name
- `processors` (str or dict): Which processors to download
- `logging_level` (str, default `'INFO'`): Log verbosity
- `verbose` (bool): Shortcut — True=INFO, False=ERROR

Override storage location with `STANZA_RESOURCES_DIR` environment variable.

## Offline Usage

Download models ahead of time and disable auto-download:

```python
import stanza
stanza.download('en')
nlp = stanza.Pipeline('en', download_method=None)
```

Or reuse existing resources file:

```python
from stanza.pipeline.core import DownloadMethod
nlp = stanza.Pipeline('zh', download_method=DownloadMethod.REUSE_RESOURCES)
```

## Manual Download

Models are hosted on HuggingFace in per-language repos (e.g., `stanfordnlp/stanza-en`).

1. Download `resources.json` from the Stanford git repo into `$STANZA_RESOURCES_DIR/resources.json`
2. Download the language's `default.zip` (e.g., from `stanza-en/models/default.zip`)
3. Place it in `$STANZA_RESOURCES_DIR/en/default.zip`
4. Unzip — expected layout:

```
$STANZA_RESOURCES_DIR/
├── resources.json
└── en/
    ├── default.zip
    ├── backward_charlm/1billion.pt
    ├── constituency/ptb3-revised_charlm.pt
    ├── depparse/combined_charlm.pt
    ├── forward_charlm/1billion.pt
    ├── lemma/combined_nocharlm.pt
    ├── ner/ontonotes_charlm.pt
    ├── pos/combined_charlm.pt
    ├── pretrain/conll17.pt
    ├── pretrain/fasttextcrawl.pt
    ├── sentiment/sstplus.pt
    └── tokenize/combined.pt
```

Individual models can be downloaded from the language repo tree, e.g., `https://huggingface.co/stanfordnlp/stanza-en/tree/main/models/ner`.

## Combined Models

For some languages, Stanza builds combined models from multiple datasets simultaneously, providing wider coverage and better performance. When available, combined models are the defaults.

## Biomedical and Clinical Models

Specialized English model packages for biomedical literature and clinical notes:

- **NER**: Disease, chemical, and gene entity recognition
- **Syntactic analysis**: Tokenization, POS tagging, lemmatization, dependency parsing on biomedical text

Download with specific package names. See the [biomedical documentation](https://stanfordnlp.github.io/stanza/biomed.html) for available models and performance metrics.

## Language Identification Model

The multilingual language identification model detects 80+ languages using a character-level Bi-LSTM trained on UD 2.5 text snippets. Works on short text (10+ characters), sentences, tweets, and paragraphs.

```python
stanza.download('multilingual')
```

Supported detection codes include: af, ar, be, bg, ca, cs, da, de, el, en, es, fi, fr, he, hi, hu, id, it, ja, ko, nl, pl, pt, ro, ru, sv, ta, te, tr, uk, vi, zh-hans, zh-hant, and many more.
