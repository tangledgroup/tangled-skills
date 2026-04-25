# CUDA GPU Acceleration

For bulk operations on Nvidia GPUs:

```python
import stringzillas as szs

# Use GPU if available
gpu_scope = szs.DeviceScope(gpu_device=0)  # Pick GPU 0

strings_a = sz.Strs(["kitten", "flaw"])
strings_b = sz.Strs(["sitting", "lawn"])

# Optional: transfer to device ahead of time
strings_a = szs.to_device(strings_a)
strings_b = szs.to_device(strings_b)

engine = szs.LevenshteinDistances(match=0, mismatch=2, open=3, extend=1)
distances = engine(strings_a, strings_b, device=gpu_scope)

# CUDA can be 100x faster than CPU for large batches
# Example: 93B CUPS (CUDA Update Per Second) vs 3.4B on x86 CPU
```
