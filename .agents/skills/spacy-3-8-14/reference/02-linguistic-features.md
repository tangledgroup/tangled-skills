# Linguistic Features and Annotations

This guide covers spaCy's core linguistic features: tokenization, POS tagging, dependency parsing, NER, lemmatization, and morphological analysis.

## Tokenization

Tokenization splits text into words, punctuation, and other meaningful units.

### Basic Tokenization

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Hello, world! This is a test.")

# Iterate over tokens
for token in doc:
    print(token.text)

# Access by index
print(doc[0].text)   # "Hello"
print(doc[1].text)   # ","
print(doc[2].text)   # "world"

# Token span
print(doc[0:3].text)  # "Hello, world"
```

### Token Properties

Each token has rich linguistic information:

```python
token = doc[0]  # "Hello"

print(token.text)      # "Hello" - the actual text
print(token.idx)       # 0 - start position in original text
print(token.i)         # 0 - index in the Doc
print(token.is_alpha)  # True - alphabetic characters
print(token.is_upper)  # True - all uppercase
print(token.is_punct)  # False - punctuation
print(token.like_num)  # False - looks like a number
print(token.is_space)  # False - whitespace
```

### Special Tokens

spaCy handles special cases intelligently:

```python
doc = nlp("U.S.A. has 300M people. Dr. Smith works at St. Mary's.")

for token in doc:
    print(token.text, token.is_alpha)

# Output shows how contractions and abbreviations are handled
# "U.S.A." may be one or multiple tokens depending on the model
```

### Custom Tokenization

You can customize tokenization rules:

```python
import spacy
from spacy.tokenizer import Tokenizer
from spacy.util import get_lang_class

# Load language class
Lang = get_lang_class("en")
nlp = Lang()

# Add custom tokenization rule
prefixes = nlp.Defaults.prefixes
suffixes = nlp.Defaults.suffixes
infixes = nlp.Defaults.infixes

# Add a custom suffix (e.g., for hashtags)
suffixes |= {(r"#\w+", spacy.tokens.Token.set_flag("hashtag"))}

# Create tokenizer with custom rules
tokenizer = Tokenizer(nlp.vocab, prefixes=prefixes, suffixes=suffixes, infixes=infixes)
nlp.tokenizer = tokenizer

doc = nlp("Check out #spacy for NLP")
for token in doc:
    print(token.text, hasattr(token._., "hashtag"))
```

## Part-of-Speech Tagging

POS tagging assigns grammatical categories to each token.

### Universal POS Tags

spaCy uses universal POS tags for cross-linguistic consistency:

```python
doc = nlp("The quick brown fox jumps over the lazy dog.")

for token in doc:
    print(token.text, token.pos_)

# Output:
# The DET (determiner)
# quick ADJ (adjective)
# brown ADJ
# fox NOUN
# jumps VERB
# over ADP (adposition/preposition)
# the DET
# lazy ADJ
# dog NOUN
# . PUNCT
```

### Detailed POS Tags

For more granular tags, use `token.tag_`:

```python
for token in doc:
    print(token.text, token.pos_, token.tag_)

# Output includes detailed tags like:
# The DET DT (determiner, indefinite)
# jumps VERB VBZ (verb, 3rd person singular present)
# dog NOUN NN (noun, singular)
```

### POS Tag Set

Common universal POS tags:

| Tag | Description | Examples |
|-----|-------------|----------|
| NOUN | noun | dog, cat, London |
| VERB | verb | run, is, have |
| ADJ | adjective | quick, brown, lazy |
| ADV | adverb | quickly, very, not |
| DET | determiner | the, a, this |
| PRON | pronoun | I, you, he |
| PROPN | proper noun | John, London, Apple |
| ADP | adposition | in, on, at |
| NUM | numeral | one, 123, first |
| PUNCT | punctuation | . , ! ? |
| CONJ | conjunction | and, or, but |
| PART | particle | to, not |
| INTJ | interjection | wow, ouch |

## Dependency Parsing

Dependency parsing identifies grammatical relationships between words.

### Basic Dependency Analysis

```python
doc = nlp("The quick brown fox jumps over the lazy dog.")

for token in doc:
    print(token.text, token.dep_, token.head.text)

# Output shows:
# The DET det -> fox (determiner of fox)
# quick AMOD amod -> fox (adjectival modifier of fox)
# brown AMOD amod -> fox
# fox NROOT nroot -> fox (root of sentence)
# jumps VERB nsubj -> fox (noun subject of fox)
# over ADP case -> jumps
# the DET det -> dog
# lazy AMOD amod -> dog
# dog NOUN obl -> jumps (oblique argument)
# . PUNCT punct -> jumps
```

### Dependency Tree Traversal

```python
# Access the root of the sentence
root = doc.root
print(root.text)  # "fox" or "jumps" depending on model

# Traverse children
for child in root.children:
    print(child.text, child.dep_)

# Access head (governor)
token = doc[4]  # "jumps"
print(token.head.text)  # The word it depends on

