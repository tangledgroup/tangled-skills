# Lingua-Py 2.2.0 - Parallel Processing

Multi-threaded batch processing for high-throughput language detection tasks.

## Overview

Lingua provides multi-threaded versions of all detection methods, allowing you to process multiple texts in parallel using all available CPU cores. This is essential for:

- Batch processing large datasets
- High-throughput web services
- Real-time language detection for many users
- Preprocessing pipelines with thousands of documents

**Thread safety**: All `LanguageDetector` instances are thread-safe and can be shared across threads safely.

## Parallel Methods Reference

### Method Mapping

| Single-Threaded Method | Multi-Threaded Method | Input | Output |
|------------------------|----------------------|-------|--------|
| `detect_language_of(text)` | `detect_languages_in_parallel_of(texts)` | `str` / `list[str]` | `Language \| None` / `list[Language \| None]` |
| `detect_multiple_languages_of(text)` | `detect_multiple_languages_in_parallel_of(texts)` | `str` / `list[str]` | `list[DetectionResult]` / `list[list[DetectionResult]]` |
| `compute_language_confidence_values(text)` | `compute_language_confidence_values_in_parallel(texts)` | `str` / `list[str]` | `list[LanguageConfidence]` / `list[list[LanguageConfidence]]` |
| `compute_language_confidence(text, lang)` | `compute_language_confidence_in_parallel(texts, lang)` | `str, Language` / `list[str], Language` | `float` / `list[float]` |

---

## Basic Usage

### Parallel Single-Language Detection

Detect language for multiple texts in parallel.

```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

texts = [
    "Hello world",
    "Hola mundo",
    "Bonjour le monde",
    "Hallo Welt",
    "Ciao mondo",
    "こんにちは世界"
] * 100  # 600 texts

# Parallel detection
languages = detector.detect_languages_in_parallel_of(texts)

# Process results
for text, lang in zip(texts, languages):
    if lang:
        print(f"{text}: {lang.name}")
    else:
        print(f"{text}: Unknown")
```

### Handling None Results

Some texts may return `None` if detection fails.

```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().build()

texts = [
    "Hello world",      # Detectable
    "xkcdqw",           # Gibberish - may return None
    "",                 # Empty string - returns None
    "Hola mundo"        # Detectable
]

results = detector.detect_languages_in_parallel_of(texts)

for text, lang in zip(texts, results):
    if lang is None:
        print(f"'{text}': Could not detect language")
    else:
        print(f"'{text}': {lang.name}")
```

**Output**:
```
'Hello world': ENGLISH
'xkcdqw': Could not detect language
'': Could not detect language
'Hola mundo': SPANISH
```

---

## Performance Comparison

### Sequential vs Parallel Processing

Compare performance of sequential vs parallel detection.

```python
from lingua import LanguageDetectorBuilder
import time

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

texts = ["Hello world", "Hola mundo", "Bonjour le monde"] * 1000  # 3000 texts

# Sequential processing
start = time.time()
results_seq = [detector.detect_language_of(text) for text in texts]
seq_time = time.time() - start

# Parallel processing
start = time.time()
results_par = detector.detect_languages_in_parallel_of(texts)
par_time = time.time() - start

print(f"Sequential: {seq_time:.3f}s ({len(texts)/seq_time:.1f} texts/sec)")
print(f"Parallel:   {par_time:.3f}s ({len(texts)/par_time:.1f} texts/sec)")
print(f"Speedup:    {seq_time/par_time:.2f}x")
```

**Typical results on 8-core CPU**:
```
Sequential: 0.850s (3529 texts/sec)
Parallel:   0.210s (14286 texts/sec)
Speedup:    4.05x
```

### Scaling with Text Count

Performance scales well with increasing text count.

