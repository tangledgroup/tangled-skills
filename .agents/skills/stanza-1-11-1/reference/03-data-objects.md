# Data Objects and Annotations

## Object Hierarchy

Stanza represents annotated text through a hierarchical object structure:

```
Document
  └── Sentence (list)
        ├── Token (list)
        │     └── Word (list, usually 1 per token)
        └── Span (list, for entities)
```

## Document

The top-level container for an entire annotated document.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `text` | str | Raw input text |
| `sentences` | List[Sentence] | List of segmented sentences |
| `entities` or `ents` | List[Span] | Named entities found in document |
| `num_tokens` | int | Total token count |
| `num_words` | int | Total word count |

### Methods

```python
doc = nlp("Barack Obama was born in Hawaii.")

# Iterate over all words
for word in doc.iter_words():
    print(word.text, word.upos)

# Iterate over all tokens
for token in doc.iter_tokens():
    print(token.text)

# Convert to dictionary (list of lists, one per sentence)
doc_dict = doc.to_dict()
# [[{'id': 1, 'text': 'Barack', ...}, {'id': 2, 'text': 'Obama', ...}], ...]

# Serialize to bytes (for storage/transmission)
serialized = doc.to_serialized()
# Later: doc2 = stanza.models.common.doc.Document.from_serialized(serialized)
```

### Example Usage

```python
import stanza

nlp = stanza.Pipeline('en')
doc = nlp("Barack Obama was born in Hawaii. He was elected president in 2008.")

print(f"Document text: {doc.text}")
print(f"Number of sentences: {len(doc.sentences)}")
print(f"Total tokens: {doc.num_tokens}")
print(f"Total words: {doc.num_words}")
print(f"Named entities: {doc.entities}")
# [Span(text='Barack Obama', type='PERSON'), 
#  Span(text='Hawaii', type='GPE'),
#  Span(text='2008', type='DATE')]
```

## Sentence

Represents a single segmented sentence with all its annotations.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `doc` | Document | Back-pointer to parent document |
| `text` | str | Raw text of this sentence |
| `dependencies` | List[(Word, str, Word)] | Dependency relations (head, relation, dependent) |
| `tokens` | List[Token] | Tokens in sentence |
| `words` | List[Word] | Words in sentence (after MWT expansion) |
| `entities` or `ents` | List[Span] | Entities in this sentence |
| `sentiment` | str | Sentiment score ('0'='negative', '1'='neutral', '2'='positive') |
| `constituency` | ParseTree | Constituency parse tree (if constituency processor used) |
| `sent_id` | str | Sentence ID (from document index or CoNLL file) |

### Methods

```python
sentence = doc.sentences[0]

# Print dependency relations
sentence.print_dependencies()
# Output:
# ('Barack', '4', 'nsubj:pass')
# ('Obama', '1', 'flat')
# ...

# Print tokens only
sentence.print_tokens()

# Print words only
sentence.print_words()

# Get tokens as string
tokens_str = sentence.tokens_string

# Get words as string
words_str = sentence.words_string

# Convert to dictionary
sent_dict = sentence.to_dict()
```

### Example: Accessing Dependencies

```python
for sent in doc.sentences:
    print(f"Sentence: {sent.text}")
    for head_word, deprel, dep_word in sent.dependencies:
        print(f"  {dep_word.text} --{deprel}--> {head_word.text}")
```

## Token

Represents a surface-form token (may expand to multiple Words via MWT).

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | Tuple[int] | 1-based index in sentence. Range for MWTs (e.g., `(3, 4)`), single for normal tokens `(3,)` |
| `text` | str | Token text as it appears in input |
| `misc` | str | Miscellaneous annotations (internal use) |
| `words` | List[Word] | Underlying syntactic words (1+ for MWTs) |
| `start_char` | int | Start character offset in document |
| `end_char` | int | End character offset in document |
| `ner` | str | NER tag in BIOES format (e.g., 'B-PERSON') |
| `spaces_after` | str | Space(s) following token |
| `spaces_before` | str | Space(s) before token |

### Methods

```python
token = sentence.tokens[0]

# Convert to dictionary
token_dict = token.to_dict()

# Pretty print with MWT expansion
print(token.pretty_print)
# Output: "au -> à le" (for French MWT)
```

### Example: Multi-Word Tokens

```python
# French example with MWT
nlp_fr = stanza.Pipeline('fr')
doc_fr = nlp_fr("Je vais au marché.")

for token in doc_fr.sentences[0].tokens:
    if len(token.words) > 1:  # MWT detected
        print(f"MWT: {token.text} -> {' '.join(w.text for w in token.words)}")
        # Output: MWT: au -> à le
```

## Word

Represents a syntactic word with all annotations.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | int | 1-based index in sentence (0 is artificial root) |
| `text` | str | Word text |
| `lemma` | str | Lemma/base form |
| `upos` or `pos` | str | Universal POS tag (e.g., 'NOUN', 'VERB') |
| `xpos` | str | Treebank-specific POS tag (e.g., 'NNP', 'VBZ') |
| `feats` | str | Morphological features (e.g., 'Gender=Fem\|Person=3') |
| `head` | int | ID of syntactic head (0 for root) |
| `deprel` | str | Dependency relation to head (e.g., 'nmod', 'nsubj') |
| `deps` | str | Combined head and deprel string |
| `misc` | str | Miscellaneous annotations |
| `parent` | Token | Back-pointer to parent token |

### Methods

