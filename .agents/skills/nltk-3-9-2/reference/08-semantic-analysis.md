# NLTK Semantic Analysis - Complete Guide

## Overview

NLTK provides tools for semantic analysis including logic representation, inference, feature structures, and lambda calculus for formal semantics.

## Feature Structures

### Basic Feature Structures

Represent linguistic information as attribute-value matrices:

```python
from nltk.sem import featstruct

# Create feature structure
fs = featstruct.FeatStruct({
    'PERS': 1,
    'NUM': 'sg',
    'GEND': 'masc'
})

print(fs)
# [ PERS : 1
#    NUM  : sg
#    GEND : masc ]

# Create with path notation
fs2 = featstruct.FeatStruct('PERS:1 & NUM:sg')
print(fs2)

# Access values
print(fs['PERS'])  # 1
print(fs['NUM'])   # sg

# Check containment
fs3 = featstruct.FeatStruct('PERS:1')
print(fs3.subsumes(fs))  # True (fs3 is more general than fs)
```

### Complex Feature Structures

Nested and recursive structures:

```python
from nltk.sem import featstruct

# Nested feature structure
fs = featstruct.FeatStruct({
    'HEAD': {
        'VERB': 'yes',
        'TENSE': 'past'
    },
    'SUBJ': {
        'PERS': 3,
        'NUM': 'sg'
    }
})

print(fs)
# [ HEAD : [ VERB : yes
#             TENSE : past ]
#    SUBJ : [ PERS : 3
#             NUM  : sg ] ]

# Access nested values
print(fs['HEAD']['VERB'])  # 'yes'
print(fs['SUBJ']['PERS'])  # 3

# Path notation for complex structures
fs2 = featstruct.FeatStruct('HEAD.VERB:yes & HEAD.TENSE:past & SUBJ.PERS:3')
```

### Unification

Combine feature structures:

```python
from nltk.sem import featstruct

# Two compatible feature structures
fs1 = featstruct.FeatStruct('PERS:1 & NUM:sg')
fs2 = featstruct.FeatStruct('NUM:sg & GEND:masc')

# Unify them
result = fs1.unify(fs2)
print(result)
# [ PERS : 1
#    NUM  : sg
#    GEND : masc ]

# Incompatible structures (unification fails)
fs3 = featstruct.FeatStruct('NUM:sg')
fs4 = featstruct.FeatStruct('NUM:pl')

result = fs3.unify(fs4)
print(result)  # None (unification failed)
```

### Recursion and Co-indexation

```python
from nltk.sem import featstruct

# Recursive structure with co-indexation
fs = featstruct.FeatStruct({
    'CAT': 'NP',
    'FEAT': '$x',
    'DAUGHTERS': [
        {'CAT': 'Det', 'FEAT': '$x'},
        {'CAT': 'N', 'FEAT': '$x'}
    ]
})

print(fs)
# Shows co-indexed variables ($x refers to same feature structure)
```

## Logic Representation

### Propositional Logic

```python
from nltk.sem.logic import Expression, Variable, Constant, FunctionExpression

# Create logical expressions
p = Expression('P')  # Proposition P
q = Expression('Q')  # Proposition Q

# Logical connectives
not_p = Expression('~', [p])           # ¬P
p_and_q = Expression('&', [p, q])      # P ∧ Q
p_or_q = Expression('|', [p, q])       # P ∨ Q
p_implies_q = Expression('>', [p, q])  # P → Q

print(f"P: {p}")
print(f"¬P: {not_p}")
print(f"P ∧ Q: {p_and_q}")
print(f"P → Q: {p_implies_q}")

# Parse from string
expr = Expression.fromstring('(P & Q)')
print(f"Parsed: {expr}")
```

### First-Order Logic

```python
from nltk.sem.logic import Expression, Variable, Constant, FunctionExpression, QuantifiedExpression

# Constants and variables
john = Constant('john')
x = Variable('x')

# Predicates
man = FunctionExpression('man', [john])           # man(john)
mortal = FunctionExpression('mortal', [x])        # mortal(x)

# Complex expressions
loves = FunctionExpression('loves', [john, Constant('mary')])  # loves(john, mary)

# Quantification
forall_x_mortal = QuantifiedExpression(
    'forall', 
    x, 
    FunctionExpression('mortal', [x])
)  # ∀x mortal(x)

exists_x_man = QuantifiedExpression(
    'exists',
    x,
    FunctionExpression('man', [x])
)  # ∃x man(x)

print(f"man(john): {man}")
print(f"loves(john, mary): {loves}")
print(f"∀x mortal(x): {forall_x_mortal}")
print(f"∃x man(x): {exists_x_man}")

# Parse complex expressions
expr = Expression.fromstring('forall(x, (man(x) -> mortal(x))')
print(f"\nParsed: {expr}")
# ∀x (man(x) → mortal(x))
```

