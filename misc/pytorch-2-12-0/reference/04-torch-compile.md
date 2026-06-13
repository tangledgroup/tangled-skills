# torch.compile

## Contents
- Basics and Modes
- Programming Model
- Graph Breaks
- Dynamic Shapes
- CUDA Graphs Integration
- torch.accelerator.Graph API
- Performance Profiling
- Troubleshooting

## Basics and Modes

`torch.compile` optimizes model execution by tracing the computation graph, lowering to ATen IR, and generating optimized kernels via TorchInductor:

```python
import torch

model = MyModel()
compiled_model = torch.compile(model)
outputs = compiled_model(inputs)  # first call triggers compilation
```

Modes control the optimization strategy:

| Mode | Behavior |
|------|----------|
| `"default"` | Balanced speed and memory (recommended starting point) |
| `"reduce-overhead"` | Minimizes Python overhead, best for small models/batches |
| `"max-autotune"` | Searches for best kernel configurations, longest warmup |
| `"max-autotune-no-cudagraphs"` | Like max-autotune without CUDA Graph capture |

Disable compilation temporarily:

```python
from torch.compiler import disable

with disable():
    outputs = compiled_model(inputs)  # runs uncompiled
```

## Programming Model

TorchDynamo traces Python bytecode to build a graph of PyTorch operations. The graph is then lowered through multiple IRs (Graph → ATen → Inductor) before generating optimized code.

Key constraints:
- Traced functions must be structurally stable (same control flow across calls)
- Data-dependent control flow causes graph breaks
- Global mutable state can trigger recompilation

Check if currently compiling:

```python
if torch.compiler.is_compiling():
    # inside a torch.compile trace — use tracing-compatible code
    pass
```

## Graph Breaks

Graph breaks occur when TorchDynamo cannot capture an operation, falling back to eager execution for that region. Common causes:

- `print()`, `assert`, or other side effects
- Data-dependent control flow (`if x.sum() > 0`)
- Unsupported Python operations on tensors
- Third-party library calls

Minimize graph breaks by:
- Using `torch.cond` for data-dependent branching (supported in 2.12)
- Moving I/O outside the compiled function
- Keeping model code pure (no side effects in forward)

Debug recompilation with logging:

```python
import torch._logging
torch._logging.set_logs(recompiles="default")
```

## Dynamic Shapes

Enable dynamic shapes to handle varying input sizes without recompilation:

```python
compiled = torch.compile(model, dynamic=True)
# Works with different batch sizes
out1 = compiled(torch.randn(8, 3, 224, 224))
out2 = compiled(torch.randn(16, 3, 224, 224))
```

Use `torch.export.Dim` for fine-grained control:

```python
from torch.export import Dim

batch_dim = Dim("batch", min=1, max=128)
sym_shape = torch.export.Dim("seq", min=10, max=1000)

exported = torch.export.export(
    model,
    (torch.randn(1, 50),),
    dynamic_shapes={0: {"batch_size": batch_dim, "seq_len": sym_shape}},
)
```

## CUDA Graphs Integration

CUDA Graphs eliminate CPU overhead by recording kernel launches and replaying them. In 2.12, `torch.cond` control flow can be captured within CUDA Graphs using CUDA 12.4's conditional IF nodes:

```python
# torch.cond inside CUDA Graph (new in 2.12)
@torch.compile(backend="cudagraphs")
def step(x, condition):
    return torch.cond(condition, lambda x: x * 2, lambda x: x + 1, [x])
```

CUDA Graph kernel annotations (`enable_annotations=True`) inject metadata into captured graphs for profiling with Perfetto/Chrome traces.

## torch.accelerator.Graph API

New in 2.12 — device-agnostic graph capture and replay across CUDA, XPU, and out-of-tree backends:

```python
import torch.accelerator as ta

# Device-agnostic graph capture
graph = ta.Graph()
with graph.capture():
    output = model(input)

# Replay
with graph.replay():
    result = model(new_input)
```

Each backend registers its own `GraphImplInterface` implementation. Stream context now exposes `is_capturing()` as a backend-agnostic alternative to device-specific checks.

## Performance Profiling

Profile compiled models with the PyTorch Profiler:

```python
from torch.profiler import profile, ProfilerActivity

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    profile_memory=True,
) as prof:
    for batch in loader:
        outputs = compiled_model(batch)
        prof.step()

print(prof.key_averages().table(sort_by="cuda_time_total"))
```

Use `torch.utils.benchmark` for precise micro-benchmarks:

```python
import torch.utils.benchmark as benchmark

t = benchmark.Timer(
    stmt="model(x)",
    globals={"model": compiled_model, "x": x},
)
print(t.blocked_time)
```

## Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| Recompilation every step | Check for changing tensor shapes, dtypes, or module structure |
| Graph break on control flow | Use `torch.cond` or restructure to avoid data-dependent branching |
| OOM during compilation | Use `mode="reduce-overhead"` or reduce autotune search space |
| Numerical mismatch vs eager | Check fused operations; use FMA-based lowering for parity |
| Slow first iteration | Compilation happens on first call — warm up before benchmarking |

Set `TORCH_LOGS="+dynamo,inductor,recompiles"` for detailed compiler logging.

## Gradient Checkpointing with torch.compile

Combine activation checkpointing with torch.compile for memory-efficient training of large models:

```python
from torch.utils.checkpoint import checkpoint

class CheckpointedBlock(torch.nn.Module):
    def __init__(self, block):
        super().__init__()
        self.block = block

    def forward(self, x):
        return checkpoint(self.block, x)

# Works with torch.compile — Dynamo captures the checkpoint boundary
model = torch.compile(model_with_checkpointing)
```
