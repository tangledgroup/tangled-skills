# Troubleshooting

### Issue: Hash values differ between platforms

**Solution:** StringZilla uses stable 64-bit hashing with seed parameter. Ensure you use the same seed value across platforms:

```python
hash1 = sz.hash(b"test", seed=42)  # Always same value on any platform
```

### Issue: Case-folding output buffer too small

**Solution:** Unicode case-folding can expand characters (ß → ss, ﬃ → ffi). Allocate output buffer at least 3× input size:

```python
output = bytearray(len(input_text) * 3)
sz.utf8_case_fold(input_text, output)
```

### Issue: SIMD backend not detected

**Solution:** Check capabilities and ensure compilation flags match CPU features:

```python
import stringzilla
print(stringzilla.__capabilities__)  # Should show available backends

# For C/C++, compile with appropriate flags:
# -mavx2 -mavx512f for x86, or enable NEON/SVE for ARM
```

### Issue: Memory mapping fails on Windows

**Solution:** Use `File` class which handles platform-specific memory mapping:

```python
from stringzilla import File
mapped = File("large-file.txt")  # Works cross-platform
```

### Issue: CUDA backend not available

**Solution:** Install CUDA-specific package and verify GPU availability:

```bash
pip install stringzillas-cuda
python -c "import stringzillas; print(stringzillas.__capabilities__)"  # Should show 'cuda'
```
