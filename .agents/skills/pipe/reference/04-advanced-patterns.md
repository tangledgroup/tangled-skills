# Advanced Patterns

## Contents
- Multi-Line Pipes
- Composition With Other Meta-Skills
- Reusable Pipe Templates
- Limitations and Known Constraints

## Multi-Line Pipes

Pipes can span multiple lines for readability. Use one of these continuation styles:

### Implicit Continuation (Recommended)

Each line after the first starts with `|` to indicate it is a continuation of the pipe:

```
/pipe search for "distributed consensus algorithms"
| summarize top 5 results
| extract key terms from summaries
| generate comparison table
```

The leading `|` on continuation lines signals that the stage belongs to the same pipe expression. This is the preferred style as it is unambiguous and doesn't conflict with markdown table syntax.

### Code Block Enclosure

For complex pipes, enclose the entire expression in a code block:

````
```
/pipe read architecture.md
| extract component names
| for each component, find related files
| generate dependency graph
```
````

The code block preserves all `|` characters literally and avoids any markdown parsing interference.

### Line Continuation with `\`

Standard backslash continuation works but is less readable:

```
/pipe read config.yaml \
| extract database settings \
| validate connection string
```

This style is valid but not recommended — implicit continuation (leading `|`) is clearer.

## Composition With Other Meta-Skills

Pipes compose with other meta-skills to drive structured workflows:

### Pipe + Plan

Use pipes within plan tasks to specify multi-step execution for a single task:

```markdown
- ☐ Task 3.2 Analyze and report (depends on: Task 3.1)
  - Execute: /pipe read analysis-data.csv | compute statistics | generate report
```

The pipe defines the concrete steps; the plan tracks completion status.

### Pipe + Evaluation-Driven Development

Use pipes to chain evaluation steps:

```
/pipe run baseline test without skill | record results
| load skill and re-run same test | record results
| compare scores and identify gaps
```

## Reusable Pipe Templates

Document common pipe patterns as templates for reuse. This reduces repetition and ensures consistent execution across similar tasks.

### Template Pattern

Define a named template with parameterized stages:

```
Template: "code-review-pipe"
/pipe read <file> | check for bugs | suggest improvements | format as checklist
```

When the user requests a code review, substitute `<file>` and execute the template. Templates are conventions — not a formal syntax. The agent should recognize repeated pipe patterns and suggest templating them.

### Common Templates

| Template Name | Pipe Expression | Use Case |
|---|---|---|
| Search & Summarize | `search <query> \| summarize results` | Quick research |
| Read & Analyze | `read <file> \| analyze content \| report findings` | Code/document review |
| Transform & Validate | `read <input> \| transform to <format> \| validate output` | Data migration |
| Explore & Document | `bash ls -R \| filter <pattern> \| generate file tree` | Project exploration |

## Limitations and Known Constraints

- **No nested pipes**: A pipe stage cannot itself contain a pipe expression. Use sequential separate pipes instead.
- **No branching within pipes**: Pipes are strictly linear. For conditional logic, use separate pipes or free-text instructions that include conditionals.
- **No variable binding**: Pipes don't support named variables between stages. Context propagation is implicit — the next stage sees all prior outputs but cannot reference them by name.
- **No loops**: Pipes execute each stage exactly once. For iteration, use a single stage that describes the loop (e.g., "for each file found, do X").
- **Context size limits**: Very long pipes with many stages may exceed context windows. Keep pipes to 5-10 stages for reliability; break longer workflows into multiple pipes.
- **Markdown table collision**: Never start or end a line with `|` alone — this triggers markdown table rendering. Always have content before and after the `|` delimiter on the same line, or use implicit continuation style with content after the leading `|`.
