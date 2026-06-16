# Language Server and Editor Integration

## Supported LSP features

ty implements a comprehensive set of LSP capabilities:

| Feature | Status |
|---------|--------|
| Diagnostics (pull + push) | ✅ |
| Go to Definition / Declaration / Type Definition | ✅ |
| Find All References | ✅ |
| Document / Workspace Symbols | ✅ |
| Code Completions (with auto-import) | ✅ |
| Hover | ✅ |
| Inlay Hints (variable types, parameter names) | ✅ |
| Signature Help | ✅ |
| Rename Symbol | ✅ |
| Code Actions / Quick Fixes | ✅ |
| Document Highlight | ✅ |
| Semantic Highlighting | ✅ |
| Selection Range | ✅ |
| Code Folding | ✅ |
| Call Hierarchy | ✅ |
| Type Hierarchy | ✅ |
| Notebook (`.ipynb`) Support | ✅ |
| CodeLens | ❌ |
| Document Color / Document Link | ❌ |
| Implementation | ❌ |
| File Rename Will-Rename | ❌ |

Formatting is intentionally delegated to [Ruff](https://docs.astral.sh/ruff/).

## Fine-grained incrementality

ty updates only affected parts of the codebase when files change, down to individual definitions. This provides sub-millisecond feedback in the IDE, even on large projects. Dependencies on third-party packages are also skipped when irrelevant to the current file.

## Diagnostic modes

Controlled via `diagnosticMode` editor setting:

- `openFilesOnly` (default) — diagnostics only for open files
- `workspace` — diagnostics for all files in the workspace
- `off` — no diagnostics (useful if ty is only used for completions/hover)

## VS Code

Install the official [ty extension](https://marketplace.visualstudio.com/items?itemName=astral-sh.ty). It automatically disables the Python extension's language server by setting `python.languageServer` to `"None"`.

To use ty only for type checking with another LSP for features:

```json
{
  "python.languageServer": "Pylance",
  "ty.disableLanguageServices": true
}
```

### VS Code-specific settings

```json
{
  "ty.importStrategy": "fromEnvironment",     // or "useBundled"
  "ty.interpreter": ["/path/to/python"],
  "ty.path": ["/path/to/ty"],
  "ty.trace.server": "off"                    // off, messages, verbose
}
```

## Neovim

### Neovim >= 0.11 (recommended)

```lua
vim.lsp.config('ty', {
  settings = {
    ty = {
      -- configuration here
    }
  }
})
vim.lsp.enable('ty')
```

### Neovim < 0.11

```lua
require('lspconfig').ty.setup({
  settings = {
    ty = {
      -- configuration here
    }
  }
})
```

## Zed

ty is built into Zed. Enable it and disable basedpyright:

```json
{
  "languages": {
    "Python": {
      "language_servers": ["ty", "ruff"]
    }
  }
}
```

Override the binary path:

```json
{
  "lsp": {
    "ty": {
      "binary": {
        "path": "/home/user/.local/bin/ty",
        "arguments": ["server"]
      }
    }
  }
}
```

## PyCharm

Starting with version 2025.3:

1. Go to **Python | Tools | ty** in Settings
2. Enable the checkbox
3. Choose Execution mode:
   - **Interpreter**: searches installed packages
   - **Path**: searches `$PATH` or custom path

## Emacs

```elisp
(with-eval-after-load 'eglot
  (add-to-list 'eglot-server-programs
               '((python-base-mode :language-id "python") . ("ty" "server"))))
(add-hook 'python-base-mode-hook 'eglot-ensure)
```

For Flycheck integration, use [flycheck-eglot](https://github.com/flycheck/flycheck-eglot).

## Other editors

Any LSP-compatible editor works. Start the server with:

```bash
ty server
```

## Common editor settings

### Configuration (inline)

```json
{
  "ty.configuration": {
    "rules": {
      "unresolved-reference": "warn"
    }
  }
}
```

Inline settings always take precedence over config files.

### Inlay hints

```json
{
  "ty.inlayHints.variableTypes": true,       // Default: true
  "ty.inlayHints.callArgumentNames": true    // Default: true
}
```

### Completions

```json
{
  "ty.completions.autoImport": true,                    // Default: true
  "ty.completions.completeFunctionParentheses": false   // Default: false
}
```

### Syntax errors

```json
{
  "ty.showSyntaxErrors": true   // Default: true. Set false if another LSP handles syntax.
}
```

### Logging (initialization options)

These require editor restart to take effect.

```json
// VS Code
{
  "ty.logFile": "/path/to/ty.log",
  "ty.logLevel": "debug"    // trace, debug, info, warn, error
}
```

```lua
-- Neovim >= 0.11
vim.lsp.config('ty', {
  init_options = {
    logFile = '/path/to/ty.log',
    logLevel = 'debug',
  },
})
```
