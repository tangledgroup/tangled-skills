# Model Quantization

## Overview

Quantization reduces model weight precision (e.g., from FP32 to 4-bit integers), shrinking model size and speeding up inference at some accuracy cost. Accuracy loss is measured via perplexity (PPL) and KL divergence.

The `llama-quantize` tool converts GGUF models between quantization formats:

```bash
llama-quantize input-model-f32.gguf output-Q4_K_M.gguf Q4_K_M
```

## Quantization Types

### K-Quant (Recommended)

K-quants use mixed precision — critical tensors kept at higher precision while others are compressed more aggressively.

- **Q4_K_M** — best balance of quality and size (~4.9 GB for Llama 3.1 8B). Recommended default.
- **Q4_K_S** — slightly smaller than Q4_K_M with minimal quality loss
- **Q5_K_M** — higher quality, larger size (~5.3 GB for 8B)
- **Q5_K_S** — smaller variant of Q5
- **Q6_K** — high quality (~6.1 GB for 8B), good for demanding tasks
- **Q8_0** — near-FP16 quality (~8.0 GB for 8B), smallest accuracy loss among quants

### I-Quant (2-bit and 3-bit)

I-quants use importance matrices for even more aggressive compression:

- **IQ2_XS** through **IQ2_XXS** — ~2.0 bits/weight, smallest size (~1.9-2.2 GB for 8B)
- **IQ3_XS** through **IQ3_M** — ~3.3-3.8 bits/weight
- **IQ4_XS**, **IQ4_NL** — ~4.5-4.7 bits/weight

### Legacy Quant

- **Q2_K** / **Q2_K_S** — 2-bit k-quant, very aggressive compression
- **Q3_K_S/M/L** — 3-bit variants
- **F16** — FP16, no quantization (~15 GB for 8B)

## Quantization Workflow

### Step 1: Convert to GGUF

Convert from Hugging Face format using the `convert_*.py` scripts in the repo:

```bash
python3 convert_hf_to_gguf.py ./models/mymodel/
# Produces: mymodel/ggml-model-f16.gguf
```

### Step 2: Generate Importance Matrix (Optional but Recommended)

For better quantization quality, compute an importance matrix:

```bash
llama-imatrix -m model-f16.gguf -f data/*.txt -o imatrix.gguf
```

### Step 3: Quantize

```bash
# Basic quantization
llama-quantize input-f16.gguf output-Q4_K_M.gguf Q4_K_M

# With importance matrix
llama-quantize --imatrix imatrix.gguf input-f16.gguf output-Q4_K_M.gguf Q4_K_M

# Custom tensor types with regex
llama-quantize --imatrix imatrix.gguf \
  --tensor-type "\.(\d*[13579])\.attn_k=q5_k" \
  --tensor-type "\.(\d*[02468])\.attn_q=q3_k" \
  input-f16.gguf output-Q4_K_M.gguf Q4_K_M

# Set output layer precision
llama-quantize --imatrix imatrix.gguf \
  --output-tensor-type q5_k \
  --token-embedding-type q3_k \
  input-f16.gguf output-Q4_K_M.gguf Q4_K_M
```

### Step 4: Verify Quality

Measure perplexity to compare quantization quality:

```bash
llama-perplexity -m model-Q4_K_M.gguf -f test-corpus.txt
# Lower perplexity = better quality
```

## Quantization Options

- `--allow-requantize` — allow requantizing already-quantized tensors (warning: quality loss)
- `--leave-output-tensor` — keep output.weight unquantized (increases size, may improve quality)
- `--pure` — disable k-quant mixtures, use single quant type for all tensors
- `--keep-split` — preserve input file's shard structure in output
- `--prune-layers 20,21,22` — remove specific layers (for model surgery)
- `--override-kv key=int:value` — override metadata in quantized model

## Memory Requirements

| Model | FP16 Size | Q4_K_M | Q8_0 |
|-------|-----------|--------|------|
| 8B    | ~16 GB    | ~4.9 GB | ~8.0 GB |
| 70B   | ~140 GB   | ~43 GB  | ~72 GB |
| 405B  | ~812 GB   | ~249 GB | ~413 GB |

You need sufficient RAM to load the source model and disk space for intermediate files.

## Online Tools

Hugging Face provides web-based tools:

- **GGUF-my-repo** — convert to GGUF and quantize online: https://huggingface.co/spaces/ggml-org/gguf-my-repo
- **GGUF-editor** — edit GGUF metadata in browser: https://huggingface.co/spaces/CISCai/gguf-editor
- **GGUF-my-LoRA** — convert LoRA adapters to GGUF: https://huggingface.co/spaces/ggml-org/gguf-my-lora

## Model Sources

Models are available on Hugging Face. Search for GGUF models:

```bash
# Download directly via CLI
llama-cli -hf ggml-org/gemma-3-1b-it-GGUF

# With specific quantization
llama-cli -hf bartowski/Llama-3.1-8B-Instruct-GGUF:Q4_K_M

# With custom file selection
llama-cli -hfr bartowski/Qwen2.5-7B-Instruct-GGUF \
  -hff Qwen2.5-7B-Instruct-Q6_K.gguf
```

Models can also be stored in a local directory for router mode:

```bash
llama-server --models-dir ./my_models
```
