# Providers and Models

## Contents
- Supported Providers
- Authentication Methods
- OAuth Providers
- Custom Models
- Provider-Specific Options
- Environment Variables
- Model Selection

## Supported Providers

Pi supports 20+ providers. Each provider uses a specific API implementation:

| Provider | API | Auth |
|----------|-----|------|
| Anthropic | `anthropic-messages` | API key or OAuth (Pro/Max) |
| OpenAI | `openai-responses` | API key |
| OpenAI Codex | `openai-codex-responses` | OAuth (ChatGPT Plus/Pro) |
| Azure OpenAI | `azure-openai-responses` | API key |
| Google Gemini | `google-generative-ai` | API key |
| Vertex AI | `google-vertex` | API key or ADC |
| DeepSeek | `openai-completions` | API key |
| Mistral | `mistral-conversations` | API key |
| Groq | `openai-completions` | API key |
| Cerebras | `openai-completions` | API key |
| xAI | `openai-completions` | API key |
| Amazon Bedrock | `bedrock-converse-stream` | AWS credentials |
| OpenRouter | `openai-completions` | API key |
| Vercel AI Gateway | `openai-completions` | API key |
| Cloudflare AI Gateway | `openai-completions` | API key + Account ID |
| Cloudflare Workers AI | `openai-completions` | API key + Account ID |
| GitHub Copilot | `openai-completions` | OAuth |
| Fireworks | `anthropic-messages` (compatible) | API key |
| Kimi For Coding | `anthropic-messages` (compatible) | API key |
| MiniMax | `openai-completions` | API key |
| Xiaomi MiMo | `anthropic-messages` (compatible) | API key (API billing or Token Plan) |
| OpenCode Zen / Go | `openai-completions` | API key |
| Any OpenAI-compatible | `openai-completions` | API key |

OpenAI-compatible providers (Ollama, vLLM, LM Studio, etc.) use `openai-completions` API.

## Authentication Methods

### API Keys

Set via environment variables or pass explicitly:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
pi
```

Or in interactive mode:
```
/login   # Interactive provider selection
```

Credentials saved to `~/.pi/agent/auth.json`.

### Subscription Login (OAuth)

Three providers support subscription-based OAuth:
- **Anthropic** — Claude Pro/Max
- **OpenAI Codex** — ChatGPT Plus/Pro (access to GPT-5.x Codex models)
- **GitHub Copilot** — Copilot subscription

Use `/login` in interactive mode or `npx @earendil-works/pi-ai login <provider>` from CLI.

## OAuth Providers

### Anthropic Pro/Max
```bash
npx @earendil-works/pi-ai login anthropic
```
Credentials saved to `auth.json`. Token auto-refreshes via `refreshOAuthToken()`.

### OpenAI Codex
Requires ChatGPT Plus or Pro subscription. Provides access to GPT-5.x Codex models with extended context windows and reasoning capabilities. Automatically handles session-based prompt caching when `sessionId` is provided. Set `transport` to `"sse"`, `"websocket"`, or `"auto"` for transport selection. WebSocket connections are reused per session and expire after 5 minutes of inactivity.

### GitHub Copilot
If you get "The requested model is not supported", enable the model manually in VS Code: open Copilot Chat, click model selector, select model (warning icon), click "Enable".

### Vertex AI
Supports API key or Application Default Credentials (ADC):
```bash
# Local development (ADC)
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="my-project"
export GOOGLE_CLOUD_LOCATION="us-central1"

# CI/Production (service account)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

## Custom Models

Add custom models via `~/.pi/agent/models.json` for providers that speak a supported API (OpenAI, Anthropic, Google). For custom APIs or OAuth, use extensions.

### Example: Ollama via OpenAI-compatible API

```json
{
  "ollama": {
    "baseUrl": "http://localhost:11434/v1",
    "apiKey": "dummy",
    "models": [
      {
        "id": "llama-3.1-8b",
        "name": "Llama 3.1 8B (Ollama)",
        "reasoning": false,
        "input": ["text"],
        "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
        "contextWindow": 128000,
        "maxTokens": 32000
      }
    ]
  }
}
```

### OpenAI Compatibility Settings

For custom proxies or unknown endpoints, use the `compat` field:

```json
{
  "litellm": {
    "baseUrl": "http://localhost:4000/v1",
    "apiKey": "...",
    "compat": {
      "supportsStore": false,
      "supportsDeveloperRole": false,
      "supportsReasoningEffort": false,
      "maxTokensField": "max_tokens"
    },
    "models": [...]
  }
}
```

