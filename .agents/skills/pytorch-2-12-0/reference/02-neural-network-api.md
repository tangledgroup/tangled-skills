# Neural Network API

## Contents
- nn.Module Patterns
- Common Layers
- Loss Functions
- Activation Functions
- Optimizers
- Weight Initialization

## nn.Module Patterns

`nn.Module` is the base class for all neural network components. Register submodules as instance attributes in `__init__`, define the forward pass in `forward()`:

```python
class ResidualBlock(torch.nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.conv1 = torch.nn.Conv2d(channels, channels, 3, padding=1)
        self.conv2 = torch.nn.Conv2d(channels, channels, 3, padding=1)
        self.relu = torch.nn.ReLU()

    def forward(self, x):
        identity = x
        out = self.relu(self.conv1(x))
        out = self.conv2(out)
        return self.relu(out + identity)
```

Key methods:
- `.parameters()` — iterator over all trainable parameters
- `.named_modules()` — iterate over all submodules with names
- `.to(device)` — move all parameters/buffers to device
- `.train()` / `.eval()` — toggle training/inference mode (affects Dropout, BatchNorm)
- `.state_dict()` / `.load_state_dict()` — save/load model weights

Use `torch.nn.Sequential` for simple linear stacks:

```python
model = torch.nn.Sequential(
    torch.nn.Linear(784, 256),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.3),
    torch.nn.Linear(256, 10),
)
```

## Common Layers

**Linear (Fully Connected)**: `torch.nn.Linear(in_features, out_features, bias=True)`

**Convolution**: `torch.nn.Conv2d(in_channels, out_channels, kernel_size, stride=1, padding=0)`
- Also: `Conv1d`, `Conv3d`, `ConvTranspose2d`

**Normalization**:
- `torch.nn.BatchNorm2d(num_features)` — per-channel mean/variance normalization
- `torch.nn.LayerNorm(normalized_shape)` — normalize across feature dimensions
- `torch.nn.GroupNorm(num_groups, num_channels)`

**Recurrent**:
- `torch.nn.LSTM(input_size, hidden_size, num_layers=1, batch_first=True)`
- `torch.nn.GRU(input_size, hidden_size, ...)`

**Transformer**:
- `torch.nn.Transformer(d_model=512, nhead=8, num_encoder_layers=6, ...)`
- `torch.nn.MultiheadAttention(embed_dim, num_heads)`
- `torch.nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward)`

**Attention**:
- `torch.nn.functional.scaled_dot_product_attention(query, key, value, attn_mask=None, dropout_p=0.0)`
- FlexAttention for custom attention patterns (causal, sliding window, ALiBi)

**Embedding**:
- `torch.nn.Embedding(num_embeddings, embedding_dim, padding_idx=None)`
- `torch.nn.EmbeddingBag(num_embeddings, embedding_dim, mode='mean')` — for variable-length sequences

**Dropout and Regularization**:
- `torch.nn.Dropout(p=0.5)` — standard dropout
- `torch.nn.Dropout2d(p=0.5)` — drops entire feature maps
- `torch.nn.AlphaDropout(p=0.5)` — preserves mean/variance (compatible with BatchNorm)

**ModuleList and ModuleDict**:
Use these instead of Python lists/dicts so submodules are properly registered:

```python
self.layers = torch.nn.ModuleList([
    torch.nn.Linear(128, 64),
    torch.nn.ReLU(),
    torch.nn.Linear(64, 10)
])
for layer in self.layers:
    x = layer(x)
```

## Loss Functions

| Loss | Use Case |
|------|----------|
| `torch.nn.CrossEntropyLoss()` | Multi-class classification (logits + integer targets) |
| `torch.nn.MSELoss()` | Regression |
| `torch.nn.BCEWithLogitsLoss()` | Binary classification (logits + float targets) |
| `torch.nn.NLLLoss()` | Negative log likelihood (log-probabilities) |
| `torch.nn.L1Loss()` | Mean absolute error |
| `torch.nn.SmoothL1Loss()` | Huber loss, robust to outliers |

```python
criterion = torch.nn.CrossEntropyLoss(weight=torch.tensor([1.0, 5.0, 1.0]))  # class weights
loss = criterion(logits, targets)
```

## Activation Functions

Use via `torch.nn.functional` or as module instances:

```python
# As modules (registered in nn.Module)
self.relu = torch.nn.ReLU()
self.gelu = torch.nn.GELU()
self.swish = torch.nn.SiLU()

# Functional (inline, no parameter registration)
x = torch.nn.functional.relu(x)
x = torch.nn.functional.gelu(x)
```

Common activations: `ReLU`, `GELU`, `SiLU` (Swish), `LeakyReLU`, `Tanh`, `Sigmoid`, `Softmax`.

## Optimizers

All optimizers take model parameters and hyperparameters:

```python
import torch.optim as optim

# SGD with momentum
optimizer = optim.SGD(model.parameters(), lr=1e-2, momentum=0.9, weight_decay=1e-4)

# AdamW (decoupled weight decay)
optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-2)

# RMSprop
optimizer = optim.RMSprop(model.parameters(), lr=1e-3, alpha=0.9)

# Adagrad with fused kernel (new in 2.12)
optimizer = optim.Adagrad(model.parameters(), lr=1e-2, fused=True)
```

Fused optimizers (`fused=True`) perform the entire optimizer step in a single CUDA kernel, reducing kernel launch overhead and memory traffic. Supported: SGD, Adam, AdamW, Adagrad (new in 2.12).

Learning rate scheduling:

```python
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)
# or step-based
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)

for epoch in range(100):
    train_one_epoch()
    scheduler.step()
```

## Weight Initialization

Proper initialization improves convergence. Use `torch.nn.init`:

```python
import torch.nn.init as init

# Default nn.Linear uses Kaiming uniform
def __init__(self):
    self.fc = torch.nn.Linear(256, 128)
    init.xavier_uniform_(self.fc.weight)
    init.constant_(self.fc.bias, 0.0)

# Common initializers
init.kaiming_normal_(weight, mode='fan_in', nonlinearity='leaky_relu')
init.xavier_uniform_(weight)
init.normal_(weight, mean=0.0, std=0.01)
```

Default initializations in PyTorch layers are generally appropriate; customize only when defaults cause convergence issues.

## State Dict and Serialization

```python
# Save/load model weights
torch.save(model.state_dict(), "model.pth")
model.load_state_dict(torch.load("model.pth", weights_only=True))

# Partial loading (transfer learning)
pretrained = torch.load("pretrained.pth", weights_only=True)
model.load_state_dict(pretrained, strict=False)  # ignore missing/extra keys

# Save optimizer state too (for resuming training)
torch.save({
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
}, "checkpoint.pth")
```

**Parameters vs Buffers**: `nn.Parameter` registers trainable parameters (appear in `model.parameters()`). Use `model.register_buffer()` for non-trainable persistent state like BatchNorm's `running_mean` — buffers appear in `state_dict` but not in `model.parameters()`.
