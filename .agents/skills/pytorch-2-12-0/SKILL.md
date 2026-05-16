---
name: pytorch-2-12-0
description: >-
  Complete toolkit for PyTorch 2.12 providing n-dimensional tensors, automatic
  differentiation, neural network modules, data loading, torch.compile optimization,
  torch.export serialization, and comprehensive torch.optim coverage (15 algorithms,
  LR schedulers, SWA/EMA). Use when building deep learning models, training neural
  networks on CPU/CUDA/XPU/MPS/ROCm, selecting optimization algorithms (SGD, AdamW,
  Adafactor, Muon, etc.), configuring learning rate schedules, compiling models with
  torch.compile, exporting models with torch.export, or implementing distributed
  training with DDP/FSDP/tensor parallelism.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.3.0"
tags:
  - pytorch
  - deep-learning
  - tensors
  - autograd
  - torch-compile
  - torch-export
  - neural-networks
category: ml-ai
external_references:
  - https://pytorch.org/
  - https://github.com/pytorch/pytorch/tree/v2.12.0
  - https://docs.pytorch.org/docs/2.12/optim.html
---

# PyTorch 2.12.0

## Overview

PyTorch is a flexible deep learning framework built around n-dimensional tensors
with automatic differentiation, dynamic computation graphs, and hardware acceleration
across CUDA, ROCm, Intel XPU, Apple MPS, and CPU. Version 2.12 introduces the
device-agnostic `torch.accelerator.Graph` API, Microscaling (MX) quantization
export support, fused Adagrad optimizer, `torch.cond` within CUDA Graphs, and
significant performance improvements including up to 100x faster batched
eigendecomposition on CUDA.

PyTorch's core components: **Tensors** for data, **Autograd** for gradients,
**nn.Module** for model architecture, **DataLoader** for data pipelines,
**torch.compile** for optimization, and **torch.export** for serialization.

## When to Use

- Building and training neural networks (CNNs, RNNs, Transformers, diffusion models)
- Research prototyping with dynamic computation graphs
- Optimizing model performance with `torch.compile`
- Exporting models for production deployment with `torch.export`
- Multi-GPU/multi-node distributed training with DDP, FSDP, or tensor parallelism
- Quantizing models for edge deployment or reduced inference cost
- Custom operator development with `torch.library`

## Core Concepts

### Tensors

The fundamental data structure — n-dimensional arrays with device placement, dtype, and gradient tracking:

```python
import torch

x = torch.randn(3, 4, device="cuda", dtype=torch.float32)
y = torch.tensor([[1, 2], [3, 4]], requires_grad=True)
z = x @ y.to(x.device, x.dtype)
```

Key properties: `.shape`, `.dtype`, `.device`, `.requires_grad`, `.grad`.

### Autograd

Automatic differentiation tracks operations on tensors with `requires_grad=True` and builds a dynamic computation graph. Call `.backward()` to compute gradients:

```python
x = torch.randn(2, 3, requires_grad=True)
y = x.pow(2).sum()
y.backward()
print(x.grad)  # dy/dx
```

### nn.Module

The base class for all neural network components. Subclass `nn.Module` to define models, use `nn.Parameter` for trainable weights, and register submodules as instance attributes:

```python
class SimpleNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(10, 5)
        self.relu = torch.nn.ReLU()

    def forward(self, x):
        return self.relu(self.fc(x))
```

### DataLoader

Efficient data pipelines with batching, shuffling, and parallel loading:

```python
from torch.utils.data import DataLoader, TensorDataset

dataset = TensorDataset(torch.randn(1000, 64), torch.randint(0, 10, (1000,)))
loader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4)
```

## Usage Examples

### Basic Training Loop

```python
model = SimpleNet()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = torch.nn.CrossEntropyLoss()

for epoch in range(10):
    for inputs, targets in loader:
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
```

### torch.compile — One-Line Optimization

Wrap a module or function with `torch.compile` to auto-optimize via TorchInductor:

```python
compiled_model = torch.compile(model, mode="max-autotune")
# Use identical to the original model
outputs = compiled_model(inputs)
```

Modes: `"default"` (balanced), `"reduce-overhead"` (fast forward pass), `"max-autotune"` (best throughput, longer warmup).

### torch.export — Model Serialization

Export a model to a portable graph format for deployment:

```python
import torch.export

example_input = torch.randn(1, 10)
exported_program = torch.export.export(model, (example_input,))
exported_program.save("model.pt2")
loaded = torch.export.load("model.pt2")
```

### Automatic Mixed Precision

Reduce memory and accelerate training with FP16/BF16:

```python
from torch.amp import autocast
from torch.cuda.amp import GradScaler

scaler = GradScaler()
with autocast(device_type="cuda", dtype=torch.bfloat16):
    outputs = model(inputs)
    loss = criterion(outputs, targets)
scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### Checkpoint Save and Load

```python
# Save checkpoint
checkpoint = {
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "loss": loss.item(),
}
torch.save(checkpoint, "checkpoint.pth")

# Resume training
ckpt = torch.load("checkpoint.pth", weights_only=True)
model.load_state_dict(ckpt["model_state_dict"])
optimizer.load_state_dict(ckpt["optimizer_state_dict"])
```

### Distributed Training (DDP) — Minimal Example

```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
dist.init_process_group("nccl")
model = DDP(MyModel().cuda(dist.get_rank()), device_ids=[dist.get_rank()])
# Training loop is identical to single-GPU
```

## Advanced Topics

**Tensors & Autograd**: Tensor operations, broadcasting, custom autograd functions → [Tensors and Autograd](reference/01-tensors-and-autograd.md)

**Neural Network API**: nn.Module patterns, layers, loss functions, optimizers, weight initialization → [Neural Network API](reference/02-neural-network-api.md)

**Data Loading**: Datasets, DataLoaders, transforms, multiprocessing best practices → [Data Loading](reference/03-data-loading.md)

**torch.compile**: TorchDynamo tracing, graph breaks, dynamic shapes, CUDA Graphs, torch.accelerator.Graph → [torch.compile](reference/04-torch-compile.md)

**torch.export**: Export workflow, IR specification, control flow operators, MX quantization export, AOTInductor → [torch.export](reference/05-torch-export.md)

**Distributed Training**: DDP, FSDP, ProcessGroups, tensor parallelism, pipeline parallelism, distributed checkpointing → [Distributed Training](reference/06-distributed-training.md)

**Quantization & AMP**: Automatic mixed precision, PTQ, QAT, Microscaling (MX) formats, fused optimizers → [Quantization and AMP](reference/07-quantization-and-amp.md)

**Accelerators & Platforms**: CUDA, ROCm, Intel XPU, Apple MPS, device management, profiler integration → [Accelerators and Platforms](reference/08-accelerators-and-platforms.md)

**Optimizers & Scheduling**: All 15 torch.optim algorithms (SGD, Adam, AdamW, RMSprop, Adafactor, Muon, etc.), foreach/fused implementations, LR schedulers, SWA/EMA, optimizer hooks → [Optimizers and Scheduling](reference/09-optimizers-and-scheduling.md)
