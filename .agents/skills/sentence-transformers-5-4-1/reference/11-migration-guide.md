# Migration Guide

Guide for migrating to Sentence Transformers v5.4.x from earlier versions.

## Migrating from v5.x to v5.4+

### Updated Import Paths

Some modules have been reorganized:

```python
# Old (v5.0-5.3)
from sentence_transformers import util
from sentence_transformers.evaluation import SentenceSimilarityEvaluator

# New (v5.4+)
from sentence_transformers import util
from sentence_transformers import evaluator as se
evaluator = se.SentenceSimilarityEvaluator(...)
```

### Renamed Methods and Parameters

```python
# Old
model.encode(sentences, batch_size=32, use_gpu=True)

# New (use_gpu deprecated)
model = SentenceTransformer("model-name", device="cuda")
model.encode(sentences, batch_size=32)
```

### CrossEncoder max_length → max_seq_length

```python
# Old
model = CrossEncoder("model-name", max_length=256)

# New
model = CrossEncoder("model-name", max_seq_length=256)
```

### Trainer tokenizer → processing_class

```python
# Old
trainer = SentenceTransformerTrainer(
    model=model,
    tokenizer=my_tokenizer,
)

# New
trainer = SentenceTransformerTrainer(
    model=model,
    processing_class=my_processor,
)
```

### tokenizer_kwargs → processor_kwargs

```python
# Old
model = SentenceTransformer("model-name", tokenizer_kwargs={"padding_side": "right"})

# New
model = SentenceTransformer("model-name", processor_kwargs={"padding_side": "right"})
```

### CrossEncoder API Changes

```python
# Old - predict returns raw scores
scores = model.predict(pairs)

# New - same, but use apply_softmax for probabilities
probs = model.predict(pairs, apply_softmax=True)
```

### Removed tags Parameter from push_to_hub

```python
# Old
model.push_to_hub("username/model", tags=["embedding", "sts"])

# New - use Hugging Face Hub API directly
from huggingface_hub import HfApi
api = HfApi()
api.create_repo("model", repo_type="model")
model.push_to_hub("username/model")
# Then add tags via HF web interface or API
```

## Migrating from v4.x to v5.x

### Model.encode() Changes

Major changes to the encode method:

```python
# Old (v4.x)
embeddings = model.encode(sentences, batch_size=32, show_progress_bar=True)

# New (v5.x) - same basic API, but with more options
embeddings = model.encode(
    sentences,
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True,  # Explicit conversion
    normalize_embeddings=False,
)
```

### Asym to Router

Asymmetric encoding now uses router pattern:

```python
# Old
model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
query_emb = model.encode(query, prompt="query:")
doc_emb = model.encode(doc, prompt="passage:")

# New - use prompt_name for built-in prompts
query_emb = model.encode(query, prompt_name="query")
doc_emb = model.encode(doc, prompt_name="passage")
```

### Advanced Usage Changes

```python
# Old - direct access to auto_model
token_ids = model.auto_model.tokenizer.encode("text")

# New - use processor
processing_output = model.processor("text", return_tensors="pt")
token_ids = processing_output["input_ids"]
```

## Migrating from v3.x to v4.x

### CrossEncoder Parameters

Many parameters renamed or reorganized:

```python
# Old (v3.x)
model = CrossEncoder(
    "model-name",
    num_labels=1,
    max_length=256,
)

# New (v4.x+)
model = CrossEncoder(
    "model-name",
    num_labels=1,
    max_seq_length=256,
)
```

### CrossEncoder.fit() Changes

```python
# Old
model.fit(
    train_objectives=train_data,
    evaluator=evaluator,
    epochs=3,
    steps_per_epoch=1000,
    scheduler_name="cosine",
    warmup_steps=100,
)

# New - use Trainer API
from sentence_transformers.trainer import CrossEncoderTrainer
from sentence_transformers.training_args import CrossEncoderTrainingArguments

train_args = CrossEncoderTrainingArguments(
    output_dir="./model",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
)

trainer = CrossEncoderTrainer(
    model=model,
    args=train_args,
    train_dataset=train_data,
)
trainer.train()
```

### CrossEncoder Evaluators

```python
# Old
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
evaluator = EmbeddingSimilarityEvaluator(...)

# New - renamed
from sentence_transformers import evaluator as se
evaluator = se.SentenceSimilarityEvaluator(...)
```

## Migrating from v2.x to v3.x

### SentenceTransformer.fit() Changes

```python
# Old (v2.x)
model.fit(
    train_objectives=train_data,
    epochs=1,
    scheduler="WarmupLinearSchedule",
    warmup_steps=100,
)

# New (v3.x+) - use Trainer API
from sentence_transformers.trainer import SentenceTransformerTrainer
from sentence_transformers.training_args import SentenceTransformerTrainingArguments

train_args = SentenceTransformerTrainingArguments(
    output_dir="./model",
    num_train_epochs=1,
    per_device_train_batch_size=16,
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=train_data,
    loss=loss_fn,
)
trainer.train()
```

### Custom Datasets and DataLoaders

```python
# Old - custom DataLoader passed to fit()
dataloader = DataLoader(dataset, batch_size=16)
model.fit(train_objectives=[(dataloader, loss_fn)], epochs=1)

# New - pass dataset directly to Trainer
trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=dataset,  # Not dataloader
    loss=loss_fn,
)
```

## General Migration Tips

1. **Update imports**: Use new module paths (`evaluator as se`)
2. **Use Trainer API**: Replace `.fit()` with `SentenceTransformerTrainer`
3. **Check parameter names**: `max_length` → `max_seq_length`, `tokenizer_kwargs` → `processor_kwargs`
4. **Device handling**: Set device on model init, not in encode()
5. **Explicit conversions**: Use `convert_to_numpy=True` or `convert_to_tensor=True`

## Testing Your Migration

After migrating, verify:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("your-model")

# Test encoding
test_sentences = ["Hello world", "Test sentence"]
embeddings = model.encode(test_sentences)
assert embeddings.shape == (2, model.get_sentence_embedding_dimension())

# Test similarity
from sentence_transformers import util
sim = util.cos_sim(embeddings[0].unsqueeze(0), embeddings[1].unsqueeze(0))
assert sim.shape == (1, 1)

print("✓ Migration successful!")
```

## Common Issues

### Issue: ImportError for evaluation module

**Solution**: Use new import path:
```python
from sentence_transformers import evaluator as se
```

### Issue: max_length attribute not found

**Solution**: Use `max_seq_length` instead

### Issue: Trainer API missing parameters

**Solution**: Move parameters to `SentenceTransformerTrainingArguments`:
```python
train_args = SentenceTransformerTrainingArguments(
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    # ... other params
)
```