```python
word = sentence.words[0]

# Convert to dictionary
word_dict = word.to_dict()

# Pretty print all annotations
print(word.pretty_print)
# Output: "Barack NNP B-PERSON 4 nsubj:pass Barack"
```

### Example: Extracting All Annotations

```python
for sent in doc.sentences:
    for word in sent.words:
        print(f"{word.id:3d} {word.text:15s} {word.upos:8s} {word.lemma:10s} "
              f"{word.head:3d} {word.deprel:12s} {word.xpos}")
# Output format similar to CoNLL-U:
#   1 Barack          NOUN       Barack       4 nsubj:pass   NNP
#   2 Obama           NOUN       Obama        1 flat         NNP
```

## Span

Represents a contiguous span of text (primarily for named entities).

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `doc` | Document | Back-pointer to parent document |
| `text` | str | Text of the span |
| `tokens` | List[Token] | Tokens in the span |
| `words` | List[Word] | Words in the span |
| `type` | str | Entity type (e.g., 'PERSON', 'ORG', 'GPE') |
| `start_char` | int | Start character offset |
| `end_char` | int | End character offset |

### Methods

```python
entity = doc.entities[0]

# Convert to dictionary
entity_dict = entity.to_dict()

# Pretty print
print(entity.pretty_print)
# Output: "Barack Obama PERSON"
```

### Example: Entity Extraction

```python
for entity in doc.entities:
    print(f"{entity.type}: {entity.text} (chars {entity.start_char}-{entity.end_char})")
# Output:
# PERSON: Barack Obama (chars 0-13)
# GPE: Hawaii (chars 24-30)
# DATE: 2008 (chars 57-61)

# Filter by entity type
persons = [e for e in doc.entities if e.type == 'PERSON']
organizations = [e for e in doc.entities if e.type == 'ORG']
```

## ParseTree

Represents constituency parse trees (from constituency parser).

### Structure

```python
ParseTree
  ├── label: str          # Bracket type or POS tag or word text
  └── children: List[ParseTree]  # Nested children (empty for leaves)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `label` | str | Node label (bracket type, POS tag, or word text) |
| `children` | List[ParseTree] | Child nodes (preterminals have 1 child, leaves have none) |

### Example: Constituency Parsing

```python
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos,constituency')
doc = nlp("The cat sat on the mat.")

sentence = doc.sentences[0]
parse_tree = sentence.constituency

# Print tree structure (recursive)
def print_tree(node, indent=0):
    print("  " * indent + node.label)
    for child in node.children:
        print_tree(child, indent + 1)

print_tree(parse_tree)
# Output:
# ROOT
#   SENTENCE
#     NP
#       DET The
#       NOUN cat
#     VP
#       VERB sat
#       PP
#         IN on
#         NP
#           DET the
#           NOUN mat
```

## Adding Custom Properties

Extend Stanza data objects with custom annotations:

```python
from stanza.models.common.doc import Document, Sentence, Word

# Add property to Document class
Document.add_property(
    'char_count',
    default=0,
    getter=lambda self: len(self.text),
    setter=None  # Read-only by default
)

# Now accessible on all Document instances
doc = nlp("Hello world")
print(doc.char_count)  # 11

# Add property with setter
Word.add_property(
    'is_capitalized',
    default=False,
    getter=lambda self: self.text[0].isupper() if self.text else False,
    setter=lambda self, value: None  # Computed, not settable
)

for sent in doc.sentences:
    for word in sent.words:
        print(word.text, word.is_capitalized)
```

## Serialization and Deserialization

### Document Serialization

```python
# Serialize entire document
serialized = doc.to_serialized()

# Save to file
with open('doc.pkl', 'wb') as f:
    f.write(serialized)

# Load from file
with open('doc.pkl', 'rb') as f:
    serialized = f.read()
doc_loaded = stanza.models.common.doc.Document.from_serialized(serialized)
```

### Dictionary Conversion

```python
# Document to dict (list of sentences, each list of tokens)
doc_dict = doc.to_dict()

# Sentence to dict (list of tokens)
sent_dict = sentence.to_dict()

# Token to dict (list of words under this token)
token_dict = token.to_dict()

# Word to dict (single word with all annotations)
word_dict = word.to_dict()

# Entity to dict
entity_dict = entity.to_dict()
```

## Character Offset Mapping

Map annotations back to original text:

```python
doc = nlp("Hello, world!")

for sent in doc.sentences:
    for token in sent.tokens:
        # Extract exact substring from original text
        substring = doc.text[token.start_char:token.end_char]
        print(f"Token '{token.text}' at {token.start_char}-{token.end_char}: '{substring}'")

# For entities
for entity in doc.entities:
    entity_text = doc.text[entity.start_char:entity.end_char]
    print(f"{entity.type}: '{entity_text}'")
```

## CoNLL-U Format Integration

Stanza objects can be converted to/from CoNLL-U format:

```python
from stanza.io import ConllUFile, ConllUDocument

# Read from CoNLL-U file
with ConllUFile('data.conllu') as f:
    for doc in f:
        print(doc)

# Write to CoNLL-U format
doc = nlp("Hello world")
with open('output.conllu', 'w') as f:
    # Manual conversion using word properties
    for sent in doc.sentences:
        for word in sent.words:
            print(f"{word.id}\t{word.text}\t{word.text}\t{word.upos}\t"
                  f"{word.xpos or '_'}\t{word.feats or '_'}\t"
                  f"{word.head}\t{word.deprel}\t{word.misc or '_'}\t_", file=f)
        print(file=f)  # Blank line between sentences
```
