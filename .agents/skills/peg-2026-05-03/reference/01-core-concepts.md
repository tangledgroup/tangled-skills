# Core Concepts

## Contents
- Parsing Expressions and Grammars
- Atomic Expressions
- Operator Semantics
- Cut/Commit Operator
- Gather Syntax
- Precedence Table
- Key Semantic Differences from CFGs
- The Midpoint Problem
- Self-Describing PEG Meta-Grammar

## Parsing Expressions and Grammars

A **parsing expression** is a pattern that each string either matches or does not match. On match, a unique prefix of the string is consumed (which may be empty, partial, or the whole string). Whether a string matches may depend on parts after the consumed prefix (via lookahead predicates).

A **parsing expression grammar** is a collection of named parsing expressions that reference each other, with a designated starting expression. Formally: a tuple `(N, Σ, P, eS)` where `N` is nonterminals, `Σ` is terminals, `P` maps nonterminals to parsing expressions, and `eS` is the start expression.

**Concrete syntax conventions:**
- Ford's primary dialect: `Identifier ← Expression`
- Common variants: `<-`, `:=`, `=`, `:`
- Terminals in quotes: `"terminal"`, `'another'`
- Nonterminals as bare identifiers: `Nonterminal`
- Character classes: `[abc]`, `[0-9A-Za-z]`
- Any character: `.`
- Backslash escapes: `\n`, `\r`, `\\`

## Atomic Expressions

- **Terminal**: A literal character or string. `"bar"` equals `"b" "a" "r"`.
- **Nonterminal**: Reference to another rule, equivalent to a function call.
- **Character class**: `[abc]` matches one listed character. Ranges: `[0-9]`.
- **Any**: `.` matches any single terminal.
- **Empty string (ε)**: Always succeeds, consumes nothing. Written as `?` on an empty expression or simply omitted.
- **End of input**: `!.` (not-predicate on any-char) — succeeds when no next character exists.
- **Failure**: Matches nothing. Some PEG variants provide explicit `failure` or `_` expressions.

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

### Ordered Choice (`e1 / e2` or `e1 | e2`)

Try `e1`. If it succeeds, return immediately — `e2` is never attempted. If `e1` fails, backtrack to the starting position and try `e2`.

```
# CORRECT order — longer alternative first:
IfStmt ← 'if' Expr 'then' Stmt 'else' Stmt
       / 'if' Expr 'then' Stmt

# WRONG — second alternative never fires:
IfStmt ← 'if' Expr 'then' Stmt
       / 'if' Expr 'then' Stmt 'else' Stmt
```

This is the PEG solution to the **dangling else** problem. In CFGs, `if-then` and `if-then-else` create ambiguity. In PEG, ordering resolves it deterministically.

### Repetition (`e*`, `e+`, `e?`)

- `e*`: Zero or more consecutive matches. Always greedy — consumes as many as possible.
- `e+`: One or more. Same greedy behavior, must match at least once.
- `e?`: Zero or one. Greedy — matches if possible.

**Critical difference from regex:** These never backtrack to leave input for subsequent patterns. `(a* a)` always fails because `a*` consumes all `a`s.

### And-Predicate (`&e`)

Invoke `e`. If `e` succeeds, the predicate succeeds. If `e` fails, the predicate fails. **Never consumes input** — always backtracks to starting position regardless of how much `e` consumed internally.

```
# Matches identifier only if NOT followed by "<-" (not a rule definition)
Primary ← Identifier !LEFTARROW

# Matches "foo" only if followed by "bar"
FooIfBar ← "foo" &"bar"
```

### Not-Predicate (`!e`)

Invoke `e`. If `e` fails, the predicate succeeds. If `e` succeeds, the predicate fails. **Never consumes input.**

```
# Matches any character except newline
NonNewline ← !EndOfLine .

# End of input: no next character exists
EndOfFile ← !.
```

## Cut/Commit Operator (`~`)

The cut operator (`~`), supported by pegen and some other PEG variants, commits to the current alternative. Once the parser passes `~`, it will not backtrack past this point — even if the rule ultimately fails.

