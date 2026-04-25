# Installation

Ruff is available through multiple package managers and installation methods.

## PyPI (Recommended)

Install Ruff via pip:

```shell
pip install ruff
```

Once installed, run from the command line:

```shell
ruff check   # Lint all files in current directory
ruff format  # Format all files in current directory
```

**Upgrade:**
```shell
pip install --upgrade ruff
```

## Homebrew

For macOS and Linux users:

```shell
brew install ruff
```

**Update:**
```shell
brew upgrade ruff
```

## Conda

For Conda users via conda-forge:

```shell
conda install -c conda-forge ruff
```

**Update:**
```shell
conda update -c conda-forge ruff
```

## pkgx

For pkgx users:

```shell
pkgx install ruff
```

## Arch Linux

Available in official repositories:

```shell
pacman -S ruff
```

## Alpine Linux

Available in testing repositories:

```shell
apk add ruff
```

## openSUSE Tumbleweed

Available in distribution repository:

```shell
sudo zypper install python3-ruff
```

## Docker

Ruff is published as `ghcr.io/astral-sh/ruff`:

```shell
# Latest version
docker run -v .:/io --rm ghcr.io/astral-sh/ruff check

# Specific version
docker run -v .:/io --rm ghcr.io/astral-sh/ruff:0.4.10 check

# Format with Docker
docker run -v .:/io --rm ghcr.io/astral-sh/ruff format
```

**Available tags:**
- `latest` - Latest release
- `0.4.10` - Specific version
- `0.4` - Latest patch in 0.4.x series

## Cargo

For Rust users (builds from source):

```shell
cargo install ruff
```

**Note:** This requires a Rust toolchain and builds Ruff from source.

## UV

For uv users:

```shell
# Add as dev dependency
uv add --dev ruff

# Run with uv
uv run ruff check

# Install globally
uv tool install ruff
```

## GitHub Releases

Download pre-built binaries directly from [GitHub Releases](https://github.com/astral-sh/ruff/releases). Each release includes binaries for:
- Linux (x86_64, aarch64, musl)
- macOS (x86_64, arm64)
- Windows (x86_64)

## Shell Autocompletion

Enable shell autocompletion after installation:

**Bash:**
```bash
echo 'eval "$(ruff generate-shell-completion bash)"' >> ~/.bashrc
```

**Zsh:**
```bash
echo 'eval "$(ruff generate-shell-completion zsh)"' >> ~/.zshrc
```

**fish:**
```bash
ruff generate-shell-completion fish > ~/.config/fish/completions/ruff.fish
```

## Verifying Installation

```shell
# Check version
ruff --version

# Check available commands
ruff --help

# Test linting
ruff check --help

# Test formatting
ruff format --help
```

## Project-Level Installation (Recommended)

For team projects, install Ruff as a development dependency:

```shell
pip install ruff
```

This ensures all developers use the same version. Pin the version in `requirements-dev.txt` or `pyproject.toml`:

```toml
[dev-dependencies]
ruff = "0.4.10"
```

## System-Wide vs Project Installation

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| pip (global) | Personal use | Simple, always available | Version conflicts between projects |
| pip (project) | Team projects | Version consistency | Requires activation |
| Homebrew/conda | System-wide | Easy updates | May lag behind PyPI |
| Docker | CI/CD | Isolated, reproducible | Slower startup |
| uv | Modern Python | Fast, integrated | Requires uv |

## Troubleshooting Installation

### "command not found" after installation

**Solution:** Ensure installation directory is in PATH:

```bash
# For pip user install
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Verify ruff is accessible
which ruff
ruff --version
```

### Permission denied errors

**Solution:** Use `--user` flag or virtual environment:

```bash
# Install for current user only
pip install --user ruff

# Or use virtual environment
python -m venv .venv
source .venv/bin/activate
pip install ruff
```

### Outdated version

**Solution:** Force upgrade:

```bash
pip install --upgrade --force-reinstall ruff
```

## Next Steps

After installation:
1. Run `ruff check` in your project directory
2. Configure rules in `pyproject.toml` if needed
3. Set up editor integration for real-time feedback
4. Add to CI/CD pipeline for automated checking
