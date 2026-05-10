---
name: lingua-py-2-2-0
description: Accurate natural language detection library for Python supporting 75 languages with high accuracy on short text and mixed-language content. Use when building NLP applications requiring language identification, content routing, multilingual support, or preprocessing for text classification and spell checking.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - nlp
  - language-detection
  - text-processing
  - multilingual
  - natural-language-processing
category: nlp
external_references:
  - https://github.com/pemistahl/lingua-py
  - https://github.com/pemistahl/lingua-rs
  - https://pypi.org/project/lingua-language-detector
  - https://www.apache.org/licenses/LICENSE-2.0
compatibility: Python >= 3.12, requires native extension (Rust via PyO3)
---

# Lingua-Py 2.2.0

## Overview

Lingua is an accurate natural language detection library for Python that identifies which language a given text is written in. It supports 75 languages and excels at detecting languages in very short text — even single words and phrases — where most other detectors struggle.

The library combines two approaches: a rule-based engine that filters candidate languages by alphabet and unique characters, and a statistical Naive Bayes model using n-grams of sizes 1 through 5. Unlike competitors that rely only on trigrams (n=3), Lingua's broader n-gram range produces much more reliable probabilities for short input text.

Version 2.x replaces the pure Python implementation with compiled bindings to the native [Rust implementation](https://github.com/pemistahl/lingua-rs) via PyO3, delivering fast performance with a small memory footprint (few dozen megabytes even with all 75 language models). Language models are stored as finite-state transducers (FSTs), allowing disk-based search without full memory loading — suitable for low-resource environments.

The library operates completely offline once installed. No external API calls, no neural networks, no word dictionaries.

## When to Use

- Preprocessing step for NLP pipelines: route text to language-specific classifiers, spell checkers, or translators
- Content routing: direct e-mails or messages to geographically appropriate support departments based on detected language
- Mixed-language text analysis: identify language segments within a single document
- Short-text classification: detect language in Twitter messages, chat messages, or single words where CLD2/CLD3 underperform
- Low-resource environments: when memory is constrained and FST-based models are preferred over neural approaches
- Offline NLP: when no internet connection is available for API-based detection

## Core Concepts

### Detection Pipeline

Lingua uses a two-stage detection pipeline:

1. **Rule-based filter**: Determines the alphabet of input text, searches for characters unique to certain languages, and filters out impossible candidates. If exactly one language remains, the statistical model is skipped entirely.
2. **Statistical n-gram model**: For remaining candidates, computes log-probabilities using character n-grams of sizes 1–5 (unigrams through 5-grams). The language with the highest probability wins.

### Language Models as FSTs

Language models are stored as finite-state transducers on disk. They are loaded lazily by default — only the models relevant to the current input text are read into memory. Multiple `LanguageDetector` instances share thread-safe access to the same loaded models, so each model is loaded only once regardless of how many detectors exist.

### Accuracy Modes

- **High accuracy mode** (default): Uses full n-gram models (sizes 1–5). Best for short text and maximum precision.
- **Low accuracy mode**: Loads a smaller subset of models. Detection accuracy for texts under 120 characters drops significantly, but longer text remains mostly unaffected. Useful when resources are constrained or only long documents need classification.

### Thread Safety

The entire library is thread-safe. A single `LanguageDetector` instance can be shared across multiple threads. For batch processing, multi-threaded methods are available that efficiently use all CPU cores.

### Single-Language Mode

When built with exactly one language, the detector operates in single-language mode: it checks whether the input text is written in that language or not, returning the language or `None`. It uses unique and most common n-grams collected beforehand for each supported language.

## Installation / Setup

Lingua-Py 2.2.0 requires Python >= 3.12. It is distributed as a native extension (compiled Rust via PyO3) on PyPI under the package name `lingua-language-detector`.

Install with pip:

```bash
pip install lingua-language-detector
```

Pre-built wheels are available for common platforms. In environments that do not support native Python extensions (e.g., Juno), use the pure Python 1.x branch instead:

```bash
pip install lingua-language-detector==1.4.0
```

## Usage Examples

### Basic Detection

```python
from lingua import Language, LanguageDetectorBuilder

languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

language = detector.detect_language_of("languages are awesome")
print(language)  # Language.ENGLISH
print(language.iso_code_639_1.name)  # 'EN'
print(language.iso_code_639_3.name)  # 'ENG'
```

### Confidence Values

Get probability scores for all candidate languages:

```python
from lingua import Language, LanguageDetectorBuilder

languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

confidence_values = detector.compute_language_confidence_values("languages are awesome")
for confidence in confidence_values:
    print(f"{confidence.language.name}: {confidence.value:.2f}")
# ENGLISH: 0.93
# FRENCH: 0.04
# GERMAN: 0.02
# SPANISH: 0.01
```

Values are probabilities between 0.0 and 1.0 that sum to 1.0. If the rule engine unambiguously identifies a language, it receives 1.0 and all others receive 0.0.

For a single language confidence:

```python
confidence = detector.compute_language_confidence("languages are awesome", Language.FRENCH)
print(f"{confidence:.2f}")  # 0.04
```

Returns 0.0 if the language is not supported by this detector instance.

### Minimum Relative Distance

Set a threshold to reject uncertain detections:

```python
from lingua import Language, LanguageDetectorBuilder

languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH]
detector = LanguageDetectorBuilder.from_languages(*languages)\
    .with_minimum_relative_distance(0.9)\
    .build()

result = detector.detect_language_of("prologue")  # word valid in both English and French
print(result)  # None — distance too small, detection unreliable
```

The relative distance depends on input text length. Longer text produces larger distances between language probabilities. For very short phrases, do not set the threshold too high or `None` will be returned frequently.

### Mixed-Language Detection

Detect multiple languages within a single text:

```python
from lingua import Language, LanguageDetectorBuilder

languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

sentence = ("Parlez-vous français? "
            "Ich spreche Französisch nur ein bisschen. "
            "A little bit is better than nothing.")

for result in detector.detect_multiple_languages_of(sentence):
    print(f"{result.language.name}: '{sentence[result.start_index:result.end_index]}'")
# FRENCH: 'Parlez-vous français? '
# GERMAN: 'Ich spreche Französisch nur ein bisschen. '
# ENGLISH: 'A little bit is better than nothing.'
```

Each `DetectionResult` provides `language`, `start_index`, and `end_index` for the contiguous single-language segment. This feature is experimental — it works best in high-accuracy mode with multiple long words per language. Reducing the candidate language set improves accuracy.

### Parallel (Multi-Threaded) Processing

For batch processing, use multi-threaded equivalents of single-threaded methods:

```python
from lingua import Language, LanguageDetectorBuilder

languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

texts = ["Hello world", "Bonjour le monde", "Hallo Welt"]

# Parallel detection
results = detector.detect_languages_in_parallel_of(texts)

# Parallel confidence values
confidences = detector.compute_language_confidence_values_in_parallel(texts)

# Parallel mixed-language detection
mixed_results = detector.detect_multiple_languages_in_parallel_of(texts)

# Parallel single-language confidence
single_confidences = detector.compute_language_confidence_in_parallel(texts, Language.ENGLISH)
```

Method mapping:

- `detect_language_of` → `detect_languages_in_parallel_of`
- `detect_multiple_languages_of` → `detect_multiple_languages_in_parallel_of`
- `compute_language_confidence_values` → `compute_language_confidence_values_in_parallel`
- `compute_language_confidence` → `compute_language_confidence_in_parallel`

### Builder Methods

Select languages for the detector using various strategies:

```python
from lingua import LanguageDetectorBuilder, Language, IsoCode639_1, IsoCode639_3

# All 75 supported languages
LanguageDetectorBuilder.from_all_languages()

# All spoken languages (excludes Latin)
LanguageDetectorBuilder.from_all_spoken_languages()

# Only Cyrillic-script languages
LanguageDetectorBuilder.from_all_languages_with_cyrillic_script()

# Exclude specific languages
LanguageDetectorBuilder.from_all_languages_without(Language.SPANISH)

# Explicit language list
LanguageDetectorBuilder.from_languages(Language.ENGLISH, Language.GERMAN)

# By ISO 639-1 codes
LanguageDetectorBuilder.from_iso_codes_639_1(IsoCode639_1.EN, IsoCode639_1.DE)

# By ISO 639-3 codes
LanguageDetectorBuilder.from_iso_codes_639_3(IsoCode639_3.ENG, IsoCode639_3.DEU)
```

Restricting the candidate language set improves both accuracy and performance. If you know certain languages cannot appear in your input, exclude them explicitly.

### Eager Loading (Preloading Models)

By default, language models are loaded lazily on demand. For web services where predictable latency matters, preload all models at startup:

```python
detector = LanguageDetectorBuilder.from_all_languages()\
    .with_preloaded_language_models()\
    .build()
```

Multiple detector instances share the same preloaded models in memory with thread-safe access.

### Low Accuracy Mode

Trade accuracy for speed and lower memory usage:

```python
detector = LanguageDetectorBuilder.from_all_languages()\
    .with_low_accuracy_mode()\
    .build()
```

Accuracy for texts under 120 characters drops significantly. Texts longer than 120 characters remain mostly unaffected. This mode loads only a small subset of the full n-gram models.

## Supported Languages

Lingua supports 75 languages:

- Afrikaans, Albanian, Arabic, Armenian, Azerbaijani
- Basque, Belarusian, Bengali, Norwegian Bokmal, Bosnian, Bulgarian
- Catalan, Chinese, Croatian, Czech
- Danish, Dutch
- English, Esperanto, Estonian
- Finnish, French
- Ganda, Georgian, German, Greek, Gujarati
- Hebrew, Hindi, Hungarian
- Icelandic, Indonesian, Irish, Italian
- Japanese
- Kazakh, Korean
- Latin, Latvian, Lithuanian
- Macedonian, Malay, Maori, Marathi, Mongolian
- Norwegian Nynorsk
- Persian, Polish, Portuguese, Punjabi
- Romanian, Russian
- Serbian, Shona, Slovak, Slovene, Somali, Sotho, Spanish, Swahili, Swedish
- Tagalog, Tamil, Telugu, Thai, Tsonga, Tswana, Turkish
- Ukrainian, Urdu
- Vietnamese
- Welsh
- Xhosa, Yoruba
- Zulu

## PyO3 Enum Limitations

Because version 2.x uses Rust bindings via PyO3, the `Language` enum does not behave exactly like a native Python enum:

```python
# Iteration — use .all() instead of direct iteration
for language in sorted(Language.all()):
    print(language)

# Dynamic lookup — use .from_str() instead of subscripting
assert Language.from_str("GERMAN") == Language.GERMAN
assert Language.from_str("german") == Language.GERMAN  # case-insensitive
```

PyO3 does not yet support metaclasses, so `for lang in Language:` and `Language["GERMAN"]` will not work.

## Performance Characteristics

Lingua is among the fastest language detectors in multi-threaded mode. Benchmarks on an iMac 3.6 GHz 8-Core Intel Core i9 with 40 GB RAM (classifying 3000 texts across all 75 languages):

- CLD 2: 8.65 sec
- CLD 3: 16.77 sec
- Lingua (low accuracy, multi-threaded): 11.81 sec
- Lingua (high accuracy, multi-threaded): 21.13 sec
- Simplemma: 2 min 36 sec
- Langid: 3 min 50 sec
- Langdetect: 10 min 44 sec

Memory usage is only a few dozen megabytes even with all 75 language models loaded, thanks to FST-based storage.

## Accuracy

Tested on the Wortschatz corpora from Leipzig University (1 million sentences per language for training, 10 thousand for testing). Sample German results:

- Single words (avg 9 chars): ~74% accuracy
- Word pairs (avg 18 chars): ~94% accuracy
- Sentences (avg 111 chars): ~99.7% accuracy
- Average across all three: ~89% accuracy

Lingua outperforms CLD2, CLD3, Langid, Simplemma, and Langdetect on short text detection while remaining competitive on longer text.

## Key Differences from Other Detectors

1. **n-gram range**: Uses n-grams of sizes 1–5 instead of only trigrams (n=3), producing reliable probabilities even for single words.
2. **Two-stage pipeline**: Rule-based alphabet filtering reduces the candidate set before statistical classification, saving memory and CPU.
3. **Mixed-language detection**: Can identify multiple language segments within a single text — rare among lightweight detectors.
4. **Offline operation**: No API calls or external services required after installation.
5. **FST storage**: Language models stored as finite-state transducers on disk, enabling low memory usage even with all 75 languages.
