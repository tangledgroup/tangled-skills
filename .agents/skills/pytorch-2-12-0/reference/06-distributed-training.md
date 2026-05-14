# Distributed Training

## Contents
- Initialization and ProcessGroups
- Distributed Data Parallel (DDP)
- FullyShardedDataParallel (FSDP)
- Collective Operations
- Tensor Parallelism
- Pipeline Parallelism
- Distributed Checkpointing
- Profiling Distributed Training

## Initialization and ProcessGroups

Set up distributed training with `torch.distributed`:

```python
import torch.distributed as dist
import torch.nn as nn

# Initialize the process group
dist.init_process_group(backend="nccl")  # "nccl" for GPU, "gloo" for CPU
rank = dist.get_rank()
world_size = dist.get_world_size()

# Move model to local GPU
model = MyModel().cuda(rank)
```

Launch with `torchrun`:

```bash
torchrun --nproc-per-node=4 --nnodes=1 train.py
```

In 2.12, `torchrun` defaults to an OS-assigned free port for single-node training (no more static port 29500 conflicts). Use `--master-port=29500` for explicit port control.

ProcessGroups support direct `ProcessGroup` object arguments in custom ops and functional collectives (new in 2.12):

```python
group = dist.new_group(ranks=[0, 1])
result = dist.all_reduce(tensor, group=group)  # accepts ProcessGroup directly
```

## Distributed Data Parallel (DDP)

`DistributedDataParallel` replicates the model across GPUs and synchronizes gradients:

```python
model = MyModel().cuda(rank)
ddp_model = nn.parallel.DistributedDataParallel(
    model,
    device_ids=[rank],
    output_device=rank,
    find_unused_parameters=False,  # set True if some params aren't used in forward
)

for inputs, targets in loader:
    outputs = ddp_model(inputs.cuda(rank))
    loss = criterion(outputs, targets.cuda(rank))
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
```

Key considerations:
- Use `DistributedSampler` to partition data across ranks
- Gradient synchronization happens automatically during `backward()`
- Bucketing groups parameters for efficient all-reduce communication
- Communication hooks can compress gradients or overlap computation with communication

## FullyShardedDataParallel (FSDP)

FSDP shards model parameters, gradients, and optimizer states across GPUs, enabling training of models that exceed single-GPU memory:

```python
from torch.distributed.fsdp import FullyShardedDataParallel, ShardingStrategy
from torch.distributed.fsdp.fully_shard import fully_shard

model = MyModel()

# API 1: FullyShardedDataParallel wrapper
fsdp_model = FullyShardedDataParallel(
    model,
    sharding_strategy=ShardingStrategy.FULL_SHARD,
    cpu_offload=False,
)

# API 2: Granular fully_shard (recommended for fine control)
model = MyModel()
model = fully_shard(model)
# Or wrap individual submodules
for layer in model.layers:
    layer = fully_shard(layer)
```

Sharding strategies:
- `FULL_SHARD` — shard parameters, gradients, optimizer states (max memory savings)
- `SHARD_GRAD_OP` — shard gradients and optimizer states only
- `_NO_SHARD` — no sharding (local replica, useful for small modules)
- `HYBRID_SHARD` — shard within nodes, replicate across nodes

Use CPU offload (`cpu_offload=True`) when GPU memory is extremely constrained, accepting higher communication overhead.

## Collective Operations

Functional collectives for fine-grained control:

```python
from torch.distributed._functional_collectives import (
    all_reduce, all_gather, reduce_scatter, all_to_all_single,
)

# All-reduce with sum
result = all_reduce(tensor, reduceOp="sum", group=group)

# Reduce-scatter
result = reduce_scatter(tensor, reduceOp="avg", group=group)

# All-gather
result = all_gather(tensor, dim=-1, group=group)
```

Note: `torch.distributed.nn.functional` ops raise `RuntimeError` under `torch.compile` in 2.12 — use `torch.distributed._functional_collectives` instead.

## Tensor Parallelism

Split large layers (especially attention and linear) across GPUs with `torch.distributed.tensor.parallel`:

```python
from torch.distributed.tensor.parallel import (
    ColwiseParallel, RowwiseParallel, parallelize_module,
    PairwiseSequenceParallel,
)
from torch.distributed.device_mesh import init_device_mesh

# Create device mesh
mesh = init_device_mesh("cuda", (1, world_size), mesh_dim_names=("replica", "tp"))

# Parallelize a transformer model
parallel_plan = {
    "q_proj": ColwiseParallel(),
    "k_proj": ColwiseParallel(),
    "v_proj": ColwiseParallel(),
    "output": RowwiseParallel(),
}

model = parallelize_module(model, mesh, parallel_plan)
```

## Pipeline Parallelism

Split the model across stages and process multiple micro-batches to minimize bubble idle time:

```python
from torch.distributed.pipelining import split_into_segments, schedule_loop

# Split model into stages
stages = split_into_segments(model, num_stages=4)

# Schedule with 1F1B (1 forward, 1 backward) scheduling
micro_batches = [torch.randn(micro_batch_size, *input_shape) for _ in range(num_micro_batches)]
schedule_loop(stages, micro_batches)
```

Pipeline parallelism is most effective for very large models where inter-stage communication overhead is amortized across many layers.

## Distributed Checkpointing

Save and load model state across multiple processes with `torch.distributed.checkpoint`:

```python
import torch.distributed.checkpoint as dist_cp

# Save
state_dict = {"model": model.state_dict(), "optimizer": optimizer.state_dict()}
dist_cp.save(state_dict, checkpoint_id="checkpoint/step-1000")

# Load
dist_cp.load(state_dict, checkpoint_id="checkpoint/step-1000")
model.load_state_dict(state_dict["model"])
optimizer.load_state_dict(state_dict["optimizer"])
```

Distributed checkpointing writes shards in parallel across ranks, significantly faster than single-process saves for large models.

## Profiling Distributed Training

In 2.12, the Profiler Events API exposes flow IDs, flow types, and NCCL collective `seq_num` for correlating traces across ranks:

```python
from torch.profiler import profile, ProfilerActivity, tensorboard_trace_handler

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    with_stack=True,
    record_shapes=True,
) as prof:
    for batch in loader:
        outputs = model(batch)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        prof.step()

# Export to TensorBoard
writer = tensorboard_trace_handler("./logs")(prof)
```

Multi-GPU profiling now correlates NCCL collective traces across ranks using shared `seq_num` within a ProcessGroup.
