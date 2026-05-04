# Export Workflows

## Contents
- Figma Integration
- Code Export
- AI Studio Integration
- Antigravity IDE Integration
- Agent Skills Library

## Figma Integration

Stitch supports pasting generated designs directly to Figma for further refinement and collaboration with design teams.

Workflow:

1. Generate or refine a screen in Stitch
2. Use the "Paste to Figma" function
3. The design appears in Figma as editable layers
4. Integrate into existing Figma design systems

This bridges the gap between AI-generated designs and professional design workflows.

## Code Export

Stitch generates clean, functional HTML/CSS based on your designs. Access code via:

### SDK

```ts
const html = await screen.getHtml();  // Returns download URL
```

### MCP Tools

- `get_screen_code` — retrieves raw HTML/CSS of a specific screen
- `build_site` — maps screens to routes, returns per-page HTML

### CLI

```bash
# Preview screens locally (serves HTML via Vite dev server)
npx @_davideast/stitch-mcp serve -p <project-id>

# Build a complete Astro site
npx @_davideast/stitch-mcp site -p <project-id>
```

The `site` command generates an Astro project with screens mapped to routes, producing a deployable static site.

## AI Studio Integration

Export designs from Stitch to Google AI Studio for continued development:

1. Generate and refine UI in Stitch
2. Export the design (HTML/CSS + DESIGN.md)
3. Import into AI Studio's vibe coding environment
4. Use Gemini to build a fully functional web app from the design foundation

This creates a design-to-code pipeline: Stitch handles visual design, AI Studio handles implementation.

## Antigravity IDE Integration

Connect Stitch to Google's Antigravity IDE via MCP for autonomous design-to-code workflows:

1. Set up Stitch MCP server in Antigravity
2. Agent fetches design assets and screen HTML via MCP tools
3. Agent implements a production-ready React site from the designs
4. DESIGN.md provides the design system context to the agent

The CodeLab "Design-to-Code with Antigravity and Stitch" demonstrates this full workflow: generate UI in Stitch → connect via MCP → autonomous agent builds a React application.

## Agent Skills Library

The `stitch-skills` repository (`google-labs-code/stitch-skills`, 5.2k stars) provides agent skills that work with the Stitch MCP server. Each skill follows the Agent Skills open standard for compatibility with Antigravity, Gemini CLI, Claude Code, and Cursor.

### Available Skills

| Skill | Description |
|-------|-------------|
| `stitch-design` | Unified entry point: prompt enhancement, design system synthesis, screen generation/editing |
| `stitch-loop` | Generate complete multi-page websites from a single prompt with automated file organization |
| `design-md` | Analyze Stitch projects and generate DESIGN.md files documenting design systems |
| `enhance-prompt` | Transform vague UI ideas into polished, Stitch-optimized prompts |
| `react:components` | Convert Stitch screens to React component systems with validation |
| `remotion` | Generate walkthrough videos from Stitch projects using Remotion |
| `shadcn-ui` | Expert guidance for integrating shadcn/ui components with Stitch designs |

### Installation

```bash
# List available skills
npx skills add google-labs-code/stitch-skills --list

# Install a specific skill
npx skills add google-labs-code/stitch-skills --skill stitch-design --global
```

### Workflow: stitch-loop

The `stitch-loop` skill generates complete multi-page websites from a single prompt:

1. Agent receives a high-level website description
2. Calls Stitch to generate individual screens for each page
3. Organizes files into a project structure
4. Validates HTML consistency across pages
5. Outputs a complete, navigable website

### Workflow: react:components

The `react:components` skill converts Stitch-generated HTML into React component systems:

1. Fetch screen HTML via Stitch MCP
2. Parse and convert to React components
3. Validate design token consistency
4. Output a component library with proper TypeScript types
