# Stage Resolution

## Contents
- Skill-First Guardrail
- Script-Assisted Resolution
- Stage Analysis
- Resolution Priority Order
- Ambiguity Resolution
- Examples of Stage-to-Capability Mapping

## Skill-First Guardrail

**Before resolving any stage as a shell command or free-text instruction, check if a skill can handle it.**

This is the most important rule in stage resolution. The pipe's purpose is to chain agent capabilities — skills are the richest, most structured of those capabilities. Guessing a `bash` command when a dedicated skill exists defeats the purpose and produces weaker results.

### The Rule

When a stage mentions a project name, tool name, domain keyword, or operation that could match an available skill:

1. Extract keywords from the stage text
2. Run `list-skills.sh --filter <keyword>` to check for matches
3. If skills match, load the most specific one and let it handle the stage
4. **Only if no skills match** fall through to built-in tools, MCP calls, or free-text

### What Triggers a Skill Check?

Any of these in stage text should trigger a skill lookup:

| Stage Pattern | Example Keywords | Likely Skill Match |
|---|---|---|
| Project/tool name | `ruff`, `curl`, `nginx`, `duckdb` | Exact or near-exact skill name |
| Domain operation | `search`, `fetch`, `format`, `validate` | Skills tagged with that domain |
| File format mention | `YAML`, `PDF`, `Dockerfile` | Format-specific skills |
| Protocol mention | `HTTP`, `SSE`, `WebSocket`, `SSH` | Protocol-specific skills |
| Framework mention | `aiohttp`, `nextjs`, `solidjs` | Framework-specific skills |

### What Does NOT Trigger a Skill Check?

These patterns are safe to resolve without skill lookup:

| Stage Pattern | Reason |
|---|---|
| Direct built-in tool names | `read src/main.py`, `edit file.txt`, `write output.md` — these name built-in tools directly |
| Pure reasoning/generation | `summarize`, `count them`, `compare results` — no external capability needed |
| Simple shell operations with no skill equivalent | `ls -la`, `echo hello` — unlikely to have a skill for basic shell commands |

## Script-Assisted Resolution

Use the `list-skills.sh` script to obtain an inventory of available skills:

```bash
bash scripts/list-skills.sh
```

For targeted lookups, use `--filter`:

```bash
bash scripts/list-skills.sh --filter "search"
```

The script outputs a structured list of all available skills with their names, descriptions, and tags. For multiple keywords, run the script multiple times or combine filters:

```bash
bash scripts/list-skills.sh --filter "web" --filter "search"
```

### Why a Script?

With potentially 100+ available skills, relying on the agent's memory alone can lead to missed skills or incorrect selections. The script ensures:
- **Complete inventory**: Every installed skill is surfaced
- **Accurate metadata**: Names, descriptions, and tags are parsed from actual YAML headers
- **No hallucination**: The agent works from real data, not assumptions

## Stage Analysis

Stages in a pipe are heterogeneous — each stage carries its own type of intent. Before resolving, the agent should analyze what kind of operation the stage describes:

| Stage Type | Characteristics | Example |
|---|---|---|
| **Skill invocation** | References a domain, tool, or project that has a corresponding skill | `format with ruff`, `search for "rust async"` |
| **Tool call** | Directly names a built-in tool or describes a simple file operation | `read src/main.py`, `write output.txt` |
| **MCP call** | References an external service or MCP-exposed capability | `query the database via mcp` |
| **Free-text instruction** | Describes reasoning, analysis, or generation that doesn't map to a specific capability | `summarize top 3 results`, `count them` |

The agent should distinguish these types by analyzing the stage's language:
- Does it mention a project/tool name? → **check skill inventory first**
- Does it name a built-in tool directly? → direct tool call
- Does it describe reasoning or generation? → free-text interpretation
- When uncertain, check the skill inventory first

## Resolution Priority Order

After analyzing each stage's intent, resolve by checking capabilities in this priority order:

1. **Skill invocation** — Run `list-skills.sh --filter <keyword>` to check for matching skills. If found, use the skill.
2. **Tool call** — Is there a built-in tool (read, bash, edit, write) that performs the operation?
3. **MCP call** — Is there an MCP server with a relevant tool/resource?
4. **Free-text interpretation** — Treat as a direct instruction to the agent's reasoning.

The first match wins. If multiple skills match, prefer the most specific one (narrowest scope that satisfies the stage).

### Priority Rationale

Skills are checked first because they provide the most structured, domain-specific knowledge. Built-in tools are next because they are always available and fast. MCP calls are third because they require network overhead. Free-text interpretation is last as a fallback for stages that don't map to any explicit capability.

### Never Reinterpret Skill Logic

When a skill is selected for a stage, let the skill handle its own decisions. The pipe orchestrates the chain of stages but does not control or reinterpret how individual skills operate. This principle ensures:

- Skills retain their full autonomy and domain expertise
- Pipe remains a lightweight orchestration layer, not a control mechanism
- Skills can evolve independently without breaking pipe expressions

Example: if a stage invokes a web search skill, the skill decides how many results to return, what format to use, and which backend to query. The pipe just passes the output to the next stage.

## Ambiguity Resolution

When multiple capabilities match a stage:

1. **Prefer specificity**: Choose the narrowest scope that satisfies the stage
2. **Prefer exact keyword match**: If the stage mentions a project/tool name, prefer the skill for that project
3. **Prefer built-in over external**: If a built-in tool and an MCP tool both match, use the built-in
4. **Ask for clarification**: If ambiguity cannot be resolved and the choice significantly affects output, ask the user

Example of ambiguity resolution:

```
/pipe read requirements.txt | analyze dependencies
```

If skills exist for `pip`, `poetry`, and `uv`, and the file is a standard `requirements.txt`, prefer the `pip` skill since it matches the file format. If no format-specific skill matches, fall back to free-text analysis.

## Examples of Stage-to-Capability Mapping

| Stage Text | Resolved Capability | Reasoning |
|---|---|---|
| `read src/main.py` | Built-in `read` tool | Direct built-in tool name — no skill check needed |
| `write output.md` | Built-in `write` tool | Direct built-in tool name — no skill check needed |
| `search for "rust async"` | Skill (web-search or duckduckgo) | "search" is a domain operation → run `list-skills.sh --filter search` → find web-search skill |
| `fetch https://example.com` | Skill (scrapling or jina-ai-reader) | URL fetching has dedicated skills → check inventory first, don't guess `curl` |
| `summarize top 3 results` | Free-text interpretation | No specific skill/tool — agent reasoning |
| `format with ruff` | `ruff` skill | Project name in stage text matches skill |
| `count them` | Free-text interpretation | Context-dependent — agent counts from prior stage output |
| `find function definitions` | Free-text or code analysis skill | Depends on available skills; falls back to reasoning |
| `validate YAML header` | Free-text or validation skill | Depends on context and available capabilities |
| `bash ls -la` | Built-in `bash` tool | Explicit bash invocation — no skill equivalent for basic shell commands |

The key principle: the agent analyzes each stage independently using the skill inventory from `list-skills.sh` and its best judgment. The pipe syntax provides structure, but resolution is agent-driven with script-assisted awareness. **Never guess a shell command when a skill might handle the stage.**
