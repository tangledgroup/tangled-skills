# Advanced Model Configuration

This reference covers advanced topics including custom models, component overrides, and the Blobber factory pattern.

## Overview

TextBlob allows you to override default implementations for:
- Sentiment analyzers
- POS taggers
- Noun phrase extractors
- Tokenizers
- Parsers

This section shows how to customize each component and when to use alternatives.

## Sentiment Analyzers

### Available Analyzers

1. **PatternAnalyzer** (default) - Based on pattern library
   - Returns: `Sentiment(polarity, subjectivity)`
   - Fast, rule-based approach
   
2. **NaiveBayesAnalyzer** - Machine learning based
   - Returns: `Sentiment(classification, p_pos, p_neg)`
   - Trained on movie reviews corpus

### Using PatternAnalyzer (Default)

```python
from textblob import TextBlob

text = TextBlob("I love this library")
sentiment = text.sentiment

# Output from PatternAnalyzer:
# Sentiment(polarity=0.6, subjectivity=0.6)

print(sentiment.polarity)      # 0.6
print(sentiment.subjectivity)  # 0.6
```

### Using NaiveBayesAnalyzer

```python
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

# Create TextBlob with custom analyzer
text = TextBlob("I love this library", 
                analyzer=NaiveBayesAnalyzer())

sentiment = text.sentiment

# Output from NaiveBayesAnalyzer:
# Sentiment(classification='pos', p_pos=0.7996, p_neg=0.2004)

print(sentiment.classification)  # 'pos'
print(sentiment.p_pos)           # 0.7996
print(sentiment.p_neg)           # 0.2004
```

### Comparing Analyzers

```python
from textblob import TextBlob
from textblob.sentiments import PatternAnalyzer, NaiveBayesAnalyzer

text = "This movie was absolutely terrible and boring."

# Pattern analyzer
pattern_blob = TextBlob(text, analyzer=PatternAnalyzer())
print("Pattern:", pattern_blob.sentiment)

# Naive Bayes analyzer
nb_blob = TextBlob(text, analyzer=NaiveBayesAnalyzer())
print("NaiveBayes:", nb_blob.sentiment)

# Output:
# Pattern: Sentiment(polarity=-0.65, subjectivity=0.6)
# NaiveBayes: Sentiment(classification='neg', p_pos=0.15, p_neg=0.85)
```

### Custom Sentiment Analyzer

Create a custom analyzer by implementing the base class:

```python
from textblob.base import BaseSentimentAnalyzer
from textblob import TextBlob

class CustomSentimentAnalyzer(BaseSentimentAnalyzer):
    """Custom sentiment analyzer using simple keyword matching."""
    
    def __init__(self):
        self.positive_words = {'great', 'good', 'excellent', 'amazing', 'love'}
        self.negative_words = {'bad', 'terrible', 'horrible', 'awful', 'hate'}
    
    def __call__(self, text):
        """Analyze sentiment of text."""
        words = set(str(text).lower().split())
        
        pos_count = len(words & self.positive_words)
        neg_count = len(words & self.negative_words)
        
        total = pos_count + neg_count or 1
        
        polarity = (pos_count - neg_count) / total
        subjectivity = min(1.0, (pos_count + neg_count) / len(words)) if words else 0
        
        return Sentiment(polarity=polarity, subjectivity=subjectivity)

from textblob.en.sentiments import Sentiment

# Use custom analyzer
analyzer = CustomSentimentAnalyzer()
text = TextBlob("This is great and amazing!", analyzer=analyzer)
print(text.sentiment)  # Sentiment(polarity=1.0, subjectivity=0.4)
```

## POS Taggers

### Available Taggers

1. **PatternTagger** (default) - Based on pattern library
   - Fast, rule-based
   - Good general accuracy
   
2. **NLTKTagger** - Uses NLTK's averaged perceptron tagger
   - Requires NumPy
   - Generally more accurate

### Using PatternTagger (Default)

```python
from textblob import TextBlob

text = TextBlob("Python is a high-level programming language.")
tags = text.tags

# Output from PatternTagger:
# [('Python', 'NNP'), ('is', 'VBZ'), ('a', 'DT'), 
#  ('high-level', 'JJ'), ('programming', 'NN'), ('language', 'NN')]
```

### Using NLTKTagger

