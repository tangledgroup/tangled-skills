# Extensions and Skills

## Extension System

`gh` extensions are separate binaries or Go packages that extend `gh` functionality. They appear as subcommands and can be discovered, installed, and managed from the CLI.

### Naming Convention

Extensions use the `gh-` prefix for binary names and are invoked as:

```bash
# Installed extension appears as a gh subcommand
gh <extname> [args]

# Binary name on disk
gh-<extname>
```

### Managing Extensions

```bash
# List installed extensions
gh extension list

# Search for extensions
gh extension search <query>

# Browse extensions in terminal UI
gh extension browse

# Install an extension from a GitHub repository
gh extension install cli/copilot

# Pin to specific version
gh extension install cli/some-ext --pin v1.0.0

# Remove an extension
gh extension remove copilot

# Upgrade all extensions
gh extension upgrade --all

# Upgrade specific extension
gh extension upgrade copilot

# Execute an extension directly
gh extension exec <extname> [args]
```

### Creating Extensions

```bash
# Create a new Go extension
gh extension create my-extension

# Create a precompiled extension (Go binary)
gh extension create my-extension --precompiled go

# Create a precompiled extension (other language)
gh extension create my-extension --precompiled other
```

Extensions are stored in the `~/.local/share/gh/extensions` directory by default. Override with `GH_CONFIG_DIR`.

### Extension Discovery

Extensions are discovered from GitHub repositories matching the pattern `gh-<name>` or `<owner>/gh-<name>`. The search command filters available extensions:

```bash
# Search with filters
gh extension search --license MIT --sort stars --limit 20
gh extension search --owner cli --order desc
```

## Skills (v2.91)

The `gh skill` command manages AI agent skills — markdown-based instruction files that extend coding agent capabilities. Skills are stored as `SKILL.md` files in GitHub repositories and can be installed to multiple agent hosts.

### Searching for Skills

```bash
# Search the skill registry
gh skill search terraform
gh skill search "code review"
```

### Installing Skills

```bash
# Interactive mode — choose repo, skill, and agent
gh skill install

# Choose a skill from a specific repo interactively
gh skill install github/awesome-copilot

# Install a specific skill
gh skill install github/awesome-copilot git-commit

# Install a specific version
gh skill install github/awesome-copilot git-commit@v1.2.0

# Install from a large namespaced repo by path
gh skill install github/awesome-copilot skills/monalisa/code-review

# Install from a local directory
gh skill install ./my-skills-repo --from-local

# Install a specific local skill
gh skill install ./my-skills-repo git-commit --from-local
```

### Agent Targeting

Skills can be installed for specific AI coding agents:

```bash
# Install for Claude Code at user scope
gh skill install github/awesome-copilot git-commit \
  --agent claude-code --scope user

# Install for a specific agent at project scope (default)
gh skill install github/awesome-copilot git-commit \
  --agent pi --scope project
```

Supported agents include Claude Code, Codex, Cursor, Gemini CLI, OpenCode, and others. Run `gh skill install --help` for the complete list.

### Scopes

- `project` — install into the current project's skill directory (default)
- `user` — install into the user-level skill directory

### Directory Options

```bash
# Specify custom installation directory
gh skill install github/awesome-copilot git-commit --dir .agents/skills

# Allow discovery in hidden directories (.claude/skills/, .github/skills/)
gh skill install owner/repo --allow-hidden-dirs
```

### Pinning and Updates

```bash
# Pin to a specific git ref
gh skill install github/awesome-copilot git-commit --pin v2.0.0

# Update all installed skills
gh skill update --all

# Force reinstall
gh skill install github/awesome-copilot git-commit --force
```

### Preview and Publish

```bash
# Preview a skill before installing
gh skill preview github/awesome-copilot git-commit

# Validate skills for publishing (dry run)
gh skill publish --dry-run
```

### Upstream Detection (v2.91)

`gh skill install` detects if a skill is re-published from an upstream source and offers to install from the original. Use `--upstream` for non-interactive installation from the detected upstream.

### Skill Repository Structure

Skills follow this structure in repositories:

```
repo/
└── skills/
    └── <skill-name>/
        └── SKILL.md          # Main skill file with YAML header
        └── reference/        # Optional reference files
            ├── 01-topic.md
            └── 02-topic.md
```

Hidden directories are also supported with `--allow-hidden-dirs`:

```
repo/
├── .claude/skills/...
├── .agents/skills/...
└── .github/skills/...
```
