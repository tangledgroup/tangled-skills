# Lingua-Py 2.2.0 - Troubleshooting

Common issues, limitations, error handling, and solutions for lingua-py.

## Installation Issues

### Python Version Compatibility

**Problem**: Installation fails due to Python version mismatch.

**Error**:
```
ERROR: lingua-language-detector 2.2.0 requires Python >=3.12,<3.15
```

**Solution**: Upgrade Python to version 3.12 or higher.

```bash
# Check current Python version
python --version

# Install Python 3.12+ using pyenv
pyenv install 3.12.0
pyenv local 3.12.0

# Or using system package manager (Ubuntu/Debian)
sudo apt update
sudo apt install python3.12 python3.12-venv

# Create virtual environment with Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate
```

**Verify**:
```python
import sys
print(sys.version)  # Should show 3.12.x or 3.13.x or 3.14.x
```

### Missing System Dependencies (Linux)

**Problem**: Installation fails with compilation errors on Linux.

**Error**:
```
error: command 'gcc' failed with exit code 1
```

**Solution**: Install build dependencies.

**Ubuntu/Debian**:
```bash
sudo apt install build-essential python3-dev
```

**RHEL/CentOS/Fedora**:
```bash
sudo dnf install gcc python3-devel
```

**Arch Linux**:
```bash
sudo pacman -S base-devel python
```

### Wheel Installation Issues

**Problem**: Binary wheel not available for your platform.

**Solution**: Use pre-built wheels from PyPI or build from source.

```bash
# Try installing with --no-build-isolation to use system dependencies
pip install --no-build-isolation lingua-language-detector

# Or install Rust and build from source
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
pip install lingua-language-detector
```

**Note**: Version 2.x uses Rust bindings via PyO3. Pre-built wheels are available for:
- Linux (manylinux): x86_64, aarch64
- macOS: x86_64, arm64 (Apple Silicon)
- Windows: x86_64

---

## Detection Issues

### Low Confidence Scores

**Problem**: All confidence scores are low (< 50%).

**Causes**:
1. Very short text (< 5 characters)
2. Gibberish or random characters
3. Mixed-language content without clear boundaries
4. Language not in detector's supported set

**Solutions**:

**1. Increase text length**:
```python
# Short text - low confidence
text = "cat"
confidences = detector.compute_language_confidence_values(text)
print(confidences[0].value)  # May be < 50%

# Longer text - higher confidence
text = "The cat sat on the mat"
confidences = detector.compute_language_confidence_values(text)
print(confidences[0].value)  # Should be > 90%
```

**2. Check if language is supported**:
```python
from lingua import Language

# Verify your language is in the supported list
supported_languages = Language.all()
print(f"Supported languages: {len(supported_languages)}")

# Check for specific language
if Language.FRENCH in supported_languages:
    print("French is supported")
```

**3. Restrict language set**:
```python
from lingua import Language, LanguageDetectorBuilder

# If you know text is English or French, restrict to those
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH
).build()

# Better confidence than using all 75 languages
```

**4. Use minimum relative distance**:
```python
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH
).with_minimum_relative_distance(0.5).build()

# Returns None if not confident enough
result = detector.detect_language_of("ambiguous text")
if result is None:
    print("Could not determine language with required confidence")
```

### Incorrect Detection for Similar Languages

**Problem**: Dutch detected as Afrikaans, Spanish as Portuguese, etc.

**Cause**: These languages share vocabulary and grammatical structures.

**Solutions**:

**1. Use longer text samples**:
```python
# Short phrase - may be ambiguous
text = "goede dag"  # Could be Dutch or Afrikaans

# Full sentence - more distinctive
text = "Goedemorgen, hoe gaat het met u vandaag?"  # Clearly Dutch
```

**2. Set minimum relative distance**:
```python
detector = LanguageDetectorBuilder.from_languages(
    Language.DUTCH, Language.AFRIKAANS
).with_minimum_relative_distance(0.3).build()

result = detector.detect_language_of("goede dag")
if result is None:
    print("Cannot reliably distinguish between Dutch and Afrikaans")
```

**3. Check confidence gap**:
```python
confidences = detector.compute_language_confidence_values(text)

top_lang = confidences[0].language
top_conf = confidences[0].value
second_conf = confidences[1].value
gap = top_conf - second_conf

if gap < 0.2:
    print(f"Ambiguous detection: {top_lang.name} vs {confidences[1].language.name}")
    print(f"Gap: {gap:.2%} (below threshold)")
else:
    print(f"Confident detection: {top_lang.name}")
```

