# torch.export

## Contents
- Export Workflow
- Programming Model
- IR Specification
- PT2 Archive Format
- Control Flow Operators
- Microscaling (MX) Quantization Export
- AOTInductor

## Export Workflow

`torch.export` serializes a PyTorch model into a portable, device-agnostic graph format. It is the replacement for TorchScript (`torch.jit.trace` / `torch.jit.script`), which was deprecated in 2.10:

```python
import torch
import torch.export

model = MyModel().eval()
example_input = torch.randn(1, 3, 224, 224)

# Export
exported_program = torch.export.export(model, (example_input,))

# Save to disk
exported_program.save("model.pt2")

# Load and run
loaded = torch.export.load("model.pt2")
output = loaded.module()(torch.randn(1, 3, 224, 224))
```

## Programming Model

Export captures the model's forward pass as a traced graph. The exported program contains:
- **Module**: A runnable version of the model
- **Graph**: The computation graph in ATen IR
- **State dict**: Parameters and buffers

Access the internal structure:

```python
exported = torch.export.export(model, (example_input,))

# Run with the exported module
output = exported.module()(input)

# Inspect the graph
print(exported.graph_module.graph)

# Access state dict
state_dict = exported.state_dict
```

Export supports dynamic shapes via `dynamic_shapes`:

```python
from torch.export import Dim

batch_dim = Dim("batch_size", min=1, max=128)
exported = torch.export.export(
    model,
    (example_input,),
    dynamic_shapes=[{"batch_size": batch_dim}],
)
```

## IR Specification

The export IR is ATen-level — a sequence of `torch.ops.aten.*` operations. This provides:
- **Portability**: Runs on any device with the operators implemented
- **Transformability**: Apply graph transformations before deployment
- **Inspectability**: Readable computation graph for debugging

Key IR nodes:
- `call_function`: ATen operations (e.g., `aten.add`, `aten.linear`)
- `call_method`: Tensor methods
- `placeholder`: Input parameters
- `get_attr`: Module attributes (parameters, buffers)
- `output`: Return values

## PT2 Archive Format

The `.pt2` file is a self-contained archive containing:
- Computation graph (serialized IR)
- Parameters and buffers
- Dynamic shape constraints
- Metadata

```python
# Save
exported_program.save("model.pt2")

# Load
loaded = torch.export.load("model.pt2")

# Run
output = loaded.module()(input_tensor)
```

PT2 is the standard format for model exchange between training and deployment systems. Use ExecuTorch for on-device inference from exported models.

## Control Flow Operators

Export supports higher-order control flow operators that capture branching and looping in the graph:

**torch.cond** — data-dependent conditional:

```python
import torch

def true_fn(x):
    return x * 2

def false_fn(x):
    return x + 1

x = torch.randn(3, 4)
condition = x.sum() > 0
result = torch.cond(condition, true_fn, false_fn, [x])
```

**torch.while_loop** — data-dependent loops:

```python
def cond(carry):
    x, i = carry
    return i < 10

def body(carry):
    x, i = carry
    return (x * 2, i + 1)

initial = (torch.ones(3), torch.tensor(0))
final_x, final_i = torch.while_loop(cond, body, initial)
```

**torch.scan** — functional fold/reduce over sequences:
**torch.map** — element-wise mapping with state

These operators enable exporting models with dynamic control flow, essential for autoregressive generation and variable-length processing.

## Microscaling (MX) Quantization Export

New in 2.12 — `torch.export.save` and `torch.export.load` now support Microscaling quantization formats (MXFP4, MXFP6, MXFP8). The `float8_e8m0fnu` dtype used for shared block-scale exponents is correctly serialized:

```python
import torch
import torch.export

# Model with MX quantization
quantized_model = apply_mx_quantization(model)  # your quantization pipeline

exported = torch.export.export(quantized_model, (example_input,))
exported.save("model-mx.pt2")

# Load and verify
loaded = torch.export.load("model-mx.pt2")
output = loaded.module()(input_tensor)
```

This unblocks the full export-to-deployment workflow for aggressively compressed models on cost-constrained or edge environments.

## AOTInductor

AOTInductor performs ahead-of-time compilation of exported programs to optimized C++/CUDA code:

```python
from torch._inductor.aot_inductor import aot_inductor
import torch.export

exported = torch.export.export(model, (example_input,))
compiled_module = aot_inductor(
    exported.module(),
    exported.graph_signature,
    example_inputs=(example_input,),
)
```

AOTInductor generates standalone C++ code with CUDA kernels, suitable for deployment without the PyTorch Python runtime. Use the AOTInductor minifier to debug compilation failures on minimal reproducing examples.
