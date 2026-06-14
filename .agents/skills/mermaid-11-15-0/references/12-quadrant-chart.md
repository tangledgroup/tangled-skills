# Quadrant Chart Reference

## Description

Quadrant charts plot data points on a two-dimensional grid divided into four quadrants. Used to identify patterns, prioritize actions, and compare items across two variables. Common in business analysis, marketing, and risk management.

> **Note:** Point coordinates must be between 0 and 1. Values outside this range are clamped silently.

## Basic Syntax

```mermaid
quadrantChart
    title Reach and Engagement
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 Expand
    quadrant-2 Promote
    quadrant-3 Re-evaluate
    quadrant-4 Improve
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
```

## Axes

### X-Axis

```
x-axis <left_label> --> <right_label>
x-axis <left_label>          %% Only left label
```

### Y-Axis

```
y-axis <bottom_label> --> <top_label>
y-axis <bottom_label>            %% Only bottom label
```

## Quadrants

Quadrants are numbered counter-clockwise from top-right:

| Quadrant | Position |
|----------|----------|
| `quadrant-1` | Top-right |
| `quadrant-2` | Top-left |
| `quadrant-3` | Bottom-left |
| `quadrant-4` | Bottom-right |

```
quadrant-1 "Label"
quadrant-2 "Label"
quadrant-3 "Label"
quadrant-4 "Label"
```

## Data Points

```
Point Label: [x, y]
```

- `x` and `y` are values between 0 and 1
- Point labels can contain spaces (no quotes needed)

## Examples

### Campaign Analysis

```mermaid
quadrantChart
    title Reach and Engagement of Campaigns
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
    Campaign C: [0.57, 0.69]
    Campaign D: [0.78, 0.34]
    Campaign E: [0.40, 0.34]
    Campaign F: [0.35, 0.78]
```

### Risk Assessment

```mermaid
quadrantChart
    title Risk Assessment Matrix
    x-axis Low Impact --> High Impact
    y-axis Low Probability --> High Probability
    quadrant-1 Critical — Act immediately
    quadrant-2 Watch closely
    quadrant-3 Monitor
    quadrant-4 Accept or mitigate
    Server outage: [0.9, 0.3]
    Data breach: [0.8, 0.7]
    Minor bug: [0.2, 0.8]
    Feature request: [0.5, 0.2]
```
