# ☑ Plan: Check Skill Versions for Updates

**Depends On:** NONE
**Created:** 2026-05-01T00:00:00Z
**Updated:** 2026-05-01T18:35:00Z
**Current Phase:** ☑ Phase 9
**Current Task:** ☑ Phase 9 - ☑ Task 9.1

## ☑ Phase 1 Extract Version Info From All Skills

- ☑️ Task 1.1 Parse all SKILL.md files to extract package name, version, and external reference URLs
  - Extract YAML headers for package name, version, homepage/registry URLs
  - Build a structured list of all skills with their version info and check endpoints

- ☑️ Task 1.2 Classify skills by registry type (PyPI, npm, GitHub releases, etc.)
  - Group by: pypi, npm, github-releases, github-tags, other

- ☑️ Task 1.3 Batch-check latest versions from registries
  - Query PyPI JSON API for Python packages
  - Query npm registry API for Node.js packages
  - Query GitHub API for release-based projects
  - Check homepages/other sources for remaining

## ☑ Phase 2 Compare And Report

- ☑️ Task 2.1 Compile version comparison results (depends on: Task 1.3)
  - List skills with newer versions available
  - Note any breaking changes or migration notes if detectable

- ☑️ Task 2.2 Present findings to user (depends on: Task 2.1)
  - Summary table of outdated skills
  - Skills already at latest version
  - Skills that couldn't be checked

## ☑ Phase 3 Generate New Skill Files for Updated Versions

> Rules: never remove existing skills, keep all older versions. Skip tinypy-1-1-0 and llama-cpp-1-0-0. Skip meta skills (write-skill, git, tzip, workflow, caveman, coding-guidelines).

- ☑ Task 3.1 Generate ruff-0-15-12 (PyPI 0.4.10 → 0.15.12)
  - Major update with many rule changes

- ☑ Task 3.2 Generate mem0-2-0-1 (PyPI 1.0.11 → 2.0.1)
  - Major v2 release

- ☑ Task 3.3 Generate cryptography-47-0-0 (PyPI 46.0.0 → 47.0.0)

- ☑ Task 3.4 Generate spec-kit-0-8-3 (GitHub 0.6.1 → 0.8.3)

- ☑ Task 3.5 Generate aiozmq-1-0-0 (PyPI 0.7.0 → 1.0.0)

- ☑ Task 3.6 Generate transformers-5-7-0 (PyPI 5.5.4 → 5.7.0)

- ☑ Task 3.7 Generate tokenizers-0-23-1 (PyPI 0.22.3 → 0.23.1)

- ☑ Task 3.8 Generate curl-8-20-0 (GitHub 8.19.0 → 8.20.0)

- ☑ Task 3.9 Generate gh-2-92-0 (GitHub 2.91.0 → 2.92.0)

- ☑ Task 3.10 Generate pi-mono-0-71-0 (GitHub 0.66.1 → 0.71.0)

- ☑ Task 3.11 Generate networkxternal-0-5 (GitHub 0.3.0 → 0.5)

- ☑ Task 3.12 Generate rustfs-1-0-0-beta-1 (GitHub alpha.93 → beta.1)

- ☑ Task 3.13 Generate payloadcms-3-84-1 + payloadcms-blank/website/ecommerce-3-84-1 (npm 3.82.1 → 3.84.1)

- ☑ Task 3.14 Generate deno-2-7-14 (GitHub 2.7.0 → 2.7.14)

- ☑ Task 3.15 Generate bun-1-3-13 (GitHub/npm 1.3.12 → 1.3.13)

## ☑ Phase 4 Generate Patch-Level Skill Updates

- ☑ Task 4.1 Generate aiohttp-3-13-5 (PyPI 3.13.0 → 3.13.5)

- ☑ Task 4.2 Generate aiohttp-session-2-12-1 (PyPI 2.12.0 → 2.12.1)

- ☑ Task 4.3 Generate daisyui-5-5-19 (npm 5.5.0 → 5.5.19)

- ☑ Task 4.4 Generate dayjs-1-11-20 (npm 1.11.0 → 1.11.20)

- ☑ Task 4.5 Generate mempalace-3-3-4 (PyPI 3.3.0 → 3.3.4)

