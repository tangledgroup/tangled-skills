---
name: s-expression
description: S-expressions (symbolic expressions) are a minimal notation for nested tree-structured data using atoms and lists. Invented for Lisp, they represent both code and data with the same syntax (homoiconicity). Covers function definitions, lambda forms, calling conventions, and result binding across Lisp-family languages. Use when working with Lisp-family languages, designing domain-specific languages, building parsers, representing abstract syntax trees, or serializing hierarchical data in a portable format.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - s-expression
  - sexp
  - lisp
  - data-format
  - tree
  - homoiconic
  - notation
category: language-concept
external_references:
  - https://en.wikipedia.org/wiki/S-expression
  - https://github.com/s-expressions/pose
  - https://uwplse.org/2025/12/09/S-expressions.html
  - https://lisp-lang.org/learn/functions
  - https://www.gnu.org/software/emacs/manual/html_node/eintr/lambda.html
  - https://clojure.org/guides/learn/functions
  - https://standards.scheme.org/corrected-r7rs/r7rs-Z-H-6.html#TAG:__tex2page_chap_4
---

# S-expressions

## Overview

An **S-expression** (symbolic expression, abbreviated sexp or sexpr) is a notation for representing nested, tree-structured data. Invented by John McCarthy in 1960 for Lisp, it remains one of the simplest and most powerful data representations in computer science.

The entire system rests on two rules:

1. An **atom** — a single, indivisible value (symbol, string, or number)
2. A **list** — a parenthesized sequence of S-expressions

Every S-expression is either an atom or a list of S-expressions. This recursive definition means any finite tree can be represented exactly.

```lisp
(+ 1 (* 2 3))
```

This expression contains atoms (`+`, `*`, `1`, `2`, `3`) and nested lists. As data it is a tree. As Lisp code it computes `7`. The same syntax represents both — this property is called **homoiconicity**.

## When to Use

- Reading or writing data in Lisp-family languages (Common Lisp, Scheme, Clojure, Racket, Emacs Lisp)
- Designing domain-specific languages where code and data share representation
- Building parsers — S-expressions eliminate the need for complex grammar definitions
- Representing abstract syntax trees (ASTs) in human-readable text format
- Serializing hierarchical data portably across language boundaries (POSE format)
- Understanding function definition, lambda forms, and calling conventions in Lisp-family languages

## Core Concepts

### The Two Rules

```
S-expression := atom | list
atom         := symbol | string | number
list         := ( S-expression* )
```

An **atom** is a leaf node. A **list** is an internal node containing zero or more child S-expressions. Lists can contain atoms and other lists to arbitrary depth.

### Atoms

Atoms are terminal values:

- **Symbols**: named identifiers like `foo`, `my-variable`, `+`
- **Strings**: quoted text like `"hello world"`
- **Numbers**: integers and floats like `42`, `-7`, `3.14`, `6.02e23`

### Lists

Lists group S-expressions using parentheses:

```lisp
()                    ; empty list
(foo bar baz)         ; three atoms
(+ 1 2)               ; function call in prefix notation
((a b) (c d))         ; two sublists
```

Parentheses must be properly matched. Whitespace separates tokens but is otherwise ignored.

### Prefix Notation

The first element of a list is conventionally an operator; remaining elements are arguments:

```lisp
(+ 2 3)               ; 5
(* 4 (+ 1 2))         ; 12
(max 10 20 30)        ; 30
```

Prefix notation eliminates operator precedence rules — nesting alone determines evaluation order.

### Homoiconicity

Homoiconicity means a language's primary representation of programs is also a data structure in the language itself. The expression `(+ 1 2)` is valid code (evaluates to `3`) and valid data (a list of three elements). This enables macros, metaprogramming, and REPL-based interactive development.

### Cons Cells

Lisp implements lists using **cons cells** — ordered pairs with two fields (car and cdr). A proper list chains cons cells: car holds an element, cdr points to the next cell or `nil`. The notation `(a b c)` represents this chain visually as a flat sequence.

## Datatypes and Syntax

### Symbols

Named identifiers serving as labels, variable names, function names, and keys. Allowed characters (POSE portable subset): lowercase `a-z`, digits `0-9`, punctuation `!$&*+-/<=>_?@`. A symbol may start with a single colon (`:keyword`) for pragmatic compatibility.

```lisp
foo       my-symbol-name   +   count-items   :option
```

