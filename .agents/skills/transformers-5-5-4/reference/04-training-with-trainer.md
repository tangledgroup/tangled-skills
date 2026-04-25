# Training with Trainer - Complete Guide

Comprehensive guide to the Trainer API, custom training loops, distributed training, and mixed precision in Transformers 5.5.4.

## Overview

The Trainer is a comprehensive training framework that supports:
- Mixed precision training (FP16/BF16)
- Distributed training (DDP, FSDP, DeepSpeed)
- Automatic hardware optimization
- Logging and evaluation
- Checkpointing and resume

## Basic Training Setup

### Sequence Classification Example

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import torch
from datasets import load_dataset

# Load dataset
dataset = load_dataset("imdb")

# Load model and tokenizer
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# Tokenize dataset
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=128
    )

tokenized_datasets = dataset.map(tokenize_function, batched=True)
tokenized_datasets = tokenized_datasets.rename_column("label", "labels")
tokenized_datasets.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

# Split train/test
train_dataset = tokenized_datasets["train"].select(range(8000))
eval_dataset = tokenized_datasets["test"].select(range(200))

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    num_train_epochs=3,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=10,
)

# Create trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# Train
trainer.train()

# Evaluate
results = trainer.evaluate()
print(results)

# Save final model
trainer.save_model("./final-model")
```

## Training Arguments Reference

### Basic Configuration

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    # Output directory
    output_dir="./results",
    
    # Training epochs and steps
    num_train_epochs=3,
    max_steps=-1,  # -1 means use num_train_epochs
    
    # Batch sizes
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    gradient_accumulation_steps=1,  # Effective batch = batch_size * accumulation
    
    # Learning rate
    learning_rate=2e-5,
    warmup_ratio=0.1,  # Warmup for first 10% of steps
    lr_scheduler_type="cosine",  # cosine, linear, constant, etc.
    
    # Weight decay
    weight_decay=0.01,
)
```

### Logging and Evaluation

```python
training_args = TrainingArguments(
    # Logging
    logging_dir="./logs",
    logging_steps=50,  # Log every 50 steps
    logging_first_step=True,
    
    # Evaluation
    evaluation_strategy="epoch",  # epoch, steps, or no
    eval_steps=500,  # If strategy="steps"
    
    # Saving
    save_strategy="epoch",  # epoch, steps, or no
    save_steps=500,  # If strategy="steps"
    save_total_limit=2,  # Keep only last 2 checkpoints
    
    # Checkpointing
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    greater_is_better=True,
)
```

### Mixed Precision

```python
training_args = TrainingArguments(
    # FP16 training
    fp16=True,  # Enable FP16 (requires CUDA)
    
    # BF16 training (Ampere+ GPUs)
    bf16=True,  # Enable BF16 instead of FP16
    
    # Full determinism (slower but reproducible)
    dataloader_drop_last=False,
    torch_deterministic=True,
)
```

### Optimization Settings

```python
training_args = TrainingArguments(
    # Gradient clipping
    max_grad_norm=1.0,  # Clip gradients at norm 1.0
    
    # Adam optimizer settings
    adam_beta1=0.9,
    adam_beta2=0.999,
    adam_epsilon=1e-8,
    
    # Label smoothing
    label_smoothing_factor=0.1,
    
    # DeepSpeed configuration
    deepspeed="./deepspeed_config.json",
)
```

## Custom Training Loop

### When to Use Custom Loop

Use a custom training loop when:
- You need full control over the training process
- Your task doesn't fit the Trainer API
- You're implementing novel training techniques
- You need custom gradient manipulation

### Basic Custom Loop

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_scheduler
import torch
from torch.utils.data import DataLoader

# Setup
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# Move to GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Create dataloader
train_dataset = ...  # Your dataset
dataloader = DataLoader(train_dataset, batch_size=16, shuffle=True)

