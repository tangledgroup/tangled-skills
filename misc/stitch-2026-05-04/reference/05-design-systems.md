# Design Systems

## Contents
- DESIGN.md Format
- Token Types
- Component Tokens
- SDK Design System API
- Extracting Design DNA
- Linting and Validation

## DESIGN.md Format

DESIGN.md is Stitch's agent-readable design system format. It combines machine-readable design tokens (YAML front matter) with human-readable design rationale (markdown prose).

```yaml
---
name: MyBrand
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
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
```

The tokens are the normative values. The prose provides context for how to apply them. An agent reading this file produces UI with deep ink headlines in Public Sans, a warm limestone background, and Boston Clay call-to-action buttons.

DESIGN.md is open-source (version `alpha`). Full spec: `google-labs-code/design.md` on GitHub. A separate skill (`design-md-0-1-1`) covers the full specification including linting rules and export formats.

## Token Types

| Type | Format | Example |
|------|--------|---------|
| Color | `#` + hex (sRGB) | `"#1A1C1E"` |
| Dimension | number + unit (`px`, `em`, `rem`) | `48px`, `-0.02em` |
| Token Reference | `{path.to.token}` | `{colors.primary}` |
| Typography | object with `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing` | See example above |

## Component Tokens

Components map a name to sub-token properties:

```yaml
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.sm}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.tertiary-container}"
```

Valid component properties: `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`.

Variants (hover, active, pressed) are expressed as separate component entries with related key names.

## SDK Design System API

Create and manage design systems programmatically:

```ts
import { stitch } from "@google/stitch-sdk";

const project = stitch.project("project-id");

// Create a design system
const ds = await project.createDesignSystem({
  colors: { primary: "#1A1C1E", accent: "#B8422E" },
  typography: { body: { fontFamily: "Public Sans", fontSize: "1rem" } },
});

// Apply to screens
const applied = await ds.apply([
  { id: "screen-instance-1", sourceScreen: "screen-id-1" },
  { id: "screen-instance-2", sourceScreen: "screen-id-2" },
]);

// Update
await ds.update({ colors: { primary: "#0D0F10" } });

// List existing design systems
const systems = await project.listDesignSystems();
```

## Extracting Design DNA

Use `extract_design_context` (via MCP tool) to capture the visual identity of an existing screen:

```
Tool: extract_design_context
Input: { projectId: "...", screenId: "..." }
Output: Color palettes, typography, layout patterns
```

This extracted context can be passed when generating new screens to maintain consistency. The `stitch-design` skill from `stitch-skills` automates this workflow.

## Cross-Project Consistency

DESIGN.md files are portable between Stitch projects and other tools:

1. Export DESIGN.md from one project
2. Import into another Stitch project
3. Or use with coding agents via the `design-md` skill
4. Export to Tailwind config or W3C DTCG tokens for implementation

## Linting and Validation

The `@google/design.md` CLI validates DESIGN.md files:

```bash
# Validate structure
npx @google/design.md lint DESIGN.md

# Compare versions
npx @google/design.md diff DESIGN.md DESIGN-v2.md

# Export to Tailwind
npx @google/design.md export --format json-tailwind DESIGN.md > tailwind.theme.json
```

Linting rules check for broken token references, WCAG contrast ratios, missing sections, and orphaned tokens. See the `design-md-0-1-1` skill for full linting rules reference.