**4. Use contextual information**:
```python
# If you know the geographic context, restrict languages accordingly
if user_location == "south_africa":
    detector = LanguageDetectorBuilder.from_languages(
        Language.AFRIKAANS, Language.ENGLISH, Language.ZULU
    ).build()
else:
    detector = LanguageDetectorBuilder.from_languages(
        Language.DUTCH, Language.GERMAN, Language.ENGLISH
    ).build()
```

### Empty or None Results

**Problem**: `detect_language_of()` returns `None`.

**Causes**:
1. Empty string input
2. Text too short (< 2 characters)
3. All characters are non-linguistic (numbers, symbols)
4. Minimum relative distance threshold not met
5. Language not in detector's supported set

**Solutions**:

**1. Validate input**:
```python
def safe_detect(text, detector):
    """Safely detect language with input validation."""
    if not text or not text.strip():
        return None
    
    if len(text) < 2:
        return None
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    return detector.detect_language_of(text)

# Usage
result = safe_detect("   ", detector)  # Returns None gracefully
```

**2. Check minimum distance setting**:
```python
# If using minimum relative distance, it might be too high
detector_strict = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH
).with_minimum_relative_distance(0.95).build()

result = detector_strict.detect_language_of("prologue")  # Returns None

# Lower the threshold
detector_loose = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH
).with_minimum_relative_distance(0.3).build()

result = detector_loose.detect_language_of("prologue")  # Returns a language
```

**3. Handle None gracefully**:
```python
language = detector.detect_language_of(user_input)

if language is None:
    # Fallback strategies:
    # 1. Ask user to specify language
    # 2. Use default language
    # 3. Flag for manual review
    
    handle_undetermined_language(user_input)
else:
    process_with_language(language, user_input)
```

### Script Detection Issues

**Problem**: Languages with unique scripts (Arabic, Chinese, Cyrillic) not detected correctly.

**Cause**: Text encoding issues or mixed scripts.

**Solutions**:

**1. Ensure proper UTF-8 encoding**:
```python
# When reading files
with open('text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# When receiving from web APIs
import json
text = response.text.encode('utf-8').decode('utf-8')
```

**2. Check for encoding corruption**:
```python
def is_valid_unicode(text):
    """Check if text contains valid Unicode characters."""
    try:
        text.encode('utf-8').decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

if not is_valid_unicode(text):
    print("Warning: Text may have encoding issues")
```

**3. Use script-specific detectors**:
```python
from lingua import LanguageDetectorBuilder

# Cyrillic-only detector for better accuracy on Cyrillic texts
cyrillic_detector = LanguageDetectorBuilder.from_all_languages_with_cyrillic_script().build()

result = cyrillic_detector.detect_language_of("Привет мир")  # Better accuracy
```

---

## Performance Issues

### Slow Detection Speed

**Problem**: Language detection is slower than expected.

**Causes**:
1. Lazy loading of language models on first use
2. Using all 75 languages when fewer would suffice
3. Not using parallel processing for batch operations
4. High-accuracy mode with short texts

**Solutions**:

**1. Preload language models**:
```python
# Slow: Models loaded on-demand
detector = LanguageDetectorBuilder.from_all_languages().build()
result1 = detector.detect_language_of("Hello")  # Slow (loads English model)
result2 = detector.detect_language_of("Hola")   # Slow (loads Spanish model)

# Fast: All models preloaded
detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()
result1 = detector.detect_language_of("Hello")  # Fast
result2 = detector.detect_language_of("Hola")   # Fast
```

**2. Restrict language set**:
```python
# Slower: All 75 languages
detector_all = LanguageDetectorBuilder.from_all_languages().build()

# Faster: Only needed languages
from lingua import Language
detector_subset = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH, Language.FRENCH
).build()
```

**3. Use parallel processing**:
```python
# Slow: Sequential processing
results = [detector.detect_language_of(text) for text in texts]

# Fast: Parallel processing
results = detector.detect_languages_in_parallel_of(texts)
```

**4. Use low-accuracy mode for long texts**:
```python
# If processing mostly long documents (> 120 chars)
detector = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()
```

### High Memory Usage

**Problem**: Application uses too much memory.

**Cause**: All 75 language models loaded into memory (~50-60 MB).

**Solutions**:

**1. Use lazy loading (default)**:
```python
# Don't use with_preloaded_language_models() unless needed
detector = LanguageDetectorBuilder.from_all_languages().build()  # Lazy loading
```

