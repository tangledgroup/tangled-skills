# Practical Implementations

## Contents
- CPython pegen (PEP 617)
- DuckDB Runtime-Extensible Parser
- LPeg (Lua)
- PeppaPEG (ANSI C)
- peg/leg (Ian Piumarta)
- Guile `(ice-9 peg)` Module
- LL(1) Workarounds Eliminated by PEG

## CPython pegen (PEP 617)

CPython replaced its LL(1) parser with a PEG-based parser starting in Python 3.9 (alternative), becoming the default from Python 3.10. The parser generator is called **pegen** (PEG engine).

### Grammar syntax

```
file_input:
    (ENDMARKER / stmt)+

stmt:
    simple_stmt
    / compound_stmt

simple_stmt:
    small_stmt (';' small_stmt)* NEWLINE
```

### Complete operator reference

| Syntax | Meaning |
|--------|---------|
| `e1 e2` | Match e1, then match e2 |
| `e1 \| e2` | Match e1 or e2 (ordered choice) |
| `(e)` | Grouping |
| `[e]` or `e?` | Optionally match e |
| `e*` | Zero or more occurrences of e |
| `e+` | One or more occurrences of e |
| `s.e+` | One or more e separated by s (gather) |
| `&e` | Succeed if e parses, consume nothing (positive lookahead) |
| `!e` | Fail if e parses, consume nothing (negative lookahead) |
| `~` | Commit to current alternative (cut) |
| `name=e` | Named capture — bind result to name for use in actions |

### Key features

- **Selective memoization**: Disabled by default. Opt-in via `(memo)` marker:
  ```
  expr_list[type] (memo):
      expr (',' expr)* ','?
  ```
  Left-recursive rules always use memoization internally.

- **Hard vs soft keywords**: Single quotes for hard (`'class'`), double quotes for soft (`"match"`). Soft keywords allow `match = 42` as valid identifier usage.

- **Grammar actions**: Code blocks after rule matches:
  ```
  power[expr_ty]: a=primary '**' b=power #{ binop(a, b, '#') #}
  ```
  Named captures via `name=` prefix. Actions generate C code in the output parser.

- **Error handling**: Two-pass parsing with `invalid_` rules for specialized error messages. Rules starting with `invalid_` are excluded from first pass and only active on retry.

- **Separate tokenizer**: Python's tokenizer handles indentation tracking (requires a stack), encoding, interactive mode, f-string nesting, and backtracking errors. Produces token stream consumed via `mark()`/`reset()` for backtracking.

- **Left recursion**: Supported via Ford/Warth iterative fixed-point algorithm. Handles direct, indirect, and hidden left recursion.

### Rationale for PEG over LL(1)

- **Some rules are not actually LL(1):** Assignment vs expression disambiguation requires unlimited lookahead. Old workaround:
  ```
  # Old LL(1) workaround — accepts invalid programs, checked later
  namedexpr_test: test [':=' test]
  ```
  PEG allows the natural form: `[NAME ':='] test`. Similarly, `with ( ... )` continuation across lines was impossible in LL(1) since first sets of context managers include `(`.
- **Complex AST construction:** Old parser had huge coupling between AST generation and parse tree shape. Code inspected child node counts to deduce which grammar alternative produced them.
- **No left recursion support:** Required awkward grammar rewrites producing flat parse trees needing post-processing.
- **Intermediate parse tree (CST):** bpo-26415 showed excessive peak memory from keeping CST in memory. PEG constructs AST directly, eliminating the intermediate step.

### Performance

Tuned to within 10% of the old LL(1) parser in speed and memory. For compiling stdlib: new parser is slightly faster but uses ~10% more memory. The elimination of intermediate CST partially offsets packrat memoization overhead.

## DuckDB Runtime-Extensible Parser

DuckDB v1.5 (March 2026) shipped an experimental PEG parser, opt-in via `CALL enable_peg_parser()`.

### Design goals

- **Runtime grammar loading**: Load/modify grammar at runtime without recompilation
- **Plugin syntax extensions**: Extensions can add new SQL dialect features
- **Dialect switching**: Support multiple SQL variants in one instance
- **Wasm-friendly**: Avoid baking all grammar into binary

### Implementation

