---
name: stitch-2026-05-04
description: AI-powered UI design tool generating high-fidelity screens and frontend code from text prompts and images. Provides MCP tools for coding agents, a TypeScript SDK, DESIGN.md format, and export to Figma/AI Studio. Use when generating UI designs from prompts or images, connecting Stitch to AI coding agents via MCP, or building multi-page sites from prompt-driven designs.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - stitch
  - ui-design
  - ai-design
  - mcp
  - google-labs
  - frontend
category: ml-ai
external_references:
  - https://stitch.withgoogle.com/docs/
---

# Stitch (Google Labs)

## Overview

Stitch is a Google Labs experiment that generates high-fidelity UI designs and frontend code from natural language prompts and images. Powered by Gemini models, it transforms text descriptions or wireframe sketches into interactive, responsive interfaces.

The platform supports an AI-native infinite canvas where designers can explore ideas, iterate with voice commands, and collaborate with an embedded design agent. Designs can be exported as HTML/CSS, pasted to Figma, or connected to coding agents via MCP for automated implementation.

Key integrations:

- **MCP server** — exposes Stitch tools to AI coding agents (Claude Code, Cursor, Gemini CLI, etc.)
- **TypeScript SDK** (`@google/stitch-sdk`) — programmatic API for projects, screens, and design systems
- **CLI** (`@_davideast/stitch-mcp`) — local preview, site building, interactive browsing
- **DESIGN.md** — agent-readable design system format for cross-project consistency

## When to Use

- Generating UI designs from natural language descriptions or image inputs
- Creating multi-screen applications through iterative prompting
- Connecting Stitch to AI coding agents via MCP for automated design-to-code workflows
- Programmatically generating, editing, and exporting screens via the TypeScript SDK
- Maintaining design system consistency across projects with DESIGN.md
- Building complete websites by mapping generated screens to routes
- Extracting design DNA (colors, typography, layout patterns) from existing designs

## Core Concepts

### Projects and Screens

A **project** is a container for related UI screens. Each project has an ID and can hold multiple screens. A **screen** is a single generated UI page with associated HTML/CSS code and a screenshot image.

```
Project → Screens (1:N)
  ├─ Screen 1: Landing page
  ├─ Screen 2: Dashboard
  └─ Screen 3: Settings
```

### Device Types

Screens target specific device form factors:

- `MOBILE` — phone-sized layouts
- `DESKTOP` — wide-screen layouts
- `TABLET` — medium-width layouts
- `AGNOSTIC` — responsive, device-independent

Mobile UIs tend to produce higher quality results than desktop.

### Generation Models

Two Gemini models power screen generation:

- `GEMINI_3_PRO` — higher quality, slower
- `GEMINI_3_FLASH` — faster, good for exploration

### Design Systems

Stitch supports design systems via **DESIGN.md** — a markdown file with YAML front matter containing machine-readable design tokens (colors, typography, spacing, rounded corners) and prose explaining design rationale. Design systems can be created per project and applied across screens for consistency.

## Quick Start

### Via MCP (recommended for coding agents)

Register the Stitch MCP server in your coding agent's config:

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["@_davideast/stitch-mcp", "proxy"]
    }
  }
}
```

Then instruct your agent to:

1. Call `create_project` with a title
2. Call `generate_screen_from_text` with a prompt and the project ID
3. Call `get_screen_code` to retrieve the HTML/CSS

### Via TypeScript SDK

```ts
import { stitch } from "@google/stitch-sdk";

// Create or reference a project
const project = await stitch.projects()[0]; // or stitch.project("project-id")

// Generate a screen from a prompt
const screen = await project.generate(
  "A modern analytics dashboard with charts and stat cards",
  "DESKTOP"
);

// Get the HTML code
const html = await screen.getHtml();

// Edit the screen
const edited = await screen.edit("Make the background dark and add a sidebar");

// Generate variants
const variants = await screen.variants("Try different color schemes", {
  variantCount: 3,
  creativeRange: "EXPLORE",
  aspects: ["COLOR_SCHEME", "LAYOUT"],
});
```

### Via CLI

```bash
# Set up authentication (one-time)
npx @_davideast/stitch-mcp init

# Preview all screens from a project locally
npx @_davideast/stitch-mcp serve -p <project-id>

# Build an Astro site from your designs
npx @_davideast/stitch-mcp site -p <project-id>
```

## Advanced Topics

**MCP Integration**: Platform-specific setup, available tools, authentication methods, virtual tools → [MCP Integration](reference/01-mcp-integration.md)

**TypeScript SDK Reference**: Full API reference for `@google/stitch-sdk` including classes, methods, AI SDK integration → [SDK Reference](reference/02-sdk-reference.md)

**CLI Reference**: Commands for local preview, site building, interactive browsing, and MCP proxy → [CLI Reference](reference/03-cli-reference.md)

**Prompt Engineering**: Strategies for generating quality UI from text descriptions, iteration patterns → [Prompt Engineering](reference/04-prompt-engineering.md)

**Design Systems**: DESIGN.md format, token types, cross-project consistency, linting → [Design Systems](reference/05-design-systems.md)

**Export Workflows**: Figma paste, code export, AI Studio/Antigravity integration, agent skills → [Export Workflows](reference/06-export-workflows.md)
