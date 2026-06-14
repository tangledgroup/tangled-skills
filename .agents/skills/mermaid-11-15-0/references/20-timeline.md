# Timeline Reference

## Description

Timelines illustrate chronologies of events, dates, or periods. Events are organized by time periods with optional sections and icons.

> **Note:** Experimental — icon integration is experimental. Syntax otherwise stable.

## Basic Syntax

```mermaid
timeline
    title History of Social Media
    2002 : LinkedIn
    2004 : Facebook
         : Google
    2005 : YouTube
    2006 : Twitter
```

## Structure

```
timeline
    title "Optional Title"
    {time_period} : {event}
                 : {another_event}    %% Same time period
    {time_period} : {event} : {event} %% Multiple events on one line
```

- Time periods and events are plain text (not limited to numbers)
- Multiple events per period: indent continuation lines or use `:` separators

## Sections

```mermaid
timeline
    title Project Timeline
    section Planning
        2024-Q1 : Requirements
                : Design
    section Development
        2024-Q2 : Sprint 1
                : Sprint 2
    section Launch
        2024-Q3 : Beta Release
```

## Icons

```mermaid
timeline
    title Events
    2020 : Event A ::icon(fa fa-star)
         : Event B
```

Icon syntax: `::icon(icon_pack icon_name)` — uses iconify packs.

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `animating` | Enable animation | `false` |
| `height` | Diagram height | auto |
| `scale` | Time scale | `1` |
| `useWidth` | Use full width | `true` |

## Examples

### Company History

```mermaid
timeline
    title Company Milestones
    2015 : Founded
         : First product launch
    2017 : Series A funding
         : Team grows to 50
    2019 : Product v2.0
         : International expansion
    2021 : Series B funding
         : 200 employees
    2024 : IPO
```

### With Sections

```mermaid
timeline
    title Software Development Lifecycle
    section Planning
        Week 1-2 : Requirements gathering
                 : Stakeholder interviews
    section Design
        Week 3-4 : Architecture design
                 : UI/UX prototyping
    section Development
        Week 5-8 : Sprint 1
                 : Sprint 2
    section Testing
        Week 9-10 : QA testing
                  : Bug fixes
    section Release
        Week 11 : Production deployment
```
