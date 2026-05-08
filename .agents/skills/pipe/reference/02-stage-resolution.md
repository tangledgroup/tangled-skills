# Stage Resolution

## Contents
- Resolution Priority Order
- Discovery Mechanism
- Ambiguity Resolution
- Examples of Stage-to-Capability Mapping

## Resolution Priority Order

When the agent encounters a stage, it resolves it by checking available capabilities in this priority order:

1. **Skill match** — Check if any loaded skill's description matches the stage's intent
2. **Tool call** — Check if a built-in tool (read, bash, edit, write) performs the operation
3. **MCP call** — Check if an MCP server exposes a relevant tool or resource
4. **Free-text interpretation** — Treat as a direct instruction to the agent's reasoning

The first match wins. If multiple skills match, prefer the most specific one (narrowest scope that satisfies the stage).

### Priority Rationale

Skills are checked first because they provide the most structured, domain-specific knowledge. Built-in tools are next because they are always available and fast. MCP calls are third because they require network overhead. Free-text interpretation is last as a fallback for stages that don't map to any explicit capability.

## Discovery Mechanism

The agent discovers available capabilities through:

- **Loaded skills**: Skills listed in the agent's available skills (from `.agents/skills/` or platform-provided)
- **Built-in tools**: Platform-native tools (read, bash, edit, write on pi; equivalent tools on other platforms)
- **MCP servers**: Connected MCP servers and their exposed tools/resources

The agent should check its current capability set at pipe evaluation time — not at skill load time. This ensures resolution reflects the actual runtime environment.

### Resolution Strategy

For each stage:
1. Parse the stage's free-text instruction for key terms and intent
2. Match against skill descriptions (keywords, category, tags)
3. If no skill match, check built-in tools
4. If no tool match, check MCP servers
5. If nothing matches, interpret as free-text instruction

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
| `read src/main.py` | Built-in `read` tool | Direct tool name match |
| `bash ls -la` | Built-in `bash` tool | Direct tool name match |
| `search for "rust async"` | Skill or web search MCP | Keyword match against available skills/MCPs |
| `summarize top 3 results` | Free-text interpretation | No specific skill/tool — agent reasoning |
| `format with ruff` | `ruff` skill | Project name in stage text matches skill |
| `count them` | Free-text interpretation | Context-dependent — agent counts from prior stage output |
| `find function definitions` | Free-text or code analysis skill | Depends on available skills; falls back to reasoning |
| `validate YAML header` | Free-text or validation skill | Depends on context and available capabilities |

The key principle: the agent resolves each stage independently using its best judgment. The pipe syntax provides structure, but resolution is agent-driven.
