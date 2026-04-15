# CUDA GPU Programming with Numba

## Overview

Numba's CUDA support enables Python code execution on NVIDIA GPUs using the `@cuda.jit` decorator. This provides access to:
- GPU kernel programming with explicit thread hierarchies
- Global, shared, and local memory management
- Device functions for code reuse
- CUDA streams and events for asynchronous execution
- Cooperative groups for advanced synchronization

**Requirements:**
- NVIDIA GPU with compute capability 5.0+
- CUDA Toolkit installed (11.2+ recommended)
- Numba with CUDA support (`conda install cuda-nvcc cuda-nvrtc`)

## Kernel Basics

### Simple Kernel

```python
from numba import cuda
import numpy as np

@cuda.jit
def vector_add(x, y, result):
    """Add two vectors on GPU."""
    idx = cuda.grid(1)  # Get global thread index
    if idx < x.size:
        result[idx] = x[idx] + y[idx]

# Prepare data
x = np.arange(1000, dtype=np.float64)
y = np.ones(1000, dtype=np.float64)
result = np.zeros(1000, dtype=np.float64)

# Launch kernel
threads_per_block = 256
blocks_per_grid = (x.size + threads_per_block - 1) // threads_per_block
vector_add[blocks_per_grid, threads_per_block](x, y, result)
```

### Thread Hierarchy

CUDA organizes threads in a hierarchy:
- **Grid**: Collection of blocks
- **Block**: Collection of threads that can share memory and synchronize
- **Thread**: Individual execution unit

```python
@cuda.jit
def thread_info_kernel(output):
    """Demonstrate thread positioning."""
    # Thread index within block (0 to blockDim.x-1)
    tx = cuda.threadIdx.x
    
    # Block index within grid (0 to gridDim.x-1)
    bx = cuda.blockIdx.x
    
    # Threads per block
    bw = cuda.blockDim.x
    
    # Compute global position
    pos = tx + bx * bw
    
    if pos < output.size:
        output[pos] = float(pos)

# Launch with 4 blocks of 256 threads each
output = np.zeros(1024, dtype=np.float64)
thread_info_kernel[4, 256](output)
```

### Multi-dimensional Grids

```python
@cuda.jit
def matrix_add(A, B, C):
    """Add two 2D matrices."""
    # Get 2D thread position
    row, col = cuda.grid(2)
    
    # Check bounds
    if row < A.shape[0] and col < A.shape[1]:
        C[row, col] = A[row, col] + B[row, col]

# Create matrices
A = np.random.rand(1024, 1024).astype(np.float64)
B = np.random.rand(1024, 1024).astype(np.float64)
C = np.zeros((1024, 1024), dtype=np.float64)

# Launch with 2D grid and blocks
threads_per_block = (32, 32)
blocks_per_grid = (
    (A.shape[1] + threads_per_block[1] - 1) // threads_per_block[1],
    (A.shape[0] + threads_per_block[0] - 1) // threads_per_block[0]
)

matrix_add[blocks_per_grid, threads_per_block](A, B, C)
```

## Memory Management

### Device Memory

Transfer data to GPU explicitly:

```python
from numba import cuda
import numpy as np

# Host array
h_data = np.arange(1000000, dtype=np.float64)

# Transfer to device
d_data = cuda.to_device(h_data)

# Use in kernel
@cuda.jit
def process(data):
    idx = cuda.grid(1)
    if idx < data.size:
        data[idx] *= 2.0

process[100, 1000](d_data)

# Copy back to host
h_result = d_data.copy_to_host()

# Or copy directly to existing array
h_output = np.zeros(1000000, dtype=np.float64)
d_data.copy_to_hst(h_output)
```

### Memory Context Management

```python
from numba import cuda
import numpy as np

# Manual memory management
with cuda.device(0):  # Select GPU device 0
    d_array = cuda.device_array((1000, 1000), dtype=np.float64)
    
    @cuda.jit
    def init_array(arr):
        row, col = cuda.grid(2)
        if row < arr.shape[0] and col < arr.shape[1]:
            arr[row, col] = row + col
    
    init_array[(32, 32), (32, 32)](d_array)
    
    # Data automatically freed when d_array goes out of scope

# Synchronize to ensure completion
cuda.synchronize()
```

### Pinned Memory for Faster Transfers

```python
from numba import cuda
import numpy as np

# Allocate page-locked host memory (faster transfers)
h_data = cuda.pinned(np.arange(1000000, dtype=np.float64))
d_data = cuda.to_device(h_data)

# Transfers are asynchronous and faster
```

