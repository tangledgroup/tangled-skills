# Training Overview

Comprehensive guide to training and fine-tuning Sentence Transformer models.

## Why Fine-Tune?

Pretrained models work well for general tasks, but fine-tuning provides:

- **Domain adaptation**: Specialize for medical, legal, technical domains
- **Task optimization**: Improve for specific use cases (search, clustering, etc.)
- **Language support**: Extend to low-resource languages
- **Performance gains**: 5-20% improvement on domain-specific benchmarks

## Training Components

### 1. Model

Choose base model to fine-tune:

```python
from sentence_transformers import SentenceTransformer

# Start from pretrained model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Or initialize from transformers model
from transformers import AutoModel
model = SentenceTransformer(AutoModel.from_pretrained("bert-base-uncased"))
```

### 2. Dataset

Prepare training data in appropriate format:

```python
from sentence_transformers import InputExample

# For pair-based losses (STS, similarity)
train_examples = [
    InputExample(texts=["sentence A", "sentence B"], label=0.8),  # Similarity score
    InputExample(texts=["sentence C", "sentence D"], label=0.2),
]

# For triplet losses
train_examples = [
    InputExample(
        texts=["anchor", "positive", "negative"],
        label=1.0
    ),
]

# For classification (NLI, duplicate detection)
train_examples = [
    InputExample(texts=["premise", "hypothesis"], label=0),  # Entailment
    InputExample(texts=["premise", "hypothesis"], label=1),  # Neutral
    InputExample(texts=["premise", "hypothesis"], label=2),  # Contradiction
]
```

### 3. Loss Function

Select loss function based on task:

```python
from sentence_transformers.losses import (
    CosineSimilarityLoss,           # STS with similarity scores
    MultipleNegativesRankingLoss,   # Single sentences (paraphrases)
    TripletLoss,                    # Anchor-positive-negative triplets
    SoftmaxLoss,                    # Classification tasks
    ContrastiveLoss,                # Binary similar/dissimilar pairs
)

# Example: STS task
loss_fn = CosineSimilarityLoss(model)

# Example: Paraphrase mining training
loss_fn = MultipleNegativesRankingLoss(model)
```

See [`references/07-loss-functions.md`](references/07-loss-functions.md) for complete loss function guide.

### 4. Training Arguments

Configure training hyperparameters:

```python
from sentence_transformers.training_args import SentenceTransformerTrainingArguments

train_args = SentenceTransformerTrainingArguments(
    # Output directory
    output_dir="./models/my-finetuned-model",
    
    # Training duration
    num_train_epochs=3,
    max_steps=1000,  # Or use epochs
    
    # Batch size
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    
    # Learning rate
    learning_rate=2e-5,
    weight_decay=0.01,
    
    # Optimization
    warmup_ratio=0.1,
    lr_scheduler_type="cosine",
    
    # Logging and evaluation
    logging_steps=50,
    evaluation_strategy="steps",
    eval_steps=100,
    save_steps=100,
    save_total_limit=3,
    
    # Mixed precision (faster training on GPU)
    fp16=True,  # Or bf16 for Ampere GPUs
    
    # Other options
    seed=42,
    run_name="my-experiment",
)
```

### 5. Evaluator

Monitor training progress:

```python
from sentence_transformers import evaluator as se
from datasets import load_dataset

# Load evaluation dataset
eval_dataset = load_dataset("glue", "stsb", split="validation")

# Create evaluator (cosine similarity for STS)
evaluator = se.SentenceSimilarityEvaluator(
    sentences1=eval_dataset['sentence1'],
    sentences2=eval_dataset['sentence2'],
    scores=eval_dataset['label'],
    main_si_model="cosine",
    batch_size=32,
    output_path="./eval-results",
)

# Alternative: Information Retrieval evaluator
evaluator = se.InformationRetrievalEvaluator(
    queries=eval_dataset['query'],
    corpus=eval_dataset['corpus'],
    relevant_docs=eval_dataset['positive'],
    main_info_retrieval_metric="ndcgAt10",
)
```

### 6. Trainer

Orchestrate training process:

```python
from sentence_transformers.trainer import SentenceTransformerTrainer

trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=train_examples,
    loss=loss_fn,
    evaluator=evaluator,
)

# Start training
trainer.train()

# Save final model
trainer.save_model("./final-model")
```

## Complete Training Example

### STS Task Training

```python
from sentence_transformers import SentenceTransformer, evaluator, datasets
from sentence_transformers.losses import CosineSimilarityLoss
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer
import numpy as np

# 1. Load base model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Load training data (STS dataset)
train_dataset = datasets.StsBenchmark(name="stsbenchmark", split="train")
eval_dataset = datasets.StsBenchmark(name="stsbenchmark", split="test")

# 3. Define loss function
loss_fn = CosineSimilarityLoss(model)

# 4. Create evaluator
evaluator = se.SentenceSimilarityEvaluator(
    sentences1=eval_dataset.sentences1,
    sentences2=eval_dataset.sentences2,
    scores=np.array(eval_dataset.scores),
    main_si_model="cosine",
    batch_size=32,
)

# 5. Configure training
train_args = SentenceTransformerTrainingArguments(
    output_dir="./sts-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
    warmup_ratio=0.1,
    evaluation_strategy="steps",
    eval_steps=500,
    logging_steps=100,
    fp16=True,
)

# 6. Create trainer
trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=train_dataset,
    loss=loss_fn,
    evaluator=evaluator,
)

# 7. Train
trainer.train()

# 8. Save model
trainer.save_model("./final-sts-model")

# Optional: Push to Hugging Face Hub
trainer.model.push_to_hub("username/sts-finetuned-model")
```

