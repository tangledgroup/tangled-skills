# Training Custom Models and Fine-Tuning

This guide covers training custom spaCy models, data preparation, configuration, evaluation, and fine-tuning pretrained models.

## Training Overview

spaCy's training system supports:
- Training new models from scratch
- Fine-tuning existing pretrained models
- Multi-task learning with multiple components
- Custom loss functions and architectures

### Training Workflow

1. **Prepare training data** in spaCy format
2. **Create configuration file** for training settings
3. **Run training** with `spacy train` command
4. **Evaluate model** on validation data
5. **Iterate** with hyperparameter tuning

## Data Preparation

### Training Data Format

Training data consists of `Example` objects with annotated documents:

```python
from spacy.training import Example
import spacy

nlp = spacy.blank("en")

# Create training example
text = "John works at Google in Mountain View."
annotations = {
    "entities": [(0, 4, "PERSON"), (16, 22, "ORG"), (25, 39, "GPE")]
}

# Create Example object
doc = nlp.make_doc(text)
example = Example.from_dict(doc, annotations)

# Access annotated elements
for span in example.get("entities"):
    print(span.label_, span.text)
```

### Creating Training Data from Dictionary

```python
train_data = [
    {
        "text": "Apple is looking at buying U.K. startup",
        "entities": [(0, 5, "ORG"), (27, 30, "GPE")]
    },
    {
        "text": "John Smith lives in New York",
        "entities": [(0, 10, "PERSON"), (21, 30, "GPE")]
    },
    {
        "text": "Google announced new products today",
        "entities": [(0, 6, "ORG")]
    }
]

# Convert to Example objects
nlp = spacy.blank("en")
examples = []
for item in train_data:
    doc = nlp.make_doc(item["text"])
    example = Example.from_dict(doc, {"entities": item["entities"]})
    examples.append(example)
```

### Text Classification Data

```python
train_data = [
    {
        "text": "This product is amazing!",
        "cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}
    },
    {
        "text": "Terrible experience, very disappointed",
        "cats": {"POSITIVE": 0.0, "NEGATIVE": 1.0}
    },
    {
        "text": "It's okay, nothing special",
        "cats": {"POSITIVE": 0.4, "NEGATIVE": 0.3}
    }
]

# Convert to examples
examples = []
for item in train_data:
    doc = nlp.make_doc(item["text"])
    example = Example.from_dict(doc, {"cats": item["cats"]})
    examples.append(example)
```

### Saving Training Data

```python
import srsly

# Save training data to JSON
train_data = [
    {"text": "John works at Google", "entities": [(0, 4, "PERSON"), (16, 22, "ORG")]},
    {"text": "Apple releases new iPhone", "entities": [(0, 5, "ORG"), (21, 27, "PRODUCT")]}
]

srsly.write_json("train.json", train_data)

# Load training data
train_data = srsly.read_json("train.json")
```

## Configuration Files

spaCy 3.x uses `.cfg` files for configuration.

### Basic Training Config

```python
# config.cfg
[paths]
train = null
dev = null
vectors = null
output = "output"
init_tok2vec = null

[system]
seed = 0
gpu_allocator = null

[nlp]
lang = "en"
pipeline = ["ner"]
disabled = []
before_creation = null
tokenizer = {"@tokenizers": "spacy.Tokenizer.v1"}

[components]

[components.ner]
factory = "ner"
incorrect_spans_key = null
moves_limit = 50

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "ner"
extra_state_tokens = false
hidden_width = 64
maxout_pieces = 3
use_upper = true
norm_entropy_factor = 0.0001

[components.ner.model.tok2vec]
@architectures = "spacy.Tok2Vec.v2"

[components.ner.model.tok2vec.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = ${components.ner.model.hidden_width}
rows = [512, 512, 512, 1500]
attrs = ["ORTH", "SHAPE", "PREFIX", "SUFFIX"]
use_markup = false

[components.ner.model.tok2vec.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = ${components.ner.model.hidden_width * 2}
depth = 4
window_size = 1
maxout_pieces = 3

[corpus]
@readers = "spacy.Corpus.v1"
path = ${paths.train}
max_length = 0
gold_preproc = false
limit = 0
augmenter = null

[training]
seed = ${system.seed}
gpu_allocator = ${system.gpu_allocator}
dropout = 0.1
accumulate_gradient = 1
patience = 1600
max_epochs = 0
eval_frequency = 0
dev_corpus = ${corpus}
before_to_disk = null
annotating_components = []
drop = 0.0

[training.batcher]
@batchers = "spacy.BatchByTokens.v1"
buffer = 256
size = "dynamic"
window = 0x7FFFFFFF
get_length = null

[training.optimizer]
@optimizers = "Adam.v1"
beta1 = 0.9
beta2 = 0.999
lr = 0.001

[training.logger]
@loggers = "spacy.ConsoleLogger.v1"
progress_bar = false

[training.initialize]
@initializers = "spacy.BuildDefaults.v1"
```