### Expression Manipulation

```python
from nltk.sem.logic import Expression

# Parse expression
expr = Expression.fromstring('forall(x, man(x))')

# Get components
print(f"Operator: {expr.operator()}")  # 'forall'
print(f"Variables: {expr.variables()}")  # ['x']
print(f"Arguments: {expr.arguments()}")  # [Variable('x'), Expression('man', [Variable('x')])]

# Check if atomic
atomic = Expression('P')
print(f"\n{atomic} is atomic: {atomic.is_atomic()}")  # True
print(f"{expr} is atomic: {expr.is_atomic()}")  # False

# Free variables
expr2 = Expression.fromstring('loves(x, y)')
print(f"\nFree variables in loves(x, y): {expr2.free_vars()}")  # ['x', 'y']

expr3 = Expression.fromstring('forall(x, loves(x, y))')
print(f"Free variables in ∀x loves(x, y): {expr3.free_vars()}")  # ['y']
```

## Lambda Calculus

### Lambda Expressions

Represent functions and meanings:

```python
from nltk.sem import lambda_calculus as lc

# Create lambda expression: λx. man(x)
x = lc.Variable('x')
man_x = lc.FunctionExpression('man', [x])
lambda_man = lc.LambdaExpression([x], man_x)

print(f"λx. man(x): {lambda_man}")

# Apply to argument: (λx. man(x))(john)
john = lc.Constant('john')
result = lambda_man.apply(john)
print(f"(λx. man(x))(john) = {result}")  # man(john)

# Complex lambda: λx.λy. loves(x, y)
y = lc.Variable('y')
loves_xy = lc.FunctionExpression('loves', [x, y])
lambda_loves = lc.LambdaExpression([x, y], loves_xy)

print(f"\nλx.λy. loves(x, y): {lambda_loves}")

# Partial application: (λx.λy. loves(x, y))(john)
partial = lambda_loves.apply(john)
print(f"(λx.λy. loves(x, y))(john) = {partial}")  # λy. loves(john, y)

# Full application: ((λx.λy. loves(x, y))(john))(mary)
mary = lc.Constant('mary')
full = partial.apply(mary)
print(f"((λx.λy. loves(x, y))(john))(mary) = {full}")  # loves(john, mary)
```

### Reduction

Reduce lambda expressions:

```python
from nltk.sem import lambda_calculus as lc

# Create expression that needs reduction
x = lc.Variable('x')
expr = lc.LambdaExpression([x], lc.FunctionExpression('f', [x]))
application = expr.apply(lc.Constant('a'))

print(f"Before reduction: {application}")

# Reduce (beta reduction)
reduced = application.reduce()
print(f"After reduction: {reduced}")  # f(a)

# Multiple reductions
y = lc.Variable('y')
expr2 = lc.LambdaExpression(
    [x], 
    lc.LambdaExpression([y], lc.FunctionExpression('g', [x, y]))
)
application2 = expr2.apply(lc.Constant('a')).apply(lc.Constant('b'))

print(f"\nBefore: {application2}")
reduced2 = application2.reduce()
print(f"After: {reduced2}")  # g(a, b)
```

## Discourse Representation Theory (DRT)

### DRS Construction

Build Discourse Representation Structures:

```python
from nltk.sem import drt

# Create empty DRS
drs = drt.DRS()

# Add universe (entities)
drs.universe.append('x')
drs.universe.append('y')

# Add conditions
drs.conditions.append(drt.DRTCondition('donkey', ['x']))
drs.conditions.append(drt.DRTCondition('own', ['john', 'x']))
drs.conditions.append(drt.DRTCondition('beat', ['x', 'y']))

print(f"Universe: {drs.universe}")
print(f"Conditions: {drs.conditions}")

# Nested DRS (for implications)
if_drs = drt.DRS()
if_drs.universe.append('z')
if_drs.conditions.append(drt.DRTCondition('farm', ['z']))

then_drs = drt.DRS()
then_drs.conditions.append(drt.DRTCondition('go', ['john', 'z']))

# Add implication to main DRS
drs.conditions.append(drt.DRTImplication(if_drs, then_drs))
```

### DRS Access and Manipulation

