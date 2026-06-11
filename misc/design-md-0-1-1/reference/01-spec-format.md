# Format Specification

## Contents
- Token Schema
- Token Types
- Section Order and Aliases
- Component Tokens
- Consumer Behavior for Unknown Content

## Token Schema

The YAML front matter follows this schema:

```yaml
version: <string>          # optional, current version: "alpha"
name: <string>             # required
description: <string>      # optional
colors:
  <token-name>: <Color>
typography:
  <token-name>: <Typography>
rounded:
  <scale-level>: <Dimension>
spacing:
  <scale-level>: <Dimension | number>
components:
  <component-name>:
    <property-name>: <string | token reference>
```

The `<scale-level>` placeholder represents a named level in a sizing or spacing scale. Common names: `xs`, `sm`, `md`, `lg`, `xl`, `full`. Any descriptive string key is valid.

## Token Types

### Color

A hex color in sRGB color space. Must start with `#` followed by 3 or 6 hex digits.

```yaml
primary: "#1A1C1E"
secondary: "#6C7278"
```

Validation: `/^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/`

### Dimension

A number with a unit suffix. Spec-standard units: `px`, `em`, `rem`. The parser accepts all known CSS length/percentage units but only flags `px`, `em`, `rem` as spec-compliant.

```yaml
sm: 4px
md: 0.5rem
```

Validation: `/^(-?\d*\.?\d+)([a-zA-Z%]+)$/` — accepts optional leading sign and decimal (`.5rem` is valid).

### Typography

An object with the following properties:

| Property | Type | Description |
|:---------|:-----|:------------|
| `fontFamily` | string | Font family name |
| `fontSize` | Dimension | Font size with unit |
| `fontWeight` | number | Numeric weight (e.g., 400, 700). Bare number or quoted string in YAML. |
| `lineHeight` | Dimension \| number | Dimension (e.g., `24px`) or unitless multiplier (e.g., `1.6`). Unitless is recommended CSS practice. |
| `letterSpacing` | Dimension | Letter spacing with unit |
| `fontFeature` | string | Configures `font-feature-settings` CSS property |
| `fontVariation` | string | Configures `font-variation-settings` CSS property |

Example:

```yaml
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.02em
  body-md:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
```

### Token References

Wrap a path in curly braces to reference another token: `{path.to.token}`.

- For most token groups, the reference must point to a **primitive value** (e.g., `{colors.primary}`), not a group (`{colors}`).
- Within `components`, references to **composite values** are permitted (e.g., `{typography.label-md}`).
- Validation: `/^\{[a-zA-Z0-9._-]+\}$/`

## Section Order and Aliases

Sections use `##` headings. An optional `#` heading may appear for document titling but is not parsed as a section. Sections can be omitted if not relevant, but those present must follow canonical order:

| # | Canonical Name | Aliases |
|:--|:---------------|:--------|
| 1 | Overview | Brand & Style |
| 2 | Colors | — |
| 3 | Typography | — |
| 4 | Layout | Layout & Spacing |
| 5 | Elevation & Depth | Elevation |
| 6 | Shapes | — |
| 7 | Components | — |
| 8 | Do's and Don'ts | — |

### Per-Section Guidance

**Overview / Brand & Style**: Holistic description of look and feel. Defines brand personality, target audience, and emotional response (playful vs professional, dense vs spacious). Guides high-level stylistic decisions when no specific rule exists.

**Colors**: Define color palettes with semantic roles. At minimum, define `primary`. Common convention: `primary`, `secondary`, `tertiary`, `neutral`. Prose should describe each palette's purpose and usage context.

**Typography**: Define 9–15 typography levels. Common naming: semantic categories (`headline`, `display`, `body`, `label`, `caption`) subdivided by size (`small`, `medium`, `large`).

**Layout / Layout & Spacing**: Describe layout strategy (grid-based, fluid, margins/safe areas). Spacing tokens support the layout model — e.g., column spans, gutters, margins for fixed grid layouts.

**Elevation & Depth / Elevation**: How visual hierarchy is conveyed. If using elevation: define spread, blur, color. For flat designs: explain alternative methods (borders, color contrast).

**Shapes**: How visual elements are shaped — corner radius language, geometric patterns.

**Components**: Style guidance for component atoms (buttons, chips, lists, tooltips, checkboxes, radio buttons, input fields). Define additional domain-specific components as needed.

**Do's and Don'ts**: Practical guidelines and common pitfalls. Acts as guardrails when creating designs.

## Component Tokens

Components map a name to sub-token properties:

```yaml
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.md}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.secondary}"
```

### Valid Component Properties

| Property | Type |
|:---------|:-----|
| `backgroundColor` | Color |
| `textColor` | Color |
| `typography` | Typography (composite reference) |
| `rounded` | Dimension |
| `padding` | Dimension |
| `size` | Dimension |
| `height` | Dimension |
| `width` | Dimension |

### Variant Pattern

Variants (hover, active, pressed) are expressed as separate component entries with a related key name:

```yaml
components:
  button-primary:
    backgroundColor: "{colors.primary}"
  button-primary-hover:
    backgroundColor: "{colors.primary-container}"
  button-primary-active:
    backgroundColor: "{colors.primary-70}"
```

## Consumer Behavior for Unknown Content

| Scenario | Behavior | Example |
|:---------|:---------|:--------|
| Unknown section heading | Preserve; do not error | `## Iconography` |
| Unknown color token name | Accept if value is valid | `surface-container-high: '#ede7dd'` |
| Unknown typography token name | Accept as valid typography | `telemetry-data` |
| Unknown spacing value | Accept; store as string if not a valid dimension | `grid-columns: '5'` |
| Unknown component property | Accept with warning | `borderColor` |
| **Duplicate section heading** | **Error; reject the file** | Two `## Colors` headings |

## Recommended Token Names (Non-Normative)

**Colors**: `primary`, `secondary`, `tertiary`, `neutral`, `surface`, `on-surface`, `error`

**Typography**: `headline-display`, `headline-lg`, `headline-md`, `body-lg`, `body-md`, `body-sm`, `label-lg`, `label-md`, `label-sm`

**Rounded**: `none`, `sm`, `md`, `lg`, `xl`, `full`
