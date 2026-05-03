# Parsing Algorithms

## Contents
- Recursive Descent Parsing
- Packrat Parsing
- Selective Memoization
- Tokenizer Integration

## Recursive Descent Parsing

The most direct PEG implementation maps each nonterminal to a function. Each function takes an input position and returns success/failure plus the number of consumed characters.

**Core model:**
```python
def rule_name(position):
    # Try first alternative
    result = try_alternative_1(position)
    if result.success:
        return result
    # First failed, try second (ordered choice semantics)
    result = try_alternative_2(position)
    return result
```

**Key properties:**
- Each grammar rule → one function
- Failure ≠ error — means "try next alternative"
- On failure, no input is consumed (backtrack to calling position)
- Sequence: call first sub-rule, then second on remainder
- Choice: try first, if fails try second from same position
- Predicates: call sub-rule, discard result, return success/fail without advancing

**Naive recursive descent has exponential worst case.** The unlimited lookahead capability means the parser may explore an exponential number of paths. For a grammar with L precedence levels and P operators, parsing a single token can require O((P+1)^L) expression invocations.

## Packrat Parsing

Packrat parsing eliminates exponential behavior through **memoization** of `(rule_name, input_position)` → `result`. Before executing a rule at a position, check the memo table. If cached, return immediately. Otherwise, compute and store.

**Memo table structure:**
```
memo[rule_id][position] = (success, consumed_length, result_data)
```

**Algorithm:**
1. At rule invocation, check `memo[rule][position]`
2. If hit: return cached result
3. If miss: execute rule body, store result in memo, return

**Complexity guarantees:**
- **Time**: O(n × r) where n = input length, r = number of rules. Each rule executes at most once per position.
- **Space**: O(n × r) for the memo table. Proportional to total input size, not parse tree depth.
- **Amortized constant access**: Requires hash table or direct addressing for memo lookups.

**Memory tradeoff:** Packrat parsers use more memory than LR/LL parsers (which scale with parse depth), but queries and source code typically have bounded nesting depth in practice, making the difference manageable.

## Selective Memoization

Full memoization has overhead: cache lookup costs time even when reparsing would be faster. The **pegen** approach (used by CPython) disables memoization by default and requires explicit opt-in:

```
rule_name[type] (memo):
    ...
```

Only rules marked with `(memo)` use the cache. Left-recursive rules always use memoization internally since the left-recursion implementation depends on it.

**When to enable memoization:**
- Rules that are called from many different contexts
- Rules involved in complex backtracking paths
- Rules where recomputation is expensive relative to cache lookup

**How to determine:** Benchmark with and without memoization on representative inputs. Compare execution time and memory usage.

## Tokenizer Integration

PEG parsers support two approaches to tokenization:

### Separate tokenizer (traditional)

A tokenizer runs before the parser, producing a stream of tokens. The parser operates on tokens rather than raw characters.

**Benefits:**
- Complex indentation tracking (Python requires a stack)
- Encoding handling and interactive mode
- Existing well-tested tokenizers can be reused
- Tokenizer errors reported before parser sees bad input

**Tokenizer API requirements for PEG backtracking:**
```python
class Tokenizer:
    def mark(self):          # Save current position
        return self.pos

    def reset(self, pos):    # Restore to saved position
        self.pos = pos

    def get_token(self):     # Advance and return next token
        token = self.peek_token()
        self.pos += 1
        return token

    def peek_token(self):    # Return next token without advancing
        ...
```

**Lazy tokenization:** Tokenize on demand rather than eagerly consuming all input. This ensures syntax errors are reported before distant tokenizer errors (e.g., unclosed string at end of file).

### Unified grammar (scannerless)

The PEG handles both lexical and syntactic rules in a single grammar. No separate tokenizer phase.

**Benefits:**
- Per-region lexing: different tokenization rules for embedded languages
- Nested constructs handled naturally (e.g., nested comments `(* (* inner *) outer *)`)
- No lexer hack needed for context-sensitive tokenization
- Whitespace can be attached to preceding or following tokens

**Whitespace integration strategies:**
1. Attach to preceding token: each token rule ends with `Spacing`
2. Attach to following token: each token rule starts with `Spacing`
3. Explicit at strategic points: reference `Spacing` only where needed

Ford's self-describing PEG uses approach 1 — each lexical token definition consumes trailing whitespace and comments via a `Spacing` nonterminal.
