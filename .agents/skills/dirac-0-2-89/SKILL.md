---
name: dirac-0-2-89
description: >
  Open-source coding agent that reduces API costs by 64.8% while maintaining
  100% accuracy on complex refactoring tasks. Uses hash-anchored parallel edits,
  AST-native manipulation via tree-sitter, multi-file batching, and high-bandwidth
  context curation. Available as both VS Code extension and CLI. Fork of Cline.
  Use when building or configuring Dirac, understanding its edit engine internals,
  integrating with its tool system, or deploying it as a coding agent in CI/CD.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - coding-agent
  - hash-anchored-edits
  - ast-manipulation
  - tree-sitter
  - multi-file-batching
  - token-efficiency
  - vscode-extension
  - cli
category: agents
external_references:
  - https://github.com/dirac-run/dirac
  - https://dirac.run/
  - https://dirac.run/docs/cli
  - https://www.npmjs.com/package/dirac-cli
---

# Dirac v0.2.89

## Overview

Dirac is an open-source AI coding agent that achieves **64.8% cost reduction** compared to competing agents (Cline, Kilo, Opencode, Roo) while maintaining **100% accuracy** on complex real-world refactoring tasks across repositories like HuggingFace Transformers, VS Code, and Django. It topped the Terminal-Bench-2 leaderboard with a 65.2% score using `gemini-3-flash-preview`.

Its core innovation: instead of search-and-replace edits that force the LLM to repeat unchanged code (O(S+R) output tokens), Dirac uses **hash-anchored edits** that reduce output to only the replacement text (O(R)). Combined with AST-native tools via tree-sitter, multi-file batching, and tight context curation, this makes large-scale refactoring tractable in single tasks.

Dirac is a fork of [Cline](https://github.com/cline/cline) and does **not** use MCP — it implements its own tool protocol directly.

## When to Use

- Deploying Dirac as a coding agent (CLI or VS Code extension)
- Understanding the hash-anchored edit engine architecture
- Integrating with Dirac's tool system or building custom tools
- Configuring subagents, worktrees, or checkpoints for safe parallel editing
- Debugging anchor reconciliation or AST-based refactoring workflows

## Core Concepts

**Hash-Anchored Edits**: Each line in a file is assigned a stable word anchor (e.g., `Moderator§def process():`). When the LLM proposes an edit, it references anchors instead of repeating full search text. The `AnchorStateManager` uses FNV-1a content hashing internally and Myers Diff to reconcile anchors after edits — unchanged lines keep their exact anchor, only new/changed lines get fresh ones. This eliminates cascading invalidation.

**AST-Native Precision**: Dirac embeds tree-sitter parsers for TypeScript, Python, C++, Go, Rust, Java, Ruby, PHP, and more. Tools like `get_file_skeleton`, `get_function`, `find_symbol_references`, `replace_symbol`, and `rename_symbol` operate on the AST rather than raw text, enabling structural refactoring with 100% syntactic accuracy.

**Multi-File Batching**: All `edit_file` blocks in a single LLM turn are grouped by file path, validated in memory, and applied atomically. Diagnostics run in parallel across all modified files after save. This reduces roundtrip latency and API costs significantly.

**High-Bandwidth Context**: Dirac only reads what the LLM needs. File skeletons (AST definition lines with anchors) replace full file reads. The `ContextLoader` extracts file paths, directories, and symbol names from user prompts to auto-enrich context. Conversation condensation (`/smol`) truncates history when needed.

## Advanced Topics

**Architecture Overview**: Codebase modules, core flow (extension → webview → controller → task), CLI vs VS Code extension → [Architecture Overview](reference/01-architecture-overview.md)

**Hash-Anchored Edits Deep Dive**: AnchorStateManager internals, FNV-1a hashing, Myers Diff reconciliation, single-token word anchors, § delimiter, validator, reconciler lifecycle → [Hash-Anchored Edits](reference/02-hash-anchored-edits.md)

**AST-Native Tools**: tree-sitter integration, ASTAnchorBridge, file skeleton extraction, get_function, find_symbol_references, replace_symbol, rename_symbol, symbol index service → [AST-Native Tools](reference/03-ast-native-tools.md)

**Tool System**: All 28 tools (DiracDefaultTool enum), handler patterns, approval workflow, auto-approval, read-only vs write tools → [Tool System](reference/04-tool-system.md)

**Context Curation**: ContextLoader, context condensation, symbol enrichment, high-bandwidth strategy → [Context Curation](reference/05-context-curation.md)

**Subagents, Worktrees & Checkpoints**: Parallel subagent spawning, git worktree isolation, checkpoint-based diff tracking → [Subagents, Worktrees & Checkpoints](reference/06-subagents-worktrees-checkpoints.md)

**CLI Reference**: Commands, flags, slash commands, authentication, environment variables, piping → [CLI Reference](reference/07-cli-reference.md)

**VS Code Extension**: Sidebar, settings, Dirac Rules, browser integration, theme support → [VS Code Extension](reference/08-vscode-extension.md)
