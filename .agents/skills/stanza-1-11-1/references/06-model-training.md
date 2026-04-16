# Model Training and Evaluation

## Overview

Train custom Stanza models on your own annotated data. All neural modules (tokenizer, MWT expander, POS tagger, lemmatizer, dependency parser, NER) can be trained from scratch or fine-tuned.

**Note:** Training requires cloning the Stanza repository, not just installing via pip.

## Setup

### Clone Repository

```bash
git clone https://github.com/stanfordnlp/stanza.git
cd stanza
pip install -e .
```

### Configure Environment

Edit `scripts/config.sh` to set environment variables:

```bash
# Source configuration
source scripts/config.sh

# Or set manually in .bashrc
export UDBASE=/path/to/universal-dependencies
export NERBASE=/path/to/ner-datasets
export DATA_ROOT=/path/to/intermediate-files
export WORDVEC_DIR=/path/to/word-vectors
```

### Key Environment Variables

| Variable | Description |
|----------|-------------|
| `UDBASE` | Root directory for Universal Dependencies data (CoNLL-U format) |
| `NERBASE` | Root directory for NER datasets |
| `DATA_ROOT` | Directory for intermediate training files |
| `{module}_DATA_DIR` | Subdirectory for each module's intermediate files |
| `WORDVEC_DIR` | Directory for word vector files |

Example directory structure:
```
$UDBASE/
├── UD_English-EWT/
│   ├── en_ewt-ud-train.conllu
│   ├── en_ewt-ud-dev.conllu
│   └── en_ewt-ud-test.conllu
├── UD_French-GSD/
└── ...

$NERBASE/
├── en_ontonotes/
├── fi_turku/
└── ...
```

## Data Preparation

### Universal Dependencies Data

