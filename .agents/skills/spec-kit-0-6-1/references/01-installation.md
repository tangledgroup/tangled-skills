# Installation and Upgrade Guide

Detailed installation procedures, upgrade workflows, and troubleshooting for Spec Kit 0.6.1.

## Prerequisites Checklist

Before installing Spec Kit, ensure you have:

- [ ] **uv** installed (https://docs.astral.sh/uv/)
- [ ] **Python 3.11+** installed
- [ ] **Git** installed and configured
- [ ] AI coding agent selected and installed:
  - Claude Code CLI
  - GitHub Copilot (VS Code extension)
  - Gemini CLI
  - Pi Coding Agent
  - Codebuddy CLI
  - Windsurf IDE
  - Cursor IDE
  - Or other supported agents

## Installation Methods

### Method 1: Persistent Installation (Recommended)

Install the `specify` CLI tool once for global use:

```bash
# Install from stable release v0.6.1 (recommended for production)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.6.1

# Verify installation
which specify
specify --version
specify check
```

**Benefits:**
- Single installation, use everywhere
- Faster command execution
- Easy upgrades with `--force` flag
- Pin to specific version for stability

### Method 2: One-time Usage with uvx

Run without installing (good for testing):

```bash
# Create new project
uvx --from git+https://github.com/github/spec-kit.git@v0.6.1 specify init my-project --ai claude

# Initialize current directory
uvx --from git+https://github.com/github/spec-kit.git@v0.6.1 specify init . --ai copilot
```

**Benefits:**
- No installation required
- Always uses latest version from main branch
- Good for quick testing

**Drawbacks:**
- Slower (downloads on each run)
- Less predictable (main branch may have unreleased changes)

## Project Initialization

### New Project

```bash
# Basic initialization
specify init my-project --ai claude

# With specific AI agent
specify init my-project --ai copilot
specify init my-project --ai gemini
specify init my-project --ai pi
specify init my-project --ai codebuddy
specify init my-project --ai windsurf

# Force script type (auto-detected otherwise)
specify init my-project --ai claude --script sh    # Bash scripts
specify init my-project --ai claude --script ps    # PowerShell scripts
```

### Existing Directory

```bash
# Initialize in current directory
specify init . --ai claude

# Using --here flag
specify init --here --ai copilot

# Skip git initialization if already a git repo
specify init --here --ai claude --no-git
```

### Initialization Options

| Option | Description | Default |
|--------|-------------|---------|
| `--ai <agent>` | AI agent type (claude, copilot, gemini, pi, etc.) | Detected from environment |
| `--script <type>` | Script type (sh or ps) | Auto-detected from OS |
| `--no-git` | Skip git repository initialization | false |
| `--ignore-agent-tools` | Skip tool availability checks | false |
| `--offline` | Use bundled templates without network access | false |

## Enterprise and Air-Gapped Installation

For environments with restricted network access:

### Step 1: Build Wheel on Connected Machine

```bash
# Clone repository on connected machine
git clone https://github.com/github/spec-kit.git
cd spec-kit

# Build wheel and dependencies
pip install build
python -m build --wheel --outdir dist/

# Download all dependencies (same OS and Python version as target)
pip download -d dist/ dist/specify_cli-*.whl
```

**Important:** Run this on a machine with the **same OS and Python version** as the air-gapped target to get platform-specific wheels.

### Step 2: Transfer to Air-Gapped Machine

Copy the entire `dist/` directory (contains specify-cli wheel + all dependency wheels) via USB, network share, or other approved transfer method.

### Step 3: Install on Air-Gapped Machine

```bash
# Navigate to dist/ directory
cd /path/to/dist/

# Install without network access
pip install --no-index --find-links=./ specify-cli
```

### Step 4: Initialize Project Offline

```bash
# Initialize with offline flag (uses bundled templates)
specify init my-project --ai claude --offline
```

**Note:** Starting with v0.6.0, `specify init` uses bundled assets by default. The `--offline` flag will be removed in future versions as network access is no longer required.

## Upgrade Procedures

### Quick Reference

| What to Upgrade | Command | When to Use |
|----------------|---------|-------------|
| **CLI Tool Only** | `uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@v0.6.1` | Get latest CLI features without touching project files |
| **Project Files** | `specify init --here --force --ai <your-agent>` | Update slash commands, templates, and scripts |
| **Both** | Run CLI upgrade, then project update | Recommended for major version updates |

### Upgrade CLI Tool

```bash
# Upgrade to specific version
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@v0.6.1

# Verify upgrade
specify check
```

### Upgrade Project Files

**Important:** Before upgrading, back up customizations:

```bash
# Back up constitution (will be overwritten)
cp .specify/memory/constitution.md /tmp/constitution-backup.md

# Back up custom templates if modified
cp -r .specify/templates /tmp/templates-backup
```

Then run upgrade:

```bash
# Update project files
specify init --here --force --ai claude

# Restore constitution
mv /tmp/constitution-backup.md .specify/memory/constitution.md
```

**What gets updated:**
- ✅ Slash command files (`.claude/commands/`, `.gemini/commands/`, etc.)
- ✅ Script files (`.specify/scripts/`)
- ✅ Template files (`.specify/templates/`)
- ⚠️ Memory files (`.specify/memory/constitution.md`) - **will be overwritten**

**What stays safe:**
- ✅ Your specifications (`specs/*/`) - **never touched**
- ✅ Implementation plans (`specs/*/plan.md`, `tasks.md`)
- ✅ Source code
- ✅ Git history

### Understanding the --force Flag

Without `--force`:

```text
Warning: Current directory is not empty (25 items)
Template files will be merged with existing content and may overwrite existing files
Proceed? [y/N]
```

With `--force`, skips confirmation and proceeds immediately.

**Safe to use:** Your `specs/` directory is **never included** in upgrade packages and cannot be overwritten.

## Common Upgrade Scenarios

### Scenario 1: Get New Slash Commands

```bash
# 1. Upgrade CLI
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@v0.6.1

# 2. Update project files
specify init --here --force --ai copilot

# 3. Restore constitution if customized
git restore .specify/memory/constitution.md
```

### Scenario 2: Customized Constitution and Templates

```bash
# 1. Back up customizations
cp .specify/memory/constitution.md /tmp/constitution-backup.md
cp -r .specify/templates /tmp/templates-backup

# 2. Upgrade CLI
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@v0.6.1

# 3. Update project
specify init --here --force --ai copilot

# 4. Restore customizations
mv /tmp/constitution-backup.md .specify/memory/constitution.md

# 5. Manually merge template changes if needed
diff -r /tmp/templates-backup .specify/templates
```

### Scenario 3: Duplicate Slash Commands

Some IDE-based agents (Kilo Code, Windsurf) show duplicate commands after upgrades:

```bash
# Navigate to agent folder
cd .kilocode/rules/

# List files and identify duplicates
ls -la

# Delete old versions
rm speckit.specify-old.md
rm speckit.plan-v1.md

# Restart IDE to refresh command list
```

### Scenario 4: Non-Git Projects

If you initialized with `--no-git`:

```bash
# Back up constitution
cp .specify/memory/constitution.md /tmp/constitution-backup.md

# Upgrade without git
specify init --here --force --ai copilot --no-git

# Restore constitution
mv /tmp/constitution-backup.md .specify/memory/constitution.md
```

**For non-git projects:** Set `SPECIFY_FEATURE` environment variable before using planning commands:

```bash
# Bash/Zsh
export SPECIFY_FEATURE="001-my-feature"

# PowerShell
$env:SPECIFY_FEATURE = "001-my-feature"
```

## Troubleshooting

### CLI Not Found After Upgrade

**Symptom:** `specify: command not found`

**Solution:**

```bash
# Check installed tools
uv tool list

# Should show specify-cli. If not, reinstall:
uv tool uninstall specify-cli
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.6.1

# Verify path
which specify
```

### Slash Commands Not Showing Up

**Symptom:** AI agent doesn't recognize `/speckit.*` commands

**Solutions:**

1. **Restart IDE/editor completely** (not just reload window)

2. **Verify command files exist:**

   ```bash
   # For Claude Code
   ls -la .claude/commands/

   # For GitHub Copilot
   ls -la .github/prompts/

   # For Pi Coding Agent
   ls -la .pi/prompts/

   # For Gemini CLI
   ls -la .gemini/commands/
   ```

3. **Check agent-specific setup:**
   - Codex requires `CODEX_HOME` environment variable
   - Some agents need workspace reload or cache clearing

4. **Verify you're in correct directory** where you ran `specify init`

### Constitution Overwritten After Upgrade

**Symptom:** Custom constitution lost after `specify init --here --force`

**Solution:** Restore from git or backup:

```bash
# If committed before upgrading
git restore .specify/memory/constitution.md

# If backed up manually
cp /tmp/constitution-backup.md .specify/memory/constitution.md
```

**Prevention:** Always commit or back up `constitution.md` before upgrading.

### "Warning: Current Directory Is Not Empty"

**Full warning:**

```text
Warning: Current directory is not empty (25 items)
Template files will be merged with existing content and may overwrite existing files
Do you want to continue? [y/N]
```

**What this means:**
- Directory has existing content (25 files/folders in example)
- New template files will be added alongside existing files
- Some Spec Kit files (`.claude/`, `.specify/`) will be replaced

**Safe to proceed:** Your `specs/` directory and source code are untouched.

**How to respond:**
- Type `y` and Enter to proceed (recommended for upgrades)
- Type `n` to cancel
- Use `--force` flag to skip confirmation

### Git Credential Manager on Linux

If experiencing Git authentication issues:

```bash
#!/bin/bash
set -e
echo "Downloading Git Credential Manager v2.6.1..."
wget https://github.com/git-ecosystem/git-credential-manager/releases/download/v2.6.1/gcm-linux_amd64.2.6.1.deb
echo "Installing Git Credential Manager..."
sudo dpkg -i gcm-linux_amd64.2.6.1.deb
echo "Configuring Git to use GCM..."
git config --global credential.helper manager
echo "Cleaning up..."
rm gcm-linux_amd64.2.6.1.deb
```

### Windows PowerShell Requirements

For offline scaffolding on Windows:

- Requires **PowerShell 7+** (`pwsh`), not Windows PowerShell 5.x (`powershell.exe`)
- Install from https://aka.ms/powershell

## Version Compatibility

Spec Kit follows semantic versioning. CLI and project files are designed to be compatible within the same major version.

**Best practice:** Keep both CLI and project files in sync during major version changes.

## Post-Upgrade Checklist

After upgrading:

- [ ] Test new slash commands (run `/speckit.constitution` or another command)
- [ ] Review release notes for new features and breaking changes
- [ ] Update team workflows if new commands were added
- [ ] Check documentation at https://github.github.io/spec-kit/
- [ ] Verify constitution was restored if customized
- [ ] Remove duplicate command files if present

## Additional Resources

- [GitHub Releases](https://github.com/github/spec-kit/releases) - Release notes and changelog
- [Documentation Site](https://github.github.io/spec-kit/) - Full documentation
- [SPEC KIT GITHUB REPOSITORY](https://github.com/github/spec-kit) - Source code and issues
- [SUPPORT GUIDE](../SUPPORT.md) - Getting help from the community
