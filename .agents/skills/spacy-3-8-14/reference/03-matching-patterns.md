# Rule-Based Matching and Pattern Recognition

This guide covers spaCy's rule-based matching capabilities: Matcher, PhraseMatcher, SpanMatcher, and similarity search.

## The Matcher

The Matcher finds patterns of tokens based on their linguistic attributes.

### Basic Usage

```python
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Define a pattern: ADJ + NOUN
pattern = [{"POS": "ADJ"}, {"POS": "NOUN"}]
matcher.add("ADJ_NOUN", [pattern])

# Process text
doc = nlp("The quick brown fox jumps")
matches = matcher(doc)

# Iterate over matches
for match_id, start, end in matches:
    span = doc[start:end]
    print(match_id, span.text)
```

### Pattern Specifications

Patterns can specify various token attributes:

```python
# Match specific text
pattern = [{"TEXT": "John"}, {"TEXT": "Smith"}]
matcher.add("PERSON_NAME", [pattern])

# Match with POS tag
pattern = [{"POS": "VERB", "MORPH": {"VerbForm": "Inf"}}]
matcher.add("INFINITIVE", [pattern])

# Match negation patterns
pattern = [{"TEXT": {"IN": ["not", "never", "no"]}}, {"POS": "ADJ"}]
matcher.add("NEG_ADJ", [pattern])

# Match with length constraint
pattern = [{"IS_PUNCT": True, "OP": "*"}, {"POS": "NOUN"}]
matcher.add("PUNCT_NOUN", [pattern])
```

### Pattern Operators

spaCy supports operators for flexible matching:

| Operator | Description | Example |
|----------|-------------|---------|
| `*` | Zero or more | `{"OP": "*"}` matches 0+ tokens |
| `+` | One or more | `{"OP": "+"}` matches 1+ tokens |
| `?` | Optional | `{"OP": "?"}` matches 0 or 1 token |
| `{n,m}` | Range | `{"OP": "{2,4}"}` matches 2-4 tokens |

```python
# Zero or more adjectives before noun
pattern = [
    {"POS": "ADJ", "OP": "*"},
    {"POS": "NOUN"}
]
matcher.add("MODIFIED_NOUN", [pattern])

doc = nlp("The very quick brown fox")
for match_id, start, end in matcher(doc):
    print(doc[start:end].text)  # "quick brown fox"

# Optional middle element
pattern = [
    {"TEXT": "Mr"},
    {"TEXT": {"IS_TITLE": True}, "OP": "?"},
    {"POS": "PROPN"}
]
matcher.add("TITLE_NAME", [pattern])

# Range operator
pattern = [
    {"POS": "ADJ", "OP": "{1,3}"},
    {"POS": "NOUN"}
]
matcher.add("MULTI_ADJ_NOUN", [pattern])
```

### Multiple Patterns per Label

You can add multiple alternative patterns for the same label:

```python
# Match phone numbers with different formats
patterns = [
    [{"TEXT": {"REGEX": r"\d{3}"}, "IS_SPACE": False}],  # Area code
    [{"TEXT": "-"}],  # Hyphen (optional)
    [{"TEXT": {"REGEX": r"\d{4}"}}]  # Number
]

# Add multiple pattern variations
phone_patterns = [
    [{"TEXT": {"REGEX": r"\d{3}"}}],
    [{"TEXT": "-"}],
    [{"TEXT": {"REGEX": r"\d{3}"}}],
    [{"TEXT": "-"}],
    [{"TEXT": {"REGEX": r"\d{4}"}}]
]

matcher.add("PHONE", [phone_patterns])

# Alternative patterns
patterns = [
    [{"TEXT": {"REGEX": r"\(\d{3}\)"}}, {"TEXT": {"REGEX": r"\d{3}-\d{4}"}}],
    [{"TEXT": {"REGEX": r"\d{3}-\d{3}-\d{4}"}}]
]
matcher.add("PHONE_ALT", patterns)
```

### Excluding Matches

Use the `exclude` parameter to filter out nested matches:

