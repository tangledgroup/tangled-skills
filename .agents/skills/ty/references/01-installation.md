# Installation Methods

## Running without installation

Use `uvx` for ephemeral execution:

```bash
uvx ty check
```

This is the fastest way to try ty without any persistent install.

## Adding to a project (recommended)

Add ty as a dev dependency so all team members use the same version:

```bash
uv add --dev ty
uv run ty check
```

To update:

```bash
uv lock --upgrade-package ty
```

## Global installation with uv

```bash
uv tool install ty@latest
ty check
```

Update with `uv tool upgrade ty`.

## Standalone installer

### macOS and Linux

```bash
curl -LsSf https://astral.sh/ty/install.sh | sh
```

Pin a specific version:

```bash
curl -LsSf https://astral.sh/ty/0.0.49/install.sh | sh
```

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/ty/install.ps1 | iex"
```

## GitHub Releases

Download binaries directly from [GitHub Releases](https://github.com/astral-sh/ty/releases). Each release includes binaries for all supported platforms.

## pip / pipx

```bash
pip install ty
# or
pipx install ty
```

Update: `pipx upgrade ty`

## mise

```bash
mise install ty
mise use --global ty
```

## Docker

```dockerfile
COPY --from=ghcr.io/astral-sh/ty:latest /ty /bin/
```

Available tags:

- `ghcr.io/astral-sh/ty:latest`
- `ghcr.io/astral-sh/ty:0.0.49` (specific version)
- `ghcr.io/astral-sh/ty:0.0` (latest patch)

## Bazel

Use [`aspect_rules_lint`](https://registry.bazel.build/docs/aspect_rules_lint#function-lint_ty_aspect) which provides a lint aspect that runs ty.

## Shell autocompletion

Add to your shell config:

```bash
# Bash
echo 'eval "$(ty generate-shell-completion bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(ty generate-shell-completion zsh)"' >> ~/.zshrc

# Fish
echo 'ty generate-shell-completion fish | source' > ~/.config/fish/completions/ty.fish
```

Supported shells: bash, zsh, fish, elvish, powershell.

## Pre-commit hook

A pre-commit integration is available at <https://github.com/astral-sh/ty-pre-commit>. Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ty-pre-commit
    rev: 0.0.49
    hooks:
      - id: ty
```

## Version policy

ty uses `0.0.x` versioning with no stable API guarantee. Breaking changes, including diagnostic changes, can occur between any two versions. Track the [type system features issue](https://github.com/astral-sh/ty/issues/1889) for a detailed overview of supported features.
