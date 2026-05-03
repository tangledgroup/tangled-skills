# Practical Implementations

## Contents
- CPython pegen (PEP 617)
- DuckDB Runtime-Extensible Parser
- LPeg (Lua)
- PeppaPEG (ANSI C)
- peg/leg (Ian Piumarta)
- Guile `(ice-9 peg)` Module

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

compound_stmt:
    if_stmt
    / while_stmt
    / for_stmt
    / try_stmt
    / with_stmt
    / funcdef
    / classdef
```

### Key features

- **Selective memoization**: Disabled by default. Opt-in via `(memo)` marker after rule name:
  ```
  expr_list[type] (memo):
      expr (',' expr)* ','?
  ```
  Left-recursive rules always use memoization internally.

- **Hard vs soft keywords**: Single quotes for hard (`'class'`), double quotes for soft (`"match"`). Soft keywords allow `match = 42` as valid identifier usage.

- **Grammar actions**: C function calls after rule matches:
  ```
  power: a=primary '**' b=power #{ binop(a, b, '#') #}
  ```
  Named captures via `name=` prefix. Actions generate C code in the output parser.

- **Error handling**: Two-pass parsing with `invalid_` rules for specialized error messages. Rules starting with `invalid_` are excluded from first pass and only active on retry.

- **Separate tokenizer**: Python's tokenizer handles indentation tracking (requires a stack), encoding, interactive mode, f-string nesting, and backtracking errors (unclosed parentheses). The tokenizer produces a token stream that the parser consumes via `mark()`/`reset()` for backtracking.

- **Left recursion**: Supported via Ford/Warth iterative fixed-point algorithm. Rules like `expr: expr '+' term` work directly.

### Rationale for PEG over LL(1)

- Some Python rules are not actually LL(1) (e.g., assignment vs expression disambiguation requires unlimited lookahead)
- Complex AST construction scattered across grammar rules
- No left recursion support in LL(1), requiring awkward grammar rewrites
- Intermediate parse tree (CST) adds memory overhead before AST conversion

## DuckDB Runtime-Extensible Parser

DuckDB v1.5 (March 2026) shipped an experimental PEG parser, opt-in via `CALL enable_peg_parser()`.

### Design goals

- **Runtime grammar loading**: Load/modify grammar at runtime without recompilation
- **Plugin syntax extensions**: Extensions can add new SQL dialect features
- **Dialect switching**: Support multiple SQL variants in one instance
- **Wasm-friendly**: Avoid baking all grammar into binary

### Implementation

- Uses **cpp-peglib** (single-header C++17 PEG engine) as the execution backend
- Grammar load time: ~3ms from text representation
- Parsing performance: ~10x slower than YACC baseline on TPC-H queries
- Grammar syntax uses `/` for choice (cpp-peglib convention), `?` for optional, `*` for repetition

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

Special rules `Parens(D)` and `List(D)` are grammar macros. `%whitespace` rule handles tokenization.

## LPeg (Lua)

Created by Roberto Ierusalimschy (Lua author). PEG-based pattern matching library that replaces regex in Lua.

### Architecture

- Compiles PEG patterns to efficient bytecode (not interpreted at runtime)
- Parser combinators style: patterns are first-class values composable with operators
- `re` module provides regex-like syntax on top of LPeg internals

### Usage pattern

```lua
local lpeg = require "lpeg"

-- Character classes
local Cn = lpeg.R"09"^1          -- digits
local Cl = lpeg.R"az"            -- lowercase letter

-- Sequence and choice
local Number = Cn
local Ident = Cl * (Cl + Cn)^0

-- And-predicate (lookahead)
local NotSpace = lpeg.P" " ^ -1  -- succeed if not space
```

### Strengths

- Extremely fast (compiled patterns, not interpreted)
- Integrates naturally with Lua's pattern matching
- Used in production for parsing JSON, XML, and custom DSLs in Lua applications

## PeppaPEG (ANSI C)

Ultra-lightweight PEG parser in ANSI C. Single header (`peppa.h`) + source file (`peppa.c`).

### Features

- Built-in grammars: JSON, TOML v1.0, Lua v5.3, Go v1.17, HCL2, ABNF (RFC 5234)
- CLI tool `peppa` for grammar development and testing
- Annotations for tree control:
  - `@tight`: Remove intermediate nodes
  - `@squashed`: Flatten nested groups
  - `@lifted`: Promote child to parent level
  - `@spaced`: Handle whitespace around rule

### Example grammar (JSON)

```
@lifted entry = &. value !.;
@lifted value = object / array / string / number / true / false / null;
object = "{" (item ("," item)*)? "}";
item = string ":" value;
array = "[" (value ("," value)*)? "]";
@tight string = "\"" ([\u0020-\u0021] / [\u0023-\u005b] / [\u005d-\U0010ffff] / escape )* "\"";
@squashed @tight number = minus? integral fractional? exponent?;
```

### Build

CMake-based. Can be used as a library (`pkg-config --cflags --libs libpeppa`) or by copying header/source into project. Uses Unity testing framework and Valgrind for memory leak detection.

## peg/leg (Ian Piumarta)

Two recursive-descent parser generators producing C code from PEG grammars.

### peg

Processes PEGs using Ford's original syntax. Generates a C program that recognizes sentences of the grammar.

### leg

Alternative syntax intended as a `lex`/`yacc` replacement:
- Familiar conventions for developers coming from lex/yacc
- Supports unlimited backtracking and ordered choice
- Combines scanning and parsing in one pass

### Features

- Semantic actions via `{...}` blocks with access to `yytext`
- Inline variables in actions
- Error actions via `~` operator
- Reentrant parsing through `yyparsefrom_r()`
- `#line` directives for error reporting (disable with `-P`)
- MIT licensed, unencumbered generated parsers

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

- Superset of standard PEG syntax for controlling preserved information
- Compiles to Scheme lambdas (not bytecode or C)
- Supports both matching (regex-like) and full parsing (tree-building)
- Documented with syntax reference, API reference, tutorial, and internals guide
