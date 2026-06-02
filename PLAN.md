# ☑ Plan: Create Vega 6.2.0 Skill
<!-- Plan Title is short but descriptive title of current plan -->

**Depends On:** NONE

**Created:** 2026-06-02T09:30:00Z

**Updated:** 2026-06-02T09:30:00Z

<!-- [emoji-of-phase] Phase X Phase Title -->
**Current Phase:** ☑ Phase 4

<!-- [emoji-of-phase] Phase X - [emoji-of-task] Task X.Y -->
**Current Task:** ☑ Task 4.4

## ☑ Phase 1 Research & Planning

Gather all source material, analyze structure, and plan the skill layout.

- ☑ Task 1.1 Fetch and review npm page for Vega 6.2.0
- ☑ Task 1.2 Fetch and review GitHub repo tree at v6.2.0 tag
- ☑ Task 1.3 Fetch core documentation: specification, data, transforms, marks, scales, signals, expressions, event streams, config
- ☑ Task 1.4 Analyze content scope and determine reference file structure
- ☑ Task 1.5 Create detailed task plan for skill generation

## ☑ Phase 2 Generate SKILL.md

Write the main SKILL.md with YAML header, overview, when to use, core concepts, and navigation to references.

- ☑ Task 2.1 Write YAML header with validated metadata (name: vega-6-2-0, description, version 0.1.0)
- ☑ Task 2.2 Write Overview section covering what Vega is, its JSON spec format, Canvas/SVG rendering
- ☑ Task 2.3 Write When to Use section with specific scenarios
- ☑ Task 2.4 Write Core Concepts section covering the visualization grammar paradigm and spec structure
- ☑ Task 2.5 Write Advanced Topics navigation hub linking to all reference files

## ☑ Phase 3 Generate Reference Files

Create numbered reference files covering distinct subtopics of Vega's specification.

- ☑ Task 3.1 Generate reference/01-specification-and-data.md — top-level spec properties, autosize, data sources and formats
- ☑ Task 3.2 Generate reference/02-scales-and-projections.md — all scale types, domains, ranges, projections
- ☑ Task 3.3 Generate reference/03-marks-and-encoding.md — mark types, encode sets (enter/update/exit/hover), visual encodings
- ☑ Task 3.4 Generate reference/04-transforms.md — basic, geographic, layout, hierarchy, cross-filter transforms
- ☑ Task 3.5 Generate reference/05-signals-and-events.md — signal definitions, event streams, handlers, triggers
- ☑ Task 3.6 Generate reference/06-expressions.md — expression language, bound variables, functions (math, string, date, color, etc.)
- ☑ Task 3.7 Generate reference/07-axes-legends-title.md — axes, legends, title configuration and properties
- ☑ Task 3.8 Generate reference/08-configuration-and-theming.md — config object, view/mark/axis/legend defaults, styles
- ☑ Task 3.9 Generate reference/09-api-and-embedding.md — View API, parse/render methods, embedding in web pages, Node.js usage
- ☑ Task 3.10 Generate reference/10-usage-examples.md — practical examples: bar chart, line chart, scatterplot, interactive tooltip

## ☑ Phase 4 Validate & Finalize

Run structural validation, check for anti-patterns, and regenerate README table.

- ☑ Task 4.1 Run validate-skill.sh structural validator
- ☑ Task 4.2 Perform LLM judgment checks (content accuracy, no hallucination, concise writing)
- ☑ Task 4.3 Fix any issues found during validation
- ☑ Task 4.4 Regenerate README.md skills table using gen-skills-table.sh
