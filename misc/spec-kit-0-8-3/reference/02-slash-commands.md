# Slash Commands Reference

## Core Commands

Essential commands for the Spec-Driven Development workflow. After running `specify init`, your AI coding agent will have access to these slash commands. For integrations that support skills mode, passing `--integration <agent> --integration-options="--skills"` installs agent skills instead of slash-command prompt files.

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
- Marks independent tasks `[P]` for parallel execution
- Writes `tasks.md` in the feature directory with dependency ordering
- Organizes tasks by user story for incremental delivery

### `/speckit.taskstoissues`

Convert generated task lists into GitHub issues for tracking and execution.

```bash
/speckit.taskstoissues
```

This command:
- Reads `tasks.md` from the current feature directory
- Creates GitHub issues for each task with proper labeling and linking
- Maintains traceability between spec artifacts and issue tracker

### `/speckit.implement`

Execute all tasks to build the feature according to the plan.

```bash
/speckit.implement
```

This command:
- Validates that all prerequisites are in place (constitution, spec, plan, and tasks)
- Parses the task breakdown from `tasks.md`
- Executes tasks in the correct order, respecting dependencies and parallel execution markers
- Follows the TDD approach defined in your task plan
- Provides progress updates and handles errors appropriately

## Optional Commands

Additional commands for enhanced quality and validation.

### `/speckit.clarify`

Clarify underspecified areas. Recommended before `/speckit.plan`.

```bash
/speckit.clarify Focus on security and performance requirements
```

Structured, sequential, coverage-based questioning that records answers in a Clarifications section of the spec. Reduces rework downstream by resolving ambiguities before planning begins.

### `/speckit.analyze`

Cross-artifact consistency and coverage analysis. Run after `/speckit.tasks`, before `/speckit.implement`.

```bash
/speckit.analyze
```

Validates that all specification requirements are covered by the implementation plan and task breakdown. Identifies gaps, contradictions, and missing edge cases.

### `/speckit.checklist`

Generate custom quality checklists that validate requirements completeness, clarity, and consistency.

```bash
/speckit.checklist Create a checklist for API design quality
```

Produces tailored validation criteria for specific aspects of the specification or implementation.

## Command Resolution

Commands are resolved per integration type. Some agents use dot notation (`speckit.implement`), others use hyphens (`speckit-implement`). Spec Kit automatically dispatches commands using the correct format for each integration.

Run `specify integration list` to see all available integrations in your installed version.