# Optimizer and scheduler
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
num_epochs = 3
num_steps = len(dataloader) * num_epochs
scheduler = get_scheduler(
    "cosine",
    optimizer=optimizer,
    num_warmup_steps=int(0.1 * num_steps),
    num_training_steps=num_steps
)

# Training loop
model.train()
for epoch in range(num_epochs):
    for batch in dataloader:
        # Move to device
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        loss = outputs.loss
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        
        # Update weights
        optimizer.step()
        scheduler.step()
        
        # Logging
        if step % 50 == 0:
            print(f"Epoch {epoch}, Step {step}, Loss: {loss.item():.4f}")
```

### Custom Loop with Mixed Precision

```python
from torch.cuda.amp import autocast, GradScaler

# Setup scaler for FP16 training
scaler = GradScaler()

model.train()
for epoch in range(num_epochs):
    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        
        optimizer.zero_grad()
        
        # Mixed precision forward/backward
        with autocast():
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            loss = outputs.loss
        
        # Scaled backward pass
        scaler.scale(loss).backward()
        
        # Unscaled optimizer step
        scaler.step(optimizer)
        scaler.update()
```

## Custom Trainer

### Extending the Trainer

```python
from transformers import Trainer

class CustomTrainer(Trainer):
    """Custom trainer with additional functionality"""
    
    def compute_loss(self, model, inputs, return_outputs=False):
        """Custom loss computation"""
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        
        # Custom loss calculation
        logits = outputs.logits
        loss_fct = torch.nn.CrossEntropyLoss(label_smoothing=0.1)
        loss = loss_fct(logits, labels)
        
        return (loss, outputs) if return_outputs else loss
    
    def evaluation_loop(self, *args, **kwargs):
        """Custom evaluation logic"""
        # Add custom metrics or preprocessing
        return super().evaluation_loop(*args, **kwargs)

# Usage
trainer = CustomTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)
```

### Custom Metrics

```python
from transformers import Trainer, TrainingArguments
import numpy as np
from sklearn.metrics import f1_score, precision_recall_fscore_support

