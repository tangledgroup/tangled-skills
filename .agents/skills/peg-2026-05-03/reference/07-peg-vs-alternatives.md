# PEG vs Alternatives

## Contents
- PEG vs Context-Free Grammars
- PEG vs Regular Expressions
- Advantages Summary
- Disadvantages Summary

## PEG vs Context-Free Grammars

### Fundamental difference: choice semantics

| Property | CFG | PEG |
|----------|-----|-----|
| Choice operator | Unordered (`\|`) | Ordered (`/` or `\|`) |
| Commutativity | `A \| B` = `B \| A` | `A / B` ≠ `B / A` |
| Ambiguity | Possible (multiple parse trees) | Impossible (single parse tree or none) |
| Parsing approach | Deduce which alternative fits | Try alternatives in order, first wins |
| Empty productions | Natural (`A → ε`) | Via `?` operator |
| Adding rules | Cannot remove strings from language | Can subsume existing alternatives |

### Language expressiveness

**PEG can do some things CFG cannot:**
- Non-context-free languages: `a^n b^n c^n` is expressible as PEG but provably not CFG
- Greedy longest-match semantics directly in grammar
- Negative syntax (`!e`) for exclusion patterns
- Closed under intersection and complement (via `&` and `!`)

**CFG may do some things PEG cannot (conjectured, not proven):**
- The midpoint problem: `S ← 'x' S 'x' / 'x'` struggles with odd-length `x` strings due to greedy matching
- Palindrome language: open problem whether expressible as PEG
- It is conjectured that some CFG languages cannot be expressed as PEGs, but no concrete example has been proven

### Closure properties

| Operation | CFG | PEG |
|-----------|-----|-----|
| Union | ✓ | ✓ |
| Intersection | ✗ | ✓ |
| Complement | ✗ | ✓ |

PEG languages are closed under intersection and complement. This is a direct consequence of the predicate operators `&` and `!`.

### Parsing complexity

| Parser type | Worst-case time |
|-------------|-----------------|
| General CFG (CYK) | O(n³), equivalent to boolean matrix multiplication |
| LL(1) | O(n) but restricted grammar class |
| LALR(1) | O(n) but restricted grammar class |
| GLR | O(n²) worst case, handles all CFGs |
| PEG (naive recursive descent) | O(2^n) exponential |
| PEG (packrat with memoization) | O(n × r) linear for any PEG |

### Practical comparison

**CFG advantages:**
- Mature tooling (yacc, bison, antlr)
- Well-understood theory and transformations
- Good error reporting in LR parsers (position is known)
- Lower memory usage (LR parsers scale with parse depth, not input size)

**PEG advantages:**
- No ambiguity — grammar order determines behavior
- Unlimited lookahead via predicates
- Unified lexer + parser eliminates scannerless gap
- Linear-time parsing guaranteed with packrat
- Grammar closely matches how the parser operates (easier to reason about)
- Easier to express complex disambiguation (dangling else, soft keywords)
- Direct AST construction via grammar actions (eliminates intermediate CST)

### Migration motivation (pycparser case study)

Eli Bendersky's pycparser project (~20M daily downloads) migrated from PLY (YACC-based) to hand-written recursive descent, motivated by:
- **177 reduce-reduce conflicts** in the latest PLY-based release — severe maintenance hazard where parsing rules are tie-broken by order of appearance (very brittle, "spooky-action-at-a-distance" effects)
- Growing conflicts as C11/C23 features were added
- PLY abandonment/archiving creating dependency risk
- **~30% speedup** observed from recursive descent vs YACC-generated parser
- Recursive descent parsers being easier to understand and maintain

## PEG vs Regular Expressions

### Expressiveness

| Feature | Pure Regex (finite automaton) | PEG |
|---------|------------------------------|-----|
| Bounded nesting | Fixed depth only | Unbounded via recursion |
| `a^n b^n` | Impossible | Trivial: `('a' AB 'b')?` |
| Greedy repetition | Optional (`*?` non-greedy) | Always greedy (no non-greedy mode) |
| Lookahead | Limited (`(?=...)`, `(?!...)`) | Unlimited (`&e`, `!e` with any expression) |
| Backreferences | In many engines (non-theoretical) | Via rule references |

### Key differences

**Greedy behavior:** PEG repetition is always greedy. `[ab]?[bc][cd]` matches `bc` as a regex but not as a PEG, because `[ab]?` greedily consumes `b`, then `[bc]` consumes `c`, leaving nothing for `[cd]`.

**End of input:** PEG expresses end-of-input with `!.` (no next character exists). Regex requires magic anchors `$` or `\Z`.

**Regex → PEG compilation:** Any regex can be compiled to a PEG by creating a nonterminal for each NFA state and encoding transitions as ordered choices. Use NFA (not DFA) — the DFA equivalent can be exponentially larger for some regex families.

### When to prefer PEG over regex

- Parsing nested/recursive structures (parentheses, brackets, templates)
- When the pattern involves context-sensitive rules
- When you need to build a parse tree, not just match
- When combining lexical and syntactic analysis

## Advantages Summary

1. **No compilation required**: PEGs can be executed directly without converting to state machines or lookup tables
2. **Unambiguous by construction**: Ordered choice eliminates the ambiguity problem entirely
3. **Linear-time parsing**: Packrat memoization guarantees O(n × r) for any PEG
4. **Unified grammar**: Single grammar handles both lexical and syntactic rules (scannerless parsing)
5. **Unlimited lookahead**: Predicates provide arbitrary lookahead without special machinery
6. **Ordered choice matches intuition**: Grammar order reflects parser behavior — easier to reason about
7. **Rich operator set**: Sequence, choice, repetition, predicates, cut, grouping — expressive with few primitives
8. **Closure under intersection/complement**: Enables powerful composition of grammars
9. **Direct AST construction**: Grammar actions build AST during parsing, eliminating intermediate CST

## Disadvantages Summary

1. **Memory consumption**: Packrat memoization scales with input size × rule count, not parse depth
2. **Left recursion**: Traditional packrat parsers cannot handle left recursion; workarounds lose linear-time guarantees
3. **Ordered choice pitfalls**: Subsumed alternatives and hidden effects through rule levels can create subtle bugs
4. **Undecidable emptiness**: Cannot algorithmically determine if a PEG matches any strings (reduction from Post correspondence problem)
5. **No inherent error location**: On total failure, the parser does not know where the error is
6. **Midpoint problem**: Greedy matching may miss globally optimal parses for certain nondeterministic CFG rules
7. **Flat parse trees**: Idiomatic repetition form `A (op A)*` produces flat lists, not binary trees — associativity must be imposed post-parse
8. **Not all CFG languages expressible**: Conjectured that some context-free languages cannot be expressed as PEGs
9. **Eager matching**: Parser accepts first successful match even if it causes failure later (no global backtracking)
