---
name: nirzabari-agent
description: A comprehensive guide to understanding and building coding agent harnesses, covering the 7-layer architecture, context engineering, tool orchestration, safety systems, and real-world implementations from Codex, OpenCode, Cursor, and Claude Code. Use when designing agentic systems, analyzing agent architectures, implementing harness patterns, or studying production-grade coding agent implementations.
version: "0.2.0"
author: Generated from Nir Zabari's research <nirzabari.github.io>
license: MIT
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
required_environment_variables: []
---

# Nir Zabari Agent Skill

A comprehensive toolkit for understanding and building production-grade coding agent harnesses, based on deep analysis of real-world implementations including Codex CLI, OpenCode, Cursor, and Claude Code. This skill covers the complete architecture from agent loops to safety systems, with practical patterns from systems that have written millions of lines of code autonomously.

## When to Use

- Designing a coding agent system or harness architecture
- Analyzing the difference between LLMs and agentic systems
- Implementing context building strategies for agents
- Building tool orchestration and safety layers
- Studying production agent implementations (Codex, OpenCode, Cursor)
- Understanding multi-agent coordination patterns
- Learning about streaming APIs and event-driven agent architectures
- Planning long-running autonomous coding tasks
- Researching harness engineering best practices

## Quick Start

### The Core Insight

**LLM ≠ Agent**. An LLM is a text generation model. A coding agent is a **harness** - a runtime system that repeatedly builds context, calls the model, executes tools, persists state, and loops back. The gap between "call an LLM" and "ship a coding product" is entirely product engineering.

### The 7-Layer Architecture

Every production coding agent implements these layers:

1. **Agent Loop** - Conversation turns with tool execution
2. **Context Building** - What data the model sees and when
3. **Tooling Systems** - Registry of available tools with schemas
4. **Safety** - Approvals, policies, sandboxes, undo
5. **Replay/Persistence** - Event logs for debugging and recovery
6. **Client Surface** - TUI, Web, or IDE interface
7. **Extensibility** - MCP, plugins, AGENTS.md conventions

See [Layer Architecture Deep Dive](references/01-layer-architecture.md) for complete breakdown of each layer with code examples.

### Simple vs Production Agents