- ☑ Task 4.6 Generate nltk-3-9-4 (PyPI 3.9.2 → 3.9.4)

- ☑ Task 4.7 Generate numba-0-65-1 (PyPI 0.65.0 → 0.65.1)

- ☑ Task 4.8 Generate pywebview-6-2-1 (PyPI 6.2.0 → 6.2.1)

- ☑ Task 4.9 Generate textual-8-2-5 (PyPI 8.2.4 → 8.2.5)

- ☑ Task 4.10 Generate openai-2-33-0 (PyPI 2.31.0 → 2.33.0)

- ☑ Task 4.11 Generate opentelemetry-python-1-41-1 (PyPI 1.41.0 → 1.41.1)

- ☑ Task 4.12 Generate uv-0-11-8 (PyPI 0.11.6 → 0.11.8)

- ☑ Task 4.13 Generate boto3-1-43-1 (PyPI 1.42.89 → 1.43.1)

- ☑ Task 4.14 Generate ty-0-0-33 (PyPI 0.0.29 → 0.0.33)

- ☑ Task 4.15 Generate matplotlib-3-10-9 (PyPI 3.10.8 → 3.10.9)

## ☑ Phase 5 Generate npm Patch Updates

- ☑ Task 5.1 Generate alpinejs-3-15-12 (npm 3.15.11 → 3.15.12)

- ☑ Task 5.2 Generate axios-1-15-2 (npm 1.15.0 → 1.15.2)

- ☑ Task 5.3 Generate htm-3-1-1 (npm 3.1.0 → 3.1.1)

- ☑ Task 5.4 Generate nextjs-16-2-4 (npm 16.2.3 → 16.2.4)

- ☑ Task 5.5 Generate oat-0-6-1 (npm 0.6.0 → 0.6.1)

- ☑ Task 5.6 Generate solid-meta-0-29-4 (npm 0.29.0 → 0.29.4)

- ☑ Task 5.7 Generate solid-router-0-16-1 (npm 0.16.0 → 0.16.1)

- ☑ Task 5.8 Generate solid-start-1-3-2 (npm 1.3.0 → 1.3.2)

- ☑ Task 5.9 Generate tailwindcss-browser-4-2-4 (npm 4.2.0 → 4.2.4)

## ☑ Phase 6 Generate GitHub Release Updates

- ☑ Task 6.1 Generate crun-1-27-1 (GitHub 1.27.0 → 1.27.1)

- ☑ Task 6.2 Generate obscura-0-1-1 (GitHub 0.1.0 → 0.1.1)

- ☑ Task 6.3 Generate podman-5-8-2 (GitHub 5.8.1 → 5.8.2)

- ☑ Task 6.4 Generate rsync-3-4-2 (GitHub 3.4.1 → 3.4.2)

## ☑ Phase 7 Handle htmx 2.x and 4.x Exact Versions

> htmx 4.0 is not yet on npm (latest is 2.0.10). Generate exact-version skills for both series.

- ☑ Task 7.1 Update htmx-2-0-0 to reflect latest 2.x (2.0.10) or generate htmx-2-0-10
  - Keep existing htmx-2-0-0, add htmx-2-0-10 for latest 2.x

- ☑ Task 7.2 Verify htmx 4.0 status and generate if available
  - Check four.htmx.org for actual 4.0 release
  - If 4.0 exists, keep htmx-4-0-0; if beta only, note in skill

## ☑ Phase 8 Handle Special Cases

- ☑ Task 8.1 Generate agentmemory-0-9-4 (npm/GitHub 0.8.10 → 0.9.4)

- ☑ Task 8.2 Generate opentelemetry-1-56-0 (spec 1.55.0 → 1.56.0)

- ☑ Task 8.3 Generate haproxy-3-3-8 (website 3.3.0 → 3.3.8)

## ☑ Phase 9 Regenerate README.md Skills Table

- ☑ Task 9.1 Run gen-skills-table.py to update README.md (depends on: Task 3.1, Task 4.1, Task 5.1, Task 6.1, Task 7.1, Task 8.1)
  - python3 scripts/gen-skills-table.py
