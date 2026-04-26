---
name: agent-nirzabari
description: A comprehensive guide to understanding and building coding agent harnesses, covering the 7-layer architecture, context engineering, tool orchestration, safety systems, and real-world implementations from Codex, OpenCode, Cursor, and Claude Code. Use when designing agentic systems, analyzing agent architectures, implementing harness patterns, or studying production-grade coding agent implementations.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - ai-agents
  - coding-agents
  - harness-engineering
  - llm-systems
  - agent-architecture
  - tool-orchestration
  - context-management
  - codex
  - opencode
  - cursor
category: ai-agents
external_references:
  - https://nirzabari.github.io/blog/2026-03-07-coding-agents
---

# Coding Agent Harness Architecture

## Overview

An LLM is neither a coding agent nor a product. A coding agent product is a text generation model coupled with a **harness** — a runtime that repeatedly builds context, calls the model, executes tool calls, persists state, renders to the user, recovers from failures, and loops back. This guide covers the 7-layer architecture of production-grade coding agents, drawn from analysis of real codebases including Codex (OpenAI), OpenCode, Claude Code, and Cursor.

The gap between a simple loop like `while :; do cat PROMPT.md | claude-code; done` and what Codex or Claude Code actually ship is **product engineering**. That gap — context management, safety boundaries, persistence, recovery, and multi-client support — is the subject of this skill.

## When to Use

- Designing agentic systems that go beyond simple prompt loops
- Analyzing agent architectures across different products (Codex, OpenCode, Claude Code, Cursor)
- Implementing harness patterns for context building, tool orchestration, or safety
- Studying production-grade coding agent implementations and their trade-offs
- Understanding the LLM provider contract (streaming events, tool calling, multi-turn state)
- Building scalable autonomous coding systems with parallelization and specialization

## Core Concepts: The 7 Layers

A coding agent harness consists of 7 layers:

1. **Agent Loop** — Conversation turns: system prompt → user → model → tools → model → ... Each turn can include hundreds of tool calls. Context management is the agent's core responsibility.
2. **Context Building** — Gathering relevant data: which files are relevant, what's been done, style conventions. Context engineering is UX engineering — the product decides what the model sees and when.
3. **Tooling Systems** — Tool registry with argument schemas, multi-modal support, and parameters. Examples: shell, file edit, code search, browser automation, screenshot analysis.
4. **Safety** — Allowlists/denylists, sandboxing, snapshotting, recovery. Safety is architecture — approvals, policies, sandboxes, and undo.
5. **Replay / Persistence** — Forking chats and environments for debugging. Systems are made of turns, tool calls, diffs, approvals, and events that must be restorable.
6. **Client Surface (TUI / Web / IDE)** — How the user interacts: TUI (OpenCode, Claude Code, Codex), IDE (Cursor, Antigravity, Replit Agent), or Web (Bolt.new, v0, Lovable).
7. **Extensibility** — MCP for tool connectivity, AGENTS.md for repo-specific instructions, Skills for Anthropic's convention, and Open Responses for provider-agnostic API shape.

## Capability Jumps

Four major jumps in AI capability from a user's perspective:

1. **GPT-3.5** (ChatGPT, November 2022) — the leap was the product itself, not just the model
2. **GPT-4** (Spring 2023)
3. **Reasoning models** (o1-preview, then o3 in Spring 2025)
4. **Actually useful agentic systems** (late 2025, strong reasoning models paired with solid harnesses)

## Advanced Topics

**Harness Fundamentals**: The simplest agent loop, ralph wiggum pattern, and why it breaks at scale → [Harness Fundamentals](reference/01-harness-fundamentals.md)

**Context Engineering**: Prompt architecture, AGENTS.md patterns, OpenAI's lessons on context management → [Context Engineering](reference/02-context-engineering.md)

**Tooling Systems**: Tool registries, compiled vs dynamic tool handlers, Codex orchestrator vs OpenCode plugins → [Tooling Systems](reference/03-tooling-systems.md)

**Safety and Persistence**: Allowlists, sandboxing, AST-based command analysis, replay architecture → [Safety and Persistence](reference/04-safety-and-persistence.md)

**Client Surfaces and Extensibility**: TUI vs Web vs IDE patterns, MCP integration, Skills, plugin systems → [Client Surfaces and Extensibility](reference/05-client-surfaces-and-extensibility.md)

**LLM Provider Contract**: Streaming events (SSE), three-phase tool call lifecycle, multi-turn thread state, portability → [LLM Provider Contract](reference/06-llm-provider-contract.md)

**Harness Deep Dive**: Codex (Rust monolith) vs OpenCode (TS/Bun control-plane) architecture comparison across all 7 layers → [Harness Deep Dive](reference/07-harness-deep-dive.md)

**Scaling Case Study**: Anthropic's C compiler case study — parallel Claude agents, git-based coordination, lessons learned → [Scaling Case Study](reference/08-scaling-case-study.md)
