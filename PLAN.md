# ☑ Plan: ghostscript-10-07-0 skill

**Depends On:** NONE
**Created:** 2026-05-13T13:45:00Z
**Updated:** 2026-05-13T13:45:00Z
**Current Phase:** ☑ Phase 5
**Current Task:** ☑ Task 5.3

## ☑ Phase 1 — Crawl and Collect Sources

- ☑ Task 1.1 Fetch remaining key documentation pages (Color Management, GhostPDL framework, Fonts, PostScript language reference)
- ☑ Task 1.2 Fetch GitHub repo README, NEWS/CHANGES, and key source files (configure.ac, Makefile.in snippets for build config)
- ☑ Task 1.3 Save all fetched content to temp files for reference during writing

## ☑ Phase 2 — Analyze and Plan Structure

- ☑ Task 2.1 Determine reference file split based on collected content domains (CLI usage, devices, API/SDK, build/install, PDF-specific features)
- ☑ Task 2.2 Draft the SKILL.md outline with YAML header fields and section plan

## ☑ Phase 3 — Write SKILL.md

- ☑ Task 3.1 Write YAML header (name: ghostscript-10-07-0, description, tags, category)
- ☑ Task 3.2 Write Overview section (WHAT Ghostscript is, key capabilities)
- ☑ Task 3.3 Write When to Use section with specific trigger scenarios
- ☑ Task 3.4 Write Core Concepts section (PDL interpreters, devices, output model)
- ☑ Task 3.5 Write quick-start Usage Examples (most common CLI patterns)
- ☑ Task 3.6 Write Advanced Topics navigation hub linking to reference files

## ☑ Phase 4 — Write Reference Files

- ☑ Task 4.1 Write `reference/01-command-line-reference.md` — switches, parameters (-d/-s), environment variables, file searching, pipes
- ☑ Task 4.2 Write `reference/02-output-devices.md` — raster devices (PNG/JPEG/TIFF/PNM), high-level devices (pdfwrite/ps2write/eps2write/txtwrite/docxwrite/xpswrite), device selection, resolution, per-page output
- ☑ Task 4.3 Write `reference/03-pdf-features.md` — PDF-specific switches (-dPDFFitPage, box options, page ranges, password, annotations, AcroForm, compression)
- ☑ Task 4.4 Write `reference/04-build-and-install.md` — configure/make workflow, platform notes (Unix/Windows/macOS), shared library builds, source layout
- ☑ Task 4.5 Write `reference/05-api-and-bindings.md` — gsapi C API lifecycle (new_instance/init/run/exit/delete), language bindings (Python/C#/Java), display device callbacks

## ☑ Phase 5 — Validate and Finalize

- ☑ Task 5.1 Run structural validator: `bash scripts/validate-skill.sh .agents/skills/ghostscript-10-07-0`
- ☑ Task 5.2 LLM judgment checks (content accuracy, no hallucination, consistent terminology, concise writing)
- ☑ Task 5.3 Regenerate README.md skills table: `bash scripts/gen-skills-table.sh`
