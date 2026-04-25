# NLTK Tokenization - Complete Guide

## Overview

Tokenization is the process of splitting text into smaller units (tokens) such as words, sentences, or phrases. NLTK provides multiple tokenizers for different use cases and languages.

## Word Tokenization

### Punkt Tokenizer (Default)

The `word_tokenize()` function uses the Punkt tokenizer, which handles most cases correctly:

```python
from nltk import word_tokenize

text = "Dr. Smith said, 'Hello!' It's 3:30 PM on 12/25/2024."
tokens = word_tokenize(text)
print(tokens)
# ['Dr.', 'Smith', 'said', ',', "'", 'Hello', '!', "'", 
#  'It', "'s", '3:30', 'PM', 'on', '12/25/2024', '.']
```

**Features:**
- Handles contractions correctly (it's → it, 's)
- Preserves punctuation as separate tokens
- Recognizes abbreviations (Dr., Mr., etc.)
- Supports multiple languages

### Language-Specific Tokenization

```python
from nltk import word_tokenize

# German text with special handling
german_text = "Ich muss unbedingt daran denken, Mehl, usw. für einen Kuchen einzukaufen."
tokens_default = word_tokenize(german_text)  # Treats "usw." as two tokens
tokens_german = word_tokenize(german_text, language='german')  # Keeps "usw." intact

print(tokens_default)  
# [..., 'usw', '.', ...]
print(tokens_german)
# [..., 'usw.', ...]
```

**Supported languages:** english, german, spanish, french, portuguese

### Treebank Word Tokenizer

Faster alternative for Penn Treebank-style tokenization:

```python
from nltk.tokenize import TreebankWordTokenizer

tokenizer = TreebankWordTokenizer()
text = "It's a 3D rendering, isn't it?"
tokens = tokenizer.tokenize(text)

print(tokens)
# ["It", "'s", 'a', '3', 'D', 'rendering', ',', "isn", "'t", 'it', '?']
```

**Note:** Splits contractions more aggressively than Punkt.

### Regexp Tokenizer

Custom tokenization using regular expressions:

```python
from nltk.tokenize import RegexpTokenizer

# Tokenize words only (alphanumeric sequences)
tokenizer = RegexpTokenizer(r'\w+')
text = "Hello, world! This is a test."
tokens = tokenizer.tokenize(text)
print(tokens)  # ['Hello', 'world', 'This', 'is', 'a', 'test']

# Tokenize words and numbers
tokenizer = RegexpTokenizer(r'\b\w+\b|\d+(?:,\d{3})*(?:\.\d+)?')
text = "The price is $1,234.56 and quantity is 100."
tokens = tokenizer.tokenize(text)
print(tokens)  # ['price', 'is', '1,234.56', 'quantity', 'is', '100']

# Split on punctuation (gaps=True)
tokenizer = RegexpTokenizer(r'[,.!?;]', gaps=True)
text = "Hello. How are you? Fine, thanks!"
tokens = tokenizer.tokenize(text)
print(tokens)  # ['Hello', ' How are you', ' Fine', ' thanks']
```

### Tweet Tokenizer

Optimized for social media text with hashtags, mentions, emojis:

```python
from nltk.tokenize import TweetTokenizer

tknzr = TweetTokenizer()

# Basic tokenization
text = "This is a cooool #dummysmiley: :-) :-P <3 and some arrows < > -> <--"
tokens = tknzr.tokenize(text)
print(tokens)
# ['This', 'is', 'a', 'cooool', '#dummysmiley', ':', ':-)', 
#  ':-P', '<3', 'and', 'some', 'arrows', '<', '>', '->', '<--']

# With mentions and hashtags
text = "@Joyster2012 @CathStaincliffe Good for you, girl!! Best wishes :-)"
tokens = tknzr.tokenize(text)
print(tokens)
# ['@Joyster2012', '@CathStaincliffe', 'Good', 'for', 'you', ',', 
#  'girl', '!', '!', 'Best', 'wishes', ':-)']

# Strip handles and reduce repeated characters
tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
text = "@remy: This is waaaaayyyy too much for you!!!!!!"
tokens = tknzr.tokenize(text)
print(tokens)
# [':', 'This', 'is', 'waaayyy', 'too', 'much', 'for', 'you', '!', '!', '!']

# Preserve case control
tknzr = TweetTokenizer(preserve_case=False)
text = "@jrmy: I'm REALLY HAPPYYY about that! NICEEEE :D :P"
tokens = tknzr.tokenize(text)
print(tokens)
# ['@jrmy', ':', "i'm", 'really', 'happyyy', 'about', 'that', '!', 
#  'niceeee', ':D', ':P']
```

