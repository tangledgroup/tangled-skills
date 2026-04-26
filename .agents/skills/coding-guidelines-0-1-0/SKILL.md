---
name: coding-guidelines-0-1-0
description: Behavioral guidelines to reduce common LLM coding mistakes including
  overcomplication, hidden assumptions, orthogonal edits, and weak success criteria.
  Use when writing, reviewing, or refactoring code to enforce simplicity, surgical
  changes, explicit reasoning, and verifiable outcomes. Derived from Andrej Karpathy's
  observations on LLM coding pitfalls, curated by Forrest Chang.
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

# Coding Guidelines 0.1.0

## Overview

Behavioral guidelines to reduce common LLM coding mistakes, derived from Andrej Karpathy's observations on how AI coding agents systematically produce overcomplicated code, make hidden assumptions, and perform orthogonal edits that touch more than they should. Curated by Forrest Chang into four actionable principles.

These guidelines bias toward caution over speed. For trivial tasks — simple typo fixes, obvious one-liners — use judgment. The goal is reducing costly mistakes on non-trivial work, not slowing down simple tasks.

## When to Use

Apply these guidelines when:

- Writing new code or features
- Reviewing generated code before accepting it
- Refactoring existing codebases
- Debugging issues introduced by LLM-generated changes
- Setting up behavioral rules for AI coding assistants (CLAUDE.md, Cursor rules, pi skills)
- Evaluating whether a code change is appropriately scoped

## The Four Principles

**Think Before Coding**: Don't assume. Don't hide confusion. Surface tradeoffs. State assumptions explicitly and push back when simpler approaches exist.

**Simplicity First**: Minimum code that solves the problem. Nothing speculative. No features beyond what was asked, no abstractions for single-use code.

**Surgical Changes**: Touch only what you must. Clean up only your own mess. Every changed line should trace directly to the user's request.

**Goal-Driven Execution**: Define success criteria. Loop until verified. Transform imperative tasks into declarative goals with verification loops.

## How to Know It's Working

These guidelines are effective when you observe:

- Fewer unnecessary changes in diffs — only requested changes appear
- Fewer rewrites due to overcomplication — code is simple the first time
- Clarifying questions come before implementation — not after mistakes
- Clean, minimal PRs — no drive-by refactoring or "improvements"

## Advanced Topics

**The Four Principles**: Detailed guidance for each principle with rules and tests → [The Four Principles](reference/01-four-principles.md)

**Code Examples**: Real-world examples showing what LLMs commonly do wrong and how to fix it → [Code Examples](reference/02-code-examples.md)

**Anti-Patterns & Key Insights**: Summary of common anti-patterns, the timing problem, and why "good" patterns become bad when applied too early → [Anti-Patterns and Key Insights](reference/03-anti-patterns.md)