The simplest working agent is the [Ralph Wiggum loop](https://ghuntley.com/ralph/):

```bash
while :; do cat PROMPT.md | claude-code --dangerously-skip-permissions; done
```

This works surprisingly well but lacks: context management, safety boundaries, persistence, recovery mechanisms, and multi-client support. Production agents add all of these through harness engineering.

Learn more in [Ralph Wiggum Pattern](references/02-ralph-wiggum-pattern.md).

## Reference Files

- [`references/01-layer-architecture.md`](references/01-layer-architecture.md) - Complete 7-layer breakdown with Codex vs OpenCode comparison
- [`references/02-ralph-wiggum-pattern.md`](references/02-ralph-wiggum-pattern.md) - Simple loop pattern and Geoffrey Huntley's insights
- [`references/03-context-engineering.md`](references/03-context-engineering.md) - Context building strategies, AGENTS.md patterns, prompt design
- [`references/04-tool-systems.md`](references/04-tool-systems.md) - Tool orchestration, registry patterns, model-aware tool swapping
- [`references/05-safety-systems.md`](references/05-safety-systems.md) - Approvals, AST parsing, sandboxing, permission brokers
- [`references/06-streaming-apis.md`](references/06-streaming-apis.md) - SSE events, Anthropic vs OpenAI streaming contracts
- [`references/07-multi-agent-coordination.md`](references/07-multi-agent-coordination.md) - Parallel agents, planner/worker patterns, lock-free coordination
- [`references/08-codex-deep-dive.md`](references/08-codex-deep-dive.md) - Codex CLI architecture, Rust implementation details
- [`references/09-opencode-deep-dive.md`](references/09-opencode-deep-dive.md) - OpenCode client-server architecture, TypeScript/Bun implementation
- [`references/10-scaling-patterns.md`](references/10-scaling-patterns.md) - Long-running agents, million-line codebases, Cursor's scaling experiments

## Key Concepts

### Harness Engineering

The term "harness" (used by OpenAI) refers to the system around the model that makes it useful. Key principles:

- **Give agents a map, not a 1000-page manual** - Short AGENTS.md (~100 lines) as table of contents, with detailed docs in structured directories
- **Context engineering is UX engineering** - The product decides what the model sees and when
- **Streaming as events, not just text** - Tool calls must stream as they happen for responsive UIs
- **Safety is architecture, not warnings** - Approvals, policies, sandboxes, and undo mechanisms

### Model Specialization

Different models excel at different tasks:
- **Hebrew/multilingual**: Gemini (superior multilingual quality)
- **Coding/technical**: Anthropic models (Sonnet/Opus consistently best for coding)
- **Math/research**: ChatGPT with extended thinking or Pro model
- **Long-running autonomy**: GPT-5.2 (better at following instructions, avoiding drift)

### Multi-Agent Patterns

From Cursor's scaling experiments (1M+ lines of code, weeks of runtime):

**Planners and Workers Pattern:**
- Planners explore codebase, create tasks, spawn sub-planners recursively
- Workers pick up tasks, complete them without coordination, push changes
- Judge agent determines whether to continue at cycle end

This solved coordination problems that flat agent structures couldn't handle.

### The Bottom Line

> "When something failed, the fix was almost never 'try harder.' Human engineers always stepped into the task and asked: 'what capability is missing, and how do we make it both legible and enforceable for the agent?'"

**Humans steer. Agents execute.** The question is whether we can build harnesses that let them do it reliably.

## Troubleshooting

### Common Agent Issues

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Agent drifts off-task | Context window rot, no grounding | Implement context compaction, add date/instructions to prompt |
| Placeholder implementations | Model bias toward minimal code | Explicit anti-placeholder instructions in system prompt |
| Tool call formatting errors | Model not optimized for tool schema | Use models trained on specific IDE/harness (Anthropic for Cursor) |
| Lock contention in multi-agent | Flat agent structure with locks | Switch to planner/worker hierarchy, use optimistic concurrency |
| Agent stuck on same bug | No feedback loop | Add self-evaluation steps, compile/test in loop |

See [Layer Architecture](references/01-layer-architecture.md) and [Scaling Patterns](references/10-scaling-patterns.md) for detailed solutions.

## Related Resources

- **OpenAI Harness Engineering**: https://openai.com/index/harness-engineering/
- **Anthropic Building Effective Agents**: https://www.anthropic.com/engineering/building-effective-agents
- **Cursor Scaling Blog**: https://cursor.com/blog/scaling-agents
- **Geoffrey Huntley's Ralph Wiggum**: https://ghuntley.com/ralph/
- **Open Responses Standard**: https://www.openresponses.org/
- **AGENTS.md Best Practices**: https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md/

## Architecture Comparison

| Dimension | Codex CLI | OpenCode | Cursor |
|-----------|-----------|----------|--------|
| **Architecture** | Single-process Rust TUI | Client-server TS/Bun | Proprietary IDE |
| **Agent Loop** | Tokio event loop multiplexing | SSE event backbone | Optimized for Anthropic |
| **Context** | Compiled prompts + model overlays | Runtime model-ID matching | Proprietary optimization |
| **Tools** | Compiled + MCP through orchestrator | Dynamic registry + plugins | Custom tool system |
| **Safety** | Orchestrator approvals + sandbox | AST parsing + permission broker | Proprietary |
| **Extensibility** | MCP as runtime component | First-class plugins | Marketplace |

See individual deep dives in [Codex Architecture](references/08-codex-deep-dive.md) and [OpenCode Architecture](references/09-opencode-deep-dive.md).

## Important Notes

1. **Context management is the hardest problem** - Context window rot limits all long-running agents
2. **Model choice matters for role** - Different models excel at planning vs execution
3. **Simplicity wins** - Many improvements came from removing complexity, not adding it
4. **Tests define what agents solve** - High-quality test harnesses are critical
5. **Prompt quality > architecture** - Extensive prompt experimentation often matters more than system design
6. **100ms latency target** - For perceived immediacy in UI responsiveness
7. **Cost vs quality tradeoff** - $20k for 100K lines (Anthropic C compiler case) is cost-effective but needs human verification

This skill is based on Nir Zabari's March 2026 analysis of coding agent architectures, supplemented with documentation from Codex, OpenCode, Cursor, and related research. The field evolves rapidly - always check latest documentation for specific implementations.
