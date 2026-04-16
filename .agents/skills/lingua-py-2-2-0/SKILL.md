---
name: lingua-py-2-2-0
description: Accurate natural language detection library for Python supporting 75 languages with high accuracy on short text and mixed-language content. Use when building NLP applications requiring language identification, content routing, multilingual support, or preprocessing for text classification and spell checking.
license: Apache-2.0
author: Peter M. Stahl <pemistahl@gmail.com>
version: "2.2.0"
tags:
  - nlp
  - language-detection
  - text-processing
  - multilingual
  - natural-language-processing
category: nlp
external_references:
  - https://github.com/pemistahl/lingua-py
---

# Lingua-Py 2.2.0

## Overview

Lingua is an accurate natural language detection library for Python that identifies which language text is written in. It supports **75 languages** and excels at detecting languages in both long and short text fragments, including single words and mixed-language content. Built on Rust bindings (PyO3) for high performance and low memory usage.

**Key features:**
- 75 supported languages with high detection accuracy
- Works on single words, phrases, and full sentences
- Mixed-language text detection (experimental)
- Offline operation - no external API dependencies
- Thread-safe for concurrent use
- Low memory footprint (~dozens of MB) using finite-state transducers
- Multi-threaded parallel processing for batch operations

## When to Use

Use Lingua when:

- **Language identification**: Need to detect which language text is written in
- **Content routing**: Route emails, documents, or user input to appropriate language-specific handlers
- **NLP preprocessing**: Prepare text for text classification, spell checking, or other NLP tasks
- **Multilingual applications**: Build features that adapt based on detected language
- **Short text detection**: Work with tweets, headlines, or single-word inputs where other libraries fail
- **Mixed-language content**: Identify language boundaries in code-switching or multilingual texts
- **Offline requirements**: Need language detection without internet connectivity

**Do NOT use Lingua when:**
- You need dialect detection (e.g., US vs UK English)
- You require script detection only (use other libraries for this)
- You need to detect programming languages

## Installation

Install via pip from PyPI:

```bash
pip install lingua-language-detector
```

**Requirements:**
- Python >= 3.12, < 3.15
- Compatible with Windows, macOS, Linux

**Verify installation:**

```python
>>> from lingua import Language
>>> print(Language.ENGLISH)
Language.ENGLISH
```

## Quick Start

### Basic Detection

```python
from lingua import Language, LanguageDetectorBuilder

# Build detector for specific languages
languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

# Detect language
language = detector.detect_language_of("languages are awesome")
print(language)  # Language.ENGLISH
```

### Using All Languages

```python
from lingua import LanguageDetectorBuilder

# Build detector with all 75 supported languages
detector = LanguageDetectorBuilder.from_all_languages().build()

# Detect language from any supported language
language = detector.detect_language_of("Hola, ¿cómo estás?")
print(language)  # Language.SPANISH
```

### Getting ISO Codes

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().build()
language = detector.detect_language_of("Bonjour le monde")

# Get ISO 639-1 code (2-letter)
print(language.iso_code_639_1)  # IsoCode639_1.FR
print(language.iso_code_639_1.name)  # 'FR'