```python
from lingua import LanguageDetectorBuilder
import time

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

for count in [100, 500, 1000, 5000, 10000]:
    texts = ["Hello world"] * count
    
    start = time.time()
    results = detector.detect_languages_in_parallel_of(texts)
    elapsed = time.time() - start
    
    print(f"{count:6d} texts: {elapsed:.3f}s ({count/elapsed:.1f} texts/sec)")
```

**Typical output**:
```
   100 texts: 0.015s (6667 texts/sec)
   500 texts: 0.045s (11111 texts/sec)
  1000 texts: 0.082s (12195 texts/sec)
  5000 texts: 0.365s (13699 texts/sec)
 10000 texts: 0.742s (13477 texts/sec)
```

---

## Advanced Use Cases

### Parallel Mixed-Language Detection

Detect multiple languages in each text, processed in parallel.

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH, Language.FRENCH
).build()

mixed_texts = [
    "Hello world. Hola mundo.",
    "Bonjour le monde. Hallo Welt.",
    "Ciao mondo. Привет мир.",
    "This is English with español words mixed."
] * 100

# Parallel mixed-language detection
results_list = detector.detect_multiple_languages_in_parallel_of(mixed_texts)

# Process results
for text, results in zip(mixed_texts[:5], results_list[:5]):  # Show first 5
    langs = [r.language.name for r in results]
    print(f"{text[:50]}...")
    print(f"  Languages: {', '.join(langs)}")
    print()
```

### Parallel Confidence Computation

Compute confidence values for all texts in parallel.

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH, Language.GERMAN
).build()

texts = [
    "Hello world",
    "Bonjour le monde",
    "Hallo Welt",
    "This is clearly English text"
] * 100

# Get confidence values for all languages, for all texts
confidence_lists = detector.compute_language_confidence_values_in_parallel(texts)

# Analyze results
for i, (text, confidences) in enumerate(zip(texts[:5], confidence_lists[:5])):
    print(f"\nText {i+1}: {text}")
    for conf in confidences:
        print(f"  {conf.language.name}: {conf.value:.2%}")
```

### Parallel Single-Language Confidence

Compute confidence for one specific language across many texts.

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH, Language.FRENCH
).build()

texts = [
    "Hello world",              # High English confidence
    "Hola mundo",               # Low English confidence
    "Bonjour le monde",         # Low English confidence
    "This is definitely English"  # Very high English confidence
] * 100

# Compute English confidence for all texts in parallel
english_confidences = detector.compute_language_confidence_in_parallel(
    texts, Language.ENGLISH
)

# Filter texts with high English confidence
threshold = 0.8
high_confidence_texts = [
    (text, conf) for text, conf in zip(texts, english_confidences)
    if conf >= threshold
]

print(f"Found {len(high_confidence_texts)} texts with >= {threshold} English confidence")

# Show examples
for text, conf in high_confidence_texts[:5]:
    print(f"  {conf:.2%}: {text}")
```

---

## Batch Processing Patterns

### Chunked Processing

Process very large datasets in chunks to manage memory.

```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

def process_in_chunks(texts, chunk_size=1000):
    """Process texts in chunks to manage memory."""
    all_results = []
    
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        results = detector.detect_languages_in_parallel_of(chunk)
        all_results.extend(results)
        
        # Progress reporting
        processed = min(i + chunk_size, len(texts))
        print(f"Progress: {processed}/{len(texts)} ({processed/len(texts)*100:.1f}%)")
    
    return all_results

# Usage with large dataset
texts = ["Hello world"] * 100000  # 100,000 texts
results = process_in_chunks(texts, chunk_size=5000)

print(f"\nProcessed {len(results)} texts")
```

### Progress Tracking with Tqdm

Use tqdm for progress bars during batch processing.

```python
from lingua import LanguageDetectorBuilder
from tqdm import tqdm

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

texts = ["Hello world"] * 10000

# Process in chunks with progress bar
chunk_size = 1000
all_results = []