class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        loss = outputs.loss
        return (loss, outputs) if return_outputs else loss
    
    def prediction_step(self, model, inputs, prediction_loss_only, ignore_keys=None):
        """Custom prediction step for metrics"""
        with torch.no_grad():
            labels = inputs["labels"]
            outputs = model(**inputs)
            logits = outputs.logits
            
            # Get predictions
            predictions = torch.argmax(logits, dim=-1)
        
        return (outputs.loss, predictions, labels)
    
    def compute_metrics(self, eval_pred):
        """Compute custom metrics"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average="binary"
        )
        
        return {
            "f1": f1,
            "precision": precision,
            "recall": recall,
        }

# Usage
trainer = CustomTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)
```

## Distributed Training

### Data Parallelism (DDP)

Automatic with Trainer on multiple GPUs:

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",
    device_ids=[0, 1],  # Use specific GPUs
    per_device_train_batch_size=16,  # Per GPU batch size
    # Total batch size = 16 * num_gpus * gradient_accumulation_steps
)

# Run with multiple GPUs
# accelerate launch train.py  # Automatic DDP setup
```

### Fully Sharded Data Parallelism (FSDP)

For very large models:

```python
from transformers import TrainingArguments
from accelerate.utils import DistributedType

training_args = TrainingArguments(
    output_dir="./results",
    fsdp="full_shard auto_wrap",  # Enable FSDP
    fsdp_config={
        "fsdp_min_num_params": 0,  # Shard everything
        "xla": False,
        "xla_fsdp_grad_ckpt": False,
        "xla_fsdp_grad_accumulation_steps": 1,
        "xla_fsdp_overlap_communication": False,
        "backwards_prefetch": False,
        "forward_prefetch": False,
    },
)

# Run with FSDP
# accelerate launch --num_processes=4 train.py
```

### DeepSpeed Integration

```python
# Create deepspeed_config.json
deepspeed_config = {
    "train_batch_size": 64,
    "train_micro_batch_size_per_gpu": 16,
    "gradient_accumulation_steps": 1,
    "optimizer": {
        "type": "AdamW",
        "params": {
            "lr": 2e-5,
            "betas": [0.9, 0.999],
            "eps": 1e-8,
            "weight_decay": 0.01
        }
    },
    "scheduler": {
        "type": "WarmupLR",
        "params": {
            "warmup_min_lr": 0,
            "warmup_max_lr": 2e-5,
            "warmup_num_steps": 1000
        }
    },
    "fp16": {
        "enabled": True,
        "loss_scale": 0,
        "loss_scale_window": 1000,
        "initial_scale_power": 16,
        "hysteresis": 2,
        "min_loss_scale": 1
    },
    "zero_optimization": {
        "stage": 2,  # 0, 1, 2, or 3
        "allgather_partitions": True,
        "reduce_scatter": True,
        "allgather_bucket_size": 2e8,
        "reduce_bucket_size": 2e8,
        "overlap_comm": True,
        "contiguous_gradients": True
    }
}

import json
with open("deepspeed_config.json", "w") as f:
    json.dump(deepspeed_config, f)

# Use in TrainingArguments
training_args = TrainingArguments(
    output_dir="./results",
    deepspeed="deepspeed_config.json",
)
```

## Callbacks

### Custom Callbacks

```python
from transformers import TrainerCallback, TrainerControl

class EarlyStoppingCallback(TrainerCallback):
    def __init__(self, stopping_threshold=0.0003, min_delta=0):
        self.stopping_threshold = stopping_threshold
        self.min_delta = min_delta
        self.best_metric = None
        self.wait = 0
    
    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if self.best_metric is None:
            self.best_metric = metrics["eval_loss"]
        elif metrics["eval_loss"] > self.best_metric + self.min_delta:
            self.wait += 1
            if self.wait >= 3:  # Stop after 3 epochs without improvement
                control.should_training_stop = True
                print("Early stopping triggered")
        else:
            self.best_metric = metrics["eval_loss"]
            self.wait = 0

# Usage
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    callbacks=[EarlyStoppingCallback()]
)
```

### Logging Callbacks

```python
from transformers import TensorBoardCallback, WandbCallback

# TensorBoard logging (automatic with Trainer)
trainer = Trainer(
    model=model,
    args=training_args,
    # TensorBoard automatically enabled if logging_dir is set
)

# Weights & Biases logging
from transformers.integrations import WandbCallback

trainer = Trainer(
    model=model,
    args=training_args,
    callbacks=[WandbCallback]
)

# Custom logging callback
class CustomLoggingCallback(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is not None:
            # Custom logging logic
            print(f"Custom log: loss={logs.get('loss', 'N/A')}, lr={logs.get('learning_rate', 'N/A')}")

trainer = Trainer(
    model=model,
    args=training_args,
    callbacks=[CustomLoggingCallback()]
)
```

## Hyperparameter Search

### Grid Search with Trainer

```python
from transformers import TrainingArguments, Trainer
import itertools

# Define hyperparameter grid
hyperparameter_search_space = {
    "learning_rate": [2e-5, 3e-5, 5e-5],
    "per_device_train_batch_size": [8, 16],
    "num_train_epochs": [3, 5],
    "weight_decay": [0.01, 0.1],
}

# Manual grid search
best_score = 0
best_params = None

for lr, bs, epochs, wd in itertools.product(
    hyperparameter_search_space["learning_rate"],
    hyperparameter_search_space["per_device_train_batch_size"],
    hyperparameter_search_space["num_train_epochs"],
    hyperparameter_search_space["weight_decay"]
):
    training_args = TrainingArguments(
        output_dir=f"./results_lr{lr}_bs{bs}_e{epochs}_wd{wd}",
        learning_rate=lr,
        per_device_train_batch_size=bs,
        num_train_epochs=epochs,
        weight_decay=wd,
        evaluation_strategy="epoch",
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )
    
    trainer.train()
    metrics = trainer.evaluate()
    
    if metrics["eval_accuracy"] > best_score:
        best_score = metrics["eval_accuracy"]
        best_params = {"lr": lr, "bs": bs, "epochs": epochs, "wd": wd}

print(f"Best params: {best_params}, Score: {best_score}")
```

### Using Optuna for Hyperparameter Search

```python
from transformers import Trainer, TrainingArguments, default_hp_search
import optuna

def hp_space(trial):
    """Define hyperparameter search space"""
    return {
        "learning_rate": trial.loguniform(-8, -4),  # 1e-8 to 1e-4
        "num_train_epochs": trial.choice([3, 5, 7]),
        "per_device_train_batch_size": trial.choice([8, 16, 32]),
        "weight_decay": trial.loguniform(-4, -1),  # 1e-4 to 1e-1
    }

def hp_params(trial):
    """Convert trial params to TrainingArguments"""
    return {
        "learning_rate": trial.params["learning_rate"],
        "num_train_epochs": trial.params["num_train_epochs"],
        "per_device_train_batch_size": trial.params["per_device_train_batch_size"],
        "weight_decay": trial.params["weight_decay"],
    }

# Run hyperparameter search
class TrainerWithHP(Trainer):
    def evaluation_loop(self, *args, **kwargs):
        output = super().evaluation_loop(*args, **kwargs)
        return output
    
    def hp_search_space(self, trial):
        return hp_space(trial)
    
    def optimize_model(self, trial):
        params = hp_params(trial)
        training_args = TrainingArguments(
            output_dir=f"./results_{trial.number}",
            **params,
            evaluation_strategy="epoch",
            load_best_model_at_end=True,
        )
        
        self.args = training_args
        self.train()
        metrics = self.evaluate()
        
        return metrics["eval_accuracy"]

# Run search with Optuna
study = optuna.create_study(direction="maximize")
study.optimize(
    lambda trial: TrainerWithHP(...).optimize_model(trial),
    n_trials=20
)

print(f"Best params: {study.best_params}")
print(f"Best score: {study.best_value}")
```

## Training Tips and Best Practices

### Memory Optimization

```python
training_args = TrainingArguments(
    # Gradient checkpointing (trade compute for memory)
    gradient_checkpointing=True,
    
    # Smaller batch size with gradient accumulation
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,  # Effective batch = 32
    
    # FP16 training
    fp16=True,
    
    # Disable unnecessary features
    disable_tqdm=True,
)
```

### Faster Training

```python
training_args = TrainingArguments(
    # Larger batch size (if GPU memory allows)
    per_device_train_batch_size=32,
    
    # FP16/BF16 training
    fp16=True,  # or bf16=True for Ampere+
    
    # XLA compilation (TPU or CUDA)
    # Use with: xla_spawn() or torch.xla.model_parallel
    
    # DeepSpeed ZeRO-2/3 for large models
    deepspeed="deepspeed_config.json",
)
```

### Reproducibility

```python
import numpy as np
import random
import torch

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

set_seed(42)

training_args = TrainingArguments(
    seed=42,  # Trainer also sets seeds
    data_seed=42,  # For dataset shuffling
)
```

## Troubleshooting

### Out of Memory

```python
# Reduce batch size
training_args.per_device_train_batch_size = 4

# Enable gradient accumulation
training_args.gradient_accumulation_steps = 8

# Enable FP16
training_args.fp16 = True

# Enable gradient checkpointing
model.config.gradient_checkpointing_enable()
```

### NaN Loss

```python
# Reduce learning rate
training_args.learning_rate = 1e-5

# Enable gradient clipping
training_args.max_grad_norm = 1.0

# Check for label issues
# Ensure labels are in correct range [0, num_labels-1]
```

### Slow Training

```python
# Enable FP16/BF16
training_args.fp16 = True

# Use larger batch size
training_args.per_device_train_batch_size = 32

# Compile model (PyTorch 2.0+)
model = torch.compile(model)

# Use Flash Attention
model.config._attn_implementation = "flash_attention_2"
```
