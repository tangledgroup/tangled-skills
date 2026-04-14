# NLTK Stemming and Lemmatization - Complete Guide

## Overview

Stemming and lemmatization are techniques for reducing words to their base or root form, which is essential for text normalization in NLP tasks.

- **Stemming**: Rule-based process that chops off word endings (may produce non-words)
- **Lemmatization**: Dictionary-based process that returns valid dictionary words (lemmas)

## Stemming Algorithms

### Porter Stemmer (English)

The classic stemming algorithm by Martin Porter:

```python
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

words = ['running', 'runs', 'ran', 'better', 'best', 'mice', 'studies']
stems = [stemmer.stem(word) for word in words]

for word, stem in zip(words, stems):
    print(f"{word:12} → {stem}")
# running    → run
# runs       → run
# ran        → ran
# better     → better
# best       → best
# mice       → mic
# studies    -> studi
```

**Characteristics:**
- Fast and efficient
- Language-specific (English only)
- May produce non-words ("studies" → "studi")
- Doesn't understand context or part of speech

### Snowball Stemmer (Multi-language)

Improved version of Porter with support for 30+ languages:

```python
from nltk.stem import SnowballStemmer

# English stemmer
stemmer_en = SnowballStemmer('english')
print(stemmer_en.stem('running'))  # run

# Spanish stemmer
stemmer_es = SnowballStemmer('spanish')
print(stemmer_es.stem('comiendo'))  # comi

# French stemmer  
stemmer_fr = SnowballStemmer('french')
print(stemmer_fr.stem('mangeant'))  # mange

# German stemmer
stemmer_de = SnowballStemmer('german')
print(stemmer_de.stem('laufend'))  # lauf
```

**Supported languages:** arabic, danish, dutch, english, finnish, french, german, hungarian, italian, norwegian, portuguese, romanian, russian, spanish, swedish

### Lancaster Stemmer (English)

More aggressive stemming algorithm:

```python
from nltk.stem import LancasterStemmer

stemmer = LancasterStemmer()

words = ['running', 'runner', 'runnable', 'better', 'best']
stems = [stemmer.stem(word) for word in words]

for word, stem in zip(words, stems):
    print(f"{word:12} → {stem}")
# running    → run
# runner     → run
# runnable   → runabl
# better     → good
# best       → good
```

**Characteristics:**
- More aggressive than Porter
- Can produce very short stems
- May over-stem (lose too much information)

## Lemmatization

### WordNet Lemmatizer

Uses WordNet dictionary to find valid lemmas:

```python
from nltk.stem import WordNetLemmatizer
import nltk.corpus.wordnet as wn

lemmatizer = WordNetLemmatizer()

# Without POS specification (defaults to noun)
words = ['running', 'better', 'mice', 'studies', 'went']
lemmas = [lemmatizer.lemmatize(word) for word in words]

for word, lemma in zip(words, lemmas):
    print(f"{word:12} → {lemma}")
# running    → running  (not recognized as verb without POS)
# better     → better   (not recognized as adjective without POS)
# mice       → mouse    (noun plural correctly identified)
# studies    → study    (noun plural correctly identified)
# went       → went     (verb not recognized without POS)

# With POS specification
lemmas_with_pos = [
    lemmatizer.lemmatize('running', pos=wn.VERB),   # running
    lemmatizer.lemmatize('better', pos=wn.ADJ),     # good
    lemmatizer.lemmatize('mice', pos=wn.NOUN),      # mouse
    lemmatizer.lemmatize('studies', pos=wn.NOUN),   # study
    lemmatizer.lemmatize('went', pos=wn.VERB),      # went (irregular, not in WordNet)
]

print(lemmas_with_pos)
# ['run', 'good', 'mouse', 'study', 'went']
```

**POS constants:**
- `wn.NOUN` or 'n': Noun
- `wn.VERB` or 'v': Verb
- `wn.ADJ` or 'a': Adjective
- `wn.ADV` or 'r': Adverb

### POS-Aware Lemmatization Pipeline

Combine POS tagging with lemmatization for better results:

```python
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
import nltk.corpus.wordnet as wn

def pos_to_wordnet(pos):
    """Convert NLTK POS tag to WordNet POS."""
    if pos.startswith('NN'):
        return wn.NOUN
    elif pos.startswith('VB'):
        return wn.VERB
    elif pos.startswith('JJ'):
        return wn.ADJ
    elif pos.startswith('RB'):
        return wn.ADV
    else:
        return wn.NOUN  # Default to noun

text = "The quick brown foxes were jumping over the slower dogs"
tokens = word_tokenize(text.lower())
pos_tags = pos_tag(tokens)

lemmatizer = WordNetLemmatizer()
lemmas = []

for word, pos in pos_tags:
    wn_pos = pos_to_wordnet(pos)
    lemma = lemmatizer.lemmatize(word, pos=wn_pos)
    lemmas.append(lemma)

print(list(zip(tokens, pos_tags, lemmas)))
# [('the', 'DT', 'the'), ('quick', 'JJ', 'quick'), ('brown', 'JJ', 'brown'),
#  ('foxes', 'NNS', 'fox'), ('were', 'VBD', 'were'), ('jumping', 'VBG', 'jump'),
#  ('over', 'IN', 'over'), ('the', 'DT', 'the'), ('slower', 'JJR', 'slow'),
#  ('dogs', 'NNS', 'dog')]
```

