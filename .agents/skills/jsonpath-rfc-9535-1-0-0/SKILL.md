---
name: jsonpath-rfc-9535-1-0-0
description: Complete reference for JSONPath RFC 9535, the IETF Standards Track specification defining a string syntax for selecting and extracting JSON values from within a given JSON value. Use when writing JSONPath query expressions, understanding selector semantics (name, wildcard, index, slice, filter), implementing function extensions (length, count, match, search, value), or comparing JSONPath to JSON Pointer RFC 6901.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - JSON
  - query-language
  - data-selection
  - extraction
  - IETF-standard
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

JSONPath defines a string syntax for selecting and extracting JSON values from within a given JSON value. Published as an IETF Standards Track document in February 2024, it standardizes the popular JSONPath query language originally proposed by Stefan Gössner in 2007.

A JSONPath expression is applied to a JSON value (the _query argument_) and produces a _nodelist_ — a list of zero or more nodes selected from within that value. Each node represents a value at a specific location within the query argument's tree structure.

JSONPath is not a replacement for JSON Pointer (RFC 6901) but a more powerful companion. While JSON Pointer identifies a single value in a known structure, JSONPath can search and extract multiple values from structures known only generally — supporting wildcards, filters, array slicing, and descendant traversal.

## When to Use

- Writing JSONPath query expressions for selecting data from JSON documents
- Understanding selector semantics: name, wildcard, index, slice, and filter
- Implementing function extensions (length, count, match, search, value)
- Building query APIs that return nodelists or normalized paths
- Comparing JSONPath to JSON Pointer (RFC 6901) or XPath
- Working with I-JSON (RFC 7493) constraints on exact integer ranges
- Using I-Regexp (RFC 9485) patterns in match/search functions
- Validating JSONPath query well-formedness and well-typedness
- Understanding security considerations for JSONPath implementations

## Core Concepts

### Query Structure

A JSONPath expression consists of:

1. A root identifier (`$`) referring to the entire query argument
2. Zero or more _segments_, each containing one or more _selectors_

```
$.store.book[0].title          # dot notation (shorthand)
$['store']['book'][0]['title']  # bracket notation (canonical)
```

### Identifiers

- `$` — root node identifier, refers to the entire query argument
- `@` — current node identifier, valid only within filter selectors (Section 2.3.5)

### Two Notations

- **Bracket notation** `[<selectors>]` — canonical form, supports all selector types
- **Dot notation** `.name` — shorthand for `['name']`, limited to simple member names

Both can be mixed freely: `$.store.book[0].title` is equivalent to `$['store']['book'][0]['title']`.

### Segments

Segments navigate the JSON tree:

- **Child segment** `[<selectors>]` — selects children of current nodes (one level deeper)
- **Descendant segment** `..[<selectors>]` — selects descendants at any depth

### Selectors

Five types of selectors operate within segments:

| Selector | Example | Description |
|----------|---------|-------------|
| Name | `'title'` | Selects a named member of an object |
| Wildcard | `*` | Selects all children (members or elements) |
| Index | `3` or `-1` | Selects an array element by zero-based index |
| Slice | `1:5:2` | Selects a range of array elements with step |
| Filter | `?@.price < 10` | Selects children matching a logical expression |

### Nodelists and Evaluation

- A query produces a _nodelist_ (list of zero or more nodes)
- Each segment operates on every node in its input nodelist
- Results from each input node are concatenated in order
- Duplicate nodes are preserved (not deduplicated)
- Empty nodelists are valid results — they propagate through remaining segments
- Object member ordering is non-deterministic; array element ordering is preserved

### Query Well-Formedness and Validity

A JSONPath query must be both well-formed (conforms to ABNF syntax) and valid:

1. Integer values (indices, steps) must be within the I-JSON exact range: `[-(2^53)+1, (2^53)-1]`
2. Function extension uses must be well-typed per Section 2.4.3
3. Queries must be encoded in UTF-8

Implementations MUST raise an error for queries that are not well-formed and valid. Well-formedness/validity is independent of the query argument — no further query errors can occur during evaluation.

## Usage Examples

### Basic Selections

```json
// Given this JSON (the bookstore example from RFC 9535):
{
  "store": {
    "book": [
      { "category": "reference", "author": "Nigel Rees", "title": "Sayings of the Century", "price": 8.95 },
      { "category": "fiction", "author": "Evelyn Waugh", "title": "Sword of Honour", "price": 12.99 },
      { "category": "fiction", "author": "Herman Melville", "title": "Moby Dick", "isbn": "0-553-21311-3", "price": 8.99 },
      { "category": "fiction", "author": "J.R.R. Tolkien", "title": "The Lord of the Rings", "isbn": "0-395-19395-8", "price": 22.99 }
    ],
    "bicycle": { "color": "red", "price": 399 }
  }
}
```

```
$.store.book[*].author      → authors of all books in the store
$..author                   → all authors anywhere in the document
$.store.*                   → all things in the store (books array + bicycle object)
$.store..price              → prices of everything in the store
$..book[2]                  → the third book
$..book[-1]                 → the last book
$..book[:2]                 → the first two books
$..book[?@.isbn]            → all books with an ISBN
$..book[?@.price < 10]      → all books cheaper than 10
$..*                        → all member values and array elements in the document
```

### Filter Expressions

```
$.store.book[?@.category == 'fiction']          → fiction books only
$.store.book[?@.price < 10 && @.isbn]           → cheap books with ISBN
$.store.book[?@.author == 'Nigel Rees' || @.price > 20]  → specific author or expensive
```

### Array Slicing

```
$[1:3]       → elements at indices 1 and 2 (step defaults to 1)
$[5:]        → elements from index 5 to end
$[1:5:2]     → elements at indices 1 and 3 (step of 2)
$[5:1:-2]    → elements at indices 5 and 3 (reverse, step -2)
$[::-1]      → all elements in reverse order
```

### Function Extensions

```
$[?length(@.authors) >= 5]     → items with 5+ authors
$[?count(@..tag) > 3]          → items with more than 3 descendant "tag" nodes
$[?match(@.date, "^2024-")]    → items where date starts with 2024
$[?search(@.name, "[A-Z]ob")]  → items where name contains substring matching pattern
$[?value(@..color) == "red"]   → items where the unique descendant "color" is "red"
```

## Advanced Topics

**Selectors**: Full semantics for all five selector types with syntax rules and examples → [Selectors](reference/01-selectors.md)

**Function Extensions**: Type system, well-typedness rules, and all five built-in functions → [Function Extensions](reference/02-function-extensions.md)

**Segments and Paths**: Child/descendant segment semantics, normalized paths, null handling → [Segments and Paths](reference/03-segments-and-paths.md)

**Comparison with JSON Pointer**: JSON Pointer (RFC 6901), XPath comparison, I-JSON constraints, I-Regexp → [Comparison with JSON Pointer](reference/04-comparison-with-json-pointer.md)
