# Extensions System

## Overview

Extensions are modular packages that add new commands and functionality to Spec Kit without bloating the core framework. They expand *what Spec Kit can do* — for example, adding domain-specific workflows, integrating with external tools (Jira, Linear, GitHub), or adding entirely new development phases.

Extensions introduce new slash commands that appear in your coding agent after installation. They are installed into `.specify/extensions/<name>/` and automatically registered as agent skills when using skills-based integrations.

## Extension Structure

```text
my-extension/
├── extension.yml              # Required: Extension manifest
├── README.md                  # Required: Documentation
├── LICENSE                    # Required: License file
├── CHANGELOG.md               # Recommended
├── .extensionignore           # Optional: Exclude files from installation
│
├── commands/                  # Extension commands
│   ├── command1.md
│   └── command2.md
│
├── config-template.yml        # Config template (if needed)
│
└── docs/                      # Additional documentation
```

## Extension Manifest (`extension.yml`)

```yaml
schema_version: "1.0"

extension:
  id: "my-ext"                          # Lowercase, alphanumeric + hyphens only
  name: "My Extension"
  version: "1.0.0"                      # Semantic versioning
  description: "Brief description (one sentence)"
  author: "Your Name"
  repository: "https://github.com/you/spec-kit-my-ext"
  license: "MIT"

requires:
  speckit_version: ">=0.1.0"            # Minimum spec-kit version
  tools:                                # Optional: External tools required
    - name: "my-tool"
      required: true
      version: ">=1.0.0"
  commands:                             # Optional: Core commands needed
    - "speckit.tasks"

provides:
  commands:
    - name: "speckit.my-ext.hello"      # Must follow: speckit.{ext-id}.{cmd}
      file: "commands/hello.md"
      description: "Say hello"
      aliases: ["speckit.my-ext.hi"]    # Optional aliases

  config:                               # Optional: Config files
    - name: "my-ext-config.yml"
      template: "my-ext-config.template.yml"
      description: "Extension configuration"
      required: false

hooks:                                  # Optional: Integration hooks
  after_tasks:
    command: "speckit.my-ext.hello"
    optional: true
    prompt: "Run hello command?"

tags:                                   # For catalog discovery
  - "example"
  - "utility"
```

### Validation Rules

**Extension ID**: Pattern `^[a-z0-9-]+$` — valid: `my-ext`, invalid: `MyExt`, `my_ext`

**Version**: Semantic versioning (X.Y.Z) — valid: `1.0.0`, invalid: `v1.0.0`, `1.0`

**Command Name**: Pattern `^speckit\.[a-z0-9-]+\.[a-z0-9-]+$` — valid: `speckit.my-ext.hello`, invalid: `my-ext.hello`

## Command File Format

Command files are Markdown with YAML frontmatter:

```markdown
---
description: "Command description"
tools:
  - 'some-tool/function'
scripts:
  sh: ../../scripts/bash/helper.sh
  ps: ../../scripts/powershell/helper.ps1
---

# Command Name

## User Input

$ARGUMENTS

## Steps

1. Parse arguments
2. Execute logic
```

Special placeholders:
- `$ARGUMENTS` — user-provided arguments
- `{SCRIPT}` — replaced with script path during registration

Script paths use relative paths that get rewritten during registration (e.g., `../../scripts/bash/helper.sh` → `.specify/scripts/bash/helper.sh`).

## Hooks

Hooks execute automatically after core commands. Available hook points:

- `before_specify` / `after_specify`
- `before_plan` / `after_plan`
- `before_tasks` / `after_tasks`
- `before_implement` / `after_implement`
- `before_analyze` / `after_analyze`
- `before_checklist` / `after_checklist`
- `before_clarify` / `after_clarify`
- `before_constitution` / `after_constitution`
- `before_taskstoissues` / `after_taskstoissues`

Hook configuration:

```yaml
hooks:
  after_tasks:
    command: "speckit.my-ext.hello"
    optional: true          # If true, prompt user before executing
    prompt: "Run hello?"
    description: "Description of what the hook does"
```

## Configuration

Extensions support layered configuration:

```text
.specify/extensions/my-ext/
├── my-ext-config.yml           # Project config (version controlled)
├── my-ext-config.local.yml     # Local overrides (gitignored)
└── my-ext-config.template.yml  # Template (reference)
```

Configuration merges in this order (highest priority last):
1. Extension defaults (`extension.yml` → `defaults`)
2. Project config (`my-ext-config.yml`)
3. Local overrides (`my-ext-config.local.yml`)
4. Environment variables (`SPECKIT_MY_EXT_*`)

Project-wide extension settings are stored in `.specify/extensions.yml`:

```yaml
installed:
  - jira
  - linear

settings:
  auto_execute_hooks: true

hooks:
  after_tasks:
    - extension: jira
      command: speckit.jira.specstoissues
      enabled: true
      optional: true
      prompt: "Create Jira issues from tasks?"
```

## .extensionignore

Exclude files from installation using `.gitignore`-compatible patterns:

```gitignore
# Development files
tests/
.github/
__pycache__/
*.pyc
dist/

# Documentation source
docs/
CONTRIBUTING.md
```

Pattern matching uses the `pathspec` library with standard `.gitignore` rules (`*`, `**`, `?`, trailing `/`, negation with `!`).

## CLI Commands

```bash
# Search available extensions
specify extension search
specify extension search jira
specify extension search --tag issue-tracking
specify extension search --verified

# Get detailed information
specify extension info jira

# Install from catalog (by name)
specify extension add jira

# Install from URL
specify extension add <name> --from https://github.com/org/ext/archive/refs/tags/v1.0.0.zip

# Install from local directory (development)
specify extension add --dev /path/to/extension

# List installed extensions
specify extension list

# Update extensions
specify extension update
specify extension update jira

# Disable/enable temporarily
specify extension disable jira
specify extension enable jira

# Remove
specify extension remove jira
specify extension remove jira --keep-config
specify extension remove jira --force
```

## Catalogs

Spec Kit uses a catalog stack — an ordered list of catalogs searched simultaneously:

- **`catalog.json`** (default) — Curated extensions, install allowed by default
- **`catalog.community.json`** (community) — Discovery only by default

Override the catalog URL:

```bash
export SPECKIT_CATALOG_URL="https://your-org.com/spec-kit/catalog.json"
specify extension search
```

Manage catalogs:

```bash
specify extension catalog list
specify extension catalog add --name "internal" --priority 2 --install-allowed https://internal.company.com/catalog.json
specify extension catalog remove internal
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SPECKIT_CATALOG_URL` | Override the full catalog stack with a single URL | Built-in default stack |
| `GH_TOKEN` / `GITHUB_TOKEN` | GitHub token for authenticated requests to private repos | None |
| `SPECKIT_{EXT_ID}_*` | Extension-specific configuration overrides | Extension defaults |

## Publishing Extensions

To publish to the community catalog:

1. Create `extension.yml` manifest with valid fields
2. Create a GitHub release (tag `vX.Y.Z`)
3. Fork `github/spec-kit` and add entry to `extensions/catalog.community.json`
4. Add extension to the Community Extensions table in `README.md`
5. Submit a Pull Request

See the [Extension Publishing Guide](https://github.com/github/spec-kit/blob/main/extensions/EXTENSION-PUBLISHING-GUIDE.md) for detailed steps.
