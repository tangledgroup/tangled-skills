---
name: coding-guidelines-0-1-0
description: Behavioral guidelines to reduce common LLM coding mistakes including overcomplication, hidden assumptions, orthogonal edits, and weak success criteria. Use when writing, reviewing, or refactoring code to enforce simplicity, surgical changes, explicit reasoning, and verifiable outcomes. Derived from Andrej Karpathy's observations on LLM coding pitfalls, curated by Forrest Chang.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - behavioral-guidelines
  - code-quality
  - simplicity
  - llm-best-practices
category: guidelines
external_references:
  - https://github.com/forrestchang/andrej-karpathy-skills
  - https://x.com/karpathy/status/2015883857489522876
---

# Coding Guidelines v0.1.0


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

Behavioral guidelines to reduce common LLM coding mistakes including overcomplication, hidden assumptions, orthogonal edits, and weak success criteria. Use when writing, reviewing, or refactoring code to enforce simplicity, surgical changes, explicit reasoning, and verifiable outcomes. Derived from Andrej Karpathy's observations on LLM coding pitfalls, curated by Forrest Chang.

Behavioral guidelines to reduce common LLM coding mistakes, derived from observations on LLM coding pitfalls.

> **Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## When to Use

- **Writing new code** - Apply before implementation to enforce simplicity and reasoning
- **Code review** - Check diffs against each principle
- **Refactoring** - Ensure surgical scope, no drive-by changes
- **Bug fixing** - Define verifiable success criteria before starting
- **AGENTS.md / agent configuration** - Include as behavioral guardrails

## The Four Principles

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

LLMs often pick an interpretation silently and run with it. This principle forces explicit reasoning.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

**The test:** Would a senior engineer say this is overcomplicated? If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

**The test:** Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform imperative tasks into verifiable goals:

| Instead of... | Transform to... |
|---------------|-----------------|
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test that reproduces it, then make it pass" |
| "Refactor X" | "Ensure tests pass before and after" |

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## Combining the Principles

These principles reinforce each other:

1. **Think** → identify the simplest correct approach
2. **Simplify** → strip away everything not requested
3. **Go surgical** → touch only what's necessary
4. **Verify** → confirm with concrete criteria

When in doubt, ask: "What would the simplest thing that could possibly work look like?" Then do that.

## How to Know It's Working

These guidelines are working if you see:

- **Fewer unnecessary changes in diffs** - Only requested changes appear
- **Fewer rewrites due to overcomplication** - Code is simple the first time
- **Clarifying questions come before implementation** - Not after mistakes
- **Clean, minimal PRs** - No drive-by refactoring or "improvements"

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