## Shared Memory

Shared memory is fast on-chip memory shared by threads in a block:

```python
@cuda.jit
def shared_memory_example(input_arr, output_arr):
    """Demonstrate shared memory usage."""
    # Declare shared memory (256 floats per block)
    shared_data = cuda.shared.array(shape=256, dtype=np.float64)
    
    idx = cuda.threadIdx.x
    tid = cuda.blockIdx.x * 256 + idx
    
    if tid < input_arr.size:
        # Load from global to shared memory
        shared_data[idx] = input_arr[tid]
    
    # Synchronize threads in block
    cuda.syncthreads()
    
    # Process from shared memory
    if tid < output_arr.size:
        output_arr[tid] = shared_data[idx] * 2.0

# Launch
input_data = np.arange(10000, dtype=np.float64)
output_data = np.zeros(10000, dtype=np.float64)
shared_memory_example[40, 256](input_data, output_data)
```

### Shared Memory for Tiling

```python
@cuda.jit
def matrix_multiply_tiled(A, B, C):
    """Matrix multiplication with shared memory tiling."""
    TILE_SIZE = 16
    
    # Shared memory tiles
    tile_A = cuda.shared.array((TILE_SIZE, TILE_SIZE), dtype=np.float64)
    tile_B = cuda.shared.array((TILE_SIZE, TILE_SIZE), dtype=np.float64)
    
    # Thread coordinates
    row = cuda.blockIdx.y * TILE_SIZE + cuda.threadIdx.y
    col = cuda.blockIdx.x * TILE_SIZE + cuda.threadIdx.x
    
    # Accumulator
    val = 0.0
    
    # Loop over tiles
    for t in range((A.shape[1] + TILE_SIZE - 1) // TILE_SIZE):
        # Load tiles into shared memory
        tile_row = row
        tile_col = t * TILE_SIZE + cuda.threadIdx.x
        
        if tile_row < A.shape[0] and tile_col < A.shape[1]:
            tile_A[cuda.threadIdx.y, cuda.threadIdx.x] = A[tile_row, tile_col]
        else:
            tile_A[cuda.threadIdx.y, cuda.threadIdx.x] = 0.0
        
        tile_row = t * TILE_SIZE + cuda.threadIdx.y
        tile_col = col
        
        if tile_row < B.shape[0] and tile_col < B.shape[1]:
            tile_B[cuda.threadIdx.y, cuda.threadIdx.x] = B[tile_row, tile_col]
        else:
            tile_B[cuda.threadIdx.y, cuda.threadIdx.x] = 0.0
        
        # Synchronize before using shared data
        cuda.syncthreads()
        
        # Compute partial product
        for k in range(TILE_SIZE):
            val += tile_A[cuda.threadIdx.y, k] * tile_B[k, cuda.threadIdx.x]
        
        # Synchronize before loading next tile
        cuda.syncthreads()
    
    # Write result
    if row < C.shape[0] and col < C.shape[1]:
        C[row, col] = val

# Launch with 2D grid of blocks
N = 1024
A = np.random.rand(N, N).astype(np.float64)
B = np.random.rand(N, N).astype(np.float64)
C = np.zeros((N, N), dtype=np.float64)

threads_per_block = (16, 16)
blocks_per_grid = (N // 16, N // 16)
matrix_multiply_tiled[blocks_per_grid, threads_per_block](A, B, C)
```

## Device Functions

Device functions run on GPU but are called from kernels:

```python
from numba import cuda
import numpy as np

@cuda.jit(device=True)
def distance_squared(x1, y1, x2, y2):
    """Compute squared Euclidean distance (device function)."""
    dx = x2 - x1
    dy = y2 - y1
    return dx * dx + dy * dy

@cuda.jit
def find_nearest(points, query_x, query_y, nearest_idx):
    """Find nearest point to query position."""
    idx = cuda.grid(1)
    
    if idx < points.shape[0]:
        px, py = points[idx, 0], points[idx, 1]
        dist = distance_squared(px, py, query_x, query_y)
        
        # Atomic minimum to find nearest
        current_min = nearest_idx[0]
        while True:
            old = nearest_idx[0]
            if dist < old or old == -1:
                if cuda.atomic.exch(nearest_idx, dist) < dist:
                    continue
            break

# Usage
points = np.random.rand(10000, 2).astype(np.float64)
nearest_idx = np.array([-1.0], dtype=np.float64)
find_nearest[100, 100](points, 0.5, 0.5, nearest_idx)
```

