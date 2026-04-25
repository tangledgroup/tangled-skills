---
name: agent-coding-wyattdave
description: A toolkit for creating custom AI coding agents using prompt engineering, instruction files, and skill modules. Use when building bespoke coding assistants for niche domains where general LLM training data is insufficient or misleading, particularly for specialized frameworks like Power Platform Code Apps with vanilla JavaScript.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - ai-agents
  - prompt-engineering
  - vscode-extensions
  - coding-assistants
  - customization
category: development
required_environment_variables: []

external_references:
---
## Overview
A toolkit for creating custom AI coding agents using prompt engineering, instruction files, and skill modules. Use when building bespoke coding assistants for niche domains where general LLM training data is insufficient or misleading, particularly for specialized frameworks like Power Platform Code Apps with vanilla JavaScript.

## When to Use
- Building coding agents for specialized frameworks or SDKs with limited documentation
- Creating domain-specific assistants that avoid misleading general training data
- Developing VS Code extensions that integrate AI with custom UI and CLI commands
- Implementing prompt stacks with system prompts, instructions, and skills
- Optimizing context usage for LLMs with token limits
- Training agents through iterative testing and documentation of learnings

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.## Overview

A toolkit for creating custom AI coding agents using prompt engineering, instruction files, and skill modules. Use when building bespoke coding assistants for niche domains where general LLM training data is insufficient or misleading, particularly for specialized frameworks like Power Platform Code Apps with vanilla JavaScript.

A comprehensive approach to building custom AI coding agents through layered prompt engineering, instruction files, and modular skill systems. This methodology enables creation of specialized coding assistants for niche domains where general LLM training is insufficient or counterproductive.

## Quick Start
### Understanding the Prompt Stack

The agent uses a hierarchical prompt structure:

1. **Model System Prompt** - Security and legality guidelines from model provider
2. **Application System Prompt** - Tool-specific instructions and patterns
3. **Instruction.md** - Project-specific conventions and principles
4. **Skill.md** - Task-specific knowledge loaded dynamically
5. **User Prompt** - The actual request with context

See [Prompt Stack Architecture](reference/01-prompt-stack.md) for detailed explanation of each layer.

### Platform Selection

Choose implementation platform based on requirements:

| Platform | Advantages | Best For |
|----------|-----------|----------|
| VS Code Extension | Built-in auth, terminal, custom UI, free distribution | Integrated development workflows |
| CLI Wrapper | Cross-platform, scriptable, lightweight | Automation and DevOps |
| GitHub Copilot Extensions | Leverages existing Copilot license | Enhanced Copilot functionality |

Refer to [Platform Implementation](reference/02-platform-implementation.md) for build guidance.

### Core Components

Build three main advantages over generic assistants:

1. **Simplified UI-based CLI commands** - Abstract complex CLI operations into button presses
2. **Custom system prompt** - Prevent LLM from using misleading general training
3. **Skill files** - Document all learnings from implementation experience

See [Implementation Guide](reference/03-implementation.md) for component details.

## Advanced Topics
## Advanced Topics

- [Prompt Stack](reference/01-prompt-stack.md)
- [Platform Implementation](reference/02-platform-implementation.md)
- [Implementation](reference/03-implementation.md)
- [Context Optimization](reference/04-context-optimization.md)
- [Training Workflow](reference/05-training-workflow.md)

## Troubleshooting
### Context Limit Issues

**Symptom**: "No choices" errors or failures on work accounts with lower limits

**Solutions**:
- Minimize system prompts, instruction.md, and skill.md content
- Send only relevant skill files (let LLM choose which ones needed)
- Use tight file trees to limit sent data
- Implement decision log files to compact history
- Break projects into tasks, remove tool calls after completion

See [Context Optimization](reference/04-context-optimization.md) for detailed strategies.

### Model Performance Variations

**Symptom**: Great results on Opus 4.6/GPT-5.4 but poor on Auto or GPT-4.1

**Solution**: Recommend better models during setup and document prompting strategies for older models

### Duplicate CLI Installations

**Symptom**: Extension uses wrong/outdated CLI version

**Solution**: Move functionality to UI buttons, have LLM guide users to use buttons when issues occur

**Note:** Code is deterministic - move critical functionality to traditional code/UI whenever possible.

## Key Principles
1. **Iterative Training** - Build many apps, read reasoning, document every bug resolution
2. **Test Extensively** - Each test generates nudges/tweaks to instructions and prompts
3. **Document Learnings** - The secret sauce is learning from experience and documenting it
4. **Minimize Context** - Optimize prompt stack size for token-limited environments
5. **Move to Code** - When possible, implement in deterministic code rather than LLM decisions

