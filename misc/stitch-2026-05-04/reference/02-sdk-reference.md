# TypeScript SDK Reference

## Contents
- Installation
- Core Classes
- Variant Options
- Tool Client
- AI SDK Integration
- Configuration
- Error Handling

## Installation

```bash
npm install @google/stitch-sdk
```

For Vercel AI SDK integration, also install `ai`:

```bash
npm install @google/stitch-sdk ai
```

Latest version: v0.1.1 (April 2026). License: Apache 2.0. Repository: `google-labs-code/stitch-sdk`.

## Core Classes

### `stitch` Singleton

Pre-configured instance that reads `STITCH_API_KEY` from the environment. Lazily initialized on first use.

```ts
import { stitch } from "@google/stitch-sdk";

const projects = await stitch.projects();
```

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `projects()` | — | `Promise<Project[]>` | List all accessible projects |
| `project(id)` | `id: string` | `Project` | Reference a project by ID (no API call) |

### `Project`

A Stitch project containing screens.

| Property | Type | Description |
|----------|------|-------------|
| `id` | `string` | Alias for `projectId` |
| `projectId` | `string` | Bare project ID (no `projects/` prefix) |

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `generate(prompt, deviceType?)` | `prompt: string`, `deviceType?: DeviceType` | `Promise<Screen>` | Generate a screen from text |
| `screens()` | — | `Promise<Screen[]>` | List all screens |
| `getScreen(screenId)` | `screenId: string` | `Promise<Screen>` | Retrieve specific screen |
| `createDesignSystem(ds)` | `ds: object` | `Promise<DesignSystem>` | Create a design system |
| `listDesignSystems()` | — | `Promise<DesignSystem[]>` | List design systems |
| `designSystem(id)` | `id: string` | `DesignSystem` | Reference by ID (no API call) |

### `Screen`

A generated UI screen with HTML and screenshot access.

| Property | Type | Description |
|----------|------|-------------|
| `id` | `string` | Alias for `screenId` |
| `screenId` | `string` | Bare screen ID |
| `projectId` | `string` | Parent project ID |

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `edit(prompt, deviceType?, modelId?)` | `prompt: string` | `Promise<Screen>` | Edit with text prompt |
| `variants(prompt, opts, deviceType?, modelId?)` | `prompt: string`, `opts: object` | `Promise<Screen[]>` | Generate variants |
| `getHtml()` | — | `Promise<string>` | Get HTML download URL |
| `getImage()` | — | `Promise<string>` | Get screenshot download URL |

`getHtml()` and `getImage()` use cached data from the generation response when available. If the screen was loaded from `screens()` or `getScreen()`, they call the `get_screen` API automatically.

### `DesignSystem`

A visual theme or branding applied to projects and screens.

| Property | Type | Description |
|----------|------|-------------|
| `id` | `string` | Alias for `assetId` |
| `assetId` | `string` | Bare asset ID (no `assets/` prefix) |
| `projectId` | `string` | Parent project ID |

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `update(ds)` | `ds: object` | `Promise<DesignSystem>` | Update theme |
| `apply(selectedScreenInstances)` | `instances: object[]` | `Promise<Screen[]>` | Apply to screens |

`selectedScreenInstances` is an array of `{ id: string, sourceScreen: string }` objects from `project.data.screenInstances`.

## Variant Options

The `screen.variants()` method accepts a `variantOptions` object:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `variantCount` | `number` | 3 | Number of variants (1–5) |
| `creativeRange` | `string` | `"EXPLORE"` | `"REFINE"`, `"EXPLORE"`, or `"REIMAGINE"` |
| `aspects` | `string[]` | all | `"LAYOUT"`, `"COLOR_SCHEME"`, `"IMAGES"`, `"TEXT_FONT"`, `"TEXT_CONTENT"` |

```ts
const variants = await screen.variants("Try different color schemes", {
  variantCount: 3,
  creativeRange: "EXPLORE",
  aspects: ["COLOR_SCHEME", "LAYOUT"],
});
```

## Enums

### `DeviceType`

