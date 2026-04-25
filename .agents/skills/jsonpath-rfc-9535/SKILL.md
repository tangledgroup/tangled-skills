---
name: jsonpath-rfc-9535
description: Complete reference for JSONPath RFC 9535, the IETF Standards Track specification defining a string syntax for selecting and extracting JSON values from within a given JSON value. Use when writing JSONPath query expressions, understanding selector semantics (name, wildcard, index, slice, filter), implementing function extensions (length, count, match, search, value), or comparing JSONPath to JSON Pointer RFC 6901.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.0.0"
tags:
  - JSON
  - query language
  - data selection
  - extraction
  - IETF standard
category: data-formats
external_references:
  - https://www.rfc-editor.org/rfc/rfc9535
  - https://www.rfc-editor.org/rfc/rfc6901
  - https://www.rfc-editor.org/rfc/rfc7493
  - https://www.rfc-editor.org/rfc/rfc8259
  - https://www.rfc-editor.org/rfc/rfc9485
---

# JSONPath RFC 9535

## Overview

JSONPath defines a string syntax for selecting and extracting JSON (RFC 8259) values from within a given JSON value. It is not intended as a replacement for JSON Pointer (RFC 6901), but as a more powerful companion.

A JSONPath expression is applied to a JSON value (the query argument) and produces a **nodelist** — a list of zero or more nodes, where each node is a pair of a value and its location within the query argument.

JSONPath was published as an IETF Standards Track document in February 2024 by Gössner, Normington, and Bormann. It supersedes earlier informal JSONPath specifications with a formal ABNF grammar and well-defined semantics.

## When to Use

- Writing JSONPath query expressions to select specific data from JSON documents
- Understanding the difference between child segments (`[...]`) and descendant segments (`..[...]`)
- Implementing filter expressions with comparison operators, logical operators, and function extensions
- Comparing JSONPath (RFC 9535) to JSON Pointer (RFC 6901)
- Building JSONPath parsers or validators conforming to the IETF standard
- Understanding security considerations for JSONPath implementations

## Core Concepts

### JSON Values as Trees of Nodes

JSON values are treated as trees where:
- **Value**: A data item — primitive (number, string, true, false, null) or structured (object, array)
- **Member**: A name/value pair in an object (not itself a value)
- **Element**: A value in a JSON array
- **Node**: A pair of a value along with its location within the query argument
- **Root Node**: The unique node whose value is the entire query argument
- **Location**: The position of a value, represented as a sequence of names and indexes

### Expression Structure

A JSONPath expression consists of:
1. **Root identifier** (`$`) — required, refers to the root node
2. **Zero or more segments**, each containing one or more **selectors**

```
jsonpath-query = root-identifier segments
root-identifier = "$"
```

### Identifiers

| Identifier | Meaning | Valid Context |
|------------|---------|---------------|
| `$` | Root node identifier | Everywhere except inside filter expressions |
| `@` | Current node identifier | Only inside filter selectors (2.3.5) |

## Syntax Overview

### Table: JSONPath Syntax Elements

| Syntax Element | Description | Section |
|----------------|-------------|---------|
| `$` | Root node identifier | 2.2 |
| `@` | Current node identifier (filter context only) | 2.3.5 |
| `[<selectors>]` | Child segment: selects children of a node | 2.5.1 |
| `.name` | Shorthand for `['name']` | 2.5.1 |
| `.*` | Shorthand for `[*]` | 2.3.2 |
| `[...<selectors>]` | Descendant segment: selects descendants of a node | 2.5.2 |
| `..name` | Shorthand for `..['name']` | 2.5.2 |
| `..*` | Shorthand for `..[*]` | 2.3.2 |
| `'name'` or `"name"` | Name selector: selects named child of an object | 2.3.1 |
| `*` | Wildcard selector: selects all children of a node | 2.3.2 |
| `3` | Index selector: selects indexed child of array (0-based) | 2.3.3 |
| `-1` | Negative index: counts from array end (-1 = last) | 2.3.3 |
| `0:100:5` | Array slice: start:end:step for arrays | 2.3.4 |
| `?<logical-expr>` | Filter selector: selects children using logical expression | 2.3.5 |
| `length(@.foo)` | Function extension in filter expressions | 2.4 |

### Bracket vs Dot Notation

Both notations are equivalent; bracket notation is canonical:

```
$.store.book[0].title    ≡    $['store']['book'][0]['title']
$.o[*]                   ≡    $[*] applied to $.o
$..author                ≡    $..['author']
```

