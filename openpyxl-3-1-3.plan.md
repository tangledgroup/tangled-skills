# ☑ Plan: openpyxl-3-1-3 Skill Generation

**Depends On:** NONE

**Created:** 2026-05-29T00:00:00Z

**Updated:** 2026-05-29T00:00:00Z

**Current Phase:** ☑ Phase 8

**Current Task:** ☑ Task 8.2

## ☑ Phase 1 Content Collection

- ☑ Task 1.1 Fetch remaining documentation pages (worksheet properties, validation, worksheet tables, filters, print settings, pivot, comments, datetime, simple formulae, defined names, workbook custom doc props, protection, images, pandas, performance, rich text)
  - Fetch all "Worksheets" section docs: editing_worksheets, worksheet_properties, validation, worksheet_tables, filters, print_settings, pivot, comments, datetime, simple_formulae
  - Fetch all "Workbooks" section docs: defined_names, workbook_custom_doc_props, protection
  - Fetch remaining sections: images, pandas, performance, rich_text
- ☑ Task 1.2 Fetch chart type reference pages (bar, area, line, pie, scatter, bubble, doughnut, radar, stock, surface) and chart layout/axes docs
  - Fetch charts/bar.html, charts/area.html, charts/line.html, charts/pie.html, charts/scatter.html, charts/bubble.html, charts/doughnut.html, charts/radar.html, charts/stock.html, charts/surface.html
  - Fetch charts/chart_layout.html, charts/limits_and_scaling.html, charts/secondary.html, charts/pattern.html, charts/gauge.html
- ☑ Task 1.3 Organize fetched content by domain for reference file mapping
  - Group all fetched content into the planned reference file categories

## ☑ Phase 2 Structure Design

- ☑ Task 2.1 Define SKILL.md outline and reference file split (depends on: Task 1.3)
  - SKILL.md: Overview, When to Use, Core Concepts (Workbook/Worksheet/Cell model), Quick Start examples, Installation, link to Advanced Topics
  - Plan 8-10 reference files covering distinct domains so agents load only what they need
- ☑ Task 2.2 Draft YAML header with validated name, description, tags, category
  - name: openpyxl-3-1-3, version: 0.1.0, category: library
  - Description following WHAT + WHEN formula, ~200 chars

## ☑ Phase 3 Write SKILL.md (Hub File)

- ☑ Task 3.1 Write YAML header and Overview section
  - Include project summary, supported formats (xlsx/xlsm/xltx/xltm), key classes (Workbook, Worksheet, Cell)
- ☑ Task 3.2 Write When to Use and Core Concepts sections
  - Specific trigger scenarios: Excel file creation, data export, report generation, spreadsheet manipulation
  - Core concepts: Workbook → Worksheet → Cell hierarchy, coordinate systems, Python type auto-conversion
- ☑ Task 3.3 Write Installation/Setup and Quick Start code examples
  - pip install openpyxl, optional deps (pillow for images, lxml for large files, defusedxml for security)
  - Minimal working example: create workbook, write data, save
- ☑ Task 3.4 Write Advanced Topics navigation hub linking to reference files
  - Link each reference file with one-line description

## ☑ Phase 4 Write Reference Files — Core Operations

- ☑ Task 4.1 Write reference/01-workbooks.md (depends on: Task 2.1)
  - Workbook creation, loading (load_workbook flags: data_only, keep_vba, read_only, rich_text, keep_links)
  - Sheet management (create_sheet, delete, copy_worksheet, sheetnames, iteration)
  - Saving (file paths, streams, template mode, xlsm/keep_vba caveats)
  - Workbook properties and document metadata
- ☑ Task 4.2 Write reference/02-cells-and-data.md (depends on: Task 2.1)
  - Cell access (ws['A1'], ws.cell(row, col)), value assignment, Python type conversion
  - Range access (slicing, iter_rows, iter_cols, ws.rows, ws.columns, values_only)
  - Data appending (ws.append()), row/column operations (insert, delete, move_range)
  - Cell types and coordinate utilities (get_column_letter, column_index_from_string)
