# Linguistic Features

## Part-of-Speech Tagging

After tokenization, spaCy's trained pipeline assigns POS tags to each token. Tags are available as `Token` attributes:

```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
          token.shape_, token.is_alpha, token.is_stop)
```

**Token attributes:**

- `token.text` — Original word text
- `token.lemma_` — Base form of the word
- `token.pos_` — Simple UPOS part-of-speech tag (e.g., "VERB", "NOUN")
- `token.tag_` — Detailed language-specific POS tag (e.g., "VBZ", "NN")
- `token.dep_` — Syntactic dependency relation
- `token.shape_` — Word shape (capitalization, punctuation, digits pattern)
- `token.is_alpha` — Token consists of alphabetic characters
- `token.is_stop` — Token is a common stop word

Use `spacy.explain()` to get descriptions:

```python
print(spacy.explain("VBZ"))   # "verb, 3rd person singular present"
print(spacy.explain("NNP"))   # "noun, proper singular"
```

## Morphology

Inflectional morphology describes how a root form is modified by prefixes/suffixes specifying grammatical function.

```python
doc = nlp("I was reading the paper")
for token in doc:
    if token.morph:
        print(token.text, token.morph)
```

Access individual features:

```python
token.morph.get("Tense")       # ["Past", "Pres"]
token.morph.get("VerbForm", all=True)  # all values
"Tense=Past" in token.morph    # True/False
```

**Statistical Morphologizer** (v3.0+): The `morphologizer` component assigns morphological features and coarse-grained POS tags as `Token.morph` and `Token.pos_`.

**Rule-based morphology**: For simpler languages like English, spaCy assigns morphology through rules using token text and fine-grained POS tags.

## Lemmatization

spaCy assigns the base form (lemma) of each word:

```python
doc = nlp("The rats were running across the street")
for token in doc:
    print(token.text, "→", token.lemma_)
# The → the
# rats → rat
# were → be
# running → run
```

**Rule-based Lemmatizer** (`lemmatizer`): Uses lookup tables from `spacy-lookups-data`. Requires `pip install spacy[lookups]` or `pip install spacy-lookups-data` for training.

**Trainable EditTreeLemmatizer** (`edittreelemmatizer`): Statistical lemmatizer using edit trees. Trainable on custom data.

## Dependency Parsing

spaCy assigns syntactic dependency labels describing the relations between tokens:

```python
doc = nlp("The cat sat on the mat")
for token in doc:
    print(f"{token.text:10} head={token.head.text:5} dep={token.dep_:10} children={[c.text for c in token.children]}")
```

**Key dependency attributes:**

- `token.head` — The governing token (parent in dependency tree)
- `token.dep_` — Dependency relation label
- `token.children` — Direct dependent tokens
- `token.subtree` — All tokens in the subtree
- `token.lefts` / `token.rights` — Left/right children
- `token.is_root` — Whether the token is the root of the sentence

**Noun chunks** (noun phrases):

```python
doc = nlp("The big cat sat on the mat")
for chunk in doc.noun_chunks:
    print(chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text)
```

## Named Entity Recognition

spaCy's NER labels "real-world" objects — persons, companies, locations, products:

```python
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")
for ent in doc.ents:
    print(ent.text, ent.label_, spacy.explain(ent.label_))
```

**Standard English entity labels:**

- `PERSON` — People, including fictional
- `NORP` — Nationalities, religious or political groups
- `FAC` — Buildings, airports, highways, bridges
- `ORG` — Companies, agencies, institutions
- `GPE` — Countries, cities, states
- `LOC` — Non-gpe locations
- `PRODUCT` — Objects, vehicles, foods, etc.
- `EVENT` — Named hurricanes, battles, wars, sports events
- `WORK_OF_ART` — Titles of books, songs, etc.
- `LAW` — Names of documents
- `LANGUAGE` — Any language
- `DATE` — Absolute or relative dates
- `TIME` — Times smaller than a day
- `PERCENT` — Percentage
- `MONEY` — Monetary values
- `QUANTITY` — Measurements, e.g. weight, distance
- `ORDINAL` — "first", "second", etc.
- `CARDINAL` — Numerals that do not fall under another type

**Span attributes for entities:**

```python
ent = doc.ents[0]
print(ent.text)       # Entity text
print(ent.label_)     # Entity label
print(ent.start)      # Start token index
print(ent.end)        # End token index (exclusive)
print(ent.start_char) # Start character offset
print(ent.end_char)   # End character offset
```

Visualize with displaCy:

```python
from spacy import displacy
displacy.serve(doc, style="ent")  # Web server
displacy.render(doc, style="ent")  # HTML/Markdown
```

## Entity Linking

Entity linking disambiguates textual entities to unique identifiers in a knowledge base:

```python
from spacy.pipeline.entitylinker import InMemoryLookupKB

kb = InMemoryLookupKB(nlp.vocab, entity_vector_length=200)
# Add entities and their aliases
kb.add_entity(entity="Q42", vectors=some_vector, prob=1.0)
kb.add_alias("Alan Turing", entities=["Q42"], probs=[1.0])

nlp.add_pipe("entitylinker", config={"ent_cwd": kb})
```