- Uses **cpp-peglib** (single-header C++17 PEG engine) as the execution backend
- Grammar load time: ~3ms from text representation — matters for short-lived instances (Wasm, DuckDB lives for milliseconds)
- Parsing performance: ~10x slower than YACC baseline (YACC 0.03ms vs cpp-peglib 0.3ms for TPC-H Query 1), but sub-ms absolute — acceptable since parsing is a tiny fraction of query processing
- cpp-peglib makes heavy use of recursive function calls — optimization opportunity via loop abstraction
- Grammar syntax uses `/` for choice (cpp-peglib convention), `?` for optional, `*` for repetition

### Grammar macros and features

- `Parens(D)` — shorthand for `'(' D ')'`
- `List(D)` — shorthand for `D (',' D)*`
- `%whitespace` rule handles tokenization
- `%recover(Name)` — recovery annotation for custom error messages
- `i"keyword"` — case-insensitive keyword matching

### Example grammar (abridged)

```
Statements <- SingleStmt (';' SingleStmt )* ';'*
SingleStmt <- SelectStmt
SelectStmt <- SimpleSelect (SetopClause SimpleSelect)*
SimpleSelect <- WithClause? SelectClause FromClause?
    WhereClause? GroupByClause? HavingClause?
    OrderByClause? LimitClause?
FromClause <- 'FROM' TableReference ((',' TableReference) / ExplicitJoin)*
```

### Runtime extension examples

**Adding UNPIVOT statement:**
```
UnpivotStatement <- 'UNPIVOT' Identifier
    'ON' Parens(List(Identifier) / '*')
SingleStmt <- SelectStatement / UnpivotStatement
```

**Adding SQL/PGQ GRAPH_TABLE:**
```
PropertyGraphReference <- 'GRAPH_TABLE'i '('
        Identifier ','
        'MATCH'i List(Pattern)
        'COLUMNS'i Parens(List(ColumnReference))
    ')' Identifier?
TableReference <- PropertyGraphReference / ...
```

**Adding dplyr syntax:**
```
DplyrStatement <- Identifier Pipe Verb (Pipe Verb)*
Verb <- VerbName Parens(List(Argument))
Pipe <- '%>%'
SingleStmt <- SelectStatement / DplyrStatement
```

### Error handling advantages over YACC

YACC-style parsers exhibit "all-or-nothing" behavior: the entire query either parses or doesn't. PEG with `%recover` annotations can show multiple errors and provide context-specific messages, addressing one of the most-reported support issues in database systems.

## LPeg (Lua)

Created by Roberto Ierusalimschy (Lua author). PEG-based pattern matching library that replaces regex in Lua.

### Architecture

- **Parser combinator model:** Patterns are first-class Lua values composable with operators (`*` for sequence, `+` for choice, `^` for repetition). This differs from text-based PEG grammars — patterns are constructed programmatically.
- Compiles PEG patterns to efficient bytecode (not interpreted at runtime)
- `re` module provides regex-like syntax on top of LPeg internals
- Memoization via decorator pattern: any parser can be wrapped with memoization without modifying its implementation

### Parser combinator API

```lua
local lpeg = require "lpeg"

-- Character classes
local Cn = lpeg.R"09"^1          -- digits (one or more)
local Cl = lpeg.R"az"            -- lowercase letter

-- Sequence and choice
local Number = Cn
local Ident = Cl * (Cl + Cn)^0

-- And-predicate (lookahead)
local NotSpace = lpeg.P" " ^ -1  -- succeed if not space

-- Captures (extract matched text)
local Capture = lpeg.C(Ident)    -- capture identifier

-- Rule references (for recursion)
local V = lpeg.V                 -- reference to named rule

-- Pattern table for recursive grammars
local grammar = lpeg.P {
    "expression";
    expression = lpeg.V("term") * (lpeg.P"+" * lpeg.V("term"))^0;
    term = lpeg.R"09"^1;
}
```

### Strengths

- Extremely fast (compiled patterns, not interpreted)
- Integrates naturally with Lua's pattern matching
- Used in production for parsing JSON, XML, and custom DSLs in Lua applications
- No separate tokenizer needed — patterns operate directly on strings

## PeppaPEG (ANSI C)

Ultra-lightweight PEG parser in ANSI C. Single header (`peppa.h`) + source file (`peppa.c`).

### Features

