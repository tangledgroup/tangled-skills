# Migration Guide

Migrating to Ruff from other Python linting and formatting tools.

## From Flake8

### Installation

```bash
# Install Ruff
pip install ruff

# Optionally uninstall Flake8
pip uninstall flake8
```

### Command Mapping

| Flake8 | Ruff |
|--------|------|
| `flake8 src/` | `ruff check src/` |
| `flake8 --select=E,W,F src/` | `ruff check --select=E,W,F src/` |
| `flake8 --ignore=E501 src/` | `ruff check --ignore=E501 src/` |
| `flake8 --max-line-length=100` | `ruff check --line-length=100` |

### Configuration Mapping

**Flake8 (`.flake8` or `setup.cfg`):**
```ini
[flake8]
max-line-length = 88
exclude = .venv,build,dist
extend-ignore = E501,E722
select = E,W,F,B,C4
per-file-ignores =
    __init__.py:F401
    tests/*:S101
```

**Ruff (`pyproject.toml`):**
```toml
[tool.ruff]
line-length = 88
exclude = [".venv", "build", "dist"]

[tool.ruff.lint]
ignore = ["E501", "E722"]
select = ["E", "W", "F", "B", "C4"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/*" = ["S101"]
```

### Plugin Mapping

| Flake8 Plugin | Ruff Category |
|---------------|---------------|
| Built-in | E, W, F (built-in) |
| flake8-bugbear | B |
| flake8-comprehensions | C4 |
| flake8-bandit | S |
| flake8-quotes | Q |
| flake8-print | T20 |
| flake8-simplify | SIM |
| flake8-pytest-style | PT |
| flake8-django | DJ |
| flake8-fastapi | FAST |

### noqa Comments

Flake8 `noqa` comments work with Ruff:

```python
# Works in both
x = 1  # noqa: F841

# Multiple rules (with or without space)
i = 1  # noqa: E741,F841
```

## From Black

### Installation

```bash
# Install Ruff
pip install ruff

# Optionally uninstall Black
pip uninstall black
```

### Command Mapping

| Black | Ruff |
|-------|------|
| `black src/` | `ruff format src/` |
| `black --check src/` | `ruff format --check src/` |
| `black --diff src/` | `ruff format --diff src/` |
| `black --line-length 100` | `ruff format --line-length 100` |

### Configuration Mapping

**Black (`pyproject.toml`):**
```toml
[tool.black]
line-length = 88
target-version = ['py310']
skip-string-normalization = true
```

**Ruff (`pyproject.toml`):**
```toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.format]
quote-style = "preserve"  # Equivalent to skip-string-normalization
```

### Format Suppression

Black `fmt: off/on` comments work with Ruff:

```python
# Works in both
# fmt: off
not_formatted = True
# fmt: on
```

### Compatibility

- >99.9% line compatibility on Black-formatted code
- Known deviations documented at https://docs.astral.sh/ruff/formatter/black/
- Ruff is 20-300x faster than Black

## From isort

### Installation

```bash
# Install Ruff
pip install ruff

# Optionally uninstall isort
pip uninstall isort
```

### Command Mapping

| isort | Ruff |
|-------|------|
| `isort src/` | `ruff check --select I --fix src/` |
| `isort --check-only src/` | `ruff check --select I src/` |
| `isort --diff src/` | `ruff check --select I --diff src/` |

### Configuration Mapping

**isort (`pyproject.toml`):**
```toml
[tool.isort]
profile = "black"
known_first_party = ["my_package"]
known_third_party = ["django", "flask"]
skip = [".venv", "build"]
```

**Ruff (`pyproject.toml`):**
```toml
[tool.ruff.lint]
select = ["I"]  # Enable isort rules

[tool.ruff.lint.isort]
known-first-party = ["my_package"]
known-third-party = ["django", "flask"]

[tool.ruff]
exclude = [".venv", "build"]
```

## From pyupgrade

### Installation

```bash
# Install Ruff
pip install ruff

# Optionally uninstall pyupgrade
pip uninstall pyupgrade
```

### Command Mapping

