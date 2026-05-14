# Slash Commands Reference

## Core Commands

Essential commands for the Spec-Driven Development workflow. After running `specify init`, your AI coding agent will have access to these slash commands.

### `/speckit.constitution`

Create or update project governing principles and development guidelines.

```bash
/speckit.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements
```

The constitution is stored in `.specify/memory/constitution.md` and guides all subsequent development. It defines architectural principles like library-first design, test-first imperatives, simplicity gates, and anti-abstraction rules.

### `/speckit.specify`

Define what you want to build — requirements and user stories. Focus on the **what** and **why**, not the tech stack.

```bash
/speckit.specify Build an application that can help me organize my photos in separate photo albums. Albums are grouped by date and can be re-organized by dragging and dropping.
```

This command:
- Scans existing specs to determine the next feature number (001, 002, 003…)
- Generates a semantic branch name from your description and creates it automatically
- Copies and customizes the feature specification template with your requirements
- Creates the proper `specs/<branch-name>/` directory structure

### `/speckit.plan`

Create technical implementation plans with your chosen tech stack and architecture choices.

```bash
/speckit.plan The application uses Vite with minimal libraries. Vanilla HTML, CSS, and JavaScript. Images stored locally, metadata in SQLite.
```

This command:
- Reads and understands the feature requirements, user stories, and acceptance criteria
- Ensures alignment with project constitution and architectural principles
- Converts business requirements into technical architecture and implementation details
- Generates supporting documents for data models, API contracts, and test scenarios
- Produces a quickstart guide capturing key validation scenarios

### `/speckit.tasks`

Generate actionable task lists for implementation.

```bash
/speckit.tasks
```

This command:
- Reads `plan.md` (required) and, if present, `data-model.md`, `contracts/`, and `research.md`
- Converts contracts, entities, and scenarios into specific tasks
- Marks independent tasks `[P]` and outlines safe parallel groups
- Writes `tasks.md` in the feature directory

### `/speckit.taskstoissues`

Convert generated task lists into GitHub issues for tracking and execution.

```bash
/speckit.taskstoissues
```

### `/speckit.implement`

Execute all tasks to build the feature according to the plan.

```bash
/speckit.implement
```

For complex projects, implement in phases — start with core functionality, validate it works, then add features incrementally.

## Optional Commands

Additional commands for enhanced quality and validation.

### `/speckit.clarify`

Clarify underspecified areas. Recommended before `/speckit.plan`.

```bash
/speckit.clarify Focus on security and performance requirements
```

Interactively identifies and resolves ambiguities in the specification using `[NEEDS CLARIFICATION]` markers.

### `/speckit.analyze`

Cross-artifact consistency and coverage analysis. Run after `/speckit.tasks`, before `/speckit.implement`.

```bash
/speckit.analyze
```

Analyzes specifications for ambiguity, contradictions, and gaps — not as a one-time gate but as ongoing refinement.

### `/speckit.checklist`

Generate custom quality checklists that validate requirements completeness, clarity, and consistency.

```bash
/speckit.checklist
```

## Agent Skill Mode

For integrations that support skills mode, passing `--integration <agent> --integration-options="--skills"` installs agent skills instead of slash-command prompt files.

| Slash Command | Agent Skill Name |
|---|---|
| `/speckit.constitution` | `speckit-constitution` |
| `/speckit.specify` | `speckit-specify` |
| `/speckit.plan` | `speckit-plan` |
| `/speckit.tasks` | `speckit-tasks` |
| `/speckit.taskstoissues` | `speckit-taskstoissues` |
| `/speckit.implement` | `speckit-implement` |
| `/speckit.clarify` | `speckit-clarify` |
| `/speckit.analyze` | `speckit-analyze` |
| `/speckit.checklist` | `speckit-checklist` |

## Context Awareness

Spec Kit commands automatically detect the active feature based on your current Git branch (e.g., `001-feature-name`). To switch between different specifications, simply switch Git branches.

Without git (using `--no-git`), set the `SPECIFY_FEATURE` environment variable:

```bash
export SPECIFY_FEATURE="001-my-feature"
```

## Example Workflow: Building a Chat Feature

```bash
# Step 1: Create the feature specification (5 minutes)
/speckit.specify Real-time chat system with message history and user presence

# Automatically creates:
# - Branch "003-chat-system"
# - specs/003-chat-system/spec.md

# Step 2: Generate implementation plan (5 minutes)
/speckit.plan WebSocket for real-time messaging, PostgreSQL for history, Redis for presence

# Step 3: Generate executable tasks (5 minutes)
/speckit.tasks

# Automatically creates:
# - specs/003-chat-system/plan.md
# - specs/003-chat-system/research.md
# - specs/003-chat-system/data-model.md
# - specs/003-chat-system/contracts/
# - specs/003-chat-system/quickstart.md
# - specs/003-chat-system/tasks.md

# Step 4: Implement
/speckit.implement
```

In 15 minutes, you have a complete feature specification, detailed implementation plan, API contracts, data models, and task list — all properly versioned in a feature branch.
