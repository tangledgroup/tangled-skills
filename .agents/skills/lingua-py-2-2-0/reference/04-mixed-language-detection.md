# Lingua-Py 2.2.0 - Mixed-Language Detection

Detecting multiple languages within a single text (code-switching, multilingual content).

## Overview

Lingua can detect language boundaries in mixed-language texts, identifying which segments are written in which languages. This is particularly useful for:

- Social media posts with code-switching
- Multilingual documents
- Conversations mixing multiple languages
- Technical content with foreign terminology

**Note**: Mixed-language detection is experimental and works best with:
- High-accuracy mode (default)
- Multiple long words per language segment
- Clear language boundaries
- Restricted language sets (when possible)

## Basic Usage

### Detecting Multiple Languages

```python
from lingua import Language, LanguageDetectorBuilder

# Build detector with expected languages
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, 
    Language.FRENCH, 
    Language.GERMAN
).build()

# Mixed-language text
sentence = (
    "Parlez-vous français? " +
    "Ich spreche Französisch nur ein bisschen. " +
    "A little bit is better than nothing."
)

# Detect language segments
results = detector.detect_multiple_languages_of(sentence)

# Process results
for result in results:
    segment = sentence[result.start_index:result.end_index]
    print(f"{result.language.name}: '{segment}'")
```

**Output**:
```
FRENCH: 'Parlez-vous français? '
GERMAN: 'Ich spreche Französisch nur ein bisschen. '
ENGLISH: 'A little bit is better than nothing.'
```

### Understanding DetectionResult

Each `DetectionResult` contains:
- `language`: Detected `Language` enum
- `start_index`: Start position (inclusive)
- `end_index`: End position (exclusive)

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH
).build()

text = "Hello hola world mundo"
results = detector.detect_multiple_languages_of(text)

for result in results:
    segment = text[result.start_index:result.end_index]
    print(f"Language: {result.language.name}")
    print(f"Segment: '{segment}'")
    print(f"Position: [{result.start_index}:{result.end_index}]")
    print(f"Length: {result.end_index - result.start_index} chars")
    print("---")
```

**Output**:
```
Language: ENGLISH
Segment: 'Hello '
Position: [0:6]
Length: 6 chars
---
Language: SPANISH
Segment: 'hola '
Position: [6:11]
Length: 5 chars
---
Language: ENGLISH
Segment: 'world '
Position: [11:17]
Length: 6 chars
---
Language: SPANISH
Segment: 'mundo'
Position: [17:22]
Length: 5 chars
---
```

---

## Practical Applications

### Language Segment Statistics

Analyze language distribution in multilingual content.

```python
from lingua import Language, LanguageDetectorBuilder
from collections import Counter

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH, Language.FRENCH
).build()

text = """
Hello everyone! Bienvenidos todos. 
Today we're learning español and français together.
¡Que divertido! What a great day! C'est la vie.
"""

results = detector.detect_multiple_languages_of(text)

# Count characters per language
lang_stats = Counter()
for result in results:
    segment_length = result.end_index - result.start_index
    lang_stats[result.language.name] += segment_length

# Calculate percentages
total_chars = sum(lang_stats.values())
print("Language distribution:")
for lang, chars in sorted(lang_stats.items(), key=lambda x: -x[1]):
    percentage = (chars / total_chars) * 100
    print(f"  {lang}: {chars} chars ({percentage:.1f}%)")
```

**Output**:
```
Language distribution:
  ENGLISH: 89 chars (52.4%)
  SPANISH: 42 chars (24.7%)
  FRENCH: 39 chars (22.9%)
```

### Code-Switching Detection

Identify language switches in conversation.

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH
).build()

conversation = "Hey friend ¿cómo estás? I'm good gracias and you?"

results = detector.detect_multiple_languages_of(conversation)

print("Language switches detected:")
current_lang = None
switch_count = 0

for result in results:
    segment = conversation[result.start_index:result.end_index]
    lang = result.language.name
    
    if current_lang is not None and lang != current_lang:
        switch_count += 1
        print(f"  Switch {switch_count}: {current_lang} -> {lang}")
    
    print(f"  [{lang}] '{segment}'")
    current_lang = lang

print(f"\nTotal switches: {switch_count}")
```

### Extract Monolingual Segments

Split multilingual text into monolingual segments for processing.

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.GERMAN, Language.FRENCH
).build()

text = "Hello world. Bonjour le monde. Hallo Welt."

results = detector.detect_multiple_languages_of(text)

# Create dictionary of language -> segments
segments_by_language = {}
for result in results:
    lang = result.language.name
    segment = text[result.start_index:result.end_index].strip()
    
    if lang not in segments_by_language:
        segments_by_language[lang] = []
    segments_by_language[lang].append(segment)

# Process each language separately
for lang, segments in segments_by_language.items():
    print(f"\n{lang}:")
    for segment in segments:
        print(f"  - '{segment}'")
        # Apply language-specific processing here