for i in tqdm(range(0, len(texts), chunk_size), desc="Detecting languages"):
    chunk = texts[i:i + chunk_size]
    results = detector.detect_languages_in_parallel_of(chunk)
    all_results.extend(results)

print(f"Completed: {len(all_results)} detections")
```

### Error Handling in Batch Processing

Handle exceptions gracefully when processing large batches.

```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().build()

def safe_batch_detection(texts, chunk_size=1000):
    """Process texts with error handling."""
    results = []
    errors = []
    
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        chunk_indices = range(i, min(i + chunk_size, len(texts)))
        
        try:
            chunk_results = detector.detect_languages_in_parallel_of(chunk)
            results.extend(zip(chunk_indices, chunk_results))
            
        except Exception as e:
            # Log error and mark all texts in chunk as failed
            print(f"Error processing chunk {i//chunk_size}: {e}")
            errors.extend([(idx, str(e)) for idx in chunk_indices])
    
    return results, errors

# Usage
texts = ["Hello world"] * 10000
results, errors = safe_batch_detection(texts)

print(f"Successful detections: {len(results)}")
print(f"Errors: {len(errors)}")
```

---

## Performance Optimization

### Optimal Chunk Size

Find the optimal chunk size for your hardware.

```python
from lingua import LanguageDetectorBuilder
import time

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

texts = ["Hello world"] * 10000

# Test different chunk sizes
for chunk_size in [100, 500, 1000, 5000, 10000]:
    start = time.time()
    
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        results = detector.detect_languages_in_parallel_of(chunk)
    
    elapsed = time.time() - start
    print(f"Chunk size {chunk_size:5d}: {elapsed:.3f}s ({len(texts)/elapsed:.1f} texts/sec)")
```

**Typical results**:
```
Chunk size   100: 0.892s (11211 texts/sec)
Chunk size   500: 0.745s (13423 texts/sec)
Chunk size  1000: 0.698s (14327 texts/sec)
Chunk size  5000: 0.712s (14045 texts/sec)
Chunk size 10000: 0.725s (13793 texts/sec)
```

**Recommendation**: Chunk sizes of 1000-5000 typically provide best performance.

### CPU Core Utilization

Lingua automatically uses all available CPU cores in parallel methods.

```python
from lingua import LanguageDetectorBuilder
import psutil

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

print(f"Available CPU cores: {psutil.cpu_count(logical=True)}")

texts = ["Hello world"] * 10000

# Monitor CPU usage during processing
import time

start_time = time.time()
start_cpu = psutil.cpu_percent(interval=None)

results = detector.detect_languages_in_parallel_of(texts)

end_cpu = psutil.cpu_percent(interval=None)
elapsed = time.time() - start_time

print(f"Processing time: {elapsed:.3f}s")
print(f"CPU usage during processing: ~{end_cpu}%")
print(f"Throughput: {len(texts)/elapsed:.1f} texts/sec")
```

### Memory-Efficient Batch Processing

Process large datasets without loading all results into memory.

```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

def process_as_generator(texts, chunk_size=1000):
    """Yield results as they're processed to save memory."""
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        results = detector.detect_languages_in_parallel_of(chunk)
        
        for j, result in enumerate(results):
            yield texts[i + j], result

# Usage - process without storing all results
texts = ["Hello world"] * 100000

english_count = 0
for text, lang in process_as_generator(texts):
    if lang == Language.ENGLISH:
        english_count += 1
    
    # Process each result immediately instead of storing

print(f"Found {english_count} English texts")
```

---

## Real-World Examples

### Document Classification Pipeline

Classify thousands of documents by language.

```python
from lingua import LanguageDetectorBuilder
from collections import Counter

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

# Simulate document corpus
documents = [
    {"id": i, "text": f"Hello world document {i}"} if i % 3 == 0 
    else {"id": i, "text": f"Hola mundo documento {i}"} if i % 3 == 1
    else {"id": i, "text": f"Bonjour le monde document {i}"}
    for i in range(10000)
]

