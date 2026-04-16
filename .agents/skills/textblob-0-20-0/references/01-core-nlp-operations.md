# Core NLP Operations

This reference covers the fundamental NLP operations available in TextBlob 0.20.0.

## Creating TextBlobs

### Basic Creation

```python
from textblob import TextBlob

# Create from string
text = TextBlob("Python is a high-level programming language.")

# Create from variable
content = "Natural language processing is fascinating."
blob = TextBlob(content)
```

### String-like Operations

TextBlobs behave like Python strings:

```python
zen = TextBlob("Beautiful is better than ugly. Explicit is better than implicit.")

# Slicing
zen[0:19]  # TextBlob("Beautiful is better")

# String methods
zen.upper()  # TextBlob("BEAUTIFUL IS BETTER THAN UGLY...")
zen.find("Simple")  # Returns index

# Comparisons
TextBlob("apples") < TextBlob("bananas")  # True
TextBlob("apples") == "apples"  # True

# Concatenation
TextBlob("apples") + " and " + TextBlob("bananas")
# TextBlob("apples and bananas")

# Formatting
"{0} and {1}".format(TextBlob("apples"), TextBlob("bananas"))
# 'apples and bananas'
```

## Part-of-Speech Tagging

### Basic POS Tagging

Returns a list of (word, tag) tuples:

```python
from textblob import TextBlob

wiki = TextBlob("Python is a high-level, general-purpose programming language.")
tags = wiki.tags

# Output:
# [('Python', 'NNP'), ('is', 'VBZ'), ('a', 'DT'), 
#  ('high-level', 'JJ'), ('general-purpose', 'JJ'), 
#  ('programming', 'NN'), ('language', 'NN')]
```

### Common POS Tags

| Tag | Description | Example |
|-----|-------------|---------|
| NN | Noun, singular | language |
| NNS | Noun, plural | languages |
| NNP | Proper noun | Python |
| JJ | Adjective | high-level |
| VB | Verb, base form | process |
| VBP | Verb, non-3rd person | process |
| VBZ | Verb, 3rd person singular | processes |
| RB | Adverb | quickly |
| DT | Determiner | the, a |
| IN | Preposition | in, of |

### Accessing POS Tags for Words

```python
blob = TextBlob("The quick brown fox jumps.")
for word, tag in blob.tags:
    print(f"{word}: {tag}")
```

## Noun Phrase Extraction

### Basic Extraction

```python
from textblob import TextBlob

text = TextBlob("Python is a high-level programming language used for web development.")
phrases = text.noun_phrases

# Output: WordList(['python', 'high-level programming language', 'web development'])
```

### Use Cases

- Topic extraction from documents
- Keyword identification
- Content summarization
- Information retrieval

```python
document = TextBlob("""
Machine learning is a subset of artificial intelligence. 
Deep learning uses neural networks for pattern recognition.
""")

topics = document.noun_phrases
# ['machine learning', 'subset', 'artificial intelligence', 
#  'deep learning', 'neural networks', 'pattern recognition']
```

## Sentiment Analysis

### Basic Sentiment

Returns `Sentiment(polarity, subjectivity)` namedtuple:

```python
from textblob import TextBlob

testimonial = TextBlob("TextBlob is amazingly simple to use. What great fun!")
sentiment = testimonial.sentiment

print(sentiment.polarity)    # 0.391666... (positive)
print(sentiment.subjectivity)  # 0.435714... (moderately subjective)
```

### Polarity Scale

- **-1.0**: Very negative
- **0.0**: Neutral
- **+1.0**: Very positive

### Subjectivity Scale

- **0.0**: Very objective (factual)
- **1.0**: Very subjective (opinion-based)

### Sentiment by Sentence

```python
text = TextBlob("""
The beer was good. 
But the hangover was horrible.
Service was excellent though.
""")

for sentence in text.sentences:
    pol = sentence.sentiment.polarity
    print(f"{sentence}: {pol:+.3f}")

# Output:
# The beer was good.: +0.150
# But the hangover was horrible.: -0.600
# Service was excellent though.: +0.625
```

### Document-Level Sentiment

Calculate average sentiment across all sentences:

```python
def document_sentiment(blob):
    if not blob.sentences:
        return 0.0
    return sum(s.sentiment.polarity for s in blob.sentences) / len(blob.sentences)

text = TextBlob("Great product! Terrible service. But overall okay.")
avg = document_sentiment(text)
print(f"Average polarity: {avg:+.3f}")
```

## Tokenization

### Word Tokenization

```python
from textblob import TextBlob

zen = TextBlob("Beautiful is better than ugly. Explicit is better than implicit.")
words = zen.words

# Output: WordList(['Beautiful', 'is', 'better', 'than', 'ugly', 
#                   'Explicit', 'is', 'better', 'than', 'implicit'])

# Access individual words
print(words[0])  # 'Beautiful'
print(len(words))  # 10
```