## Atomic Operations

Atomic operations ensure thread-safe updates:

```python
@cuda.jit
def atomic_histogram(values, histogram, num_bins):
    """Build histogram using atomic operations."""
    idx = cuda.grid(1)
    
    if idx < values.size:
        # Compute bin index
        bin_idx = int(values[idx] * num_bins)
        bin_idx = min(bin_idx, num_bins - 1)  # Clamp to valid range
        
        # Atomic increment
        cuda.atomic.add(histogram, bin_idx, 1)

# Usage
values = np.random.rand(1000000).astype(np.float64)
histogram = np.zeros(100, dtype=np.int32)
atomic_histogram[100, 1000](values, histogram, 100)
```

### Available Atomic Operations

- `cuda.atomic.add(arr, idx, val)` - Atomic addition
- `cuda.atomic.sub(arr, idx, val)` - Atomic subtraction
- `cuda.atomic.max(arr, idx, val)` - Atomic maximum
- `cuda.atomic.min(arr, idx, val)` - Atomic minimum
- `cuda.atomic.inc(arr, idx, val)` - Atomic increment and wrap
- `cuda.atomic.exch(arr, idx, val)` - Atomic exchange

## Streams and Asynchronous Execution

```python
from numba import cuda
import numpy as np

# Create stream
stream = cuda.stream()

@cuda.jit
def kernel(data):
    idx = cuda.grid(1)
    if idx < data.size:
        data[idx] *= 2.0

# Prepare data
data = cuda.to_device(np.arange(1000000, dtype=np.float64))

# Launch in stream (asynchronous)
kernel[100, 100](data, stream=stream)

# Synchronize stream (wait for completion)
stream.synchronize()

# Or synchronize all streams
cuda.synchronize()

# Copy back
result = data.copy_to_host()
```

### Multiple Streams for Overlap

```python
from numba import cuda
import numpy as np

# Create multiple streams
stream1 = cuda.stream()
stream2 = cuda.stream()

@cuda.jit
def kernel1(data):
    idx = cuda.grid(1)
    if idx < data.size:
        data[idx] += 1.0

@cuda.jit
def kernel2(data):
    idx = cuda.grid(1)
    if idx < data.size:
        data[idx] *= 2.0

# Prepare arrays
data1 = cuda.to_device(np.arange(500000, dtype=np.float64))
data2 = cuda.to_device(np.arange(500000, dtype=np.float64))

# Launch in different streams (can overlap)
kernel1[100, 100](data1, stream=stream1)
kernel2[100, 100](data2, stream=stream2)

# Wait for both
stream1.synchronize()
stream2.synchronize()
```

## Events for Timing

```python
from numba import cuda
import numpy as np

@cuda.jit
def kernel(data):
    idx = cuda.grid(1)
    if idx < data.size:
        data[idx] = np.sin(data[idx])

# Prepare data
data = cuda.to_device(np.arange(1000000, dtype=np.float64))

# Create events for timing
start_event = cuda.event()
end_event = cuda.event()

# Record start
start_event.record()

# Run kernel multiple times
for _ in range(100):
    kernel[100, 100](data)

# Record end
end_event.record()

# Synchronize and get elapsed time
cuda.synchronize()
elapsed_ms = end_event.elapsed_time(start_event)
print(f"Average kernel time: {elapsed_ms / 100:.3f} ms")
```

## Cooperative Groups

Cooperative groups enable advanced synchronization patterns:

```python
from numba import cuda
from numba.cuda import cooperative_groups as cg
import numpy as np

@cuda.jit
def block_reduction(arr):
    """Reduce array using cooperative groups."""
    # Get block as cooperative group
    block = cg.this_grid_block()
    
    # Shared memory for reduction
    shared_data = cuda.shared.array(shape=1024, dtype=np.float64)
    
    idx = cg.this_thread().tid_in_block
    tid = cuda.blockIdx.x * 1024 + idx
    
    # Load data
    if tid < arr.size:
        shared_data[idx] = arr[tid]
    else:
        shared_data[idx] = 0.0
    
    block.sync()
    
    # Parallel reduction in shared memory
    for stride in [512, 256, 128, 64, 32, 16, 8, 4, 2, 1]:
        if idx < stride:
            shared_data[idx] += shared_data[idx + stride]
        block.sync()
    
    # First thread writes result
    if idx == 0:
        print(f"Block {cuda.blockIdx.x} sum: {shared_data[0]}")

# Launch
data = np.arange(10240, dtype=np.float64)
block_reduction[10, 1024](data)
```

