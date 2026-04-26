---
name: spec-kit-0-6-1
description: A skill for implementing Spec-Driven Development (SDD) using GitHub's Spec Kit v0.6.1 toolkit, enabling specification-first workflows with AI agents to generate executable specifications, implementation plans, and task breakdowns that drive code generation. Use when building software projects requiring structured specification workflows, integrating AI coding assistants (Claude, Copilot, Gemini, Pi, etc.) with spec-driven methodologies, or migrating existing projects to specification-first development practices.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.6.1"
tags:
  - specification-driven-development
  - sdd
  - ai-assisted-development
  - project-management
  - workflow-automation
  - slash-commands
  - feature-specification
category: development
external_references:
  - https://github.com/github/spec-kit
---

# Spec Kit 0.6.1

## Overview

Spec Kit is an open-source toolkit by GitHub that enables **Spec-Driven Development (SDD)** — a methodology where specifications become the primary artifact and code serves as their generated expression. It provides the `specify` CLI to bootstrap projects, plus slash commands (`/speckit.*`) that integrate with 30+ AI coding agents to automate the specification → planning → tasking → implementation workflow.

The core idea: instead of writing code directly from prompts ("vibe coding"), you first create rich specifications, then derive technical plans and executable tasks from them. This eliminates the gap between intent and implementation by making specifications precise enough to generate working systems.

## When to Use

- Starting a new project with structured specification-first development
- Integrating AI coding assistants (Claude Code, Copilot, Gemini CLI, Codex, Pi, etc.) with SDD workflows
- Creating governing principles (constitution) for a development project
- Breaking complex features into specifications, plans, and actionable tasks
- Extending Spec Kit with custom commands via the extension system
- Customizing Spec Kit behavior via presets (template/command overrides)
- Migrating existing projects to specification-driven practices
- Publishing extensions or presets to the community catalog

## Core Concepts

### Spec-Driven Development (SDD)

SDD inverts the traditional power structure: specifications don't serve code — code serves specifications. The Product Requirements Document (PRD) is the source that generates implementation. Technical plans are precise definitions that produce code. This eliminates the gap between intent and implementation.

Key principles:
- **Intent-driven development** — team intent expressed in natural language, design assets, and core principles
- **Executable specifications** — precise, complete, unambiguous enough to generate working systems
- **Continuous refinement** — consistency validation as an ongoing process, not a one-time gate
- **Research-driven context** — agents gather technical context throughout specification
- **Bidirectional feedback** — production reality informs specification evolution
- **Branching for exploration** — multiple implementation approaches from the same specification

### The Six-Step Workflow

1. **`specify init`** — Bootstrap the project with Spec Kit structure and agent integration
2. **`/speckit.constitution`** — Define governing principles and development guidelines
3. **`/speckit.specify`** — Create feature specifications (what and why, not how)
4. **`/speckit.plan`** — Generate technical implementation plans with architecture choices
5. **`/speckit.tasks`** — Break down into actionable, parallelizable task lists
6. **`/speckit.implement`** — Execute all tasks to build the feature

Optional quality gates:
- **`/speckit.clarify`** — Resolve ambiguities in specifications before planning
- **`/speckit.analyze`** — Cross-artifact consistency and coverage analysis
- **`/speckit.checklist`** — Generate custom quality validation checklists

### Feature Numbering and Branching

Spec Kit uses automatic feature numbering (001, 002, 003…) and creates semantic git branches for each feature. The active feature is detected from the current branch name. Specs live in `specs/<feature-number>-<name>/` directories.

### Constitution

The constitution (`memory/constitution.md`) is a set of immutable architectural principles governing how specifications become code. It includes articles covering library-first design, CLI interface mandates, test-first development, simplicity gates, anti-abstraction rules, and integration-first testing.

### Extensions and Presets

- **Extensions** add new capabilities (new commands, integrations, workflows)
- **Presets** customize existing behavior (template overrides, terminology, compliance formats)
- Template resolution walks top-down: project overrides → presets → extensions → core defaults

## Installation / Setup

Spec Kit is installed from GitHub (not PyPI). The official package is `specify-cli`.

### Persistent Installation (Recommended)

```bash
# Pin a specific release tag for stability
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z

# Or with pipx
pipx install git+https://github.com/github/spec-kit.git@vX.Y.Z
```

### One-Shot Usage

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init <PROJECT_NAME>
```

### Initialize a Project

```bash
# New project directory
specify init <PROJECT_NAME>

# Current directory
specify init . --integration copilot

# Force merge into non-empty directory
specify init . --force --integration claude

# Skip git initialization
specify init my-project --no-git

# Specify script type (sh or ps)
specify init my-project --script sh
```

### Prerequisites

- Linux, macOS, or Windows (PowerShell scripts supported)
- Python 3.11+
- Git
- `uv` (recommended) or `pipx` for package management
- Supported AI coding agent

## Usage Examples

### Complete Workflow: Building a Photo Album App

```bash
# Step 1: Initialize project
specify init photo-albums --integration claude

# Step 2: Define constitution (in your coding agent)
/speckit.constitution Library-first approach, strict TDD, functional programming patterns

# Step 3: Create specification
/speckit.specify Build an application to organize photos in albums grouped by date. Albums are flat (no nesting). Photos previewed in a tile interface with drag-and-drop reorganization.

# Step 4: Clarify ambiguities
/speckit.clarify Focus on security and performance requirements

# Step 5: Create technical plan
/speckit.plan Vite with vanilla HTML/CSS/JS. SQLite for metadata. No image uploads — local storage only.

# Step 6: Generate tasks
/speckit.tasks

# Step 7: Analyze (optional quality gate)
/speckit.analyze

# Step 8: Implement
/speckit.implement
```

### Using Extensions

```bash
# Search available extensions
specify extension search jira

# Install from catalog
specify extension add spec-kit-jira

# List installed extensions
specify extension list

# Remove an extension
specify extension remove spec-kit-jira --keep-config
```

### Upgrading

```bash
# Upgrade CLI
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@vX.Y.Z

# Update project files
specify init --here --force --integration copilot

# Restore custom constitution (known issue: --force overwrites it)
git restore .specify/memory/constitution.md
```

## Advanced Topics

**SDD Methodology**: The philosophy, workflow, and constitutional foundation of spec-driven development → See [SDD Methodology](reference/01-sdd-methodology.md)

**Slash Commands Reference**: Complete reference for all core and optional `/speckit.*` commands → See [Slash Commands Reference](reference/02-slash-commands.md)

**Extensions System**: Extension manifest schema, command files, hooks, catalog publishing, and development guide → See [Extensions System](reference/03-extensions.md)

**Presets System**: Preset structure, template overrides, stacking priority, and publishing guide → See [Presets System](reference/04-presets.md)

**CLI Reference**: `specify` CLI commands, flags, environment variables, and troubleshooting → See [CLI Reference](reference/05-cli-reference.md)