**2. Restrict language set**:
```python
from lingua import Language

# Load only needed languages
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH, Language.FRENCH,
    Language.GERMAN, Language.FRENCH, Language.ITALIAN
).build()  # ~10 MB instead of ~50 MB
```

**3. Use low-accuracy mode**:
```python
# Reduces memory by ~40% (only loads trigram models)
detector = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()
```

**4. Create detectors on-demand**:
```python
# For infrequent detection tasks, create detector per use
def detect_language(text, languages):
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    return detector.detect_language_of(text)
```

### CPU Usage Spikes

**Problem**: High CPU usage during detection.

**Cause**: Parallel processing using all CPU cores.

**Solutions**:

**1. Process in smaller batches**:
```python
# Instead of processing 10,000 texts at once
results = detector.detect_languages_in_parallel_of(all_texts)

# Process in chunks
chunk_size = 1000
for i in range(0, len(texts), chunk_size):
    chunk = texts[i:i + chunk_size]
    results = detector.detect_languages_in_parallel_of(chunk)
    process_results(results)
```

**2. Use single-threaded methods for small batches**:
```python
# For < 100 texts, sequential may be faster (less overhead)
if len(texts) < 100:
    results = [detector.detect_language_of(text) for text in texts]
else:
    results = detector.detect_languages_in_parallel_of(texts)
```

---

## API Usage Issues

### PyO3 Enum Limitations

**Problem**: Enums don't behave like native Python enums.

**Issue 1**: Cannot iterate directly over enum.

```python
# WRONG - This won't work
for language in Language:
    print(language)

# CORRECT - Use .all() method
for language in sorted(Language.all()):
    print(language)
```

**Issue 2**: Enums are not subscriptable.

```python
# WRONG - This won't work
language = Language["ENGLISH"]

# CORRECT - Use from_str() method
language = Language.from_str("english")  # Case-insensitive
language = Language.from_str("ENGLISH")
language = Language.from_str("EngLish")
```

**Issue 3**: Cannot use enum methods like .name directly in some contexts.

```python
# Access name property correctly
language = Language.ENGLISH
print(language.name)  # 'ENGLISH'

# Convert to string
str(language)  # 'Language.ENGLISH'
```

### Type Hint Issues

**Problem**: Type checkers complain about return types.

**Solution**: Use correct type hints for Lingua's PyO3 types.

```python
from lingua import Language, LanguageDetector, LanguageDetectorBuilder
from typing import Optional, List

def detect_language(text: str, detector: LanguageDetector) -> Optional[Language]:
    """Detect language with proper type hints."""
    return detector.detect_language_of(text)  # Returns Language | None

def detect_batch(texts: List[str], detector: LanguageDetector) -> List[Optional[Language]]:
    """Detect languages for multiple texts."""
    return detector.detect_languages_in_parallel_of(texts)  # Returns list[Language | None]
```

---

## Version Migration

### Migrating from 1.x to 2.x

**Breaking changes**:

**1. Installation package name changed**:
```python
# Version 1.x (pure Python)
pip install lingua-language-detector  # Same name, different implementation

# Version 2.x (Rust bindings)
pip install lingua-language-detector  # Now uses Rust via PyO3
```

**2. Python version requirement**:
```python
# Version 1.x: Python >= 3.7
# Version 2.x: Python >= 3.12, < 3.15
```

**3. Enum behavior changed**:
```python
# Version 1.x (native Python enum)
for language in Language:  # Works in 1.x
    print(language)

# Version 2.x (PyO3 enum)
for language in sorted(Language.all()):  # Must use .all() in 2.x
    print(language)
```

**4. Performance characteristics**:
```python
# Version 1.x: Slower, higher memory (800 MB - 3 GB)
# Version 2.x: Faster, lower memory (~50 MB)
```

**Migration checklist**:
- [ ] Upgrade Python to 3.12+
- [ ] Update code that iterates over Language enum
- [ ] Update code that uses Language["NAME"] syntax
- [ ] Test detection accuracy (may differ slightly due to Rust implementation)
- [ ] Update type hints if using static type checking

### Using Pure Python Implementation

If you cannot use version 2.x (e.g., Python < 3.12 or no native extensions):

```bash
# Install version 1.x specifically
pip install lingua-language-detector==1.2.0
```

**Note**: Version 1.x is maintained but receives only security updates. New features are in 2.x.

---

## Debugging Tools

### Enable Verbose Logging

Lingua doesn't have built-in logging, but you can add instrumentation:

```python
import time
from lingua import LanguageDetectorBuilder

class DebugDetector:
    """Wrapper for debugging detection performance."""
    
    def __init__(self, detector):
        self.detector = detector
        self.call_count = 0
        self.total_time = 0
    
    def detect_language_of(self, text):
        self.call_count += 1
        start = time.time()
        
        result = self.detector.detect_language_of(text)
        
        elapsed = time.time() - start
        self.total_time += elapsed
        
        print(f"[{self.call_count}] Detected {result} in {elapsed*1000:.2f}ms")
        print(f"  Text: '{text[:50]}...'")
        
        return result

# Usage
detector = LanguageDetectorBuilder.from_all_languages().build()
debug_detector = DebugDetector(detector)

debug_detector.detect_language_of("Hello world")
debug_detector.detect_language_of("Hola mundo")

print(f"\nAverage detection time: {debug_detector.total_time/debug_detector.call_count*1000:.2f}ms")
```

### Memory Profiling

Track memory usage during detection:

```python
import psutil
import os
from lingua import LanguageDetectorBuilder

def get_memory_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

baseline = get_memory_mb()
print(f"Baseline memory: {baseline:.1f} MB")

detector = LanguageDetectorBuilder.from_all_languages().build()
after_build = get_memory_mb()
print(f"After detector build: {after_build:.1f} MB (+{after_build - baseline:.1f})")

# Trigger detection for various languages
texts = ["Hello", "Hola", "Bonjour", "Hallo", "Ciao"]
for text in texts:
    detector.detect_language_of(text)

after_detection = get_memory_mb()
print(f"After detections: {after_detection:.1f} MB (+{after_detection - after_build:.1f})")
```

### Performance Benchmarking

Benchmark detection performance:

```python
import time
from lingua import LanguageDetectorBuilder

def benchmark_detector(detector, texts, name="Detector"):
    """Benchmark detection performance."""
    # Warm up
    for _ in range(10):
        detector.detect_language_of(texts[0])
    
    # Benchmark sequential
    start = time.time()
    for _ in range(100):
        [detector.detect_language_of(text) for text in texts]
    seq_time = time.time() - start
    
    # Benchmark parallel
    start = time.time()
    for _ in range(100):
        detector.detect_languages_in_parallel_of(texts)
    par_time = time.time() - start
    
    print(f"\n{name}:")
    print(f"  Sequential: {seq_time*1000:.1f}ms (100 iterations × {len(texts)} texts)")
    print(f"  Parallel:   {par_time*1000:.1f}ms (100 iterations × {len(texts)} texts)")
    print(f"  Speedup:    {seq_time/par_time:.2f}x")

# Create detectors
detector_all = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()
detector_subset = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH, Language.FRENCH
).with_preloaded_language_models().build()

texts = ["Hello world", "Hola mundo", "Bonjour le monde"] * 10

benchmark_detector(detector_all, texts, "All Languages (75)")
benchmark_detector(detector_subset, texts, "Subset (3 languages)")
```

---

## Best Practices Summary

### Do's

✅ **Preload models for web services**: Use `with_preloaded_language_models()` to eliminate latency spikes
✅ **Restrict language sets**: Only include languages you actually need
✅ **Reuse detector instances**: Create once, use many times
✅ **Use parallel methods for batches**: Process multiple texts efficiently
✅ **Validate input**: Check for empty strings and very short texts
✅ **Handle None results**: Always check if detection returns `None`
✅ **Check confidence values**: Don't blindly trust low-confidence detections

### Don'ts

❌ **Create detector per request**: Reuse instances for performance
❌ **Use all 75 languages unnecessarily**: Restrict to your use case
❌ **Expect perfect word-level accuracy**: Mixed-language detection is experimental
❌ **Ignore confidence thresholds**: Set appropriate minimums for your use case
❌ **Use low-accuracy mode for short texts**: Accuracy drops significantly
❌ **Assume dialect detection**: Lingua detects languages, not dialects

---

## Getting Help

### Resources

- **GitHub Issues**: https://github.com/pemistahl/lingua-py/issues
- **Documentation**: README.md in repository
- **Rust implementation**: https://github.com/pemistahl/lingua-rs
- **PyPI page**: https://pypi.org/project/lingua-language-detector

### When to File a Bug

File an issue if you encounter:

- Crashes or exceptions during detection
- Consistently incorrect detections with high confidence
- Performance significantly worse than documented
- Installation failures on supported platforms
- Missing languages that should be supported

### Before Filing an Issue

1. Check existing issues for similar problems
2. Verify Python version is >= 3.12, < 3.15
3. Test with latest version from PyPI
4. Prepare minimal reproducible example
5. Include lingua-py version: `pip show lingua-language-detector`
