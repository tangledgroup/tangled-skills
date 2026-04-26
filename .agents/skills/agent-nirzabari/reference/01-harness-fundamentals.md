# Harness Fundamentals

## The Simplest Agent That Works

The simplest version of an agentic coding system that actually works is the [ralph wiggum loop](https://ghuntley.com/ralph/):

```bash
while :; do cat PROMPT.md | claude-code --dangerously-skip-permissions; done
```

[Geoffrey Huntley](https://ghuntley.com) created the technique and ran it to build entire programming languages. At a Y Combinator hackathon, a team used it to [ship 6 repos overnight](https://github.com/repomirrorhq/repomirror/blob/main/repomirror.md). No orchestrator, no tool registry, no safety layer — just a model in a loop, reading a prompt file, writing code, and looping back.

### Key Insights from the Ralph Wiggum Pattern

**The feedback loop is everything.** You want to program in ways where the agent can evaluate itself. This could be as simple as instructing it to add logging, or asking it to compile the application and inspect the output. The obsession with finding the perfect prompt is a trap — there is no perfect prompt.

**Agent bias toward minimal implementations.** The agent has an inherent bias toward placeholder and minimal implementations. Huntley's solution was blunt:

> "DO NOT IMPLEMENT PLACEHOLDER OR SIMPLE IMPLEMENTATIONS. WE WANT FULL IMPLEMENTATIONS. DO IT OR I WILL YELL AT YOU."

When the agent drifted too far, he'd `git reset --hard` and start again. Every time something went wrong, he tuned the prompt — "like tuning a guitar."

### Where It Breaks

For many tasks, a while loop and a good prompt can take you surprisingly far. But it breaks in ways that are invisible until they're catastrophic:

- **No context management** — the model eventually drowns in its own output
- **No safety boundary** — `--dangerously-skip-permissions` is right there in the flag name
- **No persistence** — kill the process and your state is gone
- **No recovery** — when the agent loops on the same bug for an hour, nobody notices

The gap between that one-liner and what Codex, Cursor, or Claude Code actually ship is **product engineering**.

## LLM vs Agent: The Distinction

An LLM is typically a gigantic transformer that predicts the next token given a system prompt and a context. But how do you use that building block to create an impressive and capable product — a **harness**?

**OpenAI** uses the word "harness" for Codex's core agent loop and execution logic. In their architecture, the agent loop orchestrates interaction between the user, the model, and the tools — and the "App Server" exposes that harness to multiple clients (TUI, VS Code, desktop, partners) via a stable protocol.

**Anthropic** frames this slightly differently but arrives at the same place. Their ["Building Effective Agents"](https://www.anthropic.com/engineering/building-effective-agents) post describes the basic building block as an "augmented LLM" — a model enhanced with retrieval, tools, and memory. A product is an augmented LLM. The harness is what does the augmenting.

## The Agent Loop

```
"System Prompt" → user → model → tools → model → ...
```

The conversation runs in turns. Because the agent can execute tool calls that modify the local environment, its "output" isn't limited to the assistant message — often the primary output is the code it writes or edits on your machine. But each turn always ends with an assistant message (like "I added the architecture.md you asked for"), which signals a termination state. From the agent's perspective, its work is complete and control returns to the user.

An agent could make hundreds of tool calls in a single turn, potentially exhausting the context window. **That makes context management one of the agent's core responsibilities, and in the current model landscape, probably the most important one.**

## Model Specialization

Today developers route to different models depending on the task:

- **Hebrew conversations and easily-searchable topics** — Gemini (multilingual quality is noticeably better)
- **Coding and technical work** — Anthropic models
- **Deep math, paper analysis, or thorough web research** — ChatGPT with extended thinking or the Pro model

Each player seems to focus their efforts on a slightly different field. This routing strategy is a key part of harness design — knowing which model to call for which task.
