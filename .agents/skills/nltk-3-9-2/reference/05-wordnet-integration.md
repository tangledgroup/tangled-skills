# NLTK WordNet Integration - Complete Guide

## Overview

WordNet is a large lexical database of English with synsets (groups of synonyms), semantic relationships, and definitions. NLTK provides comprehensive WordNet integration including multilingual support via OMW (Open Multilingual WordNet).

## Basic WordNet Usage

### Loading WordNet

```python
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')  # For multilingual support

import nltk.corpus.wordnet as wn
```

### Finding Synsets

Get all synsets (meanings) for a word:

```python
import nltk.corpus.wordnet as wn

# Get all synsets for "bank"
synsets = wn.synsets('bank')
print(f"Number of senses: {len(synsets)}")  # 6

for i, synset in enumerate(synsets, 1):
    print(f"\n{i}. {synset.name()}")
    print(f"   Definition: {synset.definition()}")
    print(f"   Examples: {synset.examples}")
    print(f"   POS: {synset.pos()}")

# Output:
# 1. bank.n.01 (financial institution)
#    Definition: a financial institution that accepts deposits and channels the money into lending activities
#    Examples: ['they took out a mortgage']
#    POS: n

# 2. bank.n.02 (deposit bank)
#    Definition: an inferior deposit of something
#    ...
```

### Filtering by Part of Speech

```python
import nltk.corpus.wordnet as wn

# Get only noun synsets
noun_synsets = wn.synsets('bank', pos=wn.NOUN)
print(f"Noun senses: {len(noun_synsets)}")  # 4

# Get only verb synsets
verb_synsets = wn.synsets('bank', pos=wn.VERB)
print(f"Verb senses: {len(verb_synsets)}")  # 2

# POS constants
# wn.NOUN or 'n' - noun
# wn.VERB or 'v' - verb
# wn.ADJ or 'a' - adjective
# wn.ADV or 'r' - adverb
```

### Getting Specific Synset

```python
import nltk.corpus.wordnet as wn

# Get specific synset by offset
synset = wn.synset('bank.n.01')  # First noun sense
print(synset.name())      # bank.n.01
print(synset.definition())  # a financial institution...
print(synset.examples)     # ['they took out a mortgage']

# Get by lemma name
synset = wn.synset('financial_institution.n.01')  # Same synset, different name
print(synset.name())  # financial_institution.n.01
```

## Synset Navigation

### Lemmas (Words in Synset)

```python
import nltk.corpus.wordnet as wn

synset = wn.synset('dog.n.01')

# Get all lemmas (words) in this synset
lemmas = synset.lemmas()
print(f"Words: {[lemma.name() for lemma in lemmas]}")  # ['dog', 'domestic_dog']

# Lemma details
for lemma in lemas:
    print(f"{lemma.name():20} → count: {lemma.count()}")
```

### Semantic Relations

#### Hypernyms (Parent Concepts)

```python
import nltk.corpus.wordnet as wn

dog = wn.synset('dog.n.01')

# Direct hypernyms (immediate parents)
hypernyms = dog.hypernyms()
print("Direct hypernyms:")
for h in hypernyms:
    print(f"  {h.name()}: {h.definition()}")

# All hypernyms (up to root)
all_hypernyms = dog.hypernym_closure()
print(f"\nTotal hypernyms to root: {len(all_hypernyms)}")

# Root hypernyms (top-level concepts)
roots = dog.root_hypernyms()
print(f"\nRoot concepts: {[r.name() for r in roots]}")  # ['entity.n.01']
```

#### Hyponyms (Child Concepts)

```python
import nltk.corpus.wordnet as wn

animal = wn.synset('animal.n.01')

# Direct hyponyms (immediate children)
hyponyms = animal.hyponyms()[:10]  # First 10 only
print("Sample hyponyms:")
for h in hyponyms:
    print(f"  {h.name()}")

# All hyponyms (can be very large!)
all_hyponyms = animal.hyponym_closure()
print(f"\nTotal hyponyms: {len(all_hyponyms)}")  # Thousands!
```

#### Meronyms and Holonyms (Part-Whole Relations)

```python
import nltk.corpus.wordnet as wn

car = wn.synset('car.n.01')

# Meronyms (parts of)
print("Parts of car:")
for m in car.member_meronyms()[:5]:
    print(f"  {m.name()}")

# Holonyms (whole that contains)
print("\nWholes containing car:")
for h in car.part_holonyms():
    print(f"  {h.name()}")
```

