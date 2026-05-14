# Providers & Models

Pi supports subscription-based providers via OAuth and API key providers via environment variables or auth file. Model list is updated with every release.

## Subscriptions (via /login)

- Anthropic Claude Pro/Max
- OpenAI ChatGPT Plus/Pro (Codex)
- GitHub Copilot

**Removed in 0.71.0:** Google Gemini CLI and Google Antigravity support was removed. Existing configurations using those providers must switch to another supported provider.

## API Keys

Set via environment variable or store in `~/.pi/agent/auth.json`:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pi
```

Key providers: Anthropic, OpenAI, Azure OpenAI Responses, DeepSeek, Google Gemini, Google Vertex, Amazon Bedrock, Mistral (incl. Medium 3.5), Groq, Cerebras, Cloudflare AI Gateway, Cloudflare Workers AI, xAI, OpenRouter, Vercel AI Gateway, ZAI, OpenCode Zen/Go, Hugging Face, Fireworks, Kimi For Coding, MiniMax, Moonshot AI.

Environment variable reference: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`, `GROQ_API_KEY`, `CEREBRAS_API_KEY`, `CLOUDFLARE_API_KEY` (+ `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_GATEWAY_ID`), `XAI_API_KEY`, `OPENROUTER_API_KEY`, `AI_GATEWAY_API_KEY`, `ZAI_API_KEY`, `OPENCODE_API_KEY`, `HF_TOKEN`, `FIREWORKS_API_KEY`, `KIMI_API_KEY`, `MINIMAX_API_KEY`, `MOONSHOT_API_KEY`.

Auth file (`~/.pi/agent/auth.json`):

```json
{
  "anthropic": { "type": "api_key", "key": "sk-ant-..." },
  "openai": { "type": "api_key", "key": "sk-..." }
}
```

Key resolution: CLI `--api-key` → auth.json → environment variable → custom provider keys from models.json.

### Key Formats in auth.json / models.json

- **Shell command:** `"!command"` — executes and uses stdout (cached for process lifetime)
- **Environment variable:** `"MY_API_KEY"` — reads env var value
- **Literal:** `"sk-ant-..."` — used directly

## Cloud Providers

### Azure OpenAI

```bash
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com
# or
export AZURE_OPENAI_RESOURCE_NAME=your-resource
```

### Amazon Bedrock

```bash
export AWS_PROFILE=your-profile
# or AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_BEARER_TOKEN_BEDROCK
export AWS_REGION=us-west-2  # optional, defaults to us-east-1
```

For application inference profiles without recognizable model names: `export AWS_BEDROCK_FORCE_CACHE=1`.

### Google Vertex AI

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_CLOUD_LOCATION=us-central1
```

### Cloudflare AI Gateway (new in 0.71.0)

Routes to OpenAI, Anthropic, and Workers AI through Cloudflare AI Gateway.

```bash
export CLOUDFLARE_API_KEY=...           # or use /login
export CLOUDFLARE_ACCOUNT_ID=...
export CLOUDFLARE_GATEWAY_ID=...        # create at dash.cloudflare.com → AI → AI Gateway
pi --provider cloudflare-ai-gateway --model "claude-sonnet-4-5"
```

Workers AI uses the Unified API (`/compat`) with prefixed model IDs (`workers-ai/@cf/...`). OpenAI passthrough uses `/openai` with native IDs like `gpt-5.1`. Anthropic passthrough uses `/anthropic` with native IDs.

Upstream auth modes: Workers AI (Cloudflare token only), Unified billing (Cloudflare handles upstream auth), Stored BYOK (Cloudflare injects provider keys), Inline BYOK (request supplies upstream key).

### Cloudflare Workers AI

```bash
export CLOUDFLARE_API_KEY=...           # or use /login
export CLOUDFLARE_ACCOUNT_ID=...
pi --provider cloudflare-workers-ai --model "@cf/moonshotai/kimi-k2.6"
```

Pi automatically sets `x-session-affinity` for prefix caching discounts.

### Moonshot AI (new in 0.71.0)

Built-in provider with `MOONSHOT_API_KEY`, default model resolution, and `/login` display support.

```bash
export MOONSHOT_API_KEY=...
pi --provider moonshot --model "kimi-k2.6"
```

## Custom Models (models.json)

Add Ollama, LM Studio, vLLM, or any provider speaking a supported API via `~/.pi/agent/models.json`:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false
      },
      "models": [
        { "id": "llama3.1:8b" },
        { "id": "gpt-oss:20b", "reasoning": true }
      ]
    }
  }
}
```

### Provider Configuration Fields

- `baseUrl` — API endpoint URL
- `api` — API type (see below)
- `apiKey` — API key (supports shell command, env var, literal)
- `headers` — Custom headers (same value resolution as apiKey)
- `authHeader` — Set true for `Authorization: Bearer <apiKey>`
- `models` — Array of model configurations
- `modelOverrides` — Per-model overrides for built-in models

