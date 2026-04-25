# Build Guide for llama.cpp b8789

## Quick Build (CPU Only)

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release -j$(nproc)
```

Binaries will be in `build/bin/`:
- `llama-cli` - Command-line inference tool
- `llama-server` - OpenAI-compatible HTTP server
- `llama-bench` - Benchmarking tool
- `llama-quantize` - Model quantization utility

## Installation Methods

### Homebrew (macOS/Linux)

```bash
brew install llama.cpp
```

Automatically updated with new releases. Includes all binaries.

### Winget (Windows)

```powershell
winget install llama.cpp
```

Auto-updating package from Windows Package Manager.

### Nix (macOS/Linux)

```bash
# With flakes
nix profile install nixpkgs#llama-cpp

# Without flakes
nix-env --file '<nixpkgs>' --install --attr llama-cpp
```

## GPU-Accelerated Builds

### CUDA (NVIDIA GPU)

**Prerequisites:**
- NVIDIA GPU with compute capability ≥ 3.5
- CUDA Toolkit 12.x or 13.x installed

**Build:**
```bash
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release
```

**Non-native build (all architectures):**
```bash
cmake -B build -DGGML_CUDA=ON -DGGML_NATIVE=OFF
```

**Specific architectures:**
```bash
# RTX 3080 (8.6) + RTX 4090 (8.9)
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="86;89"
```

**Override CUDA version:**
```bash
cmake -B build -DGGML_CUDA=ON \
  -DCMAKE_CUDA_COMPILER=/opt/cuda-11.7/bin/nvcc \
  -DCMAKE_INSTALL_RPATH="/opt/cuda-11.7/lib64;\$ORIGIN" \
  -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON
```

### Metal (Apple Silicon)

Enabled by default on macOS:

```bash
cmake -B build
cmake --build build --config Release
```

**Disable Metal:**
```bash
cmake -B build -DGGML_METAL=OFF
```

### HIP (AMD GPU via ROCm)

**Prerequisites:**
- AMD GPU with ROCm support
- ROCm toolkit installed

**Build:**
```bash
cmake -B build -DGGML_HIP=ON
cmake --build build --config Release
```

### Vulkan

**Prerequisites:**
- Vulkan SDK installed
- GPU with Vulkan support

**Build:**
```bash
cmake -B build -DGGML_VULKAN=ON
cmake --build build --config Release
```

### SYCL (Intel GPU)

**Prerequisites:**
- Intel GPU (Data Center Max, Arc, iGPU)
- oneAPI toolkit installed

**Build:**
```bash
source /opt/intel/oneapi/setvars.sh
cmake -B build -DGGML_SYCL=ON
cmake --build build --config Release
```

See [SYCL.md](../../docs/backend/SYCL.md) for detailed Intel GPU setup.

### MUSA (Moore Threads GPU)

**Prerequisites:**
- Moore Threads GPU
- MUSA SDK installed

**Build:**
```bash
cmake -B build -DGGML_MUSA=ON
cmake --build build --config Release
```

## BLAS Acceleration

BLAS improves prompt processing performance for batch sizes > 32.

### OpenBLAS

```bash
# Install OpenBLAS first (e.g., apt install libopenblas-dev)
cmake -B build -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS
cmake --build build --config Release
```

### Intel oneMKL

```bash
source /opt/intel/oneapi/setvars.sh
cmake -B build \
  -DGGML_BLAS=ON \
  -DGGML_BLAS_VENDOR=Intel10_64lp \
  -DCMAKE_C_COMPILER=icx \
  -DCMAKE_CXX_COMPILER=icpx \
  -DGGML_NATIVE=ON
cmake --build build --config Release
```

### Accelerate Framework (macOS)

Enabled by default on macOS. No additional configuration needed.

## Docker Builds

### Pull Pre-built Images

**Full image (all tools):**
```bash
docker pull ghcr.io/ggml-org/llama.cpp:full
```

**Light image (cli only):**
```bash
docker pull ghcr.io/ggml-org/llama.cpp:light
```

**Server image:**
```bash
docker pull ghcr.io/ggml-org/llama.cpp:server
```

**CUDA-enabled:**
```bash
docker pull ghcr.io/ggml-org/llama.cpp:server-cuda
```

### Build Locally

**CUDA Docker:**
```bash
docker build -t local/llama.cpp:full-cuda \
  --target full \
  -f .devops/cuda.Dockerfile .
