# Model Optimization

Guide to optimizing Sentence Transformer models for faster inference and lower resource usage.

## ONNX Export

Export models to ONNX format for faster inference:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Export to ONNX
model.save("./my-model-onnx", safe_serialization=False)

# Or use onnx directly
import onnx
from onnx import load_model, check_model

onnx_model = load_model("./my-model.onnx")
check_model(onnx_model)  # Validate
```

### Run ONNX Model

```python
import onnxruntime as ort
import numpy as np

# Load ONNX model
session = ort.InferenceSession("./my-model.onnx")

# Prepare input
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# Run inference
embeddings = session.run(
    [output_name],
    {input_name: input_ids}
)[0]
```

## OpenVINO Optimization

Intel's OpenVINO for CPU optimization:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert to OpenVINO IR format
from openvino.tools.mo import mo_main
mo_main(
    "--input_model=./my-model",
    "--output_dir=./openvino-model",
    "--input_shape=[1,512]"
)

# Load and use
from openvino.inference_engine import IECore
ie = IECore()
ir = ie.read_network(model="./openvino-model/model.xml")
exec_net = ie.load_network(network=ir, device_name="CPU")
```

## Quantization

### INT8 Quantization

Reduce model size and improve speed:

```python
from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer("all-MiniLM-L6-v2")

# Dynamic quantization (works on CPU)
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},
    dtype=torch.qint8
)

# Save quantized model
quantized_model.save("./quantized-model")
```

### Embedding Quantization

Quantize embeddings instead of models:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(["text1", "text2"], convert_to_numpy=True)

# Binary quantization (1-bit)
binary_embeddings = np.sign(embeddings)

# INT8 quantization
scaled = embeddings / np.max(np.abs(embeddings))  # Normalize to [-1, 1]
int8_embeddings = (scaled * 127).astype(np.int8)

# Store compressed embeddings
np.save("./compressed-embeddings.npy", int8_embeddings)
```

## Model Distillation

Compress large models into smaller ones:

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.losses import KnowledgeDistillationLoss
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer

# Teacher (large, accurate)
teacher = SentenceTransformer("all-mpnet-base-v2").eval()

# Student (small, fast)
student = SentenceTransformer("distilbert-base-uncased")

# Distillation loss
loss_fn = KnowledgeDistillationLoss(
    student,
    teacher,
    temperature=2.0
)

train_args = SentenceTransformerTrainingArguments(
    output_dir="./distilled-model",
    num_train_epochs=5,
    per_device_train_batch_size=32,
    learning_rate=5e-5,
)

trainer = SentenceTransformerTrainer(
    model=student,
    args=train_args,
    train_dataset=train_data,
    loss=loss_fn,
)

trainer.train()
```

## PEFT (Parameter-Efficient Fine-Tuning)

Use adapters to fine-tune without updating all parameters:

```python
from sentence_transformers import SentenceTransformer
from peft import LoraConfig, get_peft_model

model = SentenceTransformer("all-MiniLM-L6-v2")

# Configure LoRA adapter
lora_config = LoraConfig(
    r=16,  # Rank
    lora_alpha=32,
    target_modules=["query", "value"],
    lora_dropout=0.1,
)

# Apply adapter
model.auto_model = get_peft_model(model.auto_model, lora_config)

# Train only adapter parameters (much faster!)
```

### Loading Adapters

```python
from sentence_transformers import SentenceTransformer

# Load base model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load specific adapter
model.load_adapter("./medical-adapter")

# Switch between adapters
model.load_adapter("./legal-adapter")
model.active_adapters = ["medical"]  # Or "legal"
```

## Unsloth Integration

Memory-efficient training with Unsloth:

```python
from sentence_transformers import SentenceTransformer
from unsloth import FastLanguageModel

# Load with Unsloth optimizations
model = FastLanguageModel.from_pretrained(
    model_name="all-MiniLM-L6-v2",
    max_seq_length=512,
    load_in_4bit=True,  # 4-bit quantization
)

# Train with reduced memory usage
# Same API as regular training
```

## Batch Processing Optimization

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Optimize batch encoding
embeddings = model.encode(
    large_corpus,
    batch_size=64,  # Tune for your GPU memory
    show_progress_bar=True,
    convert_to_numpy=True,
    use_gpu=True,
)

# Multi-process for CPU
embeddings = model.encode(
    large_corpus,
    batch_size=32,
    multi_process=True,
    num_workers=4,
)
```

## Caching Embeddings

Pre-compute and cache static corpus:

```python
import pickle
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode and cache
corpus = load_corpus()  # Your document corpus
embeddings = model.encode(corpus, normalize_embeddings=True)

# Save to disk
with open("./corpus-embeddings.pkl", "wb") as f:
    pickle.dump({
        "corpus": corpus,
        "embeddings": embeddings,
        "model": "all-MiniLM-L6-v2"
    }, f)

# Load later (no re-encoding needed!)
with open("./corpus-embeddings.pkl", "rb") as f:
    cached = pickle.load(f)
corpus_embeddings = cached["embeddings"]
```

## GPU Optimization

### Mixed Precision Training

```python
from sentence_transformers.training_args import SentenceTransformerTrainingArguments

train_args = SentenceTransformerTrainingArguments(
    output_dir="./model",
    fp16=True,  # FP16 mixed precision (Volta+ GPUs)
    # Or: bf16=True  # BFloat16 (Ampere+ GPUs)
)
```

### Gradient Checkpointing

Reduce memory usage:

```python
train_args = SentenceTransformerTrainingArguments(
    output_dir="./model",
    gradient_checkpointing=True,
)
```

## Benchmarking

Measure inference speed:

```python
import time
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
test_sentences = ["Test sentence"] * 1000

# Warmup
model.encode(test_sentences[:10])

# Benchmark
start = time.time()
for _ in range(10):
    embeddings = model.encode(test_sentences, batch_size=32)
end = time.time()

sentences_per_second = len(test_sentences) * 10 / (end - start)
print(f"Throughput: {sentences_per_second:.1f} sentences/second")
```

## Performance Comparison

| Optimization | Speedup | Model Size | Accuracy Loss |
|--------------|---------|------------|---------------|
| Base model | 1x | 42MB | - |
| ONNX + CPU | 2-3x | 42MB | None |
| OpenVINO + CPU | 3-5x | 42MB | None |
| INT8 Quantization | 2-4x | 10MB | <1% |
| Distillation (DistilBERT) | 2x | 13MB | 2-5% |
| LoRA Adapter | 1x | +1MB | None (same as full fine-tune) |
| 4-bit Quantization | 1x | 5MB | 1-3% |

## Best Practices

1. **Profile first**: Measure baseline performance before optimizing
2. **ONNX for CPU**: Best speedup for CPU inference
3. **Mixed precision for GPU**: Enable fp16/bf16 training
4. **Cache embeddings**: Pre-compute static corpus once
5. **Distillation for deployment**: Trade accuracy for speed
6. **PEFT for multi-domain**: Use adapters instead of full fine-tuning
7. **Batch processing**: Always use batch_size > 1