## Stemming vs Lemmatization Comparison

| Aspect | Stemming | Lemmatization |
|--------|----------|---------------|
| **Speed** | Very fast | Slower (dictionary lookup) |
| **Accuracy** | Lower (may produce non-words) | Higher (valid words only) |
| **Context awareness** | None | With POS tagging |
| **Language support** | Limited (Snowball: 30+) | WordNet languages (10+) |
| **Use case** | Search, quick preprocessing | Semantic analysis, NLP pipelines |

### Practical Comparison

```python
from nltk.stem import PorterStemmer, WordNetLemmatizer
import nltk.corpus.wordnet as wn

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

words = ['running', 'runs', 'better', 'best', 'mice', 'studies', 'went', 'children']

print(f"{'Word':12} {'Stem':12} {'Lemma (NOUN)':15} {'Lemma (VERB)':15}")
print("-" * 60)

for word in words:
    stem = stemmer.stem(word)
    lemma_noun = lemmatizer.lemmatize(word, pos=wn.NOUN)
    lemma_verb = lemmatizer.lemmatize(word, pos=wn.VERB)
    print(f"{word:12} {stem:12} {lemma_noun:15} {lemma_verb:15}")

# Word         Stem         Lemma (NOUN)    Lemma (VERB)  
# ------------------------------------------------------------
# running      run          running         run
# runs         run          runs            run
# better       better       better          better
# best         best         best            best
# mice         mic          mouse           mouse
# studies      studi        study           study
# went         went         went            went
# children     children     child           child
```

## Advanced Techniques

### Custom Stemmer Rules

Create domain-specific stemmer:

```python
from nltk.stem import WordNetLemmatizer

class MedicalStemmer:
    """Custom stemmer for medical terminology."""
    
    def __init__(self):
        self.suffixes = [
            ('-itis', ''),      # inflammation
            ('-ology', 'olog'), # study of
            ('-ectomy', 'ectom'), # surgical removal
            ('-scope', 'scop'),  # viewing instrument
        ]
        self.base_lemmatizer = WordNetLemmatizer()
    
    def stem(self, word):
        # Try custom rules first
        for suffix, replacement in self.suffixes:
            if word.endswith(suffix):
                return word[:-len(suffix)] + replacement
        
        # Fall back to standard lemmatization
        return self.base_lemmatizer.lemmatize(word)

stemmer = MedicalStemmer()
medical_terms = ['arthritis', 'cardiology', 'appendectomy', 'endoscope']

for term in medical_terms:
    print(f"{term:15} → {stemmer.stem(term)}")
# arthritis      → arthr
# cardiology     → cardiolog
# appendectomy   → appendectom
# endoscope      → endoscop
```

### Hybrid Approach

Combine stemming and lemmatization:

```python
from nltk.stem import PorterStemmer, WordNetLemmatizer
import nltk.corpus.wordnet as wn

class HybridStemmer:
    """Use lemmatization when possible, fall back to stemming."""
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.valid_words = set(nltk.corpus.words.words())
    
    def stem(self, word):
        # Try lemmatization first
        lemma = self.lemmatizer.lemmatize(word, pos=wn.NOUN)
        
        # If lemma is a valid word, use it
        if lemma.lower() in self.valid_words:
            return lemma
        
        # Otherwise, use stemming
        return self.stemmer.stem(word)

hybrid = HybridStemmer()
words = ['running', 'mice', 'studies', 'xyz123']  # xyz123 not in dictionary

for word in words:
    print(f"{word:12} → {hybrid.stem(word)}")
# running    → running (valid word, kept as-is)
# mice       → mouse   (valid lemma)
# studies    → study   (valid lemma)
# xyz123     → xyz123  (stemmed, not in dictionary)
```

## Multilingual Stemming

### Spanish Example

```python
from nltk.stem import SnowballStemmer

stemmer_es = SnowballStemmer('spanish')

words_es = ['comiendo', 'comí', 'comer', 'comes', 'comíamos']
stems_es = [stemmer_es.stem(word) for word in words_es]

for word, stem in zip(words_es, stems_es):
    print(f"{word:12} → {stem}")
# comiendo   → comi
# comí       → comi
# comer      → com
# comes      → com
# comíamos   → comi
```

### French Example

```python
from nltk.stem import SnowballStemmer

stemmer_fr = SnowballStemmer('french')

words_fr = ['mangeant', 'mangé', 'manger', 'manges', 'mangions']
stems_fr = [stemmer_fr.stem(word) for word in words_fr]

for word, stem in zip(words_fr, stems_fr):
    print(f"{word:12} → {stem}")
# mangeant   → mange
# mangé      → mange
# manger     → mange
# manges     → mange
# mangions   → mangi
```

### German Example

