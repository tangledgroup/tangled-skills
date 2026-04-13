# Integrations

Ruff integrates with most Python editors, IDEs, and CI/CD platforms.

## Editor Integrations

### VS Code

**Official Extension:** [ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

**Features:**
- Real-time linting
- Auto-fix on save
- Format on save
- Code actions

**Settings (`.vscode/settings.json`):**
```jsonc
{
  // Enable Ruff
  "ruff.enabled": true,
  
  // Auto-fix on save
  "ruff.fixOnSave": true,
  
  // Format with Ruff
  "ruff.formatOnSave": true,
  
  // Disable other formatters
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

### Neovim

**Using nvim-lspconfig:**
```lua
-- Install nvim-lspconfig
require('lspconfig').ruff.setup({
  settings = {
    ruff = {
      -- Ruff settings
      config = {
        line-length = 88,
      },
    },
  },
  init_options = {
    format = true,  -- Enable formatting
  },
})
```

**Using ruff.nvim (recommended):**
```lua
-- Install ruff.nvim plugin
require("ruff").setup({
  lint_command = "ruff",
  format_command = "ruff_format",
})
```

### PyCharm

**Built-in Support (2023.2+):**

1. Go to **Settings → Tools → Ruff**
2. Enable Ruff linter and formatter
3. Configure path to Ruff executable
4. Select rules to enable

**Features:**
- Real-time linting
- Auto-fix intentions
- Format on save
- Code inspections

### Vim

**Using ALE (Asynchronous Lint Engine):**
```vim
" Add to .vimrc
let g:ale_python_ruff_enabled = 1
let g:ale_python_ruff_executable = 'ruff'

" Auto-fix on save
let g:ale_linters += {'python': ['ruff']}
```

**Using coc.nvim:**
```jsonc
// .coc-settings.json
{
  "python.linting.ruffEnabled": true,
  "python.linting.ruffArgs": ["check", "--format=json"],
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.python"
  }
}
```

### Emacs

**Using eglot:**
```elisp
(with-eval-after-load 'eglot
  (add-to-list 'eglot-server-programs
               '(python-mode . ("ruff" "server"))))

(add-hook 'python-mode-hook 'eglot-ensure)
```

**Using lsp-mode:**
```elisp
(add-hook 'python-mode-hook #'lsp-enable)
(setq lsp-pythonadditional-interpreterArgs '("ruff"))
```

### Zed

Built-in support. Add to `settings.json`:

```jsonc
{
  "languages": {
    "Python": {
      "language_servers": ["ruff"]
    }
  }
}
```

## CI/CD Integrations

### GitHub Actions

**Basic Setup:**
```yaml
name: Ruff Check

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install Ruff
        run: pip install ruff
      
      - name: Run Ruff Lint
        run: ruff check .
      
      - name: Run Ruff Format Check
        run: ruff format --check .
```

**With Caching:**
```yaml
- name: Cache Ruff
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/ruff
    key: ${{ runner.os }}-ruff-${{ hashFiles('**/pyproject.toml') }}

- name: Run Ruff with cache
  run: ruff check --cache-dir ~/.cache/ruff .
```

### GitLab CI

```yaml
stages:
  - lint

ruff-lint:
  stage: lint
  image: python:3.12
  script:
    - pip install ruff
    - ruff check .
    - ruff format --check .
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

### CircleCI

```yaml
version: 2.1

jobs:
  lint:
    docker:
      - image: python:3.12
    steps:
      - checkout
      - run:
          name: Install Ruff
          command: pip install ruff
      - run:
          name: Run Ruff Lint
          command: ruff check .
      - run:
          name: Run Ruff Format Check
          command: ruff format --check .

workflows:
  lint-workflow:
    jobs:
      - lint
```

### Pre-commit Hooks

**Setup (`.pre-commit-config.yaml`):**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.10
    hooks:
      # Lint
      - id: ruff
        args: [--fix]
      
      # Format
      - id: ruff-format
```

**Install:**
```bash
pre-commit install
pre-commit run --all-files
```

## Docker Integration

### Using Ruff in Docker

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

# Install Ruff
RUN pip install ruff

# Run linting during build
RUN ruff check .

# Run formatting during build
RUN ruff format .

WORKDIR /app
COPY . .

CMD ["python", "app.py"]
```

### Multi-Stage Build with Ruff

```dockerfile
# Lint stage
FROM python:3.12-slim AS lint
RUN pip install ruff
WORKDIR /app
COPY . .
RUN ruff check . && ruff format --check .

# Build stage
FROM python:3.12-slim AS build
WORKDIR /app
COPY --from=lint /app .
RUN pip install -r requirements.txt

CMD ["python", "app.py"]
```

## IDE-Specific Tips

### VS Code

- Use `Ruff: Select Interpreter` to choose Python environment
- Enable `editor.codeActionsOnSave` for auto-fix on save
- Use `Ruff: Show Output` for debugging

### Neovim

- Use `:RuffCheck` for manual linting
- Use `:RuffFormat` for manual formatting
- Configure `diagnostic.virtual_text` for inline errors

### PyCharm

- Enable "Run inspections on save" for real-time feedback
- Use "Show Intention" to apply auto-fixes
- Configure Ruff path in Settings → Tools → Ruff

## Troubleshooting

### Editor Not Detecting Ruff

**Check Ruff is in PATH:**
```bash
which ruff
ruff --version
```

**Set explicit path in editor settings:**
```jsonc
{
  "ruff.executable": "/full/path/to/ruff"
}
```

### Auto-Fix Not Working in Editor

**Check editor settings:**
```jsonc
{
  "ruff.fixOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": true
  }
}
```

### CI/CD Failing Locally Passing

**Ensure same Ruff version:**
```yaml
- name: Install specific Ruff version
  run: pip install ruff==0.4.10
```

**Use Docker for consistency:**
```yaml
- name: Run Ruff in Docker
  run: docker run -v $(pwd):/io --rm ghcr.io/astral-sh/ruff:0.4.10 check /io
```

## Next Steps

- Configure [rules](./04-rules.md) for your project
- Set up [pre-commit hooks](https://pre-commit.com/) for local enforcement
- Customize [configuration](./06-configuration.md) for team standards