Download from [Universal Dependencies website](https://universaldependencies.org/):

```bash
# Download all treebanks
git clone https://github.com/unicode-org/icu.git
# Or download specific language:
wget https://raw.githubusercontent.com/UniversalDependencies/UD_English-EWT/master/en_ewt-ud-train.conllu
wget https://raw.githubusercontent.com/UniversalDependencies/UD_English-EWT/master/en_ewt-ud-dev.conllu
wget https://raw.githubusercontent.com/UniversalDependencies/UD_English-EWT/master/en_ewt-ud-test.conllu
```

### Convert UD Data

Prepare data for each module:

```bash
# Tokenizer
python -m stanza.utils.datasets.prepare_tokenize_treebank UD_English-EWT

# MWT expander
python -m stanza.utils.datasets.prepare_mwt_treebank UD_English-EWT

# POS tagger
python -m stanza.utils.datasets.prepare_pos_treebank UD_English-EWT

# Lemmatizer
python -m stanza.utils.datasets.prepare_lemma_treebank UD_English-EWT

# Dependency parser
python -m stanza.utils.datasets.prepare_depparse_treebank UD_English-EWT
```

### NER Data Preparation

NER uses BIOES format, not CoNLL-U:

```bash
# Prepare supported datasets
python -m stanza.utils.datasets.ner.prepare_ner_dataset en_ontonotes
python -m stanza.utils.datasets.ner.prepare_ner_dataset fi_turku
python -m stanza.utils.datasets.ner.prepare_ner_dataset es_ancora

# For custom datasets, convert to BIO format first
python -m stanza.utils.datasets.ner.prepare_ner_file input.iob output.json
```

Expected NER directory structure:
```
$NER_DATA_DIR/
├── en_ontonotes.train.json
├── en_ontonotes.dev.json
└── en_ontonotes.test.json
```

### Word Vectors

Download or prepare word vectors for better performance:

```bash
# Use existing Stanza models as source
import stanza
stanza.download('en')  # Downloads pretrain.pt

# Or use external embeddings (GloVe, FastText)
# Convert to Stanza format if needed
```

## Training Scripts

### Train Tokenizer

```bash
python -m stanza.utils.training.run_tokenize UD_English-EWT \
    --batch_size 32 \
    --dropout 0.33 \
    --hidden_dim 256 \
    --num_layers 2 \
    --emb_dim 128
```

### Train MWT Expander

```bash
python -m stanza.utils.training.run_mwt UD_English-EWT \
    --batch_size 32 \
    --dropout 0.33 \
    --hidden_dim 256
```

### Train POS Tagger

```bash
python -m stanza.utils.training.run_pos UD_English-EWT \
    --batch_size 512 \
    --dropout 0.33 \
    --hidden_dim 256 \
    --num_layers 2 \
    --emb_dim 128 \
    --pretrain_path saved_models/pos/en_ewt.pretrain.pt \
    --charlm \
    --charlm_shorthand en_elevate_wiki
```

### Train Lemmatizer

```bash
python -m stanza.utils.training.run_lemma UD_English-EWT \
    --batch_size 512 \
    --dropout 0.33 \
    --hidden_dim 256 \
    --pretrain_path saved_models/pos/en_ewt.pretrain.pt
```

### Train Dependency Parser

```bash
python -m stanza.utils.training.run_depparse UD_English-EWT \
    --batch_size 64 \
    --dropout 0.33 \
    --hidden_dim 256 \
    --pretrain_path saved_models/pos/en_ewt.pretrain.pt \
    --charlm \
    --charlm_shorthand en_elevate_wiki \
    --iter 100
```

### Train NER Model

```bash
python -m stanza.utils.training.run_ner en_ontonotes \
    --batch_size 64 \
    --dropout 0.33 \
    --hidden_dim 256 \
    --pretrain_path saved_models/pos/en_ewt.pretrain.pt \
    --charlm \
    --charlm_shorthand en_elevate_wiki
```

## Training Options Reference

### Common Options

| Option | Default | Description |
|--------|---------|-------------|
| `--batch_size` | varies | Mini-batch size for training |
| `--dropout` | 0.33 | Dropout probability |
| `--hidden_dim` | 256 | Hidden layer dimension |
| `--emb_dim` | 128 | Embedding dimension |
| `--num_layers` | 2 | Number of LSTM layers |
| `--iter` | varies | Number of training iterations |
| `--learning_rate` | 0.001 | Initial learning rate |
| `--weight_decay` | 0.0 | L2 regularization |

### Advanced Options

| Option | Description |
|--------|-------------|
| `--pretrain_path` | Path to word vector file |
| `--charlm` | Use character language model |
| `--charlm_shorthand` | Shorthand for charlm dataset |
| `--bidirectional` | Use bidirectional LSTM (default) |
| `--fine_tune` | Fine-tune pretrained embeddings |
| `--save_dir` | Directory to save trained models |
| `--cuda` | Use GPU for training |
| `--cpu` | Force CPU training |

## Evaluation

### Automatic Evaluation

Evaluation runs automatically after training:

```bash
# Training output includes dev/test scores
python -m stanza.utils.training.run_pos UD_English-EWT
# Output:
# Dev accuracy: 96.23%
# Test accuracy: 95.87%
```

### Manual Evaluation

Evaluate trained models on specific splits:

```bash
# Evaluate on dev set
python -m stanza.utils.training.run_pos UD_English-EWT --score_dev

# Evaluate on test set
python -m stanza.utils.training.run_pos UD_English-EWT --score_test
```

### End-to-End Pipeline Evaluation

Evaluate full pipeline performance:

```bash
python -m stanza.utils.training.run_ete UD_English-EWT --score_test
```

Metrics reported:
- Tokenization accuracy
- MWT expansion F1
- POS tagging accuracy
- Lemmatization accuracy
- Dependency parsing UAS/LAS (Unlabeled/Labeled Attachment Score)

## Fine-Tuning Existing Models

Fine-tune pretrained models on domain-specific data:

```bash
# Start from pretrained model
python -m stanza.utils.training.run_pos UD_English-EWT \
    --pretrain_path saved_models/pos/en_ewt.pretrain.pt \
    --fine_tune \
    --model_path saved_models/pos/en_ewt.pt \
    --train_file data/custom_train.conllu \
    --eval_file data/custom_dev.conllu
```

## Character Language Models (CharLM)

CharLMs improve performance on low-resource languages and morphologically rich languages.

### Train CharLM

```bash
python -m stanza.utils.training.run_charlm en_elevate_wiki \
    --train_file data/charlm/train.txt \
    --eval_file data/charlm/dev.txt \
    --hidden_dim 1024 \
    --num_layers 3
```

### Use CharLM in Training

```bash
python -m stanza.utils.training.run_pos UD_English-EWT \
    --charlm \
    --charlm_shorthand en_elevate_wiki \
    --forward_charlm_path saved_models/charlm/en_elevate_wiki_forward.pt \
    --backward_charlm_path saved_models/charlm/en_elevate_wiki_backward.pt
```

## GPU Training

### Automatic GPU Detection

Training scripts auto-detect CUDA:

```bash
python -m stanza.utils.training.run_pos UD_English-EWT
# Uses GPU if available
```

### Force CPU Mode

```bash
python -m stanza.utils.training.run_pos UD_English-EWT --cpu
```

### Multi-GPU Training

For multi-GPU setups, use PyTorch DistributedDataParallel (advanced):

```python
from torch.nn.parallel import DistributedDataParallel

model = DistributedDataParallel(model)
```

## Common Training Issues

### Out of Memory

Reduce batch size:

```bash
python -m stanza.utils.training.run_pos UD_English-EWT --batch_size 32
```

### Poor Convergence

- Increase number of iterations (`--iter`)
- Adjust learning rate (`--learning_rate`)
- Check data quality and formatting
- Use pretrained embeddings

### Data Format Errors

Ensure CoNLL-U format is correct:
- 10 columns per line (id, form, lemma, upos, xpos, feats, head, deprel, deps, misc)
- Blank lines between sentences
- Comment lines start with `#`

### Missing Word Vectors

Train without embeddings (reduced performance):

```bash
python -m stanza.utils.training.run_pos UD_English-EWT --no_pretrain
```

Or download/create word vectors first.

## Training Tips

### Data Quality

- Ensure consistent tokenization across train/dev/test
- Check for OOV (out-of-vocabulary) words
- Balance entity types for NER
- Verify CoNLL-U format with validation scripts

### Hyperparameter Tuning

Start with defaults, then tune:
1. `batch_size`: Larger = faster but more memory
2. `hidden_dim`: 256-512 for most tasks
3. `dropout`: 0.3-0.5 to prevent overfitting
4. `learning_rate`: 0.001-0.01

### Monitoring Training

Watch these metrics:
- Training loss (should decrease)
- Dev accuracy (should increase, then plateau)
- Test accuracy (final evaluation)

Early stopping when dev performance degrades.

### Saving Checkpoints

Models auto-save during training:

```
saved_models/
├── tokenize/
│   └── en_ewt/
│       └── tokenizer.pt
├── pos/
│   └── en_ewt/
│       ├── tagger.pt
│       └── en_ewt.pretrain.pt
└── depparse/
    └── en_ewt/
        └── parser.pt
```

## Using Trained Models

Load custom models in pipeline:

```python
import stanza

nlp = stanza.Pipeline(
    'en',
    tokenize_model_path='./saved_models/tokenize/en_ewt/tokenizer.pt',
    pos_model_path='./saved_models/pos/en_ewt/tagger.pt',
    depparse_model_path='./saved_models/depparse/en_ewt/parser.pt'
)

doc = nlp("Hello world")
```

Or set `dir` to custom models directory:

```python
nlp = stanza.Pipeline('en', dir='./saved_models')
```
