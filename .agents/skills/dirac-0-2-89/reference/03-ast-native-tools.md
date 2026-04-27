# AST-Native Tools

## Tree-Sitter Integration

Dirac embeds `web-tree-sitter` to parse source files into Abstract Syntax Trees. Language parsers are loaded on-demand via `loadRequiredLanguageParsers()` based on file extension. Supported languages include TypeScript, JavaScript, Python, C++, Go, Rust, Java, Ruby, PHP, and others with corresponding tree-sitter grammars.

Parser queries use tree-sitter's named capture syntax to identify definitions and references:

- `@name.definition.function` — Function name identifiers
- `@name.definition.method` — Method name identifiers
- `@name.definition.class` — Class name identifiers
- `@name.definition.interface` — Interface name identifiers
- `@name.reference` — Symbol references (calls, accesses)
- `@definition.*` — Full definition blocks (used for line counting and scope analysis)

Query files live in `src/services/tree-sitter/queries/`.

## ASTAnchorBridge

The `ASTAnchorBridge` class (`src/utils/ASTAnchorBridge.ts`) bridges AST parsing with the anchor system. It provides three core operations:

### getFileSkeleton()

Extracts definition lines from a file with their stable anchors and optional metadata:

```
|----
│Apple§class DynamicCache
│    # Lines: 42
│    # Calls: [update, get_seq_length]
│Bison§def __init__(self):
│    # Lines: 8
│Cider§def update(self, layer_past, present):
│    # Lines: 15
│    # Calls: [get_seq_length]
|----
```

When `showCallGraph` is enabled, each function/method definition includes its line count and a sorted list of other defined functions it calls within its body. This gives the LLM structural awareness without reading full file contents.

### getFunctions()

Retrieves specific functions by name with their full source code and anchors:

```
src/cache.py::DynamicCache.update
[Function Hash: a3f2b1c4]
All Hash Anchors provided below are stable and can be used with edit_file directly.
Cider§def update(self, layer_past, present):
Dingo§    key_states = ...
...
```

Supports fully qualified names (`ClassName.methodName`) and partial matching. Uses the `SymbolContextResolver` to include relevant type context around the function.

### getSymbolRange()

Finds the exact byte range of a symbol definition for replacement operations. Handles wrapper nodes (export statements, decorators, ambient declarations) and includes preceding comments/decorators in the range.

## Available AST Tools

### get_file_skeleton

Returns AST definition lines with anchors for one or more files. Auto-approved by default. Supports call graph metadata showing line counts and inter-function calls.

### get_function

Retrieves specific named functions/methods from a file with full source code and stable anchors. The returned content can be used directly with `edit_file` since all anchors are included.

### find_symbol_references

Finds all references to a given symbol across the codebase using the Symbol Index Service. Returns locations with file paths, line numbers, and reference types (definition vs. usage).

### replace_symbol

Replaces all occurrences of a symbol name throughout the codebase. Uses AST-aware matching to avoid false positives in strings or comments. Operates on the symbol index for efficiency.

### rename_symbol

Similar to `replace_symbol` but with additional validation that the new name is valid for the target language and doesn't conflict with existing symbols.

## SymbolIndexService

The `SymbolIndexService` (`src/services/symbol-index/`) maintains a persistent index of all symbols in the workspace:

- Scans supported file extensions (`.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.rs`, `.go`, `.c`, `.cpp`, `.h`, etc.)
- Stores symbol names, types (definition/reference), kinds (function/class/method), and source ranges
- Persists to disk with file modification time tracking for incremental updates
- Excludes common directories: `node_modules`, `.git`, `dist`, `build`, `__pycache__`, `.venv`, etc.
- Uses `p-limit` for concurrent file processing

The index enables fast symbol lookup without re-parsing files, making `find_symbol_references` and `replace_symbol` operations efficient even on large codebases.

## parseFile() Core Logic

The `parseFile()` function in `src/services/tree-sitter/index.ts`:

1. Reads file content
2. Loads the appropriate language parser and query
3. Parses into AST via `parser.parse(fileContent)`
4. Applies tree-sitter query to get named captures
5. Sorts captures by start position
6. For each `name.definition` capture, extracts:
   - Line index
   - Full line text
   - Indentation level
   - Optional: line count of the definition block
   - Optional: list of called functions (call graph)
7. Deduplicates by line index