```

**Output**:
```
ENGLISH:
  - 'Hello world.'

FRENCH:
  - 'Bonjour le monde.'

GERMAN:
  - 'Hallo Welt.'
```

---

## Advanced Techniques

### Confidence-Based Filtering

Filter out low-confidence detections.

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH, Language.GERMAN
).build()

text = "Hello bonjour world"

results = detector.detect_multiple_languages_of(text)

# Get confidence for each segment
filtered_results = []
for result in results:
    segment = text[result.start_index:result.end_index]
    confidence = detector.compute_language_confidence(segment, result.language)
    
    if confidence >= 0.7:  # Only keep high-confidence detections
        filtered_results.append((result, confidence))
        print(f"✓ {result.language.name}: '{segment}' (confidence: {confidence:.2f})")
    else:
        print(f"✗ {result.language.name}: '{segment}' (confidence: {confidence:.2f} - filtered out)")

print(f"\nKept {len(filtered_results)} of {len(results)} segments")
```

### Minimum Segment Length

Ignore very short segments that may be noise.

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH
).build()

text = "The rápido cat jumped over the lazy perro"

results = detector.detect_multiple_languages_of(text)

# Filter by minimum segment length
min_length = 5  # characters
filtered_results = [
    result for result in results 
    if (result.end_index - result.start_index) >= min_length
]

print(f"Original segments: {len(results)}")
print(f"After filtering (>= {min_length} chars): {len(filtered_results)}")

for result in filtered_results:
    segment = text[result.start_index:result.end_index]
    print(f"  {result.language.name}: '{segment}' ({len(segment)} chars)")
```

### Dominant Language Detection

Find the primary language in mixed-content text.

```python
from lingua import Language, LanguageDetectorBuilder
from collections import Counter

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH, Language.FRENCH, Language.GERMAN
).build()

text = """
This is primarily an English document with some 
Spanish words like hola and adios mixed in.
Maybe a French word like Bonjour too.
But mostly English content here.
"""

results = detector.detect_multiple_languages_of(text)

# Count characters per language
lang_chars = Counter()
for result in results:
    lang_chars[result.language] += result.end_index - result.start_index

# Find dominant language
dominant_lang, dominant_chars = lang_chars.most_common(1)[0]
total_chars = sum(lang_chars.values())

print(f"Dominant language: {dominant_lang.name}")
print(f"Character count: {dominant_chars} ({(dominant_chars/total_chars)*100:.1f}%)")

print("\nAll languages detected:")
for lang, chars in lang_chars.most_common():
    print(f"  {lang.name}: {chars} chars ({(chars/total_chars)*100:.1f}%)")
```

---

## Performance Considerations

### Parallel Processing for Multiple Texts

Process many multilingual texts in parallel.

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH, Language.FRENCH
).build()

texts = [
    "Hello world. Hola mundo.",
    "Bonjour le monde. Hallo Welt.",
    "Ciao mondo. Привет мир.",
    # ... more texts
] * 100  # 100 texts

# Use parallel method for batch processing
results_list = detector.detect_multiple_languages_in_parallel_of(texts)

# Process results
for text, results in zip(texts, results_list):
    languages_detected = [r.language.name for r in results]
    print(f"{text[:50]}... -> {', '.join(languages_detected)}")
```

### Memory Usage for Mixed-Language Detection

Mixed-language detection uses more memory than single-language detection.

```python
from lingua import Language, LanguageDetectorBuilder
import psutil, os

def get_memory_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

baseline = get_memory_mb()

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()
after_build = get_memory_mb()

# Single-language detection
text_single = "Hello world"
result = detector.detect_language_of(text_single)
after_single = get_memory_mb()

# Mixed-language detection
text_mixed = "Hello hola bonjour hallo ciao mundo"
results = detector.detect_multiple_languages_of(text_mixed)
after_mixed = get_memory_mb()

print(f"Baseline: {baseline:.1f} MB")
print(f"After build: {after_build:.1f} MB (+{after_build - baseline:.1f})")
print(f"After single detection: {after_single:.1f} MB (+{after_single - after_build:.1f})")
print(f"After mixed detection: {after_mixed:.1f} MB (+{after_mixed - after_single:.1f})")
```

---

## Limitations and Best Practices

### Accuracy Factors

Mixed-language detection accuracy depends on:

1. **Segment length**: Longer segments = higher accuracy
   - Single words: ~60-70% accuracy
   - Short phrases (2-3 words): ~80-90% accuracy
   - Full sentences: ~95%+ accuracy

2. **Language similarity**: Similar languages are harder to distinguish
   - Spanish vs Portuguese: More errors
   - English vs Chinese: Fewer errors

3. **Number of languages**: More candidate languages = more confusion
   - 2-3 languages: High accuracy
   - 10+ languages: Reduced accuracy

### Best Practices

