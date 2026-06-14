# XY Charts

Line, bar, area, and scatter charts with configurable axes.

## Syntax

```
xychart beta           %% "beta" keyword required
    title "Title"      %% Optional
    x-axis [Jan, Feb, Mar, Apr]
    y-axis "Values" 0 --> 100
    bar [10, 25, 45, 80]
    line [10, 25, 45, 80]
```

## Chart types

| Type | Syntax | Description |
| --- | --- | --- |
| Line | `line [...]` | Line chart |
| Bar | `bar [...]` | Bar chart |
| Area | `area [...]` | Area chart |
| Scatter | `scatter [...]` | Scatter plot |

Multiple chart types can be combined in one diagram.

## Axis configuration

### X-axis (categorical)

```
x-axis [Jan, Feb, Mar, Apr]
x-axis "Months" [Jan, Feb, Mar]
```

Accepts string array labels. Optional title.

### Y-axis (numerical range)

```
y-axis "Values" 0 --> 100
y-axis 0 --> 100
y-axis "Score" 0.0 --> 1.0
```

Format: `"title" min --> max`. Title optional. Supports decimals.

## Multiple data series

```
xychart beta
    x-axis [Q1, Q2, Q3, Q4]
    y-axis "Revenue" 0 --> 1000
    line [100, 300, 500, 800]
    bar [80, 250, 450, 700]
```

Each chart type keyword adds a new series.
