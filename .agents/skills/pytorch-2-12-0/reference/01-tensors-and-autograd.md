# Tensors and Autograd

## Contents
- Tensor Creation
- Tensor Properties
- Tensor Operations
- Broadcasting
- Device Placement
- Autograd Mechanics
- Custom autograd.Function

## Tensor Creation

Tensors are n-dimensional arrays supporting automatic differentiation and hardware acceleration.

```python
import torch

# From data
x = torch.tensor([1, 2, 3])                    # int64
y = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float32)

# With shape
z = torch.randn(2, 3, 4)                       # random normal
zeros = torch.zeros(5, 5)
ones = torch.ones(3, 4)
empty = torch.empty(10, 10)                    # uninitialized

# From other tensors
w = x.clone()
v = x.new_ones(5)                               # same dtype/device as x

# Sequences
seq = torch.arange(0, 10, 2)                   # [0, 2, 4, 6, 8]
linspace = torch.linspace(0, 1, steps=100)
eye = torch.eye(3)                              # identity matrix
```

## Tensor Properties

Every tensor has key attributes:

| Property | Description |
|----------|-------------|
| `.shape` / `.size()` | Dimensions as `torch.Size` |
| `.dtype` | Data type (e.g., `torch.float32`) |
| `.device` | Device placement (e.g., `cuda:0`, `cpu`) |
| `.requires_grad` | Whether gradients are tracked |
| `.grad` | Accumulated gradient tensor |
| `.ndim` / `.dim()` | Number of dimensions |
| `.numel()` | Total element count |

Common dtypes: `torch.float32`, `torch.float16`, `torch.bfloat16`, `torch.int64`, `torch.bool`, `torch.complex64`.

## Tensor Operations

Tensors support arithmetic, linear algebra, and element-wise operations. Most ops are overloaded operators or functions in `torch`:

```python
a = torch.randn(3, 4)
b = torch.randn(3, 4)

# Arithmetic
c = a + b          # element-wise add
d = a * b          # element-wise mul
e = a @ b.T        # matrix multiply
f = a.pow(2)       # element-wise power

# Reduction
total = a.sum()
mean = a.mean(dim=1, keepdim=True)
max_val, max_idx = a.max(dim=-1)

# Linear algebra
q, r = torch.linalg.qr(a.T @ a)
eigenvalues = torch.linalg.eigvalsh(a.T @ a)
```

Batched `linalg.eigh` on CUDA is up to 100x faster in 2.12 due to cuSolver backend selection (syevj_batched kernel).

## Broadcasting

Broadcasting automatically expands smaller tensors to match larger ones along dimensions of size 1:

```python
a = torch.randn(3, 4)       # shape (3, 4)
b = torch.randn(1, 4)       # shape (1, 4) → broadcasts to (3, 4)
c = torch.randn(4)          # shape (4,) → broadcasts to (3, 4)

result = a + b + c          # all broadcast together
```

Rules: dimensions are aligned right-to-left; a dimension can broadcast if it is 1 or absent in one operand.

## Device Placement

Move tensors between devices with `.to()`:

```python
x_cpu = torch.randn(100, 100)
x_cuda = x_cpu.to("cuda")
x_xpu = x_cpu.to("xpu")
x_mps = x_cpu.to("mps")

# Or at creation
x = torch.randn(100, 100, device="cuda")

# Check availability
if torch.cuda.is_available():
    device = "cuda"
elif torch.xpu.is_available():
    device = "xpu"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"
```

Use `torch.no_grad()` to disable gradient tracking during inference:

```python
with torch.no_grad():
    predictions = model(inputs)
```

## Autograd Mechanics

Autograd builds a dynamic computation graph by recording operations on tensors with `requires_grad=True`:

```python
x = torch.randn(3, 3, requires_grad=True)
y = x.pow(2)
z = y.sum()
z.backward()
print(x.grad)  # 2*x
```

Key concepts:
- **Leaf tensors**: Created by the user (not by an operation). Only leaf tensors accumulate `.grad`.
- **Computational graph**: Built dynamically during forward pass; freed after `backward()` unless `retain_graph=True`.
- **Gradient accumulation**: Gradients accumulate in `.grad`; call `optimizer.zero_grad()` or `tensor.grad.zero_()` to clear.

`torch.autograd.Function` for custom differentiable operations:

```python
class MyLinear(torch.autograd.Function):
    @staticmethod
    def forward(ctx, input, weight, bias):
        ctx.save_for_backward(input, weight, bias)
        output = input @ weight.t() + bias
        return output

    @staticmethod
    def backward(ctx, grad_output):
        input, weight, bias = ctx.saved_tensors
        grad_input = grad_output @ weight
        grad_weight = grad_output.t() @ input
        grad_bias = grad_output.sum(dim=0)
        return grad_input, grad_weight, grad_bias
```

## Custom autograd.Function

Use `torch.autograd.Function` when you need a custom backward pass not covered by existing operations. Register with `@staticmethod` for both `forward` and `backward`. Save intermediate values with `ctx.save_for_backward()` for use in the backward pass.

For simpler cases, compose existing PyTorch operations instead — they already have optimized kernels and correct gradients.
