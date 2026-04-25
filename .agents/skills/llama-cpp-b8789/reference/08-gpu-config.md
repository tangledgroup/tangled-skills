# GPU Configuration for llama.cpp b8789

## Overview

llama.cpp supports multiple GPU backends with various offloading strategies. Proper configuration maximizes performance while avoiding VRAM exhaustion.

## Backend Detection

### List Available Devices

```bash
llama-server --list-devices
```

**Example output:**
```
GPU 0: NVIDIA GeForce RTX 4090 (CUDA, compute 8.9)
GPU 1: NVIDIA GeForce RTX 3080 (CUDA, compute 8.6)
CPU: Intel Core i9-13900K (AVX2, AVX512)
```

### Check Backend Support

```bash
llama-server --version
# Shows compiled backends: CUDA, Metal, HIP, Vulkan, etc.
```

## GPU Offloading Basics

### Number of GPU Layers

**Offload all layers:**
```bash
llama-server -m model.gguf --n-gpu-layers 99
```

**Offload specific count:**
```bash
llama-server -m model.gguf --n-gpu-layers 30
```

**Auto-detect (default):**
```bash
llama-server -m model.gguf --n-gpu-layers auto
```

**No GPU offloading:**
```bash
llama-server -m model.gguf --n-gpu-layers 0
```

### VRAM Estimation

For a 7B model with Q4_K_M quantization:
- Model weights: ~3.2 GB
- KV cache (4K context): ~2 GB
- Overhead: ~0.5 GB
- **Total:** ~5.7 GB VRAM

**Rule of thumb:** Leave 1-2 GB headroom to avoid OOM errors.

## Multi-GPU Configuration

### Layer Splitting (Default)

Split model layers across GPUs:

```bash
# Two GPUs, split layers evenly
llama-server -m model.gguf \
  --tensor-split 1,1 \
  --n-gpu-layers 99
```

**How it works:**
- GPU 0: First half of layers
- GPU 1: Second half of layers
- KV cache split proportionally

### Row Splitting

Split tensor rows across GPUs:

```bash
llama-server -m model.gguf \
  --split-mode row \
  --tensor-split 1,1,1,1 \
  --n-gpu-layers 99
```

**Use cases:**
- Very large models (70B+)
- Multiple smaller GPUs
- Better load balancing

### Tensor Split Ratios

**Uneven split (larger GPU gets more):**
```bash
# GPU 0: 75%, GPU 1: 25%
llama-server --tensor-split 3,1
```

**Three GPUs:**
```bash
# GPU 0: 50%, GPU 1: 30%, GPU 2: 20%
llama-server --tensor-split 5,3,2
```

### Main GPU Selection

Specify primary GPU for intermediates:

```bash
llama-server -m model.gguf \
  --main-gpu 0 \
  --tensor-split 1,1
```

**Useful when:**
- One GPU has more VRAM
- Using row split mode
- Processing large batches

## CUDA-Specific Configuration

### Compute Capability Override

If auto-detection fails:

```bash
# RTX 3080 (8.6) + RTX 4090 (8.9)
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="86;89"
```

**Find your compute capability:** https://developer.nvidia.com/cuda-gpus

### CUDA Environment Variables

**Hide specific GPUs:**
```bash
CUDA_VISIBLE_DEVICES="-0" llama-server ...  # Hide first GPU
CUDA_VISIBLE_DEVICES="1,2" llama-server ...  # Use only GPUs 1 and 2
```

**Enable unified memory (Linux):**
```bash
GGML_CUDA_ENABLE_UNIFIED_MEMORY=1 llama-server ...
```

Prevents crash when VRAM exhausted by swapping to RAM.

**Increase CUDA command buffer:**
```bash
CUDA_SCALE_LAUNCH_QUEUES=4x llama-server ...
```

Beneficial for multi-GPU pipeline parallelism.

**Force FP32 compute in cuBLAS:**
```bash
GGML_CUDA_FORCE_CUBLAS_COMPUTE_32F=1 llama-server ...
```

Prevents numerical overflow on GeForce cards (slower).

### CUDA Performance Tuning

**Force custom MMQ kernels:**
```bash
cmake -B build -DGGML_CUDA=ON -DGGML_CUDA_FORCE_MMQ=ON
```

