# Text Generation

## The Generate API

The `model.generate()` method is the core text generation interface, available on all models with generative capabilities:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", device_map="auto")

inputs = tokenizer(["A list of colors: red, blue"], return_tensors="pt").to(model.device)
generated_ids = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0])
```

## Generation Configuration

All generation settings are stored in `GenerationConfig`, loaded from the model's `generation_config.json`:

```python
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", device_map="auto")
print(model.generation_config)
# Shows non-default values (e.g., bos_token_id, eos_token_id)
```

Override settings directly in `generate()`:

```python
model.generate(**inputs, num_beams=4, do_sample=True, max_new_tokens=100)
```

Save a custom generation config:

```python
from transformers import GenerationConfig

gen_config = GenerationConfig(
    max_new_tokens=50,
    do_sample=True,
    top_k=50,
    eos_token_id=model.config.eos_token_id
)
gen_config.save_pretrained("my-model-dir", push_to_hub=True)
```

## Common Generation Options

- `max_new_tokens` (int) — Maximum tokens to generate. Always set this explicitly; defaults vary by model.
- `do_sample` (bool) — `True` for multinomial sampling (creative), `False` for greedy search (deterministic).
- `temperature` (float) — Controls randomness. High (>0.8) for creative tasks, low (<0.4) for focused output. Requires `do_sample=True`.
- `num_beams` (int) — Beam count for beam search. Set >1 to enable. Good for input-grounded tasks.
- `repetition_penalty` (float) — Set >1.0 to reduce repetition.
- `eos_token_id` (list[int]) — Tokens that stop generation.

## Decoding Strategies

### Greedy Search

Default strategy. Selects the most likely token at each step. Good for short, deterministic outputs but tends to repeat on longer sequences.

```python
outputs = model.generate(**inputs, max_new_tokens=20)
```

### Multinomial Sampling

Randomly selects tokens based on probability distribution. Produces more diverse and creative outputs.

```python
outputs = model.generate(**inputs, do_sample=True, num_beams=1, max_new_tokens=50)
```

### Beam Search

Tracks multiple candidate sequences and selects the one with highest overall probability. Best for input-grounded tasks like translation or transcription.

```python
outputs = model.generate(**inputs, num_beams=4, max_new_tokens=50)
```

## Streaming

Stream generated text token-by-token to reduce perceived latency:

```python
from transformers import TextStreamer

streamer = TextStreamer(tokenizer)
model.generate(**inputs, streamer=streamer, max_new_tokens=20)
```

Custom streamers must implement `put()` and `end()` methods.

## Watermarking

Detect machine-generated text with watermarking:

```python
from transformers import WatermarkDetector, WatermarkingConfig

watermark_config = WatermarkingConfig(bias=2.5, seeding_scheme="selfhash")
out = model.generate(**inputs, watermarking_config=watermark_config, do_sample=False, max_length=20)

detector = WatermarkDetector(model_config=model.config, device="cpu", watermarking_config=watermark_config)
result = detector(out, return_dict=True)
print(result.prediction)  # array([True, True])
```

## Custom Generation Methods

Share custom decoding loops as Hub repositories with the `custom_generate` tag:

```python
gen_out = model.generate(
    **inputs,
    custom_generate="transformers-community/custom_generate_example",
    trust_remote_code=True
)
```

Create a custom generation method by pushing `custom_generate/generate.py` and `custom_generate/requirements.txt` to a model repository.

## Common Pitfalls

### Output Length

Default generation length is typically 20 tokens. Always set `max_new_tokens`:

```python
# Too short (default)
model.generate(**inputs)

# Controlled length
model.generate(**inputs, max_new_tokens=100)
```

### Padding Side

Set `padding_side="left"` for generation with batching:

```python
tokenizer = AutoTokenizer.from_pretrained("model-name", padding_side="left")
tokenizer.pad_token = tokenizer.eos_token
```

Right-padding causes the model to generate garbage from padding tokens.

### Prompt Format

Chat models expect properly formatted messages, not raw strings:

```python
# Wrong — raw string to a chat model
model.generate(tokenizer("How many cats...", return_tensors="pt"))

# Right — use chat template
messages = [{"role": "user", "content": "How many cats..."}]
inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
model.generate(inputs)
```

## Extending Generation

- `logits_processor` — Custom `LogitsProcessor` instances to manipulate token probabilities
- `stopping_criteria` — Custom `StoppingCriteria` to halt generation based on conditions

```python
from transformers import LogitsProcessorList, StoppingCriteriaList

custom_processors = LogitsProcessorList([MyCustomProcessor()])
custom_stoppers = StoppingCriteriaList([MyCustomStopper()])

model.generate(**inputs, logits_processor=custom_processors, stopping_criteria=custom_stoppers)
```
