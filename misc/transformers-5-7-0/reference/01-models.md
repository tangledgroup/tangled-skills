# Models

## Loading Models

Transformers provides 450+ pretrained model architectures. Load any model with `from_pretrained()`, which downloads weights and configuration from the Hugging Face Hub (or loads from a local directory).

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    dtype="auto",
    device_map="auto"
)
```

Weights are stored in [safetensors](https://huggingface.co/docs/safetensors) format by default — more secure and faster than pickle-based serialization.

## AutoClasses

AutoClasses automatically resolve the correct model class from the configuration file. You only need to know the task and checkpoint name.

### Task-specific AutoModel classes

**Natural Language Processing:**

- `AutoModelForCausalLM` — Text generation (decoder-only models like GPT, Llama)
- `AutoModelForMaskedLM` — Fill-in-the-blank (encoder models like BERT)
- `AutoModelForSeq2SeqLM` — Sequence-to-sequence (T5, BART)
- `AutoModelForSequenceClassification` — Text classification
- `AutoModelForTokenClassification` — Named entity recognition, token-level tasks
- `AutoModelForQuestionAnswering` — Extractive QA
- `AutoModelForMultipleChoice` — Multiple choice classification
- `AutoModelForNextSentencePrediction` — Next sentence prediction

**Computer Vision:**

- `AutoModelForImageClassification` — Image classification
- `AutoModelForObjectDetection` — Object detection
- `AutoModelForImageSegmentation` — Image segmentation
- `AutoModelForVideoClassification` — Video classification
- `AutoModelForDepthEstimation` — Depth estimation
- `AutoModelForMaskedImageModeling` — Masked image modeling

**Multimodal:**

- `AutoModelForDocumentQuestionAnswering` — Document QA
- `AutoModelForVisualQuestionAnswering` — Visual QA

### Other Auto Classes

- `AutoConfig` — Load model configuration
- `AutoTokenizer` — Load tokenizer
- `AutoFeatureExtractor` — Load audio feature extractor
- `AutoImageProcessor` — Load image processor
- `AutoVideoProcessor` — Load video processor
- `AutoProcessor` — Combined multimodal processor

## Model Data Types

The `dtype` argument controls the precision of model weights:

```python
import torch

# Auto-detect from config.json or checkpoint
model = AutoModelForCausalLM.from_pretrained("model-name", dtype="auto")

# Force specific precision
model = AutoModelForCausalLM.from_pretrained("model-name", dtype=torch.float16)
model = AutoModelForCausalLM.from_pretrained("model-name", dtype=torch.bfloat16)
```

Without `dtype="auto"`, PyTorch loads weights in `torch.float32` by default, which doubles memory usage if the checkpoint is stored in bfloat16.

## Large Models

### Sharded Checkpoints

Checkpoints larger than 50GB are automatically sharded. An index file (`model.safetensors.index.json`) maps parameter names to shard files. Parameters load in parallel.

```python
import json

# Inspect the index
with open("model.safetensors.index.json") as f:
    index = json.load(f)

print(index["metadata"])  # {'total_size': 28966928384}
print(list(index["weight_map"].keys())[:5])  # parameter -> shard mapping
```

### Big Model Inference

Accelerate's Big Model Inference creates a model skeleton on the meta device (no real data, only metadata), then loads pretrained weights directly — avoiding holding two copies of weights in memory.

Set `device_map="auto"` to enable automatic device placement:

```python
model = AutoModelForCausalLM.from_pretrained("google/gemma-7b", device_map="auto")
```

Custom device mapping for fine-grained control:

```python
device_map = {
    "model.layers.0": 0,
    "model.layers.14": 1,
    "model.layers.31": "cpu",
    "lm_head": "disk"
}
model = AutoModelForCausalLM.from_pretrained("big-model", device_map=device_map)
print(model.hf_device_map)  # Inspect placement
```

## Model Architecture vs Checkpoint

- **Architecture** — The model's skeleton (e.g., BERT, Llama, GPT-2). Defined by `configuration.py` and `modeling.py`.
- **Checkpoint** — The trained weights for a given architecture (e.g., `google-bert/bert-base-uncased`).

A barebones model (like `LlamaModel`) returns raw hidden states. A model with a task head (like `LlamaForCausalLM`) converts those into task-specific outputs.

## Custom Models

Register custom model classes with AutoClasses:

```python
from transformers import AutoConfig, AutoModel

AutoConfig.register("new-model", NewModelConfig)
AutoModel.register(NewModelConfig, NewModel)

# Now AutoClass resolves your custom model
model = AutoModel.from_pretrained("my-custom-model")
```

Ensure `NewModelConfig.model_type` matches the registration key, and `NewModel.config_class` references `NewModelConfig`.

## Saving Models

```python
model.save_pretrained("./output-dir", max_shard_size="50GB")
tokenizer.save_pretrained("./output-dir")

# Push to Hub
model.push_to_hub("my-account/my-model")
```
