# Ishikawa Diagrams (v11.12.3+)

Fishbone (cause-and-effect) diagrams for root cause analysis.

## Syntax

```mermaid
ishikawa-beta
    Blurry Photo              %% The problem (head of fish)
    Process                   %% Main cause category
        Out of focus          %% Sub-cause
        Shutter speed too slow
    User
        Shaky hands
    Equipment
        LENS                  %% Nested category
            Inappropriate lens
            Damaged lens
        SENSOR
            Dirty sensor
    Environment
        Too dark
```

## Structure

- First line: the event/problem (fish head)
- Top-level indented lines: main cause categories (fish bones)
- Further indentation: sub-causes (smaller bones)
- Supports arbitrary nesting depth
- Hierarchy defined entirely by indentation