## Sentence Segmentation

spaCy identifies sentence boundaries:

```python
doc = nlp("First sentence. Second sentence? Third one!")
for sent in doc.sents:
    print(sent.text)

# Check if a token starts a sentence
for token in doc:
    if token.is_sent_start:
        print(f"Sentence starts: {token.text}")
```

Sentences are `Span` objects — they support all span operations.

## Tokenization

spaCy's tokenizer is linguistically motivated and handles edge cases:

```python
nlp = spacy.load("en_core_web_sm")
doc = nlp("Hello-world! It's 3:30 PM.")
for token in doc:
    print(token.text, repr(token.whitespace_))
```

**Tokenization attributes:**

- `token.text` — Token text
- `token.idx` — Character index in original text
- `token.whitespace_` — Trailing whitespace
- `token.is_space` — Token is whitespace

**Customizing tokenization:**

```python
# Add special cases (e.g., don't split "don't")
nlp.tokenizer.add_special_case("n't", [{"ORTH": "n"}, {"ORTH": "'"}, {"ORTH": "t"}])

# Replace tokenizer entirely
from spacy.tokenizer import Tokenizer
def custom_tokenizer(nlp):
    return Tokenizer(nlp.vocab)
nlp.tokenizer = custom_tokenizer(nlp)
```

## Merging and Splitting

Merge tokens into a single token:

```python
doc = nlp("New York is a big city")
from spacy.tokens import Span
entity = Span(doc, 0, 2, label="GPE")
with doc.retokenize() as retokenizer:
    retokenizer.merge(entity)
print([t.text for t in doc])  # ["New York", "is", "a", "big", "city"]
```

Split tokens:

```python
with doc.retokenize() as retokenizer:
    retokenizer.split(doc[0], [{"LIKE_NUM": True}, {"ORTH": "-"}, {"LIKE_NUM": True}])
```

## Vectors and Similarity

Word vectors represent word meanings as multi-dimensional vectors. spaCy's large models include pretrained vectors:

```python
nlp = spacy.load("en_core_web_lg")  # includes vectors

# Token similarity
doc = nlp("dog cat banana")
print(doc[0].similarity(doc[1]))  # dog vs cat (high)
print(doc[0].similarity(doc[2]))  # doc[0] vs banana (low)

# Span/Doc similarity
doc1 = nlp("I love cats")
doc2 = nlp("I adore felines")
print(doc1.similarity(doc2))

# Vector operations
print(nlp.vocab["dog"].vector.shape)  # (300,)
```

**Note:** Similarity requires a model with word vectors (`_lg` or `_trf`). The small models (`_sm`) do not include vectors.

## Language Data

spaCy supports 75+ languages for tokenization and 25+ with trained pipelines:

**Languages with trained pipelines:**

- English (en), French (fr), German (de), Spanish (es), Portuguese (pt)
- Italian (it), Dutch (nl), Polish (pl), Russian (ru)
- Chinese (zh), Japanese (ja), Korean (ko)
- Danish (da), Finnish (fi), Norwegian (nb), Swedish (sv)
- Catalan (ca), Greek (el), Croatian (hr), Macedonian (mk)
- Lithuanian (lt), Slovenian (sl), Ukrainian (uk), Romanian (ro)

**Languages with tokenization only** (use `spacy.blank("xx")` or import language class directly):

Afrikaans, Albanian, Amharic, Ancient Greek, Arabic, Armenian, Azerbaijani, Basque, Bengali, Bulgarian, Czech, Estonian, Faroese, Gujarati, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Irish, Kannada, Kyrgyz, Latin, Latvian, Ligurian, Lower Sorbian, Luganda, Luxembourgish, Malay, Malayalam, Marathi, Nepali, Norwegian Nynorsk, Persian, Sanskrit, Serbian, Setswana, Sinhala, Slovak, Tagalog, Tamil, Tatar, Telugu, Thai, Tigrinya, Turkish, Upper Sorbian, Urdu, Vietnamese, Yoruba.

**Multi-language pipelines** use language code `xx`:

```python
nlp = spacy.blank("xx")
# or
from spacy.lang.xx import MultiLanguage
nlp = MultiLanguage()
```

**Language-specific dependencies:**

- Japanese: SudachiPy
- Korean: mecab-ko, mecab-ko-dic, natto-py
- Thai: pythainlp
- Vietnamese: Pyvi
- Chinese: Jieba, spacy-pkuseg (optional segmenters)

**Chinese segmentation options:**

```python
# Character segmentation (default)
nlp = spacy.blank("zh")

# Jieba
config = {"segmenter": "jieba"}
nlp = spacy.blank("zh", config=config)

# PKUSeg
config = {"segmenter": "pkuseg"}
nlp = spacy.blank("zh", config=config)
```