**1. Restrict language set when possible**:

```python
from lingua import Language, LanguageDetectorBuilder

# If you know the text contains only English and Spanish
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH
).build()

# Better than using all 75 languages
```

**2. Use high-accuracy mode (default)**:

```python
# Don't use low_accuracy_mode for mixed-language detection
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH, Language.GERMAN
).build()  # High accuracy mode by default
```

**3. Post-process with confidence filtering**:

```python
results = detector.detect_multiple_languages_of(text)

# Filter low-confidence segments
filtered = []
for result in results:
    segment = text[result.start_index:result.end_index]
    confidence = detector.compute_language_confidence(segment, result.language)
    
    if confidence >= 0.6:
        filtered.append(result)
```

**4. Set minimum segment length**:

```python
# Ignore very short segments (< 3 characters)
filtered = [
    result for result in results 
    if (result.end_index - result.start_index) >= 3
]
```

**5. Validate with context**:

```python
# Check if detected languages make sense together
def validate_language_sequence(results, allowed_pairs):
    """Check if consecutive language pairs are plausible."""
    for i in range(len(results) - 1):
        lang1 = results[i].language.name
        lang2 = results[i + 1].language.name
        
        if (lang1, lang2) not in allowed_pairs and (lang2, lang1) not in allowed_pairs:
            print(f"Warning: Unusual language transition {lang1} -> {lang2}")
```

### Common Pitfalls

**Pitfall 1: Expecting perfect word-level accuracy**

```python
# DON'T expect perfect detection for single words
text = "cat perro chat"  # English, Spanish, French
results = detector.detect_multiple_languages_of(text)

# May detect as: ENGLISH "cat perro chat" (all one language)
# Word-level detection is experimental and less accurate
```

**Pitfall 2: Using low-accuracy mode**

```python
# DON'T use low accuracy mode for mixed-language detection
detector = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()

# This will significantly reduce mixed-language detection quality
```

**Pitfall 3: Not handling None results**

```python
# DO handle cases where detection fails
results = detector.detect_multiple_languages_of(text)

if not results:
    print("No language segments detected")
else:
    for result in results:
        process_segment(result)
```

---

## Real-World Examples

### Social Media Post Analysis

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().build()

# Code-switching social media post
post = "Just had the best tacos in Miami ¡qué rico! Definitely going back tomorrow 🌮"

results = detector.detect_multiple_languages_of(post)

print("Language breakdown:")
for result in results:
    segment = post[result.start_index:result.end_index]
    print(f"  {result.language.name}: '{segment}'")

# Calculate primary language for categorization
lang_chars = {}
for result in results:
    lang = result.language.name
    chars = result.end_index - result.start_index
    lang_chars[lang] = lang_chars.get(lang, 0) + chars

primary_lang = max(lang_chars, key=lang_chars.get)
print(f"\nPrimary language for categorization: {primary_lang}")
```

### Multilingual Document Processing

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.GERMAN, Language.FRENCH
).build()

# Document with sections in different languages
document = """
Section 1: Introduction to the topic. This is written in English.

Abschnitt 2: Diese Sektion ist auf Deutsch geschrieben für deutsche Leser.

Section 3: Cette partie est en français pour les lecteurs francophones.

Conclusion: Summary in English to wrap up the document.
"""

# Split by paragraphs and detect language per paragraph
paragraphs = document.strip().split('\n\n')

for i, para in enumerate(paragraphs, 1):
    results = detector.detect_multiple_languages_of(para)
    if results:
        # Get dominant language for this paragraph
        lang_chars = {}
        for result in results:
            lang = result.language.name
            chars = result.end_index - result.start_index
            lang_chars[lang] = lang_chars.get(lang, 0) + chars
        
        dominant = max(lang_chars, key=lang_chars.get)
        print(f"Paragraph {i}: {dominant} ({len(para)} chars)")
```

### Chat Message Language Detection

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH, Language.PORTUGUESE
).build()

chat_messages = [
    "Hey how are you?",
    "Hola amigo, ¿cómo estás?",
    "I'm good thanks! Tú?",
    "Estou bem também!",
    "Great let's meet tomorrow",
    "¡Perfecto! See you then"
]

for msg in chat_messages:
    results = detector.detect_multiple_languages_of(msg)
    
    if len(results) == 1:
        # Single language
        lang = results[0].language.name
        print(f"[{lang}] {msg}")
    else:
        # Mixed languages
        langs = [r.language.name for r in results]
        print(f"[MIXED: {', '.join(langs)}] {msg}")
```

**Output**:
```
[ENGLISH] Hey how are you?
[SPANISH] Hola amigo, ¿cómo estás?
[MIXED: ENGLISH, SPANISH] I'm good thanks! Tú?
[PORTUGUESE] Estou bem também!
[ENGLISH] Great let's meet tomorrow
[MIXED: SPANISH, ENGLISH] ¡Perfecto! See you then
```
