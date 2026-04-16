# Lingua-Py 2.2.0 - Advanced Configuration

Detailed guide to builder options, accuracy modes, loading strategies, and performance tuning.

## Builder Configuration Methods

### Minimum Relative Distance

Set a threshold for confidence gap between top languages to avoid ambiguous detections.

**Purpose**: Prevent false positives when text could belong to multiple similar languages.

```python
from lingua import Language, LanguageDetectorBuilder

# Default (no minimum distance)
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH
).build()

result = detector.detect_language_of("prologue")  # Returns ENGLISH or FRENCH

# With minimum relative distance of 0.9
detector_strict = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH
).with_minimum_relative_distance(0.9).build()

result = detector_strict.detect_language_of("prologue")  # Returns None (too ambiguous)
```

**How it works**:
- Computes logarithmized and summed probabilities for each language
- Requires minimum gap between top two language scores
- Returns `None` if threshold not met

**Recommended values by text length**:
| Text Length | Recommended Distance | Rationale |
|-------------|---------------------|-----------|
| Single word (< 10 chars) | 0.0 - 0.3 | Very few n-grams, low confidence |
| Short phrase (10-50 chars) | 0.3 - 0.6 | Moderate n-gram coverage |
| Medium text (50-200 chars) | 0.6 - 0.8 | Good n-gram coverage |
| Long text (> 200 chars) | 0.8 - 1.0 | High confidence possible |

**Example with adaptive thresholds**:

```python
from lingua import Language, LanguageDetectorBuilder

def detect_with_adaptive_threshold(text, languages):
    """Adjust threshold based on text length."""
    if len(text) < 10:
        distance = 0.2
    elif len(text) < 50:
        distance = 0.5
    elif len(text) < 200:
        distance = 0.7
    else:
        distance = 0.9
    
    detector = LanguageDetectorBuilder.from_languages(*languages).with_minimum_relative_distance(distance).build()
    return detector.detect_language_of(text)

# Usage
languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN]
print(detect_with_adaptive_threshold("hello", languages))  # Lower threshold
print(detect_with_adaptive_threshold("This is a longer sentence with more context", languages))  # Higher threshold
```

---

### Preloaded Language Models (Eager Loading)

Load all language models into memory at detector creation time.

**Purpose**: Eliminate latency from on-demand model loading, ideal for web services.

```python
from lingua import LanguageDetectorBuilder
import time

# Without preloading (lazy loading - default)
start = time.time()
detector_lazy = LanguageDetectorBuilder.from_all_languages().build()
print(f"Detector creation: {time.time() - start:.3f}s")  # Fast (~0.1s)

start = time.time()
result = detector_lazy.detect_language_of("Hello world")
print(f"First detection: {time.time() - start:.3f}s")  # Slower (model loading)

# With preloading (eager loading)
start = time.time()
detector_eager = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()
print(f"Detector creation with preload: {time.time() - start:.3f}s")  # Slower (~1-2s)

start = time.time()
result = detector_eager.detect_language_of("Hello world")
print(f"First detection: {time.time() - start:.3f}s")  # Fast (models already loaded)
```

**When to use**:
- ✅ Web services with consistent request rates
- ✅ Applications where first-request latency matters
- ✅ Multi-threaded applications sharing one detector instance

**When NOT to use**:
- ❌ CLI tools with short runtime
- ❌ Memory-constrained environments
- ❌ Applications detecting only occasionally

**Memory impact**:
```python
from lingua import LanguageDetectorBuilder
import psutil
import os

def get_memory_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

print(f"Initial memory: {get_memory_mb():.1f} MB")

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()
print(f"After preload: {get_memory_mb():.1f} MB")  # ~50-60 MB total
```

**Thread safety**: Preloaded models are shared across all detector instances, loaded only once even with multiple builders.

---

### Low Accuracy Mode

Load only trigram (3-character n-gram) models instead of full n-gram set (1-5 grams).

**Purpose**: Reduce memory usage and improve speed at cost of accuracy on short text.

```python
from lingua import LanguageDetectorBuilder

# High accuracy mode (default) - uses n-grams 1-5
detector_high = LanguageDetectorBuilder.from_all_languages().build()

# Low accuracy mode - uses only trigrams
detector_low = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()
```

**Accuracy comparison by text length**:

| Text Length | High Accuracy Mode | Low Accuracy Mode | Difference |
|-------------|-------------------|-------------------|------------|
| Single word (5-10 chars) | 74% | 45% | -29% |
| Word pair (15-20 chars) | 94% | 82% | -12% |
| Short sentence (30-50 chars) | 98% | 95% | -3% |
| Long text (> 120 chars) | 99% | 98% | -1% |

**When to use**:
- ✅ Processing mostly long documents (> 120 characters)
- ✅ Memory-constrained environments (reduces memory by ~40%)
- ✅ Speed-critical applications with acceptable accuracy trade-off
- ✅ Pre-filtering before high-accuracy detection

**When NOT to use**:
- ❌ Short text detection (tweets, headlines, single words)
- ❌ Mixed-language detection (requires full n-gram models)
- ❌ Applications needing maximum accuracy

