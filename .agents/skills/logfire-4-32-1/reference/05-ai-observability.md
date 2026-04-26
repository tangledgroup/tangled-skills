# AI Observability

## Overview

Logfire is an AI-native observability platform. "AI-native" means:

1. **Designed for AI development workflows** — purpose-built features for LLM applications: conversation panels, token tracking, cost monitoring, tool call inspection. Integrates with pydantic-evals for systematic testing. Unlike AI-only tools, Logfire traces your entire application stack via OpenTelemetry.

2. **Designed to be queried by AI** — all observability data exposed via SQL (PostgreSQL-compatible syntax). Coding agents can query production data directly through the MCP server without being limited to predefined dashboards or APIs.

## Quick Start

```python
from openai import OpenAI
import logfire

logfire.configure()
logfire.instrument_openai()

client = OpenAI()
response = client.chat.completions.create(
    model='gpt-5-mini',
    messages=[{'role': 'user', 'content': 'Hello!'}],
)
```

Three lines to instrument AI calls.

## AI-Specific Features

### LLM Panels

Visual inspection of conversations, tool calls, and responses. See the full context of every LLM interaction.

### Token Tracking

See token usage per request and per model. Understand where tokens are consumed.

### Cost Monitoring

Track spending across providers. Set up alerts when costs exceed thresholds.

### Tool Call Inspection

See arguments, responses, and latency for each tool call. Essential for debugging agent behavior.

### Streaming Support

Debug streaming responses with full visibility into each chunk. Logfire creates two spans — one around the initial request and one around the streamed response.

### Multi-turn Conversations

Trace entire conversation flows across multiple turns and tool calls.

### Evaluations

pydantic-evals is a code-first evaluation framework integrating with Logfire. Key difference from other eval tools: it can evaluate any Python function, not just LLM calls. Define evals in Python, run locally or in CI, view results in Logfire.

## Framework Integrations

**Python frameworks with Logfire wrappers** (one function call each):

- Pydantic AI — `logfire.instrument_pydantic_ai()`
- OpenAI — `logfire.instrument_openai()`
- Anthropic — `logfire.instrument_anthropic()`
- LlamaIndex — `logfire.instrument_llamaindex()`
- LiteLLM — `logfire.instrument_litellm()`
- Google GenAI — `logfire.instrument_google_genai()`
- MCP — Model Context Protocol support

**JavaScript/TypeScript**: The Logfire JS SDK supports Node.js, browsers, Next.js, Cloudflare Workers, and Deno. Vercel AI SDK has built-in OTel support.

**Any OTel-Compatible Framework**: If your framework has OpenTelemetry instrumentation, it works with Logfire automatically.

## Why Full-Stack Context Matters

AI-only observability tools only see the LLM layer. When debugging AI applications, you need to answer:

1. What triggered this LLM call?
2. What did the AI access (databases, APIs, tools)?
3. What happened with the response?

For agents specifically: tool execution data comes from application tracing, not the LLM framework. An AI-only tool sees "tool `search_products` was called with `query='red shoes'`, returned 47 results" but has no visibility into the actual database query performance, connection pool state, or data freshness.

With Logfire, you can diagnose both AI problems (agent didn't pass delivery filter) and backend problems (stale data in estimated_delivery column).

## No Lock-In

Logfire is built on OpenTelemetry. Instrumentation is portable — you can configure the SDK to send data to other backends, or use standard OTel libraries directly pointing at Logfire's OTLP endpoint.

## SQL-Based Analysis

Query AI observability data with SQL:

```sql
SELECT
    span_name,
    attributes->>'gen_ai.usage.input_tokens' as input_tokens,
    attributes->>'gen_ai.usage.output_tokens' as output_tokens,
    duration
FROM records
WHERE span_name LIKE 'llm%'
ORDER BY start_timestamp DESC
LIMIT 100
```

## Sensitive Data in LLM Messages

Scrubbing is **disabled** for LLM message attributes (`gen_ai.input.messages`, `gen_ai.output.messages`, `pydantic_ai.all_messages`) because:
- False positives are common (LLMs produce words like "password" in normal conversation)
- Regex detection can't catch sensitive data without keyword patterns

If LLM interactions might contain sensitive data, exclude message content entirely:

```python
logfire.instrument_pydantic_ai(include_content=False)
```

This still logs spans for timing and metadata, but excludes prompts, completions, and tool call arguments/responses.
