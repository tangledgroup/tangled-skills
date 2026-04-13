# AI Agent Support

Comprehensive guide to supported AI coding assistants and their integration with Spec Kit.

## Supported Agents Overview

Spec Kit supports multiple AI coding assistants through a plugin architecture. Each agent receives slash commands tailored to its interface and capabilities.

### Officially Supported Agents

| Agent | Type | CLI Required | Command Format | Directory |
|-------|------|--------------|----------------|-----------|
| Claude Code | CLI | Yes | Markdown | `.claude/commands/` |
| GitHub Copilot | IDE | No | Markdown | `.github/prompts/` |
| Gemini CLI | CLI | Yes | TOML | `.gemini/commands/` |
| Pi Coding Agent | CLI/IDE | Yes | Markdown | `.pi/prompts/` |
| Codebuddy CLI | CLI | Yes | Markdown | `.codebuddy/commands/` |
| Windsurf | IDE | No | Markdown | `.windsurf/workflows/` |
| Cursor | IDE | No | Skills | `.cursor/skills/` |
| Kiro CLI | CLI | Yes | Markdown | `.kiro/commands/` |

### Community-Supported Agents

Additional agents supported via community contributions:

- **Codex CLI** - Skills-based integration (`.agents/skills/`)
- **Roo Code** - VS Code extension (`.roo/commands/`)
- **Kilo Code** - Markdown commands (`.kilocode/rules/`)
- **Tabnine** - IDE integration (`.tabnine/commands/`)
- **Forgecode** - CLI tool (`.forge/commands/`)
- **iFlow CLI** - Workflow automation (`.iflow/commands/`)
- **Junie** - AI assistant integration
- **Aide** - CLI-based agent
- **Trae** - Development assistant

## Agent Integration Architecture

### Integration Types

Spec Kit uses a plugin architecture with base classes for common patterns:

**1. MarkdownIntegration**
- For agents using markdown command files (`.md`)
- Default argument placeholder: `$ARGUMENTS`
- Examples: Claude, Pi, Windsurf, Kiro

**2. TomlIntegration**
- For agents using TOML configuration (`.toml`)
- Argument placeholder: `{{args}}`
- Example: Gemini

**3. SkillsIntegration**
- For agents using skill directories with `SKILL.md` files
- Each command is a directory with `SKILL.md` inside
- Examples: Codex, Cursor (migrated from `.cursor/commands`)

**4. IntegrationBase**
- Custom integration for agents with unique requirements
- Full control over file generation and registration
- Example: Copilot (creates `.agent.md` + `.prompt.md` files)

### Command Registration Flow

```
specify init --ai <agent>
    ↓
Integration registry lookup
    ↓
Load agent-specific integration class
    ↓
Generate commands in agent directory
    ↓
Register commands with AI agent
    ↓
Update agent context file (if applicable)
```

## Agent-Specific Configurations

### Claude Code

**Type:** CLI-based agent
**Directory:** `.claude/commands/`
**Format:** Markdown with YAML frontmatter

**Command file example:**

```markdown
---
description: "Create feature specification"
argument-hint: "<feature description>"
---

## User Input

```text
$ARGUMENTS
```

## Execution

1. Parse feature description
2. Create spec directory
3. Generate specification
```

**Context file:** `CLAUDE.md`

**Installation:**

```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Initialize Spec Kit
specify init my-project --ai claude
```

**Configuration:**

```json
// .claude/settings.json (optional)
{
  "commands": {
    "enabled": true,
    "autoReload": true
  }
}
```

**Notes:**
- Supports `argument-hint` frontmatter for CLI autocomplete
- Commands reload automatically when files change
- Native skills support via `.agents/skills/` (alternative to `.claude/commands/`)

---

### GitHub Copilot

**Type:** IDE-based agent (VS Code)
**Directory:** `.github/prompts/`
**Format:** Markdown with YAML frontmatter

**Command file example:**

```markdown
---
description: "Create feature specification"
mode: speckit.specify
---

## User Input

```text
$ARGUMENTS
```

## Execution

...
```

**Context files:**
- `.github/COPILOT.md` - Copilot instructions
- `.github/copilot-instructions.md` - Alternative location
- `.github/specify-rules.md` - Spec Kit rules