**Memory comparison**:
```python
from lingua import LanguageDetectorBuilder
import psutil, os

def get_memory_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

baseline = get_memory_mb()

detector_high = LanguageDetectorBuilder.from_all_languages().build()
memory_high = get_memory_mb() - baseline

detector_low = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()
memory_low = get_memory_mb() - memory_high

print(f"High accuracy mode: ~{memory_high:.1f} MB")  # ~50 MB
print(f"Low accuracy mode: ~{memory_low:.1f} MB")     # ~30 MB
```

**Combined with other options**:

```python
from lingua import LanguageDetectorBuilder

# Low accuracy + preload for fast long-text detection
detector = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().with_preloaded_language_models().build()

# Low accuracy + specific languages for targeted detection
from lingua import Language
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH, Language.FRENCH
).with_low_accuracy_mode().build()
```

---

## Loading Strategies

### Lazy Loading (Default)

Models loaded on-demand when first needed.

**Pros**:
- Fast detector creation
- Lower initial memory usage
- Only loads models for languages actually detected

**Cons**:
- First detection of each language has latency spike
- Unpredictable response times in web services

```python
from lingua import LanguageDetectorBuilder

# Fast creation
detector = LanguageDetectorBuilder.from_all_languages().build()

# First English detection triggers English model load (slower)
result1 = detector.detect_language_of("Hello world")

# Second English detection is fast (model cached)
result2 = detector.detect_language_of("Good morning")

# First Spanish detection triggers Spanish model load (slower again)
result3 = detector.detect_language_of("Hola mundo")
```

### Eager Loading (Preload)

All models loaded at detector creation.

**Pros**:
- Consistent response times
- No latency spikes during detection
- Ideal for production web services

**Cons**:
- Slow detector creation
- Higher initial memory usage
- Loads unused language models

```python
from lingua import LanguageDetectorBuilder

# Slower creation (loads all 75 language models)
detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

# All detections fast (models already in memory)
result1 = detector.detect_language_of("Hello world")   # Fast
result2 = detector.detect_language_of("Hola mundo")    # Fast
result3 = detector.detect_language_of("Bonjour monde") # Fast
```

### Hybrid Strategy

Preload only frequently used languages, lazy-load others.

```python
from lingua import Language, LanguageDetectorBuilder

# Preload top 10 languages by your usage statistics
frequent_languages = [
    Language.ENGLISH, Language.SPANISH, Language.GERMAN,
    Language.FRENCH, Language.PORTUGUESE, Language.ITALIAN,
    Language.RUSSIAN, Language.JAPANESE, Language.ARABIC, Language.CHINESE
]

detector = LanguageDetectorBuilder.from_languages(*frequent_languages).with_preloaded_language_models().build()

# For less common languages, create separate lazy-loaded detector
fallback_detector = LanguageDetectorBuilder.from_all_languages_without(
    *frequent_languages
).build()

def detect_language(text):
    # Try frequent languages first
    lang = detector.detect_language_of(text)
    if lang:
        return lang
    
    # Fall back to all other languages
    return fallback_detector.detect_language_of(text)
```

---

## Performance Tuning

### Detector Instance Reuse

Create detector once and reuse across all detections.

```python
from lingua import LanguageDetectorBuilder

# WRONG: Creating new detector for each detection
def detect_wrong(text):
    detector = LanguageDetectorBuilder.from_all_languages().build()
    return detector.detect_language_of(text)

# CORRECT: Reuse single detector instance
detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

def detect_correct(text):
    return detector.detect_language_of(text)
```

**Performance impact**:
- Wrong approach: ~100-500ms per detection (detector creation overhead)
- Correct approach: ~1-10ms per detection (just detection logic)

### Thread-Safe Sharing

Single detector instance is safe to use across multiple threads.

```python
from lingua import LanguageDetectorBuilder
from concurrent.futures import ThreadPoolExecutor

# Create single detector (thread-safe)
detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

def detect_text(text):
    return detector.detect_language_of(text)

texts = [
    "Hello world",
    "Hola mundo",
    "Bonjour le monde",
    "Hallo Welt",
    "Ciao mondo"
] * 100  # 500 texts

# Process in parallel using thread pool
with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(detect_text, texts))

print(f"Processed {len(results)} texts")
```

### Language Subset Optimization

Restrict languages to improve speed and accuracy.

```python
from lingua import Language, LanguageDetectorBuilder

# Scenario: Your app only serves European users
european_languages = [
    Language.ENGLISH, Language.GERMAN, Language.FRENCH,
    Language.SPANISH, Language.ITALIAN, Language.PORTUGUESE,
    Language.DUTCH, Language.SWEDISH, Language.NORWEGIAN_BOKMAL,
    Language.DANISH, Language.FINNISH, Language.POLISH,
    Language.CZECH, Language.HUNGARIAN, Language.GREEK,
    Language.RUSSIAN, Language.UKRAINIAN
]

detector = LanguageDetectorBuilder.from_languages(*european_languages).build()

# Benefits:
# 1. Faster detection (fewer models to compare)
# 2. Higher accuracy (less confusion between distant languages)
# 3. Lower memory usage (only loads needed models)
```