## Selectors

Selectors appear inside child segments (`[...]`) and descendant segments (`..[...]`). Each produces a nodelist of zero or more children of the input value.

### Name Selector

Selects at most one object member value by name.

```
$['store']['book'][0]['title']
$.o["j j"]["k.k"]          # dot in name requires bracket notation
```

String literals support both single and double quotes with escape sequences (`\b`, `\t`, `\n`, `\f`, `\r`, `\"`, `\'`, `\/`, `\\`, `\uXXXX`). Member name comparison is Unicode scalar value identity — no normalization.

### Wildcard Selector

Selects all children of an object or array. Object child order is not stipulated (objects are unordered). Array children appear in array order.

```
$[*]                       # all top-level members
$.o[*]                     # all children of $.o
$.a[*]                     # all elements of array $.a
```

### Index Selector

Selects a single array element by zero-based index. Negative indices count from the end.

```
$[0]                       # first element
$[-1]                      # last element
$[-2]                      # second-to-last element
```

Nothing is selected (not an error) if the index is out of range.

### Array Slice Selector

Selects a subset of array elements: `start:end:step`. Default step is 1. The end index is exclusive. When step is negative, selection is in reverse order. Step of 0 selects nothing.

```
$[0:2]                     # indices 0 and 1
$[1:5:2]                   # indices 1 and 3
$[:3]                      # first three elements (start defaults to 0)
$[-3:]                     # last three elements
::-1                       # all elements in reverse order
$[5:1:-2]                  # indices 5, 3 (reverse with step -2)
```

### Filter Selector

Iterates over array elements or object members, evaluating a logical expression for each. The current node is referenced via `@`.

```
$..book[?@.price < 10]     # books cheaper than 10
$..book[?@.isbn]           # books with an ISBN (existence test)
$.a[*][?@.k > 5]           # elements where member k > 5
```

#### Filter Expression Operators (by precedence, highest first)

| Precedence | Operator Type | Syntax |
|------------|--------------|--------|
| 5 | Grouping / Function Expressions | `(...)`, `name(...)` |
| 4 | Logical NOT | `!` |
| 3 | Relations | `==`, `!=`, `<=`, `>=`, `<`, `>` |
| 2 | Logical AND | `&&` |
| 1 | Logical OR | `\|\|` |

#### Filter Expression Types

- **Test expression**: Tests existence of a node (`@.foo`) or result of a function (`length(@) > 3`)
- **Comparison expression**: Compares primitive values (`@.price == 8.95`, `@.title == "Moby Dick"`)
- **Logical expressions**: Combine with `||` (OR), `&&` (AND), `!` (NOT)

#### Literals in Filter Expressions

```
true, false, null          # JSON literals (lowercase only)
8.95                       # number
"string" or 'string'       # string (single quotes allowed)
@.price < 10               # singular query comparison
```

## Function Extensions

Function extensions extend filter expression functionality with registered functions. Each function has a unique lowercase name, declared parameter types, and a declared return type. Functions must be free of side effects.

### Predefined Functions

#### `length(value)` → unsigned integer or Nothing

Computes the length of a value:
- **String**: Number of Unicode scalar values
- **Array**: Number of elements
- **Object**: Number of members
- **Other**: Returns Nothing

```
$[?length(@.authors) >= 5]
```

#### `count(nodelist)` → unsigned integer

Returns the number of nodes in a nodelist (no deduplication).

```
$[?count(@.*.author) >= 5]
```

#### `match(string, regexp)` → true/false

Checks if an entire string matches a regular expression (I-Regexp per RFC 9485).

```
$[?match(@.date, "1974-05..")]
```

#### `search(string, regexp)` → true/false

Checks if a string contains a substring matching a regular expression.

```
$[?search(@.author, "[BR]ob")]
```

#### `value(nodelist)` → value or Nothing

Converts a nodelist to a single value:
- Single node: returns the node's value
- Empty or multiple nodes: returns Nothing

```
$[?value(@..color) == "red"]
```

### Type System

| Type | Instances | Description |
|------|-----------|-------------|
| `ValueType` | JSON values or Nothing | Primitive values (numbers, strings, booleans, null) |
| `LogicalType` | LogicalTrue or LogicalFalse | Boolean results of filter expressions |
| `NodesType` | Nodelists | Lists of nodes selected by queries |

