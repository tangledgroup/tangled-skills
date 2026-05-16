# Optimizers and Learning Rate Scheduling

## Contents
- Optimizer Basics
- Construction and Parameter Groups
- Optimization Step Patterns
- Implementation Variants (for-loop / foreach / fused)
- Algorithm Reference
  - SGD
  - Adam / AdamW
  - Adadelta
  - Adafactor
  - Adagrad
  - Adamax
  - ASGD
  - LBFGS
  - Muon
  - NAdam
  - RAdam
  - RMSprop
  - Rprop
  - SparseAdam
- Optimizer Hooks
- Learning Rate Schedulers
- Weight Averaging (SWA and EMA)

## Optimizer Basics

`torch.optim` implements optimization algorithms that update model parameters based on computed gradients. All optimizers inherit from `torch.optim.Optimizer`.

**Standard training loop:**

```python
import torch.optim as optim

optimizer = optim.AdamW(model.parameters(), lr=1e-3)
criterion = torch.nn.CrossEntropyLoss()

for inputs, targets in loader:
    optimizer.zero_grad()
    outputs = model(inputs)
    loss = criterion(outputs, targets)
    loss.backward()
    optimizer.step()
```

## Construction and Parameter Groups

Construct an optimizer with an iterable of parameters and hyperparameters:

```python
# All parameters share same settings
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# Explicit parameter list
optimizer = optim.Adam([var1, var2], lr=0.0001)

# Named parameters (tuples of name, parameter)
optimizer = optim.SGD(model.named_parameters(), lr=0.01, momentum=0.9)
```

**Per-parameter options** — pass dicts instead of raw parameters to set different hyperparameters per group:

```python
# Different learning rates per sub-module
optimizer = optim.SGD([
    {'params': model.backbone.parameters(), 'lr': 1e-3},
    {'params': model.head.parameters(), 'lr': 1e-2},
], momentum=0.9)  # shared across all groups

# Exclude weight decay from biases (common in LLM training)
bias_params = [p for n, p in model.named_parameters() if 'bias' in n]
other_params = [p for n, p in model.named_parameters() if 'bias' not in n]
optimizer = optim.AdamW([
    {'params': other_params, 'weight_decay': 1e-2},
    {'params': bias_params, 'weight_decay': 0},
], lr=1e-4)
```

**Adding parameter groups dynamically:**

```python
# Freeze backbone, train new head from scratch
model.head = torch.nn.Linear(512, 10)
optimizer.add_param_group({'params': model.head.parameters(), 'lr': 1e-2})
```

## Optimization Step Patterns

**Standard step** — call after `loss.backward()`:

```python
for inputs, targets in loader:
    optimizer.zero_grad()
    loss = criterion(model(inputs), targets)
    loss.backward()
    optimizer.step()
```

**Closure-based step** — required by LBFGS and conjugate gradient methods that re-evaluate the function multiple times:

```python
for inputs, targets in loader:
    def closure():
        optimizer.zero_grad()
        loss = criterion(model(inputs), targets)
        loss.backward()
        return loss
    optimizer.step(closure)
```

## Implementation Variants (for-loop / foreach / fused)

Optimizers have multiple implementations for performance:

- **for-loop** — iterates parameters sequentially with Python loops. Baseline, most readable.
- **foreach** (multi-tensor) — combines parameters into batched tensor operations, reducing kernel launch overhead. Default for most optimizers.
- **fused** — single CUDA kernel performing the entire step. Fastest but newest; not all algorithms support it.

Performance: fused > foreach > for-loop.

```python
# Explicitly select implementation
optimizer = optim.Adam(model.parameters(), lr=1e-3, foreach=True)   # multi-tensor
optimizer = optim.Adam(model.parameters(), lr=1e-3, fused=True)     # single kernel (CUDA)
optimizer = optim.SGD(model.parameters(), lr=0.01, differentiable=True)  # graph-compatible
```

**Available implementations per algorithm:**