## Multi-Dataset Training

Train on multiple datasets simultaneously:

```python
from sentence_transformers import SentenceTransformer, InputExample
from sentence_transformers.losses import (
    MultipleNegativesRankingLoss,
    CosineSimilarityLoss,
)
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Dataset 1: Paraphrase pairs (Quora)
quora_data = [
    InputExample(texts=["q1", "q2"], label=1.0),  # Duplicate
    InputExample(texts=["q1", "q3"], label=0.0),  # Not duplicate
]

# Dataset 2: STS pairs (STS-B)
sts_data = [
    InputExample(texts=["s1", "s2"], label=0.8),  # Similarity score
]

# Dataset 3: Triplets
triplet_data = [
    InputExample(texts=["anchor", "positive", "negative"]),
]

# Create multi-dataset training with different losses
train_datasets = [
    ("quora", quora_data, MultipleNegativesRankingLoss(model)),
    ("sts", sts_data, CosineSimilarityLoss(model)),
    ("triplets", triplet_data, TripletLoss(model)),
]

train_args = SentenceTransformerTrainingArguments(
    output_dir="./multi-dataset-model",
    num_train_epochs=5,
    per_device_train_batch_size=16,
    learning_rate=1e-5,
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_datasets=train_datasets,  # List of (name, dataset, loss) tuples
)

trainer.train()
```

## Callbacks

Customize training with callbacks:

```python
from sentence_transformers.trainer_callback import TrainerCallback
import numpy as np

class EarlyStoppingCallback(TrainerCallback):
    def __init__(self, patience=3, metric="eval_loss"):
        self.patience = patience
        self.metric = metric
        self.best_value = float('inf')
        self.wait = 0
    
    def on_evaluate(self, args, state, control, logs=None, **kwargs):
        current_value = logs.get(self.metric, float('inf'))
        
        if current_value < self.best_value:
            self.best_value = current_value
            self.wait = 0
        else:
            self.wait += 1
            
            if self.wait >= self.patience:
                print(f"Early stopping at step {state.global_step}")
                control.should_training_stop = True

# Use callback
trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=train_data,
    loss=loss_fn,
    callbacks=[EarlyStoppingCallback(patience=5)],
)
```

## Distributed Training

### Multi-GPU Training

```python
# Using accelerate (automatic)
train_args = SentenceTransformerTrainingArguments(
    output_dir="./distributed-model",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    # Auto-detect GPUs
    # Use all available GPUs by default
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=train_data,
    loss=loss_fn,
)

trainer.train()  # Automatically uses all GPUs
```

### FSDP (Fully Sharded Data Parallel)

For very large models:

```python
from sentence_transformers.training_args import SentenceTransformerTrainingArguments

train_args = SentenceTransformerTrainingArguments(
    output_dir="./fsdp-model",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    fsdp="full_shard auto_wrap",  # Enable FSDP
    fsdp_config={
        "sharding_strategy": "FULL_SHARD",
        "cpu_offload": False,
    },
)
```

## Training Tips

1. **Start small**: Fine-tune MiniLM first before larger models
2. **Monitor loss**: Watch for overfitting (train loss ↓, eval loss ↑)
3. **Learning rate**: 1e-5 to 5e-5 typical for fine-tuning
4. **Batch size**: Larger is better (use gradient accumulation if needed)
5. **Mixed precision**: Use fp16/bf16 for faster training on GPU
6. **Early stopping**: Stop when eval metrics plateau
7. **Multi-task**: Combine datasets for more robust models

## Common Issues

### Issue: Out of memory during training

**Solutions**:
- Reduce `per_device_train_batch_size`
- Enable gradient accumulation: `gradient_accumulation_steps=4`
- Use mixed precision: `fp16=True`
- Enable CPU offloading in FSDP config

### Issue: Loss not decreasing

**Solutions**:
- Increase learning rate (try 5e-5)
- Check data format matches loss function requirements
- Verify labels are in correct range (0-1 for similarity)
- Try different loss function

### Issue: Model overfitting

**Solutions**:
- Add more training data
- Reduce number of epochs
- Increase weight_decay (try 0.05)
- Use early stopping callback
- Add dropout layers

## Next Steps

After training:
1. **Evaluate on MTEB**: See [`references/12-evaluation.md`](references/12-evaluation.md)
2. **Optimize for inference**: See [`references/09-model-optimization.md`](references/09-model-optimization.md)
3. **Share with community**: Push to Hugging Face Hub
