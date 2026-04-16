# Lingua-Py 2.2.0 - API Reference

Complete API documentation for all classes, methods, and builder patterns.

## Core Classes

### LanguageDetectorBuilder

Factory class for creating `LanguageDetector` instances with various configuration options.

#### Builder Methods

**from_all_languages()**
```python
from lingua import LanguageDetectorBuilder

# Include all 75 supported languages
detector = LanguageDetectorBuilder.from_all_languages().build()
```

**from_all_spoken_languages()**
```python
from lingua import LanguageDetectorBuilder

# Exclude extinct languages (currently only Latin)
detector = LanguageDetectorBuilder.from_all_spoken_languages().build()
```

**from_all_languages_with_cyrillic_script()**
```python
from lingua import LanguageDetectorBuilder

# Include only Cyrillic-script languages
detector = LanguageDetectorBuilder.from_all_languages_with_cyrillic_script().build()
```

**from_languages(*languages)**
```python
from lingua import Language, LanguageDetectorBuilder

# Specify exact languages to support
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, 
    Language.GERMAN, 
    Language.FRENCH
).build()
```

**from_iso_codes_639_1(*codes)**
```python
from lingua import LanguageDetectorBuilder, IsoCode639_1

# Select languages by ISO 639-1 codes
detector = LanguageDetectorBuilder.from_iso_codes_639_1(
    IsoCode639_1.EN, 
    IsoCode639_1.DE, 
    IsoCode639_1.FR
).build()
```

**from_iso_codes_639_3(*codes)**
```python
from lingua import LanguageDetectorBuilder, IsoCode639_3

# Select languages by ISO 639-3 codes
detector = LanguageDetectorBuilder.from_iso_codes_639_3(
    IsoCode639_3.ENG, 
    IsoCode639_3.DEU, 
    IsoCode639_3.FRA
).build()
```

**from_all_languages_without(*languages)**
```python
from lingua import Language, LanguageDetectorBuilder

# Exclude specific languages from all supported languages
detector = LanguageDetectorBuilder.from_all_languages_without(
    Language.LATIN, 
    Language.ESPERANTO
).build()
```

#### Configuration Methods

**with_minimum_relative_distance(distance)**
```python
from lingua import Language, LanguageDetectorBuilder

# Require minimum confidence gap between top languages
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH
).with_minimum_relative_distance(0.9).build()

# Returns None if distance requirement not met
result = detector.detect_language_of("prologue")  # May return None
```

**with_preloaded_language_models()**
```python
from lingua import LanguageDetectorBuilder

# Eager-load all models into memory (recommended for web services)
detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()
```

**with_low_accuracy_mode()**
```python
from lingua import LanguageDetectorBuilder

# Load only trigram models for faster detection on long texts
detector = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()
```

See [Advanced Configuration](03-advanced-configuration.md) for detailed explanation of these options.

---

### LanguageDetector

Main class for performing language detection operations. Created via `LanguageDetectorBuilder.build()`.

#### Single-Threaded Methods

**detect_language_of(text: str) -> Language | None**
```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().build()

# Detect single language
language = detector.detect_language_of("Hello world")
print(language)  # Language.ENGLISH

# Returns None if detection fails or minimum distance not met
language = detector.detect_language_of("xkcdqw")  # May return None
```

**detect_multiple_languages_of(text: str) -> list[DetectionResult]**
```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH, Language.GERMAN
).build()

sentence = "Parlez-vous français? Ich spreche Deutsch. Hello world."

# Detect language segments in mixed-language text
results = detector.detect_multiple_languages_of(sentence)

for result in results:
    print(f"{result.language.name}: '{sentence[result.start_index:result.end_index]}'")

# Output:
# FRENCH: 'Parlez-vous français? '
# GERMAN: 'Ich spreche Deutsch. '
# ENGLISH: 'Hello world.'
```

