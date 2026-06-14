# Timeline Diagrams

Chronological event visualization with grouping and icons.

## Syntax

```
timeline
    title History of Social Media
    2002 : LinkedIn
    2004 : Facebook : Google     %% Multiple events per period
    2005 : YouTube
         : Twitter               %% Same period as above (empty time)
```

## Structure

- `timeline` keyword starts the diagram
- `title "Text"` sets the title (optional)
- Each line: `{time period} : {event}` or multiple events separated by `:`
- Empty time field (`: Event`) continues previous time period
- Supports icons via `::icon(fa fa-name)`

## Grouping

```
timeline
    title Tech Timeline
    2000s
        : 2004 : Facebook
        : 2005 : YouTube
    2010s
        : 2010 : iPad
        : 2012 : Instagram Mobile
```

Indented blocks create visual groupings.

## Icons

```
timeline
    title Events
    2024 : Launch ::icon(fa fa-rocket)
         : Update ::icon(fa fa-code-branch)
```
