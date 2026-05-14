# Installation

## Quick Install

**macOS and Linux:**

```bash
curl -fsSL https://deno.land/install.sh | sh
```

This installs Deno to `~/.deno/bin/deno` and adds it to your PATH.

**Windows (PowerShell):**

```powershell
irm https://deno.land/install.ps1 | iex
```

## Verify Installation

```bash
deno --version
```

Output shows Deno, V8, and TypeScript versions.

## Alternative Installation Methods

**Homebrew (macOS/Linux):**

```bash
brew install deno
```

**Chocolatey (Windows):**

```bash
choco install deno
```

**npm (global install):**

```bash
npm install -g deno
```

**APT repository (Debian/Ubuntu):**

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deno.land/install.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/deno.gpg
echo "deb [signed-by=/etc/apt/keyrings/deno.gpg] https://ppa.deno.land/release/stable stable main" | sudo tee /etc/apt/sources.list.d/deno-stable.list
sudo apt update
sudo apt install deno
```

**YUM repository (Fedora/RHEL):**

```bash
sudo mkdir -p /etc/yum.repos.d/
curl -fsSL https://deno.land/install.yum | sudo tee /etc/yum.repos.d/deno.repo
sudo yum install deno
```

## Updating Deno

Use the built-in upgrade command:

```bash
deno upgrade          # Upgrade to latest stable
deno upgrade 2.0.0   # Upgrade to specific version
deno upgrade --canary # Upgrade to latest canary build
```

## Uninstalling

```bash
# Remove binary and deno directory
deno uninstall
```

Or manually remove `~/.deno` directory and PATH entries.

## Environment Variables

Key environment variables for Deno:

- `DENO_DIR` — Override the default cache directory (`~/.deno`)
- `DENO_CACHE_DIR` — Override the download cache location
- `DENO_INSTALL_ROOT` — Override install directory for `deno install` scripts
- `DENO_TLS_CA_STORE` — Control TLS certificate stores (e.g., `system`, `mozilla`)
- `DENO_TRACE_PERMISSIONS=1` — Enable stack traces for permission requests
- `DENO_AUDIT_PERMISSIONS=<path>` — Write permission access audit log to file (JSONL format)
- `DENO_FUTURE` — Enable future features that may change behavior

## Shell Completion

Generate shell completions:

```bash
deno completions bash   # For bash
deno completions zsh    # For zsh
deno completions fish   # For fish
```

Source the generated script in your shell configuration.
