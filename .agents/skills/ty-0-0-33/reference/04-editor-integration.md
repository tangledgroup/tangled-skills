# Editor Integration

ty provides a full-featured language server (LSP) for Python. Start it with `ty server`.

## VS Code

Install the official [ty extension](https://marketplace.visualstudio.com/items?itemName=astral-sh.ty) from the VS Code Marketplace.

The extension automatically sets `python.languageServer` to `"None"` to avoid running two language servers. To use ty only for type checking with another LSP for other features:

```json
{
  "python.languageServer": "Pylance",
  "ty.disableLanguageServices": true
}
```

## Neovim

Use [nvim-lspconfig](https://github.com/neovim/nvim-lspconfig):

Neovim >= 0.11:
```lua
vim.lsp.config('ty', {
  settings = {
    ty = {
      -- ty language server settings
    }
  }
})
vim.lsp.enable('ty')
```

Neovim < 0.11:
```lua
require('lspconfig').ty.setup({
  settings = {
    ty = {
      -- ty language server settings
    }
  }
})
```

## Zed

ty is included with Zed out of the box. Enable ty and disable basedpyright:

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

Starting with version 2025.3, enable native ty support in Settings → Python → Tools → ty. Choose Interpreter mode (searches installed packages) or Path mode (searches `$PATH`).

## Emacs

Use the built-in Eglot client (Emacs 29+):

```elisp
(with-eval-after-load 'eglot
  (add-to-list 'eglot-server-programs
               '(python-base-mode . ("ty" "server"))))
(add-hook 'python-base-mode-hook 'eglot-ensure)
```

## Other Editors

ty works with any LSP-compatible editor. Start the server with:

```bash
ty server
```

## Language Server Features

### Diagnostics

Type errors and other diagnostics appear directly in your editor, updated as you type. Supports both "pull" (on-demand) and "push" models. Configure scope with `diagnosticMode`:
- `openFilesOnly` (default) — only open files
- `workspace` — all workspace files
- `off` — disable diagnostics

### Code Navigation

- **Go to Definition** — jump to symbol definition
- **Go to Declaration** — navigate to declaration site (may be in stub file)
- **Go to Type Definition** — navigate to the type of a symbol
- **Find All References** — find every usage across workspace
- **Document/Workspace Symbols** — outline and search symbols

### Code Completions

Intelligent suggestions for variables, functions, classes, and modules. Auto-import actions add missing `import` statements.

### Code Actions and Refactorings

- **Add import** — automatically add missing imports
- **Quick fixes** — resolve diagnostic issues
- **Rename symbol** — safe cross-codebase renaming
- **Selection range** — expand/shrink selection based on syntax

### Contextual Information

- **Hover** — type, documentation, function signatures, variance info
- **Inlay hints** — inline type hints for unannotated variables/parameters; double-click to insert. Supports "baking" keyword argument inlay hints into source code (v0.0.33). Go-to-definition from literal enum member inlay hints (v0.0.33).
- **Signature help** — function parameters and types at call sites
- **Document highlight** — highlight all occurrences of a symbol
- **Semantic highlighting** — syntax highlighting based on semantics and types. Unreachable code is dimmed (v0.0.32+). Unresolved symbols are omitted from highlighting (v0.0.33).

### Code Folding

Python-specific folding ranges, including docstrings tagged as comments.

### Notebook Support

Jupyter notebooks (`.ipynb`) are supported with diagnostics, completions, and other features working across cells.

### Fine-Grained Incrementality

ty updates only affected parts of the codebase on changes — down to individual definitions. This provides instant feedback within milliseconds, even on large projects. Fine-grained dependencies also allow skipping irrelevant third-party code.

## LSP Feature Support

Supported: `textDocument/codeAction`, `textDocument/completion`, `textDocument/declaration`, `textDocument/definition`, `textDocument/diagnostic`, `textDocument/documentHighlight`, `textDocument/documentSymbol`, `textDocument/foldingRange`, `textDocument/hover`, `textDocument/inlayHint`, `textDocument/prepareRename`, `textDocument/references`, `textDocument/rename`, `textDocument/selectionRange`, `textDocument/semanticTokens`, `textDocument/signatureHelp`, `textDocument/typeDefinition`, `workspace/diagnostic`, `workspace/symbol`, `notebookDocument/*`.

Not supported: `callHierarchy/*`, `textDocument/codeLens`, `textDocument/documentColor`, `textDocument/documentLink`, `textDocument/implementation`, `typeHierarchy/*`, `workspace/willRenameFiles`.

Formatting is delegated to [Ruff](https://docs.astral.sh/ruff/).

## Editor Settings Reference

### configuration

Inline editor settings (takes precedence over config files):

```json
{
  "ty.configuration": {
    "rules": {
      "unresolved-reference": "warn"
    }
  }
}
```

### configurationFile

Path to `ty.toml` (expands `~` and `$VAR`):

```json
{
  "ty.configurationFile": "./.config/ty.toml"
}
```

### disableLanguageServices

Disable language services (completions, hover, etc.), keeping only type checking:

```json
{
  "ty.disableLanguageServices": true
}
```

### diagnosticMode

Control diagnostic scope: `"off"`, `"openFilesOnly"` (default), `"workspace"`.

### showSyntaxErrors

Show or hide syntax error diagnostics (default: `true`):

```json
{
  "ty.showSyntaxErrors": false
}
```

### inlayHints

Control inline hints:
- `variableTypes` — show variable types (default: `true`)
- `parameterNames` — show parameter names at call sites
- `missingReturns` — show missing return type hints
