# ☑ Plan: Generate design-md-0-1-1 Skill

**Depends On:** NONE
**Created:** 2026-05-04T00:00:00Z
**Updated:** 2026-05-04T00:02:00Z
**Current Phase:** ☑ Phase 7
**Current Task:** ☑ Task 7.3

## Source Analysis Summary

Crawled and analyzed all sources for `design.md` v0.1.1:

- **GitHub repo** (`google-labs-code/design.md@0.1.1`): README, docs/spec.md, packages/cli source (index.ts, commands/lint/diff/export/spec.ts, linter rules, model types, spec-config.yaml), 3 example DESIGN.md files
- **Stitch docs** (`stitch.withgoogle.com/docs/design-md/`): SPA-rendered, empty via jina-ai-reader — all content obtained from GitHub sources instead
- **npm package**: `@google/design.md` v0.1.1

### Key findings:
- DESIGN.md = YAML front matter (machine-readable design tokens) + markdown body (human-readable rationale)
- CLI: 4 commands — `lint`, `diff`, `export`, `spec`
- Linter: 8 rules with fixed severities (error/warning/info)
- Export formats: Tailwind theme config, DTCG (W3C Design Tokens Format)
- Token types: Color (#hex), Dimension (px/em/rem), Typography (object), Token References ({path.to.token})
- Section order: 8 canonical sections with aliases
- Component tokens: 8 valid sub-properties, variants as separate entries
- Programmatic API: `lint()` function returning findings + designSystem state
- Fixer: `fixSectionOrder()` for reordering markdown sections
- Status: alpha version

### Skill structure decision: **Complex** (SKILL.md + reference/)

This covers 4+ distinct domains that an agent would load selectively:
1. Format specification (token schema, section order, types)
2. CLI commands (lint/diff/export/spec usage)
3. Linting rules (8 rules with semantics and fixes)
4. Export/interoperability (Tailwind, DTCG, programmatic API)

---

## ☑ Phase 1 Research and Analysis

- ☑ Task 1.1 Crawl all source URLs and GitHub repo
  - Read README.md from raw GitHub
  - Read docs/spec.md from raw GitHub
  - Read packages/cli/package.json for CLI metadata
  - Read CLI command sources (lint, diff, export, spec)
  - Read linter rule implementations (8 rules)
  - Read model types and spec config
  - Read example DESIGN.md files (3 examples)
  - Read exporter implementations (Tailwind, DTCG)
  - Read fixer implementation

- ☑ Task 1.2 Determine skill structure (simple vs complex)
  - Decision: Complex — 4+ distinct domains
  - Reference files: spec format, CLI commands, linting rules, export/interop

- ☑ Task 1.3 Map content to reference files
  - `reference/01-spec-format.md` — Token schema, types, section order, consumer behavior
  - `reference/02-cli-commands.md` — All 4 CLI commands with flags and examples
  - `reference/03-linting-rules.md` — 8 rules with semantics, severities, fix guidance
  - `reference/04-export-interop.md` — Tailwind/DTCG export, programmatic API, fixer

## ☑ Phase 2 Write SKILL.md

- ☑ Task 2.1 Draft YAML header (depends on: Task 1.2)
  - name: design-md-0-1-1
  - description: covers WHAT (DESIGN.md format spec + CLI toolkit) and WHEN (creating/linting/converting design system files for AI agents)
  - version: "0.1.1"
  - tags: design.md, design-tokens, design-system, cli-tool, google, linting, export
  - category: tooling

- ☑ Task 2.2 Draft Overview section (depends on: Task 1.3)
  - What DESIGN.md is: YAML tokens + markdown prose for AI agents
  - Two-layer structure explanation
  - Quick example

- ☑ Task 2.3 Draft When to Use section (depends on: Task 1.3)
  - Creating new design systems for AI agent consumption
  - Validating existing DESIGN.md files
  - Converting between formats (DESIGN.md ↔ Tailwind ↔ DTCG)
  - Comparing design system versions

- ☑ Task 2.4 Draft Quick Start section (depends on: Task 1.3)
  - Minimal valid DESIGN.md example
  - CLI lint command
  - Token reference syntax

- ☑ Task 2.5 Draft Advanced Topics navigation hub (depends on: Task 1.3, Task 2.4)
  - Links to all 4 reference files with one-line descriptions

## ☑ Phase 3 Write reference/01-spec-format.md

- ☑ Task 3.1 Token schema and types (depends on: Task 1.1)
  - Color (#hex, sRGB), Dimension (px/em/rem), Typography object properties
  - Token references ({path.to.token}) with resolution rules
  - Full YAML schema with optional/required fields

- ☑ Task 3.2 Section order and aliases (depends on: Task 1.1)
  - 8 canonical sections in order with aliases
  - Per-section guidance (what each section covers, prose examples)

- ☑ Task 3.3 Component tokens (depends on: Task 1.1)
  - 8 valid sub-properties with types
  - Variant pattern (button-primary, button-primary-hover)
  - Token reference resolution in components

- ☑ Task 3.4 Consumer behavior for unknown content (depends on: Task 1.1)
  - Table of scenarios and behaviors
  - Duplicate section = error rule

## ☑ Phase 4 Write reference/02-cli-commands.md

- ☑ Task 4.1 Installation and setup (depends on: Task 1.1)
  - npm install @google/design.md
  - npx usage for one-off runs
  - All commands accept file path or `-` for stdin

- ☑ Task 4.2 lint command (depends on: Task 1.1)
  - Usage, flags, exit codes, JSON output format
  - Example input/output

- ☑ Task 4.3 diff command (depends on: Task 1.1)
  - Compare two DESIGN.md files
  - Token-level changes + regression detection
  - Exit code behavior

- ☑ Task 4.4 export command (depends on: Task 1.1)
  - --format tailwind | dtcg
  - Output format descriptions

- ☑ Task 4.5 spec command (depends on: Task 1.1)
  - Output format specification for agent prompt injection
  - --rules, --rules-only flags

## ☑ Phase 5 Write reference/03-linting-rules.md

- ☑ Task 5.1 Rule overview table (depends on: Task 1.1)
  - All 8 rules with name, severity, description

- ☑ Task 5.2 Error-severity rules (depends on: Task 1.1)
  - broken-ref: unresolved references + unknown component sub-tokens

- ☑ Task 5.3 Warning-severity rules (depends on: Task 1.1)
  - missing-primary, contrast-ratio (WCAG AA 4.5:1), orphaned-tokens
  - missing-typography, section-order

- ☑ Task 5.4 Info-severity rules (depends on: Task 1.1)
  - token-summary, missing-sections

- ☑ Task 5.5 Programmatic linter API (depends on: Task 1.1)
  - import { lint } from '@google/design.md/linter'
  - Report structure (findings, summary, designSystem)
  - Individual rule exports for selective composition
  - fixSectionOrder fixer

## ☑ Phase 6 Write reference/04-export-interop.md

- ☑ Task 6.1 Tailwind export (depends on: Task 1.1)
  - Maps to theme.extend config structure
  - Colors, fontFamily, fontSize, borderRadius, spacing mappings
  - Example output

- ☑ Task 6.2 DTCG export (depends on: Task 1.1)
  - W3C Design Tokens Format Module compliance
  - $schema, $type, $value structure
  - Color (srgb components + hex), dimension, typography mappings

- ☑ Task 6.3 Design token interoperability patterns (depends on: Task 1.1)
  - Converting from/to Figma variables, tokens.json
  - Cross-format reference syntax compatibility

## ☑ Phase 7 Validate and Finalize

- ☑ Task 7.1 Run validation checklist (depends on: Task 2.5 , Task 3.4 , Task 4.5 , Task 5.5 , Task 6.3)
  - YAML header checks (name, description, version, structure)
  - Structure checks (directory name, SKILL.md exists, reference/ numbered files)
  - Content checks (Overview, When to Use, no hallucinations, conciseness)
  - Cross-reference integrity (all links resolve)

- ☑ Task 7.2 Verify line counts and token efficiency (depends on: Task 7.1)
  - SKILL.md under 500 lines
  - No chained references
  - Description within 150-400 char target

- ☑ Task 7.3 Regenerate README skills table (depends on: Task 7.2)
  - Run python3 misc/gen-skills-table.py
