# Prompt Stack Architecture

## Model System Prompt

The highest priority layer, set by the model owner. This is not accessible or modifiable by users. It covers:

- Not sharing how to perform illegal actions
- Not encouraging harmful actions
- Not sharing confidential information about the model itself

This layer establishes safety guardrails that all downstream prompts must operate within. You cannot override it.

## Application System Prompt

The next level down, added by the application you use (e.g., GitHub Copilot chat, Claude Code, Cursor). This covers specific tools and mechanisms the application provides:

- Tool definitions (e.g., "this tool reads the local folder")
- Resource references (e.g., "this resource provides information about X")
- Performance patterns discovered by the application designer (e.g., "when dealing with CLI commands, ensure authentication is validated first")

These are closely kept secrets by platform vendors. You cannot see or modify this layer directly, but understanding its existence helps you design your own prompts to complement rather than conflict with it.

## Instruction.md

Project-specific instructions that you fully control. These generally cover:

- **Naming conventions** — consistent file and variable naming patterns
- **Folder structure** — expected directory layout for the project
- **Design principles** — architectural guidelines and coding standards
- **Skill references** — which skills should be used in which situations
- **Accumulated learnings** — insights from LLM interactions that can be set to update the file automatically

This layer ensures project consistency and makes code easier to read and maintain. It is sent with every request, so keep it concise.

Example structure:

```markdown
# Project Instructions

## Naming Conventions
- Use camelCase for JavaScript variables
- Prefix connection helpers with `conn_`

## Folder Structure
- `/src` — application source code
- `/extensions` — VS Code extension files
- `/skill.md` — domain-specific skill definitions

## Design Principles
- Vanilla JavaScript only, no React or TypeScript
- Keep functions under 50 lines
- Always validate authentication before CLI operations

## Learnings
- The Power Platform CLI requires tenant auth before any connection commands
- Do not use npm package managers in Code Apps context
```

## Skill.md

Domain-specific knowledge modules that blur the line between prompt and context. They are specific instructions or knowledge sources for particular situations. By moving them out of the main instruction file, the LLM decides when to load them — acting as dynamic context.

Key characteristics:

- **Dynamic loading** — The LLM chooses which skills to reference based on the current task
- **Domain-specific** — Each skill covers a narrow area of expertise
- **Reusable** — Skills can be shared across projects in the same domain

Examples from the ecosystem:

- [Frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) — UI/UX design guidelines
- [Working-With-PowerPoint-Files](https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md) — PPTX file manipulation
- [Canvas-design](https://github.com/anthropics/skills/blob/main/skills/canvas-design/SKILL.md) — Canvas-based rendering
- [Power-Automate-expressions](https://github.com/wyattdave/Power-Automate-Utility/blob/main/extension/src/skill.md) — Power Automate expression syntax

Instructions and Skills were created by Anthropic for Claude Code. Other tools and models can use them too, but with less consistent or hierarchical results across platforms.

## Your Prompt

The final layer is your actual request, sent with any additional context. This is the only layer that changes per interaction. Everything above it forms the stable foundation that shapes how the LLM interprets and responds to your request.

### Layer Priority

Higher layers override lower layers. The model system prompt cannot be overridden by anything below it. Your prompt has the lowest priority but provides the specific task context that activates the entire stack.
