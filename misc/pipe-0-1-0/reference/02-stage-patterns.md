# Stage Patterns

## Contents
- Common Composition Patterns
- Anti-Patterns
- Token Budgeting
- Stage Selection Guide

## Common Composition Patterns

### Search → Scrape → Summarize

The most common web research pattern. Find information, retrieve full content, distill it.

```
| duckduckgo search for "topic" | scrapling get first result URL | summarize key findings
```

**Why it works**: Each stage reduces scope — search narrows to URLs, scrape narrows to one page, summarize narrows to key points. Token usage stays bounded.

### Read → Parse → Transform

Extract structured data from files and reformat it.

```
| read config.yaml | extract database settings | format as markdown table
```

**Why it works**: Read produces raw content, parse extracts relevant subset, transform changes representation. Each stage operates on a smaller or more focused input.

### Find → Filter → Analyze

Discovery followed by narrowing and insight extraction.

```
| bash find . -name "*.py" | filter files with "TODO" comments | group by directory and count
```

**Why it works**: Find produces a broad list, filter narrows to relevant items, analyze produces actionable output.

### Search → Compare → Recommend

Multi-source research with synthesis.

```
| duckduckgo search for "best Python ORM 2025" | scrapling get top 3 result URLs | compare features and recommend one
```

**Why it works**: Gathers multiple data points then synthesizes a recommendation. The final stage has enough context to make a meaningful comparison.

### Extract → Validate → Report

Data extraction with quality gates.

```
| read data.csv | validate all email columns are properly formatted | report any invalid entries
```

**Why it works**: Separates extraction from validation, making each step independently verifiable.

## Anti-Patterns

### Too Many Stages (6+)

```
| search | scrape | translate | summarize | format | save | notify
```

**Problem**: Each stage adds a full LLM turn. By stage 6+, context drift accumulates and token cost is high.

**Fix**: Split into two pipes or combine stages:

```
| search | scrape | translate and summarize in three bullets
```

### Unbounded Output Between Stages

```
| bash find / -type f | sort by size | ...
```

**Problem**: `find /` produces millions of results. The pipe buffer overflows, truncation loses data, subsequent stages work on incomplete input.

**Fix**: Bound the output at the source stage:

```
| bash find . -type f -maxdepth 3 | sort by size descending, top 50 | ...
```

### Ambiguous Stage Instructions

```
| do something with the data
```

**Problem**: "Do something" gives no actionable direction. The agent guesses and likely produces unhelpful output for the next stage.

**Fix**: Be specific about the operation:

```
| extract all email addresses from the data
```

### Mixing Concerns in One Stage

```
| read the file, search for errors, fix them, and write a report
```

**Problem**: Four operations crammed into one stage defeats the purpose of pipes. Each step's output is invisible, making debugging impossible.

**Fix**: Split into separate stages:

```
| read src/main.py | find all error handling gaps | generate fixes for each gap | write a summary report
```

### Circular Dependencies

```
| summarize the document | expand the summary back to full text
```

**Problem**: Stage 2 tries to reconstruct what Stage 1 destroyed. Information loss is irreversible.

**Fix**: Ensure each stage moves toward the goal, not backward. If you need both summary and detail, use separate pipes.

## Token Budgeting

### Estimating Cost Per Stage

Each pipe stage costs approximately one LLM turn (input + output). Rough estimates:

| Stage Type | Input Tokens | Output Tokens | Total Estimate |
|------------|-------------|---------------|----------------|
| Tool invocation (bash, read) | ~100 | varies by output | 100–5000+ |
| Skill execution | ~500 (skill context) + instruction | varies | 500–10000+ |
| Raw instruction | pipe buffer + instruction | ~200–800 | buffer-dependent |

### Budgeting Rules

1. **Keep pipes to 3-4 stages** for reliable results under typical context windows
2. **Bound output at each stage** — use "top N", "first X", or explicit truncation in stage instructions
3. **Prefer tools over raw instructions** for deterministic stages (bash, read) — they produce predictable output sizes
4. **Put reduction stages early** if the initial output is large — summarize before you need to work with the content
5. **Avoid "read entire large file" as Stage 1** unless subsequent stages explicitly handle large input

### When to Split Into Multiple Pipes

Split a long pipe into multiple shorter pipes when:

- You have more than 4 stages
- An intermediate result needs human review before continuing
- Different stages require different skills that shouldn't share context
- The total estimated token budget exceeds your context window comfortably

```
# Instead of one 6-stage pipe, use two 3-stage pipes:
| search for "topic A" | scrape top result | extract URLs

# Then continue with the extracted URLs as explicit input:
| read the extracted URLs from previous step | scrape each URL | compare content
```

## Stage Selection Guide

### Use a Skill When

- The operation requires domain-specific knowledge (web scraping, search, NLP)
- The skill provides optimized defaults and best practices
- You need structured output that the skill guarantees

### Use a Tool When

- The operation is deterministic and fast (file read, grep, find)
- You need exact control over arguments and flags
- The tool produces predictable, bounded output

### Use a Raw Instruction When

- The operation is a general reasoning task (summarize, compare, recommend)
- No specific skill or tool matches the operation
- You want the agent's native capabilities to handle the transformation

### Use an MCP Tool When

- The operation requires external service integration (memory search, database query)
- The MCP tool provides specialized functionality not available as a skill
