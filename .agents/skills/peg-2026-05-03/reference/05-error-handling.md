# Error Handling and Actions

## Contents
- The Error Location Problem
- Two-Pass Approach (pegen)
- Recovery Annotations
- Exception-Based Error Reporting
- Semantic Actions
- YACC "All-or-Nothing" Behavior

## The Error Location Problem

When PEG parsing fails completely (no rule succeeds in consuming all input), the parser does not inherently know **where** the error is. Every position was tried, and every attempt ultimately failed.

This contrasts with LR parsers, which can report the position where they got stuck. In PEG, the backtracking nature means the parser explores many paths before concluding failure, losing the original error location.

**YACC-style parsers exhibit "all-or-nothing" behavior:** the entire query either parses or doesn't. This is why queries with typos (e.g., `SELEXT` instead of `SELECT`) are harshly rejected. MySQL's error messages are notoriously unhelpful:
```
You have an error in your SQL syntax; check the manual that corresponds
to your MySQL server version for the correct syntax to use near 'SELEXT'
at line 1.
```
PEG parsers with recovery annotations can provide better context-specific messages.

## Two-Pass Approach (pegen)

CPython's pegen uses a two-pass strategy:

1. **First pass**: Parse without `invalid_` rules. Record failure position.
2. **Second pass**: If first pass failed, retry with `invalid_` rules enabled. These rules match common error patterns and produce specific error messages.
3. If second pass also fails generically, use the first pass's failure location.

```
# Invalid rule — only active in second pass
invalid_for_loop_statement ← 'for' !NAME
    { raise SyntaxError("expected target after 'for'") }
```

Rules starting with `invalid_` are excluded from the first parsing pass. The order of alternatives involving `invalid_` rules matters (like any rule in PEG).

## Recovery Annotations

Research papers and practical implementations describe annotating rules with recovery actions that:
1. Show multiple errors in a single parse attempt
2. Provide context-specific error messages
3. Allow parsing to continue past errors for IDE support

### DuckDB %recover pattern

DuckDB's cpp-peglib implementation uses `%recover` to match error patterns and produce custom messages:

```
OrderByClause ← 'ORDER'i 'BY'i List(OrderByExpression)
    %recover(WrongGroupBy)?
WrongGroupBy ← GroupByClause
    { error_message "GROUP BY must precede ORDER BY" }
```

When a user writes `ORDER BY` before `GROUP BY`, the parser matches the misplaced clause and reports a helpful message instead of a generic syntax error.

### Error recovery in pegen

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

## Exception-Based Error Reporting

Tokenizer errors are normally reported by raising exceptions. Some special tokenizer errors (e.g., unclosed parentheses) are reported only after the parser finishes without returning anything.

When the parser detects that an exception is raised during a grammar action, it automatically stops parsing, unwinds the stack, and reports the exception regardless of current parser state.

## Semantic Actions

Semantic actions are code executed during or after rule matching, used to build ASTs, validate content, or compute derived values.

### Grammar actions (pegen)

Code blocks executed after rule match. Two syntax modes:

**C mode:** Actions use `#{...}#` delimiters, generating C code:
```
power[expr_ty]: a=primary '**' b=power #{ binop(a, b, '#') #}
       / primary
```

**Python mode:** Actions use `{...}` delimiters, generating Python code:
```
expr: expr '+' term { ast.BinOp(expr, ast.Add(), term) }
```

Named captures via `name=` prefix bind subexpression results for use in actions. Actions generate code in the output parser.

**Return behavior:**
- If an action is omitted in C mode and there's a single name in the alternative, it gets returned automatically
- If no action and no single name, a dummy object is returned (avoid this case)
- In Python mode, omitting an action returns a list of all parsed expressions (meant for debugging)

### Inline actions (peg/leg)

Code embedded directly in the grammar, executed **during** matching (not after):

```
# peg/leg syntax — @{...} executes during matching
number ← [0-9]+ @{ return atoi(yytext); }
```

The `yytext` variable holds the matched text. Inline actions differ from post-match actions: they execute as the rule matches, not after the full rule succeeds.

### Error actions (peg/leg)

The `~` operator in peg/leg triggers error actions when the preceding expression fails:

```
# Report error if expected token is missing
statement ← expr ~ { yyerror("expected expression") }
```

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

### Pegen return behavior

If an action is omitted in C mode:
1. If there's a single name in the alternative, it gets returned
2. If not, a dummy object is returned (this case should be avoided)

In Python mode, omitting an action returns a list of all parsed expressions (meant for debugging).
