# Source Comparisons

## Contents
- Norvig (lispy.html)
- ByteGoblin (16 Lines)
- Spatters (GitHub Gist)
- Zstix (Blog Tutorial)
- AlJamal (Homoiconic Python)
- Misfra.me (Mini Lisp in Go)
- Design Tradeoffs

## Norvig (lispy.html)

**Approach**: Full Scheme subset interpreter. The gold standard for minimal Lisp interpreters.

**Structure**: ~120 lines, organized into sections: types, parsing, environments, interaction (REPL), procedures, eval.

**Key features**:
- Tokenize by space-around-parens + `.split()`
- Recursive `read_from_tokens` parser with error handling
- `Env(dict)` subclass with `outer` chain and `find()` for lexical scoping
- `Procedure` class capturing `(parms, body, env)`
- 6 special forms: quote, if, define, set!, lambda, procedure-call
- Rich standard_env: math module functions + arithmetic operators + list primitives (car, cdr, cons, map, etc.)
- REPL with `lispstr()` for S-expression output formatting

**Strengths**: Clean architecture, well-documented, production-quality minimal interpreter. Lexical scoping via Env chain is elegant.

**Limitations**: No strings, no booleans (uses truthiness), no comments, no tail-call optimization, no call/cc, no cond/let derived forms.

## ByteGoblin (16 Lines)

**Approach**: Ultra-minimal proof of concept showing the core eval-apply idea in 16 lines.

**Structure**: Single `lisp()` function with nested `parse()` and `eval_ast()`.

**Key features**:
- Tokenize by space-around-parens + `.split()`
- Parse strips outer parentheses only (no recursive parsing)
- eval_ast handles 'add' and 'sub' operations recursively
- No variables, no functions, no conditionals, no environment

**Strengths**: Demonstrates that the core idea of "parse then evaluate nested expressions" is trivially simple. Good pedagogical starting point.

**Limitations**: Functionally minimal — only handles arithmetic on two operands with no nesting support beyond one level (parse just strips parens). No language features beyond add/sub. Not a real interpreter.

## Spatters (GitHub Gist)

**Approach**: Class-based type system with proper error handling. Foundation for a type-safe Lisp.

**Structure**: Custom Lisp types (LispString, LispSymbol, LispInt, LispFloat), parse_list recursive parser, REPL with input counting.

**Key features**:
- Type classes: `LispString(str)`, `LispSymbol(str)`, `LispInt(int)`, `LispFloat(float)`
- `LispSyntaxError` exception for parse errors
- Recursive `parse_list` that validates parentheses matching
- REPL with numbered input/output (`In [0]:` / `Out [0]:`)
- String support via double-quote parsing

**Strengths**: Type distinction between symbols and strings. Good error messages. Clean separation of concerns.

**Limitations**: Only has `+` as builtin. No functions, no conditionals, no environment (lisp_eval returns expression unchanged). Incomplete interpreter.

## Zstix (Blog Tutorial)

**Approach**: Step-by-step tutorial building a Turing-complete language from scratch.

**Structure**: ~150 lines, built incrementally: lexer → parser → eval → def → builtins → if → do → fn.

**Key features**:
- Regex-based lexer: `re.findall(r"[()]|[^() \n]+", s)`
- Recursive parser with number conversion (int only)
- Built-in functions as Python lambdas in global_env dict
- Custom `Function` dataclass for user-defined functions
- `new_env(parent_env, params, args)` creates scope chain via `:parent` key
- `get_var(key, env)` recursive scope lookup
- Keywords (`:true`, `:false`) instead of booleans
- Special forms: def, if, do, fn
- Test harness with `test(s, expected)` function

**Strengths**: Excellent pedagogical progression. Shows how each feature builds on previous ones. The Function dataclass + :parent scope chain is a clean alternative to Env subclassing.

**Limitations**: Integer-only (no floats), keywords instead of proper booleans, limited builtins, no strings, no set!, no quote, no lexical scoping closure capture (env passed at call time not definition time — actually this is dynamic scoping in their implementation).

## AlJamal (Homoiconic Python)

**Approach**: Direct translation of McCarthy's original "Lisp in Lisp" from the 1960 Lisp 1.5 manual into Python.

**Structure**: No parser — uses Python lists directly as S-expressions. Implements McCarthy's eval with primitive list operations.

**Key features**:
- M-expression to Python mapping: `lambda` → Python lambda, `cond` → if/elif chain
- S-expressions represented as Python lists
- Primitives: `atom(x)`, `eq(x,y)`, `car(x)`, `cdr(x)`, `cons(x,y)`, `append(x,y)`
- `assoc(x, a)` for key lookup in association lists
- `pairlis(x, y)` for creating parameter bindings (like zip)
- Dynamic scoping via environment as association list
- Special forms: ATOM, EQ, CAR, CDR, CONS, APPEND, LABEL, LAMBDA, COND

**Strengths**: Historically significant — closest to the original Lisp 1.5 implementation. Demonstrates homoiconicity perfectly (code is data). No parser needed when using Python lists as S-expressions directly.

**Limitations**: Dynamic scoping (not lexical). Association list environments are O(n) lookup vs O(1) for dicts. No modern conveniences (no strings, no numbers beyond what you pass in). The approach is more academic than practical.

## Misfra.me (Mini Lisp in Go)

**Approach**: Go implementation inspired by Norvig + mal guide, with advanced features.

**Structure**: ~400 lines of Go, file-based execution.

**Key features**:
- Standard Lisp features: define, lambda, if, arithmetic, comparison
- Tail-call optimization (from Norvig's lispy2)
- call/cc simplified as `catch!` / `throw` for exception-like control flow
- File execution with shebang support (`#!/usr/bin/env mini-lisp`)
- String support with `str` builtin

**Strengths**: Shows advanced features beyond basic interpreters. Tail-call optimization enables infinite recursion. call/cc demonstrates continuation-based control flow.

**Limitations**: Go implementation (not Python). call/cc is simplified, not full. No REPL shown in detail.

## Design Tradeoffs

**Tokenization**: Space-around-parens split (Norvig) vs regex (Zstix). Space-split is simpler but regex handles comments and whitespace more robustly.

**Environment model**: Dict subclass with outer chain (Norvig) vs dict with :parent key (Zstix) vs association list (AlJamal). Dict subclass gives O(1) lookup + clean inheritance. Association lists are historically authentic but slower.

**Scoping**: Lexical (Norvig, our design) vs dynamic (AlJamal's original Lisp approach). Lexical scoping captures the environment where a function is defined, not where it's called. This is the modern standard and enables proper closures.

**Boolean representation**: Python bool (our design) vs keywords `:true`/`:false` (Zstix) vs truthiness (Norvig). Using Python bool with `#t`/`#f` in output gives clean semantics.

**Parserless approach** (AlJamal): Eliminates parsing entirely by using host language data structures. Great for understanding homoiconicity but not practical for a real interpreter that reads text input.
