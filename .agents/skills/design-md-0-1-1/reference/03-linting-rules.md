# Linting Rules

## Contents
- Rule Overview
- Error-Severity Rules
- Warning-Severity Rules
- Info-Severity Rules
- Programmatic API

## Rule Overview

The linter runs eight rules against a parsed DESIGN.md. Each rule produces findings at a fixed severity level. Rules execute in the order listed below.

| Rule | Severity | What it checks |
|:-----|:---------|:---------------|
| `broken-ref` | error | Token references that don't resolve; unknown component sub-tokens |
| `missing-primary` | warning | Colors defined but no `primary` color exists |
| `contrast-ratio` | warning | Component bg/text pairs below WCAG AA minimum (4.5:1) |
| `orphaned-tokens` | warning | Color tokens defined but never referenced by any component |
| `token-summary` | info | Summary count of tokens in each section |
| `missing-sections` | info | Optional sections (spacing, rounded) absent when other tokens exist |
| `missing-typography` | warning | Colors defined but no typography tokens exist |
| `section-order` | warning | Sections appear out of canonical order |

## Error-Severity Rules

### broken-ref

**Severity**: error

Checks for two conditions:

1. **Unresolved token references**: A component property references `{path.to.token}` that doesn't resolve to any defined token in the YAML tree.

   Example finding:
   ```
   path: components.button-primary
   message: Reference {colors.accent} does not resolve to any defined token.
   ```

2. **Unknown component sub-tokens**: A component property name is not in the valid set (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`). These emit a **warning** severity override (not error) within this rule.

   Example finding:
   ```
   path: components.card.border
   message: 'border' is not a recognized component sub-token. Valid sub-tokens: backgroundColor, textColor, typography, rounded, padding, size, height, width.
   ```

**Fix**: Ensure all `{...}` references point to existing tokens. Use valid component property names or accept the warning for custom properties.

## Warning-Severity Rules

### missing-primary

**Severity**: warning

Triggers when `colors` section has entries but no token named `primary` exists. Without a primary color, agents auto-generate key colors, reducing author control over the palette.

```
path: colors
message: No 'primary' color defined. The agent will auto-generate key colors, reducing your control over the palette.
```

**Fix**: Add a `primary` color token to the colors section.

### contrast-ratio

**Severity**: warning

Checks component `backgroundColor`/`textColor` pairs against WCAG AA minimum contrast ratio of **4.5:1**. Uses relative luminance calculation per WCAG 2.0.

```
path: components.button-primary
message: textColor (#333333) on backgroundColor (#1A1C1E) has contrast ratio 3.82:1, below WCAG AA minimum of 4.5:1.
```

**Fix**: Adjust color values to achieve at least 4.5:1 contrast ratio. Lighter text on dark backgrounds or vice versa.

### orphaned-tokens

**Severity**: warning

Identifies color tokens defined in the YAML but never referenced by any component's properties. Only runs when components are defined (no false positives on token-only files).

```
path: colors.accent
message: 'accent' is defined but never referenced by any component.
```

**Fix**: Either use the token in a component definition or remove it if unused.

### missing-typography

**Severity**: warning

Triggers when `colors` are defined but no `typography` tokens exist. Without typography tokens, agents use default font choices, reducing control over typographic identity.

```
path: typography
message: No typography tokens defined. Agents will use default font choices, reducing your control over the design system's typographic identity.
```

**Fix**: Add at least one typography token with `fontFamily` and `fontSize`.

### section-order

**Severity**: warning

Checks that `##` section headings appear in canonical order: Overview → Colors → Typography → Layout → Elevation & Depth → Shapes → Components → Do's and Don'ts. Resolves aliases (e.g., "Brand & Style" → "Overview").

```
message: Section 'Typography' appears before 'Colors', which is out of order. Expected order: Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts
```

**Fix**: Reorder sections to match canonical order. The fixer utility can auto-reorder (see Programmatic API below).

## Info-Severity Rules

### token-summary

**Severity**: info

Emits a single finding summarizing how many tokens are defined in each section:

```
message: Design system defines 4 colors, 3 typography scales, 2 rounding levels, 5 spacing tokens, 4 components.
```

No fix needed — informational only.

### missing-sections

**Severity**: info

Notes when optional sections (`spacing`, `rounded`) are absent while other tokens (colors) exist. These sections help agents make consistent design decisions.

```
path: spacing
message: No 'spacing' section defined. Layout spacing will fall back to agent defaults.
```

**Fix**: Add `spacing` and/or `rounded` sections if you want explicit control over these values.

## Programmatic API

The linter is available as a library for custom tooling:

```typescript
import { lint } from '@google/design.md/linter';

const report = lint(markdownString);

console.log(report.findings);       // Finding[] — all findings from all rules
console.log(report.summary);        // { errors, warnings, info }
console.log(report.designSystem);   // Parsed DesignSystemState
```

### Report Structure

- **`findings`**: Array of `{ severity, path?, message }` objects
- **`summary`**: `{ errors: number, warnings: number, info: number }`
- **`designSystem`**: Parsed state with resolved tokens:
  - `colors`: Map of name → ResolvedColor (hex, r, g, b, luminance)
  - `typography`: Map of name → ResolvedTypography
  - `rounded`: Map of name → ResolvedDimension
  - `spacing`: Map of name → ResolvedDimension
  - `components`: Map of name → ComponentDef (properties, unresolvedRefs)
  - `symbolTable`: Flat lookup `"colors.primary"` → ResolvedValue

### Selective Rule Composition

Individual rules are exported for custom rule sets:

```typescript
import {
  brokenRef,
  contrastCheck,
  orphanedTokens,
} from '@google/design.md/linter';

// Run only specific rules
const findings = [
  ...brokenRef(state),
  ...contrastCheck(state),
  ...orphanedTokens(state),
];
```

All exports: `brokenRef`, `missingPrimary`, `contrastCheck`, `orphanedTokens`, `tokenSummary`, `missingSections`, `missingTypography`, `sectionOrder`.

### Fixer Utility

Auto-reorder sections to canonical order:

```typescript
import { fixSectionOrder } from '@google/design.md/linter';

const result = fixSectionOrder({
  sections: [
    { heading: 'Typography', content: '...' },
    { heading: 'Colors', content: '...' },
  ],
});

console.log(result.fixedContent);   // Reordered markdown
console.log(result.details.beforeOrder); // ['Typography', 'Colors']
console.log(result.details.afterOrder);  // ['Colors', 'Typography']
```

### Utility Functions

```typescript
import { contrastRatio } from '@google/design.md/linter';

// Calculate WCAG contrast ratio between two resolved colors
const ratio = contrastRatio(bgColor, textColor); // e.g., 4.52
```