Common compat flags:
- `supportsStore` — Whether provider supports the `store` field (default: true)
- `supportsDeveloperRole` — Whether provider supports `developer` role vs `system` (default: true)
- `supportsReasoningEffort` — Whether provider supports `reasoning_effort` (default: true)
- `supportsUsageInStreaming` — Whether provider supports streaming usage (default: true)
- `maxTokensField` — `"max_completion_tokens"` or `"max_tokens"` (default: max_completion_tokens)
- `thinkingFormat` — `"openai"`, `"deepseek"`, `"zai"`, `"qwen"`, `"qwen-chat-template"`

### Model-Level Thinking Level Map

Map pi thinking levels to provider-specific values. Missing keys use provider defaults, `null` marks unsupported:

```json
{
  "thinkingLevelMap": {
    "minimal": null,
    "low": null,
    "medium": null,
    "high": "high",
    "xhigh": null
  }
}
```

## Provider-Specific Options

### Anthropic Thinking
```typescript
await complete(anthropicModel, context, {
  thinkingEnabled: true,
  thinkingBudgetTokens: 8192
});
```

### OpenAI Reasoning (o1, o3, gpt-5)
```typescript
await complete(openaiModel, context, {
  reasoningEffort: "medium",
  reasoningSummary: "detailed"  // OpenAI Responses API only
});
```

### Google Gemini Thinking
```typescript
await complete(googleModel, context, {
  thinking: {
    enabled: true,
    budgetTokens: 8192  // -1 for dynamic, 0 to disable
  }
});
```

### Unified Thinking (simplified)
```typescript
const response = await completeSimple(model, context, {
  reasoning: "medium"  // 'minimal' | 'low' | 'medium' | 'high' | 'xhigh'
});
```

## Environment Variables

| Provider | Variable(s) |
|----------|-------------|
| OpenAI | `OPENAI_API_KEY` |
| Azure OpenAI | `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_BASE_URL` or `AZURE_OPENAI_RESOURCE_NAME` |
| Anthropic | `ANTHROPIC_API_KEY` or `ANTHROPIC_OAUTH_TOKEN` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| Google | `GEMINI_API_KEY` |
| Vertex AI | `GOOGLE_CLOUD_API_KEY` or ADC + `GOOGLE_CLOUD_PROJECT` + `GOOGLE_CLOUD_LOCATION` |
| Mistral | `MISTRAL_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Cerebras | `CEREBRAS_API_KEY` |
| Cloudflare AI Gateway | `CLOUDFLARE_API_KEY` + `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_GATEWAY_ID` |
| Cloudflare Workers AI | `CLOUDFLARE_API_KEY` + `CLOUDFLARE_ACCOUNT_ID` |
| xAI | `XAI_API_KEY` |
| Fireworks | `FIREWORKS_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| Vercel AI Gateway | `AI_GATEWAY_API_KEY` |
| zAI | `ZAI_API_KEY` |
| MiniMax | `MINIMAX_API_KEY` |
| OpenCode Zen/Go | `OPENCODE_API_KEY` |
| Kimi For Coding | `KIMI_API_KEY` |
| Xiaomi MiMo (API billing) | `XIAOMI_API_KEY` |
| Xiaomi MiMo Token Plan (China) | `XIAOMI_TOKEN_PLAN_CN_API_KEY` |
| Xiaomi MiMo Token Plan (Amsterdam) | `XIAOMI_TOKEN_PLAN_AMS_API_KEY` |
| Xiaomi MiMo Token Plan (Singapore) | `XIAOMI_TOKEN_PLAN_SGP_API_KEY` |
| GitHub Copilot | `COPILOT_GITHUB_TOKEN` or `GH_TOKEN` or `GITHUB_TOKEN` |

## Model Selection

In interactive mode:
- `/model` — Open model selector
- `Ctrl+L` — Same as `/model`
- `Ctrl+P` / `Shift+Ctrl+P` — Cycle scoped models forward/backward
- `/scoped-models` — Enable/disable models for cycling

Via CLI:
```bash
pi --provider openai --model gpt-4o "Help me refactor"
pi --model openai/gpt-4o "Help me refactor"       # Provider prefix (no --provider needed)
pi --model sonnet:high "Solve this complex problem" # Model with thinking shorthand
pi --models "claude-*,gpt-4o"                      # Limit model cycling
```

Check if model supports features:
```typescript
if (model.input.includes("image")) console.log("Vision supported");
if (model.reasoning) console.log("Thinking/reasoning supported");
```
