# Grammar Design Patterns

## Contents
- Ordered Choice Consequences
- Whitespace Handling Strategies
- Soft vs Hard Keywords
- Error Handling and Recovery
- Semantic Actions

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

This is the PEG solution to the **dangling else** problem that plagues CFGs. In a CFG, `if-then` and `if-then-else` create ambiguity. In PEG, ordering resolves it deterministically.

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
# Because 'a'|'aa' greedily matches first 'a', then final 'a' consumes second,
# leaving third 'a' unmatched. Parser does NOT backtrack to try 'aa'.
Rule ← ('a' | 'aa') 'a'
```

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

**Pitfalls:** Soft keywords can be accepted in unintended positions due to ordered choice. Define them where few alternatives compete.

## Error Handling and Recovery

### The error location problem

When PEG parsing fails completely (no rule succeeds in consuming all input), the parser does not inherently know **where** the error is. Every position was tried, and every attempt ultimately failed.

### Two-pass approach (pegen)

CPython's pegen uses a two-pass strategy:

1. **First pass**: Parse without `invalid_` rules. Record failure position.
2. **Second pass**: If first pass failed, retry with `invalid_` rules enabled. These rules match common error patterns and produce specific error messages.
3. If second pass also fails generically, use the first pass's failure location.

```
# Invalid rule — only active in second pass
invalid_for_loop_statement ← 'for' !NAME
    { raise SyntaxError("expected target after 'for'") }
```

Rules starting with `invalid_` are excluded from the first parsing pass.

### Exception-based error reporting

In pegen, if a rule action raises an exception (including `SyntaxError`), parsing stops immediately and the exception propagates. This allows custom error messages:

```
# Grammar action that validates parsed content
type_expr ← '(' NAME ')'
    {
        if not is_valid_type(name):
            raise SyntaxError(f"'{name}' is not a valid type")
        return TypeNode(name)
    }
```

### Recovery annotations

Research papers describe annotating rules with recovery actions that:
1. Show multiple errors in a single parse attempt
2. Provide context-specific error messages
3. Allow parsing to continue past errors for IDE support

## Semantic Actions

Semantic actions are code executed during or after rule matching, used to build ASTs, validate content, or compute derived values.

### Inline actions (peg/leg)

Code embedded directly in the grammar:

```
# peg/leg syntax — @{...} executes during matching
number ← [0-9]+ @{ return atoi(yytext); }
```

### Grammar actions (pegen)

C function calls after rule match, referenced by `#` prefix:

```
# pegen grammar syntax
power ← a=primary '**' b=power #{ binop(a, b, '#') #}
       / primary
```

The `a=` and `b=` capture named results. The `#{...}#` block calls the generated C function.

### Separation of concerns

Best practice: keep grammar rules focused on structure, move complex logic to action functions:

```
# Grammar defines structure
expr ← left=term op=add_op right=expr #{ make_binop(left, op, right) #}
     / term

# Action builds AST node
make_binop(left, op, right):
    return BinOpNode(op=op, left=left, right=right)
```
