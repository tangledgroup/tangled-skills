# CLI Commands

## Contents
- Installation
- lint Command
- diff Command
- export Command
- spec Command

## Installation

```bash
npm install @google/design.md
```

Or run directly without installation:

```bash
npx @google/design.md lint DESIGN.md
```

All commands accept a file path or `-` for stdin. Output defaults to JSON.

Package details:
- **Name**: `@google/design.md`
- **Version**: 0.1.1
- **Bin**: `design.md` (also aliased as `designmd` for Windows shell compatibility)
- **Type**: ESM module
- **Engine**: Node.js >= 18

## lint Command

Validate a DESIGN.md file for structural correctness.

```bash
npx @google/design.md lint DESIGN.md
npx @google/design.md lint --format json DESIGN.md
cat DESIGN.md | npx @google/design.md lint -
```

### Arguments

| Option | Type | Default | Description |
|:-------|:-----|:--------|:------------|
| `file` | positional | required | Path to DESIGN.md (or `-` for stdin) |
| `--format` | string | `json` | Output format (`json` or `text`) |

### Exit Codes

- `0` — no errors found
- `1` — errors found

### Output Format

```json
{
  "findings": [
    {
      "severity": "warning",
      "path": "components.button-primary",
      "message": "textColor (#ffffff) on backgroundColor (#1A1C1E) has contrast ratio 15.42:1 — passes WCAG AA."
    }
  ],
  "summary": { "errors": 0, "warnings": 1, "info": 1 }
}
```

Each finding has:
- `severity`: `"error"`, `"warning"`, or `"info"`
- `path`: optional dot-separated token path (e.g., `colors.primary`)
- `message`: human-readable description

## diff Command

Compare two DESIGN.md files and report token-level changes.

```bash
npx @google/design.md diff DESIGN.md DESIGN-v2.md
```

### Arguments

| Option | Type | Default | Description |
|:-------|:-----|:--------|:------------|
| `before` | positional | required | Path to the "before" DESIGN.md |
| `after` | positional | required | Path to the "after" DESIGN.md |
| `--format` | string | `json` | Output format (`json` or `text`) |

### Exit Codes

- `0` — no regression detected
- `1` — regression detected (more errors or warnings in the "after" file)

### Output Format

```json
{
  "tokens": {
    "colors": { "added": ["accent"], "removed": [], "modified": ["tertiary"] },
    "typography": { "added": [], "removed": [], "modified": [] },
    "rounded": { "added": [], "removed": [], "modified": [] },
    "spacing": { "added": [], "removed": [], "modified": [] }
  },
  "findings": {
    "before": { "errors": 0, "warnings": 1, "info": 1 },
    "after": { "errors": 0, "warnings": 2, "info": 1 },
    "delta": { "errors": 0, "warnings": 1 }
  },
  "regression": false
}
```

The diff compares both token values and lint findings. A regression occurs when the "after" file has more errors or warnings than the "before" file.

## export Command

Export DESIGN.md tokens to other formats.

```bash
npx @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json
npx @google/design.md export --format dtcg DESIGN.md > tokens.json
```

### Arguments

| Option | Type | Default | Description |
|:-------|:-----|:--------|:------------|
| `file` | positional | required | Path to DESIGN.md (or `-` for stdin) |
| `--format` | string | required | Output format: `tailwind` or `dtcg` |

### Supported Formats

- **`tailwind`** — Tailwind CSS `theme.extend` config with colors, fontFamily, fontSize, borderRadius, and spacing.
- **`dtcg`** — W3C Design Tokens Format Module (2025.10) compliant `tokens.json` with `$schema`, `$type`, `$value` structure.

### Exit Codes

- `0` — export succeeded with no lint errors
- `1` — invalid format argument or lint errors in source file

## spec Command

Output the DESIGN.md format specification, useful for injecting spec context into agent prompts.

```bash
npx @google/design.md spec
npx @google/design.md spec --rules
npx @google/design.md spec --rules-only --format json
```

### Arguments

| Option | Type | Default | Description |
|:-------|:-----|:--------|:------------|
| `--rules` | boolean | `false` | Append the active linting rules table |
| `--rules-only` | boolean | `false` | Output only the linting rules table |
| `--format` | string | `markdown` | Output format: `markdown` or `json` |

### Usage Patterns

- **Full spec**: `npx @google/design.md spec` — outputs the complete format specification in markdown
- **Spec with rules**: `npx @google/design.md spec --rules` — appends the active linting rules table
- **Rules only (markdown)**: `npx @google/design.md spec --rules-only` — outputs just the rules table
- **Rules only (JSON)**: `npx @google/design.md spec --rules-only --format json` — structured rules for programmatic use

### JSON Output Format (rules-only)

```json
{
  "rules": [
    {
      "name": "broken-ref",
      "severity": "error",
      "description": "Broken/circular references and unknown component sub-tokens."
    },
    {
      "name": "contrast-ratio",
      "severity": "warning",
      "description": "WCAG contrast ratio — warns when component backgroundColor/textColor pairs fall below the AA minimum of 4.5:1."
    }
  ]
}
```