| Algorithm | Default | foreach | fused |
|-----------|---------|---------|-------|
| SGD | foreach | yes | yes (CUDA stable, CPU/MPS beta) |
| Adam | foreach | yes | yes (CUDA stable, CPU/MPS beta) |
| AdamW | foreach | yes | yes (CUDA stable, CPU/MPS beta) |
| Adadelta | foreach | yes | no |
| Adafactor | for-loop | no | no |
| Adagrad | foreach | yes | yes (CPU only, beta) |
| Adamax | foreach | yes | no |
| ASGD | foreach | yes | no |
| LBFGS | for-loop | no | no |
| Muon | for-loop | no | no |
| NAdam | foreach | yes | no |
| RAdam | foreach | yes | no |
| RMSprop | foreach | yes | no |
| Rprop | foreach | yes | no |
| SparseAdam | for-loop | no | no |

## Algorithm Reference

### SGD (Stochastic Gradient Descent)

`optim.SGD(params, lr, momentum=0, dampening=0, weight_decay=0, nesterov=False, maximize=False, foreach=None, differentiable=False)`

Basic gradient descent with optional momentum. Most configurable optimizer.

```python
# Plain SGD
optimizer = optim.SGD(model.parameters(), lr=0.01)

# SGD with Nesterov momentum
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9, nesterov=True)

# SGD with weight decay (L2 regularization)
optimizer = optim.SGD(model.parameters(), lr=0.01, weight_decay=1e-4)
```

Parameters:
- `momentum` — coefficient for gradient accumulation (0 = no momentum)
- `dampening` — reduces the impact of momentum when non-zero
- `nesterov` — enables Nesterov accelerated gradient
- `maximize` — maximizes parameters instead of minimizing (rarely used)

### Adam

`optim.Adam(params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, maximize=False, foreach=None, fused=None, differentiable=False)`

Adaptive Moment Estimation — combines momentum with per-parameter adaptive learning rates. Default choice for most deep learning tasks.

```python
optimizer = optim.Adam(model.parameters(), lr=1e-3)
optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4, amsgrad=True)
```

Parameters:
- `betas` — coefficients for first and second moment running averages
- `eps` — term for numerical stability
- `amsgrad` — uses max of all historical second moments (improves convergence in some cases)
- `fused` — single-kernel CUDA implementation when True

### AdamW

`optim.AdamW(params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=1e-2, amsgrad=False, maximize=False, foreach=None, fused=None, differentiable=False)`

Adam with **decoupled weight decay** — weight decay is applied directly to parameters, not accumulated in momentum or variance estimates. This fixes the regularization behavior of L2-penalized Adam. Default for transformer and large model training.

```python
optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-2)
```

Key difference from Adam: `weight_decay` defaults to `1e-2` (not 0), and decay is applied outside the adaptive update.

### Adadelta

`optim.Adadelta(params, lr=1.0, rho=0.95, eps=1e-6, weight_decay=0, maximize=False, foreach=None)`

Adaptive learning rate method that doesn't require setting a base learning rate. Accumulates squared gradients and uses them to scale updates.

```python
optimizer = optim.Adadelta(model.parameters(), rho=0.95, eps=1e-6)
```

Parameters:
- `rho` — decay rate for squared gradient accumulator
- `eps` — numerical stability term

### Adafactor

`optim.Adafactor(params, lr=None, eps=(1e-30, 1e-3), clip_threshold=1.0, decay_rate=-0.8, beta2=None, warmup_init=False, ...)`

Memory-efficient adaptive optimizer designed for large-scale models (especially transformers). Uses factored second-moment estimates, reducing memory from O(d²) to O(d).

```python
optimizer = optim.Adafactor(model.parameters(), lr=1e-3)
```

Key features:
- No momentum state for non-embedding parameters (saves ~50% memory vs AdamW)
- Automatic learning rate scheduling when `lr` is not specified
- Factorized second-moment for 2D parameters (Linear, Conv2d)

### Adagrad