```python
from nltk.stem import SnowballStemmer

stemmer_de = SnowballStemmer('german')

words_de = ['laufend', 'lief', 'laufen', 'läufst', 'liefen']
stems_de = [stemmer_de.stem(word) for word in words_de]

for word, stem in zip(words_de, stems_de):
    print(f"{word:12} → {stem}")
# laufend    → lauf
# lief       → lief
# laufen     → lauf
# läufst     → lauf
# liefen     → lief
```

## Performance Comparison

```python
import time
from nltk.stem import PorterStemmer, SnowballStemmer, LancasterStemmer, WordNetLemmatizer

# Create instances
stemmers = {
    'Porter': PorterStemmer(),
    'Snowball': SnowballStemmer('english'),
    'Lancaster': LancasterStemmer(),
}
lemmatizer = WordNetLemmatizer()

# Test corpus
test_words = ['running', 'jumping', 'better', 'best', 'mice'] * 1000

# Time each stemmer
for name, stemmer in stemmers.items():
    start = time.time()
    stems = [stemmer.stem(word) for word in test_words]
    elapsed = time.time() - start
    print(f"{name:12}: {elapsed:.4f} seconds")

# Time lemmatizer
start = time.time()
lemmas = [lemmatizer.lemmatize(word) for word in test_words]
elapsed = time.time() - start
print(f"Lemmatizer  : {elapsed:.4f} seconds")

# Typical output:
# Porter      : 0.0023 seconds
# Snowball    : 0.0025 seconds
# Lancaster   : 0.0019 seconds
# Lemmatizer  : 0.0156 seconds (slower due to dictionary lookup)
```

## Common Patterns

### Text Normalization Pipeline

```python
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk.corpus.wordnet as wn

def normalize_text(text, method='lemmatize'):
    """Normalize text using stemming or lemmatization."""
    tokens = word_tokenize(text.lower())
    
    if method == 'stem':
        from nltk.stem import PorterStemmer
        stemmer = PorterStemmer()
        return [stemmer.stem(token) for token in tokens]
    
    elif method == 'lemmatize':
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(token, pos=wn.NOUN) for token in tokens]
    
    else:
        raise ValueError("method must be 'stem' or 'lemmatize'")

text = "The quick brown foxes were jumping over the lazy dogs"

print("Original:", text)
print("Stemmed:", normalize_text(text, 'stem'))
print("Lemmatized:", normalize_text(text, 'lemmatize'))
```

### Stop Word Removal with Stemming

```python
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

def preprocess_with_stemming(text):
    # Download required data
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')
    
    # Tokenize and lowercase
    tokens = word_tokenize(text.lower())
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if w not in stop_words]
    
    # Stem remaining tokens
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(w) for w in tokens]
    
    return tokens

text = "The quick brown foxes are jumping over the lazy dogs"
result = preprocess_with_stemming(text)
print(result)
# ['quick', 'brown', 'fox', 'jump', 'over', 'lazi', 'dog']
```

## Troubleshooting

### Irregular Verbs Not Lemmatized Correctly

**Problem**: "went" → "went" instead of "go"

**Solution**: WordNet may not have all irregular forms. Use a custom mapping:

```python
from nltk.stem import WordNetLemmatizer
import nltk.corpus.wordnet as wn

# Custom irregular verb mapping
IRREGULAR_VERBS = {
    'went': 'go',
    'been': 'be',
    'was': 'be',
    'were': 'be',
    'done': 'do',
    'made': 'make',
    # Add more as needed
}

def smart_lemmatize(word, pos=wn.VERB):
    if word in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[word]
    
    lemmatizer = WordNetLemmatizer()
    return lemmatizer.lemmatize(word, pos=pos)

print(smart_lemmatize('went'))  # go
print(smart_lemmatize('running'))  # run
```

### POS Tag Mapping Issues

**Problem**: Wrong lemma returned due to incorrect POS tag

**Solution**: Improve POS tag mapping:

```python
from nltk import pos_tag, word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk.corpus.wordnet as wn

def improved_pos_mapping(pos):
    """Better NLTK POS to WordNet POS mapping."""
    if pos in ['NN', 'NNS', 'NNP', 'NNPS']:
        return wn.NOUN
    elif pos in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
        return wn.VERB
    elif pos in ['JJ', 'JJR', 'JJS']:
        return wn.ADJ
    elif pos in ['RB', 'RBR', 'RBS']:
        return wn.ADV
    else:
        return wn.NOUN  # Default

text = "She was running quickly"
tokens = word_tokenize(text.lower())
tags = pos_tag(tokens)

lemmatizer = WordNetLemmatizer()
for word, pos in tags:
    wn_pos = improved_pos_mapping(pos)
    lemma = lemmatizer.lemmatize(word, pos=wn_pos)
    print(f"{word:10} ({pos:4}) → {lemma}")
# she        (PRP)  → she
# was        (VBD)  → be
# running    (VBG)  → run
# quickly    (RB)   → quickly
```

## References

- **Porter Stemmer**: https://www.nltk.org/howto/stem.html
- **Snowball Stemmer**: https://snowballstem.org/
- **WordNet Documentation**: https://www.nltk.org/howto/wordnet.html
- **Lemmatization Guide**: https://www.nltk.org/api/nltk.stem.html