#### Antonyms (Opposites)

```python
import nltk.corpus.wordnet as wn

good = wn.synset('good.a.01')

# Get antonyms
antonyms = good.antonyms()
print("Antonyms of 'good':")
for a in antonyms:
    print(f"  {a.name()}: {a.definition()}")
```

### Traversing the Network

```python
import nltk.corpus.wordnet as wn
from pprint import pprint

dog = wn.synset('dog.n.01')

# Navigate up (hypernyms)
def print_hypernym_path(synset, indent=0):
    print("  " * indent + synset.name())
    for hypernym in synset.hypernyms():
        print_hypernym_path(hypernym, indent + 1)

print("Hypernym path from dog:")
print_hypernym_path(dog)

# Navigate down (hyponyms) - limit depth to avoid explosion
def print_hyponym_path(synset, indent=0, max_depth=3):
    if indent >= max_depth:
        return
    print("  " * indent + synset.name() + f" ({len(synset.hyponyms())} children)")
    for hyponym in synset.hyponyms()[:3]:  # Limit to 3 per level
        print_hyponym_path(hyponym, indent + 1, max_depth)

print("\nHyponym tree from animal (depth 3):")
print_hyponym_path(wn.synset('animal.n.01'))
```

## Semantic Similarity

### Path-Based Similarity

```python
import nltk.corpus.wordnet as wn

dog = wn.synset('dog.n.01')
cat = wn.synset('car.n.01')
car = wn.synset('car.n.01')

# Path similarity (based on shortest path)
print(f"Dog-Cat path similarity: {dog.path_similarity(cat):.3f}")  # Higher = more similar
print(f"Dog-Car path similarity: {dog.path_similarity(car):.3f}")  # Lower = less similar
```

### Wordnet Information Content Similarity

Requires information content data:

```python
import nltk.corpus.wordnet as wn
from nltk.corpus import wordnet_ic

# Load information content from Brown Corpus
ic_brown = wordnet_ic.ic('ic-brown.dat')

dog = wn.synset('dog.n.01')
cat = wn.synset('cat.n.01')

# Resnik similarity (based on IC of LCS)
resnik_sim = dog.res_similarity(cat, ic_brown)
print(f"Resnik similarity: {resnik_sim:.3f}")

# Jiang-Conrath similarity
jcn_sim = dog.jcn_similarity(cat, ic_brown)
print(f"JCN similarity: {jcn_sim:.3f}")

# Lin similarity
lin_sim = dog.lin_similarity(cat, ic_brown)
print(f"Lin similarity: {lin_sim:.3f}")

# Wu-Palmer similarity (doesn't require IC)
wup_sim = dog.wup_similarity(cat)
print(f"WUP similarity: {wup_sim:.3f}")
```

### Comparing Similarity Measures

```python
import nltk.corpus.wordnet as wn
from nltk.corpus import wordnet_ic

ic_brown = wordnet_ic.ic('ic-brown.dat')

# Test pairs
pairs = [
    ('dog.n.01', 'cat.n.01'),      # Similar (both pets)
    ('dog.n.01', 'car.n.01'),      # Dissimilar
    ('good.a.01', 'bad.a.01'),     # Antonyms
    ('run.v.01', 'jog.v.01'),      # Similar (both movement)
]

print(f"{'Pair':30} {'Path':6} {'WUP':6} {'Lin':6} {'JCN':6}")
print("-" * 60)

for name1, name2 in pairs:
    s1 = wn.synset(name1)
    s2 = wn.synset(name2)
    
    path_sim = s1.path_similarity(s2) or 0
    wup_sim = s1.wup_similarity(s2) or 0
    lin_sim = s1.lin_similarity(s2, ic_brown) or 0
    jcn_sim = s1.jcn_similarity(s2, ic_brown) or 0
    
    pair_name = f"{name1}-{name2}"
    print(f"{pair_name:30} {path_sim:6.3f} {wup_sim:6.3f} {lin_sim:6.3f} {jcn_sim:6.3f}")
```

## WordNet Lemmatization

### Basic Lemmatization