- ☑ Task 4.3 Write reference/03-styles-and-formatting.md (depends on: Task 2.1)
  - Font, Fill (PatternFill, GradientFill), Border (Side), Alignment, Protection
  - Cell styles (immutable after assignment) vs Named Styles (mutable templates)
  - Color models (aRGB recommended, indexed, theme), number formats
  - Page setup (orientation, paper size, fitToWidth/Height)
  - Builtin styles list

## ☑ Phase 5 Write Reference Files — Advanced Features

- ☑ Task 5.1 Write reference/04-charts.md (depends on: Task 2.1)
  - Chart creation pattern: BarChart/PieChart/etc → add_data(Reference) → set_categories → ws.add_chart
  - All chart types: Area, Bar/Column, Bubble, Line, Scatter, Pie, Doughnut, Radar, Stock, Surface
  - Axes configuration (limits, scaling, orientation, secondary axis)
  - Chart layout (size, position, legend), styling (patterns)
- ☑ Task 5.2 Write reference/05-conditional-formatting.md (depends on: Task 2.1)
  - Three rule types: builtins (ColorScale, IconSet, DataBar), standard (cellIs, formula), custom differential styles
  - ColorScaleRule, IconSetRule, DataBarRule convenience factories
  - FormulaRule for custom conditions
- ☑ Task 5.3 Write reference/06-worksheet-features.md (depends on: Task 2.1)
  - Merging/unmerging cells, merge cell styling
  - Data validation (dropdowns, date/number/text constraints, allow_blank, show_input_message)
  - AutoFilter and sorting (FilterColumn, CustomFilter, SortState)
  - Tables (Table, TableColumn, TableStyleInfo, table parts)
  - Comments on cells
  - Hyperlinks
  - Worksheet protection (SheetProtection)
  - Print settings (page breaks, print area, print titles, margins)
  - Pivot tables (read-only support overview)
  - DateTime handling and timezone considerations
- ☑ Task 5.4 Write reference/07-images-and-drawings.md (depends on: Task 2.1)
  - Image insertion (Image from file path, ws.add_image with anchor cell)
  - Drawing objects and positioning (OneCellAnchor, TwoCellAnchor, AbsoluteAnchor)
  - Rich text in cells (CellRichText, TextBlock)
  - Pillow dependency requirement

## ☑ Phase 6 Write Reference Files — Performance and Integration

- ☑ Task 6.1 Write reference/08-performance-and-modes.md (depends on: Task 2.1)
  - Read-only mode (load_workbook(read_only=True), ReadOnlyWorksheet, ws.rows iteration, wb.close())
  - Write-only mode (Workbook(write_only=True), append only, WriteOnlyCell for styled cells, single save)
  - Performance tips (lxml for large files, avoiding cell creation loops, reset_dimensions)
- ☑ Task 6.2 Write reference/09-pandas-integration.md (depends on: Task 2.1)
  - dataframe_to_rows() utility for writing pandas DataFrames to worksheets
  - Reading data back into DataFrames pattern
  - expand_index() for multi-index support

## ☑ Phase 7 Validate Structure

- ☑ Task 7.1 Run validate-skill.sh on the skill directory (depends on: Task 4.3, Task 5.4, Task 6.2)
  - bash scripts/validate-skill.sh .agents/skills/openpyxl-3-1-3
  - Fix any structural issues reported
- ☑ Task 7.2 LLM judgment review of all files (depends on: Task 7.1)
  - Check content accuracy against fetched sources
  - Verify no hallucinated content
  - Confirm consistent terminology
  - Ensure single recommended approach per topic
  - Verify code examples are correct and copy-pasteable

## ☑ Phase 8 Finalize

- ☑ Task 8.1 Regenerate README.md skills table (depends on: Task 7.2)
  - bash scripts/gen-skills-table.sh
- ☑ Task 8.2 Report completion with file tree and validation summary