Lower VRAM usage, slower for large batches.

**Force cuBLAS:**
```bash
cmake -B build -DGGML_CUDA=ON -DGGML_CUDA_FORCE_CUBLAS=ON
```

Faster prompt processing on datacenter GPUs, higher VRAM.

**Peer access batch size:**
```bash
cmake -B build -DGGML_CUDA=ON -DGGML_CUDA_PEER_MAX_BATCH_SIZE=256
```

Enable peer access for larger batches (requires NVLink or Linux).

## Metal (Apple Silicon) Configuration

### Automatic Offloading

Metal enabled by default on macOS:

```bash
llama-server -m model.gguf --n-gpu-layers 99
```

### Disable Metal

```bash
# At build time
cmake -B build -DGGML_METAL=OFF

# At runtime
llama-server --n-gpu-layers 0
```

### Memory Pressure Handling

macOS automatically manages memory pressure:
- System swaps less-used data to RAM
- May cause slowdown but prevents crashes

**Force model in RAM:**
```bash
llama-server -m model.gguf --mlock
```

## HIP (AMD GPU) Configuration

### ROCm Setup

```bash
# Build with HIP support
cmake -B build -DGGML_HIP=ON

# Run with AMD GPU
llama-server -m model.gguf --n-gpu-layers 99
```

### Multiple AMD GPUs

```bash
# Split across two AMD GPUs
llama-server -m model.gguf \
  --tensor-split 1,1 \
  --n-gpu-layers 99
```

## Vulkan Configuration

### Build with Vulkan

```bash
cmake -B build -DGGML_VULKAN=ON
cmake --build build
```

### Runtime Configuration

```bash
# List Vulkan devices
llama-server --list-devices

# Use Vulkan GPU
llama-server -m model.gguf --device vulkan0
```

## SYCL (Intel GPU) Configuration

### oneAPI Setup

```bash
# Source oneAPI environment
source /opt/intel/oneapi/setvars.sh

# Build with SYCL
cmake -B build -DGGML_SYCL=ON

# Run with Intel GPU
llama-server -m model.gguf --n-gpu-layers 99
```

See [SYCL.md](../../docs/backend/SYCL.md) for detailed setup.

## Device Selection

### Explicit Device Assignment

```bash
# Use specific devices
llama-server -m model.gguf \
  --device gpu0,gpu1 \
  --n-gpu-layers 99

# Mix CPU and GPU
llama-server --device cpu,gpu0
```

### Device List Format

| Device | Description |
|--------|-------------|
| `cpu` | CPU backend |
| `gpu0`, `gpu1`, ... | CUDA/HIP/Vulkan devices by index |
| `metal` | Metal (Apple Silicon) |
| `none` | Disable offloading |

## Memory Optimization

### KV Cache Quantization

Reduce VRAM for large contexts:

```bash
llama-server -m model.gguf \
  --cache-type-k q4_0 \
  --cache-type-v q4_0
```

**Available types:** `f16` (default), `q8_0`, `q4_0`, `q4_1`, `iq4_nl`

**Memory savings:** Up to 75% for KV cache

### Context Size Adjustment

Reduce context if VRAM limited:

```bash
llama-server -m model.gguf -c 2048  # Smaller context
```

### Fit Mode

Auto-adjust parameters to fit in memory:

```bash
# Auto-fit to available VRAM
llama-server -m model.gguf --fit on

# Target specific VRAM margin (MiB)
llama-server --fit-target 2048

# Minimum context size for --fit
llama-server --fit-ctx 4096
```

### MoE CPU Offloading

Keep expert weights on CPU:

```bash
# All MoE weights on CPU
llama-server -m mixtral.gguf --cpu-moe

# First N MoE layers on CPU
llama-server --n-cpu-moe 8
```

## Monitoring and Debugging

### VRAM Usage

**NVIDIA:**
```bash
nvidia-smi
```

**AMD:**
```bash
rocm-smi
```

**Intel:**
```bash
intel_gpu_top
```

### llama.cpp Statistics

Enable performance logging:

```bash
llama-server -m model.gguf --perf
```

**Output includes:**
- Prompt processing time
- Token generation time
- Tokens per second
- VRAM/RAM usage

### Slot Monitoring

```bash
curl http://localhost:8080/slots
```

