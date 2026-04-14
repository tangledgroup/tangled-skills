# NLTK POS Tagging and Chunking - Complete Guide

## Overview

Part-of-speech (POS) tagging assigns grammatical categories to words, while chunking groups words into phrases. Both are essential for syntactic analysis.

## POS Tagging Basics

### Default POS Tagger

NLTK's default tagger uses an averaged perceptron model:

```python
from nltk import pos_tag, word_tokenize

text = "The quick brown fox jumps over the lazy dog"
tokens = word_tokenize(text)
tags = pos_tag(tokens)

print(tags)
# [('The', 'DT'), ('quick', 'JJ'), ('brown', 'JJ'), ('fox', 'NN'), 
#  ('jumps', 'VBZ'), ('over', 'IN'), ('the', 'DT'), ('lazy', 'JJ'), 
#  ('dog', 'NN')]

# Display with formatting
for word, tag in tags:
    print(f"{word:10} → {tag}")
```

### Penn Treebank Tag Set

| Tag | Description | Example |
|-----|-------------|---------|
| NN | Noun, singular | dog, cat |
| NNS | Noun, plural | dogs, cats |
| NNP | Proper noun, singular | John, London |
| NNPS | Proper noun, plural | Americans, Johns |
| VB | Verb, base form | run, eat |
| VBD | Verb, past tense | ran, ate |
| VBG | Verb, gerund/present participle | running, eating |
| VBN | Verb, past participle | run, eaten |
| VBP | Verb, non-3rd singular present | run (I run) |
| VBZ | Verb, 3rd singular present | runs, eats |
| JJ | Adjective | quick, lazy |
| JJR | Adjective, comparative | quicker, lazier |
| JJS | Adjective, superlative | quickest, laziest |
| RB | Adverb | quickly, very |
| RBR | Adverb, comparative | more quickly |
| RBS | Adverb, superlative | most quickly |
| DT | Determiner | the, a, this |
| IN | Preposition | in, over, under |
| TO | "to" (infinitive marker) | to run |

### Custom POS Tagger Training

Train a tagger on domain-specific text:

```python
from nltk.tag import UnigramTagger, BigramTagger, DefaultTagger, BackoffTagger
from nltk.corpus import treebank
from nltk import word_tokenize, pos_tag

# Get training data
train_sents = treebank.sents()[:5000]  # Words only
train_tags = treebank.tagged_sents()[:5000]  # (word, tag) pairs

# Train unigram tagger
unigram_tagger = UnigramTagger(train_tags)
print(f"Unigram accuracy: {unigram_tagger.accuracy(treebank.tagged_sents()[5000:6000]):.2%}")

# Train bigram tagger (needs fallback)
bigram_tagger = BigramTagger(train_tags, backoff=unigram_tagger)
print(f"Bigram accuracy: {bigram_tagger.accuracy(treebank.tagged_sents()[5000:6000]):.2%}")

# Create cascade of taggers
default_tagger = DefaultTagger('NN')  # Default to noun
unigram_tagger = UnigramTagger(train_tags, backoff=default_tagger)
bigram_tagger = BigramTagger(train_tags, backoff=unigram_tagger)

# Test on new text
test_text = "The quick brown fox jumps"
tokens = word_tokenize(test_text)
tags = bigram_tagger.tag(tokens)
print(list(zip(tokens, tags)))
```

### Regex Tagger

Pattern-based tagging for known words:

```python
from nltk.tag import RegexTagger
import re

# Define patterns
patterns = [
    (r'^-?[0-9]+(.[0-9]+)?$', 'CD'),  # cardinal numbers
    (r'^(The|A|An)$', 'DT'),          # determiners
    (r'^(is|are|was|were)$', 'VBZ'),  # verbs
    (r'^(quick|slow|fast)$', 'JJ'),   # adjectives
    (r'.*ing$', 'VBG'),               # gerunds
    (r'.*ed$', 'VBD'),                # past tense
    (r'.*ly$', 'RB'),                 # adverbs
    (r'.*', 'NN'),                    # default to noun
]

tagger = RegexTagger(patterns)
text = "The quick brown fox is running fast"
tokens = word_tokenize(text)
tags = tagger.tag(tokens)

print(list(zip(tokens, tags)))
# [('The', 'DT'), ('quick', 'JJ'), ('brown', 'NN'), ('fox', 'NN'), 
#  ('is', 'VBZ'), ('running', 'VBG'), ('fast', 'RB')]
```

