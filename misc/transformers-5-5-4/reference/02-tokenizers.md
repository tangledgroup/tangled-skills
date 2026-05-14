# Tokenizers and Preprocessors

## Loading Tokenizers

Use `AutoTokenizer` to automatically resolve the correct tokenizer class:

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b")
```

Most tokenizers resolve to `TokenizersBackend`, a fast Rust-based implementation from the [Tokenizers](https://huggingface.co/docs/tokenizers) library. Python-only implementations are available via `PreTrainedTokenizer`.

## Encoding and Decoding

### Encode

```python
tokenizer("Sphinx of black quartz, judge my vow.", return_tensors="pt")
# {
#     'input_ids': tensor([[2, 235277, 82913, 576, 2656, ...]]),
#     'attention_mask': tensor([[1, 1, 1, 1, 1, 1, ...]])
# }
```

Key parameters:

- `return_tensors="pt"` — Return PyTorch tensors
- `padding=True` or `"max_length"` — Pad to longest or max length
- `truncation=True, max_length=512` — Truncate long sequences
- `add_special_tokens=False` — Skip automatic special token insertion

### Decode

```python
tokenizer.decode(output_ids, skip_special_tokens=True)
tokenizer.batch_decode(output_ids, skip_special_tokens=True)
```

## Batch Processing

Tokenize multiple sequences at once for better throughput:

```python
tokenizer(
    ["First sentence.", "Second sentence."],
    padding=True,
    truncation=True,
    max_length=128,
    return_tensors="pt"
)
```

The Rust-based backend parallelizes batch tokenization across threads, providing significant speedups over Python implementations.

## Special Tokens

Each model defines its own special tokens (BOS, EOS, PAD, MASK). The tokenizer adds them automatically during encoding.

Register additional named special tokens:

```python
tokenizer = AutoTokenizer.from_pretrained(
    "llava-hf/llava-1.5-7b-hf",
    extra_special_tokens={
        "image_token": "<image>",
        "boi_token": "<image_start>",
        "eoi_token": "<image_end>"
    }
)
print(tokenizer.image_token, tokenizer.image_token_id)  # ("<image>", 32000)
```

## Padding Side for Generation

For LLM generation, set `padding_side="left"` because models are not trained to continue from padding tokens:

```python
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1", padding_side="left")
tokenizer.pad_token = tokenizer.eos_token
```

## Chat Templates

Chat templates convert message lists into properly formatted token sequences with the correct control tokens for each model:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is quantum computing?"},
]

# Get formatted text (not tokenized)
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# Get tokenized output
tokenized = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt"
)
```

### Key Parameters

- `add_generation_prompt=True` — Adds tokens indicating the assistant should respond next. Essential for correct generation behavior.
- `continue_final_message=True` — Removes end-of-sequence tokens so the model continues from the final message. Useful for response prefills.

Do not use `add_generation_prompt` and `continue_final_message` together.

### Response Prefilling

Prefill a model's response to guide output format:

```python
chat = [
    {"role": "user", "content": "Format the answer in JSON."},
    {"role": "assistant", "content": '{"name": "'},
]
formatted = tokenizer.apply_chat_template(chat, tokenize=True, return_dict=True, continue_final_message=True)
model.generate(**formatted)  # Continues from '{"name": "'
```

### Training with Chat Templates

Apply chat templates during dataset preprocessing. Use `add_generation_prompt=False` for training:

```python
def preprocess(batch):
    return tokenizer.apply_chat_template(
        batch["conversations"],
        tokenize=True,
        add_generation_prompt=False,
        return_tensors="pt"
    )

dataset = dataset.map(preprocess, batched=True)
```

## Image Processors

Convert images to tensors for vision models:

```python
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import requests

processor = AutoImageProcessor.from_pretrained("facebook/dinov2-base")
model = AutoModelForImageClassification.from_pretrained("facebook/dinov2-base")

url = "https://huggingface.co/datasets/Narsil/image_dummy/raw/main/parrots.png"
image = Image.open(requests.get(url, stream=True).raw)

inputs = processor(image, return_tensors="pt")
outputs = model(**inputs)
```

## Feature Extractors

Process audio signals for speech models:

```python
from transformers import AutoFeatureExtractor, AutoModelForSpeechSeq2Seq
import soundfile as sf

extractor = AutoFeatureExtractor.from_pretrained("openai/whisper-large-v3")
speech, _ = sf.read("audio.flac")
inputs = extractor(speech, sampling_rate=16000, return_tensors="pt")
```

## Processors

Combined multimodal processors handle text and images together:

```python
from transformers import AutoProcessor, AutoModelForVision2Seq

processor = AutoProcessor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = AutoModelForVision2Seq.from_pretrained("Salesforce/blip2-opt-2.7b")
```

## Custom Tokenizers

Train a new tokenizer from a corpus:

```python
from transformers import GemmaTokenizer

tokenizer = GemmaTokenizer()
corpus = ["First document.", "Second document.", "Third document."]
new_tokenizer = tokenizer.train_new_from_iterator(corpus, vocab_size=1000)
```