Shows per-slot memory and timing statistics.

### Prometheus Metrics

```bash
llama-server --metrics
curl http://localhost:8080/metrics
```

Includes GPU utilization and memory metrics.

## Troubleshooting

### "Out of VRAM" Error

**Symptoms:** Server crashes or fails to start

**Solutions:**
1. Reduce `--n-gpu-layers`
2. Use smaller quantization (Q4_K_M instead of Q8_0)
3. Enable KV cache quantization
4. Use `--fit on` for auto-adjustment
5. Enable unified memory (CUDA): `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1`

### "Cannot allocate memory"

**Cause:** System RAM exhausted

**Solutions:**
- Reduce context size: `-c 2048`
- Disable mmap: `--no-mmap` (uses more RAM but faster loading)
- Add swap space
- Use `--mlock` to prevent swapping

### Slow Performance on GPU

**Possible causes:**
1. Not enough layers offloaded
2. Thermal throttling
3. CPU bottleneck for prompt processing

**Diagnosis:**
```bash
llama-server --perf  # Check timing breakdown
nvidia-smi -l 1      # Monitor GPU utilization
```

**Solutions:**
- Increase `--n-gpu-layers`
- Improve cooling
- Enable BLAS for prompt processing: `-DGGML_BLAS=ON`
- Use Flash Attention: `--flash-attn on`

### Multi-GPU Load Imbalance

**Symptoms:** One GPU at 100%, others idle

**Solutions:**
- Adjust `--tensor-split` ratios
- Use row split mode: `--split-mode row`
- Set `--main-gpu` to balance intermediates

### CUDA Initialization Failed

**Causes:**
- Incompatible CUDA version
- Driver too old
- Compute capability not supported

**Solutions:**
```bash
# Check CUDA version
nvcc --version

# Check driver
nvidia-smi

# Rebuild with correct architectures
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="86;89"
```

## Performance Benchmarks

### Single GPU (RTX 4090, 24 GB)

| Model | Quant | Layers | Tokens/sec | VRAM |
|-------|-------|--------|------------|------|
| Llama 3.1 8B | Q4_K_M | 33 | 280 | 6 GB |
| Llama 3.1 70B | Q4_K_M | 80 | 45 | 42 GB* |
| Mixtral 8x7B | Q4_K_M | 64 | 85 | 48 GB* |

*Requires CPU offloading for some layers

### Dual GPU (2x RTX 3090, 24 GB each)

| Model | Quant | Split | Tokens/sec | Total VRAM |
|-------|-------|-------|------------|------------|
| Llama 3.1 70B | Q4_K_M | 1,1 | 55 | 48 GB |
| Command R+ | Q4_K_M | 1,1 | 42 | 48 GB |

### Apple Silicon (M2 Ultra, 128 GB)

| Model | Quant | Layers | Tokens/sec | Memory |
|-------|-------|--------|------------|--------|
| Llama 3.1 8B | Q4_K_M | 33 | 180 | 7 GB |
| Llama 3.1 70B | Q4_K_M | 80 | 35 | 45 GB |
| Command R+ | Q5_K_M | 64 | 28 | 52 GB |

## Best Practices

1. **Start with auto-detection:** `--n-gpu-layers auto`
2. **Monitor VRAM usage:** Leave 1-2 GB headroom
3. **Use KV cache quantization** for large contexts
4. **Enable Flash Attention** if supported: `--flash-attn on`
5. **Test different tensor splits** for multi-GPU setups
6. **Profile with --perf** before optimizing
7. **Keep drivers updated** for best compatibility
8. **Use unified memory** as safety net (CUDA Linux)

## Advanced Configuration

### Tensor Override

Force specific tensors to CPU/GPU:

```bash
llama-server -m model.gguf \
  --override-tensor 'blk.30.*=cpu,blk.31.*=cpu'  # Last 2 layers on CPU
```

### NUMA Optimization

For systems with multiple CPU sockets:

```bash
# Distribute across NUMA nodes
llama-server --numa distribute

# Isolate to single NUMA node
llama-server --numa isolate

# Use numactl configuration
llama-server --numa numactl
```

### Direct I/O

Bypass page cache for faster loading:

```bash
llama-server -m model.gguf --direct-io
```

Useful for very large models on systems with ample RAM.