**Installation:**

```bash
# Install GitHub Copilot VS Code extension
# In VS Code: Extensions → Search "GitHub Copilot" → Install

# Initialize Spec Kit
specify init my-project --ai copilot
```

**Configuration:**

```json
// .vscode/settings.json
{
  "github.copilot.chat enabled": true,
  "github.copilot.edge.enabled": true
}
```

**Special behavior:**
- Creates companion `.agent.md` files for agent-specific instructions
- Creates `.prompt.md` files for user-facing prompts
- Merges configuration into `.vscode/settings.json`

**Notes:**
- Requires VS Code reload after initialization
- Uses `mode: speckit.command-name` in frontmatter
- Supports Chat mode in VS Code and GitHub Codespaces

---

### Gemini CLI

**Type:** CLI-based agent
**Directory:** `.gemini/commands/`
**Format:** TOML

**Command file example:**

```toml
description = "Create feature specification"

prompt = """
## User Input

```text
{{args}}
```

## Execution

1. Parse feature description
2. Create spec directory
3. Generate specification
"""
```

**Context file:** `GEMINI.md`

**Installation:**

```bash
# Install Gemini CLI
curl -fsSL https://download.gemini-cli.com/install.sh | bash

# Initialize Spec Kit
specify init my-project --ai gemini
```

**Configuration:**

```toml
# .gemini/config.toml (optional)
[commands]
enabled = true
auto_reload = true
```

**Notes:**
- Uses TOML format instead of YAML frontmatter
- Argument placeholder is `{{args}}` instead of `$ARGUMENTS`
- Strips YAML frontmatter from prompts automatically

---

### Pi Coding Agent

**Type:** CLI/IDE hybrid
**Directory:** `.pi/prompts/`
**Format:** Markdown with YAML frontmatter

**Command file example:**

```markdown
---
description: "Create feature specification"
---

## User Input

```text
$ARGUMENTS
```

## Execution

...
```

**Context file:** `.pi/instructions.md`

**Installation:**

```bash
# Pi Coding Agent is pre-installed or available via package manager

# Initialize Spec Kit
specify init my-project --ai pi
```

**Notes:**
- Supports both CLI and IDE modes
- Commands appear in Pi's prompt interface
- Context file updated with Spec Kit rules

---

### Codebuddy CLI

**Type:** CLI-based agent
**Directory:** `.codebuddy/commands/`
**Format:** Markdown

**Installation:**

```bash
# Install Codebuddy CLI
# Follow instructions at https://www.codebuddy.ai/cli

# Initialize Spec Kit
specify init my-project --ai codebuddy
```

---

### Windsurf

**Type:** IDE-based agent
**Directory:** `.windsurf/workflows/`
**Format:** Markdown

**Command file example:**

```markdown
---
description: "Create feature specification"
---

## User Input

```text
$ARGUMENTS
```

## Execution

...
```

**Context file:** `.windsurf/rules/specify-rules.md`

**Installation:**

```bash
# Install Windsurf IDE
# Download from https://windsurf.ai

# Initialize Spec Kit
specify init my-project --ai windsurf
```

**Notes:**
- Commands appear as "workflows" in Windsurf UI
- No CLI installation required
- Context rules file guides AI behavior

---

### Cursor

**Type:** IDE-based agent (VS Code fork)
**Directory:** `.cursor/skills/` (v0.6.1+) or `.cursor/commands/` (legacy)
**Format:** Skills (directories with `SKILL.md`)

**Skill directory structure:**

```
.cursor/skills/
├── speckit-specify/
│   └── SKILL.md
├── speckit-plan/
│   └── SKILL.md
└── speckit-tasks/
    └── SKILL.md
```

**SKILL.md example:**

```yaml
---
name: speckit-specify
description: Create feature specification from natural language description
user-invocable: true
---

# Speckit Specify

Create a feature specification by analyzing user input and generating structured requirements.

## Usage

Provide a feature description after the command:

/speckit.specify <feature description>
```

**Installation:**

```bash
# Install Cursor IDE
# Download from https://cursor.sh

# Initialize Spec Kit (auto-detects Cursor)
specify init my-project --ai cursor
```