### N-gram Tagger with Backoff

Combine multiple taggers for better accuracy:

```python
from nltk.tag import UnigramTagger, BigramTagger, TrigramTagger, DefaultTagger
from nltk.corpus import treebank

train_data = treebank.tagged_sents()[:10000]
test_data = treebank.tagged_sents()[10000:11000]

# Create backoff chain
default_tagger = DefaultTagger('NN')
unigram_tagger = UnigramTagger(train_data, backoff=default_tagger)
bigram_tagger = BigramTagger(train_data, backoff=unigram_tagger)
trigram_tagger = TrigramTagger(train_data, backoff=bigram_tagger)

# Evaluate
accuracy = trigram_tagger.accuracy(test_data)
print(f"Trigram tagger accuracy: {accuracy:.2%}")

# Apply to new text
from nltk import word_tokenize
text = "Natural language processing is fascinating"
tokens = word_tokenize(text)
tags = trigram_tagger.tag(tokens)
print(list(zip(tokens, tags)))
```

## Named Entity Recognition (Chunking)

### Pre-trained NE Chunker

Use NLTK's pre-trained named entity chunker:

```python
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import convert_tree_to_parse

text = "Barack Obama was born in Hawaii and worked in Chicago."
tokens = word_tokenize(text)
tags = pos_tag(tokens)

# Chunk named entities
chunked = ne_chunk(tags)
print(chunked)
# (SBAR
#   (NP (PERSON Barack/NNP Obama/NNP))
#   was/VBD born/VBN in/IN 
#   (NP (GPE Hawaii/NNP)) and/CC worked/VBD in/IN 
#   (NP (GPE Chicago/NNP)) ./.)

# Pretty print
print(chunked.prettify())
```

### NE Types

| Type | Description | Examples |
|------|-------------|----------|
| PERSON | Names of people | John Smith, Barack Obama |
| ORGANIZATION | Companies, agencies | Google, NASA |
| GPE | Geopolitical entities | France, New York City |
| LOCATION | Physical locations | Mount Everest, Pacific Ocean |
| FACILITY | Buildings, infrastructure | Eiffel Tower, Hoover Dam |
| DATE | Dates and times | January 1, 2024, yesterday |
| TIME | Times | 3:30 PM, noon |
| MONEY | Monetary values | $100, £50 |
| PERCENT | Percentages | 50%, twenty percent |
| ORDINAL | Ordinal numbers | first, second, 1st |
| CARDINAL | Cardinal numbers | one, two, 100 |

### Extracting Named Entities

```python
from nltk import ne_chunk, pos_tag, word_tokenize

def extract_entities(text):
    """Extract named entities from text."""
    tokens = word_tokenize(text)
    tags = pos_tag(tokens)
    chunked = ne_chunk(tags)
    
    entities = []
    
    for subtree in chunked:
        if hasattr(subtree, 'label'):  # Is a named entity
            entity_type = subtree.label()
            entity_text = ' '.join(token for token, tag in subtree.leaves())
            entities.append((entity_type, entity_text))
    
    return entities

text = "Elon Musk founded Tesla and SpaceX. He lives in Texas."
entities = extract_entities(text)

for entity_type, entity_text in entities:
    print(f"{entity_type:15} → {entity_text}")
# ORGANIZATION    → Elon Musk (incorrect, should be PERSON)
# ORGANIZATION    → Tesla
# ORGANIZATION    → SpaceX
# PERSON          → He
# GPE             → Texas
```

**Note**: Pre-trained chunker may have errors. Consider using spaCy or Stanford NER for production use.

### Custom Chunking with Regular Expressions

Define custom chunk patterns:

