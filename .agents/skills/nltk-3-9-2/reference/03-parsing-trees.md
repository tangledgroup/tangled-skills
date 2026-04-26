# Parsing & Trees

## Context-Free Grammars

### Defining Grammars

```python
from nltk.grammar import CFG, Nonterminal, Production
from nltk import word_tokenize

# String-based grammar definition
grammar_str = """
    S -> NP VP
    NP -> Det N | Det Adj N | PropN
    VP -> V NP | V
    Det -> 'the' | 'a'
    Adj -> 'big' | 'small'
    N -> 'dog' | 'cat' | 'ball'
    V -> 'chased' | 'saw' | 'ran'
    PropN -> 'Fido' | 'Whiskers'
"""

from nltk import load_parser
cp = load_parser(grammar_str, read_only=False)
```

### Production and Nonterminal Classes

```python
from nltk.grammar import Nonterminal, Production

S = Nonterminal('S')
NP = Nonterminal('NP')
VP = Nonterminal('VP')

# Create a production: S -> NP VP
prod = Production(S, [NP, VP])
print(prod)  # S -> NP VP
```

### Grammar Binarization and Chomsky Normal Form

```python
from nltk.grammar import CFG
from nltk.tree import chomsky_normal_form

# Convert grammar to CNF (binary rules only)
cnf_grammar = CFG.binarize(grammar)
```

## Chart Parsing

Chart parsing is an efficient dynamic programming approach that avoids redundant work by caching partial results.

### Top-Down Chart Parser

Starts from the goal symbol and works down:

```python
from nltk.parse import TopDownChartParser
from nltk.grammar import CFG

grammar = CFG.fromstring("""
    S -> NP VP
    NP -> Det N
    VP -> V NP
    Det -> 'the'
    N -> 'dog' | 'cat'
    V -> 'chased'
""")

parser = TopDownChartParser(grammar)
tokens = word_tokenize("the dog chased the cat")
for tree in parser.parse(tokens):
    print(tree.pprint())
```

### Bottom-Up Chart Parser

Starts from the input tokens and works up:

```python
from nltk.parse import BottomUpChartParser

parser = BottomUpChartParser(grammar)
trees = list(parser.parse(tokens))
```

### Left-Corner Parsing

Optimized chart parsing for left-recursive grammars:

```python
from nltk.parse import TopDownLeftCornerChartParser, BottomUpLeftCornerChartParser

parser = TopDownLeftCornerChartParser(grammar)
```

### Stepping Chart Parser

Step through the parsing process interactively:

```python
from nltk.parse import SteppingChartParser

parser = SteppingChartParser(grammar)
parser.initialize(tokens)
while not parser.is_complete():
    parser.step()
    print(parser.chart.pretty_format())
```

## Earley Parsing

Earley's algorithm handles arbitrary CFGs including left-recursive and ambiguous grammars.

### Basic Earley Parser

```python
from nltk.parse import EarleyChartParser

parser = EarleyChartParser(grammar)
trees = list(parser.parse(tokens))
for tree in trees:
    print(tree.pprint())
```

### Feature Earley Parser

Handles feature-based grammars with unification:

```python
from nltk.parse import FeatureEarleyChartParser

# Requires a FeatureGrammar
feature_parser = FeatureEarleyChartParser(feature_grammar)
```

### Incremental Parsing

Parse tokens one at a time:

```python
from nltk.parse import IncrementalEarleyChartParser

parser = IncrementalEarleyChartParser(grammar)
for token in tokens:
    parser.update(token)
trees = list(parser.parses())
```

## CCG Parsing

Combinatory Categorial Grammar parsing for lexicalized parsing:

```python
from nltk.ccg import CCGChartParser, CCGLexicon

# Define a CCG lexicon
lexicon = CCGLexicon()
lexicon.enter('dog', 'N')
lexicon.enter('chased', '(S\\NP)/NP')

parser = CCGChartParser(lexicon)
trees = list(parser.parse(['the', 'dog', 'chased', 'the', 'cat']))
```

## Dependency Parsing

### DependencyGraph

Build and manipulate dependency structures:

```python
from nltk.parse.dependencygraph import DependencyGraph

# From CoNLL format
conll_str = """
Gerald	N	NN	PROPN	0
Rubin	N	NN	PROPN	nmod	Gerald
Hunt	N	NN	PROPN	flat	Rubin
"""

dep = DependencyGraph(conll_str)
tree = dep.tree()
print(tree.pprint())

# Access graph structure
print(dep.left_children(1))
print(dep.right_children(1))
```

### CoreNLP Dependency Parser

Interface to Stanford CoreNLP server:

```python
from nltk.parse.corenlp import CoreNLPDependencyParser, CoreNLPServer

server = CoreNLPServer('corenlp-4.5.6.jar', port=9000)
server.start()

parser = CoreNLPDependencyParser()
trees = parser.parse(tokens)
```

## BLLIP Parser

Statistical parser (Charniak-Johnson model):

```python
from nltk.parse import BllipParser

parser = BllipParser('cfg/bllip_wsj_no_probs/english.mrg')
# Or from unified model directory
parser = BllipParser.from_unified_model_dir('bllip-model-dir')

trees = list(parser.parse(tokens))[:5]  # top 5 parses
```

## Tree Operations

### Creating and Navigating Trees

```python
from nltk.tree import Tree

# Create a parse tree
tree = Tree('S', [
    Tree('NP', [Tree('DT', ['the']), Tree('NN', ['dog'])]),
    Tree('VP', [
        Tree('VBD', ['chased']),
        Tree('NP', [Tree('DT', ['the']), Tree('NN', ['cat'])])
    ])
])

# Navigate the tree
print(tree.leaves())      # ['the', 'dog', 'chased', 'the', 'cat']
print(tree.height())      # 4
print(tree.pos())         # [('the', 'DT'), ('dog', 'NN'), ...]
print(tree.productions()) # list of Productions

# Access subtrees
print(tree[0])    # NP subtree
print(tree[1][0]) # VBD subtree
```

### Tree from String

```python
tree = Tree.fromstring("(S (NP (DT the) (NN dog)) (VP (VBD chased)))")
```

### Tree Transformations

```python
from nltk.tree import collapse_unary, chomsky_normal_form

# Collapse unary nodes (single-child nonterminals)
collapsed = collapse_unary(tree)

# Convert to Chomsky Normal Form
cnf_tree = chomsky_normal_form(tree)
```

### Parented Trees

Trees with parent pointers for upward navigation:

```python
from nltk.tree import ParentedTree

ptree = ParentedTree.fromstring("(S (NP (DT the)) (VP (V saw)))")
node = ptree[1][0]  # V node
print(node.parent())       # VP
print(node.left_sibling()) # None
print(node.root())         # S
```

### Tree Visualization

```python
# GUI display (requires Tkinter)
tree.draw()

# Text-based pretty print
tree.pprint()

# SVG output
from nltk.tree import TreePrettyPrinter
svg = TreePrettyPrinter(tree).svg()
```
