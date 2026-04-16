---
name: spec-kit-0-6-1
description: A skill for implementing Spec-Driven Development (SDD) using GitHub's Spec Kit v0.6.1 toolkit, enabling specification-first workflows with AI agents to generate executable specifications, implementation plans, and task breakdowns that drive code generation. Use when building software projects requiring structured specification workflows, integrating AI coding assistants (Claude, Copilot, Gemini, Pi, etc.) with spec-driven methodologies, or migrating existing projects to specification-first development practices.
version: "0.6.1"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - specification-driven-development
  - sdd
  - ai-assisted-development
  - project-management
  - workflow-automation
  - slash-commands
  - feature-specification
category: development
required_environment_variables:
  - name: uv
    prompt: "Install uv package manager from https://docs.astral.sh/uv/"
    help: "Required for installing specify-cli tool"
    required_for: "full functionality"
  - name: git
    prompt: "Install Git version control system"
    help: "Required for branch management and feature tracking"
    required_for: "full functionality"
  - name: python
    prompt: "Install Python 3.11 or higher"
    help: "Required to run specify-cli"
    required_for: "full functionality"
---

# Spec Kit 0.6.1

A comprehensive toolkit for implementing **Spec-Driven Development (SDD)** - a methodology where specifications become executable artifacts that directly generate working implementations rather than just guiding them. Spec Kit provides templates, slash commands, and AI agent integrations to transform vague ideas into structured specifications, technical plans, and actionable tasks.

## When to Use

- Building new software projects with specification-first approach
- Migrating existing projects to SDD methodology
- Integrating AI coding assistants (Claude Code, GitHub Copilot, Gemini CLI, Pi Coding Agent, etc.) with structured workflows
- Creating traceable requirements from user stories to implementation
- Managing complex features requiring clear acceptance criteria before coding
- Teams wanting to reduce the gap between specification and implementation
- Projects needing consistent documentation generated alongside code

## Setup

### Prerequisites

