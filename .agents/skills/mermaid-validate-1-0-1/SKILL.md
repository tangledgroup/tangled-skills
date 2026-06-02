---
name: mermaid-validate-1-0-1
description: Lightweight Mermaid diagram syntax validator using the official mermaid parser with jsdom. Validates diagrams in markdown files, standalone .mmd files, directories, and stdin with JSON output support. Use when checking Mermaid diagram syntax for correctness before rendering, validating documentation containing Mermaid charts, or integrating diagram validation into CI/CD pipelines.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.3.0"
tags:
  - mermaid
  - validator
  - diagram
  - syntax-checking
  - bun
  - cli-tool
  - markdown
category: cli-tool
external_references:
  - https://www.npmjs.com/package/@zabaca/mermaid-validate/v/1.0.1
  - https://github.com/Zabaca/mermaid-validate/tree/v1.0.1
---

# mermaid-validate 1.0.1

## Overview

`@zabaca/mermaid-validate` is a lightweight Mermaid diagram syntax validator that uses the official `mermaid` parser with `jsdom` for minimal DOM simulation. It validates diagram syntax accurately without requiring a full browser or puppeteer setup.

Use the wrapper script which handles runner detection (`bun x` preferred, `npx -y` fallback) and fixes the upstream tool's broken directory mode:

```bash
bash scripts/mermaid-validate.sh <file|directory|->
```

## When to Use

- Validating Mermaid diagrams embedded in markdown documentation before publishing
- Adding diagram syntax checks to CI/CD pipelines or pre-commit hooks
- Checking standalone `.mmd` files for syntax errors
- Batch-validating all diagrams across a project's documentation directory

## Core Concepts

### Exit Codes

- `0` — All diagrams valid (or no mermaid blocks found)
- `1` — One or more diagrams have syntax errors
- `2` — Usage error (no input, missing file, unknown option)

### Supported Inputs

| Input | Description |
|-------|-------------|
| `<file>` | Single `.md`, `.mmd`, `.markdown`, or `.mdx` file |
| `<directory>` | Recursively validates all matching files in the directory |
| `-` | Reads diagram code from stdin |

### Supported Diagram Types

All diagram types supported by mermaid: flowchart/graph, sequence, class, state, entity relationship, gantt, pie chart, and others.

### CLI Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show usage help |
| `-q, --quiet` | Only output errors (suppress valid file markers) |
| `--json` | Output results as JSON |

## Usage Examples

### Validate a single markdown file

```bash
bash scripts/mermaid-validate.sh README.md
```

Output for valid diagrams:
```
✓ README.md:block1
✓ README.md:block2

Summary: 2 valid, 0 invalid
```

Output for invalid diagrams:
```
✗ README.md:block1 (line 15)
  Parse error on line 1:
  ...

Summary: 1 valid, 1 invalid
```

### Validate a standalone .mmd file

```bash
bash scripts/mermaid-validate.sh diagram.mmd
```

### Validate all files in a directory

```bash
bash scripts/mermaid-validate.sh docs/
```

### Validate from stdin

```bash
echo "graph TD; A-->B" | bash scripts/mermaid-validate.sh -
```

### JSON output (for CI integration)

```bash
bash scripts/mermaid-validate.sh --json README.md
```

Output:
```json
{
  "totalValid": 2,
  "totalInvalid": 0,
  "results": [
    { "file": "README.md:block1", "valid": true },
    { "file": "README.md:block2", "valid": true }
  ]
}
```

### Quiet mode (only errors)

```bash
bash scripts/mermaid-validate.sh -q docs/
```

### CI/CD integration

Use the exit code to fail pipeline runs when diagrams are invalid:

```bash
bash scripts/mermaid-validate.sh --json docs/
```

Exit code `0` passes, `1` fails — no additional tooling needed.

## Programmatic API

Import from `@zabaca/mermaid-validate` in a TypeScript or JavaScript project:

```typescript
import { validateDiagram, validateFile, extractMermaidBlocks } from "@zabaca/mermaid-validate";

// Validate a single diagram string
const result = await validateDiagram(`graph TD
    A[Start] --> B[End]`);
// { valid: true }

// Validate all mermaid blocks in a markdown file
const fileResult = await validateFile("docs/architecture.md");
// { filePath: "...", blocks: [...], totalBlocks: 2, validBlocks: 2, invalidBlocks: 0 }

// Extract mermaid code blocks from raw markdown content
const blocks = extractMermaidBlocks(markdownContent);
// [{ code: "graph TD...", startLine: 10 }, ...]
```
