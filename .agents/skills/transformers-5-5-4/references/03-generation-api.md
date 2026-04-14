# Generation API - Complete Guide

Comprehensive guide to text generation with LLMs and VLMs in Transformers 5.5.4, covering decoding strategies, streaming, and advanced features.

## Overview

The generation API provides fast, flexible text generation for large language models (LLMs) and vision-language models (VLMs). It supports multiple decoding strategies, streaming output, and advanced features like guided generation and assisted decoding.

## Basic Generation

### Using Pipeline

```python
from transformers import pipeline

# Simplest approach
generator = pipeline("text-generation", model="gpt2")
result = generator("Once upon a time", max_length=50)

# With modern LLMs
generator = pipeline(
    "text-generation",
    model="meta-llama/Llama-3.1-8b",
    tokenizer_kwargs={"padding_side": "left"}
)

result = generator(
    "Explain quantum computing:",
    max_new_tokens=100,
    temperature=0.7,
    top_p=0.9
)
```

### Using Model Directly

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8b")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8b")

# Prepare input
prompt = "Explain machine learning in simple terms:"
inputs = tokenizer(prompt, return_tensors="pt")

# Generate
outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    temperature=0.7,
    top_p=0.9,
    do_sample=True
)

# Decode
generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(generated_text)
```

## Decoding Strategies

### Greedy Search (Default)

Deterministic, always picks highest probability token:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

inputs = tokenizer("The weather", return_tensors="pt")

# Greedy search (default)
outputs = model.generate(
    **inputs,
    max_new_tokens=20
)

# Always produces same output for same input
text = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### Beam Search

Explores multiple hypotheses, better quality but slower:

```python
outputs = model.generate(
    **inputs,
    max_new_tokens=20,
    num_beams=5,           # Number of beams
    early_stopping=True,   # Stop when all beams finished
    num_return_sequences=3 # Return top 3 results
)

# Decode multiple results
for i, output in enumerate(outputs):
    print(f"Beam {i}: {tokenizer.decode(output, skip_special_tokens=True)}")
```

### Sampling with Temperature

Adds randomness for more diverse outputs:

```python
outputs = model.generate(
    **inputs,
    max_new_tokens=20,
    do_sample=True,              # Enable sampling
    temperature=0.7              # Lower = more deterministic
)

# Temperature effects:
# 0.2 - Very deterministic, safe outputs
# 0.7 - Balanced creativity and coherence (recommended)
# 1.0 - Pure model probabilities
# 1.5+ - Very creative, potentially incoherent
```

### Top-K Sampling

Samples from top K most likely tokens:

```python
outputs = model.generate(
    **inputs,
    max_new_tokens=20,
    do_sample=True,
    top_k=50  # Sample from top 50 tokens
)

# Good for balancing diversity and quality
```

### Top-P (Nucleus) Sampling

Samples from smallest set of tokens with cumulative probability > p:

```python
outputs = model.generate(
    **inputs,
    max_new_tokens=20,
    do_sample=True,
    top_p=0.9  # Sample from top 90% probability mass
)

# Adaptive - considers more tokens when distribution is flat
```

### Combined Sampling (Recommended)

```python
outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    top_k=50
)

# Best of all: temperature for scaling, top_p for adaptivity, top_k as safety
```

### Repetition Penalty

Discourages repetitive generation:

```python
outputs = model.generate(
    **inputs,
    max_new_tokens=50,
    repetition_penalty=1.2  # >1.0 penalizes repetition
)

# Typical values:
# 1.0 - No penalty (default)
# 1.1-1.3 - Mild penalty (recommended)
# 1.5+ - Strong penalty (may affect coherence)
```

## Streaming Generation

### Token-by-Token Streaming

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.streamers import TextStreamer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8b")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8b")

# Create streamer
streamer = TextStreamer(tokenizer, skip_prompt=True)

# Generate with streaming
inputs = tokenizer("Explain photosynthesis:", return_tensors="pt")
outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    streamer=streamer  # Tokens printed as they're generated
)
```

### Custom Streamer

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.streamers import BaseStreamer
import threading

class CustomStreamer(BaseStreamer):
    def __init__(self, tokenizer, timeout=None):
        super().__init__(tokenizer, timeout=timeout)
        self.full_text = ""
    
    def on_finalized_text(self, word, stream_end=False):
        self.full_text += word
        print(f"Generated: {word}", end="", flush=True)
        if stream_end:
            print("\n--- Generation complete ---")

