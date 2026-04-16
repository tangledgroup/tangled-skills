# Model Downloading and Language Support

## Download Methods

### Automatic Download (Default)

Models auto-download on first pipeline initialization:

```python
import stanza

nlp = stanza.Pipeline('en')  # Auto-downloads English models if not present
```

### Manual Download

Download models before creating pipeline:

```python
import stanza

# Single language
stanza.download('en')

# Multiple languages
stanza.download(['en', 'fr', 'de', 'es'])

# All available languages (large download!)
stanza.download(None)  # Downloads all 80+ languages
```

### Download with Options

```python
# Specify package
stanza.download('en', package='combined')

# Custom download directory
stanza.download('en', dir='/path/to/models')

# With proxy for restricted networks
proxies = {'http': 'http://proxy:port', 'https': 'http://proxy:port'}
stanza.download('en', proxies=proxies)

# Verbose output
stanza.download('en', verbose=True)
```

## Available Packages

### Default Package

Standard models for each language, trained on Universal Dependencies treebanks:

```python
stanza.download('en', package='default')
nlp = stanza.Pipeline('en', package='default')
```

### Combined Package

Models trained on multiple datasets for better coverage:

```python
stanza.download('en', package='combined')
nlp = stanza.Pipeline('en', package='combined')
```

Available for: English, German, Spanish, French, Arabic, and more.

### NER-Specific Packages

Different NER models per language:

**English:**
- `ontonotes`: OntoNotes 5.0 dataset (default)
- `conll2000`: CoNLL 2000 dataset
- `ontonotes14`: OntoNotes 14.0 dataset

```python
stanza.download('en', package='ontonotes')
nlp = stanza.Pipeline('en', processors='ner', package='ontonotes')
```

**Other languages:**
- `fi_turku` (Finnish)
- `es_ancora` (Spanish)
- `de_gtcor` (German)
- `fr_cdnc` (French)

### Biomedical Package

Specialized models for biomedical and clinical text:

```python
stanza.download('en', package='biomed')
nlp = stanza.Pipeline('en', package='biomed')
```

See [Biomedical Models](references/08-biomedical-models.md) for details.

## Supported Languages (80+)

Stanza supports models for 80+ human languages via Universal Dependencies v2.12:

### Major European Languages

| Code | Language | Treebank(s) |
|------|----------|-------------|
| `en` | English | EWT, GWT, LinES, Combined |
| `de` | German | GS, HDG, L3, TAP, Combined |
| `fr` | French | GSD, SESTOUREZ, Combined |
| `es` | Spanish | GSD, AnCora, Combined |
| `it` | Italian | ISDT |
| `pt` | Portuguese | Bosque |
| `ru` | Russian | SynTagRus, RudTal |
| `nl` | Dutch | Lassy Small |
| `pl` | Polish | LFG |
| `sv` | Swedish | Talbanken |
| `da` | Danish | DDTC |
| `no` | Norwegian (Bokmål) | Bokmaal |
| `nn` | Norwegian (Nynorsk) | Nynorsk |

### Asian Languages

| Code | Language | Treebank(s) |
|------|----------|-------------|
| `zh-hans` | Chinese (Simplified) | GSD, CTB, Combined |
| `zh-hant` | Chinese (Traditional) | GSK |
| `ja` | Japanese | GSD, UDJP |
| `ko` | Korean | GSD, Kaist |
| `hi` | Hindi | HDTB |
| `th` | Thai | TUD, Orchid, BEST |
| `vi` | Vietnamese | VTB |
| `id` | Indonesian | GSDD |
| `my` | Myanmar | ALT |
| `te` | Telugu | MTG |
| `ta` | Tamil | IITB |
| `bn` | Bengali | DBTC |
| `mr` | Marathi | L3Cube |
| `ml` | Malayalam | ASIG |

### Middle Eastern & African Languages

| Code | Language | Treebank(s) |
|------|----------|-------------|
| `ar` | Arabic | PADT, UAJB, Combined |
| `he` | Hebrew | HIT-SD |
| `fa` | Persian | IDGPT |
| `tr` | Turkish | IMST, TED |
| `swl` | Swahili | WDT |
| `wo` | Wolof | WOL |

### Other European Languages

| Code | Language | Treebank(s) |
|------|----------|-------------|
| `el` | Greek | GSD, GTREE |
| `grc` | Ancient Greek | Proiel |
| `la` | Latin | IPM, LLAT |
| `ga` | Irish | IDEA |
| `cy` | Welsh | CCG |
| `eu` | Basque | BSC |
| `ca` | Catalan | AnCora |
| `gl` | Galician | TDG |
| `ro` | Romanian | RRT |
| `bg` | Bulgarian BTB |
| `hr` | Croatian HSE |
| `cs` | Czech PDT, CDT |
| `sk` | Slovak SNL |
| `hu` | Hungarian Szeged |
| `fi` | Finnish TDT, GTT |
| `et` | Estonian EDT |
| `lv` | Latvian LLTC |
| `lt` | Lithuanian LTH |
| `sl` | Slovenian SSJ |
| `sr` | Serbian SET |
| `sq` | Albanian SD |
| `mk` | Macedonian MAS |
| `be` | Belarusian HSE |
| `uk` | Ukrainian UD |
| `ru` | Russian SynTagRus |

### Historical & Classical Languages