`optim.Adagrad(params, lr=0.01, lr_decay=0, eps=1e-10, weight_decay=0, maximize=False, foreach=None, fused=None, differentiable=False)`

Accumulates squared gradients and divides learning rate by the square root of accumulated magnitude. Effective for sparse data.

```python
optimizer = optim.Adagrad(model.parameters(), lr=0.01)
optimizer = optim.Adagrad(model.parameters(), lr=0.01, fused=True)  # CPU fused kernel (2.12+)
```

Parameters:
- `lr_decay` — optional learning rate decay over time
- `fused` — single-kernel implementation (CPU only in 2.12)

### Adamax

`optim.Adamax(params, lr=2e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, maximize=False, foreach=None)`

Adam variant using infinity norm instead of L2 norm for the adaptive learning rate. More robust to outliers in gradient magnitude.

```python
optimizer = optim.Adamax(model.parameters(), lr=2e-3)
```

### ASGD (Averaged Stochastic Gradient Descent)

`optim.ASGD(params, lr=0.01, lambd=0.0001, alpha=0.75, t0=1000, weight_decay=0, maximize=False, foreach=None)`

SGD with averaging — maintains a separate averaged parameter set that converges to a wider optimum. Useful for fine-tuning.

```python
optimizer = optim.ASGD(model.parameters(), lr=0.01, t0=1000)
```

Parameters:
- `lambd` — coefficient for L2 regularization
- `alpha` — power for eta update
- `t0` — point at which averaging starts (steps)

### LBFGS

`optim.LBFGS(params, lr=1, max_iter=20, max_eval=None, history_size=100, tolerance_grad=1e-5, tolerance_change=1e-9, line_search_fn=None)`

Limited-memory BFGS — second-order quasi-Newton method. Requires a closure. Best for small batch sizes or full-batch optimization.

```python
optimizer = optim.LBFGS(model.parameters(), lr=1, max_iter=20)

def closure():
    optimizer.zero_grad()
    loss = criterion(model(inputs), targets)
    loss.backward()
    return loss

optimizer.step(closure)
```

Parameters:
- `max_iter` — max number of iterations per step
- `history_size` — number of previous iterations to store for Hessian approximation
- `tolerance_grad` — stop when gradient norm drops below this

### Muon

`optim.Muon(params, lr=0.02, weight_decay=0.01)`

Layer-wise preconditioning optimizer. Applies orthogonal gradient transport via the implicit QR decomposition on 2D parameters. Designed for large-scale training with strong convergence properties.

```python
optimizer = optim.Muon(model.parameters(), lr=0.02, weight_decay=0.01)
```

Use case: Large model training where second-order methods are desired without full Hessian computation.

### NAdam

`optim.NAdam(params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, maximize=False, foreach=None)`

Adam with **lookahead** (warmup-corrected) — applies a bias correction that effectively looks one step ahead. Combines ideas from RAdam and Adam.

```python
optimizer = optim.NAdam(model.parameters(), lr=1e-3)
```

### RAdam

`optim.RAdam(params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, degenerated_to_sgd=True, maximize=False, foreach=None)`

Rectified Adam — adapts the learning rate based on whether the warmup phase has completed. No manual warmup schedule needed.

```python
optimizer = optim.RAdam(model.parameters(), lr=1e-3)
```

Parameters:
- `degenerated_to_sgd` — falls back to SGD when variance is too small

### RMSprop

`optim.RMSprop(params, lr=1e-2, alpha=0.99, eps=1e-8, weight_decay=0, momentum=0, centered=False, maximize=False, foreach=None)`

Root Mean Square Propagation — adaptive learning rate with exponentially decaying average of squared gradients. Common in RNN training.

```python
optimizer = optim.RMSprop(model.parameters(), lr=1e-2, alpha=0.99)
optimizer = optim.RMSprop(model.parameters(), lr=1e-2, momentum=0.9, centered=True)
```

