# WordNet & Semantics

## WordNet Basics

WordNet is a large lexical database for English. Words are grouped into sets of synonyms called synsets, with relations between synsets.

```python
from nltk.corpus import wordnet as wn
```

### Synsets

A synset represents a distinct concept:

```python
# Find synsets for a word
synsets = wn.synsets('program')
print(len(synsets))  # 9 different senses

# Access a specific synset
synset = wn.synset('program.n.01')
print(synset.name())        # 'program.n.01'
print(synset.definition())  # 'a written plan for doing something'
print(synset.examples())    # ['he wrote his senior thesis on the battle of Gettysburg']

# Synset lemmas
for lemma in synset.lemmas():
    print(lemma.name())  # 'program', 'programme', ...

# Part of speech
print(synset.pos())  # 'n' (noun), 'v' (verb), 'a' (adjective), 'r' (adverb)
```

### Specifying Senses

```python
# By index
synset = wn.synsets('program')[3]

# By POS
synsets = wn.synsets('program', pos=wn.VERB)

# By synset name
synset = wn.synset('run.v.01')
```

### Synonym and Antonym Lookup

```python
# Get synonyms
synonyms = set()
for syn in wn.synsets('car'):
    for lemma in syn.lemmas():
        synonyms.add(lemma.name())
print(synonyms)  # {'car', 'auto', 'automobile', 'machine', 'motorcar'}

# Get antonyms
for lemma in wn.synset('hot.a.01').lemmas():
    for ant in lemma.antonyms():
        print(ant.name())  # 'cold'
```

## Lexical Relations

### Hypernyms and Hyponyms (Is-A Hierarchy)

```python
dog = wn.synset('dog.n.01')

# Hypernyms (parent concepts — broader)
print(dog.hypernyms())
# [Synset('canine.n.02'), Synset('domestic_animal.n.01')]

# Hyponyms (child concepts — narrower)
cat = wn.synset('feline.n.02')
print(cat.hyponyms())
# [Synset('house_cat.n.01'), Synset('tiger.n.01'), ...]

# Root hypernyms (top of hierarchy)
print(dog.root_hypernyms())
# [Synset('entity.n.01')]

# Traverse up the hierarchy
for syn in dog.hypernym_closure():
    print(syn.name())
```

### Meronyms and Holonyms (Part-Whole)

```python
# Part meronyms — parts of something
body = wn.synset('body.n.02')
print(body.part_meronyms())  # ['arm', 'leg', 'torso', ...]

# Member meronyms — members of a collection
pack = wn.synset('pack.n.06')
print(pack.member_holonyms())  # groups that wolves form

# Component holonyms — whole that contains something
wheel = wn.synset('wheel.n.01')
print(wheel.component_holonyms())  # vehicles with wheels
```

### Other Relations

```python
# Entailments (verb sequences)
print(wn.synset('blink.v.01').entailments())

# Similar to synonym but for adjectives
print(wn.synset('similar.a.01').similar_tos())

# Derivationally related forms
print(wn.synset('analyze.v.01').lemmas()[0].derivationals())
# ['analysis', 'analyst', 'analytic', 'analytical']
```

## Semantic Similarity

### Path Similarity

Based on the shortest path in the hypernym graph:

```python
synset1 = wn.synset('dog.n.01')
synset2 = wn.synset('cat.n.01')
print(synset1.path_similarity(synset2))  # value between 0 and 1
```

### Least Common Subsumer (LCS)

Find the most specific shared hypernym:

```python
lcs = synset1.lowest_common_hypernyms(synset2)
print(lcs)  # [Synset('feline.n.02') or similar]
```

### Other Similarity Metrics

```python
# Wu-Palmer similarity (path + depth)
print(synset1.wup_similarity(synset2))

# Resnik similarity (information content of LCS)
print(synset1.res_similarity(synset2))

# Jiang-Conrath distance
print(synset1.jcn_similarity(synset2))

# Lin similarity
print(synset1.lin_similarity(synset2))

# Leacock-Chodorow similarity
print(synset1.lch_similarity(synset2))
```

Information content requires downloading wordnet_ic:

```python
nltk.download('wordnet')
nltk.download('wordnet.ic')
# or for newer data
nltk.download('omw-1.4')
```

## WordNet Information Content

Compute information content from corpus data:

```python
from nltk.corpus import wordnet as wn

ic = wn.ic('ic-brown.dat', verbose=True, simplify=True)
synset = wn.synset('dog.n.01')
print(synset.info_content(ic))
```

## Lemmas

```python
lemma = wn.synset('read.v.01').lemmas()[0]
print(lemma.name())           # 'read'
print(lemma.synset())         # Synset('read.v.01')
print(lemma.frame_count())    # number of usage frames
print(lemma.definition())     # lemma-specific definition
print(lemma.examples())       # example sentences
```

## Semantic Logic

### Feature Structures

```python
from nltk.featstruct import FeatStruct, fsrepr

fs = FeatStruct({'POS': 'N', 'NUM': 'sg', 'GEND': 'fem'})
print(fs['POS'])  # 'N'
```

### First-Order Logic

```python
from nltk.logic import Expression, Variable, Function, Constant

# Create logical expressions
x = Variable('x')
human = Constant('human')
socrates = Constant('socrates')

expr = Function(human, [socrates])
print(expr)  # human(socrates)
```

### Resolution Prover

Automated theorem proving using resolution:

```python
from nltk.inference import ResolutionProver

prover = ResolutionProver()

# Knowledge base
kb = [
    'man(Socrates)',
    'forall x: man(x) -> mortal(x)',
]

# Query (prove Socrates is mortal)
result = prover.prove(kb, 'mortal(Socrates)')
print(result)  # True/False with proof trace
```

### Tableau Prover

Tableau-based theorem proving:

```python
from nltk.inference import TableauProver

prover = TableauProver()
result = prover.prove(kb, 'mortal(Socrates)')
```

### Discourse Representation Theory (DRT)

Semantic representation for discourse:

```python
from nltk.sem import DRS, DrtParser

# Parse DRT expressions
drs_str = '[x: man(x), walks(x)]'
drs = DrtParser().parse(drs_str)
print(drs.fol())  # Convert to first-order logic
```

### Boxer Semantic Interpreter

Interface to the Boxer DRS generator:

```python
from nltk.sem.boxer import Boxer

boxer = Boxer()
boxer.set_bin_dir('/path/to/boxer/bin')
drs = boxer.interpret('Every man walks')
print(drs)
```

## Text Analysis

### Text Class

The `Text` class provides interactive text exploration:

```python
from nltk.text import Text
from nltk.corpus import gutenberg

moby = Text(gutenberg.words('melville-moby_dick.txt'))

# Concordance search
moby.concordance('whale', width=80, lines=10)

# Distribution plot (requires matplotlib)
moby.dispersion_plot(['whale', 'ship', 'sailor'])

# Collocations
moby.collocations(num=20, window_size=2)

# Similar words
moby.similar('whale')

# Common contexts
moby.common_contexts(['whale', 'ship'])
```

### ConcordanceIndex and ContextIndex

```python
from nltk.text import ConcordanceIndex, ContextIndex

tokens = word_tokenize(text)
index = ConcordanceIndex(tokens, key=lambda s: s.lower())
index.print_concordance('word', width=80, lines=25)
```
