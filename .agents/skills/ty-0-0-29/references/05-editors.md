# Editor Integration

ty provides a language server with code navigation, completions, code actions, auto-import, inlay hints, on-hover help, and fine-grained incremental analysis.

## VS Code

### Official Extension

Install the [ty extension](https://marketplace.visualstudio.com/items?itemName=astral-sh.ty) from the VS Code Marketplace.

**Features:**
- Automatic type checking
- Real-time diagnostics
- Code navigation (go to definition, find references)
- Auto-completions with type information
- Inlay hints
- Code actions
- Hover information

### Configuration

The extension automatically disables the language server from the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) by setting `python.languageServer` to `"None"`.

**Use ty only for type checking (keep other LSP features):**

```jsonc
// .vscode/settings.json or User/Workspace settings
{
  "python.languageServer": "Pylance",  // Or "Pyright"
  "ty.disableLanguageServices": true,  // Disable ty LSP, keep type checking
}
```

**Use ty as primary language server (default):**

```jsonc
{
  "python.languageServer": "None",  // Disabled by ty extension
  "ty.disableLanguageServices": false,  // Enable full LSP features
}
```

### Additional Settings

See [editor settings reference](https://ty.dev/reference/editor-settings) for complete configuration options.

## Neovim

### Using nvim-lspconfig (Recommended)

After installing the [nvim-lspconfig](https://github.com/neovim/nvim-lspconfig) extension:

**Neovim >= 0.11:**
```lua
-- Optional: Update language server settings
vim.lsp.config('ty', {
  settings = {
    ty = {
      -- ty language server settings go here
    }
  }
})

-- Required: Enable the language server
vim.lsp.enable('ty')
```

**Neovim < 0.11:**
```lua
require('lspconfig').ty.setup({
  settings = {
    ty = {
      -- ty language server settings go here
    }
  }
})
```

### Manual Configuration

If not using nvim-lspconfig, copy [the ty configuration](https://github.com/neovim/nvim-lspconfig/blob/master/lsp/ty.lua) manually.

### Features

- Real-time type checking
- Go to definition
- Find references
- Hover information
- Completions
- Inlay hints
- Code actions

## Zed

ty is included with Zed out of the box (no extension required).

### Enable ty as Primary LSP

The default primary LSP for Python is basedpyright. Enable ty by adding to `settings.json`:

```json
{
  "languages": {
    "Python": {
      "language_servers": [
        "ty",      // Enable ty
        "ruff"     // Also enable ruff for linting
      ]
    }
  }
}
```

Other built-in servers (basedpyright, pyright, pylsp) are disabled by omission.

### Override ty Executable

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

See [Zed's documentation](https://zed.dev/docs/languages/python#configure-python-language-servers-in-zed) for more information.

## PyCharm

Native ty support is available starting with version 2025.3.

### Enable ty

1. Go to **Settings → Python → Tools → ty**
2. Select the **Enable** checkbox
3. Configure execution mode:

**Interpreter mode:**
- PyCharm searches for ty in your interpreter's packages
- Click _Install ty_ to install for selected interpreter

**Path mode:**
- PyCharm searches for ty in `$PATH`
- Browse to specify path if not found

4. Select which options to enable (type checking, language server features)

See [PyCharm documentation](https://www.jetbrains.com/help/pycharm/lsp-tools.html#ty) for more information.

## Emacs

Use the built-in [Eglot](https://www.gnu.org/software/emacs/manual/html_node/eglot/index.html) client (Emacs 29+):

```elisp
;; Add to your Emacs config (.emacs or init.el)
(with-eval-after-load 'eglot
  (add-to-list 'eglot-server-programs
               '(python-base-mode . ("ty" "server"))))

(add-hook 'python-base-mode-hook 'eglot-ensure)
```

**Features:**
- Real-time diagnostics
- Code navigation
- Completions
- Hover information

## Other Editors

ty can be used with any editor supporting the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/).

### Start Language Server

```shell
ty server
```

### Common LSP Clients

- **Sublime Text:** Use `LSP` package
- **Vim:** Use `coc.nvim`, `nvim-lspconfig`, or `lsp.vim`
- **Helix:** Add to `languages.toml`
- **Kate:** Built-in LSP support

Refer to your editor's documentation for LSP configuration.

## Language Server Features

### Type Checking

Real-time type checking with immediate feedback as you type.

### Code Navigation

- **Go to Definition:** Jump to function/class/variable definitions
- **Find References:** Find all uses of a symbol
- **Go to Type Definition:** Jump to type annotations

### Completions

Context-aware completions with full type information:
- Function parameters
- Class attributes
- Module imports
- Type annotations

### InlayHints

Automatic inline type hints:
```python
def greet(name: str) -> str:
    message: str = f"Hello, {name}"  # Type shown inline
    return message
```

### Hover Information

Hover over symbols to see:
- Type information
- Docstrings
- Function signatures
- Variable types

### Code Actions

Quick fixes for common issues:
- Import missing modules
- Fix type errors
- Extract variables
- Organize imports

### Fine-Grained Incrementality

ty uses fine-grained incremental analysis designed for fast updates when editing files:
- Only re-analyze changed portions
- Track dependencies between files
- Provide instant feedback during editing

## Configuration

Editor-specific settings can be configured in your editor's configuration files or globally in `pyproject.toml`:

```toml
[tool.ty]
# Global ty settings apply to both CLI and language server

[tool.ty.rules]
possibly-unresolved-reference = "warn"

[tool.ty.environment]
python-version = "3.12"
```

See [editor settings reference](https://ty.dev/reference/editor-settings) for editor-specific configuration options.

## Troubleshooting

### Language Server Not Starting

**Check ty is installed and in PATH:**
```shell
ty --version
which ty
```

**Verify server command works:**
```shell
ty server --help
```

### Diagnostics Not Showing

**Check editor logs:**
- VS Code: Developer Tools → Console
- Neovim: `:LspLog`
- PyCharm: Event Log

**Restart language server:**
- VS Code: Command Palette → "ty: Restart Server"
- Neovim: `:LspRestart`

### Slow Performance

**Check project size:** Large projects may take longer for initial analysis

**Configure exclusions:** Skip generated code or third-party modules

**Enable caching:** ty caches analysis results for faster subsequent runs

### Type Information Inaccurate

**Ensure virtual environment is detected:**
```toml
[tool.ty.environment]
python = "./.venv"
```

**Check Python version matches:**
```toml
[tool.ty.environment]
python-version = "3.12"
```

## Best Practices

1. **Use official extensions when available** - Better integration and support
2. **Configure python-version** - Ensures accurate type checking for target Python version
3. **Enable inlay hints** - Improves code readability during development
4. **Set up pre-commit hooks** - Run `ty check` before commits
5. **Use watch mode in terminal** - Complement LSP with `ty check --watch`

## Next Steps

- Configure [rules](./03-rules.md) for your project's needs
- Set up [suppression](./04-suppression.md) for false positives
- Customize [configuration](./07-configuration.md) for advanced settings
- Integrate with CI/CD for automated type checking