### Training with Command Line

```bash
# Create config from blank model
python -m spacy init config config.cfg

# Create config from existing model
python -m spacy init config en_core_web_sm config.cfg

# Train with config
python -m spacy train config.cfg --paths.train train.json --paths.dev dev.json --output output

# Train with GPU
python -m spacy train config.cfg --paths.train train.json --gpu-id 0

# Resume training
python -m spacy train config.cfg --paths.train train.json --init-nlp output/model-best
```

## Training NER Models

### Step-by-Step NER Training

1. **Prepare data:**

```python
import spacy
from spacy.training import Example

train_data = [
    ("I work at Google", {"entities": [(10, 16, "ORG")]}),
    ("John works in New York", {"entities": [(0, 4, "PERSON"), (14, 23, "GPE")]}),
    ("Apple released iPhone 15", {"entities": [(0, 5, "ORG"), (15, 21, "PRODUCT")]})
]

# Create NER component
nlp = spacy.blank("en")
ner = nlp.add_pipe("ner")

# Add labels
for text, annotations in train_data:
    for ent_start, ent_end, label in annotations.get("entities", []):
        ner.add_label(label)
```

2. **Train the model:**

```python
import random
from spacy.training import Example

# Convert to Example objects
def create_examples(data, nlp):
    for text, annotations in data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        yield example

# Training loop
nlp.initialize()

for i in range(20):  # 20 epochs
    random.shuffle(train_data)
    batches = minibatch(train_data, size=8)
    
    for batch in batches:
        examples = list(create_examples(batch, nlp))
        nlp.update(examples, drop=0.35)
    
    # Evaluate
    scores = evaluate(nlp, dev_data)
    print(f"Epoch {i}: {scores}")

# Save model
nlp.to_disk("my_ner_model")
```

### Fine-Tuning Existing Models

```python
import spacy

# Load pretrained model
nlp = spacy.load("en_core_web_sm")

# Add custom entity labels
ner = nlp.get_pipe("ner")
ner.add_label("CUSTOM_ENTITY")

# Prepare training data with custom entities
train_data = [
    ("This is a CUSTOM_ENTITY example", {"entities": [(10, 23, "CUSTOM_ENTITY")]}),
    # Add more examples...
]

# Fine-tune
nlp.initialize()
for i in range(20):
    random.shuffle(train_data)
    batches = minibatch(train_data, size=8)
    
    for batch in batches:
        examples = [Example.from_dict(nlp.make_doc(text), anns) for text, anns in batch]
        nlp.update(examples, drop=0.35)

nlp.to_disk("fine_tuned_model")
```

## Training Text Classifiers

### Binary Classification

```python
import spacy
from spacy.training import Example

# Prepare data
train_data = [
    ("I love this product", {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}),
    ("Terrible quality", {"cats": {"POSITIVE": 0.0, "NEGATIVE": 1.0}}),
    ("Amazing experience", {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}),
    ("Worst purchase ever", {"cats": {"POSITIVE": 0.0, "NEGATIVE": 1.0}})
]

# Create pipeline
nlp = spacy.blank("en")
textcat = nlp.add_pipe("textcat")
textcat.add_label("POSITIVE")
textcat.add_label("NEGATIVE")

# Train
nlp.initialize()

for i in range(20):
    random.shuffle(train_data)
    
    for text, annotations in train_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        nlp.update([example], drop=0.35)

nlp.to_disk("sentiment_classifier")
```

### Multi-Label Classification

```python
train_data = [
    ("Best phone camera ever", {"cats": {"PHONE": 0.9, "CAMERA": 0.8, "POSITIVE": 0.9}}),
    ("Great laptop for work", {"cats": {"LAPTOP": 0.9, "WORK": 0.7, "POSITIVE": 0.8}}),
    ("Good tablet, bad keyboard", {"cats": {"TABLET": 0.8, "KEYBOARD": 0.7, "MIXED": 0.6}})
]

nlp = spacy.blank("en")
textcat = nlp.add_pipe("textcat_multilabel")

for label in ["PHONE", "LAPTOP", "TABLET", "CAMERA", "KEYBOARD", "WORK", "POSITIVE", "NEGATIVE", "MIXED"]:
    textcat.add_label(label)

# Train as before...
```

## Evaluation

### Basic Evaluation

