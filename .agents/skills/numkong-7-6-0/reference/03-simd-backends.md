# SIMD Backends and Dispatch

> **Source:** NumKong README, include/README.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## Backend Coverage

NumKong ships 30+ SIMD backends across three architectures:

- **x86:** Haswell (AVX2), Skylake (AVX-512F), Ice Lake (AVX-512 BW/VNNI/VP2INTERSECT), Sapphire Rapids (AVX-512 FP16/AMX), Diamond Rapids
- **ARM:** NEON, DotProd, FP16FML, BFDOT, SVE, SME
- **RISC-V:** RVV, Zvfh, Zvfbfwma

Additional backends: LoongArch, WebAssembly (relaxed v128), PowerPC.

## Compile-Time vs Run-Time Dispatch

**Compile-time dispatch** selects the fastest kernel supported by the target platform at build time — thinner binaries, no indirection overhead, but requires knowing deployment hardware.

**Run-time dispatch** compiles every supported kernel into the binary and picks the best one on the target machine via `nk_capabilities()`. One pointer indirection per call, but a single binary runs everywhere. This is the default for distributed artifacts (Python wheels, Rust crate, JS native modules, shared libs from default CMake build).

```c
// Runtime dispatch
nk_capability_t caps = nk_capabilities();
nk_configure_thread(caps);  // Enable AMX features per thread

if (caps & nk_cap_sapphireamx_k) { /* AMX available */ }

// Manual kernel lookup
nk_metric_dense_punned_t angular = 0;
nk_capability_t used = nk_cap_serial_k;
nk_find_kernel_punned(
    nk_kernel_angular_k, nk_f32_k,
    nk_capabilities(),
    (nk_kernel_punned_t *)&angular, &used);
```

The first call to `nk_capabilities()` initializes the dispatch table; all subsequent calls are lock-free.

When no kernel matches, the dispatcher sets the capabilities mask to zero and fills the function pointer with an error stub that writes `0xFF` into the output (NaN for floats, −1 for signed integers, TYPE_MAX for unsigned).

## Why Not Loop Unrolling

NumKong avoids loop unrolling by design:

- **Modern CPUs already "unroll" in hardware.** Out-of-order engines with reorder buffers of 320–630 entries keep a dozen loop iterations in-flight simultaneously. Physical register files are much larger than architectural registers (Skylake: ~180 physical integer registers behind 16 GPRs, ~168 physical vector registers behind 32 ZMMs). Register renaming extracts cross-iteration parallelism automatically.

- **Unrolling inflates binary size.** With 1,500+ kernel endpoints across 30+ backends, even 2x unrolling would add megabytes to the `.text` section, impacting install size for wheels, npm packages, and crates.

- **Serial tails are a correctness hazard.** Leftover elements after the last full SIMD chunk run through a scalar loop that silently drops FMA fusion, compensated accumulation, and saturating arithmetic. NumKong often uses masked loads instead (`_mm512_maskz_loadu_ps` on AVX-512, predicated `svld1_f32` on SVE), processing every element through the same arithmetic path.

## Performance vs Auto-Vectorization

On Intel Sapphire Rapids, NumKong was benchmarked against auto-vectorized code compiled with GCC 12:

| Kind | GCC 12 f32 | GCC 12 f16 | NumKong f16 | Improvement |
|------|-----------|-----------|-------------|-------------|
| Inner Product | 3,810 K/s | 192 K/s | 5,990 K/s | 31x |
| Cosine Distance | 3,280 K/s | 336 K/s | 6,880 K/s | 20x |
| Euclidean Distance² | 4,620 K/s | 147 K/s | 5,320 K/s | 36x |
| Jensen-Shannon Divergence | 1,180 K/s | 18 K/s | 2,140 K/s | 118x |

NumKong's f16 kernels are faster than GCC's f32 output — not because of unrolling, but because they use F16C conversion instructions, widening FMA pipelines, and compensated accumulation that compilers do not synthesize.

## Platform-Specific Optimizations

### Square Roots and Special Math

Angular distance requires 1/√(‖a‖²·‖b‖²). x86 VSQRTPS takes ~12 cycles followed by VDIVPS at ~11 cycles (~23 total). VRSQRT14PS starts with a 14-bit estimate in ~4 cycles, then one Newton-Raphson iteration reaches full Float32 precision — roughly 3x faster. ARM's FRSQRTE provides only ~8 bits, requiring two Newton-Raphson iterations. NumKong selects the iteration count per platform so the final ULP bound is consistent across ISAs.

### Saturation

Reductions over long arrays use saturating arithmetic because input can be arbitrarily long (Int32 wrapping overflow occurs after just ~17 million Int8 summands). Matrix multiplications don't need saturation because GEMM depth rarely exceeds tens of thousands. x86 provides no saturating 32-bit SIMD add, so NumKong implements saturation via overflow detection with XOR-based unsigned comparison.

## CMake Build Options

- `NK_BUILD_SHARED` — shared library, ON by default for standalone builds, OFF as subdirectory
- `NK_BUILD_TEST` / `NK_BUILD_BENCH` — precision tests and benchmarks, OFF by default
- `NK_DYNAMIC_DISPATCH=1` — compile all backends, select at runtime (recommended)
- `NK_COMPARE_TO_BLAS` / `NK_COMPARE_TO_MKL` — link benchmarks against system BLAS or Intel MKL

Build enforces C99 for C layer and C++23 for C++ layer.

## Cross-Compilation Toolchains

- `cmake/toolchain-aarch64-gnu.cmake` — ARM64 Linux
- `cmake/toolchain-riscv64-gnu.cmake` — RISC-V 64 Linux
- `cmake/toolchain-android-arm64.cmake` — Android ARM64 via NDK
- `cmake/toolchain-x86_64-llvm.cmake` / `toolchain-riscv64-llvm.cmake` — Clang/LLD
- `cmake/toolchain-wasm.cmake`, `toolchain-wasm64.cmake`, `toolchain-wasi.cmake` — WebAssembly

```sh
cmake -B build -D CMAKE_TOOLCHAIN_FILE=cmake/toolchain-aarch64-gnu.cmake
```

## Python Build Notes

Pre-built wheels use `NK_DYNAMIC_DISPATCH=1`. When building from source:

- macOS x86: only AVX2 available; macOS ARM: NEON always, SME requires Apple M4+ with Xcode 16+
- RISC-V builds require Clang and LLD (GCC lacks zvfh, zvfbfwma, zvbb support)
- Windows: MSVC 19.44+ (VS 2022 17.14+) recommended for full AVX-512 with FP16/BF16/VNNI
- No OpenMP dependency; build parallelism via `NK_BUILD_PARALLEL` (defaults to min(cpu_count, 4))

```sh
NK_BUILD_PARALLEL=2 pip install . --no-build-isolation
```

## Rust Backend Selection

The crate uses the `cc` build system with `NK_DYNAMIC_DISPATCH=1` automatically. Individual backends can be disabled via environment variables:

```sh
NK_TARGET_NEON=0 cargo build
NK_TARGET_SVE=0 NK_TARGET_SME=0 cargo build
```

If a backend fails to compile, the build system automatically disables it and retries with remaining backends.

## Validation

Every kernel is validated against 118-bit extended-precision baselines with per-type ULP budgets across log-normal, uniform, and Cauchy input distributions. Tests check triangle inequality, Cauchy-Schwarz bounds, NaN propagation, overflow detection, and probability-simplex constraints for each ISA variant. Results are cross-validated against OpenBLAS, Intel MKL, and Apple Accelerate.