**Implicit conversions**: A `NodesType` can be converted to `LogicalType` (non-empty → LogicalTrue, empty → LogicalFalse). A `NodesType` cannot be implicitly converted to `ValueType`.

## Segments

### Child Segment

Drills down exactly one level into the structure. Contains a comma-separated sequence of selectors in brackets.

```
$['store']['book'][0]['title']    # chain of name selectors
$[0, 3]                           # multiple indices
$[0:2, 5]                         # slice and index combined
$.a[*].b                          # dot notation shorthand
```

### Descendant Segment

Drills down one or more levels. Selects all descendants matching the selector(s).

```
$..author                         # all 'author' members at any depth
$..book[2]                        # third 'book' at any depth
$..[*]                            # all member values and array elements
$..book[?@.price < 10]            # books cheaper than 10, at any depth
```

**Important**: `..` alone is not valid — it must be followed by a child segment (bracket notation).

## Semantics of null

JSON `null` is treated as any other JSON value — it is NOT "undefined" or "missing". It can be used as an array element, object member value, and compared in filter expressions.

```
$.a                                # returns null if $.a exists with value null
$.a[0]                             # null used as array (selects nothing, not an error)
$.a.d                              # null used as object (selects nothing, not an error)
$.b[?@ == null]                    # existence: true if @ is null
$.c[?@.d == null]                  # comparison with "missing" value
```

## Normalized Paths

A **Normalized Path** is a unique representation of a node's location in a value. It uses restricted bracket notation with single quotes and non-negative indices only.

```
$.a                    →  $['a']
$[1]                   →  $[1]
$[-3] (array len 5)   →  $[2]
$.a.b[1:2]            →  $['a']['b'][1]
```

Normalized Paths are useful for compact nodelist representation in JSON and for deterministic post-processing.

## Security Considerations

### Implementation Security (Section 4.1)

- **Never use eval()** or feed query parts to underlying language engines — this leads to injection attacks
- Implement the full JSONPath syntax independently without relying on external parsers
- Guard against resource exhaustion attacks: crafted queries or data can trigger exponential CPU usage, stack overflow from naive recursive descendant implementations, or hash-table collisions

### Query Formation Security (Section 4.2)

- Validate and escape variables used to form queries dynamically
- When constructing `.name` segments from user input, ensure the value is a safe member name
- Escape string delimiters in filter expression values
- Treat all external input as potentially adversarial — this class of injection attacks is consistently in the top causes of vulnerabilities

### Security Mechanism Attacks (Section 4.3)

- JSONPath implementations may behave differently on unpredictable constructs
- Predictable behavior is expected only for arguments conforming to I-JSON (RFC 7493)
- Differences between implementations can be exploited where JSONPath is part of a security mechanism

## Examples — Bookstore Dataset

Using the classic bookstore example from RFC 9535:

```json
{ "store": {
  "book": [
    { "category": "reference", "author": "Nigel Rees",
      "title": "Sayings of the Century", "price": 8.95 },
    { "category": "fiction", "author": "Evelyn Waugh",
      "title": "Sword of Honour", "price": 12.99 },
    { "category": "fiction", "author": "Herman Melville",
      "title": "Moby Dick", "isbn": "0-553-21311-3", "price": 8.99 },
    { "category": "fiction", "author": "J. R. R. Tolkien",
      "title": "The Lord of the Rings", "isbn": "0-395-19395-8", "price": 22.99 }
  ],
  "bicycle": { "color": "red", "price": 399 }
}}
```

| JSONPath | Result |
|----------|--------|
| `$.store.book[*].author` | All book authors in the store |
| `$..author` | All authors at any depth |
| `$.store.*` | All things in the store (books + bicycle) |
| `$.store..price` | All prices in the store |
| `$..book[2]` | The third book |
| `$..book[-1]` | The last book |
| `$..book[0,1]` or `$..book[:2]` | The first two books |
| `$..book[?@.isbn]` | All books with an ISBN |
| `$..book[?@.price < 10]` | All books cheaper than 10 |
| `$..*` | All member values and array elements in the input |

## Comparison with JSON Pointer (RFC 6901)

JSONPath is designed as a companion to, not a replacement for, JSON Pointer:

- **JSON Pointer** (`/store/book/0/title`): Simple path navigation using forward slashes
- **JSONPath** (`$.store.book[0].title`): Query language with wildcards, filtering, slicing, and descendant traversal

JSONPath supports operations that JSON Pointer cannot: wildcard selection (`*`), filtering (`?`), array slicing (`:`), and recursive descent (`..`).

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