```python
from textblob import TextBlob
from textblob.taggers import NLTKTagger

# Create tagger instance
nltk_tagger = NLTKTagger()

# Use with TextBlob
text = TextBlob("Tag! You're It!", pos_tagger=nltk_tagger)
tags = text.pos_tags

# Output from NLTKTagger:
# [(Word('Tag'), 'NN'), (Word('You'), 'PRP'), 
#  (Word("'re"), 'VBP'), (Word('It'), 'PRP')]

# Note: NLTKTagger returns Word objects instead of strings
```

### Comparing Taggers

```python
from textblob import TextBlob
from textblob.taggers import PatternTagger, NLTKTagger

text_str = "The quick brown fox jumps over the lazy dog."

# Pattern tagger
pattern_text = TextBlob(text_str, pos_tagger=PatternTagger())
print("Pattern:", pattern_text.tags)

# NLTK tagger
nltk_text = TextBlob(text_str, pos_tagger=NLTKTagger())
print("NLTK:", [(str(w), t) for w, t in nltk_text.pos_tags])
```

### Custom POS Tagger

```python
from textblob.base import BasePOS_TAGGER

class SimpleRuleTagger(BasePOSTagger):
    """Simple rule-based tagger for demonstration."""
    
    def tag(self, words):
        """Tag a list of words."""
        # Very simple rules (not production-ready)
        articles = {'the', 'a', 'an'}
        verbs = {'is', 'are', 'was', 'were', 'run', 'runs'}
        
        tags = []
        for word in words:
            if word.lower() in articles:
                tags.append((word, 'DT'))
            elif word.lower() in verbs:
                tags.append((word, 'VB'))
            else:
                tags.append((word, 'NN'))  # Default to noun
        
        return tags

# Use custom tagger
tagger = SimpleRuleTagger()
text = TextBlob("The cat runs fast.", pos_tagger=tagger)
print(text.tags)
```

## Noun Phrase Extractors

### Available Extractors

1. **FastNPExtractor** (default) - Based on Shlomi Babluki's implementation
   - Fast, rule-based
   - Good for most use cases
   
2. **ConllExtractor** - Uses CoNLL 2000 corpus
   - Trains a tagger
   - More accurate but slower

### Using FastNPExtractor (Default)

```python
from textblob import TextBlob

text = TextBlob("Python is a high-level programming language.")
phrases = text.noun_phrases

# Output from FastNPExtractor:
# WordList(['python', 'high-level programming language'])
```

### Using ConllExtractor

```python
from textblob import TextBlob
from textblob.np_extractors import ConllExtractor

# Create extractor instance
extractor = ConllExtractor()

# Use with TextBlob
text = TextBlob("Python is a high-level programming language.", 
                np_extractor=extractor)

phrases = text.noun_phrases

# Output from ConllExtractor:
# WordList(['python', 'high-level programming language'])
```

### Comparing Extractors

```python
from textblob import TextBlob
from textblob.np_extractors import FastNPExtractor, ConllExtractor

text_str = "Machine learning is a subset of artificial intelligence used for pattern recognition."

# Fast extractor
fast_text = TextBlob(text_str, np_extractor=FastNPExtractor())
print("Fast:", fast_text.noun_phrases)

# CoNLL extractor
conll_text = TextBlob(text_str, np_extractor=ConllExtractor())
print("CoNLL:", conll_text.noun_phrases)
```

### Custom Noun Phrase Extractor

```python
from textblob.base import BaseNPExtractor
from textblob import WordList

class SimpleNPExtractor(BaseNPExtractor):
    """Simple noun phrase extractor using POS patterns."""
    
    def extract_noun_phrases(self, tagged_words):
        """Extract noun phrases from tagged words."""
        phrases = []
        current_phrase = []
        
        # Look for adjective-noun sequences
        noun_tags = {'NN', 'NNS', 'NNP', 'NNPS'}
        adj_tags = {'JJ', 'JJR', 'JJS'}
        
        for word, tag in tagged_words:
            if tag in noun_tags:
                current_phrase.append(str(word))
                # End phrase at noun
                if current_phrase:
                    phrases.append(' '.join(current_phrase))
                    current_phrase = []
            elif tag in adj_tags and not current_phrase:
                # Start new phrase with adjective
                current_phrase = [str(word)]
            else:
                # Reset on other tags
                current_phrase = []
        
        return WordList(phrases)

# Use custom extractor
extractor = SimpleNPExtractor()
text = TextBlob("The quick brown fox is fast.", np_extractor=extractor)
print(text.noun_phrases)
```

## Tokenizers

### Default Tokenizers

TextBlob uses:
- `WordTokenizer` for words
- `SentenceTokenizer` for sentences (NLTK-based)

