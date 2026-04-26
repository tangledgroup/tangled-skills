# Grammar-Constrained Generation

## GBNF Grammars

GBNF (GGML BNF) defines formal grammars to constrain model outputs. Use it to force valid JSON, specific formats, or custom output structures.

### Basic Syntax

Rules use `::=` to define production:

```gbnf
root ::= "- " item+
item ::= text "\n"
text ::= [^\n]+
```

- **Terminals**: characters in quotes (`"1"`) or ranges (`[a-z]`, `[0-9]`)
- **Non-terminals**: dashed lowercase names (`move`, `check-mate`)
- **Alternatives**: `|` operator
- **Repetition**: `*` (zero+), `+` (one+), `?` (optional), `{m,n}` (range)
- **Negation**: `[^\n]` for negated character classes
- **Comments**: `# comment`

### Token Matching

Match specific tokenizer tokens rather than character sequences:

```gbnf
# Using token IDs
root ::= <[1000]> content <[1001]>
content ::= !<[1001]>*

# Using token strings (must be single vocab tokens)
root ::= <think> thinking </think>
thinking ::= !</think>*
```

### Example: JSON Grammar

```gbnf
root ::= item
item ::= "{" whitespace (string ":" value ("," whitespace string ":" value)*)? "}"
value ::= string | number | "true" | "false" | "null" | array | object
string ::= "\"" ([^"\\] | "\\" *)* "\""
number ::= ("-"? [0-9]+ ("." [0-9]+)? ([eE] [-+]? [0-9]+)?)
array ::= "[" (value ("," value)*)? "]"
object ::= item
whitespace ::= [ \t\n\r]*
```

### Using Grammars

In `llama-cli`:

```bash
# Grammar file
llama-cli -m model.gguf --grammar-file grammars/json.gbnf -p 'Generate JSON:'

# Inline grammar
llama-cli -m model.gguf --grammar 'root ::= "hello" | "world"' -p 'Say something:'
```

In `llama-server` (via `/completion` endpoint):

```json
{
  "prompt": "Generate a person object:",
  "grammar": "root ::= \"{\" \"name\" \":\" string \"}\""
}
```

## JSON Schema to Grammar

llama.cpp converts JSON schemas to GBNF grammars automatically. This is the preferred method for structured output.

### Via CLI

```bash
llama-cli -m model.gguf \
  -j '{"type":"object","properties":{"name":{"type":"string"},"age":{"type":"integer"}},"required":["name","age"]}' \
  -p 'Generate a person:'
```

### Via Server API

In `/v1/chat/completions`, use `response_format`:

```json
{
  "messages": [{"role": "user", "content": "List actors."}],
  "response_format": {
    "type": "json_schema",
    "schema": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "age": {"type": "integer"}
        },
        "required": ["name", "age"]
      }
    }
  }
}
```

### Via `/completion` Endpoint

Use the `json_schema` field:

```json
{
  "prompt": "Generate:",
  "json_schema": {"type": "object", "properties": {"result": {"type": "string"}}}
}
```

### Schema Conversion Tool

Convert schemas ahead of time:

```bash
python3 examples/json_schema_to_grammar.py schema.json > grammar.gbnf
```

### Supported Schema Features

- `type`: string, integer, number, boolean, null, array, object
- `properties`, `required`
- `minItems`, `maxItems`
- `minLength`, `maxLength`
- `minimum`, `maximum` (integer only)
- `pattern` (must start with `^` and end with `$`)
- `$ref` (limited support, nested refs broken)

### Unsupported Features

- `additionalProperties: true` defaults to `false` in GBNF conversion
- `uniqueItems`, `contains`, `if/then/else`, `not`, `patternProperties`
- Remote `$ref`s in C++ version
- String formats `uri`, `email`

## LLGuidance

LLGuidance is an alternative grammar engine with better JSON Schema coverage. Requires Rust to build:

```bash
cmake -B build -DLLAMA_LLGUIDANCE=ON
cmake --build build --config Release
```

When enabled, grammars starting with `%llguidance` and JSON schema requests use LLGuidance instead of GBNF. It uses a lexer/parser split for ~10x faster performance on large vocabularies and adheres more closely to the JSON Schema specification.

## Performance Tips

- Use `{0,N}` instead of `x? x? x?...` (N times) — the latter causes exponential backtracking
- For complex schemas, use LLGuidance if available
- Grammar sampling adds latency per token — measure with `--perf`
- The JSON schema is not injected into the prompt — describe expected structure explicitly in your prompt
