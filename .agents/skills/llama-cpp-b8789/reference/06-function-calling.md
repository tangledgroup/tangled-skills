# Function Calling for llama.cpp b8789

## Overview

Function calling (tool use) enables LLMs to call external functions or tools. llama.cpp supports OpenAI-style function calling with native format handlers for popular model families.

**Available in:** `llama-server` with `--jinja` flag (enabled by default)

## Quick Start

### Basic Function Calling

**Start server:**
```bash
llama-server -hf ggml-org/Llama-3.1-8B-Instruct-GGUF --jinja
```

**Call with tools:**
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b",
    "messages": [{
      "role": "user",
      "content": "What is the weather in Paris?"
    }],
    "tools": [{
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "default": "celsius"
            }
          },
          "required": ["location"]
        }
      }
    }],
    "tool_choice": "auto"
  }'
```

**Response with tool call:**
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"location\": \"Paris\", \"unit\": \"celsius\"}"
        }
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

**Continue with tool result:**
```bash
curl http://localhost:8080/v1/chat/completions \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the weather in Paris?"},
      {"role": "assistant", "tool_calls": [...]},
      {
        "role": "tool",
        "tool_call_id": "call_abc123",
        "content": "{\"temperature\": 18, \"condition\": \"sunny\"}"
      }
    ]
  }'
```

## Native Format Handlers

### Supported Formats

| Format | Models | Features |
|--------|--------|----------|
| **Llama 3.x** | Llama 3.1/3.2/3.3 | Native tool calls, built-in tools |
| **Hermes 2/3 Pro** | Hermes, Qwen2.5 | Tool use templates |
| **Functionary v3.1/v3.2** | Functionary models | Parallel tool calls |
| **Mistral Nemo** | Mistral Nemo 12B | Native format |
| **FireFunction v2** | Firefunction models | Optimized tool use |
| **Command R7B** | Cohere Command R | Tool calling + reasoning |
| **DeepSeek R1** | DeepSeek R1 distills | Reasoning extraction |

### Generic Format Handler

For templates not recognized by native handlers:
- Falls back to generic tag-based parsing
- May consume more tokens
- Less efficient than native formats

**Override template:**
```bash
llama-server --chat-template-file /path/to/custom-template.jinja
```

## Built-in Tools (Experimental)

Enable server-side tools for AI agents:

```bash
llama-server -hf ggml-org/Llama-3.1-8B-Instruct-GGUF \
  --tools all
```

**Available tools:**
- `read_file` - Read file contents
- `file_glob_search` - Glob pattern file search
- `grep_search` - Grep text in files
- `exec_shell_command` - Execute shell commands
- `write_file` - Write files
- `edit_file` - Edit files with sed-style operations
- `apply_diff` - Apply patch files

**Enable specific tools:**
```bash
llama-server --tools read_file,grep_search,file_glob_search
```

**⚠️ Security Warning:** Do not enable in untrusted environments. Tools have filesystem and shell access.

## JSON Schema Constraints

Force structured output with JSON schemas:

### Via API

```bash
curl http://localhost:8080/v1/chat/completions \
  -d '{
    "messages": [{"role": "user", "content": "Create a user profile"}],
    "grammar": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0, "maximum": 150}
      },
      "required": ["name", "email"]
    }
  }'
```

### Via Server Flag

```bash
llama-server -m model.gguf \
  --json-schema '{"type":"object","properties":{"city":{"type":"string"}}}'
```

**From file:**
```bash
llama-server --json-schema-file /path/to/schema.json
```

## Parallel Tool Calls

Enable multiple simultaneous tool calls:

```bash
curl http://localhost:8080/v1/chat/completions \
  -d '{
    "messages": [{"role": "user", "content": "Get weather for Paris, London, and Tokyo"}],
    "tools": [...],
    "parallel_tool_calls": true
  }'
