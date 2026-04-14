# Models and Tokenizers - Complete Guide

This reference covers model loading, tokenizer patterns, auto classes, and configuration management in Transformers 5.5.4.

## Model Loading Fundamentals

### Auto Classes

Auto classes automatically detect the model type from a pretrained checkpoint:

```python
from transformers import (
    AutoModel,
    AutoModelForSequenceClassification,
    AutoModelForCausalLM,
    AutoTokenizer
)

# Load base model
model = AutoModel.from_pretrained("bert-base-uncased")

# Load for specific task
classifier = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)

# Load generative model
generator = AutoModelForCausalLM.from_pretrained("gpt2")
```

### Loading with Configuration

```python
from transformers import AutoConfig, AutoModel

# Load configuration first
config = AutoConfig.from_pretrained(
    "bert-base-uncased",
    num_labels=3,  # Override number of labels
    output_attentions=True
)

# Load model with custom config
model = AutoModel.from_pretrained(
    "bert-base-uncased",
    config=config
)

# Or pass kwargs directly
model = AutoModel.from_pretrained(
    "bert-base-uncased",
    num_hidden_layers=4,  # Use smaller model
    torch_dtype=torch.float16  # Load in FP16
)
```

### Loading from Local Directory

```python
from transformers import AutoModel, AutoTokenizer

# Save model locally first
model.save_pretrained("./my-model")
tokenizer.save_pretrained("./my-model")

# Load from local path
model = AutoModel.from_pretrained("./my-model")
tokenizer = AutoTokenizer.from_pretrained("./my-model")

# Offline mode (no network calls)
model = AutoModel.from_pretrained(
    "./my-model",
    local_files_only=True
)
```

### Loading with Authentication

```python
from transformers import AutoModel, HfFolder

# Login via CLI first: huggingface-cli login
# Or set environment variable
import os
os.environ["HUGGING_FACE_HUB_TOKEN"] = "your_token"

# Load gated model
model = AutoModel.from_pretrained("meta-llama/Llama-3.1-8b")

# Or pass token directly
from huggingface_hub import login
login(token="your_token")
model = AutoModel.from_pretrained("meta-llama/Llama-3.1-8b")
```

## Tokenizer Patterns

### Basic Tokenization

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Single text
encoding = tokenizer("Hello, how are you?")
# {'input_ids': [101, 7592, 1010, ...], 'attention_mask': [1, 1, 1, ...]}

# With special tokens (default for most models)
encoding = tokenizer(
    "Hello, how are you?",
    add_special_tokens=True  # Adds [CLS] and [SEP] for BERT
)

# Without special tokens
encoding = tokenizer(
    "Hello, how are you?",
    add_special_tokens=False
)
```

### Padding and Truncation

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Pad to max length
encoding = tokenizer(
    "Short text",
    padding="max_length",
    max_length=128,
    truncation=True
)

# Pad to longest in batch
encodings = tokenizer(
    ["Short", "This is a longer text that needs more tokens"],
    padding=True,  # Automatically pads to longest
    truncation=True,
    max_length=128
)

# Different padding sides
tokenizer = AutoTokenizer.from_pretrained(
    "gpt2",
    padding_side="left"  # GPT models typically pad on left for generation
)
```

### Return Tensors

```python
from transformers import AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Return PyTorch tensors
encoding = tokenizer(
    "Hello, world!",
    return_tensors="pt"  # Returns dict of tensors
)
# {'input_ids': tensor([[101, 7592, ...]]), 'attention_mask': tensor([[1, 1, ...]])}

# Return NumPy arrays
encoding = tokenizer("Hello, world!", return_tensors="np")

# Return TensorFlow tensors
encoding = tokenizer("Hello, world!", return_tensors="tf")
```

### Batch Tokenization

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Tokenize multiple texts
texts = [
    "First sentence",
    "Second sentence with more words",
    "Third"
]

encodings = tokenizer(
    texts,
    padding=True,
    truncation=True,
    max_length=128,
    return_tensors="pt"
)

print(encodings["input_ids"].shape)  # torch.Size([3, 128])
```

### Tokenization for Generation

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Prepare prompt for generation
prompt = "Once upon a time"
inputs = tokenizer(
    prompt,
    return_tensors="pt",
    padding_side="left",  # Important for generation
    truncation=True,
    max_length=1024
)

# Generate and decode
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("gpt2")

outputs = model.generate(
    **inputs,
    max_new_tokens=50,
    pad_token_id=tokenizer.eos_token_id
)

generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### Special Tokens

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Access special tokens
print(tokenizer.cls_token)    # '[CLS]'
print(tokenizer.sep_token)    # '[SEP]'
print(tokenizer.pad_token)    # '[PAD]'
print(tokenizer.unk_token)    # '[UNK]'

# Add custom special tokens
num_added = tokenizer.add_special_tokens({
    "additional_special_tokens": ["<custom>", "<another>"]
})

# Update model embeddings to match
model.resize_token_embeddings(len(tokenizer))

# Tokenize with custom tokens
encoding = tokenizer("This is <custom> text", add_special_tokens=True)
```

