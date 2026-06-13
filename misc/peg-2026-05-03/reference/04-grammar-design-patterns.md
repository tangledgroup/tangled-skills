# Grammar Design Patterns

## Contents
- Mindset Shift: Don't Reason Like EBNF
- Parser Combinator Perspective
- Ordered Choice Consequences
- Whitespace Handling Strategies
- Soft vs Hard Keywords

## Mindset Shift: Don't Reason Like EBNF

PEG may look like EBNF, but its meaning is quite different. **Don't try to reason about a PEG grammar the same way you would with EBNF or context-free grammars.** PEG is optimized to describe **how** input strings will be parsed, while CFGs are optimized to generate strings of the language they describe.

Key differences in reasoning:
- Alternatives are ordered (`A | B` ≠ `B | A`)
- If a rule returns failure, it doesn't mean parsing failed — just "try something else"
- The parser is **eager**: if a rule succeeds, the caller accepts it even if accepting causes overall failure later
- Effects of ordered choice may be hidden by many levels of indirection

## Parser Combinator Perspective

PEGs can be viewed as **recursive descent parsers expressed via parser combinators** where the choice operator is ordered. This perspective clarifies several design decisions:

- Each rule is a composable parser function
- Sequence (`e1 e2`) composes two parsers: run first, then second on remainder
- Choice (`e1 / e2`) tries first, falls back to second only on total failure
- Repetition operators are combinator wrappers around the base parser
- Memoization can be applied as a decorator pattern — any parser can be wrapped with caching without modifying its implementation (LPeg uses this)

This view explains why PEG naturally supports scannerless parsing: the type-3 (regular expression) expressions in the grammar handle tokenization, and type-2 (context-free) behavior emerges through recursive rule references. Whitespace and comments are consumed at strategic points in the grammar rather than in a separate phase.

## Ordered Choice Consequences

The ordered choice operator is the defining feature of PEGs and creates several design constraints:

### Longer alternatives before shorter

When one alternative is a prefix of another, the longer must come first:

```
# WRONG — second alternative never fires
IfStmt ← 'if' Expr 'then' Stmt
       / 'if' Expr 'then' Stmt 'else' Stmt

# CORRECT — try longer form first
IfStmt ← 'if' Expr 'then' Stmt 'else' Stmt
       / 'if' Expr 'then' Stmt
```

### Subsumed alternatives

If alternative A matches every string that alternative B matches (and possibly more), B is **subsumed** and never fires:

```
# 'ab' is subsumed by 'a' — never reached
Rule ← 'a' / 'ab'
```

This differs from CFG where both alternatives contribute to the language. In PEG, adding a new rule can **remove** strings from the matched language.

### Hidden effects through rule levels

Ordered choice effects propagate through many levels of indirection:

```
# At first glance, Alt2 seems reachable
Rule1 ← Rule2 / Alt2
Rule2 ← Rule3 / Alt3
Rule3 ← AlwaysSucceeds   # If this always succeeds, Alt2 and Alt3 never fire
```

Always test grammar changes empirically — the interaction between ordered choice and rule references can be non-obvious.

### Eager matching

PEG parsers are **eager**: if a rule succeeds, the caller accepts it even if accepting it causes overall parsing to fail later. The parser does not look ahead to see if accepting this match leads to dead ends:

```
# ('a'|'aa')'a' does NOT accept "aaa"
# 'a'|'aa' greedily matches first 'a', then final 'a' consumes second,
# leaving third 'a' unmatched. Parser does NOT backtrack to try 'aa'.
Rule ← ('a' | 'aa') 'a'

# ('aa'|'a')'a' does NOT accept "aa"
# 'aa'|'a' consumes both 'a's, leaving nothing for final 'a'
Rule ← ('aa' | 'a') 'a'
```

Neither rule accepts both `aa` and `aaa`. This is fundamentally different from CFG, where both alternatives would contribute to the language. The fix: order longer alternatives first.

## Whitespace Handling Strategies

PEGs can handle whitespace in three ways:

### Attach to preceding token

Each token definition consumes trailing whitespace:

```
Identifier ← [a-zA-Z_] [a-zA-Z0-9]* Spacing
Number     ← [0-9]+ Spacing
'+'        ← '+' Spacing
Spacing    ← ([ \t\n\r] / Comment)*
Comment    ← '#' (!EndOfLine .)* EndOfLine
```

This is the convention used in Ford's self-describing PEG and PeppaPEG.

### Attach to following token

Reference `Spacing` at the start of each rule that expects whitespace:

```
Expr ← Spacing (Term (('+' / '-') Spacing Term)*)
```

### Explicit at strategic points

Only reference `Spacing` where whitespace is meaningful:

```
# Whitespace between tokens in a statement, but not inside parentheses
Stmt ← Assign (';' Spacing Assign)*
Assign ← Target '=' Expr
Target ← NAME / '(' Spacing Expr Spacing ')'
```

### Per-region lexing

Unified PEG grammars can use different whitespace rules for embedded languages:

```
# SQL string with embedded JSON — different whitespace handling
Query ← 'SELECT' JsonData
JsonData ← '{' (!'}' .)* '}'  # No whitespace skipping inside JSON
```

## Soft vs Hard Keywords

### Hard keywords

Always reserved, cannot be used as identifiers:

```
# In pegen grammar syntax (CPython)
'class' → hard keyword (single quotes)
'def'   → hard keyword
'if'    → hard keyword
```

Using `class` as a variable name always fails.

### Soft keywords

Only reserved in specific contexts, can be identifiers elsewhere:

```
# In pegen grammar syntax
"match" → soft keyword (double quotes)
"case"  → soft keyword
```

`match = 42` is valid (identifier), but `match X:` triggers the match statement rule.

**Implementation:** Soft keywords use a lookahead predicate to check context:

```
# Match "match" only when followed by ":" (start of match statement)
MatchStmt ← &"match" "match" NAME ':' ...
```

The `&"match"` predicate checks that the next token is literally `match` without consuming it. If a later rule needs `match` as an identifier, it fires first and consumes the token.

**Pitfalls:** Soft keywords can be accepted in unintended positions due to ordered choice. Define them where few alternatives compete. In pegen, soft keywords are defined using double quotes (`"match"`) while hard keywords use single quotes (`'class'`).

**Guido's note on soft keywords:** "Soft keywords can be a bit challenging to manage as they can be accepted in places you don't intend to, given how the order alternatives behave in PEG parsers. In general, try to define them in places where there is not a lot of alternatives."