```python
from nltk.sem import drt

def create_donkey_sentence_drs():
    """Create DRS for 'Every donkey owner beats his donkey'."""
    
    # Main DRS
    main = drt.DRS()
    
    # Universal quantification: if someone owns a donkey, they beat it
    if_part = drt.DRS()
    if_part.universe.extend(['x', 'y'])
    if_part.conditions.append(drt.DRTCondition('person', ['x']))
    if_part.conditions.append(drt.DRTCondition('donkey', ['y']))
    if_part.conditions.append(drt.DRTCondition('own', ['x', 'y']))
    
    then_part = drt.DRS()
    then_part.conditions.append(drt.DRTCondition('beat', ['x', 'y']))
    
    main.conditions.append(drt.DRTImplication(if_part, then_part))
    
    return main

drs = create_donkey_sentence_drs()
print("DRS for donkey sentence:")
print(f"Conditions: {drs.conditions}")
```

## Inference and Entailment

### Simple Entailment Checking

```python
from nltk.sem.logic import Expression

def entails(knowledge_base, query):
    """
    Simple entailment checker (limited).
    In practice, use a proper theorem prover.
    """
    # This is a simplified example
    # Real entailment requires resolution or tableaux methods
    
    # Check if query is in knowledge base
    if query in knowledge_base:
        return True
    
    # Check simple modus ponens: P, P→Q ⊢ Q
    for fact in knowledge_base:
        if isinstance(fact, Expression) and fact.operator() == '>':
            antecedent = fact.arguments()[0]
            consequent = fact.arguments()[1]
            
            if antecedent in knowledge_base and consequent == query:
                return True
    
    return False

# Example knowledge base
kb = [
    Expression('man', [Constant('socrates')]),  # man(socrates)
    Expression('>', [  # ∀x (man(x) → mortal(x)) - simplified
        FunctionExpression('man', [Variable('x')]),
        FunctionExpression('mortal', [Variable('x')])
    ])
]

# Query: mortal(socrates)
query = Expression('mortal', [Constant('socrates')])

print(f"Does KB entail {query}? {entails(kb, query)}")
```

### Using External Theorem Provers

NLTK can interface with external theorem provers:

```python
from nltk.sem import inference

# Example using Prover9 (requires separate installation)
# prover = inference.Prover9Prover()

# Define axioms
axioms = [
    'forall(x, man(x) -> mortal(x))',
    'man(socrates)'
]

# Define query
query = 'mortal(socrates)'

# Prove (requires Prover9 installed)
# result = prover.prove(axioms, query)
# print(f"Proven: {result}")
```

## Semantic Parsing

### CCG Semantics

Combinatory Categorial Grammar with semantics:

```python
from nltk.sem import ccg

# Define lexical entry with semantic value
# "John" -> NP/n : john
john = ccg.CCGWord(
    'John',
    ccg.CCGCategory('NP', []),
    Expression.fromstring('john')
)

# "loves" -> (S\NP)/(NP\NP) : λy.λx. loves(x, y)
from nltk.sem import lambda_calculus as lc

x = lc.Variable('x')
y = lc.Variable('y')
loves_meaning = lc.LambdaExpression(
    [y, x], 
    FunctionExpression('loves', [x, y])
)

loves_word = ccg.CCGWord(
    'loves',
    ccg.CCGCategory.fromstring('(S\\NP)/(NP\\NP)'),
    loves_meaning
)

print(f"John: {john}")
print(f"Loves: {loves_word}")
```

### Type Logical Grammar

```python
from nltk.sem import tlg

# Create type logical grammar expressions
# This is advanced - refer to NLTK documentation for detailed examples

# Basic idea: associate syntactic categories with semantic types
# NP -> e (entity)
# S -> t (truth value)
# Transitive verb -> e -> e -> t
```

## Common Patterns

### Building a Simple Semantic Interpreter

