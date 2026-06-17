# Integrations Reference

## pre-commit

Use [`ruff-pre-commit`](https://github.com/astral-sh/ruff-pre-commit):

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.4.10
  hooks:
    - id: ruff
      args: [ --fix ]
    - id: ruff-format
```

With Jupyter notebook support:

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.4.10
  hooks:
    - id: ruff
      types_or: [ python, pyi, jupyter ]
      args: [ --fix ]
    - id: ruff-format
      types_or: [ python, pyi, jupyter ]
```

When using `--fix`, place the lint hook **before** the format hook (and before Black/isort), since Ruff's fixes may produce code that needs reformatting.

## VS Code (Official)

Install the [Ruff VS Code extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff). Supports:
- Real-time linting diagnostics
- Quick fixes via code actions
- Import sorting on save
- Formatting on save

Settings in `settings.json`:

```json
{
  "ruff.lint.args": ["--select", "E,F,I,UP,B"],
  "ruff.format.args": []
}
```

## Language Server Protocol (Official)

[`ruff-lsp`](https://github.com/astral-sh/ruff-lsp) enables Ruff in any LSP-compatible editor:

```bash
pip install ruff-lsp
```

### Neovim with `nvim-lspconfig`

```lua
require('lspconfig').ruff_lsp.setup {
  init_options = {
    settings = {
      args = {},  -- Extra CLI args
    }
  }
}
```

### Neovim with `conform.nvim`

```lua
require("conform").setup({
    formatters_by_ft = {
        python = { "ruff_fix", "ruff_format" },
    },
})
```

### Neovim with `nvim-lint`

```lua
require("lint").linters_by_ft = {
  python = { "ruff" },
}
```

## Unofficial LSP Plugin

[`python-lsp-ruff`](https://github.com/python-lsp/python-lsp-ruff) for [`python-lsp-server`](https://github.com/python-lsp/python-lsp-server):

```bash
pip install python-lsp-server python-lsp-ruff
```

Neovim config:

```lua
require'lspconfig'.pylsp.setup {
  settings = {
    pylsp = {
      plugins = {
        ruff = { enabled = true },
        pycodestyle = { enabled = false },
        pyflakes = { enabled = false },
        mccabe = { enabled = false }
      }
    }
  }
}
```

## Vim / Neovim (ALE)

```vim
let g:ale_linters = { "python": ["ruff"] }
let g:ale_fixers = { "python": ["black", "ruff"] }
```

## PyCharm

### External Tool

Add Ruff as an External Tool in Preferences → Tools → External Tools. Configure the program path to `ruff` and arguments to `check $FilePath$`.

### Unofficial Plugin

[Ruff](https://plugins.jetbrains.com/plugin/20574-ruff) plugin on IntelliJ Marketplace (maintained by @koxudaxi).

## Emacs

### flymake-ruff

```elisp
(require 'flymake-ruff)
(add-hook 'python-mode-hook #'flymake-ruff-load)
```

### emacs-ruff-format

```elisp
(require 'ruff-format)
(add-hook 'python-mode-hook 'ruff-format-on-save-mode)
```

### Apheleia

```emacs-lisp
(add-to-list 'apheleia-mode-alist '(python-mode . ruff))
(add-to-list 'apheleia-mode-alist '(python-ts-mode . ruff))
```

## Other Editors

| Editor | Integration |
|---|---|
| TextMate | [`textmate2-ruff-linter`](https://github.com/vigo/textmate2-ruff-linter) |
| Sublime Text | Via `ruff-lsp` |
| Helix | Via `ruff-lsp` |
| coc.nvim | Via [`coc-pyright`](https://github.com/fannheyward/coc-pyright) |

## GitHub Actions

### Native Step

```yaml
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ruff
      - run: ruff check --output-format=github .
```

### ruff-action

```yaml
name: Ruff
on: [push, pull_request]
jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: chartboost/ruff-action@v1
```

With custom configuration:

```yaml
- uses: chartboost/ruff-action@v1
  with:
    version: 0.4.10
    args: check --select E,F,B
    src: "./src"
```

## Docker

Ruff is published as `ghcr.io/astral-sh/ruff`:

```bash
docker run -v .:/io --rm ghcr.io/astral-sh/ruff check
docker run -v .:/io --rm ghcr.io/astral-sh/ruff:0.4.10 check
```

## Shell Autocompletion

```bash
ruff generate-shell-completion zsh   > ~/.zfunc/_ruff
ruff generate-shell-completion bash  >> ~/.bashrc
ruff generate-shell-completion fish  > ~/.config/fish/completions/ruff.fish
```

Supported shells: `bash`, `elvish`, `fig`, `fish`, `powershell`, `zsh`.

## Migration from Flake8 + Black + isort

1. Install Ruff: `pip install ruff`
2. Create `ruff.toml` with equivalent rule selection
3. Run `ruff check --add-noqa .` to suppress existing violations
4. Run `ruff format .` to apply formatting
5. Remove flake8, Black, isort from dependencies and CI
6. Gradually remove `# noqa` comments as you fix violations

Typical config replacing common Flake8 plugins:

```toml
line-length = 88
target-version = "py310"

[lint]
select = [
    "E",      # pycodestyle errors
    "F",      # Pyflakes
    "I",      # isort
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "SIM",    # flake8-simplify
]
ignore = ["E501"]   # Let formatter handle line length

[format]
quote-style = "double"
```
