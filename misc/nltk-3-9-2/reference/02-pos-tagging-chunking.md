# POS Tagging & Chunking

## Part-of-Speech Tagging

POS tagging assigns grammatical categories to each token. NLTK uses the Penn Treebank tagset for English and the Russian National Corpus tagset for Russian.

### Default Tagger (PerceptronTagger)

`nltk.pos_tag()` uses `PerceptronTagger` under the hood — an averaged perceptron achieving ~97% accuracy on English:

```python
from nltk import pos_tag, word_tokenize

tagged = pos_tag(word_tokenize("John's big idea isn't all that bad."))
print(tagged)
# [('John', 'NNP'), ("'s", 'POS'), ('big', 'JJ'), ('idea', 'NN'),
#  ('is', 'VBZ'), ("n't", 'RB'), ('all', 'PDT'), ('that', 'DT'),
#  ('bad', 'JJ'), ('.', '.')]
```

### Russian Tagging

```python
tagged = pos_tag(word_tokenize("Илья оторопел и дважды перечитал бумажку."), lang='rus')
# [('Илья', 'S'), ('оторопел', 'V'), ('и', 'CONJ'), ('дважды', 'ADV'), ...]
```

### Sequential Backoff Taggers

Build tagger chains that fall back through increasingly general strategies:

```python
from nltk.tag import DefaultTagger, UnigramTagger, BigramTagger, TrigramTagger
from nltk.corpus import brown

# Training data
train_sents = brown.tagged_sents(categories='news')

# Default tagger — tags everything as most common tag (NN)
default_tagger = DefaultTagger('NN')
print(default_tagger.accuracy(train_sents))  # ~13%

# Unigram tagger — best tag for each word
unigram_tagger = UnigramTagger(train_sents)
print(unigram_tagger.accuracy(train_sents))  # ~80%

# Bigram tagger with unigram backoff
bigram_tagger = BigramTagger(train_sents, backoff=unigram_tagger)
print(bigram_tagger.accuracy(train_sents))   # ~87%

# Trigram tagger with bigram backoff
trigram_tagger = TrigramTagger(train_sents, backoff=bigram_tagger)
# ~89%
```

### AffixTagger

Tags based on word suffixes of a given length:

```python
from nltk.tag import AffixTagger

affix_tagger = AffixTagger(train_sents, affix_length=-3, backoff=default_tagger)
```

### RegexpTagger

Pattern-based tagging using regular expressions:

```python
from nltk.tag import RegexpTagger

patterns = [
    (r'^-?[0-9]+(.[0-9]+)?$', 'CD'),   # cardinal numbers
    (r'(The|the|A|a|An|an)$', 'DT'),    # determiners
    (r'.*able$', 'JJ'),                  # adjectives
    (r'.*ness$', 'NN'),                  # nouns from adjectives
    (r'.*ing$', 'VBG'),                  # present participles
    (r'.*ed$', 'VBD'),                   # simple past
    (r'.*', 'NN'),                       # default to noun
]

regexp_tagger = RegexpTagger(patterns)
```

### BrillTagger

Rule-based transformation tagger. Train with `BrillTaggerTrainer`:

```python
from nltk.tag import BrillTagger, BrillTaggerTrainer
from nltk.tag.brill_trainer import Template0, Template1, Template2, Template3, Template4, Template5

templates = [Template0(), Template1(), Template2(), Template3(), Template4(), Template5()]
trainer = BrillTaggerTrainer(default_tagger, templates, trace=2)
brill_tagger = trainer.train(train_sents)
```

### HMM Tagger

Hidden Markov Model tagger for probabilistic tagging:

```python
from nltk.tag.hmm import HiddenMarkovModelTagger, HiddenMarkovModelTrainer

trainer = HiddenMarkovModelTrainer()
hmm_tagger = trainer.train_supervised(train_sents)
```

### CRF Tagger

Requires `python-crfsuite`:

```python
from nltk.tag.crf import CRFTagger

crf_tagger = CRFTagger()
crf_tagger.train(train_sents, model_file='crf_model.tagger')
tagged = crf_tagger.tag(tokens)
```