### Supported API Types

- `openai-completions` — OpenAI Chat Completions (most compatible)
- `openai-responses` — OpenAI Responses API
- `anthropic-messages` — Anthropic Messages API
- `google-generative-ai` — Google Generative AI
- `azure-openai-responses` — Azure OpenAI Responses
- `openai-codex-responses` — OpenAI Codex Responses
- `mistral-conversations` — Mistral SDK Conversations
- `google-gemini-cli` — Google Cloud Code Assist
- `google-vertex` — Google Vertex AI
- `bedrock-converse-stream` — Amazon Bedrock Converse

### Model Configuration Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `id` | Yes | — | Model identifier |
| `name` | No | `id` | Display name |
| `api` | No | provider's api | Override API type |
| `reasoning` | No | `false` | Supports extended thinking |
| `input` | No | `["text"]` | Input types |
| `contextWindow` | No | `128000` | Context window in tokens |
| `maxTokens` | No | `16384` | Max output tokens |
| `cost` | No | all zeros | Cost per million tokens |
| `compat` | No | provider compat | Compatibility overrides |

### OpenAI Compat Flags

- `supportsStore` — Provider supports `store` field
- `supportsDeveloperRole` — Use `developer` vs `system` role
- `supportsReasoningEffort` — Support for `reasoning_effort`
- `reasoningEffortMap` — Map thinking levels to provider values
- `supportsUsageInStreaming` — Include usage in streaming (default: true)
- `maxTokensField` — `"max_completion_tokens"` or `"max_tokens"`
- `requiresToolResultName` — Include `name` on tool results
- `requiresAssistantAfterToolResult` — Insert assistant after tool results
- `requiresThinkingAsText` — Convert thinking to plain text
- `thinkingFormat` — `"openai"`, `"deepseek"`, `"zai"`, `"qwen"`, `"qwen-chat-template"`
- `cacheControlFormat` — `"anthropic"` for Anthropic-style cache markers
- `supportsStrictMode` — Include `strict` in tool definitions
- `supportsLongCacheRetention` — Accept long cache retention (default: true)
- `openRouterRouting` — OpenRouter provider routing preferences
- `vercelGatewayRouting` — Vercel AI Gateway routing config

### Override Built-in Providers

Route through proxy without redefining models:

```json
{
  "providers": {
    "anthropic": { "baseUrl": "https://my-proxy.example.com/v1" }
  }
}
```

When `models` is also provided, custom models are merged after built-in overrides. Same `id` replaces; new `id` adds alongside.

### Per-model Overrides

```json
{
  "providers": {
    "openrouter": {
      "modelOverrides": {
        "anthropic/claude-sonnet-4": {
          "name": "Claude Sonnet 4 (Bedrock Route)",
          "compat": { "openRouterRouting": { "only": ["amazon-bedrock"] } }
        }
      }
    }
  }
}
```

## Custom Providers via Extensions

For providers needing custom API or OAuth:

```typescript
pi.registerProvider("my-proxy", {
  baseUrl: "https://proxy.example.com",
  apiKey: "PROXY_API_KEY",
  api: "anthropic-messages",
  models: [{ id: "model-id", reasoning: false, input: ["text"], cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }, contextWindow: 200000, maxTokens: 16384 }],
});

// OAuth support
pi.registerProvider("corporate-ai", {
  baseUrl: "https://ai.corp.com/v1",
  api: "openai-responses",
  models: [...],
  oauth: {
    name: "Corporate AI (SSO)",
    async login(callbacks) {
      callbacks.onAuth({ url: "https://sso.corp.com/authorize?..." });
      const code = await callbacks.onPrompt({ message: "Enter code:" });
      return { refresh: "...", access: "...", expires: Date.now() + 3600000 };
    },
    async refreshToken(credentials) { return credentials; },
    getApiKey(credentials) { return credentials.access; },
  }
});
```

### Custom Streaming API

For non-standard APIs, implement `streamSimple`:

```typescript
import { createAssistantMessageEventStream, calculateCost } from "@mariozechner/pi-ai";

function streamMyProvider(model, context, options) {
  const stream = createAssistantMessageEventStream();
  (async () => {
    const output = { role: "assistant", content: [], api: model.api, provider: model.provider, model: model.id, usage: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, totalTokens: 0, cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 } }, stopReason: "stop", timestamp: Date.now() };
    stream.push({ type: "start", partial: output });
    // ... process response, push text_delta/toolcall_delta events ...
    calculateCost(model, output.usage);
    stream.push({ type: "done", reason: output.stopReason, message: output });
    stream.end();
  })();
  return stream;
}

pi.registerProvider("my-provider", { baseUrl: "...", apiKey: "...", api: "my-custom-api", models: [...], streamSimple: streamMyProvider });
```
