# Python to Common Lisp Cheatsheet (lispstudent)

## Contents
- Equality Predicates
- Sequence Types and Operations
- Map Types
- Iteration (LOOP)
- Strings
- Regex (CL-PPCRE)
- File I/O

## Equality Predicates

Tower of predicates from strictest to loosest:

| Predicate | Compares |
| --- | --- |
| `eq` | Object identity (symbols, eq-unique objects only) |
| `eql` | Like `eq` + same-type numbers + same chars. **Default for hash tables.** |
| `equal` | Structural equality for lists, strings, vectors |
| `equalp` | Case-insensitive strings, type-loose numbers, recursive arrays |
| `=` | Numeric equality across types (`(= 1 1.0)` → `T`) |
| `string=` / `string-equal` | Case-sensitive / case-insensitive string equality |

## Sequence Types

Two main concrete subtypes of abstract `sequence`:
- **list** — singly-linked cons cells: `'(1 2 3)`, `(list 1 2 3)`
- **vector** — one-dimensional arrays: `#(1 2 3)`. Subtypes: `string`, `bit-vector`

Generic functions (`length`, `elt`, `subseq`, `map`, `reduce`, `find`, `position`, `count`, `remove`) work on both.

Key operations:
```lisp
(elt s i)           ; s[i], O(n) on lists
(subseq s i j)      ; s[i:j]
(length s)          ; len(s)
(find x s :test #'cmp)   ; x in s
(position x s :test #'cmp)  ; s.index(x)
(reduce #'+ s)      ; sum(s)
(map 'list #'f s)   ; list(map(f, s))
```

`sort` may destructively modify — use `copy-seq` first if original must be preserved.

## Map Types

Three map-like structures:

**Hash table** (Python dict equivalent):
```lisp
(setf d (make-hash-table :test 'equal))   ; for string keys, MUST use :test 'equal
(setf (gethash k d) v)                    ; d[k] = v
(gethash k d)                             ; returns two values: value, present-p
(maphash (lambda (k v) ...) d)           ; iterate
```

**Alist** (list of cons cells):
```lisp
'((k1 . v1) (k2 . v2))
(cdr (assoc k d :test #'equal))           ; d[k]
(setf d (acons k v d))                    ; insert
```

**Plist** (flat alternating key-value list):
```lisp
'(:a 1 :b 2)
(getf d :a)                               ; d[:a]
(setf (getf d :k) v)                      ; d[:k] = v
```

## Iteration (LOOP)

`LOOP` macro handles range, parallel iteration, accumulation, and conditional logic:

```lisp
(loop for i below n do (f i))              ; for i in range(n)
(loop for x in s collect (f x))            ; [f(x) for x in s]
(loop for x in s when (p x) collect (f x)) ; [f(x) for x in s if p(x)]
(loop for a in xs for b in ys do (f a b))  ; zip
(loop for x in xs sum x)                   ; sum
```

## Strings

CL strings are vectors of characters. `(char s 0)` returns a character `#\h`, not a string `"h"`.

```lisp
(concatenate 'string a b)    ; a + b
(subseq s i j)               ; s[i:j]
(search sub s)               ; s.find(sub) → index or nil
(string-downcase s)          ; s.lower()
(format nil "~{~A~^, ~}" lst)  ; ", ".join(lst)
```

## Regex (CL-PPCRE)

No regex in ANSI CL. CL-PPCRE is the de facto standard:

```lisp
(ppcre:scan p s)                     ; re.search → 4 values or NIL
(ppcre:all-matches-as-strings p s)   ; re.findall
(ppcre:regex-replace-all p s r)      ; re.sub (note arg order: pattern, target, replacement)
(ppcre:split p s)                    ; re.split
(ppcre:quote-meta-chars s)           ; re.escape
```

No raw string syntax — `"\\d+"` is the CL equivalent of Python's `r"\d+"`.

## File I/O

```lisp
(with-open-file (in filename :direction :input)
  (loop for line = (read-line in nil nil)
        while line
        collect line))
```

UIOP shortcuts: `(uiop:read-file-lines fn)`, `(uiop:read-file-string fn)`.
