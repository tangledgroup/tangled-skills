# Quantization and AMP

## Contents
- Automatic Mixed Precision (AMP)
- Dynamic Quantization
- Static Quantization
- Quantization-Aware Training (QAT)
- Microscaling (MX) Formats
- Fused Optimizers

## Automatic Mixed Precision (AMP)

AMP reduces memory usage and accelerates training by using FP16/BF16 for forward/backward passes while maintaining FP32 master weights:

```python
from torch.amp import autocast
from torch.cuda.amp import GradScaler

model = MyModel().cuda()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
scaler = GradScaler()

for inputs, targets in loader:
    optimizer.zero_grad()

    with autocast(device_type="cuda", dtype=torch.bfloat16):
        outputs = model(inputs)
        loss = criterion(outputs, targets)

    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

Key points:
- Use `torch.bfloat16` on Ampere+ GPUs (no underflow issues), `torch.float16` on older architectures
- `GradScaler` prevents gradient underflow by scaling loss before backward pass
- AMP works with `torch.compile` — wrap `autocast` around the compiled model's forward

## Dynamic Quantization

Post-training quantization applied at runtime — simplest form, no calibration needed:

```python
import torch.quantization as quantization

model.eval()
quantized_model = quantization.quantize_dynamic(
    model,
    {torch.nn.LSTM, torch.nn.Linear},  # layers to quantize
    dtype=torch.qint8,
)

# Run inference with quantized model
with torch.no_grad():
    output = quantized_model(input)
```

Best for models with large linear/LSTM layers where weights dominate memory. No accuracy calibration required but less control over quantization behavior.

## Static Quantization

Full INT8 quantization of both weights and activations, requiring a calibration step:

```python
import torch.quantization as quantization

# 1. Prepare model with observers
model.eval()
model.qconfig = quantization.default_qconfig("fbgemm")  # CPU
# model.qconfig = quantization.default_qconfig("qnnpack")  # mobile
quantization.prepare(model, inplace=True)

# 2. Calibrate with representative data
with torch.no_grad():
    for inputs, _ in calib_loader:
        model(inputs)

# 3. Convert to quantized model
quantized_model = quantization.convert(model, inplace=False)
```

Static quantization provides better accuracy and performance than dynamic quantization but requires a calibration dataset representative of inference data distribution.

## Quantization-Aware Training (QAT)

Simulate quantization effects during training for best accuracy retention:

```python
import torch.quantization as quantization

model.train()
model.qconfig = quantization.default_qat_qconfig("fbgemm")
qat_model = quantization.prepare_qat(model, inplace=False)

# Train normally — fake quantization nodes simulate INT8 behavior
for epoch in range(epochs):
    for inputs, targets in train_loader:
        optimizer.zero_grad()
        outputs = qat_model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

# Convert to real quantized model
qat_model.eval()
quantized_model = quantization.convert(qat_model, inplace=False)
```

QAT is recommended when post-training quantization causes unacceptable accuracy drop. The fake quant nodes are differentiable, allowing gradients to flow through the quantization simulation.

## Microscaling (MX) Formats

Microscaling quantization uses block-wise scaling for aggressive compression:

| Format | Precision | Use Case |
|--------|-----------|----------|
| MXFP4 | 4-bit mantissa + shared exponent | Maximum compression, latest GPUs |
| MXFP6 | 6-bit mantissa + shared exponent | Balanced compression/accuracy |
| MXFP8 | FP8_E4M3 with block scaling | NVIDIA Hopper+ tensor cores |

The shared block-scale exponent uses `float8_e8m0fnu` dtype. In 2.12, `torch.export.save/load` correctly serializes this dtype, enabling full export-to-deployment for MX-quantized models:

```python
import torch

# MXFP4 tensor with block scales
data = torch.tensor([...], dtype=torch.float8_e4m3fn)
scales = torch.tensor([...], dtype=torch.float8_e8m0fnu)

# Export the quantized model
exported = torch.export.export(mx_model, (example_input,))
exported.save("model-mxfp4.pt2")
```

## Fused Optimizers

Fused optimizers perform the entire update step in a single CUDA kernel:

```python
import torch.optim as optim

# All support fused=True on CUDA
optimizer = optim.SGD(model.parameters(), lr=1e-2, momentum=0.9, fused=True)
optimizer = optim.Adam(model.parameters(), lr=1e-3, fused=True)
optimizer = optim.AdamW(model.parameters(), lr=1e-3, fused=True)
optimizer = optim.Adagrad(model.parameters(), lr=1e-2, fused=True)  # new in 2.12
```

Fused variants reduce kernel launch overhead and memory traffic by combining gradient clipping, momentum update, weight decay, and parameter update into one kernel. Use `fused=True` whenever training on CUDA for measurable speedup, especially with many small parameter groups.
