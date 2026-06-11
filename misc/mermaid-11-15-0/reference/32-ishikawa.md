# Ishikawa (Fishbone) Diagram

## Contents
- Syntax
- Nested Causes

## Overview

Ishikawa diagrams visualize causes of a problem as a fishbone structure. Available since v11.12.3. Experimental.

```mermaid
ishikawa-beta
    Blurry Photo
    Process
        Out of focus
        Shutter speed too slow
    User
        Shaky hands
    Equipment
        Inappropriate lens
        Dirty sensor
```

## Syntax

- First line: the problem (diagram title)
- Top-level indented items: cause categories (bones)
- Further indented items: sub-causes

```mermaid
ishikawa-beta
    Problem
    Category 1
        Sub-cause A
        Sub-cause B
            Nested cause
    Category 2
        Sub-cause C
```

Any nesting depth is supported. Categories and causes are plain text (no quoting required for simple names).