Symbols cannot contain spaces, parentheses, or semicolons. Tokens starting with a digit, or with `+`/`-` followed by a digit, must parse as valid numbers — this prevents ambiguity across dialects.

### Strings

Character sequences in double quotes with two escape sequences:

```lisp
"hello world"
"escaped \" quote"
"backslash \\"
```

### Numbers

**Integers**: optional sign, digits, no leading zeros (except `0` itself).

```lisp
0   42   -7   1000000
```

**Floating-point**: integer part, optional fraction, optional exponent.

```lisp
3.14   -0.5   6.02e23   1.6e-19
```

### Booleans

Scheme convention: `#t` (true) and `#f` (false) as a disjoint type. Other dialects use `true`/`false`, `t`/`nil`, or `True`/`False`. For portable interchange, treat booleans as symbols unless the target language specifies otherwise.

### Comments

Semicolon `;` begins a comment to end of line:

```lisp
(+ 1 2)   ; add one and two
; entire line is a comment
```

### Whitespace

Spaces, tabs, and newlines separate tokens. Multiple spaces, mixed whitespace, or indentation all produce identical parse results.

## Abstract vs Concrete Syntax

**Concrete syntax** — the text form:

```lisp
(set x (+ (* a b) c))
```

**Abstract syntax** — the parsed tree:

```
["set", "x", ["+", ["*", "a", "b"], "c"]]
```

The parse pipeline:

```
text → tokenize → parse → S-expression tree → (optional) abstract syntax
```

1. **Tokenize**: split text into left-paren, right-paren, and atom tokens
2. **Parse**: build nested lists from matched parenthesis pairs
3. **Transform** (optional): convert S-expression tree to language-specific AST

**Round-trip property**: `parse(print(sexp)) == sexp` — the notation is lossless.

## Functions and Lambdas

In Lisp-family languages, functions are first-class S-expressions. Defining, calling, and storing functions uses the same parenthesized notation as everything else. This section covers how each language handles these operations.

### Named Functions

Each language provides a form to define a named function. All produce an S-expression tree:

**Common Lisp** — `defun`:

```lisp
(defun factorial (n)
  (if (= n 0)
      1
      (* n (factorial (- n 1)))))
```

The `defun` form takes a name, a parameter list, and a body of expressions. The last expression's value is the return value.

**Clojure** — `defn`:

```lisp
(defn factorial [n]
  (if (zero? n)
    1
    (* n (factorial (dec n)))))
```

Clojure uses vectors `[n]` for parameter lists instead of parentheses. `defn` is conceptually `def` + `fn` — it creates an anonymous function with `fn` and binds it to a name with `def`.

**Scheme** — `define` + `lambda`:

```lisp
(define (factorial n)
  (if (= n 0)
      1
      (* n (factorial (- n 1)))))
```

Scheme's `(define (name args) body)` is syntactic sugar for `(define name (lambda (args) body))`. The fundamental function constructor is `lambda`; `define` only binds names.

**Emacs Lisp** — `defun` (same as Common Lisp):

```lisp
(defun factorial (n)
  (if (= n 0)
      1
      (* n (factorial (- n 1)))))
```

### Anonymous Functions (Lambda)

Anonymous functions are S-expressions that evaluate to a procedure without binding it to a name:

**Scheme and Emacs Lisp** — `lambda`:

```lisp
(lambda (x) (+ x x))
```

This evaluates to a procedure. Call it immediately by placing it in function position:

```lisp
((lambda (x) (+ x x)) 4)    ; → 8
```

**Clojure** — `fn` and `#()`:

```lisp
(fn [x] (+ x x))             ; full anonymous form
#(+ % 6)                     ; reader shorthand, % = first arg
#(+ %1 %2)                   ; multiple args: %1, %2, %&
```

The `#()` shorthand uses `%` for a single parameter, `%1`/`%2` for multiple, and `%&` for variadic rest. Nesting is not allowed in `#()` form.

### Calling Functions

**Direct call** — function name or expression in first position:

```lisp
(factorial 5)                ; named function
((lambda (x) (* x x)) 4)    ; anonymous, immediate call
```

In Scheme, the operator and operands are always evaluated with the same rules. `((if #f + *) 3 4)` evaluates the `if` to select `*`, then calls `(* 3 4)` → `12`.

**Indirect call** — Common Lisp provides `funcall` and `apply`:

```lisp
(funcall #'factorial 5)      ; call function object with args
(apply #'+ (list 1 2 3))     ; call with args from a list
```

