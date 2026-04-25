# Quantization Guide for llama.cpp b8789

## Overview

Quantization reduces model size and memory usage while maintaining quality. llama.cpp supports multiple quantization methods from 2-bit to 16-bit precision.

## Quantization Types

### Integer Quantizations

| Type | Bits/Weight | Speed | Quality | Use Case |
|------|-------------|-------|---------|----------|
| `IQ2_XS` | ~2.06 | Fastest | Low | Ultra-low memory |
| `IQ2_S` | ~2.15 | Very fast | Low-med | Extreme compression |
| `IQ2_M` | ~2.38 | Very fast | Medium | Small devices |
| `IQ3_XS` | ~3.04 | Fast | Med-high | Good balance |
| `IQ3_S` | ~3.17 | Fast | Med-high | Portable models |
| `IQ1_M` | ~1.68 | Fastest | Low | Research/testing |

### K-Means Quantizations (Recommended)

| Type | Bits/Weight | Speed | Quality | Use Case |
|------|-------------|-------|---------|----------|
| `Q4_K_S` | ~4.20 | Very fast | Good | Default choice |
| `Q4_K_M` | ~4.65 | Fast | Very good | **Recommended** |
| `Q5_K_S` | ~5.19 | Fast | Excellent | High quality |
| `Q5_K_M` | ~5.63 | Medium | Excellent | Quality-focused |
| `Q6_K` | ~6.28 | Medium | Near-lossless | Critical accuracy |

### Standard Quantizations

| Type | Bits/Weight | Speed | Quality | Use Case |
|------|-------------|-------|---------|----------|
| `Q8_0` | ~8.00 | Medium | Excellent | Almost full precision |
| `Q4_0` | ~4.00 | Fast | Good | Legacy format |
| `Q5_0` | ~5.00 | Fast | Very good | Legacy format |

### Floating Point

| Type | Bits/Weight | Speed | Quality | Use Case |
|------|-------------|-------|---------|----------|
| `BF16` | 16 | Slow | Reference | Baseline quality |
| `F16` | 16 | Slow | Reference | Maximum quality |
| `F32` | 32 | Slowest | Original | Development only |

## Creating Quantized Models

### Using llama-quantize

**Basic quantization:**
```bash
./llama-quantize /path/to/model-f16.gguf /path/to/model-q4_k_m.gguf Q4_K_M
```

**From full precision (F32):**
```bash
./llama-quantize model-f32.gguf model-q5_k_m.gguf Q5_K_M
```

**List available quant types:**
```bash
llama-quantize  # Without arguments shows all types
```

### Quantization with Docker

```bash
docker run -v /path/to/models:/models ghcr.io/ggml-org/llama.cpp:full \
  --quantize /models/model-f16.gguf /models/model-q4_k_m.gguf Q4_K_M
```

## Quantization Strategies

### Per-Group Quantization (K-Means)

K-means quantizations (`Q*_K_*`) use different precision for different tensor parts:
- Weights: 4-6 bits
- Some important weights: 8 bits or full precision

**Benefits:**
- Better quality at same bit rate
- Preserves important weight information
- Recommended for most use cases

### Important Quantizations (IQ*)

IQ types use importance matrices to identify critical weights:
- Analyze weight significance during quantization
- Keep important weights at higher precision
- Better than standard quantizations at low bits

**Best for:** 2-bit to 3-bit extreme compression

## Recommended Workflows

### General Purpose Models

```bash
# Create multiple quantizations for testing
llama-quantize model-f16.gguf model-q4_k_s.gguf Q4_K_S
llama-quantize model-f16.gguf model-q4_k_m.gguf Q4_K_M
llama-quantize model-f16.gguf model-q5_k_m.gguf Q5_K_M

# Test quality vs size
ls -lh model-*.gguf
```

### Memory-Constrained Devices

```bash
# Ultra-low memory (RAM < 4GB)
llama-quantize model-f16.gguf model-iq2_xs.gguf IQ2_XS

# Low memory (RAM 4-8GB)
llama-quantize model-f16.gguf model-q3_s.gguf Q3_S
```

### Quality-Critical Applications

```bash
# Near-lossless quality
llama-quantize model-f16.gguf model-q6_k.gguf Q6_K

# Almost full precision
llama-quantize model-f16.gguf model-q8_0.gguf Q8_0
```

## Size Estimates

For a 7B parameter model:

| Quant Type | Model Size | RAM (CPU) | VRAM (GPU) |
|------------|------------|-----------|------------|
| F16 | ~14 GB | ~28 GB | ~14 GB |
| Q8_0 | ~5.5 GB | ~7 GB | ~5.5 GB |
| Q6_K | ~4.5 GB | ~6 GB | ~4.5 GB |
| Q5_K_M | ~3.8 GB | ~5 GB | ~3.8 GB |
| Q4_K_M | ~3.2 GB | ~4.5 GB | ~3.2 GB |
| Q4_K_S | ~3.0 GB | ~4.2 GB | ~3.0 GB |
| Q3_S | ~2.4 GB | ~3.5 GB | ~2.4 GB |
| IQ2_XS | ~1.8 GB | ~2.8 GB | ~1.8 GB |

