# Ishikawa Diagram Reference

## Description

Ishikawa (fishbone) diagrams represent causes of a specific event or problem. The main problem sits at the "head" with cause categories branching off like fishbones. Also called cause-and-effect or herringbone diagrams.

> **Note:** Uses `ishikawa-beta` keyword — experimental, syntax may evolve. (v11.12.3+)

## Basic Syntax

```mermaid
ishikawa-beta
    Blurry Photo
    Process
        Out of focus
        Shutter speed too slow
    User
        Shaky hands
    Equipment
        LENS
            Inappropriate lens
            Damaged lens
        SENSOR
            Damaged sensor
    Environment
        Too dark
```

## Structure

- **First line:** The event/problem (the "fish head")
- **Subsequent top-level lines:** Cause categories (main fishbones)
- **Indented lines:** Sub-causes branching from categories
- **Deeper indentation:** Further sub-causes

## Examples

### Manufacturing Defect

```mermaid
ishikawa-beta
    Product Defects
    Materials
        Poor quality raw materials
        Inconsistent supplier batches
    Methods
        Incorrect assembly procedure
        Missing quality checks
    Machines
        Worn tooling
        Calibration drift
    People
        Insufficient training
        Fatigue from overtime
    Environment
        Temperature fluctuations
        Humidity levels
    Measurement
        Inaccurate gauges
        Inconsistent testing methods
```

### Website Performance

```mermaid
ishikawa-beta
    Slow Website Load Time
    Frontend
        Unoptimized images
        Excessive JavaScript
        No caching strategy
    Backend
        N+1 queries
            Missing indexes
            No query optimization
        Slow API calls
            Third-party dependencies
            No request batching
    Infrastructure
        Under-provisioned servers
        No CDN
        Inefficient load balancing
    Content
        Large page size
        Too many HTTP requests
```

### Simple Root Cause Analysis

```mermaid
ishikawa-beta
    Customer Complaints
    Product
        Poor quality
        Missing features
    Service
        Slow response time
        Unhelpful support staff
    Process
        Complicated returns
        Hidden fees
    Communication
        Unclear documentation
        No proactive updates
```
