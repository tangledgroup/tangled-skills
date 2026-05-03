# Advanced Topics

## Contents
- Pika Bottom-Up Parsing
- Runtime-Extensible Parsers
- Unified Grammars (Scannerless Parsing)
- Expression Clusters (Autumn)
- Theory and Undecidability

## Pika Bottom-Up Parsing

Pika parsing, described by Luke Hutchison (arXiv:2005.06444), applies PEG rules **bottom-up and right-to-left** — the inverse of recursive descent's top-down left-to-right order.

### How it works

1. Start from the end of input
2. Apply rules in reverse: match rightmost elements first
3. Build parse items bottom-up using dynamic programming
4. Left-recursive rules naturally terminate because parsing proceeds right-to-left

### Advantages over top-down PEG

- **Left recursion solved**: Right-to-left order means `A ← A e` does not loop — the parser has already processed the right side before reaching the left recursive reference
- **Optimal error recovery**: Bottom-up approach provides better context for error location and recovery suggestions
- **No grammar rewriting needed**: Use natural left-recursive forms directly

### Tradeoffs

- More complex implementation than recursive descent
- Different mental model — harder to reason about for practitioners accustomed to top-down parsing
- Less mature tooling ecosystem

## Runtime-Extensible Parsers

Traditional parser generators (yacc, bison) produce static parsers baked into the binary at compile time. Runtime-extensible parsers load and modify grammar at runtime.

### Use cases

- **Plugin syntax**: Database extensions adding new SQL clauses without recompiling
- **Dialect switching**: Support multiple language variants in one instance
- **Research prototyping**: Rapidly iterate on grammar changes
- **Wasm deployments**: Avoid baking all features into size-constrained binaries
- **Security restrictions**: Dynamically restrict acceptable grammar subsets

### Implementation approach (DuckDB)

1. Store base grammar as text
2. Load into PEG engine's rule dictionary at startup (~3ms for SQL grammar)
3. Extensions register additional rules programmatically
4. Parser reinitializes with merged rule set
5. No recompilation or restart required

### Performance considerations

- Grammar load time matters for short-lived instances (e.g., DuckDB in Wasm)
- Pre-compiling grammar to code is possible but defeats extensibility
- Runtime compilation overhead vs static parser: ~10x slower on benchmarks
- Absolute parsing time still sub-millisecond for typical queries
- For long-running services, load time is amortized

## Unified Grammars (Scannerless Parsing)

Traditional compiler design separates lexing (tokenization) from parsing. PEGs can unify both into a single grammar operating directly on characters.

### Ford's self-describing PEG

Ford's original paper includes a PEG that describes its own complete syntax — both lexical rules (identifiers, literals, comments) and hierarchical rules (grammar structure, expressions) in one unified specification:

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

### Benefits of unified grammars

- **No lexer hack**: C's type-name/identifier ambiguity requires special handling in lex+yacc. Unified PEG handles it naturally with predicates.
- **Per-region lexing**: Different parts of input can use different tokenization rules (e.g., embedded SQL in host language)
- **Nested constructs**: Nested comments `(* (* inner *) outer *)` handled by recursive rules, not state machines
- **Greedy tokenization**: PEG's greedy `*` naturally implements longest-match for identifiers and numbers

### When separate tokenizer is better

- Complex indentation (Python requires a stack inside the tokenizer)
- Encoding detection and handling
- Interactive mode with line-by-line processing
- Existing well-tested tokenizer that would be costly to reimplement
- Tokenizer errors should be reported before parser sees bad input

## Expression Clusters (Autumn)

Autumn's expression clusters group alternatives with explicit precedence and associativity, avoiding the layered-rule pattern:

### Traditional layered approach

```
# Requires separate rules per precedence level
Expr    ← Sum
Sum     ← Product (('+' / '-') Product)*
Product ← Value (('*' / '/') Value)*
Value   ← [0-9]+ / '(' Expr ')'
```

### Expression cluster approach

```
Expr ← expr
  → Expr '+' Expr @+ @left recur
  → Expr '-' Expr
  → Expr '*' Expr @+ @left recur
  → Expr '/' Expr
  → [0-9]+       @+
  → '(' Expr ')' @+
```

### Annotations

- `@+`: Increment precedence level for the following alternative(s)
- `@left recur`: Mark as left-recursive (enables fixed-point iteration, produces left-associative tree)
- No annotation: Inherits current precedence, right-associative (default)

### Advantages

- **Explicit precedence**: Operator precedence is visible in one place, not encoded in rule hierarchy
- **Easy evolution**: Insert new operators by adding alternatives — no need to restructure rules
- **Per-operator associativity**: Mix left and right associative operators naturally
- **Performance**: O(P × L) without full memoization, where P = operators, L = precedence levels

## Theory and Undecidability

### Emptiness is undecidable

For CFGs, determining whether a grammar generates any strings is decidable. For PEGs, it is **algorithmically undecidable** — no algorithm can determine whether a given PEG matches any strings.

**Proof sketch:** Any instance of the Post correspondence problem reduces to the PEG emptiness problem. Given pairs `(α₁, β₁), ..., (αₙ, βₙ)`, construct a PEG where a match exists iff a valid Post correspondence sequence exists. Since PCP is undecidable, so is PEG emptiness.

The constructed PEG:
```
S ← &(A !.) &(B !.) (γ₁/.../γₙ)+ γ₀
A ← γ₀ / γ₁ A α₁ / ... / γₙ A αₙ
B ← γ₀ / γ₁ B β₁ / ... / γₙ B βₙ
```

Where `γᵢ` are pairwise distinct equally long strings. Any string matched by `S` has the form where `α_{k₁}...α_{kₘ} = β_{k₁}...β_{kₘ}`, which is exactly a Post correspondence solution.

### Consequences

- Cannot algorithmically verify that a PEG grammar is "useful" (matches at least one string)
- Cannot generate sample inputs from a PEG grammar (unlike CFGs where string generation is straightforward)
- Grammar testing must be empirical — test with representative inputs

### Open problems

1. **Palindrome language**: Can a PEG recognize the language of palindromes? (Open since 2004)
2. **CFG languages not expressible as PEGs**: Conjectured to exist but no concrete example proven
3. **Optimal left-recursion handling**: Whether left recursion can be supported while maintaining linear-time guarantees

### Computational power

PEGs are at least as powerful as deterministic LR(k) languages and some non-context-free languages. The exact relationship between PEG languages and context-free languages remains one of the open questions in formal language theory.

### Non-context-free example: `a^n b^n c^n`

PEG can recognize `{a^n b^n c^n : n ≥ 0}`, which is provably not context-free:

```
S ← &(A !('a'/'b')) 'a'* B !.
A ← ('a' A 'b')?
B ← ('b' B 'c')?
```

For `A` to match, the first stretch of `a`s must be followed by exactly the same number of `b`s and no more. Additionally, `B` must match where the `a`s switch to `b`s, meaning those `b`s are followed by an equal number of `c`s. The `&` predicate ensures `A` succeeds (validating a count = b count) while consuming nothing, then `'a'*` consumes the a's, `B` matches and validates b count = c count, and `!.` ensures end of input.
