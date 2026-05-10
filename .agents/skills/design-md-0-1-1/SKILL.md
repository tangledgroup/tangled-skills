---
name: design-md-0-1-1
description: "DESIGN.md format for describing visual identity to coding agents. Combines YAML front matter design tokens (colors, typography, spacing, components) with markdown prose rationale. The `@google/design.md` npm package provides linting (8 rules including WCAG contrast checks), version diffing, and export to Tailwind theme config or W3C DTCG tokens.json. Use when creating or validating DESIGN.md files for AI agent consumption, converting design systems between formats, comparing design system versions, or injecting format specification into agent prompts."
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - design.md
  - design-tokens
  - design-system
  - cli-tool
  - google
  - linting
  - export
category: tooling
external_references:
  - https://github.com/google-labs-code/design.md/tree/0.1.1
  - https://stitch.withgoogle.com/docs/design-md/overview/
---

# DESIGN.md 0.1.1

## Overview

DESIGN.md is a plain-text format for describing a design system to coding agents. A single file combines **machine-readable design tokens** (YAML front matter) with **human-readable design rationale** (markdown prose). Tokens give agents exact values; prose tells them why those values exist and how to apply them.

The `@google/design.md` npm package provides a CLI and programmatic linter for validating, diffing, and exporting DESIGN.md files.

## When to Use

- Creating a new design system file that AI coding agents can consume
- Validating an existing DESIGN.md for structural correctness and accessibility
- Comparing two versions of a design system to detect regressions
- Converting design tokens between formats (DESIGN.md ↔ Tailwind ↔ W3C DTCG)
- Injecting the format specification into agent prompts via `npx @google/design.md spec`

## Quick Start

A minimal valid DESIGN.md:

```md
---
name: MyBrand
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  neutral: "#F7F5F2"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 3rem
  body-md:
    fontFamily: Public Sans
    fontSize: 1rem
rounded:
  sm: 4px
  md: 8px
spacing:
  sm: 8px
  md: 16px
---

## Overview

Architectural Minimalism meets Journalistic Gravitas.

## Colors

- **Primary (#1A1C1E):** Deep ink for headlines and core text.
- **Secondary (#6C7278):** Slate for borders and captions.
- **Neutral (#F7F5F2):** Warm limestone foundation.
```

Validate it:

```bash
npx @google/design.md lint DESIGN.md
```

Compare two versions:

```bash
npx @google/design.md diff DESIGN.md DESIGN-v2.md
```

Export to Tailwind theme config:

```bash
npx @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json
```

## Generate From Codebase

When asked to analyze a codebase and produce a DESIGN.md file, use the following prompt word-for-word. Feed it to the LLM along with the codebase context (files, screenshots, or a running server URL):

```
Analyze the design system of this codebase with the goal of creating a DESIGN.md file in the project root and giving the user a file for easy copy & pasting.

Reference material:
  Overview : https://stitch.withgoogle.com/docs/design-md/overview/
  Format   : https://stitch.withgoogle.com/docs/design-md/format/
  Spec     : https://github.com/google-labs-code/design.md

Examples from the spec repo:
  https://github.com/google-labs-code/design.md/blob/main/examples/atmospheric-glass/DESIGN.md
  https://github.com/google-labs-code/design.md/blob/main/examples/paws-and-paths/DESIGN.md

Requirements:
- Begin with YAML frontmatter containing all structured design tokens
  (colors, typography, spacing, elevation, motion, radii, shadows, etc.)
- Follow with free-form Markdown that describes the look & feel and
  captures design intent that token values alone cannot convey
- The file must be entirely self-contained — do not reference any
  files, variables, or paths from the codebase
- All token values must use valid YAML design token format

If you have access to a running local server or screenshots of the
product, compare your DESIGN.md against the rendered UI. Revise until
both the YAML tokens and the written description faithfully capture
the product's visual identity.
```

After generation, validate the output:

```bash
npx @google/design.md lint DESIGN.md
```

## Core Concepts

### Two-Layer Structure

1. **YAML front matter** — delimited by `---` fences at the top. Contains typed design tokens that agents parse programmatically.
2. **Markdown body** — `##` sections providing prose rationale. Agents read this for context on how to apply tokens.

The tokens are the normative values. The prose provides application guidance.

### Token Reference Syntax

Tokens can reference other tokens using `{path.to.token}` syntax:

```yaml
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.md}"
```

References resolve through the YAML tree. Unresolved references are flagged as errors by the linter.

### Section Order

Sections use `##` headings and must appear in canonical order (omitted sections are allowed):

1. Overview (alias: Brand & Style)
2. Colors
3. Typography
4. Layout (alias: Layout & Spacing)
5. Elevation & Depth (alias: Elevation)
6. Shapes
7. Components
8. Do's and Don'ts

## Advanced Topics

**Format Specification**: Token schema, types (Color, Dimension, Typography, Token References), section order with aliases, component tokens, consumer behavior for unknown content → [Format Specification](reference/01-spec-format.md)

**CLI Commands**: All four commands (`lint`, `diff`, `export`, `spec`) with flags, exit codes, and examples → [CLI Commands](reference/02-cli-commands.md)

**Linting Rules**: Eight rules covering broken references, WCAG contrast ratios, orphaned tokens, missing sections, and section ordering → [Linting Rules](reference/03-linting-rules.md)

**Export and Interoperability**: Tailwind theme config export, W3C DTCG tokens.json export, programmatic API, fixer utilities → [Export and Interoperability](reference/04-export-interop.md)