```python
from spacy.training import Example
import spacy

nlp = spacy.load("my_model")

# Test data
test_data = [
    ("John works at Apple", {"entities": [(0, 4, "PERSON"), (14, 19, "ORG")]}),
    ("London is in the UK", {"entities": [(0, 6, "GPE"), (17, 19, "GPE")]})
]

# Evaluate
scores = {}
for text, annotations in test_data:
    doc = nlp.make_doc(text)
    example = Example.from_dict(doc, annotations)
    
    # Score specific component
    score = nlp.get_pipe("ner").score([example])
    scores.update(score)

print(f"Precision: {scores['entities_p']:.2f}")
print(f"Recall: {scores['entities_r']:.2f}")
print(f"F1: {scores['entities_f']:.2f}")
```

### Using spacy evaluate

```bash
# Evaluate model on test data
python -m spacy evaluate my_model test.json
```

### Detailed Metrics

```python
from spacy.scorer import Scorer

scorer = Scorer()

# Collect predictions and references
preds = []
refs = []

for text, annotations in test_data:
    doc = nlp(text)
    
    # Get predicted entities
    pred_ents = [(ent.start, ent.end, ent.label_) for ent in doc.ents]
    preds.append(pred_ents)
    
    # Reference entities
    refs.append(annotations.get("entities", []))

# Calculate metrics
scores = scorer.score([preds], [refs])
print(scores)
```

## Hyperparameter Tuning

### Using Config Variables

```python
# In config.cfg, define variables
[hyperparams]
dropout = 0.1
batch_size = 8
learning_rate = 0.001
epochs = 20

[training]
dropout = ${hyperparams.dropout}

[training.batcher]
size = ${hyperparams.batch_size}

[training.optimizer]
lr = ${hyperparams.learning_rate}

[training]
max_epochs = ${hyperparams.epochs}
```

### Grid Search with spaCy

```python
from spacy.util import minibatch, compounding
import random

def train_with_params(dropout, batch_size, lr):
    nlp = spacy.blank("en")
    ner = nlp.add_pipe("ner")
    
    # Add labels...
    
    nlp.initialize()
    
    for i in range(20):
        random.shuffle(train_data)
        batches = minibatch(train_data, size=batch_size)
        
        for batch in batches:
            examples = [Example.from_dict(nlp.make_doc(text), anns) for text, anns in batch]
            nlp.update(examples, drop=dropout)
    
    # Evaluate
    score = evaluate(nlp, dev_data)
    return score

# Grid search
params = [
    {"dropout": 0.1, "batch_size": 8, "lr": 0.001},
    {"dropout": 0.2, "batch_size": 16, "lr": 0.0005},
    {"dropout": 0.3, "batch_size": 8, "lr": 0.002}
]

best_score = 0
best_params = None

for params in param_grid:
    score = train_with_params(**params)
    if score > best_score:
        best_score = score
        best_params = params

print(f"Best params: {best_params}, Score: {best_score}")
```

## Advanced Training Features

### Custom Loss Functions

```python
from spacy.ml.models import Model
import thinc.api

@Model.from_args("custom_loss", "X")
def custom_loss_model(X, bgrad):
    def model_func(x):
        return x
    
    def model_grad(x, dY):
        return dY
    
    return model_func, model_grad
```

### Multi-Task Learning

```python
nlp = spacy.blank("en")

# Add multiple components
ner = nlp.add_pipe("ner")
textcat = nlp.add_pipe("textcat")
parser = nlp.add_pipe("parser")

# Train all together - they share representations
nlp.initialize()

for i in range(20):
    random.shuffle(train_data)
    
    for batch in minibatch(train_data, size=8):
        examples = [...]  # Create examples with multiple annotations
        nlp.update(examples)
```

### Callbacks and Hooks

```python
def before_to_disk(model):
    """Called before saving the model"""
    print("Saving model...")
    return model

# Add to config:
[training]
before_to_disk = "before_to_disk"
```

## Common Training Issues

### Class Imbalance

```python
# Use weighted sampling or oversampling
from collections import Counter

# Count label frequencies
label_counts = Counter()
for text, annotations in train_data:
    for start, end, label in annotations.get("entities", []):
        label_counts[label] += 1

# Oversample rare classes or use class weights
```

### Overfitting

```python
# Increase dropout
nlp.update(examples, drop=0.5)

# Add more training data
# Use regularization in config
[training]
dropout = 0.3
L2 = 0.01
```

### Underfitting

```python
# Train longer
for i in range(50):  # More epochs
    ...

# Increase model capacity
[components.ner.model]
hidden_width = 128  # Instead of 64
```

## References

- [Training Documentation](https://spacy.io/usage/training)
- [Configuration Guide](https://spacy.io/usage/training#config)
- [Data Format](https://spacy.io/usage/training#data-formats)
- [Training API](https://spacy.io/api/training)
- [Project Templates](https://github.com/explosion/projects)