```python
doc = nlp("The quick brown fox")
matches = matcher(doc, exclude="OVERLAP")

# Only non-overlapping matches are returned
```

### Accessing Match Details

```python
for match_id, start, end in matches:
    # Get the label name
    label_name = matcher.get_label(match_id)
    
    # Get the matched span
    span = doc[start:end]
    
    # Get pattern details
    print(f"Label: {label_name}")
    print(f"Text: {span.text}")
    print(f"Tokens: {[t.text for t in span]}")
```

## PhraseMatcher

PhraseMatcher matches phrases and longer sequences with more flexibility.

### Basic Usage

```python
import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab, attr="TEXT")

# Create patterns from text
pattern_text = ["New York", "Los Angeles", "San Francisco"]
pattern_docs = [nlp(text) for text in pattern_text]

# Add patterns with label
matcher.add("CITY", None, *pattern_docs)

# Process text
doc = nlp("I live in New York and visit Los Angeles often.")
matches = matcher(doc)

for match_id, start, end in matches:
    print(doc[start:end].text)
```

### Matching on Different Attributes

```python
# Match on TEXT (default)
matcher_text = PhraseMatcher(nlp.vocab, attr="TEXT")

# Match on lemma (base form)
matcher_lemma = PhraseMatcher(nlp.vocab, attr="LEMMA")

# Create lemma-based patterns
patterns = [nlp("run"), nlp("running"), nlp("ran")]
matcher_lemma.add("RUN_VERB", None, *patterns)

doc = nlp("I ran yesterday and am running today")
for match_id, start, end in matcher_lemma(doc):
    print(doc[start:end].text)  # Matches "ran" and "running"
```

### Fuzzy Matching with PhraseMatcher

PhraseMatcher supports some flexibility:

```python
# Case-insensitive matching
matcher = PhraseMatcher(nlp.vocab, attr="TEXT", invalid_attrs={"IS_UPPER"})

patterns = [nlp("new york"), nlp("NEW YORK")]
matcher.add("CITY", None, *patterns)

doc = nlp("I visited New York and new york")
for match_id, start, end in matcher(doc):
    print(doc[start:end].text)
```

## SpanMatcher

SpanMatcher (available in spaCy 3.4+) matches patterns against spans rather than just tokens.

### Basic Usage

```python
import spacy
from spacy.matcher import SpanMatcher

nlp = spacy.load("en_core_web_sm")
matcher = SpanMatcher(attr="TEXT")

# Define patterns that work on spans
patterns = [
    {"label": "LOCATION", "pattern": [{"TEXT": {"REGEX": r"[A-Z][a-z]+ [A-Z][a-z]+"}}]},
]

matcher.add("LOCATIONS", patterns)

doc = nlp("I live in New York and work in San Francisco.")
matches = matcher(doc)

for label, spans in matches.items():
    for span in spans:
        print(label, span.text)
```

### Advanced Span Patterns

```python
# Match spans with specific properties
patterns = [
    {
        "label": "LONG_NP",
        "pattern": [
            {"SENT_START": False},
            {"OP": "*"},
            {"POS": "NOUN"},
            {"OP": "*"}
        ],
        "span": {"LENGTH": {">": 3}}  # Span must have more than 3 tokens
    }
]

matcher = SpanMatcher(attr="TEXT")
matcher.add("PATTERNS", patterns)
```

## Similarity and Vector Operations

spaCy supports semantic similarity when using models with word vectors.

### Word Similarity

```python
# Load model with vectors
nlp = spacy.load("en_core_web_md")  # or _lg for better vectors

# Compare words
similarity = nlp("cat").similarity(nlp("dog"))
print(similarity)  # High similarity (both animals)

similarity = nlp("cat").similarity(nlp("car"))
print(similarity)  # Lower similarity

# Compare with document
doc = nlp("The cat sat on the mat")
word = nlp("kitten")
print(doc.similarity(word))
```

### Document Similarity

```python
doc1 = nlp("The quick brown fox jumps over the lazy dog")
doc2 = nlp("A fast fox leaps over a sleeping canine")
doc3 = nlp("Database optimization and SQL queries")

print(doc1.similarity(doc2))  # High similarity
print(doc1.similarity(doc3))  # Low similarity
```