| Code | Language | Treebank(s) |
|------|----------|-------------|
| `grc` | Ancient Greek | Proiel |
| `la` | Latin | IPM, LLAT |
| `fro` | Old French | SFBG |
| `orv` | Old Russian | ORBIS |
| `xcl` | Classical Armenian | ARMTP |
| `got` | Gothic | LINGUA |
| `lzh` | Classical Chinese | SYNTACTAT |

### Additional Languages

- `af` (Afrikaans)
- `az` (Azerbaijani)
- `hy` (Armenian)
- `hyw` (Western Armenian)
- `ba` (Bashkir)
- `ckb` (Central Kurdish)
- `cu` (Church Slavic)
- `fo` (Faroese)
- `gd` (Scottish Gaelic)
- `is` (Icelandic)
- `ka` (Georgian)
- `kk` (Kazakh)
- `kmr` (Kurdish)
- `lij` (Ligurian)
- `mt` (Maltese)
- `myv` (Erzya)
- `pcm` (Nigerian Pidgin)
- `qtd` |
- `sa` (Sanskrit)
- `sd` (Sindhi)
- `si` (Sinhala)
- `sme` (Northern Sami)
- `ug` (Uyghur)
- `ur` (Urdu)

## Hugging Face Models

Stanza models are also available on Hugging Face for 80+ languages:

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification

# Load Stanza NER model from Hugging Face
model_name = "stanfordnlp/stanza-en"  # Replace with target language
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# Available models (partial list):
# stanfordnlp/stanza-af, stanza-ar, stanza-be, stanza-bg, stanza-ca
# stanza-cs, stanza-cu, stanza-cy, stanza-da, stanza-de
# stanza-el, stanza-en, stanza-es, stanza-et, stanza-eu
# stanza-fa, stanza-fi, stanza-fo, stanza-fr, stanza-fro
# stanza-ga, stanza-gd, stanza-gl, stanza-got, stanza-grc
# stanza-he, stanza-hi, stanza-hr, stanza-hu, stanza-hy
# stanza-hyw, stanza-id, stanza-is, stanza-it, stanza-ja
# stanza-ka, stanza-kk, stanza-kmr, stanza-ko, stanza-la
# stanza-lt, stanza-lv, stanza-lzh, stanza-mr, stanza-mt
# stanza-my, stanza-myv, stanza-nb, stanza-nl, stanza-nn
# stanza-orv, stanza-pcm, stanza-pl, stanza-pt, stanza-qtd
# stanza-ro, stanza-ru, stanza-sa, stanza-sd, stanza-sk
# stanza-sl, stanza-sme, stanza-sr, stanza-sv, stanza-swl
# stanza-ta, stanza-te, stanza-th, stanza-tr, stanza-ug
# stanza-uk, stanza-ur, stanza-vi, stanza-wo, stanza-zh-hans
# stanza-zh-hant, stanza-bxr, stanza-hsb, stanza-lij, stanza-multilingual
```

## Model Storage and Management

### Default Storage Location

Models are stored in `~/stanza_resources/` by default:

```
~/stanza_resources/
├── en/
│   ├── tokenize/
│   │   └── default/
│   │       └── tokenizer.pt
│   ├── mwt/
│   ├── pos/
│   ├── lemma/
│   ├── depparse/
│   ├── ner/
│   └── pretrain.pt
├── fr/
├── de/
└── ...
```

### Custom Storage Directory

```python
# Download to custom location
stanza.download('en', dir='/mnt/models/stanza')

# Use custom location in pipeline
nlp = stanza.Pipeline('en', dir='/mnt/models/stanza')
```

### Check Downloaded Models

```python
import stanza
from stanza.utils import common

# List available packages for a language
print(common.get_model_attribute('en'))

# Check if models exist
import os
models_dir = os.path.expanduser('~/stanza_resources/en')
if os.path.exists(models_dir):
    print("English models are downloaded")
```

### Download Size Estimates

| Package | Approximate Size |
|---------|------------------|
| Single language (default) | 50-200 MB |
| Single language (combined) | 100-400 MB |
| All languages | 5-10 GB |

## Troubleshooting Download Issues

### Connection Errors

```python
# Use proxy
proxies = {'http': 'http://proxy:port', 'https': 'http://proxy:port'}
stanza.download('en', proxies=proxies)

# Manual download from GitHub
# https://github.com/stanfordnlp/stanza-resources/releases
```

### Partial Downloads

If download is interrupted, resume automatically:

```python
stanza.download('en')  # Resumes from where it left off
```

### Disk Space Issues

```bash
# Check available space
df -h ~/stanza_resources

# Clean unused models
rm -rf ~/stanza_resources/xx  # Remove language xx
```

### Download Specific Processors Only

Reduce download size by selecting specific processors:

```python
# Download only NER model
stanza.download('en', processors='ner')

# Download tokenizer and POS only
stanza.download('en', processors='tokenize,pos')
```

## Language Detection for Auto-Selection

Use language identification to route text to correct pipeline:

```python
import stanza

# Download langid model (language-independent)
stanza.download('langid')

# Create language identifier
nlp_langid = stanza.Pipeline('langid')

# Detect language and process accordingly
text = "Bonjour le monde"
doc = nlp_langid(text)
detected_lang = doc.lang  # 'fr'

# Route to appropriate pipeline
pipelines = {
    'en': stanza.Pipeline('en'),
    'fr': stanza.Pipeline('fr'),
    'de': stanza.Pipeline('de')
}

if detected_lang in pipelines:
    doc = pipelines[detected_lang](text)
```
