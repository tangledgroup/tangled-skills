# Radar Charts (v11.6.0+)

Multi-axis circular charts for comparing entities across dimensions. Also known as spider, star, or Kiviat diagrams.

## Syntax

```
radar-beta
    title "Title"                    %% Optional
    axis id["Label"], id2["Label2"]  %% Define axes (multiple per line)
    axis id3["Label3"]
    curve c1["Name"]{v1, v2, v3}    %% Data curve
    curve c2["Name"]{v1, v2, v3}

    max 100                          %% Scale maximum
    min 0                            %% Scale minimum
```

## Details

### Axes

Each axis has an id and optional display label in brackets. Multiple axes can be on one line.

```
axis m["Math"], s["Science"], e["English"]
```

### Curves

Each curve has an id, optional label, and values in braces matching axis order.

```
curve alice["Alice"]{85, 90, 80, 70}
curve bob["Bob"]{70, 75, 85, 80}
```

### Graticule style

```
graticule polygon   %% Polygon grid lines
graticule circle    %% Circular grid lines (default)
```

### Scale

```
max 100
min 0
```

Defaults to auto-scaling if not specified.
