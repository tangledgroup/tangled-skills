# NLTK Parsing and Grammars - Complete Guide

## Overview

Parsing is the process of analyzing sentence structure according to a formal grammar. NLTK supports context-free grammars (CFGs), feature grammars, and various parsing algorithms.

## Context-Free Grammars (CFGs)

### Basic Grammar Definition

Define a simple CFG:

```python
from nltk import CFG

# Define grammar in string format
grammar_str = """
    S   -> NP VP
    NP  -> Det N | Det Adj N | 'John'
    VP  -> V NP | V NP PP
    PP  -> P NP
    Det -> 'the' | 'a' | 'my'
    N   -> 'cat' | 'mat' | 'rat'
    Adj -> 'big' | 'small' | 'red'
    V   -> 'chased' | 'saw' | 'sat'
    P   -> 'on' | 'in' | 'under'
"""

grammar = CFG.fromstring(grammar_str)
print(grammar)
```

### Parsing with Grammars

Use different parsing algorithms:

```python
from nltk.parse import RecursiveDescentParser, ChartParser
from nltk import CFG

grammar = CFG.fromstring("""
    S   -> NP VP
    NP  -> Det N | 'John'
    VP  -> V NP
    Det -> 'the' | 'a'
    N   -> 'cat' | 'mat'
    V   -> 'chased' | 'saw'
""")

sentence = "the cat chased the mat".split()

# Recursive descent parser
rd_parser = RecursiveDescentParser(grammar)
for tree in rd_parser.parse(sentence):
    print(tree)
    print(tree.prettify())

# Chart parser (more efficient for ambiguous sentences)
chart_parser = ChartParser(grammar)
for tree in chart_parser.parse(sentence):
    print(tree)
```

### Earley Parser (Generalized Parsing)

Handles ambiguous and ungrammatical sentences:

```python
from nltk.parse import EarleyParser
from nltk import CFG

grammar = CFG.fromstring("""
    S   -> NP VP
    NP  -> Det N | NP PP
    VP  -> V NP
    PP  -> P NP
    Det -> 'the' | 'a'
    N   -> 'cat' | 'mat' | 'rat'
    V   -> 'chased' | 'saw'
    P   -> 'on' | 'in'
""")

# Ambiguous sentence (prepositional phrase attachment)
sentence = "the cat sat on the mat".split()

parser = EarleyParser(grammar)
trees = list(parser.parse(sentence))

print(f"Number of parse trees: {len(trees)}")
for i, tree in enumerate(trees, 1):
    print(f"\nParse tree {i}:")
    print(tree.prettify())
```

### Shift-Reduce Parser

Bottom-up parsing for CFGs:

```python
from nltk.parse import ShiftReduceParser
from nltk import Nonterminal, Production

# Define grammar programmatically
S = Nonterminal('S')
NP = Nonterminal('NP')
VP = Nonterminal('VP')

grammar = CFG(
    S,
    [
        Production(S, [NP, VP]),
        Production(NP, ['the', 'cat']),
        Production(VP, ['chased', 'the', 'mat']),
    ]
)

sentence = "the cat chased the mat".split()
parser = ShiftReduceParser(grammar)

for tree in parser.parse(sentence):
    print(tree.prettify())
```

## Probabilistic Context-Free Grammars (PCFGs)

### Creating PCFG from Corpus

Learn grammar probabilities from annotated corpus:

```python
from nltk.corpus import treebank
from nltk.parse import pcfg

# Get parsed sentences from Penn Treebank
trees = treebank.parsed_sents()[:1000]

# Induce PCFG from trees
pcfg = pcfg induce_pcfg_from_corpus(trees)

print("Sample productions:")
for prod in list(pcfg.productions())[:10]:
    print(f"{prod} (probability will be learned)")
```

### Parsing with PCFG

Get most probable parse:

```python
from nltk.parse import probabilistic
from nltk.corpus import treebank

# Load pre-trained PCFG (simplified example)
grammar_str = """
    S   -> NP VP [1.0]
    NP  -> Det N [0.7] | 'John' [0.3]
    VP  -> V NP [0.8] | V [0.2]
    Det -> 'the' [0.6] | 'a' [0.4]
    N   -> 'cat' [0.5] | 'mat' [0.5]
    V   -> 'chased' [0.5] | 'saw' [0.5]
"""

pcfg = probabilistic.PCFG.fromstring(grammar_str)

sentence = "the cat chased the mat".split()

# Get most probable parse
parser = probabilistic.ChartParser(pcfg)
best_tree = parser.parse(sentence)[0][0]  # (probability, tree)

print(f"Probability: {best_tree[0]}")
print(best_tree[1].prettify())
```

## Feature Grammars

### Feature Structures

Define grammars with feature constraints:

