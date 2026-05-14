# Training and Fine-tuning

## Trainer API

`Trainer` is a complete training and evaluation loop for PyTorch models. It handles batching, shuffling, padding, forward pass, loss calculation, backpropagation, and weight updates.

```python
from transformers import Trainer, TrainingArguments

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    processing_class=tokenizer,
    data_collator=data_collator,
)

trainer.train()
trainer.push_to_hub()
```

## TrainingArguments

`TrainingArguments` controls all training hyperparameters and behavior:

### Duration and Batch Size

- `num_train_epochs` — Number of training epochs
- `per_device_train_batch_size` — Batch size per device
- `per_device_eval_batch_size` — Evaluation batch size per device
- `learning_rate` — Initial learning rate

### Optimizations

- `bf16=True` — Mixed precision with bfloat16 (Ampere+ GPUs)
- `fp16=True` — Mixed precision with float16 (older GPUs)
- `gradient_accumulation_steps=N` — Accumulate gradients over N steps before updating weights
- `gradient_checkpointing=True` — Trade compute for memory by recomputing activations during backward pass
- `torch_compile=True` — Enable torch.compile for faster training

### Evaluation and Checkpointing

- `eval_strategy="epoch"` or `"steps"` — When to evaluate
- `save_strategy="epoch"` or `"steps"` — When to save checkpoints
- `load_best_model_at_end=True` — Load best checkpoint at end (requires eval_strategy)

### Logging

- `logging_steps=N` — Frequency of loss logging
- `report_to="wandb"` — Integration with Weights & Biases

```python
training_args = TrainingArguments(
    output_dir="my-model-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,
    bf16=True,
    learning_rate=2e-5,
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    push_to_hub=True,
)
```

## Data Collators

Data collators assemble dataset samples into batches:

```python
from transformers import DataCollatorWithPadding, DataCollatorForLanguageModeling

# Dynamic padding to longest sequence in batch
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Language modeling with masking (MLM) or without (CAusal LM)
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
```

Dynamic padding saves compute by avoiding unnecessary padding tokens.

## Dataset Preparation

```python
from datasets import load_dataset
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
dataset = load_dataset("karthiksagarn/astro_horoscope", split="train")

def tokenize(batch):
    return tokenizer(batch["horoscope"], truncation=True, max_length=512)

dataset = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)
dataset = dataset.train_test_split(test_size=0.1)
```

## Callbacks

Hook into training events for logging, early stopping, and custom behavior:

```python
from transformers import TrainerCallback

class MyCallback(TrainerCallback):
    def on_epoch_end(self, args, state, control, **kwargs):
        print(f"Epoch {state.epoch} complete, loss: {state.log_history[-1]['loss']}")

trainer.add_callback(MyCallback())
```

Built-in callbacks include `EarlyStoppingCallback`, `SaveCallback`, and `LoggerCallback`.

## Subclassing Trainer

Override Trainer methods for custom behavior:

```python
from transformers import Trainer

class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        # Custom loss computation
        outputs = model(**inputs)
        loss = outputs.loss
        return (loss, outputs) if return_outputs else loss

trainer = CustomTrainer(model=model, args=args, ...)
```

## Distributed Training

### FSDP (Fully Sharded Data Parallel)

Shards model parameters, gradients, and optimizer states across GPUs:

```python
from transformers import Trainer, TrainingArguments, FsdpConfig

fsdp_config = FsdpConfig(
    backward_prefetch="BACKWARD_PRE",
    sharding_strategy="FULL_SHARD",
)

training_args = TrainingArguments(
    output_dir="output",
    fsdp=["FULL_SHARD", "AUTO_WRAP_POLICY", "TRANSFORMER_BASED_WRAP"],
    fsdp_config=fsdp_config,
)
```

### DeepSpeed

Zero-redundancy optimizer with 3 stages of optimization:

```python
training_args = TrainingArguments(
    output_dir="output",
    deepspeed="ds_config.json",
)
```

### Accelerate

Use the `accelerate` library for distributed training across multiple GPUs or nodes.

## Parameter-Efficient Fine-tuning (PEFT)

Fine-tune only a small subset of parameters using LoRA, adapters, or prefix tuning:

```python
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # Shows small fraction of total params
```

## Hyperparameter Search

Use `Trainer.hyperparameter_search()` for automated hyperparameter optimization:

```python
def model_init(params):
    model = AutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=3,
        attention_dropout=params["attention_dropout"],
    )
    return model

def hp_space(trial):
    return {
        "learning_rate": trial["learning_rate"],
        "per_device_train_batch_size": trial["batch_size"],
        "attention_dropout": trial["attention_dropout"],
    }

trainer.hyperparameter_search(
    backend="optuna",
    direction="minimize",
    hp_space=hp_space,
    n_trials=10,
)
```