```python
from nltk.stem import WordNetLemmatizer
import nltk.corpus.wordnet as wn

lemmatizer = WordNetLemmatizer()

words = ['running', 'better', 'mice', 'studies', 'went']

# Without POS (defaults to noun)
print("Without POS:")
for word in words:
    lemma = lemmatizer.lemmatize(word)
    print(f"  {word:12} → {lemma}")

# With correct POS
print("\nWith POS:")
for word in words:
    # Determine POS (simplified - in practice use POS tagger)
    if word in ['running', 'went']:
        pos = wn.VERB
    elif word in ['better']:
        pos = wn.ADJ
    else:
        pos = wn.NOUN
    
    lemma = lemmatizer.lemmatize(word, pos=pos)
    print(f"  {word:12} → {lemma}")
```

### Morphy (Lemmatization Helper)

```python
import nltk.corpus.wordnet as wn

# Morphy finds the base form using WordNet
words = ['churches', 'aardwolves', 'abaci', 'book']

print("Morphy results:")
for word in words:
    lemma = wn.morphy(word)  # Default to any POS
    print(f"  {word:15} → {lemma}")

# With specific POS
print("\nWith POS specification:")
print(f"  book (noun)     → {wn.morphy('book', wn.NOUN)}")
print(f"  book (adjective) → {wn.morphy('book', wn.ADJ)}")  # None - not an adjective
```

## Multilingual WordNet (OMW)

### Adding Multilingual Support

```python
import nltk.corpus.wordnet as wn

# Add Open Multilingual WordNet data
wn.add_omw()

# Get synsets in different languages
english_synset = wn.synset('dog.n.01')

# Get lemmas in different languages
print("English:", [l.name() for l in english_synset.lemmas(lang='eng')])
print("Spanish:", [l.name() for l in english_synset.lemmas(lang='spa')])
print("French: ", [l.name() for l in english_synset.lemmas(lang='fra')])
print("German: ", [l.name() for l in english_synset.lemmas(lang='deu')])

# Find synsets by lemma in other languages
spanish_lemmas = wn.lemmas('perro', lang='spa')
print(f"\nSpanish 'perro' maps to: {[l.synset().name() for l in spanish_lemmas]}")
```

### Language Codes

Supported languages include:
- `eng`: English
- `spa`: Spanish
- `fra`: French
- `deu`: German
- `ita`: Italian
- `por`: Portuguese
- `rus`: Russian
- `jpn`: Japanese
- And 20+ more...

## WordNet Domains

### Topic, Region, and Usage Domains

```python
import nltk.corpus.wordnet as wn

# Topic domains (subject areas)
code = wn.synset('code.n.03')
topic_domains = code.topic_domains()
print("Topic domains for 'code':")
for d in topic_domains:
    print(f"  {d.name()}")

# Region domains (geographic usage)
pukka = wn.synset('pukka.a.01')
region_domains = pukka.region_domains()
print("\nRegion domains for 'pukka':")
for d in region_domains:
    print(f"  {d.name()}")

# Usage domains (register/context)
freaky = wn.synset('freaky.a.01')
usage_domains = freaky.usage_domains()
print("\nUsage domains for 'freaky':")
for d in usage_domains:
    print(f"  {d.name()}")

# Get all terms in a domain
cs_domain = wn.synset('computer_science.n.01')
cs_terms = cs_domain.in_topic_domains()[:10]
print(f"\nSample computer science terms: {[t.name() for t in cs_terms]}")
```

## Advanced Features

### Synset Information Content

```python
from nltk.corpus import wordnet_ic
import nltk.corpus.wordnet as wn

ic_brown = wordnet_ic.ic('ic-brown.dat')

dog = wn.synset('dog.n.01')
animal = wn.synset('animal.n.01')

# Get information content (negative log probability)
from nltk.corpus.reader.wordnet import information_content

ic_dog = information_content(dog, ic_brown)
ic_animal = information_content(animal, ic_brown)

print(f"IC of 'dog': {ic_dog:.3f}")
print(f"IC of 'animal': {ic_animal:.3f}")
# Higher IC = more specific/rare concept
```

### Finding Lowest Common Hypernym

```python
import nltk.corpus.wordnet as wn

chef = wn.synset('chef.n.01')
policeman = wn.synset('policeman.n.01')

lchs = chef.lowest_common_hypernyms(policeman)
print("Lowest common hypernyms:")
for lch in lchs:
    print(f"  {lch.name()}: {lch.definition()}")
# Output: person.n.01 (a human being)
```

### Synset Tree Traversal

