# Modules Reference

SentenceTransformer models are built from sequential modules. Each module transforms features (a dict of tensors) and passes them to the next module.

## Base Modules

### Transformer

The backbone module wrapping any Hugging Face transformer model. Auto-detects modality (text, image, audio, video) from the underlying model configuration.

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.base.modules import Transformer, Pooling

model = SentenceTransformer(modules=[
    Transformer("bert-base-uncased"),
    Pooling(),
])
```

### Dense

A fully-connected layer applied to the sentence embedding:

```python
from sentence_transformers.base.modules import Dense
import torch.nn as nn

dense = Dense(
    in_features=768,
    out_features=256,
    activation=nn.ReLU(),
)
```

### Module (Base Class)

All modules inherit from `Module`. Key methods:

- `forward(features)` — transforms feature dict
- `save(output_path)` — persist module state
- `load(model_path)` — classmethod to restore
- `get_embedding_dimension()` — return output dimension
- `encode_pair(input_1, input_2)` — for pair-based modules

### InputModule

Base class for modules that handle input processing (tokenization, preprocessing). Both `Transformer` and `Router` extend this.

### Router

Creates flexible models that dynamically route inputs based on task type and modality:

```python
from sentence_transformers.sentence_transformer.modules import Router

router = Router(
    sub_modules={
        "query": [Transformer("distilbert-base"), Pooling()],
        "document": [Transformer("bert-base"), Pooling(), Dense(768, 512)],
    },
    default_route="document",
)
```

Convenience factory:

```python
router = Router.for_query_document(
    query_modules=[...],
    document_modules=[...],
)
```

Route priority order: exact `(task, modality)` → `(task, None)` → `(None, modality)` → `(None, None)` → direct task lookup → direct modality lookup → `default_route`.

## Sentence Transformer Modules

### Pooling

Reduces variable-length token sequences to fixed-size vectors. Supports multiple strategies, combinable via tuple:

```python
from sentence_transformers.sentence_transformer.modules import Pooling

# Single mode
pooling = Pooling(768, pooling_mode="mean")

# Multiple modes (concatenated)
pooling = Pooling(768, pooling_mode=("mean", "cls"))
```

Available modes:

- **`"mean"`** — average over token embeddings (default)
- **`"cls"`** — use [CLS] token embedding
- **`"max"`** — max pooling over tokens
- **`"weightedmean"`** — attention-weighted mean
- **`"mean_sqrt_len_tokens"`** — mean divided by sqrt of token count
- **`"lasttoken"`** — last token embedding

Parameter `include_prompt=False` excludes prompt tokens from pooling (useful for INSTRUCTOR-style models).

### Normalize

L2-normalizes the sentence embedding to unit length:

```python
from sentence_transformers.sentence_transformer.modules import Normalize

normalize = Normalize()
```

Essential when using dot product as similarity metric (dot product on normalized vectors = cosine similarity).

### Dropout

Standard dropout applied to sentence embeddings:

```python
from sentence_transformers.sentence_transformer.modules import Dropout

dropout = Dropout(0.1)  # 10% dropout
```

### LayerNorm

Layer normalization on sentence embeddings:

```python
from sentence_transformers.sentence_transformer.modules import LayerNorm

ln = LayerNorm()
```

### WeightedLayerPooling

Weighted mean pooling across multiple transformer hidden layers:

```python
from sentence_transformers.sentence_transformer.modules import WeightedLayerPooling

wlp = WeightedLayerPooling(
    embedding_dimension=768,
    num_hidden_layers=12,
    layer_start=4,
)
```

Requires the Transformer to output `all_layer_embeddings` (set `enable_layer_dropout=False` and configure accordingly).

### WordEmbeddings

FastText or word-level embeddings as an alternative to transformer backbones:

```python
from sentence_transformers.sentence_transformer.modules import WordEmbeddings

we = WordEmbeddings("https://s3.eu-central-1.amazonaws.com/avg-gluon-nlp/models/fasttext_cc_en_300d.pt")
```

### WordWeights

Weight tokens by importance (e.g., inverse document frequency):

```python
from sentence_transformers.sentence_transformer.modules import WordWeights

ww = WordWeights()
```

### StaticEmbedding

Static (pre-computed) embeddings for fast query encoding without transformer inference:

```python
from sentence_transformers.sentence_transformer.modules import StaticEmbedding

se = StaticEmbedding(model_name_or_path="sentence-transformers/static-retrieval-mrl-en-v1")
```

### BoW (Bag-of-Words)

TF-IDF bag-of-words representation:

```python
from sentence_transformers.sentence_transformer.modules import BoW

bow = BoW()
```

### CNN

Convolutional neural network layer on token embeddings:

```python
from sentence_transformers.sentence_transformer.modules import CNN

cnn = CNN(in_channels=768, out_channels=128, kernel_sizes=[1, 2, 3])
```

### LSTM

LSTM layer on token embeddings:

```python
from sentence_transformers.sentence_transformer.modules import LSTM

lstm = LSTM(768, hidden_dim=256, num_layers=2)
```

### CLIPModel (Deprecated)

Legacy multimodal module. Use `Transformer` directly instead — it auto-detects CLIP-style models via modality configuration.

## CrossEncoder Modules

CrossEncoder uses the same base modules plus:

### LogitScore

Applies a linear layer + activation to produce the final score:

```python
from sentence_transformers.cross_encoder.modules import LogitScore

logit = LogitScore(768)
```

## SparseEncoder Modules

SparseEncoder-specific modules:

### SpladePooling

SParse LAtent Encoder pooling — produces sparse vocabulary-sized vectors:

```python
from sentence_transformers.sparse_encoder.modules import SpladePooling

splade = SpladePooling()
```

### SparseAutoEncoder

Autoencoder-based sparse encoding:

```python
from sentence_transformers.sparse_encoder.modules import SparseAutoEncoder

sae = SparseAutoEncoder(
    model_name_or_path="bert-base-uncased",
    encoder_dimension=768,
)
```

## Building Custom Models

Compose modules into a custom pipeline:

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.base.modules import Transformer, Dense
from sentence_transformers.sentence_transformer.modules import Pooling, Normalize, Dropout

model = SentenceTransformer(modules=[
    Transformer("bert-base-uncased"),
    Pooling(768, pooling_mode="mean"),
    Dense(768, 256),
    Dropout(0.1),
    Normalize(),
])

embeddings = model.encode(["Hello world"])
print(embeddings.shape)  # (1, 256)
```

Save and load custom models:

```python
model.save("my-custom-model")
reloaded = SentenceTransformer("my-custom-model")
```

## Modality Configuration

The Transformer module handles multimodal inputs through `ModalityConfig`. For CLIP models:

```python
modality_config = {
    "text": {"method": "get_text_features", "method_output_name": "pooler_output"},
    "image": {"method": "get_image_features", "method_output_name": "pooler_output"},
}
```

Modality is auto-detected from input types: strings → text, PIL Images → image, audio tensors → audio, video tensors → video. Override with explicit `modality` parameter in `encode()`.
