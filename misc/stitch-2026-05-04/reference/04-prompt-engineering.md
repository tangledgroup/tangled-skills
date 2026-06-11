# Prompt Engineering

## Contents
- Prompt Structure
- Quality Tips
- Iteration Patterns
- Image and Wireframe Inputs

## Prompt Structure

Effective Stitch prompts follow a clear pattern: **context + layout + style + content**.

```
"A [type] for [audience/purpose] with [key sections/components],
using [style/atmosphere], [specific design details]"
```

### Good prompts include:

- **Page type**: "landing page", "dashboard", "settings screen", "checkout flow"
- **Target audience**: "for SaaS founders", "fitness enthusiasts", "enterprise admins"
- **Key components**: "hero section with CTA", "stat cards", "data table with filters"
- **Style/atmosphere**: "dark mode, card-based, minimal", "clean and modern", "playful with illustrations"
- **Layout specifics**: "sidebar navigation", "three-column grid", "full-width hero"

### Bad prompts:

- Too vague: "make it look good", "a website"
- Missing context: "a dashboard" (what kind? for whom?)

## Quality Tips

### Be specific with style keywords

Use concrete UI/UX terminology rather than abstract descriptions:

- "Dark mode, card-based, minimal" beats "modern looking"
- "Glassmorphism with blur effects" beats "trendy design"
- "Masonry grid layout" beats "nice photo gallery"

### Mobile produces higher quality

Mobile UIs tend to produce more polished results than desktop. When in doubt, generate for `MOBILE` first, then adapt to `DESKTOP`.

### Inject design system context

When generating multiple screens, include design system references in prompts:

```
"A settings page using the same color palette and typography as the
dashboard: dark background (#1A1C1E), Public Sans font, card-based layout
with 8px border radius"
```

Or use `extract_design_context` to capture the design DNA from an existing screen, then pass it as context when generating new screens.

### Device-specific prompting

Specify device type explicitly:

- SDK: `project.generate("prompt", "MOBILE")`
- MCP tool: include `deviceType` parameter
- CLI: use device flag where available

## Iteration Patterns

### Generate → Edit cycle

1. Generate an initial screen with a broad prompt
2. Use `edit_screens` (MCP) or `screen.edit()` (SDK) for refinements
3. Each edit creates a new version; the original is preserved

```ts
const screen = await project.generate("A music player app");
const v2 = await screen.edit("Add a now-playing bar at the bottom with album art");
const v3 = await v2.edit("Switch to a light theme with pastel accent colors");
```

### Variants for exploration

Use variants to explore multiple directions without committing:

```ts
const variants = await screen.variants("Explore different layouts", {
  variantCount: 3,
  creativeRange: "EXPLORE",     // REFINE | EXPLORE | REIMAGINE
  aspects: ["LAYOUT", "COLOR_SCHEME"],
});
```

- `REFINE` — small tweaks to the existing design
- `EXPLORE` — moderate variations
- `REIMAGINE` — significantly different interpretations

### Multi-screen consistency

For multi-page apps, maintain consistency by:

1. Generate the first screen (establishes the style)
2. Extract design context: `extract_design_context`
3. Include extracted context in subsequent screen prompts
4. Or apply a DESIGN.md design system to the project

## Image and Wireframe Inputs

Stitch accepts images as input alongside text prompts:

- **Screenshots**: Upload a screenshot of an existing UI to recreate or adapt it
- **Wireframes**: Hand-drawn sketches or rough wireframes from whiteboards
- **Reference designs**: Screenshots of inspiring designs from other apps

When using image inputs, combine with a text prompt describing desired changes:

```
"Convert this wireframe into a polished mobile app UI with
a blue color scheme and rounded cards"
```

## The enhance-prompt Skill

The `stitch-skills` repository includes an `enhance-prompt` skill that transforms vague UI ideas into polished, Stitch-optimized prompts. It adds UI/UX keywords, injects design system context, and structures output for better generation results.

Install: `npx skills add google-labs-code/stitch-skills --skill enhance-prompt --global`
