---
name: agent-coding-wyattdave-0-1-0
description: A toolkit for creating custom AI coding agents using prompt engineering, instruction files, and skill modules. Use when building bespoke coding assistants for niche domains where general LLM training data is insufficient or misleading, particularly for specialized frameworks like Power Platform Code Apps with vanilla JavaScript.
version: "0.1.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - ai-agents
  - prompt-engineering
  - vscode-extensions
  - coding-assistants
  - customization
  - claude-code
  - github-copilot
  - context-management
category: development
external_references:
  - https://dev.to/wyattdave/how-to-create-your-own-ai-coding-agent-2h1o
---

# Agent Coding (Wyatt Dave Method)

## Overview

A practical methodology for creating custom AI coding agents through prompt engineering, instruction files, and skill modules — without building or fine-tuning models. Based on David Wyatt's experience building a bespoke coding agent for Power Platform Code Apps using vanilla JavaScript, where general LLM training data was actively misleading.

The core insight: for niche domains, the path of least resistance is **prompting** — not building new models or fine-tuning existing ones. By layering carefully crafted system prompts, project instruction files, and domain-specific skill modules, you can create a coding agent that outperforms general-purpose assistants on specialized tasks.

## When to Use

- Building a custom coding assistant for a niche framework or domain where LLMs have limited or incorrect training data
- Creating VS Code extensions that wrap AI capabilities with domain-specific tooling
- Designing prompt stacks (system prompt + instructions + skills) for coding agents
- Managing context limits and prompt budgets in AI agent architectures
- Iteratively "training" an agent through experience-driven documentation

## Core Concepts

### Why Prompt Over Fine-Tune?

There are three approaches to getting a more bespoke model:

1. **Build your own** — train from scratch (prohibitively expensive)
2. **Fine-tune or distil** an existing model, optionally with reinforcement learning (complex, costly)
3. **Prompt** — layer instructions, context, and skills on top of existing models (accessible, iterative)

The prompt approach is the most practical for most developers. It requires no ML infrastructure, no large datasets, and can be iterated rapidly based on real usage patterns.

### The Prompt Stack

Every AI coding agent operates with a layered prompt stack, from highest priority to lowest:

- **Model System Prompt** — Set by the model owner. Covers security, legality, harmful content prevention. Not accessible or modifiable by users.
- **Application System Prompt** — Added by the application (e.g., GitHub Copilot, Claude Code). Defines available tools, resources, and performance patterns. Closely guarded by platform vendors.
- **Instruction.md** — Project-specific instructions you control. Covers naming conventions, folder structure, design principles, which skills to use, and accumulated learnings from LLM interactions.
- **Skill.md** — Domain-specific knowledge modules that the LLM loads dynamically when relevant. Blurs the line between prompt and context.
- **Your Prompt** — The user's actual request with any additional context.

Instructions and Skills were created by Anthropic for Claude Code, but other tools and models can use them too — just with less consistent or hierarchical results across platforms.

### Platform Choices

Three main approaches to building a custom coding agent:

- **CLI Wrapper** — Command-line interface wrapping an LLM API with custom prompts and tooling
- **VS Code Extension** — Full IDE integration with built-in auth, terminal, custom UI, and marketplace distribution
- **GitHub Copilot Extensions** — Leverages existing Copilot infrastructure with custom skill modules

VS Code extensions offer significant advantages: built-in GitHub Copilot authentication, integrated terminal, custom UI capabilities, button-driven interactions beyond text, no hosting or backend required, and free distribution through the VS Code marketplace.

## Advanced Topics

**Prompt Stack Architecture**: Deep dive into each layer of the prompt stack and how they interact → [Prompt Stack Architecture](reference/01-prompt-stack-architecture.md)

**Implementation Patterns**: Building UI-driven pipelines, iterative agent training, and system prompt design → [Implementation Patterns](reference/02-implementation-patterns.md)

**Context Management**: Strategies for managing context limits, prompt budgets, history compaction, and decision logs → [Context Management](reference/03-context-management.md)