### Sentence Tokenization

```python
zen = TextBlob("First sentence. Second sentence! Third sentence?")
sentences = zen.sentences

# Output: [Sentence("First sentence."), 
#          Sentence("Second sentence!"), 
#          Sentence("Third sentence?")]

# Iterate over sentences
for i, sentence in enumerate(sentences, 1):
    print(f"{i}: {sentence}")
```

### Sentence Indices

Get start and end positions of sentences:

```python
zen = TextBlob("Short. Longer sentence here. Medium.")

for s in zen.sentences:
    print(f"Text: '{s}'")
    print(f"Start: {s.start}, End: {s.end}")
    print()

# Output:
# Text: 'Short.'
# Start: 0, End: 6
#
# Text: 'Longer sentence here.'
# Start: 7, End: 28
```

## Word Operations

### Working with Word Objects

```python
from textblob import TextBlob, Word

sentence = TextBlob("Use 4 spaces per indentation level.")
words = sentence.words

# Output: WordList(['Use', '4', 'spaces', 'per', 'indentation', 'level'])

# Access individual word as Word object
word = words[2]  # 'spaces'
print(type(word))  # <class 'textblob.blob.Word'>
```

### Pluralization and Singularization

```python
from textblob import Word

# Pluralize
w = Word("space")
print(w.pluralize())  # 'spaces'

w = Word("octopus")
print(w.pluralize())  # 'octopodes'

# Singularize
w = Word("levels")
print(w.singularize())  # 'level'

w = Word("mice")
print(w.singularize())  # 'mouse'
```

### WordList Operations

Apply inflection to all words:

```python
from textblob import TextBlob

animals = TextBlob("cat dog octopus")
word_list = animals.words

# Pluralize all
pluralized = word_list.pluralize()
# WordList(['cats', 'dogs', 'octopodes'])

# Singularize all
singular = TextBlob("cats dogs mice").words.singularize()
# WordList(['cat', 'dog', 'mouse'])
```

### Lemmatization

Reduce words to their base form:

```python
from textblob import Word

# Basic lemmatization (assumes noun)
w = Word("octopi")
print(w.lemmatize())  # 'octopus'

# With part-of-speech specification
from textblob.wordnet import VERB, NOUN, ADJ

w = Word("went")
print(w.lemmatize(pos=VERB))  # 'go'

w = Word("better")
print(w.lemmatize(pos=ADJ))  # 'good'

w = Word("mice")
print(w.lemmatize(pos=NOUN))  # 'mouse'
```

### Stemming

Remove word endings to get stem:

```python
from textblob import Word

words = ["running", "runs", "ran", "runner"]
for w in words:
    word_obj = Word(w)
    print(f"{w} -> {word_obj.stem()}")

# Output:
# running -> run
# runs -> run
# ran -> ran
# runner -> runner
```

## Spelling Correction

### TextBlob Correction

```python
from textblob import TextBlob

text = TextBlob("I havv goood speling!")
corrected = text.correct()

print(corrected)  # "I have good spelling!"
```

### Word-Level Spellcheck

Get confidence scores for suggestions:

```python
from textblob import Word

w = Word("falibility")
suggestions = w.spellcheck()

# Output: [('fallibility', 1.0)]

# Get top suggestion
if suggestions:
    best_match, confidence = suggestions[0]
    print(f"Did you mean '{best_match}'? (confidence: {confidence})")
```

### Custom Spellchecker

```python
from textblob import Word

def check_spelling(text):
    """Check spelling and return corrections."""
    blob = TextBlob(text)
    corrections = []
    
    for word in blob.words:
        suggestions = Word(word).spellcheck()
        if suggestions and suggestions[0][0] != word:
            corrections.append((word, suggestions[0][0]))
    
    return corrections

text = "I havv a quik brown fox."
print(check_spelling(text))
# [('havv', 'have'), ('quik', 'quick')]
```

## Word Frequencies

### Using word_counts Dictionary

Case-insensitive word counting:

```python
from textblob import TextBlob

monty = TextBlob("We are no longer the Knights who say Ni. "
                 "We are now the Knights who say Ekki ekki ekki PTANG.")

# Access word counts
print(monty.word_counts['ekki'])  # 3
print(monty.word_counts['knights'])  # 2 (case-insensitive)
print(monty.word_counts['xyz'])  # 0 (not found)
```

### Using WordList.count() Method

```python
# Case-insensitive (default)
count = monty.words.count('ekki')  # 3

# Case-sensitive
count = monty.words.count('ekki', case_sensitive=True)  # 2
count = monty.words.count('Ekki', case_sensitive=True)  # 1
```

### Noun Phrase Frequencies

```python
wiki = TextBlob("Python is great. Python is popular. Python is versatile.")

# Count noun phrases
print(wiki.noun_phrases.count('python'))  # 3

# Get all unique noun phrases and counts
from collections import Counter
phrase_counts = Counter(wiki.noun_phrases)
print(phrase_counts)  # Counter({'python': 3})
```