**Clojure** — `apply` spreads a sequence as arguments:

```lisp
(apply + 1 2 '(3 4))         ; same as (+ 1 2 3 4) → 10
```

### Storing Results and Closures

**Binding to a name** — the result of any expression, including function creation, can be stored:

```lisp
; Scheme — define binds a name to a value
(define square (lambda (x) (* x x)))
(square 5)                   ; → 25

; Clojure — def binds a var
(def square (fn [x] (* x x)))
(square 5)                   ; → 25
```

**Closures** — functions capture the environment where they were defined:

```lisp
; Scheme
(define (make-adder n)
  (lambda (x) (+ n x)))

(define add5 (make-adder 5))
(add5 3)                     ; → 8, captures n=5 from enclosing scope

; Clojure
(defn make-adder [n]
  (fn [x] (+ n x)))

((make-adder 5) 3)           ; → 8
```

The lambda expression remembers the environment in effect when it was evaluated. Later calls extend that remembered environment with fresh bindings for parameters.

### Variadic Parameters

Functions accepting a variable number of arguments:

**Scheme** — dot notation in formals:

```lisp
(lambda (a b . rest) rest)   ; takes 2+ args, rest is a list
(((lambda (x y . z) z) 1 2 3 4))   ; → (3 4)

(lambda args args)           ; bare symbol = all args as a list
(((lambda args args) 1 2 3))       ; → (1 2 3)
```

**Clojure** — `&` marks the rest parameter:

```lisp
(fn [a b & rest] rest)
((fn [greeting & who] (println greeting who)) "Hi" "Alice" "Bob")
; → Hi (Alice Bob)
```

**Common Lisp** — `&rest` in the parameter list:

```lisp
(defun greet (greeting &rest who)
  (format t "~A ~S" greeting who))
```

### Multiple Return Values

**Common Lisp** supports multiple return values via `values`:

```lisp
(defun many (n)
  (values n (* n 2) (* n 3)))

(multiple-value-list (many 2))    ; → (2 4 6)
(nth-value 1 (many 2))            ; → 4
```

Scheme, Clojure, and Emacs Lisp return a single value — the result of the last expression in the body.

## Why S-expressions

S-expressions arise from a simple insight: if a parser's job is to turn text into a tree, make the text format directly represent trees.

**Minimalism**: Two rules (atom, list) cover all finite trees. No special syntax for conditionals, loops, or functions — those are patterns of atoms and lists.

**Extensibility**: New constructs require no grammar changes. A new feature is a new atom or list pattern interpreted by the runtime:

```lisp
(if condition then-expr else-expr)
(for variable from start to end body)
```

The parser treats these identically — it only sees lists. Meaning comes from the interpreter.

**Uniformity**: Everything is an atom or a list. Generic code traverses, transforms, or analyzes any S-expression without special cases. Function definitions, data records, and grammar rules all use the same structure.

**Parser simplicity**: Traditional implementations require complex grammars, lexer generators, and parser combinators — all language-specific. With S-expressions, the parser is generic and minimal. The only language-specific work interprets the parsed tree.

## Usage Examples

### Data Representation

```lisp
(person
  (name "Alice")
  (age 30)
  (skills lisp scheme clojure))
```

### Arithmetic Expressions

```lisp
(+ (* 2 3) (- 7 4))      ; 11
(sqrt (+ (* x x) (* y y))) ; Euclidean distance
```

### Grammar Rules

```lisp
(((sentence) (noun-phrase verb-phrase))
 ((verb-phrase) (verb))
 ((verb-phrase) (verb noun-phrase))
 ((verb) "runs")
 ((noun-phrase) "the cat"))
```

### Function as Data

```lisp
; This S-expression is both code and data:
(defun factorial (n)
  (if (= n 0)
      1
      (* n (factorial (- n 1)))))

; As a tree it is:
; (defun factorial (n) (if (= n 0) 1 (* n (factorial (- n 1)))))
; A macro receives this exact structure, transforms it as a tree,
; and returns a new S-expression for the evaluator to execute.
```

### Portable Interchange (POSE)

```lisp
; A POSE data file
(configuration
  (name "my-project")
  (version 1)
  (enabled #t)
  (tags alpha beta gamma)
  (metadata
    (author "developer")
    (description "A sample configuration")))
```

POSE restricts symbols to lowercase ASCII, forbids leading zeros in numbers, and uses `;` for line comments. Any language with an S-expression reader can parse POSE files without dialect-specific extensions.
