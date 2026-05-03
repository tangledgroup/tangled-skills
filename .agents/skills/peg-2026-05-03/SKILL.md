---
name: peg-2026-05-03
description: Parsing Expression Grammars (PEGs) — recognition-based formal grammars using ordered choice to eliminate ambiguity, with linear-time packrat parsing. Covers operators, algorithms, left recursion handling, grammar design, practical implementations (CPython pegen, DuckDB, LPeg, PeppaPEG, Mouse, Guile), CFG/regex comparisons, and undecidability. Use when designing language parsers, implementing scannerless parsing, or prototyping new language grammar.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2026-05-03"
tags:
  - peg
  - parsing
  - parser-generator
  - formal-grammar
  - compiler-construction
  - packrat-parsing
category: tooling
external_references:
  - https://en.wikipedia.org/wiki/Parsing_expression_grammar
  - https://soasme.medium.com/the-c-tricks-i-used-when-developing-peppa-peg-a93302603322
  - https://medium.com/@gvanrossum_83706/peg-parsers-7ed72462f97c
  - https://medium.com/@gvanrossum_83706/building-a-peg-parser-d4869b5958fb
  - https://pablo-bravo.com/compiler-construction-2
  - https://peps.python.org/pep-0617/
  - https://www.romanredz.se/Mouse/index.htm#grammars
  - https://github.com/soasme/PeppaPEG
  - https://github.com/gpakosz/peg
  - https://duckdb.org/2024/11/22/runtime-extensible-parsers
  - https://github.com/we-like-parsers/pegen
  - https://www.gnu.org/software/guile/manual/html_node/PEG-Parsing.html
  - https://bford.info/pub/lang/peg.pdf
  - https://arxiv.org/pdf/1509.02439
  - https://we-like-parsers.github.io/pegen/peg_parsers.html
---

# Parsing Expression Grammars (PEG)

## Overview

A Parsing Expression Grammar (PEG), introduced by Bryan Ford in 2004, is a recognition-based formal grammar that describes languages through rules for **recognizing** strings rather than generating them. Unlike context-free grammars (CFGs) where choice is nondeterministic, PEGs use **ordered choice** (`/` or `|`) — the first matching alternative wins and others are discarded. This makes PEGs unambiguous by construction: every valid string has exactly one parse tree.

PEGs unify lexical analysis (tokenization) and syntactic parsing into a single grammar, eliminating the traditional lexer/parser split. They support unlimited lookahead via syntactic predicates (`&` and `!`), can express some non-context-free languages, and admit linear-time parsing through packrat memoization.

**Non-regex example:** `{a^n b^n : n ≥ 0}` is not a regular language but trivially a PEG:
```
start ← AB !.
AB    ← ('a' AB 'b')?
```
**Non-context-free example:** `{a^n b^n c^n : n ≥ 0}` is provably not context-free but expressible as PEG:
```
S ← &(A !('a'/'b')) 'a'* B !.
A ← ('a' A 'b')?
B ← ('b' B 'c')?
```

PEGs are used in production by CPython (since 3.9, default from 3.10 via PEP 617), DuckDB (experimental PEG parser since v1.5), Lua (LPeg), Guile Scheme, jq, and various parser generator tools including Mouse (Java-based, limited backtracking with recursive ascent left-recursion support).

## When to Use

- Designing a new programming language or DSL where grammar clarity matters
- Replacing LL(1)/LALR parsers that suffer from ambiguity, shift-reduce conflicts, or limited lookahead
- Implementing scannerless parsing where lexical rules depend on syntactic context
- Building runtime-extensible parsers (e.g., SQL dialect plugins, Wasm deployments)
- Prototyping language syntax before committing to a specific parser generator
- Resolving ambiguities like dangling else that require hand-crafted CFG workarounds
- Migrating from YACC/bison when reduce-reduce conflicts become maintenance hazards

## Core Operators

