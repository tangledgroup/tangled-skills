# Export and Interoperability

## Contents
- Tailwind Theme Export
- W3C DTCG Export
- Programmatic Emitters
- Design Token Conversion Patterns

## Tailwind Theme Export

Convert DESIGN.md tokens to a Tailwind CSS `theme.extend` configuration.

```bash
npx @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json
```

### Output Structure

```json
{
  "theme": {
    "extend": {
      "colors": {
        "primary": "#1A1C1E",
        "secondary": "#6C7278",
        "neutral": "#F7F5F2"
      },
      "fontFamily": {
        "h1": ["Public Sans"],
        "body-md": ["Public Sans"]
      },
      "fontSize": {
        "h1": ["3rem", { "lineHeight": "1.1", "fontWeight": "600", "letterSpacing": "-0.02em" }],
        "body-md": ["1rem", { "lineHeight": "1.6", "fontWeight": "400" }]
      },
      "borderRadius": {
        "sm": "4px",
        "md": "8px"
      },
      "spacing": {
        "sm": "8px",
        "md": "16px"
      }
    }
  }
}
```

### Mapping Rules

| DESIGN.md Token | Tailwind Target | Notes |
|:----------------|:----------------|:------|
| `colors.*` | `theme.extend.colors` | Direct hex mapping |
| `typography.*.fontFamily` | `theme.extend.fontFamily` | Array-wrapped family name |
| `typography.*.fontSize` + meta | `theme.extend.fontSize` | Tuple of `[size, {lineHeight, fontWeight, letterSpacing}]` |
| `rounded.*` | `theme.extend.borderRadius` | Direct dimension mapping |
| `spacing.*` | `theme.extend.spacing` | Direct dimension mapping |

Typography properties without `fontSize` are skipped in the fontSize map but included in fontFamily.

## W3C DTCG Export

Export to [W3C Design Tokens Format Module](https://tr.designtokens.org/format/) (2025.10 schema).

```bash
npx @google/design.md export --format dtcg DESIGN.md > tokens.json
```

### Output Structure

```json
{
  "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
  "$description": "MyBrand Design System",
  "color": {
    "$type": "color",
    "primary": {
      "$value": {
        "colorSpace": "srgb",
        "components": [0.102, 0.110, 0.118],
        "hex": "#1a1c1e"
      }
    }
  },
  "spacing": {
    "$type": "dimension",
    "sm": { "$value": { "value": 8, "unit": "px" } },
    "md": { "$value": { "value": 16, "unit": "px" } }
  },
  "rounded": {
    "$type": "dimension",
    "sm": { "$value": { "value": 4, "unit": "px" } }
  },
  "typography": {
    "h1": {
      "$type": "typography",
      "$value": {
        "fontFamily": "Public Sans",
        "fontSize": { "value": 48, "unit": "px" },
        "fontWeight": 600,
        "lineHeight": { "value": 1.1, "unit": "" },
        "letterSpacing": { "value": -0.02, "unit": "em" }
      }
    }
  }
}
```

### Mapping Rules

| DESIGN.md Type | DTCG Structure | Notes |
|:---------------|:---------------|:------|
| Color | `$type: "color"`, value has `colorSpace: "srgb"`, `components[]` (0-1), `hex` | RGB normalized to 0-1 range, rounded to 3 decimals |
| Dimension | `$type: "dimension"`, value has `value` (number) and `unit` (string) | Direct numeric + unit split |
| Typography | `$type: "typography"`, value is object with font properties | Each sub-property mapped individually; lineHeight as dimension or number |

Empty groups are omitted from output (no empty `"color": {}`).

## Programmatic Emitters

Both exporters are available as classes for custom pipelines:

```typescript
import {
  lint,
  TailwindEmitterHandler,
  DtcgEmitterHandler,
} from '@google/design.md/linter';

const report = lint(markdownString);

// Tailwind
const twEmitter = new TailwindEmitterHandler();
const twResult = twEmitter.execute(report.designSystem);
console.log(JSON.stringify(twResult.data, null, 2));

// DTCG
const dtcgEmitter = new DtcgEmitterHandler();
const dtcgResult = dtcgEmitter.execute(report.designSystem);
console.log(JSON.stringify(dtcgResult.data, null, 2));
```

Both emitters return `{ success: boolean, data: object }`. On failure, `data` contains an error message.

## Design Token Conversion Patterns

### From DESIGN.md to Figma Variables

DESIGN.md tokens map directly to Figma variables:
- **Color tokens** → Figma Color Collection variables
- **Dimension tokens** → Figma Number/Spacing variables
- Use the DTCG export as an intermediate format — many Figma plugins accept `tokens.json`

### From Figma to DESIGN.md

1. Export Figma variables as `tokens.json` (DTCG format)
2. Manually create YAML front matter from the token groups
3. Write markdown prose sections describing usage rationale
4. Validate with `npx @google/design.md lint DESIGN.md`

### Cross-Format Reference Syntax

DESIGN.md uses `{path.to.token}` for internal references. When converting to other formats:
- **Tailwind**: References become CSS variable names or direct values
- **DTCG**: Use `$type: "reference"` with `$value` as the path string
- The exporter resolves all references before output, so exported files contain concrete values