```python
from nltk import FeatureGrammar, FeatStruct

# Define feature grammar
grammar_str = """
    S       -> NP{1} VP{1}
    NP      -> Det N
            | 'John' [person='john', gender=masc, number=sing]
            | 'Mary' [person='mary', gender=fem, number=sing]
    VP      -> V{subj} NP{obj}
    Det     -> 'the' | 'a'
    N       -> 'cat' [gender=neut, number=sing]
            | 'cats' [gender=neut, number=plur]
    V       -> 'chases' [subj-number=sing]
            | 'chase' [subj-number=plur]
    P       -> 'on' | 'in'
"""

grammar = FeatureGrammar.fromstring(grammar_str)

sentence = "John chases the cat".split()

from nltk.parse import RecursiveDescentParser
parser = RecursiveDescentParser(grammar)

for tree in parser.parse(sentence):
    print(tree.prettify())
```

### Agreement Features

Enforce subject-verb agreement:

```python
from nltk import FeatureGrammar

grammar_str = """
    S       -> NP{num} VP{num}
    NP      -> Det N
    VP      -> V{num} NP
    Det     -> 'the' | 'a'
    N       -> 'cat' [num=sing] | 'cats' [num=plur]
    V       -> 'chases' [num=sing] | 'chase' [num=plur]
"""

grammar = FeatureGrammar.fromstring(grammar_str)

# Correct sentence
sentence1 = "the cat chases".split()
print("Correct sentence:")
for tree in parser.parse(sentence1):
    print(tree.prettify())

# Incorrect sentence (should fail)
sentence2 = "the cat chase".split()
print("\nIncorrect sentence (no parse expected):")
trees = list(parser.parse(sentence2))
print(f"Number of parses: {len(trees)}")  # Should be 0
```

## Dependency Parsing

### Stanford Dependency Parser

Interface to Stanford CoreNLP:

```python
from nltk.parse import stanford

# Set path to Stanford Parser
stanford_parser_path = '/path/to/stanford-parser.jar'
stanford_options = {'javaOptions': '-mx4g'}

# Load parser
parser = stanford.StanfordDependencyParser(
    model_path=stanford_parser_path,
    options=stanford_options
)

sentence = "The cat chased the rat".split()
trees = parser.parse(sentence)

for tree in trees:
    print(tree)
```

### Universal Dependencies

Parse with universal dependency format:

```python
# Example of universal dependency relations
# nsubj: nominal subject
# obj: object
# det: determiner
# root: root of sentence

sentence = "The cat chased the rat"
# Expected dependencies:
# chased (root)
# The -> cat (det)
# cat -> chased (nsubj)
# the -> rat (det)
# rat -> chased (obj)
```

## Grammar Utilities

### Chomsky Normal Form

Convert grammar to CNF:

```python
from nltk import CFG

grammar = CFG.fromstring("""
    S   -> NP VP PP
    NP  -> Det N
    VP  -> V NP
    PP  -> P NP
    Det -> 'the'
    N   -> 'cat'
    V   -> 'chased'
    P   -> 'on'
""")

# Convert to Chomsky Normal Form
cnf_grammar = grammar.to_chomsky_normal_form()

print("Original productions:")
for prod in grammar.productions():
    print(prod)

print("\nCNF productions:")
for prod in cnf_grammar.productions():
    print(prod)
```

### Grammar Simplification

Remove unit productions and unreachable symbols:

```python
from nltk import CFG

grammar = CFG.fromstring("""
    S   -> A
    A   -> B
    B   -> 'a' | 'b'
    C   -> 'c'  # Unreachable from S
""")

# Remove unit productions (A -> B where B is non-terminal)
simplified = grammar.remove_unit_productions()

print("Simplified grammar:")
for prod in simplified.productions():
    print(prod)
```

## Parsing Evaluation

### Parse Tree Metrics

Evaluate parser accuracy:

```python
from nltk.parse import evaluate
from nltk.corpus import treebank

# Gold standard trees
gold_trees = treebank.parsed_sents()[:100]

# Predicted trees (from your parser)
# predicted_trees = [your_parser.parse(tree.leaves()) for tree in gold_trees]

# Calculate accuracy metrics
# - F-score: harmonic mean of precision and recall
# - Precision: correctly parsed brackets / total predicted brackets
# - Recall: correctly parsed brackets / total gold brackets

# Example (with actual parser output):
# evaluate(gold_trees, predicted_trees)
```

### Bracket Evaluation

Detailed bracket-level evaluation:

```python
from nltk.evaluate import BracketingEvaluation

gold = """(S (NP the cat) (VP chased (NP the rat)))"""
predicted = """(S (NP the) (VP cat chased (NP the rat)))"""

evaluator = BracketingEvaluation()
evaluator.add_parse(gold, predicted)

print(f"Precision: {evaluator.precision():.2%}")
print(f"Recall: {evaluator.recall():.2%}")
print(f"F-measure: {evaluator.f_measure():.2%}")
```

## Common Patterns

### Simple Question Parser

Build a parser for specific domain:

