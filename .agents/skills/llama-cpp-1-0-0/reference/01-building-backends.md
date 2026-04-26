# Building and Backends

## CPU Build

The baseline build uses CMake with no GPU backend:

```bash
cmake -B build
cmake --build build --config Release
```

For debug builds, use `-DCMAKE_BUILD_TYPE=Debug` for single-config generators (Unix Makefiles), or `--config Debug` for multi-config generators (Visual Studio, Xcode).

For static linking:

```bash
cmake -B build -DBUILD_SHARED_LIBS=OFF
cmake --build build --config Release
```

## CUDA (NVIDIA GPU)

Requires the CUDA toolkit installed. Build with:

```bash
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release
```

For non-native builds (runs on all CUDA GPUs):

```bash
cmake -B build -DGGML_CUDA=ON -DGGML_NATIVE=OFF
```

To override compute capabilities:

```bash
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="86;89"
```

### CUDA Runtime Environment Variables

- `CUDA_VISIBLE_DEVICES` — control which GPUs are visible
- `CUDA_SCALE_LAUNCH_QUEUES` — increase CUDA command buffer (e.g., `4x` for multi-GPU pipeline parallelism)
- `GGML_CUDA_FORCE_CUBLAS_COMPUTE_32F` — force FP32 compute in FP16 cuBLAS to prevent numerical overflow
- `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1` — enable unified memory on Linux (swap to system RAM when VRAM exhausted)

### CUDA Compilation Options

- `GGML_CUDA_FORCE_MMQ` — force custom matrix multiplication kernels for quantized models (lower VRAM, slower for large batches)
- `GGML_CUDA_FORCE_CUBLAS` — force FP16 cuBLAS instead of custom kernels (higher memory, potentially faster prompt processing on datacenter GPUs)
- `GGML_CUDA_PEER_MAX_BATCH_SIZE` — max batch size for peer access between GPUs (default: 128)

## Metal (Apple Silicon)

Enabled by default on macOS. To disable:

```bash
cmake -B build -DGGML_METAL=OFF
```

At runtime, disable GPU inference with `--n-gpu-layers 0` or `--device none`.

## HIP (AMD GPU)

Requires ROCm installed. Example for gfx1030-compatible GPU:

```bash
HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
  cmake -S . -B build -DGGML_HIP=ON -DGPU_TARGETS=gfx1030 -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -- -j 16
```

For RDNA3+ or CDNA, enable rocWMMA for flash attention: `-DGGML_HIP_ROCWMMA_FATTN=ON`

Runtime: use `HIP_VISIBLE_DEVICES` to select GPUs. For unsupported GPUs, set `HSA_OVERRIDE_GFX_VERSION` (not supported on Windows).

## Vulkan

Cross-platform GPU backend. Install the LunarG Vulkan SDK or use system packages:

```bash
# Debian/Ubuntu
sudo apt-get install libvulkan-dev glslc

# Build
cmake -B build -DGGML_VULKAN=ON
cmake --build build --config Release
```

On macOS, use MoltenVK (default) or KosmicKrisp translation layer:

```bash
export VK_ICD_FILENAMES=$VULKAN_SDK/share/vulkan/icd.d/libkosmickrisp_icd.json
cmake -B build -DGGML_VULKAN=1 -DGGML_METAL=OFF
```

## SYCL (Intel GPU)

Supports Intel Data Center Max, Flex, Arc, and integrated GPUs. See `docs/backend/SYCL.md` for detailed setup.

```bash
cmake -B build -DGGML_SYCL=ON
cmake --build build --config Release
```

## Other Backends

**MUSA** (Moore Threads GPU): `-DGGML_MUSA=ON` — requires MUSA SDK

**CANN** (Ascend NPU): `-DGGML_CANN=ON` — requires CANN toolkit

**ZenDNN** (AMD EPYC CPU): `-DGGML_ZENDNN=ON` — automatic download on first build

**Arm KleidiAI**: `-DGGML_CPU_KLEIDIAI=ON` — optimized microkernels for Arm CPUs with dotprod, int8mm, SVE, SME

**OpenCL** (Adreno GPU): `-DGGML_OPENCL=ON` — primarily for Android

**OpenVINO** (Intel CPU/GPU/NPU): See `docs/backend/OPENVINO.md`

## Multi-Backend Builds

Multiple backends can be built simultaneously:

```bash
cmake -B build -DGGML_CUDA=ON -DGGML_VULKAN=ON
cmake --build build --config Release
```

At runtime, select devices with `--device`:

```bash
# List available devices
llama-cli --list-devices

# Use specific device
llama-cli -m model.gguf --device cuda:0

# Disable GPU entirely
llama-cli -m model.gguf --device none
```

## BLAS Acceleration

BLAS improves prompt processing with batch sizes > 32 (default: 512):

```bash
# OpenBLAS
cmake -B build -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS

# Intel oneMKL
source /opt/intel/oneapi/setvars.sh
cmake -B build -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=Intel10_64lp \
  -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx -DGGML_NATIVE=ON
```

On macOS, Accelerate framework is enabled by default.

## Backend Loading

Backends can be built as dynamic libraries for runtime loading:

```bash
cmake -B build -DGGML_CUDA=ON -DGGML_BACKEND_DL=ON
```

This allows the same binary to work on machines with different GPUs.

## Device Offloading

Control how model layers are distributed across devices:

- `-ngl N` — number of layers to offload to GPU (use `99` or `all` for full offload)
- `-sm layer|row` — split mode for multi-GPU
- `-ts 3,1` — tensor split ratio across GPUs
- `-mg 0` — main GPU index

For CPU+GPU hybrid inference (models larger than VRAM), llama.cpp automatically splits layers between CPU and GPU.