**compute_language_confidence_values(text: str) -> list[LanguageConfidence]**
```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH
).build()

# Get confidence scores for all configured languages
confidences = detector.compute_language_confidence_values("languages are awesome")

for confidence in confidences:
    print(f"{confidence.language.name}: {confidence.value:.2f}")

# Output:
# ENGLISH: 0.93
# FRENCH: 0.04
# GERMAN: 0.02
# SPANISH: 0.01
```

**compute_language_confidence(text: str, language: Language) -> float**
```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH, Language.GERMAN
).build()

# Get confidence for specific language
confidence = detector.compute_language_confidence("Bonjour", Language.FRENCH)
print(f"{confidence:.2f}")  # 0.85

# Returns 0.0 if language not supported by detector
confidence = detector.compute_language_confidence("Hola", Language.SPANISH)
print(confidence)  # 0.0
```

#### Multi-Threaded Methods

**detect_languages_in_parallel_of(texts: list[str]) -> list[Language | None]**
```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().build()

texts = [
    "Hello world",
    "Hola mundo",
    "Bonjour le monde",
    "Hallo Welt"
]

# Detect languages for multiple texts in parallel
languages = detector.detect_languages_in_parallel_of(texts)

for text, language in zip(texts, languages):
    print(f"{text}: {language}")
```

**detect_multiple_languages_in_parallel_of(texts: list[str]) -> list[list[DetectionResult]]**
```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().build()

mixed_texts = [
    "Hello world. Hola mundo.",
    "Bonjour le monde. Hallo Welt."
]

# Detect multiple languages in each text, processed in parallel
results = detector.detect_multiple_languages_in_parallel_of(mixed_texts)

for text, detection_results in zip(mixed_texts, results):
    print(f"Text: {text}")
    for result in detection_results:
        print(f"  {result.language.name}: '{text[result.start_index:result.end_index]}'")
```

**compute_language_confidence_values_in_parallel(texts: list[str]) -> list[list[LanguageConfidence]]**
```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH, Language.GERMAN
).build()

texts = ["Hello", "Bonjour", "Hallo"]

# Compute confidence values for all texts in parallel
confidences = detector.compute_language_confidence_values_in_parallel(texts)

for text, confidence_list in zip(texts, confidences):
    print(f"\n{text}:")
    for conf in confidence_list:
        print(f"  {conf.language.name}: {conf.value:.2f}")
```

**compute_language_confidence_in_parallel(texts: list[str], language: Language) -> list[float]**
```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH, Language.GERMAN
).build()

texts = ["Hello world", "Bonjour le monde", "Hallo Welt"]

# Compute confidence for specific language across multiple texts
confidences = detector.compute_language_confidence_in_parallel(texts, Language.ENGLISH)

for text, confidence in zip(texts, confidences):
    print(f"{text}: {confidence:.2f}")
```

---

## Supporting Classes

### Language

Enum representing supported languages. Not a native Python enum due to PyO3 limitations.

**Usage:**
```python
from lingua import Language

# Access by name
print(Language.ENGLISH)  # Language.ENGLISH
print(Language.GERMAN)   # Language.GERMAN

# Get all languages
for lang in sorted(Language.all()):
    print(lang)

# Create from string (case-insensitive)
lang = Language.from_str("german")
print(lang)  # Language.GERMAN

lang = Language.from_str("GeRmAn")
print(lang)  # Language.GERMAN

# Get language name
print(Language.ENGLISH.name)  # 'ENGLISH'
```

**Properties:**
- `name`: String name of the language (e.g., "ENGLISH", "GERMAN")
- `iso_code_639_1`: Two-letter ISO code (e.g., IsoCode639_1.EN)
- `iso_code_639_3`: Three-letter ISO code (e.g., IsoCode639_3.ENG)

### IsoCode639_1

Enum for two-letter ISO 639-1 language codes.

```python
from lingua import IsoCode639_1

# Access by abbreviation
print(IsoCode639_1.EN)   # IsoCode639_1.EN
print(IsoCode639_1.DE)   # IsoCode639_1.DE
print(IsoCode639_1.FR)   # IsoCode639_1.FR

# Get name
print(IsoCode639_1.EN.name)  # 'EN'
```

### IsoCode639_3