```python
from nltk.chunk import RegexpParser
from nltk import pos_tag, word_tokenize

# Define chunk grammar
grammar = """
    NP: {<DT|PDT|CD>?<JJ>*<NN>+}  # Noun phrase
    VP: {<VB><.*>?}               # Verb phrase
    PP: {<IN><NP>}                # Prepositional phrase
"""

parser = RegexpParser(grammar)

text = "The quick brown fox jumps over the lazy dog"
tokens = word_tokenize(text)
tags = pos_tag(tokens)

# Parse into chunks
tree = parser.parse(tags)
print(tree)
# (S (NP The/DT quick/JJ brown/JJ fox/NN) 
#    (VP jumps/VBZ 
#       (PP over/IN (NP the/DT lazy/JJ dog/NN)))
#   )

print(tree.prettify())
```

### IOB Chunking

Inside-Outside-Beginning format for chunking:

```python
from nltk.chunk import transform_iob_tags
from nltk import pos_tag, word_tokenize

# Example with manual IOB tags
tokens = ["John", "Smith", "lives", "in", "New", "York"]
iob_tags = ["B-PERSON", "I-PERSON", "O", "O", "B-GPE", "I-GPE"]

# Convert to NLTK tree format
chunked = transform_iob_tags(iob_tags, tokens)
print(chunked)
```

## Chunking Evaluation

```python
from nltk.chunk import evaluate
from nltk.corpus import conll2000

# Get training and test data
train_sents = conll2000.chunked_sents('train.txt')
test_sents = conll2000.chunked_sents('test.txt')

# Train a simple chunker (using pre-trained POS tagger)
from nltk.chunk import RegexpParser

grammar = """
    NP: {<DT>?<JJ>*<NN>+}
    VP: {<VB><.*>?}
"""

parser = RegexpParser(grammar)

# Evaluate on test set
correct = 0
total = 0

for sent in test_sents:
    tokens = [(word, pos) for word, pos, chunk in sent]
    parsed = parser.parse(tokens)
    
    # Compare chunks
    score = evaluate(sent.chunks(), parsed.chunks())
    correct += score['correct']
    total += score['total']

print(f"Chunking accuracy: {correct/total:.2%}")
```

## Advanced Tagging Techniques

### Context-Sensitive Tagging

Use context to resolve ambiguities:

```python
from nltk.tag import PerceptronTagger

# Load pre-trained perceptron tagger
tagger = PerceptronTagger(load=False)  # Create empty tagger

# Train on custom data
from nltk.corpus import treebank
train_data = treebank.tagged_sents()[:10000]
tagger.train(train_data)

# Use for tagging
text = "The record broke the previous record"
tokens = word_tokenize(text)
tags = tagger.tag(tokens)

print(list(zip(tokens, tags)))
# [('The', 'DT'), ('record', 'NN'), ('broke', 'VBD'), 
#  ('the', 'DT'), ('previous', 'JJ'), ('record', 'NN')]
```

### Saving and Loading Taggers

```python
from nltk.tag import PerceptronTagger
from nltk.corpus import treebank

# Train tagger
tagger = PerceptronTagger(load=False)
train_data = treebank.tagged_sents()[:10000]
tagger.train(train_data)

# Save to disk
tagger.save('custom_tagger.pkl')

# Load later
loaded_tagger = PerceptronTagger(load='custom_tagger.pkl')
text = "The cat sat on the mat"
tokens = word_tokenize(text)
tags = loaded_tagger.tag(tokens)
print(list(zip(tokens, tags)))
```

## Common Patterns

### Complete NLP Pipeline