**Parameters:**
- `strip_handles`: Remove @mentions
- `reduce_len`: Reduce repeated characters to 3 (e.g., "soooo" → "soo")
- `preserve_case`: Convert to lowercase if False

### Multi-word Expression Tokenizer

Combine consecutive tokens into single multi-word expressions:

```python
from nltk.tokenize import MWETokenizer, TreebankWordTokenizer

# Define multi-word expressions
mwe_tokens = [('hors', "d'oeuvre"), ('far', 'away'), ('New', 'York')]
mwe_tokenizer = MWETokenizer(mwe_tokens, separator='_')

# Apply after basic tokenization
text = "An hors d'oeuvre in New York, far away from home"
tokenizer = TreebankWordTokenizer()
tokens = tokenizer.tokenize(text)
print(tokens)  
# ['An', 'hors', "d'oeuvre", 'in', 'New', 'York', ',', 'far', 'away', 'from', 'home']

# Combine MWEs
combined = mwe_tokenizer.tokenize(tokens)
print(combined)
# ['An', 'hors_d_\'oeuvre', 'in', 'New_York', ',', 'far_away', 'from', 'home']
```

## Sentence Tokenization

### Punkt Sentence Tokenizer

Default sentence boundary detection:

```python
from nltk import sent_tokenize

text = "Dr. Smith went to the hospital. He's a doctor. What about St. Mary's?"
sentences = sent_tokenize(text)
print(sentences)
# ['Dr. Smith went to the hospital.', "He's a doctor.", "What about St. Mary's?"]

# Multi-paragraph text
text2 = """First sentence. Second sentence.

New paragraph, third sentence! Fourth?"""
sentences2 = sent_tokenize(text2)
print(sentences2)
# ['First sentence.', 'Second sentence.', 
#  'New paragraph, third sentence!', 'Fourth?']
```

### Language-Specific Sentence Tokenization

```python
from nltk.tokenize import PunktSentenceTokenizer

# Train on specific language corpus
from nltk.corpus import brown

# English (default)
tokenizer_eng = PunktSentenceTokenizer()
sentences_eng = tokenizer_eng.tokenize(text)

# German (load pre-trained model)
tokenizer_deu = PunktSentenceTokenizer(load_lang_args='german', verbose=False)
german_text = "Herr Müller ist Arzt. Dr. Schmidt arbeitet im Krankenhaus."
sentences_deu = tokenizer_deu.tokenize(german_text)
print(sentences_deu)
# ['Herr Müller ist Arzt.', 'Dr. Schmidt arbeitet im Krankenhaus.']
```

### Custom Sentence Tokenizer

Train on domain-specific text:

```python
from nltk.tokenize import PunktSentenceTokenizer
from nltk.corpus import gutenberg

# Get training data from specific domain
train_text = gutenberg.raw('austen-emma.txt')
tokenizer = PunktSentenceTokenizer()
tokenizer.train(train_text)

# Use trained tokenizer
test_text = "Chapter 1. Emma Woodhouse, handsome, clever, and rich."
sentences = tokenizer.tokenize(test_text)
print(sentences)
```

## Text Tiling (Topic Segmentation)

Segment text into coherent subtopics:

```python
from nltk.tokenize import TextTilingTokenizer
from nltk.corpus import brown

tokenizer = TextTilingTokenizer()
text = brown.raw()[0:5000]  # First 5000 characters

# Tokenize into topic segments
segments = tokenizer.tokenize(text)
print(f"Number of segments: {len(segments)}")
print(f"First segment preview: {segments[0][:200]}...")
```

**Parameters:**
- `similarity_method`: 'log_likelihood', 'dice', 'cosine' (default: 'log_likelihood')
- `smoothing_method`: 'add_k', 'add_one', 'none' (default: 'add_k')

## Detokenization

Reconstruct text from tokens:

```python
from nltk.tokenize import TreebankWordDetokenizer, word_tokenize

text = "Hello, world! How are you?"
tokens = word_tokenize(text)

# Detokenize
detokenizer = TreebankWordDetokenizer()
reconstructed = detokenizer.detokenize(tokens)
print(reconstructed)
# "Hello, world! How are you?"

# Works with contractions and parentheses
text2 = "I've been there. (It was great!)"
tokens2 = word_tokenize(text2)
reconstructed2 = detokenizer.detokenize(tokens2)
print(reconstructed2)
# "I've been there. (It was great!)"
```