### Chat Templating

Modern models support chat templating for conversational AI:

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8b")

# Define conversation
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is quantum computing?"},
    {"role": "assistant", "content": "Quantum computing uses quantum mechanics..."},
    {"role": "user", "content": "How does it differ from classical computing?"}
]

# Apply chat template
chat_input = tokenizer.apply_chat_template(
    messages,
    tokenize=False,  # Returns string
    add_generation_prompt=True  # Add assistant prompt for generation
)

# Tokenize for model
inputs = tokenizer(
    chat_input,
    return_tensors="pt",
    truncation=True,
    max_length=2048
)
```

### Multimodal Tokenization

For vision-language models:

```python
from transformers import AutoProcessor

processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-large")

from PIL import Image
image = Image.open("image.jpg")

# Process both text and image
inputs = processor(
    images=image,
    text="Describe this image",
    return_tensors="pt",
    padding=True
)

# Contains both image and text encodings
print(inputs.keys())  # dict_keys(['pixel_values', 'input_ids', 'attention_mask'])
```

## Model Configuration

### Inspecting Configuration

```python
from transformers import AutoConfig

config = AutoConfig.from_pretrained("bert-base-uncased")

# Access configuration attributes
print(config.vocab_size)        # 30522
print(config.hidden_size)       # 768
print(config.num_hidden_layers) # 12
print(config.num_attention_heads) # 12

# Convert to dictionary
config_dict = config.to_dict()

# Save configuration
config.save_pretrained("./my-config")
```

### Modifying Configuration

```python
from transformers import AutoConfig, AutoModel

# Load and modify config
config = AutoConfig.from_pretrained("bert-base-uncased")
config.num_labels = 5  # Change number of labels
config.output_attentions = True

# Create model with modified config
model = AutoModel.from_pretrained(
    "bert-base-uncased",
    config=config
)

# Or pass kwargs directly
model = AutoModel.from_pretrained(
    "bert-base-uncased",
    num_labels=5,
    output_attentions=True,
    attention_dropout=0.1
)
```

### Configuration for Different Tasks

```python
from transformers import AutoConfig

# Sequence classification config
config = AutoConfig.from_pretrained(
    "bert-base-uncased",
    problem_type="single_label_classification",
    num_labels=3
)

# Token classification config
config = AutoConfig.from_pretrained(
    "bert-base-uncased",
    problem_type="token_classification",
    num_labels=9  # B-I-O tags
)

# Question answering config
config = AutoConfig.from_pretrained(
    "bert-base-uncased",
    problem_type="question_answering"
)
```

## Model Saving and Sharing

### Saving Locally

```python
from transformers import AutoModel, AutoTokenizer

# Load model and tokenizer
model = AutoModel.from_pretrained("bert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Save to local directory
model.save_pretrained("./my-saved-model")
tokenizer.save_pretrained("./my-saved-model")

# Also save config explicitly if modified
model.config.save_pretrained("./my-saved-model")
```

### Pushing to Hub

```python
from transformers import AutoModel, AutoTokenizer
import os

# Set your token
os.environ["HUGGING_FACE_HUB_TOKEN"] = "your_token"

# Or login via CLI: huggingface-cli login

# Load and fine-tune your model
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Push to Hub
model.push_to_hub("username/my-custom-model")
tokenizer.push_to_hub("username/my-custom-model")

# With additional metadata
model.push_to_hub(
    "username/my-custom-model",
    private=True,  # Keep model private
    commit_message="Initial version of custom model"
)
```

### Saving with Safe Tensors

```python
from transformers import AutoModel

model = AutoModel.from_pretrained("bert-base-uncased")

# Save in safe_tensors format (more secure, no Python pickling)
model.save_pretrained(
    "./my-model",
    safe_serialization=True  # Saves as model.safetensors
)

# Load from safe_tensors (automatic detection)
model = AutoModel.from_pretrained("./my-model")
```

## Device Management

### CPU and GPU

```python
import torch
from transformers import AutoModel

# Check available devices
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")

# Load on CPU (default)
model = AutoModel.from_pretrained("bert-base-uncased")

# Move to GPU
if torch.cuda.is_available():
    model = model.to("cuda")  # or model.cuda()

# Specific GPU
model = model.to("cuda:1")

# Keep track of device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
```

### Multi-GPU with Device Map

```python
from transformers import AutoModelForCausalLM

# Automatic device mapping
model = AutoModelForCausalLM.from_pretrained(
    "large-model",
    device_map="auto"  # Automatically distributes across GPUs
)

# Manual device mapping
model = AutoModelForCausalLM.from_pretrained(
    "large-model",
    device_map={
        0: ["model.embed_tokens", "model.layers.0"],
        1: ["model.layers.1", "model.layers.2"],
        # ... etc
    }
)

# Sequential mapping (one layer at a time for memory efficiency)
model = AutoModelForCausalLM.from_pretrained(
    "very-large-model",
    device_map="sequential"
)
```

### Mixed Precision

```python
import torch
from transformers import AutoModel

# Load in FP16
model = AutoModel.from_pretrained(
    "bert-base-uncased",
    torch_dtype=torch.float16
)

# Load in BF16 (requires Ampere+ GPUs)
model = AutoModel.from_pretrained(
    "bert-base-uncased",
    torch_dtype=torch.bfloat16
)

# Move to device with dtype
model = model.to(device="cuda", dtype=torch.float16)
```

## Model Quantization

### 8-bit Quantization

```python
from transformers import AutoModelForCausalLM

# Load in 8-bit (requires bitsandbytes)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    load_in_8bit=True,
    device_map="auto"
)