```python
from nltk import CFG
from nltk.parse import RecursiveDescentParser

# Grammar for simple questions
grammar = CFG.fromstring("""
    S       -> WhQuestion | YesNoQuestion
    WhQuestion -> WH VP
    YesNoQuestion -> AUX NP VP '?'
    VP      -> V NP
    WH      -> 'who' | 'what' | 'where'
    AUX     -> 'is' | 'are' | 'do' | 'does'
    NP      -> Det N | 'John' | 'Mary'
    Det     -> 'the' | 'a'
    N       -> 'cat' | 'dog' | 'book'
    V       -> 'chase' | 'read' | 'see'
""")

parser = RecursiveDescentParser(grammar)

questions = [
    "who chase the cat".split(),
    "is John read the book".split(),
]

for question in questions:
    print(f"\nQuestion: {' '.join(question)}")
    trees = list(parser.parse(question))
    if trees:
        print(trees[0].prettify())
    else:
        print("No parse found (ungrammatical)")
```

### Extract Grammatical Relations

Extract subject-object relations from parse tree:

```python
from nltk import pos_tag, word_tokenize
from nltk.parse import RegexpParser

def extract_relations(text):
    """Extract subject-verb-object relations."""
    tokens = word_tokenize(text)
    tags = pos_tag(tokens)
    
    # Simple chunking grammar
    grammar = """
        NP: {<DT>?<JJ>*<NN>}
        VP: {<VB><.*>?}
    """
    
    parser = RegexpParser(grammar)
    tree = parser.parse(tags)
    
    relations = []
    chunks = list(tree)
    
    for i, chunk in enumerate(chunks):
        if hasattr(chunk, 'label'):
            if chunk.label() == 'NP' and i < len(chunks) - 1:
                # Look for following VP
                for j in range(i + 1, len(chunks)):
                    if hasattr(chunks[j], 'label') and chunks[j].label() == 'VP':
                        subject = ' '.join(t for t, _ in chunk.leaves())
                        verb = next((t for t, p in chunks[j].leaves() 
                                    if p.startswith('VB')), None)
                        relations.append((subject, verb))
                        break
    
    return relations

text = "The cat chased the rat"
relations = extract_relations(text)
print(relations)  # [('The cat', 'chased')]
```

## Troubleshooting

### No Parse Found

**Problem**: Parser returns no trees for valid sentence

**Solution**: Check grammar coverage:

```python
from nltk import CFG
from nltk.parse import RecursiveDescentParser

grammar = CFG.fromstring("""
    S   -> NP VP
    NP  -> Det N
    VP  -> V NP
    Det -> 'the'
    N   -> 'cat'
    V   -> 'chased'
""")

# Missing 'rat' in grammar!
sentence = "the cat chased the rat".split()

parser = RecursiveDescentParser(grammar)
trees = list(parser.parse(sentence))
print(f"Parses found: {len(trees)}")  # 0

# Fix: Add 'rat' to grammar
grammar_fixed = CFG.fromstring("""
    S   -> NP VP
    NP  -> Det N
    VP  -> V NP
    Det -> 'the'
    N   -> 'cat' | 'rat'
    V   -> 'chased'
""")

parser_fixed = RecursiveDescentParser(grammar_fixed)
trees = list(parser_fixed.parse(sentence))
print(f"Parses found: {len(trees)}")  # 1
```

### Ambiguous Sentences

**Problem**: Multiple parse trees for same sentence

**Solution**: Use PCFG to get most probable parse, or add disambiguation rules:

```python
from nltk.parse import probabilistic

# Use probabilities to prefer one parse
grammar = probabilistic.PCFG.fromstring("""
    S   -> NP VP [1.0]
    NP  -> Det N [0.9] | NP PP [0.1]  # Prefer simple NP
    VP  -> V NP [1.0]
    PP  -> P NP [1.0]
    Det -> 'the' [1.0]
    N   -> 'cat' [0.5] | 'mat' [0.5]
    V   -> 'sat' [1.0]
    P   -> 'on' [1.0]
""")

sentence = "the cat sat on the mat".split()
parser = probabilistic.ChartParser(grammar)
best_tree = parser.parse(sentence)[0]

print(f"Best parse probability: {best_tree[0]}")
print(best_tree[1].prettify())
```

## Performance Tips

1. **Use chart parsing** for ambiguous grammars (avoids re-parsing)
2. **Cache grammar objects** - parsing is faster than grammar construction
3. **Simplify grammar** - remove unnecessary rules before parsing
4. **Use appropriate parser** - Earley for general CFGs, LR for deterministic

## References

- **Parsing Documentation**: https://www.nltk.org/howto/parse.html
- **Grammar Documentation**: https://www.nltk.org/howto/grammar.html
- **PCFG Documentation**: https://www.nltk.org/api/nltk.parse.pcfg.html
- **Penn Treebank**: https://catalog.ldc.upenn.edu/LDC99T42