## Tokenization Comparison

| Tokenizer | Best For | Speed | Accuracy | Special Features |
|-----------|----------|-------|----------|------------------|
| `word_tokenize()` | General purpose | Medium | High | Handles abbreviations, contractions |
| `TreebankWordTokenizer` | Penn Treebank style | Fast | Medium | Consistent with linguistic standards |
| `RegexpTokenizer` | Custom patterns | Very Fast | Variable | Full control via regex |
| `TweetTokenizer` | Social media | Fast | High (for tweets) | Handles emojis, hashtags, mentions |
| `MWETokenizer` | Multi-word expressions | Fast | High | Preserves compound terms |

## Common Patterns

### Text Preprocessing Pipeline

```python
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

def preprocess_text(text):
    # Download required data (run once)
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')
    
    # Lowercase
    text = text.lower()
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if w not in stop_words]
    
    # Stem
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(w) for w in tokens]
    
    return tokens

text = "The quick brown foxes are jumping over the lazy dogs!"
result = preprocess_text(text)
print(result)
# ['quick', 'brown', 'fox', 'jump', 'over', 'lazi', 'dog']
```

### Token Frequency Analysis

```python
from nltk import word_tokenize
from nltk.probability import FreqDist

text = """Natural language processing enables computers to understand human language.
           NLP is a fascinating field that combines linguistics and computer science."""

tokens = word_tokenize(text.lower())

# Create frequency distribution
fdist = FreqDist(tokens)

# Most common tokens
print("Top 10 tokens:")
for token, freq in fdist.most_common(10):
    print(f"  {token}: {freq}")

# Plot distribution (requires matplotlib)
# fdist.plot(20, cumulative=True)
```

## Troubleshooting

### Contractions Not Splitting Correctly

**Problem**: "don't" stays as one token instead of ["do", "n't"]

**Solution**: Use Punkt tokenizer or configure Treebank:

```python
from nltk import word_tokenize  # Uses Punkt by default
tokens = word_tokenize("I don't know")
print(tokens)  # ['I', "do", "n't", 'know']
```

### Abbreviations Causing Wrong Sentence Boundaries

**Problem**: "Dr. Smith" split into two sentences

**Solution**: Use language-specific sentence tokenizer or add abbreviations:

```python
from nltk.tokenize import PunktSentenceTokenizer

# Add custom abbreviations
tokenizer = PunktSentenceTokenizer()
tokenizer._params.abbrev_types.add('prof')
tokenizer._params.abbrev_types.add('sr')

text = "Prof. Johnson and Sr. Williams met yesterday."
sentences = tokenizer.tokenize(text)
print(sentences)  # ['Prof. Johnson and Sr. Williams met yesterday.']
```

### Unicode/Emoji Tokenization Issues

**Problem**: Emojis not tokenized correctly

**Solution**: Use TweetTokenizer which handles emoji sequences:

```python
from nltk.tokenize import TweetTokenizer

tknzr = TweetTokenizer()
text = "I love Python! 😊🐍 #programming"
tokens = tknzr.tokenize(text)
print(tokens)  # ['I', 'love', 'Python', '!', '😊', '🐍', '#programming']
```

## Performance Tips

1. **Reuse tokenizers**: Create tokenizer instances once and reuse them
2. **Batch processing**: Process multiple texts together when possible
3. **Choose appropriate tokenizer**: Use faster tokenizers for simple cases
4. **Cache results**: Store tokenized results if processing the same text repeatedly

```python
# Good: Reuse tokenizer instance
from nltk.tokenize import TreebankWordTokenizer

tokenizer = TreebankWordTokenizer()  # Create once

texts = ["Text one.", "Text two.", "Text three."]
all_tokens = [tokenizer.tokenize(text) for text in texts]
```

## References

- **NLTK Tokenization Documentation**: https://www.nltk.org/howto/tokenize.html
- **Punkt Tokenizer Paper**: Kiss, T. & Strunk, J. (2006). Unsupervised Multilingual Sentence Boundary Detection
- **Treebank Guidelines**: https://www.ling.upenn.edu/courses/Ling2400/treebank/
