# Speculative Decoding for llama.cpp b8789

## Overview

Speculative decoding accelerates token generation by predicting multiple tokens ahead and verifying them in parallel. This can achieve 2-3x speedup when draft predictions are frequently correct.

**Core concept:** Compute n tokens in batch (prompt processing) is faster than n sequential generations.

## Implementations

### Draft Model Speculation

Use a smaller model to generate draft tokens:

```bash
llama-server -m main-model.gguf \
  --model-draft draft-model.gguf \
  --draft-max 16
```

**How it works:**
1. Draft model generates up to 16 tokens quickly
2. Main model verifies all drafts in single batch
3. Accepted tokens kept, rejected tokens regenerated

**Speedup factors:**
- Draft model should be 5-10x smaller than main model
- Higher acceptance rate = better speedup
- Best for repetitive or predictable text

**Example setup:**
```bash
# Qwen 7B with 0.5B draft
llama-server -hf ggml-org/Qwen2.5-7B-Instruct-GGUF \
  --model-draft /path/to/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf \
  --draft-max 16 \
  --draft-min 4
```

### N-gram Cache (`ngram-cache`)

Maintains statistics about short n-gram sequences:

```bash
llama-server -m model.gguf \
  --spec-type ngram-cache \
  --draft-max 16
```

**Features:**
- Learns from generated text
- External statistics can be loaded
- No additional model needed

**Use case:** Repetitive content, code generation, structured text

### N-gram Simple (`ngram-simple`)

Searches token history for matching patterns:

```bash
llama-server -m model.gguf \
  --spec-type ngram-simple \
  --spec-ngram-size-n 12 \
  --spec-ngram-size-m 48 \
  --draft-max 64
```

**Parameters:**
- `n` (default 12): Length of lookup n-gram (key)
- `m` (default 48): Length of draft m-gram (value)

**How it works:**
1. Find last n tokens in history
2. Search for previous occurrence
3. Use following m tokens as draft

**Best for:** Code refactoring, text rewriting, iterative editing

### N-gram Map Key (`ngram-map-k`)

Uses hash map for efficient pattern lookup:

```bash
llama-server -m model.gguf \
  --spec-type ngram-map-k \
  --spec-ngram-size-n 8 \
  --spec-ngram-size-m 8 \
  --spec-ngram-min-hits 2 \
  --draft-max 64
```

**Features:**
- Hash map of n-gram keys to m-gram values
- Minimum hits threshold (default: 1)
- Tracks acceptance rate per n-gram

**Use case:** Text with longer repetitions, technical documentation

### N-gram Map Key-4-Values (`ngram-map-k4v`)

Experimental: tracks up to 4 possible continuations per key:

```bash
llama-server -m model.gguf \
  --spec-type ngram-map-k4v \
  --spec-ngram-size-n 8 \
  --spec-ngram-size-m 8 \
  --spec-ngram-min-hits 2 \
  --draft-max 64
```

**Features:**
- Stores up to 4 m-gram values per n-gram key
- Uses most frequent continuation
- Better for ambiguous patterns

### N-gram Mod (`ngram-mod`)

Lightweight hash-based speculation with shared pool:

```bash
llama-server -m model.gguf \
  --spec-type ngram-mod \
  --spec-ngram-size-n 24 \
  --draft-min 48 \
  --draft-max 64
```

**Characteristics:**
- ~16 MB memory footprint
- Constant memory and complexity
- Shared hash pool across all server slots
- Variable draft lengths

**Applications:**
- Code iteration (llama.vim)
- Reasoning models (repeated thinking)
- Summarization tasks

## Command-Line Options

### Draft Model Options

| Option | Default | Description |
|--------|---------|-------------|
| `--draft-max N` | 16 | Maximum draft tokens |
| `--draft-min N` | 0 | Minimum draft tokens |
| `--draft-p-min P` | 0.75 | Min probability for greedy selection |
| `--model-draft FILE` | - | Path to draft model |
| `--n-gpu-layers-draft N` | auto | GPU layers for draft model |
| `--ctx-size-draft N` | 0 | Context size for draft (0 = from model) |

