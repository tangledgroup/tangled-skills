# Training and Configuration

## Overview

spaCy's training system uses a config-based approach for reproducible experiments. Every detail of the training run is described in a configuration file, with no hidden defaults.

### Quickstart

```bash
# Generate a base config
python -m spacy init config base_config.cfg \
    --lang en \
    --pipeline ner \
    --optimizer Adam

# Fill in all defaults
python -m spacy init fill-config base_config.cfg config.cfg

# Train
python -m spacy train config.cfg --output ./output --paths.train ./data/train.spacy --paths.dev ./data/dev.spacy
```

## Config System

The config file is INI-style and describes the entire training setup:

```ini
[paths]
train = null
dev = null
vectors = null

[system]
gpu_allocator = null

[nlp]
lang = "en"
pipeline = ["tok2vec", "ner"]
batch_size = 1000

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.embed]
width = 96
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
maxout_pieces = 3
depth = 2

[components.tok2vec.encoder]
factory = "pytorch_transformer"
name = "roberta-base"

[components.ner]
factory = "ner"
moves = null
update_with_oracle_cut_size = 100

[corpora]

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths.train}
max_length = 0

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths.dev}

[training]
dev_corpus = "corpora.dev"
train_corpus = "corpora.train"
seed = 1
gpu_allocator = "pytorch"
dropout = 0.1
accumulate_gradient = 1
patience = 1600
max_epochs = 0
max_steps = 20000
eval_n = 5
frozen_components = []

[training.logger]
@loggers = "spacy.ConsoleLogger.v1"

[training.optimizer]
@optimizers = "Adam.v1"
beta1 = 0.9
beta2 = 0.999
L2_is_weight_decay = true
L2 = 0.01
grad_clip = 1.0
use_averages = true
d_warmup_steps = 250

[training.batcher]
@batchers = "spacy.batch_by_words.v1"
discard_oversize = false
tolerance = 0.2
get_length = null

[training.batcher.size]
@schedules = "compounding.v1"
start = 100
stop = 1000
compound = 1.001
t = 0.0

[initialize]
vectors = ${paths.vectors}
init_tok2vec = null

[initialize.components]

[initialize.tokenizer]
```

### Key Sections

- `[paths]` — Paths to training data, dev data, and vectors
- `[system]` — System-level settings (GPU allocator)
- `[nlp]` — Language, pipeline components, batch size
- `[components]` — Factory and config for each pipeline component
- `[corpora]` — Data readers for train/dev splits
- `[training]` — Training hyperparameters, optimizer, scheduler
- `[initialize]` — Initialization settings

### Config Variables

Use `${variable}` syntax to reference other config values:

```ini
[paths]
train = "./data/train.spacy"

[corpora.train]
path = ${paths.train}
```

### Overriding Config from CLI

```bash
python -m spacy train config.cfg \
    --output ./output \
    --paths.train ./data/train.spacy \
    --paths.dev ./data/dev.spacy \
    --training.max_steps 10000 \
    --training.dropout 0.1
```

## Data Formats

### JSONL (spaCy format)

The standard training data format:

```json
{"text": "Apple is looking at buying U.K. startup", "entities": [[0, 5, "ORG"], [30, 33, "GPE"]]}
{"text": "Barack Obama was born in Hawaii.", "entities": [[0, 11, "PERSON"], [27, 33, "GPE"]]}
```

Entity format: `[start_char, end_char, label]`

### Converting Data

Use `spacy convert` to convert various formats:

```bash
# CoNLL to spaCy format
python -m spacy convert data/conll/ data/output/ --converter ner

# JSONL to binary .spacy
python -m spacy convert data/train.jsonl data/output/
```

### Binary Format (.spacy)

Binary format using `DocBin` for efficient serialization:

```python
from spacy.tokens import DocBin
import srsly

# Load JSONL and convert
docs = []
for line in open("train.jsonl"):
    data = srsly.read_json(line)
    doc = nlp.make_doc(data["text"])
    docs.append(doc)

docbin = DocBin(docs=docs)
docbin.to_disk("train.spacy")
```

### Binary Training Data (for POS/Dependency)

For training tagger and parser, use the binary format from Universal Dependencies or similar:

```bash
python -m spacy convert data/ud/ data/output/ --converter ud
```

## Training Commands

### spacy train

```bash
python -m spacy train config.cfg --output ./output
```

### spacy init config

Generate a base config from CLI arguments:

```bash
python -m spacy init config config.cfg \
    --lang en \
    --pipeline tagger_parser \
    --optimizer Adam \
    --paths.train ./train.spacy \
    --paths.dev ./dev.spacy
```

### spacy init fill-config

Fill in all defaults in a partial config:

```bash
python -m spacy init fill-config base_config.cfg config.cfg
```

### spacy debug config

Validate and analyze a config file:

```bash
python -m spacy debug config config.cfg
```

### spacy debug data

Analyze training data for problems:

```bash
python -m spacy debug data config.cfg --paths.train ./train.spacy --paths.dev ./dev.spacy
```

Checks for: invalid entity annotations, cyclic dependencies, low data balance, label distribution.

## Evaluation

The `Scorer` computes evaluation metrics:

```python
from spacy.metrics import ner_pr_f, ents_gold_score
from spacy.scorer import Scorer

# Manual scoring
scores = Scorer.score_examples(gold_docs, pred_docs)
print(scores["ents_f"])   # Entity F-score
print(scores["uas"])      # Unlabeled attachment score
print(scores["las"])      # Labeled attachment score
```

During training, spaCy automatically evaluates on the dev set and reports metrics.

## Custom Training Functions

Register custom functions in the config registry:

```python
# my_functions.py
from thinc.api import Optimizer
from spacy.training import Example
import spacy

@spacy.registry.readers("my_reader.v1")
def create_my_reader():
    def read_corpus(path):
        # Custom data loading logic
        pass
    return read_corpus

@spacy.registry.loss_functions("my_loss.v1")
def create_my_loss():
    def loss_function(model, examples, get_loss_weight=lambda e: 1.0):
        # Custom loss computation
        pass
    return loss_function
```

Load with:

```bash
python -m spacy train config.cfg --code my_functions.py
```

## spaCy Projects

spaCy projects manage end-to-end workflows for training, packaging, and serving:

### project.yml Structure

```yaml
assets:
  - dest: data
    url: https://example.com/data.zip
    extra: false

commands:
  name: train
  help: Train the NER model
  script: train
  deps:
    - data/train.spacy
    - data/dev.spacy
  outputs:
    - models/ner/model-best
```

### Project Commands

```bash
# Clone a project template
python -m spacy project clone pipelines/tagger_parser_ud

# Download assets
python -m spacy project assets

# Run a command
python -m spacy project run train

# List available commands
python -m spacy project list
```

### Project Templates

Available in the [explosion/projects](https://github.com/explosion/projects) repository:

- `pipelines/tagger_parser_ud` — POS tagger and dependency parser on Universal Dependencies
- `pipelines/ner_conll03` — NER on CoNLL-2003
- Various other templates for different tasks

## Training Best Practices

1. **Start small**: Begin with a small model and few epochs, then scale up
2. **Use dev data**: Always have a separate evaluation set
3. **Representative data**: Training data should match your production data distribution
4. **Avoid catastrophic forgetting**: When fine-tuning NER, mix in examples the model already recognizes
5. **Monitor metrics**: Watch precision, recall, and F-score on dev data
6. **Use `debug data`**: Validate training data before starting
7. **Config reproducibility**: Every training run should be fully described by its config
8. **Batch size tuning**: Adjust based on available memory and document length
