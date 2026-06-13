# Rule-based Matching

## Overview

Compared to using regular expressions on raw text, spaCy's rule-based matchers find words and phrases while giving you access to tokens within the document and their relationships. You can analyze surrounding tokens, merge spans into single tokens, or add entries to `doc.ents`.

### Rules vs. Training

- **Rule-based**: Best for finite lists (country names, IP addresses, URLs) or very clear structured patterns. No training data needed.
- **Statistical models**: Better for generalization from examples (person names, company names). Requires labeled training data.
- **Combined approach**: Use rules to boost a statistical model's accuracy for specific cases.

## Matcher

The `Matcher` operates over tokens, similar to regular expressions. Rules refer to token annotations (text, tag, flags):

```python
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Define pattern: "hello" + punctuation + "world"
pattern = [{"LOWER": "hello"}, {"IS_PUNCT": True}, {"LOWER": "world"}]
matcher.add("HelloWorld", [pattern])

doc = nlp("Hello, world!")
matches = matcher(doc)
for match_id, start, end in matches:
    print(doc[start:end].text)  # "Hello, world"
```

### Adding patterns with callbacks

```python
def on_match(matcher, doc, id, matches):
    for match_id, start, end in matches:
        span = doc[start:end]
        print(f"Match: {span.text}")

matcher.add("Greeting", [pattern], on_match=on_match)
```

### Available Token Pattern Keys

Each dictionary in a pattern represents one token. Supported attributes:

**Text attributes:**
- `ORTH` — Exact verbatim text
- `TEXT` — Exact verbatim text (of the token)
- `NORM` — Normalized form of the text
- `LOWER` — Lowercase form
- `LENGTH` — Length of the text

**Flags (boolean):**
- `IS_ALPHA` — Alphabetic characters
- `IS_ASCII` — ASCII characters
- `IS_DIGIT` — Digits
- `IS_LOWER` — All lowercase
- `IS_UPPER` — All uppercase
- `IS_TITLE` — Titlecase
- `IS_PUNCT` — Punctuation
- `IS_SPACE` — Whitespace
- `IS_STOP` — Stop word
- `IS_SENT_START` — Start of sentence
- `LIKE_NUM` — Resembles a number
- `LIKE_URL` — Resembles a URL
- `LIKE_EMAIL` — Resembles an email
- `SPACY` — Has trailing space

**Linguistic attributes (case-sensitive values):**
- `POS` — Part-of-speech tag
- `TAG` — Fine-grained POS tag
- `MORPH` — Morphological features
- `DEP` — Dependency label
- `LEMMA` — Lemma
- `SHAPE` — Word shape
- `ENT_TYPE` — Entity label

**Custom extension attributes:**
- `_` — Properties in custom extension attributes (Dict[str, Any])

**Operator (`OP`):**
- `"?"` — Match 0 or 1 times
- `"*"` — Match 0 or more times
- `"+"` — Match 1 or more times

```python
# Pattern with operators
pattern = [
    {"POS": "ADJ", "*"},       # Zero or more adjectives
    {"POS": "PROPN", "+"},     # One or more proper nouns
    {"POS": "NOUN", "?"}       # Optional noun
]
matcher.add("NamedEntity", [pattern])
```

### Comparators

Use `>` and `<` for numeric comparisons:

```python
pattern = [{"LENGTH": {">": 10}}]  # Token longer than 10 characters
```

### Set membership (`IN`)

Match against a set of values:

```python
pattern = [{"POS": {"IN": ["NOUN", "PROPN"]}}]
```

### Negation (`NOT_IN`, `!=`)

Exclude specific values:

```python
pattern = [{"POS": "VERB", "LEMMA": {"NOT_IN": ["be", "have"]}}]
```

## PhraseMatcher

The `PhraseMatcher` matches exact phrases from a terminology list or gazetteer. It's faster than `Matcher` for large lists of exact phrases:

```python
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab)

# Create patterns from phrases
phrases = ["New York", "Los Angeles", "San Francisco"]
patterns = [nlp.make_doc(text) for text in phrases]
matcher.add("USCity", patterns)

doc = nlp("I live in New York and visit San Francisco often.")
matches = matcher(doc)
for match_id, start, end in matches:
    print(doc[start:end].text)
```

Case-insensitive matching:

```python
matcher.add("USCity", patterns, attr="LOWER")
```

## DependencyMatcher

The `DependencyMatcher` matches patterns based on dependency tree structure using Semgrex-style operators:

```python
from spacy.matcher import DependencyMatcher

nlp = spacy.load("en_core_web_sm")
matcher = DependencyMatcher(nlp.vocab)

# Find patterns: adjective modifying a noun
pattern = [
    {"LABEL": "ROOT", "DEPS": ["compound", "nsubj"]},
    {"LABEL": "HEAD", "DEPS": ["ROOT"]}
]
matcher.add("AdjNounPattern", [pattern])

doc = nlp("The big cat sat")
matches = matcher(doc)
for match_id, spans in matches:
    for span_key, span in spans.items():
        print(span_key, doc[span].text)
```

**Dependency pattern keys:**

- `HEAD` / `ROOT` — Role in the match (head or root)
- `LABEL` — Custom label for referencing in other patterns
- `DEPS` — Dependency relation to the head
- `MAXDEPS` — Maximum number of dependents
- `KEYS` — Token attributes that must match
- `ON` — Which token attribute to match on

## EntityRuler

The `EntityRuler` adds entity annotations based on patterns. It can be added as a pipeline component:

```python
nlp = spacy.load("en_core_web_sm")
ruler = nlp.add_pipe("entity_ruler", before="ner")

# Add patterns
patterns = [
    {"label": "CITY", "pattern": "New York"},
    {"label": "CITY", "pattern": "Los Angeles"},
    {"label": "COUNTRY", "pattern": [{"LOWER": "united"}, {"IS_PUNCT": True}, {"LOWER": "states"}]},
]
ruler.add_patterns(patterns)

doc = nlp("I live in New York.")
for ent in doc.ents:
    print(ent.text, ent.label_)
```

**Pattern types:**

- **String pattern**: Exact phrase match
- **Token pattern**: List of token attribute dictionaries (like Matcher)
- **Mixed**: Combine both

### Reconcile modes

Control how EntityRuler interacts with existing entities:

```python
ruler = nlp.add_pipe("entity_ruler", config={"ent_type_reconcile": "strict"})
```

- `"strict"` — Only add if no overlap (default)
- `"overwrite"` — Overwrite overlapping entities
- `"allow_overlap"` — Allow overlapping entities
- `"prefer_overlaps"` — Prefer the ruler's entities

## SpanRuler

The `SpanRuler` matches patterns and creates `SpanGroup` collections. More flexible than EntityRuler:

```python
nlp = spacy.load("en_core_web_sm")
ruler = nlp.add_pipe("span_ruler")

patterns = [
    {"label": "CITY", "pattern": "New York"},
    {"label": "CITY", "pattern": [{"LOWER": "los"}, {"LOWER": "angeles"}]},
]
ruler.add_patterns(patterns)

doc = nlp("Visit New York and Los Angeles.")
for group in doc.spans.get("sc_spans", []):
    print(group.label_, group.text)
```

## Performance Tips

- Use `PhraseMatcher` for large exact-match lists (gazetteers, terminology)
- Use `Matcher` for abstract patterns with linguistic features
- Use `DependencyMatcher` for syntactic structure matching
- Use `EntityRuler` when you want entities in `doc.ents`
- Use `SpanRuler` for flexible span collections
- Combine rules and statistical models: use EntityRuler before NER to handle specific cases
- When developing complex patterns, verify against spaCy's tokenization first