# Reduces memory usage by ~50%
```

### 4-bit Quantization

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# Load with 4-bit quantization
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    quantization_config=quantization_config,
    device_map="auto",
    torch_dtype=torch.float16
)

# Reduces memory usage by ~75%
```

## Model Inspection and Debugging

### Inspecting Model Architecture

```python
from transformers import AutoModel

model = AutoModel.from_pretrained("bert-base-uncased")

# Print model architecture
print(model)

# Get number of parameters
num_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {num_params:,}")

# Get trainable parameters
num_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Trainable parameters: {num_trainable:,}")

# Inspect specific layers
print(model.encoder.layer[0])  # First transformer layer
```

### Model Weights

```python
from transformers import AutoModel

model = AutoModel.from_pretrained("bert-base-uncased")

# Access state dict
state_dict = model.state_dict()
print(state_dict.keys())

# Get specific weights
embeddings = model.embeddings.word_embeddings.weight
print(embeddings.shape)  # torch.Size([30522, 768])

# Save state dict
torch.save(model.state_dict(), "model_weights.pt")

# Load state dict
model.load_state_dict(torch.load("model_weights.pt"))
```

### Gradient Checking

```python
from transformers import AutoModelForSequenceClassification
import torch

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
model.train()

inputs = tokenizer("Hello, world!", return_tensors="pt")
outputs = model(**inputs)
loss = outputs.loss

# Backpropagate
loss.backward()

# Check gradients
for name, param in model.named_parameters():
    if param.grad is not None:
        print(f"{name}: grad norm = {param.grad.norm().item():.4f}")
```

## Common Model Types

### Auto Model Mappings

```python
from transformers import (
    # Base models
    AutoModel,              # BERTBase, RoBERTaBase, etc.
    
    # Sequence classification
    AutoModelForSequenceClassification,
    
    # Token classification (NER, POS tagging)
    AutoModelForTokenClassification,
    
    # Question answering
    AutoModelForQuestionAnswering,
    
    # Language modeling (causal/next token prediction)
    AutoModelForCausalLM,   # GPT, Llama, etc.
    
    # Language modeling (masked)
    AutoModelForMaskedLM,   # BERT, RoBERTa
    
    # Sequence-to-sequence (encoder-decoder)
    AutoModelForSeq2SeqLM,  # T5, BART
    
    # Image classification
    AutoModelForImageClassification,
    
    # Object detection
    AutoModelForObjectDetection,
    
    # And many more...
)
```

### Task-Specific Loading Examples

```python
from transformers import (
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoModelForQuestionAnswering,
    AutoModelForCausalLM,
    AutoTokenizer
)

# Sentiment analysis
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)

# Named entity recognition
model = AutoModelForTokenClassification.from_pretrained(
    "dbmdz/bert-large-cased-finetuned-conll03-english"
)

# Question answering
model = AutoModelForQuestionAnswering.from_pretrained(
    "deepset/roberta-base-squad2"
)

# Text generation
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8b")
```

## Best Practices

1. **Use Auto classes** for automatic model type detection
2. **Cache models locally** to avoid re-downloading
3. **Set `local_files_only=True`** for production/offline deployments
4. **Use appropriate dtype** (FP16/BF16) for GPU memory efficiency
5. **Enable quantization** for large models on limited hardware
6. **Save tokenizers with models** to ensure consistent preprocessing
7. **Use `device_map="auto"`** for multi-GPU setups
8. **Check model card** for specific loading requirements

## Troubleshooting

### Model Loading Errors

```python
# Fix: Update transformers library
# pip install --upgrade transformers

# Fix: Clear cache if corrupted
from huggingface_hub import scan_cache_dir
cache_info = scan_cache_dir()
# Then manually remove problematic cache entries
```

### Tokenizer Mismatch

```python
# Always load tokenizer with matching model
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Resize embeddings if you added tokens to tokenizer
model.resize_token_embeddings(len(tokenizer))
```

### Memory Issues

```python
# Use quantization for large models
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained(
    "large-model",
    quantization_config=quantization_config,
    device_map="auto"
)
```