### Tag Evaluation

```python
from nltk.tag.util import str2tuple, tuple2str

# Evaluate a tagger against gold standard
accuracy = tagger.accuracy(test_sents)

# Precision, recall, F-measure per tag (NLTK 3.6.6+)
precision = tagger.precision(test_sents)
recall = tagger.recall(test_sents)
f_measure = tagger.f_measure(test_sents)

# Confusion matrix
confusion = tagger.confusion(test_sents)
```

### Tagset Mapping

Convert between tagsets (e.g., Penn Treebank to Universal):

```python
from nltk.tag import map_tag, tagset_mapping

# Map Penn Treebank tags to Universal tagset
universal_tags = [map_tag('en-ptb', 'universal', tag) for word, tag in tagged]
# Available tagsets: 'universal', 'en-ptb', 'en-brown', 'fr-parltree', etc.
```

## Named Entity Recognition

### ne_chunk

Identify persons, organizations, locations, and miscellaneous entities:

```python
from nltk import pos_tag, word_tokenize
from nltk.chunk import ne_chunk

sentence = "Barack Obama was born in Hawaii."
tagged = pos_tag(word_tokenize(sentence))
tree = ne_chunk(tagged)
print(tree)
# Tree('S',
#   [Tree('PERSON', [('Barack', 'NNP'), ('Obama', 'NNP')]),
#    ('was', 'VBD'), ('born', 'VBN'), ('in', 'IN'),
#    Tree('GPE', [('Hawaii', 'NNP')]), ('.', '.')])
```

### ne_chunk_sents

Process multiple sentences:

```python
trees = ne_chunk_sents([pos_tag(word_tokenize(s)) for s in sentences])
```

### Custom NER with Stanford Taggers

Requires Stanford NER jar and model files:

```python
from nltk.tag.stanford import StanfordNERTagger

st = StanfordNERTagger(
    'classifiers/english.all.3class.distsim.crf.ser.gz',
    'stanford-ner.jar'
)
tagged = st.tag('Rami Eid is studying at Stony Brook University in NY'.split())
```

## Chunking

Chunking groups tokens into meaningful chunks (noun phrases, verb phrases, etc.) without full recursive structure.

### RegexpChunkParser

Define chunk grammar with regular expressions:

```python
from nltk.chunk import RegexpChunkParser

grammar = r"""
    NP: {<DT|JJ|NN.*>+}      # Determiners, adjectives, nouns
    VP: {<VB.*><NP|PP|CB>*}  # Verbs followed by phrases
    PP: {<IN><NP>}           # Preposition + noun phrase
"""

chunk_parser = RegexpChunkParser(grammar)
tree = chunk_parser.parse(tagged_tokens)
print(tree.pprint())
```

### Chunk Rules

Build chunkers from individual rules:

```python
from nltk.chunk import ChunkRule, RegexpChunkParser

rules = [
    ChunkRule(r"<NN.*>", "Begin a noun phrase"),
    ChunkRule(r"<JJ>", "Adjectives in NP"),
    ChunkRule(r"<DT>", "Determiners in NP"),
]

chunk_parser = RegexpChunkParser(rules)
```

### Chunk Evaluation

```python
from nltk.chunk.util import ChunkScore, accuracy

# Compare predicted chunks against gold standard
score = ChunkScore()
for gold, test in zip(gold_chunks, test_chunks):
    score.update(gold, test)

print(f"Accuracy: {accuracy(gold_chunks, test_chunks)}")
```

### IOB Tagging Format

Chunks can be represented as IOB (Inside-Outside-Begin) tags:

```python
from nltk.chunk.util import tree2conlltags, conlltags2tree

# Tree to IOB tags
iob_tags = tree2conlltags(chunk_tree)
# [('The', 'NN', 'B-NP'), ('quick', 'JJ', 'I-NP'), ('brown', 'JJ', 'I-NP'), ...]

# IOB tags back to tree
tree = conlltags2tree(iob_tags)
```