## Error Handling

### Check for CUDA Errors

```python
from numba import cuda
import numpy as np

try:
    # Select device
    cuda.set_device(0)
    
    # Get device properties
    print(f"Device: {cuda.get_device_name()}")
    print(f"Memory: {cuda.current_context().get_memory_info()[0] / 1e9:.2f} GB")
    
except cuda.CudaSupportError as e:
    print(f"CUDA not available: {e}")
except cuda.CudaInitializationError as e:
    print(f"CUDA initialization failed: {e}")
```

### Kernel Error Checking

```python
from numba import cuda
import numpy as np

@cuda.jit
def safe_kernel(data):
    idx = cuda.grid(1)
    if idx < data.size:
        # Check for invalid operations
        if data[idx] < 0:
            raise ValueError(f"Negative value at index {idx}")
        data[idx] = np.sqrt(data[idx])

# Launch with error checking enabled
data = cuda.to_device(np.arange(1000, dtype=np.float64))

try:
    safe_kernel[10, 100](data)
    cuda.synchronize()  # Triggers error if kernel failed
except RuntimeError as e:
    print(f"Kernel error: {e}")
```

## Performance Tips

### Occupancy Optimization

Maximize GPU utilization with appropriate block sizes:

```python
from numba import cuda

# Check occupancy
@cuda.jit
def my_kernel(data):
    idx = cuda.grid(1)
    if idx < data.size:
        data[idx] *= 2.0

occupancy = cuda.occupancy.max_active_blocks_per_multiprocessor(
    my_kernel, 
    blocksize=256,
    dynamic_smem_size=0
)
print(f"Max blocks per multiprocessor: {occupancy}")
```

### Memory Coalescing

Ensure consecutive threads access consecutive memory:

```python
@cuda.jit
def coalesced_access(arr):
    """Good: Consecutive threads access consecutive elements."""
    idx = cuda.grid(1)
    if idx < arr.size:
        arr[idx] *= 2.0  # Coalesced: thread i accesses arr[i]

@cuda.jit  
def strided_access(arr):
    """Bad: Strided access pattern."""
    idx = cuda.grid(1)
    stride = 4
    if idx < arr.size // stride:
        arr[idx * stride] *= 2.0  # Non-coalesced
```

### Reduce Global Memory Access

Use shared memory and registers when possible:

```python
@cuda.jit
def optimized_kernel(input_arr, output_arr):
    """Minimize global memory accesses."""
    idx = cuda.grid(1)
    
    if idx < input_arr.size:
        # Load once into register
        val = input_arr[idx]
        
        # Multiple computations on register value
        val = val * 2.0 + 1.0
        val = np.sin(val)
        val = val ** 2
        
        # Write once to global memory
        output_arr[idx] = val
```

## Device Management

### Multi-GPU Systems

```python
from numba import cuda
import numpy as np

# List available devices
print(f"Number of devices: {cuda.gpus.count()}")

for i in range(cuda.gpus.count()):
    with cuda.device(i):
        print(f"Device {i}: {cuda.get_device_name()}")

# Use specific device
with cuda.device(0):
    d_data = cuda.to_device(np.arange(1000))
    # All operations use device 0

# Get current device
current_device = cuda.get_device_id()
```

### IPC (Inter-Process Communication)

Share memory between processes:

```python
from numba import cuda
import numpy as np

# Process 1: Create and share
arr = cuda.device_array(1000, dtype=np.float64)
ipc_handle = arr.__cuda_array_interface__['data'][0]  # Get handle
# Share ipc_handle with other process...

# Process 2: Open shared memory
# d_arr = cuda.IpcMemoryHandle(ipc_handle).open()
```

## Troubleshooting

### Common Errors

**CUDA out of memory:**

```python
from numba import cuda
import numpy as np

try:
    large_array = cuda.device_array((10000, 10000, 10000), dtype=np.float64)
except RuntimeError as e:
    print(f"Out of memory: {e}")
    
# Solution: Use smaller arrays or process in chunks
```

**Kernel launch failure:**

```python
from numba import cuda
import numpy as np

@cuda.jit
def kernel(data):
    idx = cuda.grid(1)
    if idx < data.size:
        data[idx] *= 2.0

# Too many threads?
try:
    kernel[1000000, 1](data)  # 1M threads in single block - will fail!
except RuntimeError as e:
    print(f"Launch failed: {e}")

# Solution: Use proper grid/block configuration
kernel[1000, 1000](data)  # 1M threads across 1000 blocks
```