### N-gram Options

| Option | Default | Description |
|--------|---------|-------------|
| `--spec-type TYPE` | none | Speculation type (ngram-cache, ngram-simple, etc.) |
| `--spec-ngram-size-n N` | 12 | N-gram key size |
| `--spec-ngram-size-m N` | 48 | M-gram value size |
| `--spec-ngram-min-hits N` | 1 | Min occurrences for ngram-map |

### Lookup Cache Options

| Option | Description |
|--------|-------------|
| `--lookup-cache-static FILE` | Static lookup cache (not updated) |
| `--lookup-cache-dynamic FILE` | Dynamic lookup cache (updated during generation) |

## Configuration Examples

### Code Generation with N-gram

```bash
llama-server -hf ggml-org/Qwen2.5-Coder-7B-Instruct-GGUF \
  --spec-type ngram-simple \
  --spec-ngram-size-n 16 \
  --spec-ngram-size-m 64 \
  --draft-max 128
```

### Reasoning Models

```bash
llama-server -hf ggml-org/DeepSeek-R1-Distill-Qwen-7B-GGUF \
  --spec-type ngram-mod \
  --spec-ngram-size-n 32 \
  --draft-min 64 \
  --draft-max 128
```

### Multi-GPU with Draft Model

```bash
llama-server -m main-model.gguf \
  --model-draft draft-model.gguf \
  --tensor-split 1,1 \
  --device gpu0,gpu1 \
  --device-draft gpu0
```

### MoE Models (require long drafts)

```bash
llama-server -hf ggml-org/Mixtral-8x7B-Instruct-v0.1-GGUF \
  --spec-type ngram-mod \
  --spec-ngram-size-n 24 \
  --draft-min 48 \
  --draft-max 96
```

## Performance Tuning

### N-gram Size Selection

**Small n (8-12):**
- Faster lookups
- More false positives
- Good for highly repetitive text

**Large n (24-32):**
- Slower lookups
- Fewer false positives
- Better for diverse content

**Rule of thumb:** Start with n=16, adjust based on acceptance rate

### Draft Length Optimization

**Short drafts (8-16 tokens):**
- Lower overhead
- More verification calls
- Good for unpredictable text

**Long drafts (48-128 tokens):**
- Higher overhead per draft
- Fewer verification calls
- Best for repetitive/predictable content

**Monitor statistics:**
```
draft acceptance rate = 0.65 (260 accepted / 400 generated)
statistics ngram_simple: #calls=25, #gen drafts=25, #acc drafts=20, #gen tokens=800, #acc tokens=520
```

### Acceptance Rate Targets

| Acceptance Rate | Speedup | Recommendation |
|-----------------|---------|----------------|
| < 40% | Minimal | Reduce draft length or n-gram size |
| 40-60% | Moderate (1.2-1.5x) | Good balance |
| 60-80% | High (1.5-2.5x) | Optimal range |
| > 80% | Very high (2.5-3x+) | Can increase draft length |

## Statistics and Monitoring

### Output Statistics

```
draft acceptance rate = 0.57576 (  171 accepted /   297 generated)
statistics ngram_simple: #calls = 15, #gen drafts = 5, #acc drafts = 5, #gen tokens = 187, #acc tokens = 73
statistics draft: #calls = 10, #gen drafts = 10, #acc drafts = 10, #gen tokens = 110, #acc tokens = 98
```

**Metrics explained:**
- `#calls`: Number of speculation attempts
- `#gen drafts`: Drafts generated
- `#acc drafts`: Drafts partially or fully accepted
- `#gen tokens`: Total draft tokens (including rejected)
- `#acc tokens`: Tokens accepted by main model

### Timing Statistics

```
statistics ngram_mod: #calls(b,g,a) = 810, dur(b,g,a) = 0.149, 0.347, 0.005 ms
```

- `b` (begin): New prompt processing time
- `g` (generation): Draft generation time
- `a` (accumulation): Acceptance verification time