# Usage
streamer = CustomStreamer(tokenizer)
outputs = model.generate(**inputs, streamer=streamer)
```

### Pipeline Streaming

```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

# Stream tokens
for token in generator(
    "Once upon a time",
    max_new_tokens=50,
    stream=True
):
    print(token["generated_text"], end="", flush=True)
```

## Advanced Generation Features

### Chat Templating

Modern models support chat templates for conversational AI:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8b")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8b")

# Define conversation
messages = [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "Write a Python function to sort a list"},
]

# Apply chat template
chat_input = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

# Generate response
inputs = tokenizer(chat_input, return_tensors="pt")
outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    temperature=0.7,
    top_p=0.9
)

# Decode response (exclude prompt)
response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
print(response)
```

### Continue Conversation

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is quantum computing?"},
    {"role": "assistant", "content": "Quantum computing uses quantum mechanics..."},
    {"role": "user", "content": "How does it differ from classical computing?"}
]

chat_input = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(chat_input, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=200)
```

### Assisted Decoding (Speculative Decoding)

Use a smaller model to accelerate generation:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load teacher (large) and assistant (small) models
teacher_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8b")
assistant_model = AutoModelForCausalLM.from_pretrained("microsoft/Phi-3-mini-4k-instruct")

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8b")

inputs = tokenizer("Explain machine learning:", return_tensors="pt")

# Generate with assisted decoding
outputs = teacher_model.generate(
    **inputs,
    assistant_model=assistant_model,  # Smaller model assists
    max_new_tokens=100
)

# Can be 2-3x faster than standard generation
```

### Constrained Generation

Generate text matching a specific pattern:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import HFRegexGenerator

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Generate valid JSON
regex = r'\{\s*"name"\s*:\s*"[^"]+"\s*\}'  # Simple JSON pattern
generator = HFRegexGenerator(regex, tokenizer)

inputs = tokenizer("Generate JSON: ", return_tensors="pt")
outputs = model.generate(
    **inputs,
    max_new_tokens=50,
    constrained_beams_decoder=generator
)

text = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### Grammar-Guided Generation

Use CFG (Context-Free Grammar) for structured output:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from lark import Lark
from transformers.generation import EpsilonConstraint, CFGLogitsProcessor

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Define grammar
grammar = Lark(r"""
    start: NUMBER operation NUMBER
    NUMBER: /\d+/
    operation: "+" | "-" | "*" | "/"
    %import common.WS
    %ignore WS
""")

# Create constraint
epsilon_constraint = EpsilonConstraint(grammar, tokenizer)

inputs = tokenizer("Math expression: 5", return_tensors="pt")
outputs = model.generate(
    **inputs,
    max_new_tokens=20,
    logits_processor=[CFGLogitsProcessor(grammar, tokenizer)]
)

text = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## Generation Parameters Reference

### Length Control

```python
# Maximum total tokens (prompt + generation)
max_length=1024

# Maximum NEW tokens (excluding prompt) - RECOMMENDED
max_new_tokens=100

# Minimum total tokens
min_length=50

# Minimum NEW tokens
min_new_tokens=10

# Stop at specific token
eos_token_id=tokenizer.eos_token_id

# Multiple stop tokens
bad_words_ids=[
    tokenizer("BAD_WORD", add_special_tokens=False).input_ids
]
```

### Diversity Control

```python
# Beam search diversity
num_beams=5              # Number of beams
num_beam_groups=3        # Group beams for diversity
diversity_penalty=0.2    # Penalty for repetitive tokens across beams

# Sampling diversity
do_sample=True           # Enable sampling
temperature=0.7          # Temperature scaling
top_k=50                 # Top-k filtering
top_p=0.9                # Nucleus sampling
typical_p=0.9            # Typical sampling (less common)

# Repetition control
repetition_penalty=1.2   # Penalize repeated tokens
encoder_repetition_penalty=1.0  # For encoder-decoder models
```

### Early Stopping

```python
# Beam search stopping criteria
early_stopping=True      # Stop when all beams finished
early_stopping="weak"    # Weak early stopping (continue if diversity)

# Maximum time
max_time=60.0            # Maximum generation time in seconds
```

### Output Control

```python
# Number of sequences to return
num_return_sequences=1   # For greedy/beam search
num_return_sequences=5   # For sampling (must have do_sample=True)

# Output format
output_scores=True       # Return token scores
return_dict_in_generate=True  # Return rich dict output

# Get full output
outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    output_scores=True,
    return_dict_in_generate=True
)

print(outputs.sequences)      # Token IDs
print(outputs.scores)         # Logits per position
```

