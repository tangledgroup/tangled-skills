# Behavioral Guidelines

## Contents
- Think Before Coding
- Simplicity First
- Surgical Changes
- Goal-Driven Execution
- No Proactive Asset Generation
- No External Dependencies
- Prefer Simple References Over Tables
- Conciseness and Clarity

## Think Before Coding

- State assumptions explicitly
- Present multiple interpretations if they exist
- Push back if the request is too vague or conflicts with existing skills

## Simplicity First

- Minimum content that solves the problem
- No abstractions for single-use code
- If a simpler approach exists, use it

## Surgical Changes

- Don't modify unrelated skills when adding/updating one
- Match existing repository style
- Mention dead code in other files — don't delete it

## Goal-Driven Execution

Define success criteria before generating:
```
1. Generate SKILL.md → verify: YAML parses, name matches directory
2. Validate content → verify: all required sections present
3. Check structure → verify: reference/ numbered correctly
```

## No Proactive Asset Generation

- Never generate `scripts/` or `assets/` on your own initiative
- Only create them when the user explicitly requests them (e.g., "include scripts", "add assets")
- If you think they would be useful, suggest it to the user first and wait for confirmation

## No External Dependencies

- Never instruct installing programs (`pip install`, `npm install`, `cargo install`, `apt install`, etc.)
- Use only tools already available on the system: `bash`, `python3`, `curl`, `jq`, `pandoc`, `pdftotext`, `gs`, `grep`, `sed`, `awk`
- If the user explicitly says a program needs to be installed, then and only then, install it
- This applies even when scripts or assets are explicitly requested
- If a required tool is missing, note it rather than generating install instructions

## Prefer Simple References Over Tables

- **Do not use markdown tables unless nothing else fits better.** This is the default, not an exception.
- Reference file links must use simple text references: `[Core Concepts](reference/01-core-concepts.md)`
- Express examples, concepts, and guidance as prose, lists, or code blocks — tables are the last resort
- YAML field rules are acceptable as a table since each row is a key-value pair with no simpler alternative

## Conciseness and Clarity

- Assume the consuming agent already knows fundamentals (what PDFs are, how libraries work)
- Only add context the agent doesn't already have — challenge each paragraph's token cost
- Use consistent terminology throughout (one term per concept, never mix synonyms)
- Avoid time-sensitive information; use "old patterns" collapsible sections for legacy content
- Provide a single recommended approach with an escape hatch, not a list of alternatives
- All file paths use forward slashes (`scripts/helper.py`), never backslashes
- Keep references one level deep from SKILL.md — no chained references