`"MOBILE"` | `"DESKTOP"` | `"TABLET"` | `"AGNOSTIC"`

### `modelId`

`"GEMINI_3_PRO"` | `"GEMINI_3_FLASH"`

## Tool Client

For agents and orchestration scripts needing direct MCP tool access:

```ts
import { StitchToolClient } from "@google/stitch-sdk";

const client = new StitchToolClient({ apiKey: "your-api-key" });
const result = await client.callTool("create_project", { title: "My Project" });
await client.close();
```

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `callTool<T>(name, args)` | `name: string`, `args: Record<string, any>` | `Promise<T>` | Call an MCP tool |
| `listTools()` | — | `Promise<{ tools }>` | List available tools |
| `connect()` | — | `Promise<void>` | Explicitly connect (auto-called by `callTool`) |
| `close()` | — | `Promise<void>` | Close the connection |

The client auto-connects on first `callTool` or `listTools`. No explicit `connect()` needed.

## AI SDK Integration

### Vercel AI SDK

Drop Stitch tools directly into `generateText()`:

```ts
import { generateText, stepCountIs } from "ai";
import { google } from "@ai-sdk/google";
import { stitchTools } from "@google/stitch-sdk/ai";

const { text, steps } = await generateText({
  model: google("gemini-2.5-flash"),
  tools: stitchTools(),
  prompt: "Create a project and generate a modern dashboard",
  stopWhen: stepCountIs(5),
});
```

Filter to specific tools:

```ts
const tools = stitchTools({
  include: ["create_project", "generate_screen_from_text", "get_screen"],
});
```

### Google ADK (Agent Development Kit)

```ts
import { stitchAdkTools } from "@google/stitch-sdk/adk";
import { LlmAgent } from "@google/adk";

const tools = stitchAdkTools();
const designerAgent = new LlmAgent({
  name: "Designer",
  model: "gemini-2.5-pro",
  instruction: "Create a project and generate a screen.",
  tools,
});
```

### StitchProxy

Expose Stitch tools through your own MCP server:

```ts
import { StitchProxy } from "@google/stitch-sdk";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const proxy = new StitchProxy({ apiKey: "..." });
const transport = new StdioServerTransport();
await proxy.start(transport);
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `STITCH_API_KEY` | Yes (or use OAuth) | API key for authentication |
| `STITCH_ACCESS_TOKEN` | No | OAuth access token (alternative) |
| `GOOGLE_CLOUD_PROJECT` | With OAuth | Google Cloud project ID |
| `STITCH_HOST` | No | Override the MCP server URL |

### Explicit Configuration

```ts
import { Stitch, StitchToolClient } from "@google/stitch-sdk";

const client = new StitchToolClient({
  apiKey: "your-api-key",
  baseUrl: "https://stitch.googleapis.com/mcp",
  timeout: 300_000,
});

const sdk = new Stitch(client);
const projects = await sdk.projects();
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | `string` | `STITCH_API_KEY` | API key |
| `accessToken` | `string` | `STITCH_ACCESS_TOKEN` | OAuth token |
| `projectId` | `string` | `GOOGLE_CLOUD_PROJECT` | Cloud project ID |
| `baseUrl` | `string` | `https://stitch.googleapis.com/mcp` | MCP server URL |
| `timeout` | `number` | `300000` | Request timeout (ms) |

Authentication requires either `apiKey` or both `accessToken` and `projectId`.

## Error Handling

All domain class methods throw `StitchError` on failure:

```ts
import { stitch, StitchError } from "@google/stitch-sdk";

try {
  const project = stitch.project("bad-id");
  await project.screens();
} catch (error) {
  if (error instanceof StitchError) {
    console.error(error.code);        // "UNKNOWN_ERROR"
    console.error(error.message);     // Human-readable description
    console.error(error.recoverable); // false
  }
}
```

Error codes: `AUTH_FAILED`, `NOT_FOUND`, `PERMISSION_DENIED`, `RATE_LIMITED`, `NETWORK_ERROR`, `VALIDATION_ERROR`, `UNKNOWN_ERROR`.