### Prometheus Metrics

With `--metrics` flag:

```
# HELP llama_speculative_acceptance_rate Draft acceptance rate
# TYPE llama_speculative_acceptance_rate gauge
llama_speculative_acceptance_rate{slot_id="0"} 0.65

# HELP llama_speculative_tokens_generated Total draft tokens generated
# TYPE llama_speculative_tokens_generated counter
llama_speculative_tokens_generated{slot_id="0"} 15234
```

## Hybrid Speculation

Combine multiple speculation methods:

```bash
llama-server -m model.gguf \
  --model-draft draft-model.gguf \
  --spec-type ngram-mod \
  --draft-max 32
```

**Precedence:** Draft model > n-gram methods

**Benefits:**
- Draft model handles general patterns
- N-gram catches repetitive sequences
- Better overall acceptance rate

## Use Cases

### Best for Speculative Decoding

1. **Code generation/refactoring** - High repetition, predictable patterns
2. **Technical documentation** - Repeated terminology and structure
3. **Summarization** - Common phrases and transitions
4. **Reasoning models** - Repeated thinking patterns
5. **Creative writing** - Character dialogue, descriptive passages

### Less Effective For

1. **Highly creative content** - Low predictability
2. **Data generation** - Random or unique values
3. **Translation** - Language-specific variations
4. **Q&A with facts** - Variable responses

## Troubleshooting

### Low Acceptance Rate (< 30%)

**Symptoms:** Speculation slower than normal generation

**Solutions:**
- Reduce `--draft-max` to 8 or 16
- Increase `--spec-ngram-size-n` for n-gram methods
- Use draft model instead of n-gram
- Disable speculation for this workload

### High Memory Usage

**Cause:** Large n-gram hash tables or draft model in VRAM

**Solutions:**
```bash
# Keep draft model on CPU
llama-server --n-gpu-layers-draft 0

# Reduce n-gram size
llama-server --spec-ngram-size-n 8 --spec-ngram-size-m 16

# Use ngram-mod (lightweight, ~16 MB)
llama-server --spec-type ngram-mod
```

### Draft Model Compatibility Issues

**Symptoms:** "Model incompatible" errors or poor acceptance

**Solutions:**
- Use same model family for draft (e.g., Qwen 0.5B draft for Qwen 7B main)
- Match tokenizer vocabularies
- Try `--spec-replace` for token translation:
  ```bash
  llama-server --spec-replace "<|begin_of_text|>" "<s>"
  ```

### No Speedup Observed

**Causes:**
- Batch size too small
- Context too short
- Content too unpredictable

**Solutions:**
- Increase batch size: `--batch-size 512`
- Use longer prompts/contexts
- Tune n-gram sizes for your content type
- Monitor statistics to verify speculation is active

## Advanced Techniques

### Custom N-gram Statistics

Load pre-computed n-gram statistics:

```bash
llama-server -m model.gguf \
  --spec-type ngram-cache \
  --lookup-cache-static /path/to/ngram-stats.bin
```

### Dynamic N-gram Adjustment

Adjust parameters based on content type:

```bash
# Code generation
--spec-ngram-size-n 16 --spec-ngram-size-m 64

# Natural language
--spec-ngram-size-n 8 --spec-ngram-size-m 24

# Technical docs
--spec-ngram-size-n 12 --spec-ngram-size-m 48
```

### Per-Slot Configuration

Different speculation settings per server slot via `--props` endpoint:

```bash
curl -X POST http://localhost:8080/props \
  -d '{"n_parallel": 4, "draft_max": 32}'
```

## Comparison with Other Methods

| Method | Speedup | Memory | Best For |
|--------|---------|--------|----------|
| Draft model | 2-3x | High (+draft model) | General purpose |
| ngram-simple | 1.5-2x | Low | Repetitive text |
| ngram-map-k | 1.5-2x | Medium | Structured content |
| ngram-mod | 1.5-2.5x | Very low (~16 MB) | Multi-user servers |
| No speculation | 1x (baseline) | Lowest | Unpredictable content |
