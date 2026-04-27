---
name: agent-ralph-wiggum-ghuntley
description: Geoffrey Huntley's Ralph Wiggum technique — a monolithic iterative loop pattern for autonomous AI-driven software development. Use when building greenfield projects through repeated LLM invocations in a bash-style loop, tuning prompts through observation, and treating the loop itself as the programmable unit rather than individual tool calls or multi-agent orchestration.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - ralph-wiggum
  - autonomous-development
  - iterative-loops
  - greenfield
  - prompt-tuning
  - context-engineering
  - monolithic-agents
category: agent-patterns
external_references:
  - https://ghuntley.com/ralph/
  - https://ghuntley.com/loop/
---

# Ralph Wiggum Technique (Geoffrey Huntley)

## Overview

The Ralph Wiggum technique is an autonomous software development methodology created by Geoffrey Huntley. At its core, it is a simple bash loop that repeatedly feeds the same prompt to an LLM coding agent:

```bash
while :; do cat PROMPT.md | claude-code; done
```

Ralph replaces the traditional brick-by-brick approach to software with an iterative loop pattern where the operator programs the loop itself — tuning prompts through observation rather than directing individual tool calls. It works best for greenfield projects, displacing a large majority of traditional software engineering effort by running autonomously while the operator watches and tunes.

The technique has been used to build production-grade systems including CURSED, an entirely new programming language compiled via LLVM — built and programmed in a language with zero training data in the model's dataset.

## When to Use

- Building greenfield projects from scratch where you want autonomous, AFK development
- Bootstrapping new codebases where you can tolerate 90% completion then manual finishing
- Situations where you have specifications written and want the LLM to decide implementation priority
- Tuning prompt-based systems through iterative observation rather than direct coding
- Replacing outsourcing for MVP delivery on new projects

**Do not use** Ralph on existing codebases. The technique is designed for greenfield bootstrapping only, with the expectation of reaching approximately 90% completion autonomously.

## Core Concepts

### The Loop Is the Program

Ralph reframes software development. Instead of writing code directly or directing an agent through individual tool calls, you program the loop itself. The prompt is your source code. The bash while-loop is your runtime. You tune by watching failure patterns and adjusting signs (prompt instructions).

> "The beauty of Ralph — the technique is deterministically bad in an undeterministic world."

### Monolithic, Not Distributed

Ralph works as a single process in a single repository performing one task per loop. This contrasts with multi-agent architectures that introduce non-determinism compounded across independent agents. The monolithic approach avoids the complexity of coordinating multiple non-deterministic processes.

### One Task Per Loop

Each loop iteration should accomplish exactly one thing. The LLM decides what is most important to implement next. As projects progress, you may relax this constraint, but if things go off the rails, narrow back down to one item. This discipline keeps context window usage minimal.

### Deterministic Stack Allocation

Every loop iteration receives the same stack allocation: specifications and a plan file. While this burns tokens every loop (re-allocating specs rather than reusing them), it ensures consistency. The practical context window is approximately 170k tokens — use as little as possible for better outcomes.

### Eventual Consistency

Ralph requires faith in eventual consistency. The codebase may be broken at any given moment. Ralph will take wrong directions. Instead of blaming the tools, the operator looks inward — each mistake is an opportunity to tune Ralph by adding new "signs" (prompt instructions) that steer behavior.

### Tuning Through Observation

Like tuning a guitar, Ralph improves through watching the stream and identifying patterns of bad behavior. When Ralph falls off the slide, you add a sign next to the slide saying "SLIDE DOWN, DON'T JUMP." Eventually all Ralph thinks about are the signs, and the output no longer feels defective.

### The Loop Mindset

Beyond the technical loop, Ralph represents a fundamental shift in how to approach software. Software becomes clay on a pottery wheel — if something isn't right, you throw it back on the wheel. This applies not just to forward-mode building but also to reverse-mode clean-rooming and system verification.

## Advanced Topics

**Core Principles**: The philosophical foundations of Ralph as a mindset, not just a technique → [Core Principles](reference/01-core-principles.md)

**Prompt Engineering**: How to structure PROMPT.md with signs, stack allocation, and anti-placeholder directives → [Prompt Engineering](reference/02-prompt-engineering.md)

**Backpressure and Testing**: Wiring validation into the loop through type systems, test suites, and static analysis → [Backpressure and Testing](reference/03-backpressure-and-testing.md)

**Subagent Patterns**: Using subagents for expensive work while keeping the primary context window as a scheduler → [Subagent Patterns](reference/04-subagent-patterns.md)

**Recovery Strategies**: Handling broken codebases, git resets, and rescue prompts when Ralph goes off track → [Recovery Strategies](reference/05-recovery-strategies.md)
