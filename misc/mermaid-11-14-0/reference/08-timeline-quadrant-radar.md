# Timeline, Quadrant Charts, and Radar Charts

## Timeline Diagrams

Chronological event sequences organized by time periods.

### Basic Syntax

```mermaid
timeline
  title History of Social Media
  2002 : LinkedIn
  2004 : Facebook : Google
  2005 : YouTube
  2006 : Twitter
```

- `title` — Optional chart title
- Each line: `{time period} : {event}` or multiple events per period with additional `:`
- Both time periods and events are plain text (not limited to numbers)

### Multiple Events Per Period

```mermaid
timeline
  title Release History
  2024 Q1 : Feature A : Feature B
          : Feature C
  2024 Q2 : Feature D
```

## Quadrant Charts

Two-axis data plotting divided into four quadrants.

### Basic Syntax

```mermaid
quadrantChart
  title Reach and engagement of campaigns
  x-axis Low Reach --> High Reach
  y-axis Low Engagement --> High Engagement
  quadrant-1 We should expand
  quadrant-2 Need to promote
  quadrant-3 Re-evaluate
  quadrant-4 May be improved
  Campaign A: [0.3, 0.6]
  Campaign B: [0.45, 0.23]
  Campaign C: [0.57, 0.69]
```

### Axis Labels

- `x-axis <left text> --> <right text>` — Both labels
- `x-axis <text>` — Left label only
- `y-axis <bottom text> --> <top text>` — Both labels
- `y-axis <text>` — Bottom label only

### Points

- Format: `Point Name: [x, y]`
- x and y values range from **0 to 1**

## Radar Charts

Multi-variable data comparison using radial axes.

### Basic Syntax

```mermaid
radar
  title Skill Assessment
  axis Speed, Strength, Agility, Endurance, Accuracy
  alice: [85, 70, 90, 60, 75]
  bob: [70, 85, 65, 80, 90]
```

- `title` — Optional chart title
- `axis` — Comma-separated axis names
- Each data series: `name: [value1, value2, ...]`
- Values typically 0-100

### Configuration

- `max` — Maximum axis value (default: 100)
- `min` — Minimum axis value (default: 0)
- `size` — Chart size in pixels