### Using Custom Tokenizers

```python
from textblob import TextBlob
from nltk.tokenize import TabTokenizer, BlanklineTokenizer

# Tab tokenizer
tab_text = "This is\ta rather tabby\tblob."
blob = TextBlob(tab_text, tokenizer=TabTokenizer())

print(blob.tokens)
# WordList(['This is', 'a rather tabby', 'blob.'])

# Blank line tokenizer
multi_para = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
blob = TextBlob(multi_para)

paragraphs = blob.tokenize(BlanklineTokenizer())
print(paragraphs)
# WordList(['First paragraph.', 'Second paragraph.', 'Third paragraph.'])
```

### Tokenize Method

Apply tokenizer without creating new TextBlob:

```python
from textblob import TextBlob
from nltk.tokenize import RegexpTokenizer

text = "One, two, three, four."
blob = TextBlob(text)

# Use regex tokenizer
tokenizer = RegexpTokenizer(r'\w+')
tokens = blob.tokenize(tokenizer)

print(tokens)
# WordList(['One', 'two', 'three', 'four'])
```

### Custom Tokenizer

```python
from nltk.tokenize.api import TokenizerI

class SpaceTokenizer(TokenizerI):
    """Simple space-based tokenizer."""
    
    def tokenize(self, sentence):
        return sentence.split()
    
    def span_tokenize(self, sentence):
        # Required method for NLTK compatibility
        tokens = self.tokenize(sentence)
        start = 0
        spans = []
        for token in tokens:
            end = start + len(token)
            spans.append((start, end))
            start = end + 1  # Skip space
        return spans

# Use custom tokenizer
text = "This is a test."
blob = TextBlob(text, tokenizer=SpaceTokenizer())
print(blob.tokens)
```

## Parsers

### Available Parsers

1. **PatternParser** - Based on pattern library (default)
   - Fast, rule-based parsing
   - Provides chunk and phrase information

### Using PatternParser

```python
from textblob import TextBlob
from textblob.parsers import PatternParser

text = TextBlob("Parsing is fun.", parser=PatternParser())
parsed = text.parse()

print(parsed)
# Parsing/VBG/B-VP/O is/VBZ/I-VP/O fun/NN/I-VP/O ././O/O
```

### Parse Output Format

Each word is formatted as: `WORD/POS/CHUNK/PHRASE`

Example breakdown:
```
Parsing/VBG/B-VP/O
  - WORD: Parsing
  - POS: VBG (verb, gerund)
  - CHUNK: B-VP (begin verb phrase)
  - PHRASE: O (outside larger phrase)
```

### Custom Parser

```python
from textblob.base import BaseParser

class SimpleParser(BaseParser):
    """Simple parser that only identifies noun phrases."""
    
    def parse(self, text):
        """Parse text and return simplified output."""
        from textblob import TextBlob
        
        blob = TextBlob(str(text))
        result = []
        
        for word, pos in blob.tags:
            if pos in ('NN', 'NNS', 'NNP', 'NNPS'):
                chunk = 'B-NP'
            else:
                chunk = 'O'
            
            result.append(f"{word}/{pos}/{chunk}/O")
        
        return ' '.join(result)

# Use custom parser
parser = SimpleParser()
text = TextBlob("The cat runs.", parser=parser)
print(text.parse())
```

## Blobber Factory Class

### What is Blobber?

`Blobber` is a factory class that creates TextBlobs with shared models. This is useful when:
- Processing many texts with the same configuration
- Wanting to avoid repeatedly passing model instances
- Needing consistent behavior across multiple TextBlobs

### Basic Usage

```python
from textblob import Blobber
from textblob.taggers import NLTKTagger

# Create Blobber with custom tagger
blobber = Blobber(pos_tagger=NLTKTagger())

# Create multiple TextBlobs
blob1 = blobber("This is the first text.")
blob2 = blobber("This is the second text.")
blob3 = blobber("And a third text.")

# All blobs share the same tagger instance
print(blob1.pos_tagger is blob2.pos_tagger)  # True
print(blob2.pos_tagger is blob3.pos_tagger)  # True
```

### Configuring Multiple Components

```python
from textblob import Blobber
from textblob.taggers import NLTKTagger
from textblob.np_extractors import ConllExtractor
from textblob.sentiments import NaiveBayesAnalyzer

# Create Blobber with multiple custom components
blobber = Blobber(
    pos_tagger=NLTKTagger(),
    np_extractor=ConllExtractor(),
    analyzer=NaiveBayesAnalyzer()
)

# All created TextBlobs use these components
text1 = blobber("First document to analyze.")
text2 = blobber("Second document with same configuration.")

print(text1.tags)           # Uses NLTKTagger
print(text1.noun_phrases)   # Uses ConllExtractor
print(text1.sentiment)      # Uses NaiveBayesAnalyzer
```

