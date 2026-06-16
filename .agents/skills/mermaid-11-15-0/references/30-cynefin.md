# Cynefin Framework Diagram (v11.15.0+)

The Cynefin framework categorizes problems into five complexity domains. Use `cynefin-beta` to render a wavy-boundary diagram with item badges per domain and optional transitions between them.

## Syntax

Declare with `cynefin-beta`, optionally add a `title`, then list items under each domain keyword.

```
cynefin-beta
  title Incident Response

  complex
    "Investigate root cause"
    "Run chaos experiment"

  complicated
    "Analyze performance data"

  clear
    "Restart service"

  chaotic
    "Page on-call immediately"

  confusion
    "Unknown failure mode"
```

### Domain keywords

| Keyword     | Domain         | Position        |
|-------------|----------------|-----------------|
| `complex`   | Complex        | Top-left        |
| `complicated` | Complicated  | Top-right       |
| `clear`     | Clear          | Bottom-right    |
| `chaotic`   | Chaotic        | Bottom-left     |
| `confusion` | Confusion      | Center ellipse  |

Domains render in fixed positions regardless of declaration order. Empty domains (keyword with no items) still render as regions.

### Items

Quoted string labels on their own lines inside a domain block. Keep lists short — the confusion ellipse caps at 3 items and shows `+N more` for overflow.

```
complex
  "Investigate root cause"
  "Run chaos experiment"
```

### Transitions

Use `-->` between two domain names with optional labels to show movement between domains.

```
complex --> complicated : "Pattern identified"
clear --> chaotic : "Complacency"
chaotic --> complex : "Stabilized"
```

Self-loop transitions (e.g., `complex --> complex`) are silently ignored.

## Configuration

Under the `cynefin` config key:

| Option                   | Type    | Default  | Description                                          |
|--------------------------|---------|----------|------------------------------------------------------|
| `width`                  | number  | `800`    | Diagram width in pixels                              |
| `height`                 | number  | `600`    | Diagram height in pixels                             |
| `padding`                | number  | `40`     | Padding around the diagram                           |
| `showDomainDescriptions` | boolean | `true`   | Show decision model and practice subtitles per domain |
| `boundaryAmplitude`      | number  | `8`      | Waviness amplitude (set `0` for straight lines)       |
| `seed`                   | number  | `0`      | Deterministic seed for waviness (`0` = auto-hash)     |

```
%%{init: {'cynefin': {'width': 1000, 'showDomainDescriptions': false}}}%%
cynefin-beta
  complex
    "Adaptive work"
```

## Theme variables

Override via `themeVariables.cynefin`:

| Variable          | Description                               |
|-------------------|-------------------------------------------|
| `complexBg`       | Complex domain background                 |
| `complicatedBg`   | Complicated domain background             |
| `clearBg`         | Clear domain background                   |
| `chaoticBg`       | Chaotic domain background                 |
| `confusionBg`     | Confusion center region background        |
| `boundaryColor`   | Wavy boundary color                       |
| `boundaryWidth`   | Boundary stroke width                     |
| `cliffColor`      | Clear/Chaotic cliff color                 |
| `cliffWidth`      | Cliff stroke width                        |
| `arrowColor`      | Transition arrow color                    |
| `arrowWidth`      | Transition arrow stroke width             |
| `labelColor`      | Domain name label color                   |
| `textColor`       | Item and subtitle text color              |
| `domainFontSize`  | Domain name font size                     |
| `itemFontSize`    | Item badge and subtitle font size         |

## Gotchas

- Hand-drawn mode is not supported.
- Only the five fixed domain keywords are recognized — no custom domains.
- The wavy boundary is deterministic: same input always produces the same diagram.
