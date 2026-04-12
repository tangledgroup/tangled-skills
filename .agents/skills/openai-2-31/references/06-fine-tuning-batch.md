# Fine-Tuning and Batch Processing

Comprehensive guide to fine-tuning OpenAI models on custom datasets and processing large batches of requests cost-effectively.

## Fine-Tuning Overview

Fine-tuning creates a custom model optimized for your specific use case:
- **Improved performance** on domain-specific tasks
- **Consistent formatting** and style
- **Better few-shot learning** with examples in training data
- **Cost efficiency** for high-volume, repetitive tasks

### Supported Models for Fine-Tuning

| Base Model | Fine-Tuned Model | Use Case |
|------------|------------------|----------|
| `gpt-4o-mini` | `gpt-4o-mini-ft-...` | Cost-effective chat/completions |
| `gpt-3.5-turbo` | `gpt-3.5-turbo-ft-...` | Legacy, still supported |

## Preparing Training Data

### Format Requirements

Training data must be in JSONL format with conversations:

```jsonl
{"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is quantum computing?"}, {"role": "assistant", "content": "Quantum computing uses quantum mechanics to process information..."}]}
{"messages": [{"role": "user", "content": "Explain photosynthesis"}, {"role": "assistant", "content": "Photosynthesis is the process by which plants..."}]}
```

### Creating Training Data

```python
import json

# Example: Create training data for a customer service bot
training_data = [
    {
        "messages": [
            {"role": "system", "content": "You are a helpful customer service representative."},
            {"role": "user", "content": "How do I reset my password?"},
            {"role": "assistant", "content": "To reset your password, go to the login page and click 'Forgot Password'."}
        ]
    },
    {
        "messages": [
            {"role": "user", "content": "What are your business hours?"},
            {"role": "assistant", "content": "Our business hours are Monday through Friday, 9 AM to 5 PM EST."}
        ]
    },
]

# Write to JSONL file
with open("training_data.jsonl", "w") as f:
    for item in training_data:
        f.write(json.dumps(item) + "\n")

print(f"Created {len(training_data)} training examples")
```

### Data Quality Guidelines

1. **Minimum 10 examples**, recommended 100+ for best results
2. **Variety of inputs** covering different scenarios
3. **High-quality responses** that match desired behavior
4. **Consistent formatting** across all examples
5. **Include system messages** if you want specific behavior
6. **Keep conversations short** (2-4 turns typically)

### Validating Training Data

```python
import json

def validate_training_data(filepath: str) -> dict:
    """Validate training data format and quality."""
    errors = []
    warnings = []
    stats = {
        "total_examples": 0,
        "with_system_message": 0,
        "avg_messages_per_example": 0,
    }
    
    total_messages = 0
    
    with open(filepath, "r") as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                
                if "messages" not in data:
                    errors.append(f"Line {line_num}: Missing 'messages' field")
                    continue
                
                messages = data["messages"]
                stats["total_examples"] += 1
                total_messages += len(messages)
                
                # Check for required fields
                for i, msg in enumerate(messages):
                    if "role" not in msg:
                        errors.append(f"Line {line_num}, message {i}: Missing 'role'")
                    if "content" not in msg:
                        errors.append(f"Line {line_num}, message {i}: Missing 'content'")
                    
                    # Validate role
                    if msg.get("role") not in ["system", "user", "assistant"]:
                        errors.append(f"Line {line_num}, message {i}: Invalid role '{msg.get('role')}'")
                
                # Track system messages
                if any(m.get("role") == "system" for m in messages):
                    stats["with_system_message"] += 1
                
                # Warn about very long conversations
                if len(messages) > 10:
                    warnings.append(f"Line {line_num}: Very long conversation ({len(messages)} messages)")
                
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: Invalid JSON - {e}")
    
    stats["avg_messages_per_example"] = total_messages / max(stats["total_examples"], 1)
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
    }

# Usage
result = validate_training_data("training_data.jsonl")

if result["valid"]:
    print("✓ Training data is valid!")
    print(f"Examples: {result['stats']['total_examples']}")
    print(f"Avg messages per example: {result['stats']['avg_messages_per_example']:.1f}")
else:
    print("✗ Training data has errors:")
    for error in result["errors"][:10]:  # Show first 10 errors
        print(f"  {error}")
```

## Uploading Training Data

```python
from openai import OpenAI

client = OpenAI()

# Upload file for fine-tuning
file = client.files.create(
    file=open("training_data.jsonl", "rb"),
    purpose="fine-tune",
)

print(f"Uploaded file ID: {file.id}")
print(f"File status: {file.status}")
```

## Creating a Fine-Tuning Job

### Basic Fine-Tuning Job

```python
from openai import OpenAI

client = OpenAI()

# Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file="file-abc123",  # ID of uploaded training file
    model="gpt-4o-mini",          # Base model to fine-tune
)

print(f"Job ID: {job.id}")
print(f"Status: {job.status}")
```