- **uv** (Python package manager): https://docs.astral.sh/uv/
- **Python 3.11+**: https://www.python.org/downloads/
- **Git**: https://git-scm.com/downloads
- AI coding agent: [Claude Code](https://www.anthropic.com/claude-code), [GitHub Copilot](https://code.visualstudio.com/), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [Pi Coding Agent](https://pi.dev), or other supported agents

### Installation

**Option 1: Persistent Installation (Recommended)**

Install once and use everywhere. Pin a specific release for stability:

```bash
# Install from stable release v0.6.1
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.6.1

# Verify installation
specify check
```

**Option 2: One-time Usage**

Run directly without installing:

```bash
uvx --from git+https://github.com/github/spec-kit.git@v0.6.1 specify init <PROJECT_NAME>
```

### Initialize Project

**Create new project:**

```bash
# With AI agent specification
specify init my-project --ai claude

# Available AI agents: claude, copilot, gemini, pi, codebuddy, windsurf, cursor, etc.
specify init my-project --ai copilot
specify init my-project --ai gemini
specify init my-project --ai pi
```

**Initialize in existing directory:**

```bash
# Initialize current directory
specify init . --ai claude

# Or use --here flag
specify init --here --ai claude
```

**Script type selection (auto-detected):**

```bash
# Force Bash scripts
specify init my-project --script sh

# Force PowerShell scripts
specify init my-project --script ps
```

See [Installation Details](references/01-installation.md) for enterprise/air-gapped setups and troubleshooting.

## Quick Start

### The 6-Step SDD Process

**Step 1: Define Constitution**

Establish core project principles using the AI agent's chat interface:

```markdown
/speckit.constitution This project follows a "Security-First" approach. All user inputs must be validated. We use microservices architecture. Code must be fully documented.
```

**Step 2: Create Specification**

Describe what to build (focus on WHAT and WHY, not HOW):

```markdown
/speckit.specify Build a photo organization app where albums are grouped by date, can be reorganized via drag-and-drop, and photos display in a tile interface within each album.
```

This automatically:
- Creates feature branch (e.g., `001-photo-organizer`)
- Generates `specs/001-photo-organizer/spec.md`
- Populates structured requirements with user stories and acceptance criteria

**Step 3: Refine Specification**

Resolve ambiguities interactively:

```markdown
/speckit.clarify Albums should support unlimited photos. Drag-and-drop should work across albums. Photos should auto-sort by date within albums.
```

**Step 4: Generate Implementation Plan**

Provide tech stack and architecture choices:

```markdown
/speckit.plan Use React with TypeScript for frontend, Node.js/Express for backend API, PostgreSQL for metadata storage, and Cloudinary for image hosting.
```

This generates:
- `specs/001-photo-organizer/plan.md` - Technical implementation plan
- `specs/001-photo-organizer/research.md` - Technology research findings
- `specs/001-photo-organizer/data-model.md` - Entity schemas and relationships
- `specs/001-photo-organizer/contracts/` - API contracts and interfaces
- `specs/001-photo-organizer/quickstart.md` - Key validation scenarios

**Step 5: Generate Task List**

Break down plan into executable tasks:

```markdown
/speckit.tasks
```

This creates `specs/001-photo-organizer/tasks.md` with parallelizable task groups.

**Step 6: Implement**

Execute the implementation:

```markdown
/speckit.implement
```

### Complete Example: Taskify Kanban Board

See [Workflow Examples](references/02-workflow-examples.md) for a detailed walkthrough building a team productivity platform with user management, project creation, and Kanban-style task boards.

## Core Commands

Spec Kit provides slash commands that transform the traditional development workflow:

| Command | Purpose | Output |
|---------|---------|--------|
| `/speckit.constitution` | Define project principles | `.specify/memory/constitution.md` |
| `/speckit.specify` | Create feature specification | `specs/<feature>/spec.md` |
| `/speckit.clarify` | Resolve ambiguities | Updated spec with clarifications |
| `/speckit.checklist` | Validate specification quality | `specs/<feature>/checklists/requirements.md` |
| `/speckit.plan` | Generate implementation plan | `specs/<feature>/plan.md` + design artifacts |
| `/speckit.tasks` | Create task breakdown | `specs/<feature>/tasks.md` |
| `/speckit.analyze` | Audit implementation plan | Analysis report with issues |
| `/speckit.implement` | Execute code generation | Source code implementation |

See [Command Reference](references/03-command-reference.md) for detailed command documentation.

## Project Structure

After initialization, Spec Kit creates:

```
my-project/
├── .specify/
│   ├── scripts/              # Automation scripts (bash/powershell)
│   ├── templates/            # Specification and plan templates
│   ├── memory/
│   │   └── constitution.md   # Project principles and constraints
│   ├── extensions.yml        # Installed extension registry
│   └── feature.json          # Current feature tracking
├── .claude/                  # or .gemini/, .github/, .pi/, etc.
│   └── commands/             # Slash command files
├── specs/                    # Feature specifications (git-tracked)
│   ├── 001-photo-organizer/
│   │   ├── spec.md           # Feature specification
│   │   ├── plan.md           # Implementation plan
│   │   ├── research.md       # Technology research
│   │   ├── data-model.md     # Entity schemas
│   │   ├── contracts/        # API/interface contracts
│   │   ├── quickstart.md     # Validation scenarios
│   │   ├── tasks.md          # Task breakdown
│   │   └── checklists/       # Quality validation checklists
│   └── 002-another-feature/
│       └── spec.md
└── src/                      # Generated source code
```

**Key directories:**
- **`specs/`**: Feature specifications, plans, and design artifacts (git-tracked, never overwritten by upgrades)
- **`.specify/`**: Spec Kit infrastructure (templates, scripts, configuration)
- **`.<agent>/`**: AI agent-specific command files (e.g., `.claude/`, `.gemini/`, `.pi/`)

## Extensions and Presets

Spec Kit supports community extensions that add domain-specific workflows:

**Built-in Extension:**
- **Git Extension** - Automatic branch creation, hooks on core commands

**Community Extensions** (install via `specify extension install`):
- **Jira Integration** - Sync specs to Jira issues
- **Linear Integration** - Connect with Linear project management
- **Confluence** - Export specifications to Confluence
- **Security Review** - Automated security analysis hooks
- **DocGuard** - Documentation quality enforcement
- **Memorylint** - Context memory optimization
- And 50+ more in the [Community Catalog](https://github.com/github/spec-kit/tree/main/extensions)

See [Extension Guide](references/04-extensions.md) for installation and development.

## Reference Files

- [`references/01-installation.md`](references/01-installation.md) - Detailed installation, upgrade procedures, and troubleshooting
- [`references/02-workflow-examples.md`](references/02-workflow-examples.md) - Complete workflow examples including Taskify Kanban app
- [`references/03-command-reference.md`](references/03-command-reference.md) - All slash commands with parameters and output formats
- [`references/04-extensions.md`](references/04-extensions.md) - Extension system, community catalog, and development guide
- [`references/05-ai-agents.md`](references/05-ai-agents.md) - Supported AI agents and integration details
- [`references/06-sdd-methodology.md`](references/06-sdd-methodology.md) - Spec-Driven Development methodology and core principles

## Troubleshooting

**Common issues:**

1. **Constitution overwritten during upgrade**: Back up `.specify/memory/constitution.md` before running `specify init --here --force`, then restore afterward.

2. **Duplicate slash commands**: Manually delete old command files from agent folder (e.g., `.kilocode/rules/speckit.old-command.md`).

3. **CLI not found after upgrade**: Reinstall with `uv tool install specify-cli --force`.

4. **Air-gapped environments**: Use bundled wheel installation with `--offline` flag.

See [Installation Guide](references/01-installation.md) for detailed troubleshooting.

## Next Steps

- Read the [SDD Methodology](references/06-sdd-methodology.md) to understand specification-driven development principles
- Explore [Workflow Examples](references/02-workflow-examples.md) for complete project walkthroughs
- Check the [Command Reference](references/03-command-reference.md) for detailed command documentation
- Browse [Community Extensions](https://github.com/github/spec-kit/tree/main/extensions) to enhance your workflow

**Resources:**
- [Spec Kit GitHub Repository](https://github.com/github/spec-kit)
- [Documentation Site](https://github.github.io/spec-kit/)
- [Releases and Changelog](https://github.com/github/spec-kit/releases)
- [Community Extensions Catalog](https://github.com/github/spec-kit/tree/main/extensions)