### Finding Similar Words

```python
# Find most similar words in vocabulary
word = nlp("king")
most_similar = word.most_similar(topn=5)

for w_score, w_vocab in most_similar:
    print(w_vocab.text, w_score)
    
# Output might include: queen, prince, man, boy, etc.
```

### Vector Operations

```python
# Access token vectors
token = nlp("king")
print(token.vector.shape)  # (300,) for en_core_web_md
print(token.has_vector)    # True

# Manual vector operations
import numpy as np

vec1 = nlp("man").vector
vec2 = nlp("woman").vector
vec3 = nlp("king").vector

# Classic word analogy: king - man + woman ≈ queen
result_vec = vec3 - vec1 + vec2

# Find closest word to result
most_similar = nlp.vocab.most_similar([result_vec], topn=5)
print(most_similar[0][0].text)  # Should be "queen" or similar
```

## EntityRuler

EntityRuler adds rule-based named entity recognition to your pipeline.

### Basic Usage

```python
import spacy
from spacy.pipeline import EntityRuler

nlp = spacy.blank("en")
ruler = nlp.add_pipe("entity_ruler")

# Add patterns
patterns = [
    {
        "label": "PRODUCT",
        "pattern": [{"TEXT": "iPhone"}]
    },
    {
        "label": "PRODUCT",
        "pattern": [{"TEXT": "MacBook"}]
    },
    {
        "label": "PRODUCT", 
        "pattern": [{"TEXT": "iPad"}]
    }
]

ruler.add_patterns(patterns)

# Process text
doc = nlp("I bought an iPhone and a MacBook")
for ent in doc.ents:
    print(ent.text, ent.label_)
```

### Complex Patterns with EntityRuler

```python
patterns = [
    # Match "iPhone" followed by optional number
    {
        "label": "PRODUCT",
        "pattern": [
            {"TEXT": "iPhone"},
            {"IS_DIGIT": True, "OP": "?"}
        ]
    },
    # Match "version" + number patterns
    {
        "label": "VERSION",
        "pattern": [
            {"TEXT": {"IN": ["version", "v"]}},
            {"TEXT": {"REGEX": r"\d+(\.\d+)*"}}
        ]
    },
    # Match email addresses with regex
    {
        "label": "EMAIL",
        "pattern": [{"TEXT": {"REGEX": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"}}]
    }
]

ruler.add_patterns(patterns)
```

### Adding Patterns Incrementally

```python
# Add single pattern
ruler.add("PRODUCT", [{"TEXT": "Android"}])

# Add multiple patterns at once
patterns = [
    {"label": "OS", "pattern": [{"TEXT": "Windows"}]},
    {"label": "OS", "pattern": [{"TEXT": "Linux"}]},
]
ruler.add_patterns(patterns)

# Check added patterns
print(ruler.get_patterns("PRODUCT"))
```

### EntityRuler with Fuzzy Matching

```python
# Enable fuzzy matching for slight variations
ruler = nlp.add_pipe("entity_ruler", config={"validation": {"ent_shape_match": False}})

patterns = [
    {
        "label": "PRODUCT",
        "pattern": [{"TEXT": "iPhone"}],
        "ent_type": "PRODUCT"
    }
]

# Add with performance options
ruler.add_patterns(patterns, performance=True)
```

## AttributeRuler

AttributeRuler sets token attributes based on rules.

### Basic Usage

```python
import spacy
from spacy.pipeline import AttributeRuler

nlp = spacy.blank("en")
ruler = nlp.add_pipe("attribute_ruler")

# Add pattern to set custom attribute
pattern = {"TEXT": {"REGEX": r"\bAPI\b"}}
attr = {"like_email": True}
ruler.add(pattern, attr)

# Process text
doc = nlp("Call the API for more information")
for token in doc:
    if token.text == "API":
        print(token._.like_email)  # True
```

### Setting Multiple Attributes

