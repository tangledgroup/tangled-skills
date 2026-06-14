# Venn Diagrams (v11.12.3+)

Show relationships between sets using overlapping circles.

## Syntax

```
venn-beta
    title "Title"              %% Optional
    set A["Label"]             %% Define a set
    set B["Label"]:10          %% Set with size
    union A,B["Overlap"]:3     %% Intersection with label and size
```

### Text nodes (labels inside sets)

```
set A["Frontend"]
    text t1["React"]
    text t2["Design Systems"]
```

Indented `text` lines attach to the most recent `set` or `union`.

## Styling

```
style A fill:#ff6b6b
style B fill:#4ecdc4
style A,B color:#333
style A1 fill-opacity:0.5
```

Properties: `fill`, `color`, `stroke`, `stroke-width`, `fill-opacity`.
