# Platform Support and Capabilities

StringZilla auto-detects and dispatches to the best available SIMD backend:

**x86_64 CPUs:**
- Westmere (SSE4.2 + AES-NI)
- Haswell (AVX2)
- Skylake (AVX-512)
- Ice Lake (AVX-512 VBMI + wider AES)

**ARM64 CPUs:**
- NEON
- NEON + AES
- NEON + SHA
- SVE (Scalable Vector Extension)
- SVE2 + AES

**GPUs:**
- CUDA (Kepler through Hopper architectures)
- ROCm (AMD GPUs)

Check available capabilities:

```python
import stringzilla
print(stringzilla.__capabilities__)  # ['serial', 'haswell', 'neon', ...]
```