| Operator | Syntax | Precedence | Description |
|----------|--------|------------|-------------|
| Grouping | `(e)` | 5 (highest) | Parenthesized expression |
| Optional | `e?` or `[e]` | 4 | Zero or one match (greedy) |
| Zero-or-more | `e*` | 4 | Zero or more matches (always greedy) |
| One-or-more | `e+` | 4 | One or more matches (always greedy) |
| Exact repetition | `{n}` | 4 | Exactly n matches (PeppaPEG) |
| Gather | `s.e+` | 4 | One or more e separated by s (pegen) |
| And-predicate | `&e` | 3 | Succeed if e matches, consume nothing |
| Not-predicate | `!e` | 3 | Succeed if e fails, consume nothing |
| Cut/commit | `~` | 3 | Commit to current alternative (pegen) |
| Sequence | `e1 e2` | 2 | Match e1 then e2, backtrack on failure |
| Ordered choice | `e1 / e2` or `e1 \| e2` | 1 (lowest) | Try e1 first; if succeeds, discard e2 |
| Failure | `_` or `failure` | — | Always fails, matches nothing (some variants) |

**Key semantics:**
- **Ordered choice is not commutative**: `A / B` ≠ `B / A`. Place longer/more-specific alternatives first.
- **Repetition is always greedy**: `a*` consumes all available `a`s. Unlike regex, no non-greedy mode. `(a* a)` always fails.
- **Predicates consume nothing**: `&e` and `!e` only check — they never advance the input position.
- **Failure is not error**: A rule returning failure means "try the next alternative", not "syntax error".
- **Cut (`~`)**: Once passed, the parser commits to the current alternative even if it later fails. Prevents backtracking past this point.

## Minimal Example: Arithmetic Expressions

**Idiomatic right-recursive form (no left recursion):**
```
Expr    ← Sum
Sum     ← Product (('+' / '-') Product)*
Product ← Value (('*' / '/') Value)*
Value   ← [0-9]+ / '(' Expr ')'
```

Operator precedence is encoded through layered rules. The `*` repetition produces a flat list — left-associativity must be imposed during AST construction.

**Left-recursive form with pegen grammar actions (CPython):**
```
expr[expr_ty]:
    | l=expr '+' r=term { _Py_BinOp(l, Add, r, EXTRA) }
    | t=term { t }

term[expr_ty]:
    | l=term '*' r=factor { _Py_BinOp(l, Mult, r, EXTRA) }
    | f=factor { f }
```

Named captures (`l=`, `r=`) bind subexpression results. The `{...}` action (Python mode) or `#{...}#` (C mode) builds the AST node directly, eliminating intermediate parse trees. Each left-recursion iteration wraps the previous result as the left operand, producing a properly left-associative tree during parsing.

## Advanced Topics

**Core Concepts**: Formal definitions, operator semantics, precedence, PEG vs CFG differences, midpoint problem, self-describing meta-grammar → [Core Concepts](reference/01-core-concepts.md)

**Parsing Algorithms**: Recursive descent infrastructure, packrat parsing with memoization, selective caching, tokenizer integration, context manager approach → [Parsing Algorithms](reference/02-parsing-algorithms.md)

**Left Recursion and Associativity**: The left recursion problem, idiomatic workarounds, Ford/Warth fixed-point algorithm, expression clusters, associativity control → [Left Recursion and Associativity](reference/03-left-recursion-and-associativity.md)

**Grammar Design Patterns**: Mindset shift from EBNF, ordered choice consequences (eager matching, subsumed alternatives), whitespace strategies, soft vs hard keywords → [Grammar Design Patterns](reference/04-grammar-design-patterns.md)

**Error Handling and Actions**: Error location problem, YACC all-or-nothing behavior, two-pass recovery, annotated recovery rules, semantic actions (Python/C modes) → [Error Handling and Actions](reference/05-error-handling.md)

**Practical Implementations**: CPython pegen (PEP 617, LL(1) workarounds eliminated), DuckDB extensible parser, LPeg (Lua, parser combinators), PeppaPEG (ANSI C), peg/leg, Guile `(ice-9 peg)` → [Practical Implementations](reference/06-practical-implementations.md)

**PEG vs Alternatives**: CFG comparison, regex comparison, advantages and disadvantages summary → [PEG vs Alternatives](reference/07-peg-vs-alternatives.md)

**Advanced Topics**: Pika bottom-up parsing, runtime-extensible grammars, unified scannerless parsing, expression clusters, theory and undecidability → [Advanced Topics](reference/08-advanced-topics.md)
