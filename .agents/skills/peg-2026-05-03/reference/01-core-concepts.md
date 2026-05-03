# Core Concepts

## Contents
- Parsing Expressions and Grammars
- Operator Semantics
- Precedence Table
- Key Semantic Differences from CFGs

## Parsing Expressions and Grammars

A **parsing expression** is a pattern that each string either matches or does not match. On match, a unique prefix of the string is consumed (which may be empty, partial, or the whole string). Whether a string matches may depend on parts after the consumed prefix (via lookahead predicates).

A **parsing expression grammar** is a collection of named parsing expressions that reference each other, with a designated starting expression. Formally: a tuple `(N, Σ, P, eS)` where `N` is nonterminals, `Σ` is terminals, `P` maps nonterminals to parsing expressions, and `eS` is the start expression.

**Concrete syntax conventions:**
- Ford's primary dialect: `Identifier ← Expression`
- Common variants: `<-`, `:=`, `=`
- Terminals in quotes: `"terminal"`, `'another'`
- Nonterminals as bare identifiers: `Nonterminal`
- Character classes: `[abc]`, `[0-9A-Za-z]`
- Any character: `.`
- Backslash escapes: `\n`, `\r`, `\\`

**Atomic expressions:**
- **Terminal**: A literal character or string. `"bar"` equals `"b" "a" "r"`.
- **Nonterminal**: Reference to another rule, equivalent to a function call.
- **Character class**: `[abc]` matches one listed character. Ranges: `[0-9]`.
- **Any**: `.` matches any single terminal.
- **Empty string (ε)**: Always succeeds, consumes nothing.
- **End of input**: `!.` (not-predicate on any-char).
- **Failure**: Matches nothing.

## Operator Semantics

### Sequence (`e1 e2`)

Invoke `e1`. If it succeeds, invoke `e2` on the remainder. If either fails, the entire sequence fails and consumes no input (backtracks to starting position).

```
# Matches "hello world"
Greeting ← "hello" " " "world"

# Fails — after matching "ab", nothing left for final "c"
Bad ← "a" "b" "c"
     # Input: "ab" → fails, consumes nothing
```

### Ordered Choice (`e1 / e2`)

Try `e1`. If it succeeds, return immediately — `e2` is never attempted. If `e1` fails, backtrack to the starting position and try `e2`.

```
# Matches "if x then y" but NOT "if x then y else z"
# because first alternative succeeds and second is discarded
IfStmt ← 'if' Expr 'then' Stmt 'else' Stmt
       / 'if' Expr 'then' Stmt

# CORRECT order — longer alternative first:
IfStmt ← 'if' Expr 'then' Stmt 'else' Stmt
       / 'if' Expr 'then' Stmt
```

### Repetition (`e*`, `e+`, `e?`)

- `e*`: Zero or more consecutive matches. Always greedy — consumes as many as possible.
- `e+`: One or more. Same greedy behavior, must match at least once.
- `e?`: Zero or one. Greedy — matches if possible.

**Critical difference from regex:** These never backtrack to leave input for subsequent patterns. `(a* a)` always fails because `a*` consumes all `a`s.

```
# Matches any number of digits
Number ← [0-9]+

# Always fails — Number consumed all digits, nothing left for final digit
Bad ← Number [0-9]
```

### And-Predicate (`&e`)

Invoke `e`. If `e` succeeds, the predicate succeeds. If `e` fails, the predicate fails. **Never consumes input** — always backtracks to starting position regardless of how much `e` consumed internally.

```
# Matches identifier only if NOT followed by "<-" (i.e., not a rule definition)
Primary ← Identifier !LEFTARROW

# Matches "foo" only if followed by "bar"
FooIfBar ← "foo" &"bar"
```

### Not-Predicate (`!e`)

Invoke `e`. If `e` fails, the predicate succeeds. If `e` succeeds, the predicate fails. **Never consumes input.**

```
# Matches any character except newline
NonNewline ← !EndOfLine .

# Matches a single "a" only if not part of a run of a's followed by b
LoneA ← !(a+ b) "a"

# End of input: no next character exists
EndOfFile ← !.
```

### Grouping (`(e)`)

Parenthesized expression. Controls precedence in complex expressions.

```
# Matches optional parenthesized expression
OptGroup ← '(' Expr ')' ?
```

## Precedence Table

From highest (tightest binding) to lowest:

| Priority | Operators |
|----------|-----------|
| 5 | `(e)` — grouping |
| 4 | `e*`, `e+`, `e?` — suffix repetition/optional |
| 3 | `&e`, `!e` — prefix predicates |
| 2 | `e1 e2` — sequence (juxtaposition) |
| 1 | `e1 / e2` — ordered choice |

This means `a &b* / c` parses as `(a (&(b*))) / c`, and `a b? / c d` parses as `((a (b?)) / c) d`.

## Key Semantic Differences from CFGs

### Ordered choice is not commutative

In CFG: `A → a b | a` equals `A → a | a b`
In PEG: `A ← a b / a` does NOT equal `A ← a / a b`

The second PEG rule never matches `ab` because `a` always succeeds first, consuming the `a`, leaving `b` unmatched.

### Greedy repetition never backtracks

CFG and regex `*+?` can yield shorter matches if context demands. PEG repetition always takes the longest possible match. This is a fundamental design choice favoring predictable behavior over flexibility.

### Single parse rule

For any given input position and rule, the result is deterministic: same success/failure outcome and same consumed length. In CFGs, the same nonterminal at the same position can produce different results depending on which path the parser takes.

### No ambiguity possible

PEGs cannot be ambiguous by construction. The ordered choice operator deterministically selects exactly one parse tree (or none). This eliminates the entire class of ambiguity-related problems that plague CFG-based parsers.