| pyupgrade | Ruff |
|-----------|------|
| `pyupgrade --py310-plus src/` | `ruff check --select UP --target-version py310 --fix src/` |

### Configuration

**Ruff:**
```toml
[tool.ruff]
target-version = "py310"

[tool.ruff.lint]
select = ["UP"]  # Enable pyupgrade rules
```

## From autoflake

### Installation

```bash
# Install Ruff
pip install ruff

# Optionally uninstall autoflake
pip uninstall autoflake
```

### Command Mapping

| autoflake | Ruff |
|-----------|------|
| `autoflake --remove-all-unused-imports src/` | `ruff check --select F401 --fix src/` |
| `autoflake --remove-unused-variables src/` | `ruff check --select F841 --fix src/` |

## From pydocstyle

### Installation

```bash
# Install Ruff
pip install ruff

# Optionally uninstall pydocstyle
pip uninstall pydocstyle
```

### Command Mapping

| pydocstyle | Ruff |
|------------|------|
| `pydocstyle src/` | `ruff check --select D src/` |

### Configuration

**Ruff:**
```toml
[tool.ruff.lint]
select = ["D"]  # Enable pydocstyle rules

[tool.ruff.lint.pydocstyle]
convention = "google"  # or "numpy", "pep257"
```

## Combined Migration (Flake8 + Black + isort)

### Before (Multiple Tools)

```bash
# Lint
flake8 --select=E,W,F,B,C4 src/

# Sort imports
isort src/

# Format
black src/
```

### After (Ruff Only)

```bash
# Lint and fix
ruff check --fix src/

# Format
ruff format src/

# Or combined
ruff check --fix src/ && ruff format src/
```

### Configuration

**Single `pyproject.toml`:**
```toml
[tool.ruff]
line-length = 88
target-version = "py310"
exclude = [".venv", "build", "dist"]

[tool.ruff.lint]
select = [
    "E", "W", "F",  # pycodestyle + Pyflakes (replaces Flake8)
    "B",            # flake8-bugbear
    "C4",           # flake8-comprehensions
    "I",            # isort
    "UP",           # pyupgrade
]

[tool.ruff.format]
# Replaces Black
quote-style = "double"
```

## Migration Strategy

### Step 1: Install Ruff

```bash
pip install ruff
```

### Step 2: Run with Defaults

```bash
# Check what Ruff finds
ruff check .

# See what can be auto-fixed
ruff check --diff
```

### Step 3: Configure Rules

Start with defaults, add rules gradually:

```toml
[tool.ruff.lint]
# Step 1: Just defaults
select = ["E4", "E7", "E9", "F"]

# Step 2: Add bugbear
extend-select = ["B"]

# Step 3: Add isort
extend-select = ["I"]

# Step 4: Add pyupgrade
extend-select = ["UP"]
```

### Step 4: Auto-Fix

```bash
# Apply safe fixes
ruff check --fix

# Format code
ruff format .
```

### Step 5: Update CI/CD

Replace old tools in CI/CD pipelines:

```yaml
# Before
- run: flake8 src/
- run: black --check src/
- run: isort --check-only src/

# After
- run: ruff check .
- run: ruff format --check .
```

### Step 6: Uninstall Old Tools (Optional)

```bash
pip uninstall flake8 black isort pyupgrade autoflake
```

## Troubleshooting

### Different Errors Than Before

Ruff may find different issues. Review and adjust rules:

```toml
[tool.ruff.lint]
# Ignore rules that don't apply to your project
ignore = ["E501", "D100"]
```

### Auto-Fix Changes Too Much

Review changes before committing:

```bash
# See what would change
ruff check --diff
ruff format --diff

# Apply only if satisfied
ruff check --fix
ruff format .
```

### Performance Issues

Ruff should be faster than old tools. If not:

```toml
[tool.ruff]
# Exclude unnecessary directories
exclude = [".venv", "node_modules", "build", "dist", "*.egg-info"]
```

## Next Steps

- Configure [rules](./04-rules.md) for your project's needs
- Set up [editor integrations](./07-integrations.md)
- Add to [CI/CD pipelines](./07-integrations.md#ci-cd-integrations)
