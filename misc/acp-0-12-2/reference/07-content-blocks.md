# Content Blocks

## Overview

Content blocks represent displayable information flowing through ACP. They provide a structured way to handle various types of user-facing content — text from LLMs, images for analysis, embedded resources for context.

Content blocks appear in:
- User prompts via `session/prompt`
- LLM output streamed through `session/update` notifications
- Progress updates and results from tool calls

ACP uses the same `ContentBlock` structure as MCP, enabling agents to forward content from MCP tool outputs without transformation.

## Text Content

Plain text is the foundation of most interactions:

```json
{
  "type": "text",
  "text": "What's the weather like today?"
}
```

All agents must support text content blocks in prompts.

Optional `annotations` field provides metadata about how content should be used or displayed.

## Image Content

Images for visual context or analysis:

```json
{
  "type": "image",
  "mimeType": "image/png",
  "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB..."
}
```

Requires the `image` prompt capability during initialization.

Fields:
- **data** — Base64-encoded image data (required)
- **mimeType** — MIME type like `image/png`, `image/jpeg` (required)
- **uri** — Optional URI reference for the image source

## Audio Content

Audio data for transcription or analysis:

```json
{
  "type": "audio",
  "mimeType": "audio/wav",
  "data": "UklGRiQAAABXQVZFb..."
}
```

Requires the `audio` prompt capability during initialization.

Fields:
- **data** — Base64-encoded audio data (required)
- **mimeType** — MIME type like `audio/wav`, `audio/mp3` (required)

## Embedded Resource

Complete resource contents embedded directly in the message:

```json
{
  "type": "resource",
  "resource": {
    "uri": "file:///home/user/script.py",
    "mimeType": "text/x-python",
    "text": "def hello():\n    print('Hello, world!')"
  }
}
```

This is the preferred way to include context in prompts — such as when using @-mentions to reference files. By embedding content directly, clients can include context from sources the agent may not have direct access to.

## Content in Tool Calls

Tool calls produce content through their `content` field:

```json
{
  "content": [
    {
      "type": "content",
      "content": { "type": "text", "text": "Result output..." }
    },
    {
      "type": "diff",
      "diff": {
        "uri": "file:///path/to/file.py",
        "unidiff": "--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new"
      }
    }
  ]
}
```

Diff content allows clients to display file changes inline in the editor.