### Advanced Fine-Tuning Options

```python
job = client.fine_tuning.jobs.create(
    training_file="file-abc123",
    model="gpt-4o-mini",
    
    # Validation file (10-20% of training data size)
    validation_file="file-def456",
    
    # Hyperparameters
    hyperparameters={
        "n_epochs": 3,           # Number of training epochs (auto, 1-10)
        "batch_size": "auto",    # Batch size (auto, 1, 2, 4, 8, 16)
        "learning_rate_multiplier": "auto",  # Learning rate (auto, 0.1-10)
    },
    
    # Post-training options
    suffix="customer-service",   # Identifier for the fine-tuned model
    
    # Integration with other services
    integrations=[
        {
            "type": "slack",
            "slack_config": {
                "channel_id": "your-slack-channel",
                "notify_on": ["completed", "failed"],
            }
        }
    ],
    
    # Metadata for tracking
    metadata={
        "project": "customer-service-bot",
        "version": "1.0",
        "team": "support",
    },
)

print(f"Job ID: {job.id}")
```

### Fine-Tuning for Function Calling

```python
import json

# Create training data with function calls
training_data = [
    {
        "messages": [
            {"role": "user", "content": "What's the weather in San Francisco?"},
            {
                "role": "assistant",
                "function_call": {
                    "name": "get_weather",
                    "arguments': json.dumps({"location": "San Francisco"}),
                },
            },
            {
                "role": "function",
                "name": "get_weather",
                "content": json.dumps({"temperature": 72, "condition": "sunny"}),
            },
            {"role": "assistant", "content": "It's currently 72°F and sunny in San Francisco."},
        ]
    },
]

# Write to file
with open("function_calling_training.jsonl", "w") as f:
    for item in training_data:
        f.write(json.dumps(item) + "\n")

# Upload and fine-tune
file = client.files.create(
    file=open("function_calling_training.jsonl", "rb"),
    purpose="fine-tune",
)

job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-4o-mini",
    suffix="weather-bot",
)
```

## Monitoring Fine-Tuning Jobs

### Checking Job Status

```python
# Retrieve job status
job = client.fine_tuning.jobs.retrieve(fine_tuning_job_id="ftjob-abc123")

print(f"Status: {job.status}")  # running, succeeded, failed, cancelled
print(f"Created at: {job.created_at}")
print(f"Model: {job.model}")
print(f"Fine-tuned model ID: {job.fine_tuned_model}")
print(f"Training files: {job.training_file}")
print(f"Validation files: {job.validation_file}")

# Check progress
if hasattr(job, 'trained_tokens'):
    print(f"Trained tokens: {job.trained_tokens}")
```

### Job Status Values

| Status | Description |
|--------|-------------|
| `pending` | Job is queued |
| `running` | Training in progress |
| `succeeded` | Training completed successfully |
| `failed` | Training failed (check last_error) |
| `cancelled` | Job was cancelled |

### Polling for Completion

```python
import time

def wait_for_finetuning(job_id: str, poll_interval: int = 10) -> str:
    """Wait for fine-tuning job to complete and return model ID."""
    while True:
        job = client.fine_tuning.jobs.retrieve(fine_tuning_job_id=job_id)
        
        print(f"Status: {job.status}", end="\r")
        
        if job.status == "succeeded":
            print(f"\n✓ Fine-tuning complete!")
            print(f"Model ID: {job.fine_tuned_model}")
            return job.fine_tuned_model
        
        elif job.status == "failed":
            print(f"\n✗ Fine-tuning failed!")
            if hasattr(job, 'last_error'):
                print(f"Error: {job.last_error.message}")
            raise Exception(f"Fine-tuning failed: {job.last_error.message}")
        
        elif job.status == "cancelled":
            print(f"\n! Fine-tuning cancelled")
            raise Exception("Fine-tuning was cancelled")
        
        time.sleep(poll_interval)

# Usage
model_id = wait_for_finetuning("ftjob-abc123")
```

### Listing Events

```python
# Get detailed events for a job
events = client.fine_tuning.jobs.list_events(
    fine_tuning_job_id="ftjob-abc123",
    limit=20,  # Number of events to retrieve
)

for event in events:
    print(f"{event.created_at}: {event.message}")
```

### Listing and Cancelling Jobs

```python
# List all fine-tuning jobs
jobs = client.fine_tuning.jobs.list()

for job in jobs:
    print(f"{job.id}: {job.status} - {job.model}")

# Cancel a running job
client.fine_tuning.jobs.cancel(fine_tuning_job_id="ftjob-abc123")
```

## Using Fine-Tuned Models

### Basic Usage