Enum for three-letter ISO 639-3 language codes.

```python
from lingua import IsoCode639_3

# Access by abbreviation
print(IsoCode639_3.ENG)  # IsoCode639_3.ENG
print(IsoCode639_3.DEU)  # IsoCode639_3.DEU
print(IsoCode639_3.FRA)  # IsoCode639_3.FRA

# Get name
print(IsoCode639_3.ENG.name)  # 'ENG'
```

### DetectionResult

Represents a detected language segment in mixed-language text detection.

**Properties:**
- `language: Language` - Detected language
- `start_index: int` - Start position in original text (inclusive)
- `end_index: int` - End position in original text (exclusive)

**Usage:**
```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH
).build()

text = "Hello monde"
results = detector.detect_multiple_languages_of(text)

for result in results:
    segment = text[result.start_index:result.end_index]
    print(f"{result.language.name}: '{segment}' (indices {result.start_index}-{result.end_index})")
```

### LanguageConfidence

Represents confidence score for a specific language.

**Properties:**
- `language: Language` - The language
- `value: float` - Confidence value between 0.0 and 1.0

**Usage:**
```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH, Language.GERMAN
).build()

confidences = detector.compute_language_confidence_values("Hello world")

for conf in confidences:
    print(f"{conf.language.name}: {conf.value:.2f}")

# Values sum to 1.0 across all languages
total = sum(conf.value for conf in confidences)
print(f"Total: {total:.2f}")  # 1.00
```

---

## Method Comparison Table

| Single-Threaded | Multi-Threaded | Input | Output |
|-----------------|----------------|-------|--------|
| `detect_language_of` | `detect_languages_in_parallel_of` | `str` / `list[str]` | `Language \| None` / `list[Language \| None]` |
| `detect_multiple_languages_of` | `detect_multiple_languages_in_parallel_of` | `str` / `list[str]` | `list[DetectionResult]` / `list[list[DetectionResult]]` |
| `compute_language_confidence_values` | `compute_language_confidence_values_in_parallel` | `str` / `list[str]` | `list[LanguageConfidence]` / `list[list[LanguageConfidence]]` |
| `compute_language_confidence` | `compute_language_confidence_in_parallel` | `str, Language` / `list[str], Language` | `float` / `list[float]` |

---

## Complete Example

```python
from lingua import (
    Language, 
    LanguageDetectorBuilder,
    IsoCode639_1,
    IsoCode639_3
)

# Build detector with specific languages
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, 
    Language.FRENCH, 
    Language.GERMAN, 
    Language.SPANISH
).build()

# Single detection
text = "The quick brown fox"
language = detector.detect_language_of(text)

if language:
    print(f"Detected: {language.name}")
    print(f"ISO 639-1: {language.iso_code_639_1.name}")
    print(f"ISO 639-3: {language.iso_code_639_3.name}")
    
    # Get confidence values
    confidences = detector.compute_language_confidence_values(text)
    print("\nConfidence scores:")
    for conf in confidences:
        print(f"  {conf.language.name}: {conf.value:.2%}")
else:
    print("Language could not be determined")

# Batch processing
texts = [
    "Hello world",
    "Bonjour le monde",
    "Hallo Welt",
    "Hola mundo"
]

languages = detector.detect_languages_in_parallel_of(texts)

print("\nBatch detection:")
for text, lang in zip(texts, languages):
    print(f"{text}: {lang.name if lang else 'Unknown'}")
```

---

## Error Handling

Lingua rarely raises exceptions. Detection failures return `None`:

```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().build()

# Empty string returns None
result = detector.detect_language_of("")
print(result)  # None

# Very short gibberish may return None
result = detector.detect_language_of("xk")
print(result)  # May be None

# Handle None gracefully
language = detector.detect_language_of(user_input)
if language:
    process_with_language(language)
else:
    handle_undetermined_language()
```

For minimum relative distance failures, also returns `None`:

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.FRENCH
).with_minimum_relative_distance(0.95).build()

# Ambiguous word may not meet threshold
result = detector.detect_language_of("prologue")  # Returns None
```
