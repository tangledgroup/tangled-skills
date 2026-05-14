# Accelerators and Platforms

## Contents
- CUDA
- ROCm (AMD)
- Apple MPS
- Intel XPU
- Device Management
- Profiler Integration

## CUDA

PyTorch's primary GPU backend. Default binary wheels ship with CUDA 13.0; CUDA 12.6 remains supported for older architectures (Pascal, Volta); CUDA 12.8 wheel is deprecated in 2.12.

```python
import torch

# Check availability
print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0))

# Multi-GPU
x = torch.randn(100, device="cuda:0")
y = torch.randn(100, device="cuda:1")
z = x + y.to(x.device)
```

**CUDA 12.6 minimum for source builds** (new in 2.12):

```bash
CUDA_HOME=/usr/local/cuda-12.6 python setup.py develop
```

### CUDA Graph Kernel Annotations (new in 2.12)

Inject annotation metadata into captured CUDA graphs for profiling:

```python
with torch.cuda.graph(storage, enable_annotations=True) as graph:
    # operations are annotated with collective names, process groups, message sizes
    output = model(input)

# Post-process with companion script
# python -m torch.cuda._annotate_cuda_graph_trace <trace_file>
```

Annotations appear in Perfetto/Chrome profiler traces, making it easier to identify what each kernel in a replayed graph is doing.

### CUDA Green Contexts (new in 2.12)

Experimental workqueue limit for GPU resource partitioning:

```python
# Constrain concurrent work submissions within a green context
# (experimental API — consult torch.cuda documentation for latest interface)
```

## ROCm (AMD)

PyTorch supports AMD GPUs via ROCm with feature parity growing each release:

```python
import torch
print(torch.version.hip)  # ROCm version
```

**New in 2.12:**
- **Expandable memory segments** (ROCm >= 7.02) — reduces fragmentation via virtual memory APIs, matching CUDA behavior
- **rocSHMEM support** — symmetric memory collective operations (`torch.ops.symm_mem.*`) for point-to-point, broadcast, all-to-all, and MoE-oriented 2D AllToAllv
- **hipSPARSELt enabled by default** (ROCm >= 7.12) — semi-structured (2:4) sparsity with FP8 input support on MI350X
- **FlexAttention pipelining** — two-stage Triton backend delivering 5-26% speedups across attention patterns on MI350X

## Apple MPS

Metal Performance Shaders backend for Apple Silicon (M1/M2/M3/M4):

```python
import torch
print(torch.backends.mps.is_available())

device = torch.device("mps")
x = torch.randn(100, 100, device=device)
```

**New in 2.12:**
- **Metal-4 offline shader compilation** — binary wheels ship with ahead-of-time-compiled Metal-4 shaders, eliminating runtime compilation overhead on first run
- `torch._C._mps_loadMetallib` API for loading pre-compiled `.metallib` blobs directly

**Breaking change (2.12):** All MPS tensors now use unified memory unconditionally (previously could be device-only or unified).

## Intel XPU

Intel GPU support via oneAPI:

```python
import torch
print(torch.xpu.is_available())

device = torch.device("xpu")
x = torch.randn(100, 100, device=device)
```

**New in 2.12:**
- `torch.accelerator.Graph` API includes XPU backend support
- FMA-based addcdiv lowering for numerical parity with CUDA eager execution
- Cross-backend stream management via `is_capturing()`

## Device Management

PyTorch provides a unified accelerator abstraction via `torch.accelerator`:

```python
import torch.accelerator as ta

# Query available devices
print(ta.list_devices())

# Device-agnostic operations
with ta.device("cuda" if torch.cuda.is_available() else "cpu"):
    x = torch.randn(100)
```

Accelerator hooks allow custom device integration:
- **Device Management** — register new device types
- **Accelerator Hooks** — intercept tensor movement between devices
- **Guard** — safety checks for device operations
- **Autoload Mechanism** — automatic backend initialization
- **Operator Registration** — register kernels for custom accelerators

## Profiler Integration

Cross-backend profiling with `torch.profiler`:

```python
from torch.profiler import profile, ProfilerActivity, schedule

profiler = profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=2),
    on_trace_ready=torch.profiler.tensorboard_trace_handler("./profiler_logs"),
    record_shapes=True,
    profile_memory=True,
)

with profiler:
    for step, (inputs, targets) in enumerate(loader):
        profiler.step()
        # training loop...
```

Profiler integration is part of the accelerator framework — custom backends can register their own activity types for unified tracing.