Parameters:
- `alpha` — smoothing coefficient for squared gradient accumulator
- `momentum` — optional momentum term (makes it similar to Adam without bias correction)
- `centered` — divides estimate by difference from mean (more stable but higher memory)

### Rprop (Resilient Backpropagation)

`optim.Rprop(params, lr=1e-2, etas=(0.5, 1.2), min_lr=1e-7, max_lr=1e2, maximize=False, foreach=None)`

Per-parameter adaptive learning rates based on sign changes of gradients. Ignores gradient magnitude entirely.

```python
optimizer = optim.Rprop(model.parameters(), lr=1e-2)
```

Parameters:
- `etas` — (eta_minus, eta_plus) factors for decreasing/increasing step sizes

### SparseAdam

`optim.SparseAdam(params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, maximize=False)`

Adam variant for sparse gradients. Maintains a mask so only non-zero gradient entries update state. Memory-efficient for embedding layers.

```python
# Use with embedding layers that produce sparse gradients
embedding = torch.nn.Embedding(10000, 128, sparse=True)
optimizer = optim.SparseAdam(embedding.parameters(), lr=1e-3)
```

## Optimizer Hooks

Register callbacks on optimizer steps for logging, gradient clipping, or custom logic.

**Per-optimizer hooks:**

```python
# Pre-step hook (runs before parameter update)
handle = optimizer.register_step_pre_hook(
    lambda opt, args, kwargs: print(f"Step with lr={opt.param_groups[0]['lr']}")
)

# Post-step hook (runs after parameter update)
optimizer.register_step_post_hook(
    lambda opt, args, kwargs: torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
)

# Remove a hook
handle.remove()
```

**Module-level hooks** (apply to all optimizers):

```python
from torch.optim.optimizer import register_optimizer_step_post_hook

# Log every optimizer step across the entire program
register_optimizer_step_post_hook(
    lambda opt, args, kwargs: print(f"{opt.__class__.__name__} stepped")
)
```

**State dict hooks** (for custom save/load behavior):

```python
optimizer.register_state_dict_pre_hook(lambda state_dict, opt: None)
optimizer.register_state_dict_post_hook(lambda state_dict, opt: None)
optimizer.register_load_state_dict_pre_hook(lambda state_dict, opt: None)
optimizer.register_load_state_dict_post_hook(lambda state_dict, opt: None)
```

## Learning Rate Schedulers

Schedulers adjust learning rates during training. Call `scheduler.step()` **after** `optimizer.step()`.

### Step-Based Schedulers

```python
# Decay by gamma every step_size epochs
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)

# Decay at specific milestone epochs
scheduler = optim.lr_scheduler.MultiStepLR(optimizer, milestones=[30, 80], gamma=0.1)

# Exponential decay every epoch
scheduler = optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.95)

# Polynomial decay over total_iters steps
scheduler = optim.lr_scheduler.PolynomialLR(optimizer, total_iters=1000, power=2.0)
```

### Warmup Schedulers

```python
# Linear warmup for first 5 epochs
scheduler = optim.lr_scheduler.LinearLR(optimizer, start_factor=0.1, total_iters=5)

# Constant warmup (multiply by small factor then hold)
scheduler = optim.lr_scheduler.ConstantLR(optimizer, factor=0.1, total_iters=5)
```

### Cosine Schedulers

```python
# Cosine annealing to 0 over T_max epochs
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

# Cosine annealing with warm restarts
scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)
```

### Metric-Based Scheduler

```python
# Reduce LR when validation loss plateaus
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.5, patience=5, threshold=0.01
)

for epoch in range(100):
    train()
    val_loss = validate()
    scheduler.step(val_loss)  # pass metric value
```

### Cyclic Schedulers

```python
# Cyclic learning rate between base_lr and max_lr
scheduler = optim.lr_scheduler.CyclicLR(
    optimizer, base_lr=1e-4, max_lr=1e-2, step_size_up=2000, cycle_momentum=True
)

# One-cycle policy (warmup + cooldown in one cycle)
scheduler = optim.lr_scheduler.OneCycleLR(
    optimizer, max_lr=1e-2, total_steps=10000, pct_start=0.3, anneal_strategy='cos'
)
```