```python
from nltk.sem.logic import Expression, Constant, FunctionExpression

class SimpleInterpreter:
    """Simple semantic interpreter for first-order logic."""
    
    def __init__(self):
        self.domain = {'john', 'mary', 'bob'}
        self.predicates = {
            'man': {'john', 'bob'},
            'woman': {'mary'},
            'loves': {('john', 'mary'), ('mary', 'bob')}
        }
    
    def evaluate(self, expr):
        """Evaluate logical expression."""
        if expr.is_atomic():
            predicate = expr.operator()
            args = tuple(str(arg) for arg in expr.arguments())
            
            if predicate in self.predicates:
                return args in self.predicates[predicate]
            return False
        
        elif expr.operator() == '~':
            return not self.evaluate(expr.arguments()[0])
        
        elif expr.operator() == '&':
            return all(self.evaluate(arg) for arg in expr.arguments())
        
        elif expr.operator() == '|':
            return any(self.evaluate(arg) for arg in expr.arguments())
        
        elif expr.operator() == '>':
            antecedent = self.evaluate(expr.arguments()[0])
            consequent = self.evaluate(expr.arguments()[1])
            return (not antecedent) or consequent
        
        return False

# Usage
interpreter = SimpleInterpreter()

# Evaluate man(john)
expr1 = FunctionExpression('man', [Constant('john')])
print(f"man(john): {interpreter.evaluate(expr1)}")  # True

# Evaluate loves(john, mary)
expr2 = FunctionExpression('loves', [Constant('john'), Constant('mary')])
print(f"loves(john, mary): {interpreter.evaluate(expr2)}")  # True

# Evaluate complex expression: man(john) & loves(john, mary)
from nltk.sem.logic import Expression
expr3 = Expression('&', [expr1, expr2])
print(f"man(john) ∧ loves(john, mary): {interpreter.evaluate(expr3)}")  # True
```

### WordNet-based Semantic Similarity

Integrate WordNet with semantic analysis:

```python
import nltk.corpus.wordnet as wn
from nltk.sem.logic import Expression

def wordnet_entailment(word1, word2):
    """Check if word1 entails word2 using WordNet hypernyms."""
    
    synsets1 = wn.synsets(word1)
    synsets2 = wn.synsets(word2)
    
    if not synsets1 or not synsets2:
        return False
    
    # Check if any synset of word2 is a hypernym of any synset of word1
    for ss1 in synsets1:
        hypernyms = ss1.hypernym_closure()
        for ss2 in synsets2:
            if ss2 in hypernyms:
                return True
    
    return False

# Examples
print(f"dog entails animal: {wordnet_entailment('dog', 'animal')}")  # True
print(f"car entails animal: {wordnet_entailment('car', 'animal')}")  # False
print(f"poodle entails dog: {wordnet_entailment('poodle', 'dog')}")  # True
```

## Troubleshooting

### Unification Fails

**Problem**: Feature structure unification returns None

**Solution**: Check for conflicting values:

```python
from nltk.sem import featstruct

# These conflict on NUM
fs1 = featstruct.FeatStruct('NUM:sg')
fs2 = featstruct.FeatStruct('NUM:pl')

result = fs1.unify(fs2)
print(result)  # None - unification failed

# Check values before unifying
print(f"fs1['NUM']: {fs1['NUM']}")  # sg
print(f"fs2['NUM']: {fs2['NUM']}")  # pl
```

### Lambda Reduction Doesn't Work

**Problem**: Expression doesn't reduce as expected

**Solution**: Ensure proper variable binding:

```python
from nltk.sem import lambda_calculus as lc

# Correct: variable is bound
x = lc.Variable('x')
expr1 = lc.LambdaExpression([x], lc.FunctionExpression('f', [x]))
result1 = expr1.apply(lc.Constant('a')).reduce()
print(result1)  # f(a) - works!

# Problem: using different variable objects
x1 = lc.Variable('x')
x2 = lc.Variable('x')  # Different object, even though same name
expr2 = lc.LambdaExpression([x1], lc.FunctionExpression('f', [x2]))
result2 = expr2.apply(lc.Constant('a')).reduce()
print(result2)  # f(x2) - doesn't reduce! x2 is free
```

### Logic Expression Parsing Errors

**Problem**: `Expression.fromstring()` fails

**Solution**: Check syntax and parentheses:

```python
from nltk.sem.logic import Expression

# Correct syntax
expr1 = Expression.fromstring('forall(x, (man(x) -> mortal(x)))')
print(expr1)  # Works!

# Common errors:
# Missing parentheses
try:
    expr2 = Expression.fromstring('forall(x, man(x) -> mortal(x))')
except Exception as e:
    print(f"Error: {e}")

# Wrong quantifier syntax
try:
    expr3 = Expression.fromstring('for all(x, man(x))')
except Exception as e:
    print(f"Error: {e}")
```

## References

- **Feature Structures**: https://www.nltk.org/howto/featstruct.html
- **Logic Documentation**: https://www.nltk.org/howto/logic.html
- **Semantics Package**: https://www.nltk.org/api/nltk.sem.html
- **DRT Documentation**: https://www.nltk.org/howto/drt.html
