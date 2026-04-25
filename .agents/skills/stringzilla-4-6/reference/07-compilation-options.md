# Compilation Options

Customize StringZilla behavior via compile-time macros:

```c
// Debug mode
#define SZ_DEBUG 1

// Avoid LibC dependencies (for embedded systems)
#define SZ_AVOID_LIBC 1

// Enable dynamic runtime dispatch
#define SZ_DYNAMIC_DISPATCH 1

// Use misaligned loads (faster on most modern CPUs)
#define SZ_USE_MISALIGNED_LOADS 1

// Performance tuning
#define SZ_SWAR_THRESHOLD 24  // Switch to SWAR over serial for strings > 24 bytes
#define SZ_CACHE_LINE_WIDTH 64  // CPU cache line size
#define SZ_CACHE_SIZE 1048576  // L1d + L2 cache combined

// Enable/disable specific SIMD backends
#define SZ_USE_WESTMERE 1  // SSE4.2 + AES-NI
#define SZ_USE_HASWELL 1   // AVX2
#define SZ_USE_SKYLAKE 1   // AVX-512
#define SZ_USE_ICE 1       // AVX-512 VBMI
#define SZ_USE_NEON 1      // ARM NEON
#define SZ_USE_SVE 1       // ARM SVE
#define SZ_USE_SVE2 1      // ARM SVE2
```
