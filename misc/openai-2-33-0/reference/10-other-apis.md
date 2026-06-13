# Other APIs

## Moderations

Check content for policy violations:

```python
from openai import OpenAI

client = OpenAI()

moderation = client.moderations.create(
    model="omni-moderation-latest",
    input="Text to check for policy violations.",
)

result = moderation.results[0]
print(result.flagged)
print(result.categories)  # which categories were flagged
```

### Multimodal Moderation

```python
moderation = client.moderations.create(
    model="omni-moderation-latest",
    input=[
        {"type": "text", "text": "Some text to moderate."},
        {"type": "image_url", "image_url": "https://example.com/image.jpg"},
    ],
)
```

## Models

List and retrieve available models:

```python
# List all models
models = client.models.list()
for model in models:
    print(model.id, model.owned_by)

# Retrieve model details
model = client.models.retrieve("gpt-4o-mini")
print(model.id)
print(model.owned_by)
```

## Completions (Legacy)

The legacy completions API for GPT-3.5 models:

```python
completion = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="Write a tagline for an ice cream shop.",
    max_tokens=50,
    temperature=0.7,
)
print(completion.choices[0].text)
```

## Webhooks

Verify and unwrap webhook events:

```python
from openai import OpenAI

client = OpenAI()

# Verify signature
client.webhooks.verify_signature(
    payload=request_body,
    headers=request_headers,
    secret=webhook_secret,
    tolerance=180,  # seconds
)

# Unwrap event
event = client.webhooks.unwrap(
    payload=request_body,
    headers=request_headers,
    secret=webhook_secret,
)

# Process by type
if event.type == "fine_tuning.job.succeeded":
    print(event.data.id)
```

## Evals

Create and manage evaluation configurations:

```python
# Create eval
eval = client.evals.create(
    name="My Evaluation",
    config={
        # eval configuration
    },
)

# Run eval
run = client.evals.runs.create(
    eval_id=eval.id,
    data_source={
        "type": "jsonl",
        "file_id": "file-abc123",
    },
)

# List runs
runs = client.evals.runs.list(eval_id=eval.id)

# Cancel run
cancelled = client.evals.runs.cancel(run_id=run.id, eval_id=eval.id)

# Get output items
items = client.evals.runs.output_items.list(
    run_id=run.id,
    eval_id=eval.id,
)
```

## Skills

Manage reusable skill definitions:

```python
# Create a skill
skill = client.skills.create(
    name="My Skill",
    # skill configuration
)

# List skills
skills = client.skills.list()

# Update skill
updated = client.skills.update(skill.id, name="Updated Name")

# Delete skill
deleted = client.skills.delete(skill.id)

# Manage versions
version = client.skills.versions.create(
    skill_id=skill.id,
    # version config
)

versions = client.skills.versions.list(skill_id=skill.id)
```

## Videos

Generate and manage AI-generated videos:

```python
# Create video
video = client.videos.create(
    model="model-name",
    prompt="A cinematic shot of a rocket launching",
    # other params
)

# Poll for completion
video = client.videos.create_and_poll(
    model="model-name",
    prompt="A cinematic shot of a rocket launching",
)

# List videos
videos = client.videos.list()

# Download content
content = client.videos.download_content(video.id)

# Create character
character = client.videos.create_character(
    # character params
)

# Edit video
edited = client.videos.edit(
    # edit params
)

# Extend video
extended = client.videos.extend(video_id=video.id)

# Remix video
remixed = client.videos.remix(video_id=video.id)
```

## Containers

Manage container environments:

```python
# Create container
container = client.containers.create(
    # container config
)

# List containers
containers = client.containers.list()

# Manage files in containers
file = client.containers.files.create(
    container_id=container.id,
    # file params
)

files = client.containers.files.list(container_id=container.id)

# Get file content
content = client.containers.files.content.retrieve(
    file_id=file.id,
    container_id=container.id,
)
```

## Conversations

Manage conversation state:

```python
# Access via client.conversations
# Operations for managing conversation history and state
```

## Graders (Fine-Tuning Alpha)

Validate and run graders for fine-tuning data:

```python
# Validate grader
result = client.fine_tuning.alpha.graders.validate(
    # validation params
)

# Run grader
result = client.fine_tuning.alpha.graders.run(
    # run params
)
```

## Module-Level Client

The SDK provides a module-level client for convenience:

```python
import openai

openai.api_key = "sk-..."
openai.organization = "org-xyz"
openai.project = "proj-abc"

response = openai.responses.create(
    model="gpt-5.2",
    input="Hello!",
)
```

## Custom HTTP Client

Pass a custom httpx client for advanced configuration:

```python
import httpx
from openai import OpenAI, DefaultHttpxClient

# Using DefaultHttpxClient retains default limits/timeout
client = OpenAI(
    http_client=DefaultHttpxClient(
        headers={"Custom-Header": "value"},
    ),
)

# Or full custom httpx client
limits = httpx.Limits(max_connections=100)
transport = httpx.HTTPTransport(retries=2)
client = OpenAI(
    http_client=httpx.Client(
        limits=limits,
        transport=transport,
    ),
)
```

## Logging

The SDK uses Python's standard logging module:

```python
import logging
import openai

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
```

Sensitive headers are automatically filtered from logs.
