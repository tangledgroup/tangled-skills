# ☑ Plan: Generate gunicorn-26-0-0 Skill

**Depends On:** NONE

**Created:** 2026-05-29T09:12:34Z

**Updated:** 2026-05-29T09:12:34Z

**Current Phase:** ☑ Phase 5

**Current Task:** ☑ Task 5.4

## ☑ Phase 1 Content Collection

- ☑ Task 1.1 Fetch gunicorn.org homepage via webfetch
- ☑ Task 1.2 Fetch GitHub README.md (tag 26.0.0) via raw GitHub URL
- ☑ Task 1.3 Fetch key documentation pages from docs/content/ on the 26.0.0 branch:
  - quickstart.md, install.md, configure.md, run.md, deploy.md
- ☑ Task 1.4 Fetch advanced documentation pages:
  - custom.md, asgi.md, uwsgi.md, signals.md, instrumentation.md, faq.md
- ☑ Task 1.5 Fetch reference/settings.md (configuration settings reference)
- ☑ Task 1.6 Fetch design.md and dirty.md for architectural understanding

## ☑ Phase 2 Content Analysis

- ☑ Task 2.1 Review all fetched content and identify core topics and subtopics
- ☑ Task 2.2 Determine reference file split strategy based on topic clustering:
  - Configuration settings (large reference table)
  - Deployment patterns (Docker, systemd, reverse proxies)
  - Worker types and customization (custom workers, ASGI, uWSGI)
  - Operational concerns (signals, instrumentation, FAQ)
- ☑ Task 2.3 Draft SKILL.md outline with YAML header fields

## ☑ Phase 3 Generate SKILL.md

- ☑ Task 3.1 Write YAML header with validated name `gunicorn-26-0-0`, description, tags, category
- ☑ Task 3.2 Write Overview section covering Gunicorn's role as WSGI HTTP server
- ☑ Task 3.3 Write When to Use section with specific trigger scenarios
- ☑ Task 3.4 Write Core Concepts section (WSGI, worker models, config approaches)
- ☑ Task 3.5 Write Installation/Setup section
- ☑ Task 3.6 Write Usage Examples section with copy-pasteable command examples
- ☑ Task 3.7 Write Advanced Topics section linking to reference files

## ☑ Phase 4 Generate Reference Files

- ☑ Task 4.1 Write reference/01-configuration-settings.md — full settings reference table from settings.md
- ☑ Task 4.2 Write reference/02-deployment.md — Docker, systemd, reverse proxy patterns from deploy.md + guides/docker.md
- ☑ Task 4.3 Write reference/03-workers-and-customization.md — worker types, custom apps, ASGI, uWSGI from custom.md, asgi.md, uwsgi.md
- ☑ Task 4.4 Write reference/04-operations.md — signals, instrumentation, FAQ, dirty code handling from signals.md, instrumentation.md, faq.md, dirty.md

## ☑ Phase 5 Validate and Finalize

- ☑ Task 5.1 Run structural validator: `bash scripts/validate-skill.sh .agents/skills/gunicorn-26-0-0`
  - Fix any reported errors
- ☑ Task 5.2 Perform LLM judgment checks:
  - Content accuracy (no hallucinated settings or options)
  - Consistent terminology throughout
  - Concise writing without over-explaining basics
  - Single recommended approach where applicable
- ☑ Task 5.3 Run skills table generator: `bash scripts/gen-skills-table.sh`
- ☑ Task 5.4 Verify README.md was updated with the new skill entry