**Note:** Add 2-4 GB for context/KV cache depending on context size.

## Quality Assessment

### Benchmark with llama-bench

```bash
# Compare different quantizations
./llama-bench -m model-q4_k_m.gguf -n 64 -ngl 0
./llama-bench -m model-q5_k_m.gguf -n 64 -ngl 0
./llama-bench -m model-q8_0.gguf -n 64 -ngl 0
```

### Perplexity Testing

Lower perplexity = better quality:

```bash
# Use Wikitext-2 test set
./llama-bench -m model-q4_k_m.gguf -f wikitext-2-test.json
```

### Manual Quality Check

```bash
# Generate with different quantizations and compare
llama-cli -m model-q4_k_m.gguf -p "Explain quantum computing" -n 100
llama-cli -m model-q5_k_m.gguf -p "Explain quantum computing" -n 100
llama-cli -m model-f16.gguf -p "Explain quantum computing" -n 100
```

## Advanced Quantization Options

### Preserving Specific Tensors

Some tensors benefit from higher precision:
- Token embedding layers
- Output projection layers
- Attention output projections

**Override tensor types:**
```bash
# Keep token embeddings in F16
llama-quantize --allow-requant \
  -s 'token_embd.*=f16,output.*=f16' \
  model-f16.gguf model-custom.gguf Q4_K_M
```

### Partial Quantization

Quantize only some layers:

```bash
# Keep first and last 4 layers in F16
llama-quantize --allow-requant \
  -s 'blk.0.*=f16,blk.1.*=f16,blk.2.*=f16,blk.3.*=f16,blk.31.*=f16,output.*=f16' \
  model-f16.gguf model-partial.gguf Q4_K_M
```

### Requantization

Convert between quantizations:

```bash
# From Q8_0 to Q4_K_M (lossy)
llama-quantize --allow-requant \
  model-q8_0.gguf model-q4_k_m.gguf Q4_K_M

# From Q4_K_S to Q5_K_M (may improve quality)
llama-quantize --allow-requant \
  model-q4_k_s.gguf model-q5_k_m.gguf Q5_K_M
```

**Warning:** Requantization from already-quantized models may reduce quality.

## KV Cache Quantization

Reduce memory for large contexts:

```bash
llama-server -m model.gguf \
  --cache-type-k q4_0 \
  --cache-type-v q4_0
```

**Available types:** `f16`, `q8_0`, `q4_0`, `q4_1`, `iq4_nl`

**Memory savings:** Up to 75% for KV cache at cost of some quality.

## Tips and Best Practices

### When to Use Each Quant Type

1. **Q4_K_M**: Default choice, best balance
2. **Q5_K_M**: Quality-critical tasks (reasoning, code)
3. **Q4_K_S**: Memory-constrained with decent quality
4. **Q6_K/Q8_0**: When accuracy is paramount
5. **IQ2_XS/IQ3_S**: Extreme memory constraints
6. **F16**: Baseline for comparison only

### Testing Protocol

```bash
# 1. Create quantizations
for type in Q4_K_M Q5_K_M Q6_K; do
  llama-quantize model-f16.gguf model-$type.gguf $type
done

# 2. Benchmark each
for type in Q4_K_M Q5_K_M Q6_K; do
  echo "=== $type ==="
  llama-bench -m model-$type.gguf -n 128
done

# 3. Quality test with known prompts
llama-cli -m model-Q4_K_M.gguf -p "Write a Python function to sort a list" -n 64
```

### Storage Strategy

Keep one high-quality quantization (Q5_K_M or Q6_K) as master:
- Re-quantize from master for experiments
- Don't chain multiple quantizations
- Store F16 if disk space allows (for future requantization)

## Troubleshooting

### "Quantization failed"

**Cause:** Corrupted input file or insufficient memory

**Solution:**
```bash
# Verify input file
llama-cli -m model-f16.gguf -n 1

# Try with more memory or smaller batch
ulimit -v unlimited
```

### Quality degradation

**Symptoms:** Nonsensical output, repetition, grammar issues

**Solutions:**
- Use higher-bit quantization (Q5_K_M instead of Q4_K_S)
- Avoid requantizing already-quantized models
- Check for corrupted source file
- Try different quant type (IQ* vs Q*_K_*)

### Memory errors during quantization

**Cause:** Large model + limited RAM

**Solution:**
```bash
# Use swap space
sudo swapon --show
sudo fallocate -s 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Then quantize with more available memory
```

## Performance Impact

Quantization affects performance differently:

| Aspect | Impact |
|--------|--------|
| **Prompt processing** | Minimal (1-5% slowdown) |
| **Token generation** | Can be 20-40% faster (less memory bandwidth) |
| **Model loading** | Faster (smaller files) |
| **Memory usage** | Dramatically reduced (50-80%) |

**Note:** Some quantizations may be slower on certain hardware due to lack of optimized kernels.