- Built-in grammars: JSON, TOML v1.0, Lua v5.3, Go v1.17, HCL2, ABNF (RFC 5234)
- CLI tool `peppa` for grammar development and testing
- Annotations for tree control

### Grammar syntax

```
@lifted entry = &. value !.;
@lifted value = object / array / string / number / true / false / null;
object = "{" (item ("," item)*)? "}";
item = string ":" value;
array = "[" (value ("," value)*)? "]";
@tight string = "\"" ([\u0020-\u0021] / [\u0023-\u005b] / [\u005d-\U0010ffff] / escape )* "\"";
@squashed @tight number = minus? integral fractional? exponent?;
@tight @squashed @lifted escape = "\\" ("\"" / "/" / "\\" / "b" / "f" / "n" / "r" / "t" / unicode);
@tight @squashed unicode = "u" ([0-9] / [a-f] / [A-F]){4};
@spaced @lifted whitespace = " " / "\r" / "\n" / "\t";
```

### Annotations

- `@tight`: Remove intermediate nodes from the parse tree
- `@squashed`: Flatten nested groups (merge sequential matches into single node)
- `@lifted`: Promote child to parent level (skip wrapper node)
- `@spaced`: Handle whitespace around rule automatically

### Special syntax

- `i"keyword"` — case-insensitive keyword matching
- `{n}` — exact repetition (e.g., `[0-9]{4}` matches exactly 4 digits)
- `;` terminates rules (vs `.` in some other PEG variants)

### Build

CMake-based. Can be used as a library (`pkg-config --cflags --libs libpeppa`) or by copying header/source into project. Uses Unity testing framework and Valgrind for memory leak detection.

### Performance optimization

Callgrind profiling revealed that functions like `P4_NeedLoosen`, `P4_IsTight`, `P4_IsScoped`, `P4_NeedSquash`, and `P4_IsSquashed` were called excessively during parsing. Removing these inline checks and pre-computing values yielded a **10x speedup**. Doxygen is used for documentation extraction from source code.

### C API

```c
P4_Grammar* grammar = P4_LoadGrammar("entry = ...");
P4_Source* source = P4_CreateSource("[1,2,3]", "entry");
P4_Parse(grammar, source);
P4_Node* root = P4_GetSourceAST(source);
P4_JsonifySourceAst(stdout, root, NULL);
```

## peg/leg (Ian Piumarta)

Two recursive-descent parser generators producing C code from PEG grammars.

### peg

Processes PEGs using Ford's original syntax. Generates a C program that recognizes sentences of the grammar. MIT licensed, unencumbered generated parsers.

### leg

Alternative syntax intended as a `lex`/`yacc` replacement:
- Familiar conventions for developers coming from lex/yacc
- Supports unlimited backtracking and ordered choice
- Combines scanning and parsing in one pass

### Features

- Semantic actions via `{...}` blocks with access to `yytext`
- Inline actions via `@{...}` executed **during** matching (not after)
- Error actions via `~` operator
- Reentrant parsing through `yyparsefrom_r()`
- `#line` directives for error reporting (disable with `-P`)

### Version history

Latest release 0.1.20 (2019). Active maintenance with incremental feature additions: semantic values, reentrant parsing, UTF-8 support, C++ compatibility.

## Guile `(ice-9 peg)` Module

Guile Scheme's PEG module compiles grammars to lambda expressions.

### Compilation modes

- **Compile-time**: `define-peg-pattern` and `define-peg-string-patterns` macros
- **Runtime**: `compile-peg-pattern` and `peg-string-compile` functions

### API

```scheme
(use-modules (ice-9 peg))

(define-peg-pattern my-pattern "rule1 / rule2")
(match-pattern my-pattern "input string")
(search-for-pattern my-pattern "longer text")
```

### Design

- **Compiles to Scheme lambdas:** Unlike most PEG implementations that produce bytecode or C code, Guile's `(ice-9 peg)` compiles grammars directly to lambda expressions. These are first-class Scheme values that can be inspected, modified, and composed.
- Superset of standard PEG syntax for controlling preserved information — the extended syntax lets you specify which matched subexpressions should be retained in the result (useful for extracting specific parts without building full parse trees)
- Supports both matching (regex-like) and full parsing (tree-building)
- Documented with syntax reference, API reference, tutorial, and internals guide