**Notes:**
- Migrated from `.cursor/commands/` to `.cursor/skills/` in v0.6.1
- Each command is a skill directory with `SKILL.md`
- Supports `user-invocable: true` frontmatter for user-accessible commands

---

### Codex CLI

**Type:** CLI-based agent
**Directory:** `.agents/skills/`
**Format:** Skills (directories with `SKILL.md`)

**Installation:**

```bash
# Install Codex CLI
git clone https://github.com/openai/codex
cd codex
npm install
npm link

# Initialize Spec Kit
specify init my-project --ai codex --skills
```

**Configuration:**

```bash
# Set CODEX_HOME environment variable
export CODEX_HOME=~/.codex
```

**Notes:**
- Uses `--skills` flag for native skills installation
- Skills appear in Codex command interface
- Context file: `AGENTS.md`

---

## Multi-Agent Projects

### Using Multiple Agents in Same Project

Spec Kit supports installing multiple agent integrations in one project:

```bash
# Initialize with primary agent
specify init my-project --ai claude

# Add secondary agent
specify integration install copilot

# Add third agent
specify integration install gemini
```

**Result:**

```
my-project/
├── .claude/commands/      # Claude slash commands
├── .github/prompts/       # Copilot slash commands
├── .gemini/commands/      # Gemini slash commands
└── .specify/
    └── extensions.yml     # All integrations registered
```

**Use cases:**
- Team members using different AI agents
- Different agents for different tasks
- Migration between agents

### Agent-Specific Customizations

Each agent can have customized commands while sharing core Spec Kit functionality:

```bash
# Customize Claude commands
# Edit .claude/commands/speckit.specify.md

# Customize Copilot commands
# Edit .github/prompts/speckit.specify.agent.md

# Changes are agent-specific, don't affect other agents
```

**Upgrade behavior:**
- `specify init --here --force` overwrites all agent commands
- Back up customizations before upgrading
- Consider creating custom extension for persistent customizations

---

## Agent Context Files

Context files provide project-wide instructions to AI agents:

### Claude: `CLAUDE.md`

```markdown
# Spec Kit Context

You are working in a Spec-Driven Development environment.

## Workflow

1. Always start with `/speckit.specify` to create specifications
2. Use `/speckit.plan` to generate implementation plans
3. Run `/speckit.tasks` before coding
4. Implement using `/speckit.implement`

## Principles

- Specifications drive implementation
- No code without specification
- All features require acceptance criteria
```

### Copilot: `.github/COPILOT.md`

```markdown
# Spec Kit Rules

This project uses Spec-Driven Development. Follow these rules:

1. Check `specs/` directory for feature specifications
2. Read constitution in `.specify/memory/constitution.md`
3. Use slash commands for workflow automation
4. Never implement without spec
```

### Gemini: `GEMINI.md`

```markdown
# Spec Kit Guidelines

## Development Process

- Specifications first, implementation second
- Use `/speckit.*` commands for all feature work
- Validate with `/speckit.checklist` before planning
```

**Context file updates:**
- Auto-updated by `update-agent-context.sh/ps1` scripts
- Preserves manual additions between markers
- Adds new technologies from implementation plans

---

## Agent Detection and Auto-Configuration

### Automatic Agent Detection

Spec Kit attempts to auto-detect available agents:

```bash
# Without --ai flag, Spec Kit checks for:
specify init my-project

# Detection order:
1. Check for .claude/ directory (Claude Code)
2. Check for .vscode/extensions (Copilot, Cursor)
3. Check for .gemini/ directory (Gemini CLI)
4. Check for .pi/ directory (Pi Coding Agent)
5. Prompt user to select agent if none detected
```

### Manual Agent Specification

Always recommend explicit agent specification:

```bash
specify init my-project --ai claude
```

**Benefits:**
- Predictable behavior
- Clear intent in scripts and documentation
- Avoids detection failures

---

## CLI-Based vs IDE-Based Agents

### CLI-Based Agents

**Agents:** Claude Code, Gemini CLI, Codebuddy, Codex, Kiro

