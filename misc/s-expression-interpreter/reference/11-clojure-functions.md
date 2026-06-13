# Clojure Functions Guide (clojure.org)

## Contents
- Creating Functions
- Multi-Arity and Variadic
- Anonymous Syntax
- apply
- Locals and Closures
- Java Interop

## Creating Functions

`defn` defines named functions:

```clojure
(defn greet [name] (str "Hello, " name))
(greet "students")  ; → "Hello, students"
```

`fn` creates anonymous functions:

```clojure
(fn [message] (println message))
```

These are equivalent:
```clojure
(defn greet [name] (str "Hello, " name))
(def greet (fn [name] (str "Hello, " name)))
```

## Multi-Arity Functions

Different arities defined in single `defn`:

```clojure
(defn messenger
  ([]     (messenger "Hello world!"))
  ([msg]  (println msg)))
```

## Variadic Functions

Variable arguments collected in a sequence via `&`:

```clojure
(defn hello [greeting & who]
  (println greeting who))

(hello "Hello" "world" "class")
; → Hello (world class)
```

## Anonymous Syntax

Shorthand `#()` with `%` positional parameters:

```clojure
#(+ 6 %)         ; (fn [x] (+ 6 x))
#(+ %1 %2)       ; (fn [x y] (+ x y))
#(println %1 %2 %)  ; variadic with %&
```

Gotcha: `#([%])` tries to invoke the vector. Use `#(vector %)` or `(fn [x] [x])` instead.

## apply

```clojure
(apply + [1 2 3])  ; → 6
```

Spreads a collection as individual arguments to a function.

## Locals and Closures

```clojure
(let [x 10 y 20]
  (+ x y))  ; → 30
```

Closures capture enclosing scope:
```clojure
(defn make-adder [n]
  (fn [x] (+ n x)))

((make-adder 5) 3)  ; → 8
```

## Java Interop

Invoke Java methods:
```clojure
(.toUpperCase "hello")       ; → "HELLO"
("hello".toUpperCase)        ; same
```

Call static methods:
```clojure
(Math/sqrt 16)  ; → 4.0
```

Java methods are not functions — they can't be passed as values directly. Wrap with `memfn` or use method references.
