# Timeline Diagrams

Chronological event visualization with grouping and icons.

## Syntax

```mermaid
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

```mermaid
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

```mermaid
timeline
    title Events
    2024 : Launch ::icon(fa fa-rocket)
         : Update ::icon(fa fa-code-branch)
```

## Text wrapping

Long text wraps automatically. Force breaks with `<br>`:

```
timeline
    2024 : Launch of the product<br>and subsequent updates
```

## Styling

Each section gets its own color scheme. Without sections, each time period (and its events) uses an individual color by default.

## Themes

Use standard Mermaid themes: `default`, `base`, `dark`, `forest`, `neutral`.