```python
patterns = [
    ({"TEXT": {"REGEX": r"\$[\d,]+"}}, {"is_money": True}),
    ({"TEXT": {"REGEX": r"\d+\%"}}, {"is_percent": True}),
    ({"TEXT": {"REGEX": r"\b[A-Z]{2,4}\b"}}, {"is_acronym": True})
]

for pattern, attrs in patterns:
    ruler.add(pattern, attrs)

doc = nlp("The API costs $100 and gives 50% discount. Contact NASA for info.")
for token in doc:
    if hasattr(token._., "is_money") and token._.is_money:
        print(f"Money: {token.text}")
```

## Combining Matchers

You can use multiple matchers together:

```python
import spacy
from spacy.matcher import Matcher, PhraseMatcher

nlp = spacy.load("en_core_web_sm")

# Token-based matcher
token_matcher = Matcher(nlp.vocab)
token_matcher.add("ADJ_NOUN", [[{"POS": "ADJ"}, {"POS": "NOUN"}]])

# Phrase-based matcher  
phrase_matcher = PhraseMatcher(nlp.vocab)
phrases = [nlp("New York"), nlp("Los Angeles")]
phrase_matcher.add("CITY", None, *phrases)

# Process text
doc = nlp("The quick brown fox in New York")

# Run both matchers
token_matches = token_matcher(doc)
phrase_matches = phrase_matcher(doc)

print("Token matches:")
for match_id, start, end in token_matches:
    print(f"  {doc[start:end].text}")

print("Phrase matches:")
for match_id, start, end in phrase_matches:
    print(f"  {doc[start:end].text}")
```

## Performance Tips

1. **Compile patterns efficiently**: Pre-compile patterns for repeated use
2. **Use specific patterns**: More specific patterns are faster
3. **Limit operator usage**: `*` and `+` operators slow down matching
4. **Cache matcher objects**: Reuse matchers across documents
5. **Batch processing**: Process multiple documents together

```python
# Efficient pattern compilation
matcher = Matcher(nlp.vocab)
patterns = [[{"POS": "VERB"}, {"POS": "NOUN"}]]
matcher.add("VERB_NOUN", patterns, performance=True)

# Reuse matcher across documents
for text in texts:
    doc = nlp(text)
    matches = matcher(doc)
```

## Common Patterns Library

### Date and Time Patterns

```python
date_patterns = [
    # "January 15, 2023"
    [{"POS": "PROPN"}, {"TEXT": {"IS_DIGIT": True}}, {"TEXT": ","}, {"TEXT": {"IS_DIGIT": True}}],
    # "2023-01-15"
    [{"TEXT": {"REGEX": r"\d{4}-\d{2}-\d{2}"}}],
    # "today", "yesterday"
    [{"TEXT": {"IN": ["today", "yesterday", "tomorrow"]}}]
]

matcher.add("DATE", date_patterns)
```

### Monetary Patterns

```python
money_patterns = [
    # "$100", "$1,000"
    [{"TEXT": {"REGEX": r"\$[\d,]+"}}],
    # "100 dollars"
    [{"TEXT": {"IS_DIGIT": True}}, {"TEXT": {"IN": ["dollars", "doller", "$"]}}],
    # "€50", "£100"
    [{"TEXT": {"REGEX": r"[€£][\d,]+"}}]
]

matcher.add("MONEY", money_patterns)
```

### Contact Information

```python
contact_patterns = [
    # Email addresses
    [{"TEXT": {"REGEX": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"}}],
    # Phone numbers (US format)
    [{"TEXT": {"REGEX": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"}}],
    # URLs
    [{"TEXT": {"REGEX": r"https?://[^\s]+"}}]
]

matcher.add("CONTACT", contact_patterns)
```

## References

- [Matcher Documentation](https://spacy.io/api/matcher)
- [PhraseMatcher Documentation](https://spacy.io/api/phrasematcher)
- [SpanMatcher Documentation](https://spacy.io/api/spanmatcher)
- [Rule-based Matching Guide](https://spacy.io/usage/rule-based-matching)
- [EntityRuler Documentation](https://spacy.io/api/entityruler)
- [AttributeRuler Documentation](https://spacy.io/api/attributeruler)