```

**Build arguments:**
- `CUDA_VERSION` - Default: 12.8.1
- `CUDA_DOCKER_ARCH` - GPU architectures to support

## Build Options Reference

### Common CMake Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `GGML_CUDA` | Bool | OFF | Enable CUDA backend |
| `GGML_METAL` | Bool | ON (macOS) | Enable Metal backend |
| `GGML_HIP` | Bool | OFF | Enable HIP backend |
| `GGML_VULKAN` | Bool | OFF | Enable Vulkan backend |
| `GGML_SYCL` | Bool | OFF | Enable SYCL backend |
| `GGML_NATIVE` | Bool | ON | Optimize for host CPU |
| `GGML_BLAS` | Bool | OFF | Enable BLAS acceleration |
| `GGML_BLAS_VENDOR` | String | Generic | BLAS vendor (OpenBLAS, Intel10_64lp) |
| `BUILD_SHARED_LIBS` | Bool | ON | Build shared libraries |
| `LLAMA_OPENSSL` | Bool | OFF | Enable SSL/TLS support |

### CUDA-Specific Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `GGML_CUDA_FORCE_MMQ` | Bool | false | Force custom MMQ kernels |
| `GGML_CUDA_FORCE_CUBLAS` | Bool | false | Force cuBLAS instead of MMQ |
| `GGML_CUDA_PEER_MAX_BATCH_SIZE` | Int | 128 | Max batch for peer access |
| `CMAKE_CUDA_ARCHITECTURES` | String | native | GPU architectures |

### Runtime Environment Variables

**CUDA:**
```bash
# Hide first GPU
CUDA_VISIBLE_DEVICES="-0" ./llama-server ...

# Enable unified memory (Linux)
GGML_CUDA_ENABLE_UNIFIED_MEMORY=1 ./llama-server ...

# Increase CUDA command buffer
CUDA_SCALE_LAUNCH_QUEUES=4x ./llama-server ...

# Force FP32 compute in cuBLAS
GGML_CUDA_FORCE_CUBLAS_COMPUTE_32F=1 ./llama-server ...
```

## Debug Builds

**Unix Makefiles (single-config):**
```bash
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build
```

**Visual Studio/Xcode (multi-config):**
```bash
cmake -B build -G "Xcode"
cmake --build build --config Debug
```

## Performance Tips

1. **Use Release builds** - Debug builds are 10-50x slower
2. **Enable ccache** - Faster recompilation: `-DCMAKE_CXX_COMPILER_LAUNCHER=ccache`
3. **Parallel compilation** - Use `-j$(nproc)` or Ninja generator
4. **Native optimization** - Keep `GGML_NATIVE=ON` for local use
5. **GPU offloading** - Move as many layers to GPU as VRAM allows

## Troubleshooting

### "Cannot find valid GPU for '-arch=native'"

Specify architectures manually:
```bash
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="86;89"
```

Check your GPU's compute capability: https://developer.nvidia.com/cuda-gpus

### Old CUDA with new glibc

Patch `/path/to/cuda/targets/x86_64-linux/include/crt/math_functions.h`:

```cpp
// Add noexcept(true) to these functions:
extern __device__ double cospi(double x) noexcept(true);
extern __device__ float cospif(float x) noexcept(true);
extern __device__ double sinpi(double x) noexcept(true);
extern __device__ float sinpif(float x) noexcept(true);
```

### Missing OpenSSL (for HTTPS)

**Debian/Ubuntu:**
```bash
sudo apt-get install libssl-dev
```

**Fedora/RHEL:**
```bash
sudo dnf install openssl-devel
```

**Arch:**
```bash
sudo pacman -S openssl
```

Then rebuild with `-DLLAMA_OPENSSL=ON`

## Platform-Specific Notes

### Windows

- Use Developer Command Prompt for Visual Studio
- Install C++ Build Tools with CMake support
- Clang alternative: `cmake --preset x64-windows-llvm-release`

### Windows on ARM (arm64)

```bash
cmake --preset arm64-windows-llvm-release -D GGML_OPENMP=OFF
cmake --build build-arm64-windows-llvm-release
```

### NixOS

Add to `/etc/nixos/configuration.nix`:
```nix
environment.systemPackages = with pkgs; [ llamaCpp ];
```

## Verification

After building, verify installation:

```bash
# Check version
./build/bin/llama-server --version

# List available devices
./build/bin/llama-server --list-devices

# Test with small model
./build/bin/llama-cli -hf ggml-org/gemma-3-1b-it-GGUF -n 32
```