```

**Response:**
```json
{
  "choices": [{
    "message": {
      "tool_calls": [
        {"id": "call_1", "function": {"name": "get_weather", "arguments": "{\"location\": \"Paris\"}"}},
        {"id": "call_2", "function": {"name": "get_weather", "arguments": "{\"location\": \"London\"}"}},
        {"id": "call_3", "function": {"name": "get_weather", "arguments": "{\"location\": \"Tokyo\"}}}"
      ]
    },
    "finish_reason": "tool_calls"
  }]
}
```

## Reasoning Models with Tool Use

### DeepSeek R1 Format

Extract reasoning from thinking tags:

```bash
llama-server -hf ggml-org/DeepSeek-R1-Distill-Qwen-7B-GGUF \
  --reasoning-format deepseek
```

**Response includes:**
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "The weather in Paris is sunny with 18°C.",
      "reasoning_content": "To answer this, I need to call the get_weather function..."
    }
  }]
}
```

**Reasoning formats:**
- `none` - No extraction (tags in content)
- `deepseek` - Extract to `reasoning_content`
- `deepseek-legacy` - Keep tags + extract

### Reasoning Budget

Limit reasoning tokens:

```bash
llama-server --reasoning-budget 512 \
  --reasoning-budget-message "<|end_of_thinking|>"
```

## Chat Templates

### Template Detection

Server auto-detects template from model metadata. Check detected format:

```bash
llama-server -m model.gguf 2>&1 | grep "Chat format"
# Output: "Chat format: Llama 3.x" or "Chat format: Generic"
```

### Common Templates

| Template Name | Models |
|---------------|--------|
| `llama3` | LLaMA 3.1/3.2/3.3 |
| `gemma` | Gemma 2/3/4 |
| `qwen` | Qwen2.5, QwQ |
| `mistral-v3` | Mistral v0.3, Nemo |
| `deepseek` | DeepSeek R1/V3 |
| `command-r` | Cohere Command R |
| `chatml` | Generic ChatML format |
| `phi3` | Phi-3/3.5 |

### Override Template

```bash
# Use built-in template
llama-server --chat-template llama3

# Use custom template file
llama-server --chat-template-file /path/to/template.jinja

# Disable jinja (use raw prompts)
llama-server --no-jinja
```

## Tool Definition Best Practices

### Good Tool Definition

```json
{
  "type": "function",
  "function": {
    "name": "calculate_expression",
    "description": "Evaluate a mathematical expression and return the result. Supports basic arithmetic (+, -, *, /) and parentheses.",
    "parameters": {
      "type": "object",
      "properties": {
        "expression": {
          "type": "string",
          "description": "The mathematical expression to evaluate, e.g., '2 + 3 * 4'"
        }
      },
      "required": ["expression"],
      "additionalProperties": false
    }
  }
}
```

**Key points:**
- Clear, specific function name
- Detailed description with examples
- Explicit parameter types
- `required` array for mandatory params
- `additionalProperties: false` to prevent extra fields

### Enum Constraints

```json
{
  "properties": {
    "unit": {
      "type": "string",
      "enum": ["celsius", "fahrenheit", "kelvin"],
      "description": "Temperature unit"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "active", "completed", "cancelled"]
    }
  }
}
```

### Array Parameters

```json
{
  "properties": {
    "locations": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of city names",
      "minItems": 1,
      "maxItems": 10
    }
  }
}
```

## Error Handling

### Tool Execution Errors

When a tool call fails:

```json
{
  "messages": [
    {"role": "user", "content": "Get weather for Paris"},
    {"role": "assistant", "tool_calls": [...]},
    {
      "role": "tool",
      "tool_call_id": "call_123",
      "content": "Error: API rate limit exceeded. Please try again later."
    }
  ]
}
```

Model should handle error and respond appropriately.

### Invalid Tool Arguments

If model generates invalid JSON:
- Server returns parse error
- Model may retry with corrected arguments

**Improve with:**
- Clearer parameter descriptions
- Fewer optional parameters
- Simpler schemas

## Advanced Patterns

### Multi-Step Tool Use

Chain multiple tool calls:

```json
{
  "messages": [
    {"role": "user", "content": "Find files containing 'TODO' and count lines"},
    {"role": "assistant", "tool_calls": [{"function": {"name": "grep_search", "arguments": "{\"pattern\": \"TODO\"}"}}]},
    {"role": "tool", "content": "[{\"file\": \"main.py\", \"line\": 42}, ...]"},
    {"role": "assistant", "tool_calls": [{"function": {"name": "read_file", "arguments": "{\"path\": \"main.py\"}"}}]},
    {"role": "tool", "content": "def main():\n    # TODO: implement\n    pass"}
  ]
}
```

### Tool Selection with tool_choice

**Force specific tool:**
```json
{
  "tool_choice": {
    "type": "function",
    "function": {"name": "get_weather"}
  }
}
```

**Always use tools:**
```json
{"tool_choice": "required"}
```

**Let model decide (default):**
```json
{"tool_choice": "auto"}
```

**No tools (use natural language):**
```json
{"tool_choice": "none"}
```

## Debugging

### Enable Verbose Logging

```bash
llama-server -m model.gguf -v
```

Look for:
- `Chat format: <format>` - Detected template
- `Tool call: <name>` - Parsed tool calls
- `Parsing error` - Failed tool extraction

### Test Tool Definitions

Validate JSON schema:
```bash
echo '{"type":"object","properties":{"x":{"type":"integer"}}}' | python3 -m json.tool
```

### Check Template Compatibility

```bash
# See which template format is detected
llama-server -m model.gguf 2>&1 | grep -i "chat\|template\|format"

# Force specific template and test
llama-server --chat-template llama3 -m model.gguf
```

## Migration from Other Systems

### From OpenAI API

llama.cpp uses compatible format, but:
- Not all models support parallel tool calls
- Some models prefer native formats over generic JSON
- Response may include `reasoning_content` for reasoning models

### From LangChain

Convert tool definitions:
```python
# LangChain tool
@tool
def get_weather(location: str) -> str:
    """Get weather for a location."""
    ...

# Convert to llama.cpp format
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "Get weather for a location.",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {"type": "string"}
      },
      "required": ["location"]
    }
  }
}
```

## Performance Tips

1. **Use native format handlers** - More efficient than generic parsing
2. **Keep schemas simple** - Complex schemas increase token usage
3. **Enable parallel tool calls** - Faster for independent tools
4. **Cache frequent tool results** - Reduce redundant calls
5. **Set reasoning budgets** - Prevent excessive thinking tokens