```
# If '(' matches, commit to this path — don't try other alternatives on failure
rule ← '(' ~ Expr ')' / OtherAlt

# Without cut: if Expr or ')' fails, backtracks to try OtherAlt
# With cut: if Expr or ')' fails, the whole rule fails (no backtrack)
```

This is useful for providing specific error messages: once you've matched the opening of a construct, you want to report errors within it rather than silently trying other alternatives.

## Gather Syntax (`s.e+`)

The gather syntax (`s.e+`), supported by pegen, matches one or more occurrences of `e` separated by `s`. The generated parse tree does not include the separator. Equivalent to `(e (s e)*)` but cleaner.

```
# Match comma-separated expressions, without commas in the result
comma_separated ← ','.expr+

# Equivalent to: expr (',' expr)*
```

## Precedence Table

From highest (tightest binding) to lowest:

| Priority | Operators |
|----------|-----------|
| 5 | `(e)` — grouping |
| 4 | `e*`, `e+`, `e?`, `{n}` — suffix repetition/optional |
| 3 | `&e`, `!e`, `~` — prefix predicates, cut |
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

### Adding rules can remove strings

In CFG, adding a new production cannot remove strings from the language (though it can introduce ambiguity). In PEG, adding a rule before an existing one can **subsume** it:

```
# G1 accepts "ab" and "a"
G1 ← "a" "b" / "a"

# G2 accepts only "a" — "ab" is consumed by first alternative, leaving nothing for second
G2 ← "a" / "a" "b"
```

## The Midpoint Problem

PEG's greedy matching can fail to find globally optimal parses for certain grammars. Ford's "midpoint problem" demonstrates this:

```
S ← 'x' S 'x' / 'x'
```

This CFG accepts odd-length strings of `x`. As a PEG, it fails on some inputs due to greedy matching. Tracing `xxxxxq`:

```
Position:  123456
  String:  xxxxxq
  Results:
           ↑ Pos.6: Neither branch of S matches (q ≠ 'x', no 'x' for first branch)
          ↑ Pos.5: First branch fails, second succeeds → match length 1
         ↑ Pos.4: First branch fails, second succeeds → match length 1
        ↑ Pos.3: First branch succeeds → match length 3 (consumes positions 3-5)
       ↑ Pos.2: First branch: after 'x' at pos 2, S matches at pos 3 (length 3),
                then needs 'x' but finds q at pos 6 → FAILS.
                Second branch succeeds → match length 1
      ↑ Pos.1: First branch: after 'x' at pos 1, S matches at pos 2 (length 1),
               then needs 'x' at pos 3 → succeeds → match length 3
```

At position 1, S matches only 3 characters (`xxx`), not all 5. The greedy choice at position 3 consumed `xxx` (positions 3-5) instead of the single `x` that would have allowed the outer rule to match all 5. **Locally optimal ≠ globally optimal.**

The language itself is regular (odd number of x's), expressible as a simple regex or CFG with different structure. But this specific PEG grammar cannot recognize it correctly.

## Self-Describing PEG Meta-Grammar

Ford's original paper includes a PEG that describes its own complete syntax — both lexical and syntactic rules in one unified specification:

```
Grammar    ← Spacing Definition+ EndOfFile
Definition ← Identifier LEFTARROW Expression
Expression ← Sequence (SLASH Sequence)*
Sequence   ← Prefix*
Prefix     ← (AND / NOT)? Suffix
Suffix     ← Primary (QUESTION / STAR / PLUS)?
Primary    ← Identifier !LEFTARROW
           / OPEN Expression CLOSE
           / Literal
           / Class
           / DOT

# Lexical rules — same grammar, different level
Identifier ← IdentStart IdentCont* Spacing
Literal    ← ['] (!['] Char)* ['] Spacing
           / ["] (!["] Char)* ["] Spacing
Class      ← '[' (!']' Range)* ']' Spacing
Spacing    ← (Space / Comment)*
Comment    ← '#' (!EndOfLine .)* EndOfLine
```

This demonstrates PEG's unified grammar capability: lexical rules (identifiers, literals, comments) and syntactic rules (grammar structure, expressions) coexist in a single specification with no separate tokenizer phase.