## Batch Generation

### Basic Batching

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Tokenize multiple prompts
prompts = [
    "The weather today is",
    "I enjoy programming because",
    "My favorite food is"
]

inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True)

# Generate for all prompts
outputs = model.generate(
    **inputs,
    max_new_tokens=20,
    pad_token_id=tokenizer.eos_token_id  # Important for padded inputs
)

# Decode results
for i, output in enumerate(outputs):
    print(f"Prompt {i}: {tokenizer.decode(output, skip_special_tokens=True)}")
```

### Parallel Generation

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from concurrent.futures import ThreadPoolExecutor

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

def generate_for_prompt(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=20)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

prompts = ["Prompt 1", "Prompt 2", "Prompt 3", "Prompt 4"]

# Parallel generation (CPU-bound tokenization, GPU-bound generation)
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(generate_for_prompt, prompts))
```

## Performance Optimization

### Model Compilation (PyTorch 2.0+)

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8b")

# Compile model for faster generation
model = model.compile(
    mode="reduce-overhead",  # or "max-autotune"
    fullgraph=True
)

# First generation will be slow (compilation), subsequent ones are fast
outputs = model.generate(**inputs, max_new_tokens=100)
```

### Flash Attention

```python
from transformers import AutoModelForCausalLM

# Load with Flash Attention 2
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    attn_implementation="flash_attention_2",  # Requires FlashAttention installed
    torch_dtype=torch.float16,
    device_map="auto"
)

# 20-40% faster generation, especially for long sequences
```

### Quantization for Generation

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    quantization_config=quantization_config,
    device_map="auto"
)

# 75% less memory, minimal quality loss
```

## Common Use Cases

### Code Generation

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("microsoft/phi-3-mini-4k-instruct")
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-3-mini-4k-instruct")

messages = [
    {"role": "system", "content": "You are a Python coding assistant."},
    {"role": "user", "content": """Write a function to find the longest common subsequence between two strings. Include type hints and docstring."""}
]

chat_input = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(chat_input, return_tensors="pt")

outputs = model.generate(
    **inputs,
    max_new_tokens=500,
    temperature=0.3,  # Lower for code (more deterministic)
    top_p=0.9
)

response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
print(response)
```

### Creative Writing

```python
from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="mistralai/Mistral-7B-v0.1",
    device=0
)

result = generator(
    "Write a short science fiction story about first contact:",
    max_new_tokens=300,
    temperature=1.2,      # Higher for creativity
    top_p=0.95,
    repetition_penalty=1.1
)

print(result[0]["generated_text"])
```

### Data Extraction

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8b")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8b")

messages = [
    {"role": "system", "content": "Extract entities in JSON format."},
    {"role": "user", "content": """Extract name, email, and phone from: "Hello, my name is John Doe. Contact me at john@example.com or 555-1234."""}
]

chat_input = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(chat_input, return_tensors="pt")

outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    temperature=0.1  # Very deterministic for extraction
)

response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
print(response)
```

## Troubleshooting

### Repetitive Generation

```python
# Increase repetition penalty
outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    repetition_penalty=1.3,
    temperature=0.7
)

# Or use beam search
outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    num_beams=5,
    early_stopping=True
)
```

### Generation Too Short

```python
# Ensure eos_token is set correctly
tokenizer.eos_token = "</s>"  # Set correct EOS token

# Increase max_new_tokens
outputs = model.generate(
    **inputs,
    max_new_tokens=500,  # Increase limit
    pad_token_id=tokenizer.eos_token_id
)
```

### Slow Generation

```python
# Use Flash Attention
model = AutoModelForCausalLM.from_pretrained(
    "model-name",
    attn_implementation="flash_attention_2"
)

# Compile model
model = model.compile()

# Use quantization
quantization_config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained(
    "model-name",
    quantization_config=quantization_config,
    device_map="auto"
)
```

## Best Practices

1. **Use `max_new_tokens`** instead of `max_length` for clearer control
2. **Set `pad_token_id`** when batching padded inputs
3. **Use temperature 0.7, top_p 0.9** as starting point for general tasks
4. **Lower temperature (0.1-0.3)** for factual/code tasks
5. **Higher temperature (1.0-1.2)** for creative writing
6. **Enable Flash Attention** for long sequences
7. **Compile model** with PyTorch 2.0+ for 10-30% speedup
8. **Use streaming** for interactive applications