## N-grams

Generate sequences of n consecutive words:

```python
from textblob import TextBlob

blob = TextBlob("Now is better than never.")

# Bigrams (n=2)
bigrams = blob.ngrams(n=2)
# [WordList(['Now', 'is']), 
#  WordList(['is', 'better']), 
#  WordList(['better', 'than']), 
#  WordList(['than', 'never'])]

# Trigrams (n=3)
trigrams = blob.ngrams(n=3)
# [WordList(['Now', 'is', 'better']), 
#  WordList(['is', 'better', 'than']), 
#  WordList(['better', 'than', 'never'])]

# Convert to strings
bigram_strings = [' '.join(ng) for ng in blob.ngrams(n=2)]
# ['Now is', 'is better', 'better than', 'than never']
```

### Use Cases for N-grams

```python
def find_common_bigrams(texts, min_count=2):
    """Find bigrams that appear in multiple texts."""
    from collections import Counter
    
    all_bigrams = []
    for text in texts:
        blob = TextBlob(text)
        bigrams = [' '.join(bg) for bg in blob.ngrams(n=2)]
        all_bigrams.extend(bigrams)
    
    return {bg: count for bg, count in Counter(all_bigrams).items() if count >= min_count}

articles = [
    "Machine learning is fascinating. Deep learning is a subset of machine learning.",
    "Machine learning powers many applications. Machine learning uses algorithms."
]

common = find_common_bigrams(articles)
print(common)  # {'machine learning': 3}
```

## Parsing

### Basic Parsing

Parse text into grammatical structure:

```python
from textblob import TextBlob

text = TextBlob("And now for something completely different.")
parsed = text.parse()

print(parsed)
# And/CC/O/O now/RB/B-ADVP/O for/IN/B-PP/B-PNP 
# something/NN/B-NP/I-PNP completely/RB/B-ADJP/O 
# different/JJ/I-ADJP/O ././O/O
```

### Parse Output Format

Each word is formatted as: `WORD/POS/CHUNK/PHRASE`

- **WORD**: The actual word
- **POS**: Part-of-speech tag
- **CHUNK**: Chunk type (NP, VP, PP, ADJP, ADVP)
- **PHRASE**: Phrase type

### Chunk Tags

| Tag | Meaning |
|-----|---------|
| NP | Noun Phrase |
| VP | Verb Phrase |
| PP | Prepositional Phrase |
| ADJP | Adjective Phrase |
| ADVP | Adverb Phrase |
| O | Outside any chunk |

## WordNet Integration

### Getting Synsets

```python
from textblob import Word

word = Word("octopus")
synsets = word.synsets

# Output: [Synset('octopus.n.01'), Synset('octopus.n.02')]

# Filter by part of speech
from textblob.wordnet import VERB, NOUN, ADJ

verb_synsets = Word("hack").get_synsets(pos=VERB)
# [Synset('chop.v.05'), Synset('hack.v.02'), ...]
```

### Getting Definitions

```python
from textblob import Word

# All definitions
definitions = Word("octopus").definitions
# ['tentacles of octopus prepared as food', 
#  'bottom-living cephalopod having a soft oval body with eight long tentacles']

# Definition by part of speech
from textblob.wordnet import NOUN

definition = Word("octopus").define(pos=NOUN)
# ['tentacles of octopus prepared as food', ...]
```

### Working with Synsets Directly

```python
from textblob.wordnet import Synset

# Create synsets directly
octopus = Synset("octopus.n.02")
shrimp = Synset("shrimp.n.03")

# Calculate semantic similarity
similarity = octopus.path_similarity(shrimp)
print(f"Similarity: {similarity:.3f}")  # 0.111

# Other similarity measures
print(octopus.wup_similarity(shrimp))  # Wu-Palmer similarity
print(octopus.lch_similarity(shrimp))  # Leacock-Chordidor similarity
```

### WordNet Similarity Use Cases

```python
from textblob import Word
from textblob.wordnet import NOUN

def find_similar_words(target, candidates, threshold=0.3):
    """Find words similar to target from a list."""
    target_synsets = Word(target).get_synsets(pos=NOUN)
    
    if not target_synsets:
        return []
    
    similar = []
    for candidate in candidates:
        candidate_synsets = Word(candidate).get_synsets(pos=NOUN)
        
        for ts in target_synsets:
            for cs in candidate_synsets:
                sim = ts.path_similarity(cs)
                if sim and sim > threshold:
                    similar.append((candidate, sim))
    
    return sorted(similar, key=lambda x: x[1], reverse=True)

# Find words similar to "car"
similar = find_similar_words("car", ["automobile", "bicycle", "house", "vehicle"])
print(similar)  # [('automobile', 0.6), ('vehicle', 0.4)]
```
