# Installation

## Running Without Installation

Use [uvx](https://docs.astral.sh/uv/guides/tools/) to quickly get started with ty:

```shell
uvx ty check
```

This is perfect for trying ty out without any installation.

## Installation Methods

### Adding ty to Your Project (Recommended)

Adding ty as a dependency ensures all developers use the same version:

```shell
# Add as development dependency
uv add --dev ty

# Run ty
uv run ty check

# Update ty to latest version
uv lock --upgrade-package ty
```

**Benefits:**
- Version consistency across team
- No global installation needed
- Works with `uv run` automatically

### Installing Globally with uv

```shell
# Install latest version
uv tool install ty@latest

# Update ty
uv tool upgrade ty

# Run ty directly
ty check
```

### Standalone Installer

**macOS and Linux:**
```console
# Latest version
curl -LsSf https://astral.sh/ty/install.sh | sh

# Specific version
curl -LsSf https://astral.sh/ty/0.0.29/install.sh | sh

# Using wget
wget -qO- https://astral.sh/ty/install.sh | sh
```

**Windows:**
```powershell
# Latest version
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/ty/install.ps1 | iex"

# Specific version
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/ty/0.0.29/install.ps1 | iex"
```

**Inspect installer before use:**
```console
# macOS/Linux
curl -LsSf https://astral.sh/ty/install.sh | less

# Windows
powershell -c "irm https://astral.sh/ty/install.ps1 | more"
```

### Installing from GitHub Releases

Download binaries directly from [GitHub Releases](https://github.com/astral-sh/ty/releases). Each release includes pre-built binaries for all supported platforms.

### Installing with pipx

```shell
# Install ty globally
pipx install ty

# Update ty
pipx upgrade ty
```

### Installing with pip

```shell
# Install into current Python environment
pip install ty

# Update ty
pip install --upgrade ty
```

**Note:** This installs ty into your current Python environment. Consider using `pipx` for global installation to avoid conflicts.

### Installing with mise

[mise](https://github.com/jdx/mise) is a universal runtime version manager:

```shell
# Install ty
mise install ty

# Set globally
mise use --global ty
```

### Installing in Docker

Copy the binary from the official image:

```dockerfile
COPY --from=ghcr.io/astral-sh/ty:latest /ty /bin/ty
```

**Available tags:**
- `ghcr.io/astral-sh/ty:latest`
- `ghcr.io/astral-sh/ty:0.0.29` (specific version)
- `ghcr.io/astral-sh/ty:0.0` (latest patch in 0.0.x series)

### Using with Bazel

[`aspect_rules_lint`](https://registry.bazel.build/docs/aspect_rules_lint#function-lint_ty_aspect) provides a Bazel lint aspect that runs ty. See its documentation for setup instructions.

## Shell Autocompletion

Enable shell autocompletion for ty commands:

**Bash:**
```bash
echo 'eval "$(ty generate-shell-completion bash)"' >> ~/.bashrc
```

**Zsh:**
```bash
echo 'eval "$(ty generate-shell-completion zsh)"' >> ~/.zshrc
```

**fish:**
```bash
echo 'ty generate-shell-completion fish | source' > ~/.config/fish/completions/ty.fish
```

**Elvish:**
```bash
echo 'eval (ty generate-shell-completion elvish | slurp)' >> ~/.elvish/rc.elv
```

**PowerShell:**
```powershell
if (!(Test-Path -Path $PROFILE)) {
  New-Item -ItemType File -Path $PROFILE -Force
}
Add-Content -Path $PROFILE -Value '(& ty generate-shell-completion powershell) | Out-String | Invoke-Expression'
```

Then restart the shell or source the config file:
```bash
source ~/.bashrc  # Or appropriate shell config
```

## Adding ty to Your Editor

See the [editor integration](./05-editors.md) guide to add ty to your editor for real-time type checking and language server features.

**Popular editors:**
- **VS Code:** Official extension available
- **Neovim:** Use nvim-lspconfig
- **PyCharm:** Native support (version 2025.3+)
- **Zed:** Built-in support
- **Emacs:** Use Eglot

## Verifying Installation

```shell
# Check ty version
ty --version

# Run type checker on current directory
ty check

# Generate shell completion (test it works)
ty generate-shell-completion bash | head -20
```

## Troubleshooting Installation

### "command not found" after installation

**Solution:** Ensure installation directory is in PATH:

```bash
# For standalone installer (macOS/Linux)
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Verify ty is accessible
which ty
ty --version
```

### Virtual environment not detected

**Solution:** Use `uv run` or specify Python explicitly:

```bash
# If installed as project dependency
uv run ty check

# Or specify Python environment
ty check --python ./.venv
```

### Permission denied errors

**Solution:** Check file permissions or reinstall:

```bash
# Make executable (if manually downloaded)
chmod +x /path/to/ty

# Or reinstall using installer
curl -LsSf https://astral.sh/ty/install.sh | sh
```

## Migration from Other Type Checkers

### From mypy

```bash
# Install ty instead of mypy
uv add --dev ty  # Instead of: uv add --dev mypy

# Update CI/CD commands
# Before: mypy src/
# After:  ty check src/

# Most mypy configurations work without changes
# ty supports type: ignore comments by default
```

### From Pyright

```bash
# Install ty
uv add --dev ty

# Update editor to use ty language server
# VS Code: Install ty extension (automatically disables Python extension LSP)

# pyrightconfig.json settings may need conversion to pyproject.toml
```

## Next Steps

After installation:
1. Run `ty check` in your project directory
2. Configure rules in `pyproject.toml` if needed
3. Add editor integration for real-time feedback
4. Set up CI/CD integration for automated checking
