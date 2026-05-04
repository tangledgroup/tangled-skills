# ☑ Plan: Stitch 2026-05-04 Skill

**Depends On:** NONE
**Created:** 2026-05-04T11:15:00Z
**Updated:** 2026-05-04T11:35:00Z
**Current Phase:** ☑ Phase 5
**Current Task:** ☑ Task 5.2

---

## Source Analysis

Stitch is a Google Labs AI-powered UI design tool (stitch.withgoogle.com). The docs site is a fully client-rendered SPA (Google's "Nemo" framework), so direct crawling yields no content. All source material was gathered from:

- **Blog posts**: developers.googleblog.com (May 2025 launch), blog.google (Mar 2026 "vibe design" update)
- **GitHub repos**: `google-labs-code/stitch-sdk` (official SDK, v0.1.1), `google-labs-code/stitch-skills` (agent skills library, 5.2k stars), `davideast/stitch-mcp` (community MCP CLI, v0.5.5), `google-labs-code/design.md` (DESIGN.md format spec)
- **Third-party guides**: sotaaz.com (MCP setup guide), codecademy.com (tutorial)
- **CodeLab**: codelabs.developers.google.com (Antigravity + Stitch integration)

### Key domains identified:

1. **Core product** — what Stitch is, how it works in the browser (prompt → UI, image → UI, iterate, export)
2. **MCP integration** — connecting Stitch to AI coding agents via MCP tools
3. **SDK (`@google/stitch-sdk`)** — programmatic TypeScript API for projects/screens/design systems
4. **CLI (`@_davideast/stitch-mcp`)** — community CLI for local preview, site building, proxy
5. **DESIGN.md** — design system format (separate skill exists, but needs coverage as Stitch feature)
6. **Agent skills (`stitch-skills`)** — companion skills library for coding agents
7. **Prompt engineering** — best practices for generating quality UI
8. **Export/workflow** — Figma paste, code export, AI Studio/Antigravity integration

### Structure decision: Complex skill with 6 reference files

SKILL.md covers overview + quick start + core concepts (under 500 lines). Reference files cover the deep domains an agent would load selectively:

- `reference/01-mcp-integration.md` — MCP setup, tools, platform configs
- `reference/02-sdk-reference.md` — TypeScript SDK API reference
- `reference/03-cli-reference.md` — stitch-mcp CLI commands
- `reference/04-prompt-engineering.md` — prompt strategies for quality UI generation
- `reference/05-design-systems.md` — DESIGN.md, design systems, consistency
- `reference/06-export-workflows.md` — Figma, code export, agent integrations

---

## Phases and Tasks

## ☑ Phase 1 Content Collection

Gather all remaining source material. The SPA docs site is inaccessible via static crawling, so we need to maximize coverage from available sources.

- ☑ Task 1.1 Crawl stitch-mcp CLI docs (raw README from GitHub)
  - Extract commands table, authentication methods, environment variables
  - Source: `github.com/davideast/stitch-mcp` raw README.md

- ☑ Task 1.2 Crawl CodeLab for Antigravity + Stitch integration details
  - Get step-by-step workflow, MCP setup in context
  - Source: `codelabs.developers.google.com/design-to-code-with-antigravity-stitch`

- ☑ Task 1.3 Crawl Codecademy tutorial for beginner-friendly workflow
  - Get UI generation steps, iteration patterns
  - Source: `codecademy.com/article/google-stitch-tutorial-ai-powered-ui-design-tool`

- ☑ Task 1.4 Verify no additional doc URLs exist (SPA nav routes from DuckDuckGo results)
  - Check: `/docs/learn/overview`, `/docs/mcp/setup`, `/docs/mcp/guide`, `/docs/design-md/overview`
  - Note which are accessible vs SPA-only

- ☑ Task 1.5 Compile content inventory
  - Map all gathered content to planned reference files
  - Identify any gaps that need synthesis from multiple sources

## ⚙️ Phase 2 SKILL.md Draft

Write the main skill file as the navigation hub with quick-start content.

- ☑ Task 2.1 Write YAML header
  - name: `stitch-2026-05-04`
  - description: Cover WHAT (AI UI design tool generating high-fidelity screens from prompts/images), key capabilities (MCP tools, TypeScript SDK, DESIGN.md design systems, code export), and WHEN (generating UI designs programmatically, connecting Stitch to coding agents, building multi-screen apps from prompts)
  - version: `"2026-05-04"` (date-based snapshot of current state)
  - tags: `stitch`, `ui-design`, `ai-design`, `mcp`, `google-labs`, `frontend`
  - category: `ml-ai`

- ☑ Task 2.2 Write Overview section
  - What Stitch is (Google Labs experiment, Gemini-powered)
  - Core value proposition (prompt/image → UI design + frontend code)
  - Key capabilities summary

- ☑ Task 2.3 Write When to Use section
  - Specific scenarios: generating UI from prompts, multi-screen app generation, connecting to coding agents via MCP, programmatic screen generation via SDK

- ☑ Task 2.4 Write Core Concepts section
  - Projects and Screens model
  - Design systems / DESIGN.md
  - Device types (MOBILE, DESKTOP, TABLET, AGNOSTIC)
  - Generation models (GEMINI_3_PRO, GEMINI_3_FLASH)

- ☑ Task 2.5 Write Quick Start section
  - Minimal working example: create project → generate screen → get HTML
  - Show both SDK and MCP approaches

- ☑ Task 2.6 Write Advanced Topics navigation hub
  - Links to all 6 reference files with one-line descriptions

## ⚙️ Phase 3 Reference Files

Write all 6 reference files with detailed content from collected sources.

- ☑ Task 3.1 Write `reference/01-mcp-integration.md` (depends on: Task 1.5)
  - MCP server setup for each platform (Claude Code, Cursor, VS Code, Gemini CLI, Codex, OpenCode)
  - Authentication methods (OAuth via gcloud, STITCH_API_KEY, system gcloud)
  - Available tools list with descriptions and schemas
  - Virtual tools (build_site, get_screen_code, get_screen_image)
  - Common issues (.env conflicts, API key vs OAuth, permission errors)
  - Health check / doctor command

- ☑ Task 3.2 Write `reference/02-sdk-reference.md` (depends on: Task 1.5)
  - Installation (`npm install @google/stitch-sdk`)
  - Core classes: Stitch, Project, Screen, DesignSystem, StitchToolClient
  - Full method reference with parameters and return types
  - Variant generation options
  - DeviceType enum
  - Error handling (StitchError, error codes)
  - Configuration (env vars, explicit config)
  - AI SDK integration (Vercel AI SDK, ADK)
  - StitchProxy for custom MCP servers

- ☑ Task 3.3 Write `reference/03-cli-reference.md` (depends on: Task 1.5)
  - Installation (`npx @_davideast/stitch-mcp`)
  - All commands with descriptions and examples
  - Authentication flows (init wizard, API key, manual gcloud)
  - Environment variables
  - Local preview server (`serve`)
  - Site builder (`site` → Astro)
  - Interactive browser (`view`, `screens`)
  - MCP proxy for agents

- ☑ Task 3.4 Write `reference/04-prompt-engineering.md` (depends on: Task 1.5)
  - Prompt structure strategies
  - UI/UX keyword injection
  - Design system context in prompts
  - Image/wireframe input patterns
  - Iteration and refinement patterns
  - Device-specific prompting
  - Quality tips (mobile vs web, specificity levels)
  - The `enhance-prompt` skill reference

- ☑ Task 3.5 Write `reference/05-design-systems.md` (depends on: Task 1.5)
  - DESIGN.md format overview (YAML front matter + markdown body)
  - Token types (Color, Dimension, Typography, Token Reference)
  - Component tokens with variants
  - Creating/applying design systems via SDK
  - Extracting design DNA from screens (`extract_design_context`)
  - Cross-project consistency patterns
  - Linting and validation (`@google/design.md` CLI)
  - Export formats (Tailwind v3/v4, DTCG)
  - Note: DESIGN.md spec itself covered by separate `design-md-0-1-1` skill

- ☑ Task 3.6 Write `reference/06-export-workflows.md` (depends on: Task 1.5)
  - Figma paste workflow
  - HTML/CSS code export
  - AI Studio integration
  - Antigravity IDE integration
  - Agent skills library (`stitch-skills`) overview
  - React component conversion (`react:components` skill)
  - shadcn/ui integration
  - Remotion video walkthroughs
  - stitch-loop for multi-page sites

## ⚙️ Phase 4 Validation and Polish

Validate all files against the write-skill checklist.

- ☑ Task 4.1 YAML header validation (depends on: Task 2.6)
  - name matches directory, regex valid
  - description 150-400 chars, includes WHAT and WHEN
  - version non-empty
  - tags 3-7, category valid

- ☑ Task 4.2 Structure validation (depends on: Task 3.6)
  - SKILL.md under 500 lines
  - Reference files numbered 01-06 with descriptive names
  - No chained references
  - All reference links from SKILL.md use correct relative paths

- ☑ Task 4.3 Content validation (depends on: Task 4.2)
  - No hallucinated content — all from crawled sources
  - Concise — no over-explaining basics
  - Consistent terminology
  - Single recommended approach per task
  - Code examples are copy-pasteable with language tags

- ☑ Task 4.4 Cross-reference check (depends on: Task 4.3)
  - Verify DESIGN.md references point to existing `design-md-0-1-1` skill where appropriate
  - Verify MCP tool names match actual upstream tools
  - Verify SDK method signatures match `@google/stitch-sdk` v0.1.1
  - Verify CLI commands match `@_davideast/stitch-mcp` v0.5.5

## ☑ Phase 5 Final Steps

- ☑ Task 5.1 Run gen-skills-table.py (depends on: Task 4.4)
  - `python3 misc/gen-skills-table.py` to sync README.md

- ☑ Task 5.2 Clean up temp files
  - Remove `/tmp/stitch_*.md` crawled source files