# Extract texts
texts = [doc["text"] for doc in documents]

# Parallel detection
languages = detector.detect_languages_in_parallel_of(texts)

# Add language to documents
for doc, lang in zip(documents, languages):
    doc["language"] = lang.name if lang else "Unknown"

# Count by language
lang_counts = Counter(doc["language"] for doc in documents)

print("Language distribution:")
for lang, count in lang_counts.most_common():
    print(f"  {lang}: {count} documents ({count/len(documents)*100:.1f}%)")
```

### Web Service Request Handling

Handle multiple concurrent requests efficiently.

```python
from lingua import LanguageDetectorBuilder
from concurrent.futures import ThreadPoolExecutor
import time

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

def process_request(request_id, text):
    """Simulate processing a single request."""
    start = time.time()
    language = detector.detect_language_of(text)
    elapsed = time.time() - start
    
    return {
        "request_id": request_id,
        "language": language.name if language else None,
        "processing_time_ms": elapsed * 1000
    }

# Simulate concurrent requests
requests = [
    {"id": i, "text": f"Hello world request {i}"} 
    for i in range(100)
]

# Process with thread pool (simulating web server)
with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(
        lambda r: process_request(r["id"], r["text"]),
        requests
    ))

# Analyze performance
avg_time = sum(r["processing_time_ms"] for r in results) / len(results)
print(f"Average processing time: {avg_time:.2f}ms")
print(f"Throughput: {len(results)/avg_time*1000:.1f} requests/sec")
```

### Data Quality Analysis

Analyze language distribution in large datasets.

```python
from lingua import LanguageDetectorBuilder
from collections import Counter

detector = LanguageDetectorBuilder.from_all_languages().build()

# Load texts from file (simulated)
def load_texts(filename, chunk_size=1000):
    """Generator to load texts in chunks."""
    with open(filename, 'r', encoding='utf-8') as f:
        chunk = []
        for line in f:
            text = line.strip()
            if text:
                chunk.append(text)
                
                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []
        
        if chunk:
            yield chunk

# Process file in chunks
all_languages = []
for chunk in load_texts("large_dataset.txt"):
    languages = detector.detect_languages_in_parallel_of(chunk)
    all_languages.extend([lang.name if lang else "Unknown" for lang in languages])

# Analyze distribution
lang_counts = Counter(all_languages)

print(f"Total texts analyzed: {len(all_languages)}")
print("\nTop 10 languages:")
for lang, count in lang_counts.most_common(10):
    percentage = count / len(all_languages) * 100
    print(f"  {lang}: {count:,} ({percentage:.2f}%)")
```

---

## Troubleshooting

### High Memory Usage

If parallel processing uses too much memory:

```python
# Reduce chunk size
results = detector.detect_languages_in_parallel_of(texts[0:1000])  # Smaller chunks

# Use generator pattern to avoid storing all results
def process_generator(texts, chunk_size=500):
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        results = detector.detect_languages_in_parallel_of(chunk)
        for result in results:
            yield result

for result in process_generator(large_text_list):
    process_result(result)  # Process immediately, don't store
```

### Slow Performance

If parallel processing is slower than expected:

```python
# Ensure models are preloaded
detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

# Use optimal chunk size (1000-5000)
chunk_size = 1000

# Check CPU utilization
import psutil
print(f"CPU cores: {psutil.cpu_count(logical=True)}")
```

### Inconsistent Results

Parallel methods should give identical results to sequential methods.

```python
detector = LanguageDetectorBuilder.from_all_languages().build()

texts = ["Hello", "Hola", "Bonjour"]

# Sequential
seq_results = [detector.detect_language_of(text) for text in texts]

# Parallel
par_results = detector.detect_languages_in_parallel_of(texts)

# Verify identical results
assert seq_results == par_results, "Results should be identical"
print("✓ Sequential and parallel results match")
```