# Access all descendants
def get_all_descendants(token):
    yield token
    for child in token.children:
        yield from get_all_descendants(child)

for t in get_all_descendants(doc.root):
    print(t.text)
```

### Common Dependency Labels

| Label | Description | Example |
|-------|-------------|---------|
| nsubj | nominal subject | The [cat](nsubj) sleeps |
| obj | object | I see the [cat](obj) |
| nmod | nominal modifier | cat [of](nmod) the dog |
| amod | adjectival modifier | [quick](amod) fox |
| advmod | adverbial modifier | runs [quickly](advmod) |
| det | determiner | [the](det) cat |
| case | case marking | cat [of](case) the dog |
| obl | oblique argument | jumps [over](obl) the dog |
| root | root of sentence | The fox [jumps](root) |
| punct | punctuation | Hello[!](punct) |

### Finding Specific Dependencies

```python
# Find all nouns that are subjects
for token in doc:
    if token.dep_ == "nsubj":
        print(token.head.text, "is done by", token.text)

# Find all objects
for token in doc:
    if token.dep_ == "obj":
        print(token.head.text, "acts on", token.text)

# Find modifiers
for token in doc:
    if token.dep_ == "amod":
        print(token.text, "describes", token.head.text)
```

## Named Entity Recognition (NER)

NER identifies and classifies named entities in text.

### Basic NER

```python
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

for ent in doc.ents:
    print(ent.text, ent.label_, ent.start_char, ent.end_char)

# Output:
# Apple ORG 0 5
# U.K. GPE 30 34
# $1 billion MONEY 48 58
```

### Entity Labels

Common entity types:

| Label | Description | Examples |
|-------|-------------|----------|
| PERSON | people | John Smith, Dr. Jones |
| ORGANIZATION | companies, agencies | Apple, NASA, UN |
| GPE | countries, cities, states | France, London, Texas |
| LOC | locations (non-political) | Himalayas, Pacific Ocean |
| PRODUCT | products | iPhone, Windows |
| EVENT | named events | World Cup, Olympics |
| WORK_OF_ART | titles | Hamlet, Mona Lisa |
| LAW | laws, acts | Patriot Act |
| NORP | nationalities, religions | Buddhist, American |
| FAC | buildings, airports | Empire State Building |
| DATE | absolute dates | today, 1999-12-31 |
| TIME | relative times | 5:00 PM, in an hour |
| PERCENT | percentages | 50%, one percent |
| MONEY | monetary values | $1 billion, £10 |
| QUANTITY | measurements | 5 kg, 10 miles |
| ORDINAL | ordinal numbers | first, second |
| CARDINAL | cardinal numbers | one, hundred |

### Entity Span Properties

```python
ent = doc.ents[0]  # First entity

print(ent.text)        # "Apple"
print(ent.label_)      # "ORG"
print(ent.start)       # Starting token index
print(ent.end)         # Ending token index (exclusive)
print(ent.start_char)  # Start character position
print(ent.end_char)    # End character position
print(ent.vocab)       # Vocab object

# Access tokens in entity
for token in ent:
    print(token.text)
```

### Entity Confidence and Scores

For transformer-based models, you can access confidence scores:

```python
# For some models, check for scores
if hasattr(ent, "confidence"):
    print(ent.confidence)

# Access the underlying span
print(ent.is_o)  # True if not an entity
```

## Lemmatization

Lemmatization reduces words to their base/dictionary form.

### Basic Lemmatization

```python
doc = nlp("running ran run better best mice cats")

for token in doc:
    print(token.text, "→", token.lemma_)

# Output:
# running → run
# ran → run
# run → run
# better → good
# best → good
# mice → mouse
# cats → cat
```

### Lemmatization by POS

Lemmatization considers POS context:

```python
doc = nlp("I like running and the running water")

for token in doc:
    if token.text == "running":
        print(token.text, token.pos_, token.lemma_)

# First "running" (VERB) → run
# Second "running" (NOUN/ADJ) → running
```

### Custom Lemmatization

You can add custom lemmatization rules:

```python
from spacy.pipeline import EntityRuler

nlp = spacy.load("en_core_web_sm")

# Add custom lemma via attribute ruler
attr_ruler = nlp.get_pipe("attribute_ruler")
attr_ruler.add({
    "TEXT": {"REGEX": r"\bAPI\b"}
}, {"lemma_": "api"})

doc = nlp("Call the API for data")
for token in doc:
    if token.text == "API":
        print(token.lemma_)  # "api"
```

## Morphological Analysis

Morphology provides detailed grammatical features for each token.

### Accessing Morphological Features

```python
doc = nlp("I am running faster than you were running yesterday")

for token in doc:
    if token.morph:
        print(token.text, token.morph)

# Output includes features like:
# am AUX VerbType=aux|Mood=ind|Number=sing|Person=1|Tense=pres|VerbForm=fin
# running VERB Tense=prt|VerbForm=part
```

### Parsing Morph Features

```python
token = doc[2]  # "running"