# Get ISO 639-3 code (3-letter)
print(language.iso_code_639_3)  # IsoCode639_3.FRA
print(language.iso_code_639_3.name)  # 'FRA'
```

## Supported Languages

Lingua supports 75 languages. See [Language Reference](references/02-language-reference.md) for complete list with ISO codes.

**Popular languages:**
- English, Spanish, French, German, Italian
- Portuguese, Russian, Chinese, Japanese, Korean
- Arabic, Hebrew, Hindi, Turkish
- Dutch, Swedish, Norwegian, Danish, Finnish
- Polish, Czech, Greek, Hungarian, Romanian

See [Language Reference](references/02-language-reference.md) for all 75 languages.

## Core Concepts

### Detection Accuracy

Lingua uses two complementary approaches:

1. **Rule-based engine**: Analyzes alphabet and unique characters to filter impossible languages
2. **Statistical n-gram model**: Uses character n-grams (sizes 1-5) for probabilistic classification

This dual approach provides high accuracy even on short text where trigram-only methods fail.

### Performance Characteristics

| Mode | Time (75 languages, 3000 texts) | Memory |
|------|--------------------------------|--------|
| Low accuracy, multi-threaded | 11.81 sec | ~30 MB |
| High accuracy, multi-threaded | 21.13 sec | ~50 MB |

**Comparison with other libraries:**
- CLD 2: 8.65 sec (C/C++)
- CLD 3: 16.77 sec (C/C++)
- Simplemma: 2 min 36 sec (pure Python)
- Langid: 3 min 50 sec (pure Python)
- Langdetect: 10 min 44 sec (pure Python)

### Thread Safety

The library is fully thread-safe:
- Single `LanguageDetector` instance can be shared across threads
- Language models are loaded once and shared between detector instances
- All detection methods are safe for concurrent use

See [Advanced Configuration](references/03-advanced-configuration.md) for performance tuning.

## Reference Files

For detailed topics, see:

- [`references/01-api-reference.md`](references/01-api-reference.md) - Complete API documentation with all builder methods and detection functions
- [`references/02-language-reference.md`](references/02-language-reference.md) - All 75 supported languages with ISO codes and examples
- [`references/03-advanced-configuration.md`](references/03-advanced-configuration.md) - Builder options, accuracy modes, loading strategies, and performance tuning
- [`references/04-mixed-language-detection.md`](references/04-mixed-language-detection.md) - Detecting multiple languages in code-switching texts
- [`references/05-parallel-processing.md`](references/05-parallel-processing.md) - Multi-threaded batch processing for large datasets
- [`references/06-confidence-values.md`](references/06-confidence-values.md) - Computing and interpreting language confidence scores
- [`references/07-troubleshooting.md`](references/07-troubleshooting.md) - Common issues, limitations, and solutions

## Use Cases

### Content Routing

Route user messages to appropriate language-specific handlers:

```python
from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().build()

def route_message(message):
    language = detector.detect_language_of(message)
    
    if language == Language.ENGLISH:
        return handle_english(message)
    elif language == Language.SPANISH:
        return handle_spanish(message)
    elif language == Language.FRENCH:
        return handle_french(message)
    else:
        return handle_unknown(message, language)
```

### NLP Preprocessing

Add language metadata before text classification:

```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().build()

def preprocess_documents(documents):
    """Add language detection to document list."""
    processed = []
    for doc in documents:
        language = detector.detect_language_of(doc['text'])
        processed.append({
            'id': doc['id'],
            'text': doc['text'],
            'language': language.name if language else None,
            'iso_code': language.iso_code_639_1.name if language else None
        })
    return processed
```

### Short Text Detection

Detect language from tweets or headlines:

```python
from lingua import LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.SPANISH, Language.FRENCH
).build()

# Works on single words
print(detector.detect_language_of("merci"))  # Language.FRENCH

# Works on short phrases  
print(detector.detect_language_of("breaking news"))  # Language.ENGLISH
```

See [Mixed-Language Detection](references/04-mixed-language-detection.md) for code-switching scenarios.

## References

- **Official repository**: https://github.com/pemistahl/lingua-py
- **PyPI package**: https://pypi.org/project/lingua-language-detector
- **Rust implementation**: https://github.com/pemistahl/lingua-rs
- **Apache 2.0 License**: https://www.apache.org/licenses/LICENSE-2.0

## Version Information

- **Current version**: 2.2.0
- **Python compatibility**: >= 3.12, < 3.15
- **Implementation**: Rust with PyO3 bindings
- **Previous pure Python implementation**: Available in `pure-python-impl` branch (version 1.*)

For migration from version 1.x to 2.x, see [Troubleshooting](references/07-troubleshooting.md).