### Composable Schedulers

```python
# Chain schedulers (each applied sequentially on the result of the previous)
scheduler1 = optim.lr_scheduler.LinearLR(optimizer, start_factor=0.1, total_iters=5)
scheduler2 = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=95)

for epoch in range(100):
    train()
    scheduler1.step()
    scheduler2.step()

# Sequential schedulers (run one after another based on epoch ranges)
scheduler = optim.lr_scheduler.SequentialLR(
    optimizer,
    schedulers=[
        optim.lr_scheduler.LinearLR(optimizer, start_factor=0.1, total_iters=5),
        optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=95),
    ],
    milestones=[5]
)

# Chain a list of schedulers
scheduler = optim.lr_scheduler.ChainedScheduler([scheduler1, scheduler2])
```

### Custom Schedulers

```python
# Lambda-based (multiply each param group's lr by a function)
scheduler = optim.lr_scheduler.LambdaLR(
    optimizer, lr_lambda=lambda epoch: 0.95 ** epoch
)

# Per-group lambdas for different schedules per parameter group
scheduler = optim.lr_scheduler.LambdaLR(
    optimizer, lr_lambda=[lambda e: 0.99 ** e, lambda e: 0.95 ** e]
)

# Multiplicative (custom factor function)
scheduler = optim.lr_scheduler.MultiplicativeLR(
    optimizer, lr_lambda=lambda epoch: 0.99
)
```

## Weight Averaging (SWA and EMA)

`torch.optim.swa_utils` provides Stochastic Weight Averaging and Exponential Moving Average utilities.

### SWA (Stochastic Weight Averaging)

Averages model weights over the latter portion of training to find wider optima:

```python
from torch.optim.swa_utils import AveragedModel, SWALR, update_bn

swa_model = AveragedModel(model)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=300)
swa_start_epoch = 160
swa_scheduler = SWALR(optimizer, swa_lr=0.05)

for epoch in range(300):
    for inputs, targets in loader:
        optimizer.zero_grad()
        loss = criterion(model(inputs), targets)
        loss.backward()
        optimizer.step()

    if epoch >= swa_start_epoch:
        swa_model.update_parameters(model)
        swa_scheduler.step()
    else:
        scheduler.step()

# Update BatchNorm statistics for the averaged model
update_bn(loader, swa_model)

# Use swa_model for inference
preds = swa_model(test_inputs)
```

`SWALR` anneals the learning rate to a fixed `swa_lr` value, then holds it constant. Supports `anneal_strategy="linear"` (default) or `"cos"`.

### EMA (Exponential Moving Average)

Maintains exponentially-decayed averages of weights throughout training:

```python
from torch.optim.swa_utils import AveragedModel, get_ema_multi_avg_fn, update_bn

decay = 0.999
ema_model = AveragedModel(
    model, multi_avg_fn=get_ema_multi_avg_fn(decay)
)

for epoch in range(300):
    for inputs, targets in loader:
        optimizer.zero_grad()
        loss = criterion(model(inputs), targets)
        loss.backward()
        optimizer.step()
        ema_model.update_parameters(model)

update_bn(loader, ema_model)
preds = ema_model(test_inputs)
```

EMA equation: `W_ema(t+1) = decay * W_ema(t) + (1 - decay) * W_model(t+1)`

Decay should be close to 1.0 (default 0.999). Smaller values can cause convergence issues.

### Custom Averaging Functions

```python
# Per-parameter averaging function
ema_avg = lambda avg_param, model_param, n_avg: 0.9 * avg_param + 0.1 * model_param
ema_model = AveragedModel(model, avg_fn=ema_avg)

# Batch averaging function (more efficient, uses foreach operations)
ema_model = AveragedModel(model, multi_avg_fn=get_ema_multi_avg_fn(0.999))
```
