# Fine-Tuning

Fine-tuning trains a custom model on your dataset. The SDK supports supervised learning, DPO (Direct Preference Optimization), and reinforcement learning methods.

## Creating a Fine-Tuning Job

### Supervised Fine-Tuning

```python
from openai import OpenAI

client = OpenAI()

# First upload your training data
file = client.files.create(
    file=open("training_data.jsonl", "rb"),
    purpose="fine-tune",
)

# Create the job
job = client.fine_tuning.jobs.create(
    model="gpt-4o-mini",
    training_file=file.id,
    method={
        "type": "supervised",
        "hyperparameters": {
            "n_epochs": 3,
            "learning_rate_multiplier": 1,
            "batch_size": "auto",
        },
    },
)
```

### DPO (Direct Preference Optimization)

Train with preferred/rejected pairs:

```python
job = client.fine_tuning.jobs.create(
    model="gpt-4o-mini",
    training_file=file.id,
    method={
        "type": "dpo",
        "hyperparameters": {
            "n_epochs": 3,
            "beta": 0.1,
        },
    },
)
```

### Reinforcement Learning

```python
job = client.fine_tuning.jobs.create(
    model="gpt-4o-mini",
    training_file=file.id,
    method={
        "type": "reinforcement",
        "hyperparameters": {
            "n_epochs": 5,
        },
    },
)
```

## Training Data Format

JSONL format with chat completions structure:

```jsonl
{"messages": [{"role": "user", "content": "What is 2+2?"}, {"role": "assistant", "content": "4"}]}
{"messages": [{"role": "user", "content": "Capital of France?"}, {"role": "assistant", "content": "Paris"}]}
```

For DPO, include `chosen` and `rejected` responses:

```jsonl
{"chosen": {"role": "assistant", "content": "Good answer"}, "rejected": {"role": "assistant", "content": "Bad answer"}, "messages": [...]}
```

## Monitoring Progress

```python
# Retrieve job status
job = client.fine_tuning.jobs.retrieve("ftjob-abc123")
print(job.status)  # validating_files, queued, running, succeeded, failed, cancelled

# List events
events = client.fine_tuning.jobs.list_events(
    fine_tuning_job_id="ftjob-abc123",
    limit=10,
)
for event in events:
    print(event.message)
```

## Job Management

```python
# List all jobs
jobs = client.fine_tuning.jobs.list(limit=20)

# Cancel a running job
cancelled = client.fine_tuning.jobs.cancel("ftjob-abc123")

# Pause and resume
paused = client.fine_tuning.jobs.pause("ftjob-abc123")
resumed = client.fine_tuning.jobs.resume("ftjob-abc123")
```

## Checkpoints

Access training checkpoints:

```python
checkpoints = client.fine_tuning.jobs.checkpoints.list(
    fine_tuning_job_id="ftjob-abc123",
    limit=5,
)
for cp in checkpoints:
    print(cp.id, cp.metrics)
```

## Using a Fine-Tuned Model

Once training completes, use the model ID in any API call:

```python
response = client.responses.create(
    model=f"ft:gpt-4o-mini:your-org:abc123",
    input="Question for my fine-tuned model.",
)
```

## Validation Files

Include a validation set for early stopping:

```python
job = client.fine_tuning.jobs.create(
    model="gpt-4o-mini",
    training_file=training_file_id,
    validation_file=validation_file_id,
    method={"type": "supervised"},
)
```

## WandB Integration

Log metrics to Weights & Biases:

```python
job = client.fine_tuning.jobs.create(
    model="gpt-4o-mini",
    training_file=file.id,
    method={"type": "supervised"},
    integrations=[
        {
            "type": "wandb",
            "wandb": {
                "name": "my-fine-tune-run",
                "project": "my-project",
                "entity": "my-team",
            },
        }
    ],
)
```
