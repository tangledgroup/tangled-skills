# Context Engineering

## What Is Context Building?

This layer figures out what data is available to better answer the user's request. For coding, that means which files are relevant, what's already been done, style conventions, and so on. During pre-training, models learn the common languages (Python, Rust, etc.); during context building, they learn your workspace conventions and schemas.

**Context engineering is UX engineering:** the product decides what the model sees and when. It's not just a capability question — it's a design question.

## OpenAI's Lessons on AGENTS.md

OpenAI learned this the hard way while building Codex. Their earliest lesson was simple: **give the agent a map, not a 1,000-page instruction manual.**

They tried the "one big AGENTS.md" approach and it failed in predictable ways:

- A giant instruction file crowds out the task and the code
- Too much guidance turns into noise
- It rots quickly
- It's hard to verify mechanically

Their solution: **treat AGENTS.md as the table of contents**, not the encyclopedia. The repository's knowledge base lives in a structured `docs/` directory treated as the system of record. **A short AGENTS.md (roughly 100 lines) gets injected into context and serves primarily as a map, with pointers to deeper sources of truth elsewhere.**

From the agent's point of view, anything it can't access in-context while running effectively doesn't exist.

## Prompt Architecture

If you stare at these projects long enough, you stop thinking of "the system prompt" as text and start treating it like product architecture. Prompts don't just influence what the model says — they decide:

- What the model believes it is
- What it believes it can do
- How consistent the product is across models
- How reproducible the agent is

### Codex: Compiled Contract

Codex treats prompts like a versioned, auditable contract that ships with the binary. Default base instructions are embedded at compile time via `include_str!`, then composed with model-specific instructions and, for some configurations, personality templates.

Codex effectively has prompt families: a base prompt, generic model prompts, codex-tuned model prompts, and orthogonal personality templates injected into a template. This is an architectural choice: behavior is much more tightly tied to releases than in a purely runtime-selected system. Switching models in Codex changes a narrow slice of the instruction surface while the harness contract stays coherent, even though runtime overrides still exist.

### OpenCode: Runtime Routing

OpenCode selects prompt fragments at runtime using model-ID string matching. This is intentionally lightweight, but also easier to break: model IDs are treated as truth, the matching logic relies on substrings rather than a canonical model registry lookup, and the fallback naming is easy to misread — which makes prompt behavior harder to predict.

OpenCode also injects environment state into the prompt, including `Today's date: ${new Date().toDateString()}`. That one line is a big deal: it makes the prompt bytes time-dependent. Great for grounding, bad for reproducibility.

## Tool Descriptions as Prompts

Tool descriptions are prompts too. OpenCode leans into this harder — its `bash.txt` does workflow steering that isn't about Bash at all; it gives the model instructions about how to behave.

This is a design choice: "how to behave" lives close to the tool, not only in the global system prompt.

**If behavior lives in tool descriptions:** the global prompt can be smaller, but each tool description becomes something you need to review carefully.

**If behavior lives in the global prompt:** tool descriptions stay tight, but the base prompt becomes a larger contract to maintain.

## Context Management and Rot

Multi-turn thread state is one of the biggest challenges. Agents aren't "one request." They're threads that grow until they hit a context window, then require compaction or truncation strategies. This is one of the ways each coding agent product differs.

For instance, Claude Code suggests cleaning the context after plan mode. Context management is still one of the biggest issues that defines a good harness — context rot is a common problem, and larger windows (today mostly up to 1M tokens) increase your costs.

As OpenAI puts it: "generally, the cost of sampling the model dominates the cost of network traffic, making sampling the primary target of our efficiency efforts. This is why prompt caching is so important."

## Model-IDE Optimization

In practice, Anthropic models handle tool use and output formatting inside Cursor noticeably better than OpenAI models. Sonnet/Opus feel native, while OpenAI's models often blunder with Cursor's system prompts. This isn't a coincidence — [Cursor is Anthropic's largest customer](https://venturebeat.com/ai/anthropic-revenue-tied-to-two-customers-as-ai-pricing-war-threatens-margins), and along with GitHub Copilot, these two coding clients drive ~25% of Anthropic's revenue. When that much of your business depends on IDEs, your models end up optimized for them.