**Characteristics:**
- Require CLI tool installation
- Commands invoked in terminal or chat interface
- Typically faster command execution
- Better for automation and scripting

**Installation pattern:**

```bash
# Install CLI tool
npm install -g <agent-cli>

# Initialize Spec Kit
specify init my-project --ai <agent>

# Use commands in agent's chat interface
<agent-cli> chat /speckit.specify "Feature description"
```

### IDE-Based Agents

**Agents:** GitHub Copilot, Windsurf, Cursor

**Characteristics:**
- No separate CLI installation
- Commands appear in IDE UI
- Integrated with editor features
- Better for interactive development

**Installation pattern:**

```bash
# Install IDE extension (via IDE interface)

# Initialize Spec Kit
specify init my-project --ai <agent>

# Use commands in IDE chat panel
/speckit.specify "Feature description"
```

---

## Troubleshooting Agent Issues

### Commands Not Showing Up

**Symptom:** Slash commands not visible in agent UI

**Solutions by agent:**

**Claude Code:**
```bash
# Verify command files exist
ls -la .claude/commands/

# Restart Claude Code
# Or reload workspace
```

**GitHub Copilot:**
```bash
# Check prompts directory
ls -la .github/prompts/

# Reload VS Code window
# Command Palette → Developer: Reload Window
```

**Gemini CLI:**
```bash
# Verify TOML files
ls -la .gemini/commands/

# Restart Gemini CLI
```

**Cursor:**
```bash
# Check skills directory (v0.6.1+)
ls -la .cursor/skills/

# Or legacy commands directory
ls -la .cursor/commands/

# Restart Cursor IDE
```

### Agent Not Detected

**Symptom:** `specify init` doesn't auto-detect agent

**Solutions:**
1. Verify agent is installed and accessible
2. Check agent's configuration files exist
3. Specify agent explicitly: `specify init --ai <agent>`

### Context File Not Updating

**Symptom:** Agent context file not updated with new technologies

**Solutions:**

```bash
# Manually trigger context update
# Bash
.specify/scripts/bash/update-agent-context.sh <agent>

# PowerShell
.specify/scripts/powershell/update-agent-context.ps1 -AgentType <agent>

# Or use command (if available)
/speckit.update-context
```

### Duplicate Commands After Upgrade

**Symptom:** Both old and new versions of commands appear

**Solution:**

```bash
# Find agent directory
ls -la .<agent>/commands/  # or .skills/, .workflows/, etc.

# Delete old command files
rm .<agent>/commands/speckit.*-old.md
rm .<agent>/commands/speckit.*-v1.md

# Restart agent/IDE
```

---

## Adding New Agent Support

For developers wanting to add support for new AI agents:

### Quick Start

1. **Choose integration base class:**
   - `MarkdownIntegration` for standard markdown commands
   - `TomlIntegration` for TOML configuration
   - `SkillsIntegration` for skill-based agents
   - `IntegrationBase` for fully custom integrations

2. **Create integration subpackage:**

```python
# src/specify_cli/integrations/newagent/__init__.py
from ..base import MarkdownIntegration


class NewAgentIntegration(MarkdownIntegration):
    key = "newagent"
    config = {
        "name": "New Agent",
        "folder": ".newagent/",
        "commands_subdir": "commands",
        "install_url": "https://newagent.example.com",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".newagent/commands",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": ".md",
    }
    context_file = ".newagent/rules/specify-rules.md"
```

3. **Register integration:**

```python
# src/specify_cli/integrations/__init__.py
def _register_builtins() -> None:
    from .newagent import NewAgentIntegration
    _register(NewAgentIntegration())
```

4. **Add update scripts:**

Create thin wrappers in `src/specify_cli/integrations/newagent/scripts/`:
- `update-context.sh`
- `update-context.ps1`

5. **Test integration:**

```bash
# Install in test project
specify init test-project --ai newagent

# Verify commands created
ls -R test-project/.newagent/commands/
```

**See AGENTS.md for complete development guide.**

---

## Next Steps

- Review [Extensions Guide](references/04-extensions.md) for extending agent capabilities
- Explore [Command Reference](references/03-command-reference.md) for command details
- Check [Installation Guide](references/01-installation.md) for troubleshooting
