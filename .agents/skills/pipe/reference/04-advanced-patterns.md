# Advanced Patterns

## Contents
- Long Pipes
- Composition With Other Meta-Skills
- Reusable Pipe Templates
- Limitations and Known Constraints

## Long Pipes

Always keep pipe expressions on a single line. Starting a line with `|` triggers markdown table rendering and corrupts the expression.

For long pipes that are hard to read on one line, enclose the entire expression in a code block:

````
```
/pipe search for "distributed consensus algorithms" | summarize top 5 results | extract key terms from summaries | generate comparison table
```
````

The code block preserves all `|` characters literally and avoids markdown parsing interference.

## Composition With Other Meta-Skills

Pipes compose with other meta-skills to drive structured workflows. The pipe provides the execution chain; the meta-skill provides the framework or tracking.

### Pipe Within Workflow Tasks

Use pipes within workflow task definitions to specify multi-step execution for a single task:

```
Task: Analyze and report
Execute: /pipe read analysis-data.csv | compute statistics | generate report
```

The pipe defines the concrete steps; the workflow skill tracks completion status.

### Pipe With Evaluation Workflows

Combine pipes with evaluation workflows to chain test steps:

```
/pipe run baseline test without skill | record results | load skill and re-run same test | record results | compare scores and identify gaps
```

The pipe sequences the evaluation steps; the evaluation framework interprets the results.

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
- **Markdown table collision**: Never start a line with `|` — this triggers markdown table rendering. Always keep pipes on a single line; use code blocks for long pipes.