```python
from openai import OpenAI

client = OpenAI()

# Use your fine-tuned model
completion = client.chat.completions.create(
    model="ft:gpt-4o-mini:your-org:customer-service:abc123",
    messages=[
        {"role": "user", "content": "How do I reset my password?"},
    ],
)

print(completion.choices[0].message.content)
```

### Streaming with Fine-Tuned Models

```python
stream = client.chat.completions.create(
    model="ft:gpt-4o-mini:your-org:customer-service:abc123",
    messages=[
        {"role": "user", "content": "What are your hours?"},
    ],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Batch Processing

Process large numbers of requests cost-effectively (up to 50% discount).

### Creating a Batch Job

```python
from openai import OpenAI

client = OpenAI()

# 1. Prepare input file in JSONL format
input_data = [
    {
        "custom_id": "request-1",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": "What is the capital of France?"}
            ],
            "max_tokens": 100,
        },
    },
    {
        "custom_id": "request-2",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": "Explain photosynthesis"}
            ],
            "max_tokens": 200,
        },
    },
]

# Write to file
with open("batch_input.jsonl", "w") as f:
    for item in input_data:
        f.write(json.dumps(item) + "\n")

# 2. Upload the input file
input_file = client.files.create(
    file=open("batch_input.jsonl", "rb"),
    purpose="batch",
)

# 3. Create the batch job
batch = client.batches.create(
    input_file_id=input_file.id,
    endpoint="/v1/chat/completions",  # or /v1/responses
    completion_window="24h",  # Maximum time for processing (24h)
    
    # Optional: Send notifications on completion
    metadata={
        "job_name": "Weekly content generation",
    },
)

print(f"Batch ID: {batch.id}")
print(f"Status: {batch.status}")
```

### Batch Endpoint Options

| Endpoint | Use Case |
|----------|----------|
| `/v1/chat/completions` | Chat Completions API |
| `/v1/responses` | Responses API |
| `/v1/embeddings` | Embedding generation |

### Monitoring Batch Jobs

```python
# Retrieve batch status
batch = client.batches.retrieve(batch_id="batch_abc123")

print(f"Status: {batch.status}")  # validing, in_progress, completed, failed, cancelling, cancelled
print(f"Created at: {batch.created_at}")

# Check progress
if hasattr(batch, 'request_counts'):
    counts = batch.request_counts
    print(f"Total: {counts.total}")
    print(f"Completed: {counts.completed}")
    print(f"Failed: {counts.failed}")
```

### Batch Status Values

| Status | Description |
|--------|-------------|
| `validating` | Validating input file |
| `in_progress` | Processing requests |
| `completed` | All requests processed |
| `failed` | Batch processing failed |
| `cancelling` | Cancellation in progress |
| `cancelled` | Batch was cancelled |

### Cancelling a Batch

```python
# Cancel a batch job
client.batches.cancel(batch_id="batch_abc123")
```

### Retrieving Results

```python
# 1. Check if batch is complete
batch = client.batches.retrieve(batch_id="batch_abc123")

if batch.status == "completed":
    # 2. Get results file ID
    results_file_id = batch.output_file_id
    
    # 3. Retrieve the results file
    response = client.files.content(file_id=results_file_id)
    
    # 4. Parse results
    results = response.content.decode("utf-8")
    for line in results.split("\n"):
        if line:
            result = json.loads(line)
            print(f"Request {result['custom_id']}:")
            print(f"  Status: {result['response']['status_code']}")
            print(f"  Body: {result['response']['body']}")
```

### Batch Result Format

Each line in the results file:

```json
{
    "custom_id": "request-1",
    "response": {
        "id": "req_abc123",
        "status_code": 200,
        "request_id": "req_xyz789",
        "body": {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "The capital of France is Paris."
                    }
                }
            ]
        }
    },
    "error": null  // Populated if request failed
}
```

## Listing and Managing Files

```python
# List all files
files = client.files.list()

for file in files:
    print(f"{file.id}: {file.filename} - {file.purpose}")

# Retrieve file details
file = client.files.retrieve(file_id="file-abc123")
print(f"Filename: {file.filename}")
print(f"Purpose: {file.purpose}")
print(f"Bytes: {file.bytes}")

# Delete a file
client.files.delete(file_id="file-abc123")
```

## Best Practices

### Fine-Tuning

1. **Start small:** 100-500 examples often sufficient
2. **Quality over quantity:** Better examples beat more examples
3. **Use validation data:** Prevents overfitting
4. **Monitor training:** Check events for issues
5. **Test thoroughly:** Evaluate before production use
6. **Iterate:** Improve training data based on results

### Batch Processing

1. **Use for non-urgent tasks:** Up to 24h processing time
2. **Include custom_id:** Essential for matching results
3. **Validate input format:** Check JSONL before uploading
4. **Monitor progress:** Check request_counts for status
5. **Handle failures:** Some requests may fail, check error field
6. **Cost optimization:** Batch is cheaper but slower than real-time
