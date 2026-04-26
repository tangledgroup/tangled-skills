# Comparison with JSON Pointer and XPath

## JSON Pointer (RFC 6901)

JSON Pointer and JSONPath serve different but complementary purposes.

### JSON Pointer Syntax

A JSON Pointer is a string of zero or more reference tokens, each prefixed by `/`:

```
json-pointer    = *( "/" reference-token )
reference-token = *( unescaped / escaped )
escaped         = "~" ( "0" / "1" )   ; ~0 for ~, ~1 for /
```

Special characters:
- `~` must be encoded as `~0`
- `/` must be encoded as `~1`
- Substitutions are applied in order: first `~1` → `/`, then `~0` → `~`

### JSON Pointer Examples

```json
// Given: { "foo": ["bar", "baz"], "": 0, "a/b": 1, "m~n": 8 }
""           → the whole document
"/foo"       → ["bar", "baz"]
"/foo/0"     → "bar"
"/"          → 0                (empty string member name)
"/a~1b"      → 1                (member name "a/b")
"/m~0n"      → 8                (member name "m~n")
```

### Key Differences

| Aspect | JSON Pointer | JSONPath |
|--------|-------------|----------|
| Purpose | Identify a single value in known structure | Search and extract from general structure |
| Root | empty string `""` | `$` |
| Navigation | `/` prefix per token | `[...]` segments or `.name` |
| Wildcards | Not supported | `*` selector |
| Descendants | Not supported | `..` descendant segment |
| Filters | Not supported | `?` filter expressions |
| Array slicing | Not supported | `start:end:step` |
| Multiple results | Single value only | Nodelist (zero or more) |
| Error on miss | Raises error | Returns empty result |

### Conversion

A Normalized JSONPath can be converted to a JSON Pointer without knowing the JSON structure:

```
$['store']['book'][0]    →   /store/book/0
$['a']['b']              →   /a/b
```

The inverse is not generally possible without knowing the data structure, because a numeric reference token in JSON Pointer could be either an array index or an object member name.

## XPath Comparison

JSONPath was inspired by XPath 1.0 but simplified for JSON:

| XPath | JSONPath | Description |
|-------|----------|-------------|
| `/` | `$` | Root node |
| `.` | `@` | Current node (in filter context) |
| `/` | `.` or `[]` | Child operator |
| `..` | n/a | Parent operator (JSONPath has no parent navigation) |
| `//` | `..name`, `..[*]`, `..*` | Descendants (borrowed from E4X) |
| `*` | `*` | Wildcard |
| `@` | n/a | Attribute access (JSON has no attributes) |
| `[]` | `[]` | Subscript / filter operator |
| `\|` | `[ , ]` | Union (list operator in JSONPath) |
| n/a | `[start:end:step]` | Array slice (unique to JSONPath) |
| `[]` | `?` | Filter expression |

### Key Behavioral Differences

- **Indexing**: XPath uses 1-based indexing; JSONPath uses 0-based
- **Square brackets in XPath**: operate on the node set from the previous path fragment
- **Square brackets in JSONPath**: operate on each node individually in the nodelist
- **JSONPath is lighter weight**: covers only essential XPath 1.0 features, no location paths in unabbreviated syntax, no expression engine

### Examples

```
XPath                    JSONPath                   Result
/store/book/author       $.store.book[*].author     authors of all books
//author                 $..author                  all authors
/store/*                 $.store.*                  all things in store
/store//price            $.store..price             prices in store
//book[3]                $..book[2]                 third book (1-based vs 0-based)
//book[last()]           $..book[-1]                last book
//book[position()<3]     $..book[:2]                first two books
//book[isbn]             $..book[?@.isbn]           books with ISBN
//*                      $..*                       all elements
```

## I-JSON (RFC 7493) Context

I-JSON (Internet JSON) is a restricted profile of JSON designed for maximum interoperability. JSONPath references it for two key constraints:

### Exact Integer Range

Integer values in JSONPath queries (indices, slice bounds/steps) must be within the I-JSON exact range:

```
[-(2^53)+1, (2^53)-1]    =   [-9007199254740990, 9007199254740990]
```

This corresponds to the range of integers that can be exactly represented in IEEE 754 double-precision floating point.

### Number Comparison

When comparing numbers in filter expressions:
- Numbers within I-JSON exact range MUST compare using normal mathematical equality/ordering
- Numbers outside this range MAY use implementation-specific comparison

### Object Constraints

I-JSON requires no duplicate member names in objects. When the query argument conforms to I-JSON, JSONPath behavior is predictable (except for object ordering). With non-I-JSON data containing duplicate names, behavior becomes unpredictable.

## I-Regexp (RFC 9485)

The `match()` and `search()` functions use I-Regexp patterns — an interoperable regular expression subset of XSD regexps.

### Key Characteristics

- Supports Unicode scalar values (not just ASCII)
- No capture groups, lookahead, or backreferences
- Boolean matching only (test whether pattern matches)
- Subset of XML Schema Definition (XSD) regular expressions

### What I-Regexp Omits

- Character class subtraction
- Multi-character escapes (`\s`, `\S`, `\w`)
- Unicode blocks

### Common Patterns

```
"^Europe/.*"           → starts with "Europe/"
"[A-Z]ob"              → substring starting with capital letter followed by "ob"
"^[0-9]{4}-[0-9]{2}"   → starts with YYYY-MM pattern
"\p{L}+"               → one or more Unicode letters
```

### Mapping to Other Regex Engines

I-Regexp can be mapped to ECMAScript, PCRE, RE2, and Ruby regexps. The main consideration is that multi-character escapes like `\s` are not available — use explicit character classes instead (e.g., `[ \t\n\r]` for whitespace).

## Security Considerations

### Injection Attacks

JSONPath queries formed from user input must be validated and escaped. Building queries by concatenating untrusted strings can lead to injection attacks similar to SQL injection.

### Resource Exhaustion

Implementations must guard against:
- Regular expressions with catastrophic backtracking (use I-Regexp which limits this)
- Descendant segments on deeply nested structures (naive recursive implementations may stack overflow)
- Hash-table collision attacks on object member lookups

### Implementation Security

Do NOT implement JSONPath by feeding query parts to `eval()` or similar language engines. The entire syntax must be implemented natively without relying on programming language parsers.