```python
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.stem import WordNetLemmatizer
import nltk.corpus.wordnet as wn

def full_nlp_pipeline(text):
    """Complete NLP pipeline: tokenize, tag, chunk, lemmatize."""
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # POS tag
    pos_tags = pos_tag(tokens)
    
    # Named entity recognition
    entities = ne_chunk(pos_tags)
    
    # Lemmatize with POS information
    lemmatizer = WordNetLemmatizer()
    
    def pos_to_wordnet(pos):
        if pos.startswith('NN'):
            return wn.NOUN
        elif pos.startswith('VB'):
            return wn.VERB
        elif pos.startswith('JJ'):
            return wn.ADJ
        elif pos.startswith('RB'):
            return wn.ADV
        return wn.NOUN
    
    lemmas = [(word, pos, lemmatizer.lemmatize(word, pos=pos_to_wordnet(pos))) 
              for word, pos in pos_tags]
    
    return {
        'tokens': tokens,
        'pos_tags': pos_tags,
        'entities': entities,
        'lemmas': lemmas
    }

text = "Barack Obama was the 44th president of the United States."
result = full_nlp_pipeline(text)

print("Tokens:", result['tokens'])
print("\nPOS Tags:", result['pos_tags'])
print("\nEntities:")
print(result['entities'].prettify())
print("\nLemmas:", result['lemmas'])
```

### Extracting Noun Phrases

```python
from nltk import pos_tag, word_tokenize
from nltk.chunk import RegexpParser

def extract_noun_phrases(text):
    """Extract noun phrases from text."""
    tokens = word_tokenize(text)
    tags = pos_tag(tokens)
    
    # NP grammar
    grammar = "NP: {<DT|PDT|CD>?<JJ>*<NN+>}"
    parser = RegexpParser(grammar)
    
    tree = parser.parse(tags)
    
    # Extract NPs
    nps = []
    for subtree in tree:
        if hasattr(subtree, 'label') and subtree.label() == 'NP':
            np_text = ' '.join(token for token, tag in subtree.leaves())
            nps.append(np_text)
    
    return nps

text = "The quick brown fox jumps over the lazy dog"
nps = extract_noun_phrases(text)
print(nps)  # ['The quick brown fox', 'the lazy dog']
```

## Troubleshooting

### Unknown Words Not Tagged Correctly

**Problem**: Domain-specific words tagged as nouns (default)

**Solution**: Train custom tagger or add regex patterns:

```python
from nltk.tag import RegexTagger, UnigramTagger, BackoffTagger

# Add domain-specific patterns
patterns = [
    (r'^API$', 'NN'),
    (r'^JSON$', 'NN'),
    (r'^HTTP$', 'NN'),
    (r'.*ing$', 'VBG'),
]

regex_tagger = RegexTagger(patterns)

# Train on domain corpus
from nltk.corpus import treebank
train_data = treebank.tagged_sents()[:10000]
unigram_tagger = UnigramTagger(train_data, backoff=regex_tagger)

text = "The API returns JSON data"
tokens = word_tokenize(text)
tags = unigram_tagger.tag(tokens)
print(list(zip(tokens, tags)))
```

### NE Chunker Accuracy Issues

**Problem**: Pre-trained chunker makes errors on specific domains

**Solution**: Use domain-specific NER or switch to spaCy:

```python
# For production use, consider spaCy which has better NER
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("Barack Obama was born in Hawaii.")

for ent in doc.ents:
    print(f"{ent.text:20} → {ent.label_}")
# Barack Obama        → PERSON
# Hawaii              → GPE
```

## Performance Tips

1. **Cache taggers**: Load pre-trained taggers once and reuse
2. **Batch processing**: Process multiple texts together
3. **Use appropriate tagger**: Pre-trained for general text, custom for domains
4. **Parallel processing**: Use multiprocessing for large datasets

```python
# Good: Reuse tagger
from nltk import pos_tag

text1 = "First sentence."
text2 = "Second sentence."

# Bad: Create new tagger each time (slow)
# tags1 = pos_tag(word_tokenize(text1))  # Loads model
# tags2 = pos_tag(word_tokenize(text2))  # Loads model again

# Good: Model is cached internally by NLTK
tags1 = pos_tag(word_tokenize(text1))
tags2 = pos_tag(word_tokenize(text2))  # Uses cached model
```

## References

- **POS Tagging Documentation**: https://www.nltk.org/howto/tag.html
- **Chunking Documentation**: https://www.nltk.org/howto/chunk.html
- **Penn Treebank Tags**: https://www.ling.upenn.edu/courses/Ling2400/treebank/
- **CoNLL 2000 Dataset**: https://www.clips.uantwerpen.be/conll2000/chunking/
