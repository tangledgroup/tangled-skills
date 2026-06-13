# Theming

## Contents
- Available Themes
- Site-Wide Theme
- Diagram-Specific Theme
- themeVariables Customization
- Color Derivation Rules
- Full Theme Variables Reference

## Available Themes

| Theme | Description |
|---|---|
| `default` | Standard Mermaid colors (applied to all diagrams by default) |
| `neutral` | Black and white, ideal for printed documents |
| `dark` | Dark mode compatible |
| `forest` | Shades of green |
| `base` | Only modifiable theme — use as foundation for customizations |

Only `base` accepts `themeVariables` overrides. Set `theme: 'base'` before customizing variables.

## Site-Wide Theme

Apply to all diagrams via `initialize()`:

```javascript
mermaid.initialize({
  securityLevel: 'loose',
  theme: 'base',
  themeVariables: {
    primaryColor: '#BB2528',
    lineColor: '#F8B229',
  },
});
```

## Diagram-Specific Theme

Use frontmatter to set theme per-diagram. Must use `base` for variable overrides:

```mermaid
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#BB2528'
    primaryTextColor: '#fff'
    primaryBorderColor: '#7C0000'
    lineColor: '#F8B229'
    secondaryColor: '#006100'
    tertiaryColor: '#fff'
---
flowchart LR
    A --> B
```

## themeVariables Customization

Theme variables define colors for all visual elements. Set via `themeVariables` under `config:` in frontmatter or `initialize()`.

### Core Variables

| Variable | Default | Description |
|---|---|---|
| `darkMode` | false | Affects how derived colors are calculated; set `true` for dark mode |
| `background` | #f4f4f4 | Background color; used to calculate contrasting items |
| `fontFamily` | trebuchet ms, verdana, arial | Font family for all diagram text |
| `fontSize` | 16px | Font size in pixels |
| `primaryColor` | #fff4dd | Node background; other colors derived from this |
| `primaryTextColor` | calculated | Text color on `primaryColor` nodes |
| `secondaryColor` | calculated from primaryColor | Secondary fill color |
| `primaryBorderColor` | calculated from primaryColor | Border on `primaryColor` nodes |
| `secondaryBorderColor` | calculated from secondaryColor | Border on `secondaryColor` nodes |
| `secondaryTextColor` | calculated from secondaryColor | Text on `secondaryColor` nodes |
| `tertiaryColor` | calculated from primaryColor | Tertiary fill color |
| `tertiaryBorderColor` | calculated from tertiaryColor | Border on `tertiaryColor` nodes |
| `tertiaryTextColor` | calculated from tertiaryColor | Text on `tertiaryColor` nodes |
| `noteBkgColor` | #fff5ad | Note rectangle background |
| `noteTextColor` | #333 | Note text color |
| `noteBorderColor` | calculated from noteBkgColor | Note border color |
| `lineColor` | calculated from background | Edge/line color |
| `textColor` | calculated from primaryTextColor | Text over background (labels, signals, Gantt title) |
| `mainBkg` | calculated from primaryColor | Background in flowchart rects/circles, class boxes, sequence actors |
| `errorBkgColor` | tertiaryColor | Syntax error message background |
| `errorTextColor` | tertiaryTextColor | Syntax error message text |

### Flowchart Variables

| Variable | Default | Description |
|---|---|---|
| `nodeBorder` | primaryBorderColor | Node border color |
| `clusterBkg` | tertiaryColor | Subgraph background |
| `clusterBorder` | tertiaryBorderColor | Subgraph border |
| `defaultLinkColor` | lineColor | Default edge/line color |
| `titleColor` | tertiaryTextColor | Title color |
| `edgeLabelBackground` | calculated from secondaryColor | Edge label background |
| `nodeTextColor` | primaryTextColor | Text inside nodes |

### Sequence Diagram Variables

| Variable | Default | Description |
|---|---|---|
| `actorBkg` | mainBkg | Actor background color |
| `actorBorder` | primaryBorderColor | Actor border color |
| `actorTextColor` | primaryTextColor | Actor text color |
| `actorLineColor` | actorBorder | Actor lifeline color |
| `signalColor` | textColor | Signal line color |
| `signalTextColor` | textColor | Signal text color |
| `labelBoxBkgColor` | actorBkg | Label box background (alt/opt/loop) |
| `labelBoxBorderColor` | actorBorder | Label box border |
| `labelTextColor` | actorTextColor | Label text color |
| `loopTextColor` | actorTextColor | Loop text color |
| `activationBorderColor` | calculated from secondaryColor | Activation bar border |
| `activationBkgColor` | secondaryColor | Activation bar fill |
| `sequenceNumberColor` | calculated from lineColor | Sequence number color |

### Pie Diagram Variables

| Variable | Default | Description |
|---|---|---|
| `pie1`–`pie12` | calculated | Fill colors for slices 1–12 |
| `pieTitleTextSize` | 25px | Title text size |
| `pieTitleTextColor` | taskTextDarkColor | Title text color |
| `pieSectionTextSize` | 17px | Section label size |
| `pieSectionTextColor` | textColor | Section label color |
| `pieLegendTextSize` | 17px | Legend label size |
| `pieLegendTextColor` | taskTextDarkColor | Legend label color |
| `pieStrokeColor` | black | Slice border color |
| `pieStrokeWidth` | 2px | Slice border width |
| `pieOuterStrokeWidth` | 2px | Outer circle border width |
| `pieOuterStrokeColor` | black | Outer circle border color |
| `pieOpacity` | 0.7 | Slice opacity |

### State Diagram Colors

| Variable | Default | Description |
|---|---|---|
| `labelColor` | primaryTextColor | Label text color |
| `altBackground` | tertiaryColor | Background in deep composite states |

### Class Diagram Colors

| Variable | Default | Description |
|---|---|---|
| `classText` | textColor | Text color in class diagrams |

### User Journey Colors

| Variable | Default | Description |
|---|---|---|
| `fillType0`–`fillType7` | calculated | Fill colors for sections 1–8 |

## Color Derivation Rules

- Derived colors (e.g., `primaryBorderColor`) are automatically calculated from their source variable
- Adjustments include color inversion, hue shift, or darkening/lightening by ~10%
- The theming engine only recognizes **hex colors** — color names like `red` will not work for derivation
- Set `darkMode: true` to change how derived colors are computed (useful for dark themes)