### Blobber with Classifier

```python
from textblob import Blobber
from textblob.classifiers import NaiveBayesClassifier

# Training data
train_data = [
    ("Great product!", "pos"),
    ("Terrible experience", "neg"),
]

# Create classifier
classifier = NaiveBayesClassifier(train_data)

# Create Blobber with classifier
blobber = Blobber(classifier=classifier)

# Create TextBlobs that can classify
text1 = blobber("This is amazing!")
text2 = blobber("This is awful.")

print(text1.classify())  # 'pos'
print(text2.classify())  # 'neg'
```

### Performance Benefits

```python
import time

from textblob import TextBlob, Blobber
from textblob.taggers import NLTKTagger

texts = ["This is a sample text. " * 10 for _ in range(100)]

# Without Blobber (create tagger each time)
start = time.time()
tagger = NLTKTagger()
for text in texts:
    blob = TextBlob(text, pos_tagger=tagger)
    _ = blob.tags
time_without_blobber = time.time() - start

# With Blobber (share tagger instance)
start = time.time()
blobber = Blobber(pos_tagger=NLTKTagger())
for text in texts:
    blob = blobber(text)
    _ = blob.tags
time_with_blobber = time.time() - start

print(f"Without Blobber: {time_without_blobber:.3f}s")
print(f"With Blobber: {time_with_blobber:.3f}s")
```

## Extensions Framework

### Available Extensions

TextBlob supports extensions for:

**Languages:**
- `textblob-fr` - French language support
- `textblob-de` - German language support

**Taggers:**
- `textblob-aptagger` - Averaged Perceptron tagger (fast and accurate)

### Installing Extensions

```bash
# French support
pip install textblob-fr

# German support
pip install textblob-de

# Averaged Perceptron tagger
pip install textblob-aptagger
```

### Using Extensions

Example with APTagger:

```python
from textblob import TextBlob
from textblob_aptagger import Postag

# Use APTagger instead of default
tagger = Postag()
text = TextBlob("Python is great.", pos_tagger=tagger)
print(text.tags)
```

### Creating Custom Extensions

To create your own extension:

1. Inherit from appropriate base classes in `textblob.base`
2. Implement required methods
3. Package and distribute via PyPI

See the [Contributing guide](https://github.com/sloria/TextBlob/blob/0.20.0/CONTRIBUTING.rst) for extension development details.

## Migration Notes

### From TextBlob <= 0.7.1

Package renamed from `text` to `textblob`:

```python
# Old (pre-0.8)
from text.blob import TextBlob, Word, Blobber
from text.classifiers import NaiveBayesClassifier

# New (0.8+)
from textblob import TextBlob, Word, Blobber
from textblob.classifiers import NaiveBayesClassifier
```

### Removed Features (0.18+)

Translation features removed:
- `TextBlob.translate()` - Use Google Translate API instead
- `TextBlob.detect_language()` - Use language detection libraries
- `textblob.translate` module - No longer available

## Best Practices

### When to Override Models

**Override when:**
- You need higher accuracy for specific domains
- Default models don't meet performance requirements
- You have domain-specific training data
- Processing speed is critical (PatternTagger vs NLTKTagger)

**Don't override when:**
- Default models work adequately
- Adding complexity isn't justified
- You're prototyping or exploring

### Model Selection Guide

| Task | Recommended Component | Reason |
|------|----------------------|--------|
| General POS tagging | PatternTagger (default) | Fast, good accuracy |
| Accurate POS tagging | NLTKTagger | More accurate, requires NumPy |
| Fast noun phrases | FastNPExtractor (default) | Good speed/accuracy tradeoff |
| Accurate noun phrases | ConllExtractor | Better for complex sentences |
| Quick sentiment | PatternAnalyzer (default) | Fast, reasonable accuracy |
| ML-based sentiment | NaiveBayesAnalyzer | Better for domain-specific text |

### Memory Considerations

```python
# Efficient: Share models with Blobber
blobber = Blobber(pos_tagger=NLTKTagger())
blobs = [blobber(text) for text in texts]

# Less efficient: Create new taggers
blobs = [TextBlob(text, pos_tagger=NLTKTagger()) for text in texts]
```
