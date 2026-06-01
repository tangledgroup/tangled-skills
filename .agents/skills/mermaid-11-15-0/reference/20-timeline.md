# Timeline Diagram

## Contents
- Basic Syntax
- Sections/Ages
- Multiple Events per Period
- Text Wrapping
- Direction (v11.14.0+)
- Styling and Themes

## Overview

Timelines illustrate chronological events. Experimental — syntax may change.

```mermaid
timeline
    title History of Social Media
    2002 : LinkedIn
    2004 : Facebook : Google
    2005 : YouTube
    2006 : Twitter
```

## Basic Syntax

Start with `timeline` keyword, optional `title`, then time periods with events:

```
{time period} : {event}
{time period} : {event} : {event}
```

Time periods and events are plain text (not limited to dates).

## Sections/Ages

Group time periods with `section`:

```mermaid
timeline
    title Industrial Revolution
    section 17th-20th century
        Industry 1.0 : Machinery, Steam power
        Industry 2.0 : Electricity, Mass production
    section 21st century
        Industry 4.0 : Internet, AI
```

Sections share a color scheme for visual grouping.

## Multiple Events per Period

Same line or indented continuation:

```mermaid
timeline
    2024 Q1 : Event A : Event B
            : Event C
    2024 Q2 : Event D
```

## Text Wrapping

Long text auto-wraps. Use `<br>` for forced line breaks:

```mermaid
timeline
    section Stone Age
        6000 BC : Sea levels rise<br>Britain becomes an island
```

## Direction (v11.14.0+)

Set direction after `timeline` keyword:

```mermaid
timeline TD
    title Vertical Timeline
    2002 : LinkedIn
    2004 : Facebook
```

Valid directions: `LR` (default), `TD`, `RL`, `BT`.

## Styling and Themes

Timelines follow the active theme. Use `classDef` for custom styling where supported.
