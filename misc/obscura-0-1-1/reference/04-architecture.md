# Architecture Deep Dive

## Crate Structure

Obscura is a Cargo workspace with six crates, each with a single responsibility:

### obscura-cli

The command-line interface crate. Produces two binaries:

- **`obscura`** — Main CLI with `serve`, `fetch`, and `scrape` subcommands
- **`obscura-worker`** — Lightweight worker process for parallel scraping, communicates via JSON over stdin/stdout

Built on `clap` for argument parsing and `tokio` (current_thread flavor) for async runtime.

### obscura-browser

Core browser logic:

- **`BrowserContext`** — Shared state per browsing session: cookie jar, HTTP client, user agent, proxy, robots cache, stealth flag
- **`Page`** — Individual page with DOM tree, JS runtime, lifecycle state, network events, and intercept channels
- **`LifecycleState`** — Enum tracking page state: `Idle`, `Loading`, `DomContentLoaded`, `Loaded`, `NetworkIdle`, `Failed`
- **`WaitUntil`** — Navigation wait conditions: `Load`, `DomContentLoaded`, `NetworkIdle0`, `NetworkIdle2`

Page navigation flow:

1. HTTP fetch via `ObscuraHttpClient` (or `StealthHttpClient` in stealth mode)
2. HTML5 parsing into `DomTree`
3. JavaScript runtime initialization with DOM binding
4. Script execution (deferred scripts first, then async)
5. Lifecycle state transitions

### obscura-cdp

Chrome DevTools Protocol implementation:

- **`CdpContext`** — Server-wide state: pages list, session-to-page mapping, pending events, preload scripts, fetch intercept state
- **`CdpServer`** — TCP listener that accepts HTTP (`/json/*`) and WebSocket (`/devtools/browser`) connections
- **`dispatch.rs`** — Routes CDP method calls to domain handlers
- **Domain handlers** — One module per CDP domain (Target, Page, Runtime, DOM, Network, Fetch, Input, Storage, LP, Browser)

The server uses a `LocalSet` for single-threaded async execution with channels for message passing between connection handlers and the central processor.

### obscura-dom

HTML5-compliant DOM tree built on `html5ever`:

- **`DomTree`** — Node-based tree with parent/child/sibling relationships
- **CSS selector engine** via `selectors` crate (same engine as Servo/Firefox)
- **HTML serialization** — `inner_html()` and `outer_html()` methods
- **Text content extraction** — Recursive text node collection
- **Tree sink** — html5ever tree builder implementation

### obscura-js

JavaScript runtime powered by Deno Core (which wraps V8):

- **`ObscuraJsRuntime`** — Wraps `deno_core::JsRuntime` with Obscura-specific state
- **`ObscuraState`** — Shared mutable state: DOM reference, URL, title, cookie jar, HTTP client, intercept channel
- **Custom ops** — Rust-to-JS bindings for DOM operations, network requests, and cookie access
- **Module loader** — Custom `deno_core` module loader for fetching external scripts
- **Snapshot** — Pre-compiled V8 snapshot for fast startup (built at compile time)

The JS runtime exposes a full `document` object with DOM API, `window`, `navigator`, `fetch`, `XMLHttpRequest`, and standard web APIs.

### obscura-net

HTTP networking layer:

- **`ObscuraHttpClient`** — HTTP client built on `reqwest` with cookie support, gzip/brotli/deflate decompression, and redirect following
- **`StealthHttpClient`** — TLS-fingerprint-spoofing variant (stealth feature)
- **`CookieJar`** — In-memory cookie storage with domain/path matching
- **`RobotsCache`** — Cached robots.txt parsing per domain
- **`RequestInterceptor`** — Request/response interception hooks
- **URL validation** — Blocks private/internal IPs (loopback, private ranges, link-local) and non-http(s) schemes

## Data Flow: Page Load

```
1. CLI/CDP requests navigation to URL
2. BrowserContext provides HTTP client + cookie jar
3. ObscuraHttpClient fetches HTML (with tracker blocking if stealth)
4. html5ever parses HTML → DomTree
5. Title extracted from <title> or <h1>
6. ObscuraJsRuntime initialized with DOM binding
7. Scripts collected from <script> tags
8. Deferred scripts executed first, then async
9. Lifecycle state advanced: Loading → DomContentLoaded → Loaded → NetworkIdle
10. Page ready for evaluation
```

## Data Flow: CDP Request

```
1. WebSocket client sends JSON-RPC message
2. Server routes to cdp_processor channel
3. dispatch.rs splits method into domain + name
4. Domain handler executes (e.g., Runtime.evaluate)
5. Result serialized as CdpResponse
6. Pending events drained and sent
7. If JS triggered navigation, Page.navigate auto-dispatched
```

## Dependencies

Key Rust dependencies from the workspace:

- `html5ever` 0.29 — HTML5 parsing
- `selectors` 0.26 — CSS selector engine
- `deno_core` — V8 JavaScript runtime
- `tokio` 1 (full features) — Async runtime
- `tokio-tungstenite` 0.26 — WebSocket support
- `reqwest` 0.12 — HTTP client (with cookies, gzip, brotli, deflate, native-tls-vendored)
- `clap` 4 — CLI argument parsing
- `serde` / `serde_json` — Serialization
- `tracing` / `tracing-subscriber` — Structured logging
- `uuid` 1 (v4) — Unique identifiers
- `thiserror` 2 / `anyhow` 1 — Error handling

## Build Requirements

- Rust 1.75+
- First build takes ~5 minutes (V8 compiles from source, cached on subsequent builds)
- Release binary: ~70 MB
- Runtime memory: ~30 MB per process