**Performance comparison**:

| Configuration | Detection Time (per text) | Memory Usage |
|--------------|--------------------------|--------------|
| All 75 languages | ~5-10ms | ~50 MB |
| 20 languages | ~2-4ms | ~20 MB |
| 5 languages | ~1-2ms | ~8 MB |
| 1 language (single-language mode) | < 1ms | ~1 MB |

---

## Single-Language Mode

When detector is built with exactly one language, it operates in single-language mode.

**Purpose**: Verify if text is written in specific language (binary classification).

```python
from lingua import Language, LanguageDetectorBuilder

# Create detector for English only
detector = LanguageDetectorBuilder.from_languages(Language.ENGLISH).build()

# Returns ENGLISH if text is English, None otherwise
result1 = detector.detect_language_of("Hello world")  # Language.ENGLISH
result2 = detector.detect_language_of("Hola mundo")   # None
result3 = detector.detect_language_of("Bonjour monde") # None
```

**Use cases**:
- Verify language before processing
- Filter documents by language
- Validate user input language

**Implementation details**:
- Uses unique and common n-grams for the single language
- Does not compare against other languages
- Much faster than multi-language detection

**Example: Language filter**:

```python
from lingua import Language, LanguageDetectorBuilder

# Create English-only detector
english_detector = LanguageDetectorBuilder.from_languages(Language.ENGLISH).build()

def is_english(text):
    """Check if text is written in English."""
    return english_detector.detect_language_of(text) == Language.ENGLISH

documents = [
    {"id": 1, "text": "This is an English document"},
    {"id": 2, "text": "Esto es un documento en español"},
    {"id": 3, "text": "Another English text here"}
]

# Filter English documents only
english_docs = [doc for doc in documents if is_english(doc['text'])]
print(f"Found {len(english_docs)} English documents")
```

---

## Configuration Combinations

### Production Web Service

```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()
```

**Rationale**: Consistent response times, acceptable memory usage for servers.

### Mobile Application

```python
from lingua import Language, LanguageDetectorBuilder

# Restrict to most common languages for your target audience
languages = [
    Language.ENGLISH, Language.SPANISH, Language.FRENCH,
    Language.GERMAN, Language.JAPANESE, Language.CHINESE
]

detector = LanguageDetectorBuilder.from_languages(*languages).build()
```

**Rationale**: Lower memory usage, faster detection on limited hardware.

### High-Throughput Batch Processing

```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

# Use parallel methods for batch processing
texts = [...]  # Large list of texts
results = detector.detect_languages_in_parallel_of(texts)
```

**Rationale**: Preloading eliminates loading overhead, parallel methods use all CPU cores.

### Memory-Constrained Environment

```python
from lingua import Language, LanguageDetectorBuilder

languages = [Language.ENGLISH, Language.SPANISH, Language.FRENCH]

detector = LanguageDetectorBuilder.from_languages(*languages).with_low_accuracy_mode().build()
```

**Rationale**: Fewer languages + low accuracy mode = minimal memory footprint (~10 MB).

### Maximum Accuracy for Short Text

```python
from lingua import Language, LanguageDetectorBuilder

languages = [Language.ENGLISH, Language.FRENCH]  # Restrict to reduce confusion

detector = LanguageDetectorBuilder.from_languages(*languages).build()
# High accuracy mode (default), no preload (lazy loading)
```

**Rationale**: Full n-gram models (1-5), restricted language set for better discrimination.

---

## Monitoring and Debugging

### Check Detector Configuration

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH, Language.GERMAN
).with_minimum_relative_distance(0.5).build()

# Inspect supported languages (if API available)
# Note: Lingua doesn't expose supported languages directly in 2.2.0
# You need to track this yourself

supported_languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN]
print(f"Detector supports {len(supported_languages)} languages")
```

### Measure Detection Performance

```python
from lingua import LanguageDetectorBuilder
import time

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

texts = ["Hello world"] * 1000

start = time.time()
results = detector.detect_languages_in_parallel_of(texts)
elapsed = time.time() - start

print(f"Processed 1000 texts in {elapsed:.3f}s")
print(f"Throughput: {1000/elapsed:.1f} texts/second")
```

### Memory Usage Monitoring

```python
from lingua import LanguageDetectorBuilder
import psutil, os

def get_memory_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

initial = get_memory_mb()
print(f"Initial memory: {initial:.1f} MB")

detector = LanguageDetectorBuilder.from_all_languages().build()
after_build = get_memory_mb()
print(f"After build: {after_build:.1f} MB (+{after_build - initial:.1f} MB)")

# Trigger model loading for a few languages
for text in ["Hello", "Hola", "Bonjour", "Hallo"]:
    detector.detect_language_of(text)

after_detection = get_memory_mb()
print(f"After detection: {after_detection:.1f} MB (+{after_detection - after_build:.1f} MB)")
```