# Get feature dict
morph = token.morph
print(morph.get("VerbForm"))  # "part"
print(morph.get("Tense"))     # "prt"
print(morph.has("Tense"))     # True
print(mooth.to_dict())        # {'Tense': 'prt', 'VerbForm': 'part'}

# Check specific features
if morph.has("Number"):
    print(morph.get("Number"))  # "sing", "plur", etc.
```

### Common Morphological Features

| Feature | Values | Description |
|---------|--------|-------------|
| Case | Nom, Acc, Gen, Dat | Grammatical case |
| Degree | Pos, Comp, Sup | Adjective/adverb degree |
| Gender | M, F, N, Neut | Grammatical gender |
| Number | Sing, Plur | Singular/plural |
| Person | 1, 2, 3 | Grammatical person |
| Tense | Past, Pres | Past/present |
| VerbForm | Fin, Inf, Part, Ger | Finite/infinitive/participle |
| VerbType | Aux, Cop, Main | Auxiliary/copula/main verb |
| Mood | Ind, Sub, Imp | Indicative/subjunctive/imperative |
| Aspect | Perf, Prog | Perfect/progressive |
| Voice | Act, Pass | Active/passive |
| Polarity | Neg | Negative |

## Sentence Segmentation

spaCy provides two sentence segmentation approaches:

### Rule-based Sentencizer (Fast)

```python
nlp = spacy.load("en_core_web_sm")  # Uses sentencizer by default

doc = nlp("Hello. How are you? I'm fine!")

for sent in doc.sents:
    print(sent)

# Output:
# Hello.
# How are you?
# I'm fine!
```

### Neural Senter (More Accurate)

```python
# Load model with senter or add it
nlp = spacy.load("en_core_web_md")  # Includes senter

# Or add to blank model
nlp = spacy.blank("en")
nlp.add_pipe("senter")

doc = nlp("Dr. Smith works at St. Mary's Hospital. He arrived at 5pm.")
for sent in doc.sents:
    print(sent)
```

### Manual Sentence Segmentation

```python
from spacy.tokens import Doc

# Create doc without sentence segmentation
nlp = spacy.load("en_core_web_sm", exclude=["senter"])
doc = nlp("Hello. World.")

# Manually set sentence boundaries
doc.sentences  # This will use rule-based sentencizer

# Or create custom boundaries
sent_starts = [0, 2]  # Tokens at indices 0 and 2 start sentences
Doc.set_sent_bounds(doc, sent_starts)
```

## Combining Features

### Comprehensive Text Analysis

```python
doc = nlp("The quick brown fox jumps over the lazy dog in London.")

for token in doc:
    analysis = {
        "text": token.text,
        "pos": token.pos_,
        "tag": token.tag_,
        "dep": token.dep_,
        "lemma": token.lemma_,
        "morph": token.morph.to_dict() if token.morph else {},
        "ent_type": token.ent_type_ if token.ent_iob != 0 else None,
        "is_root": token.head.i == token.i
    }
    print(analysis)
```

### Feature Extraction Pipeline

```python
def extract_features(doc):
    """Extract all linguistic features from a document"""
    features = {
        "tokens": [],
        "sentences": [],
        "entities": [],
        "noun_phrases": []
    }
    
    # Token features
    for token in doc:
        features["tokens"].append({
            "text": token.text,
            "pos": token.pos_,
            "lemma": token.lemma_
        })
    
    # Sentence features
    for sent in doc.sents:
        features["sentences"].append({
            "text": sent.text,
            "length": len(sent)
        })
    
    # Entity features
    for ent in doc.ents:
        features["entities"].append({
            "text": ent.text,
            "label": ent.label_
        })
    
    # Noun phrases (nouns and their modifiers)
    for token in doc:
        if token.dep_ in ("nsubj", "dobj", "nmod"):
            np = list(token.subtree)
            features["noun_phrases"].append(" ".join(t.text for t in np))
    
    return features

doc = nlp("John Smith works at Google in Mountain View, California.")
features = extract_features(doc)
print(features)
```

## Performance Considerations

1. **Tokenization**: Fastest operation, always executed
2. **POS Tagging**: Required for parser and lemmatizer
3. **Dependency Parsing**: More expensive, skip if not needed
4. **NER**: Moderate cost, useful for entity extraction
5. **Lemmatization**: Can use rules or neural model

Load only needed components:
```python
# Fast pipeline with just tokenization and POS
nlp = spacy.load("en_core_web_sm", exclude=["parser", "lemmatizer"])
```

## References

- [Linguistic Features Documentation](https://spacy.io/usage/linguistic-features)
- [Dependency Parsing Guide](https://spacy.io/usage/#dependency-parsing)
- [Named Entity Recognition](https://spacy.io/usage/#ner)
- [Token Properties](https://spacy.io/api/token)
- [Morphology Features](https://spacy.io/api/morphobj)