```python
import nltk.corpus.wordnet as wn
from pprint import pprint

dog = wn.synset('dog.n.01')

# Get tree of hyponyms (limited depth to avoid explosion)
tree = dog.tree(lambda s: s.hyponyms(), depth=2)
print("Hyponym tree (depth 2):")
pprint(tree[:3])  # Show first 3 branches

# Acyclic tree (handles cycles in also_sees relation)
bound = wn.synset('bound.a.01')
acyclic_tree = bound.acyclic_tree(lambda s: sorted(s.also_sees()))
print("\nAcyclic tree of 'bound':")
pprint(acyclic_tree)
```

## Common Patterns

### Word Sense Disambiguation (Simple)

Basic WSD using context:

```python
import nltk.corpus.wordnet as wn
from nltk import word_tokenize, pos_tag

def simple_wsd(word, context):
    """Simple word sense disambiguation using context overlap."""
    
    # Get all synsets for the word
    candidate_synsets = wn.synsets(word)
    if not candidate_synsets:
        return None
    
    # Tokenize context
    context_words = set(word_tokenize(context.lower()))
    
    # Score each synset by definition/example overlap with context
    best_synset = None
    best_score = 0
    
    for synset in candidate_synsets:
        # Get words from definition and examples
        def_words = set(word_tokenize(synset.definition().lower()))
        example_words = set(word_tokenize(' '.join(synset.examples).lower()))
        
        # Count overlap with context
        score = len(def_words & context_words) + len(example_words & context_words)
        
        if score > best_score:
            best_score = score
            best_synset = synset
    
    return best_synset

# Example
word = "bank"
context1 = "I need to deposit money at the financial institution"
context2 = "We sat on the river bank fishing"

sense1 = simple_wsd(word, context1)
sense2 = simple_wsd(word, context2)

print(f"In context 1: {sense1.name() if sense1 else 'None'}")
print(f"  Definition: {sense1.definition() if sense1 else 'N/A'}")

print(f"\nIn context 2: {sense2.name() if sense2 else 'None'}")
print(f"  Definition: {sense2.definition() if sense2 else 'N/A'}")
```

### Finding Related Words

```python
import nltk.corpus.wordnet as wn

def find_related_words(word, relation_type='hypernym', max_results=5):
    """Find words related by semantic relation."""
    
    synsets = wn.synsets(word)
    if not synsets:
        return []
    
    related = set()
    
    for synset in synsets:
        if relation_type == 'hypernym':
            for hypernym in synset.hypernyms():
                for lemma in hypernym.lemmas():
                    related.add(lemma.name())
        
        elif relation_type == 'hyponym':
            for hyponym in synset.hyponyms()[:10]:  # Limit to avoid explosion
                for lemma in hyponym.lemmas():
                    related.add(lemma.name())
        
        elif relation_type == 'antonym':
            for antonym in synset.antonyms():
                for lemma in antonym.lemmas():
                    related.add(lemma.name())
    
    return list(related)[:max_results]

# Examples
print("Hypernyms of 'dog':", find_related_words('dog', 'hypernym'))
print("Hyponyms of 'animal':", find_related_words('animal', 'hyponym'))
print("Antonyms of 'good':", find_related_words('good', 'antonym'))
```

## Troubleshooting

### WordNet Data Not Found

**Problem**: `LookupError: Resource 'wordnet' not found`

**Solution**: Download required data:

```python
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')  # For multilingual
nltk.download('wordnet_ic')  # For similarity measures
```

### Slow Synset Lookup

**Problem**: Repeated lookups are slow

**Solution**: Cache synsets:

```python
from functools import lru_cache
import nltk.corpus.wordnet as wn

@lru_cache(maxsize=10000)
def get_synset(name):
    """Cached synset lookup."""
    return wn.synset(name)

# Usage
dog = get_synset('dog.n.01')  # Cached for future lookups
```

### None Returned from Similarity

**Problem**: Similarity functions return None

**Solution**: Synsets may not share common hypernym:

```python
import nltk.corpus.wordnet as wn

# Synsets from different POS may not be comparable
noun = wn.synset('fly.n.01')  # Insect
verb = wn.synset('fly.v.01')  # To fly

sim = noun.wup_similarity(verb)
print(sim)  # May be None

# Use simulate_root parameter
sim = noun.wup_similarity(verb, simulate_root=True)
print(sim)  # Will return a value
```

## References

- **WordNet Documentation**: https://www.nltk.org/howto/wordnet.html
- **Princeton WordNet**: http://wordnet.princeton.edu/
- **Open Multilingual WordNet**: http://omw.org/
- **Similarity Measures**: https://www.nltk.org/howto/wordnet_lch.html
