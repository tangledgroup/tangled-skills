# Node.js Compatibility

Bun aims for full compatibility with Node.js built-in modules and globals. Popular frameworks like Next.js, Express, and millions of npm packages work with Bun. Thousands of tests from the Node.js test suite are run before every release.

If a package works in Node.js but not in Bun, it is considered a bug in Bun. Report issues at https://bun.com/issues.

## Built-in Module Status

The following reflects compatibility with **Node.js v23**:

### Fully Implemented (🟢)

- `node:assert` — Fully implemented
- `node:buffer` — Fully implemented
- `node:console` — Fully implemented
- `node:dgram` — Fully implemented (>90% of Node.js test suite passes)
- `node:diagnostics_channel` — Fully implemented
- `node:dns` — Fully implemented (>90%)
- `node:events` — Fully implemented (100%, `EventEmitterAsyncResource` uses `AsyncResource`)
- `node:fs` — Fully implemented (92% of test suite)
- `node:http` — Fully implemented (outgoing client request body is buffered, not streamed)
- `node:https` — APIs implemented (`Agent` not always used yet)
- `node:os` — Fully implemented (100%)
- `node:path` — Fully implemented (100%)
- `node:punycode` — Fully implemented (100%, deprecated by Node.js)
- `node:querystring` — Fully implemented (100%, deprecated by Node.js)
- `node:readline` — Fully implemented
- `node:stream` — Fully implemented
- `node:string_decoder` — Fully implemented (100%)
- `node:timers` — Recommended to use global `setTimeout` instead
- `node:tty` — Fully implemented
- `node:url` — Fully implemented
- `node:zlib` — Fully implemented (98%)

### Partially Implemented (🟡)

- `node:async_hooks` — `AsyncLocalStorage` and `AsyncResource` implemented. v8 promise hooks not called (usage strongly discouraged by Node.js).

## Globals

Bun implements both Web-standard and Node.js globals:

**Web Standard**: `AbortController`, `AbortSignal`, `Blob`, `ByteLengthQueuingStrategy`, `CountQueuingStrategy`, `Crypto`, `crypto`, `CustomEvent`, `Event`, `EventTarget`, `fetch`, `FormData`, `Headers`, `JSON`, `MessageEvent`, `performance`, `queueMicrotask()`, `ReadableStream`, `ReadableByteStreamController`, `reportError`, `Request`, `Response`, `setImmediate()`, `setInterval()`, `setTimeout()`, `ShadowRealm`, `SubtleCrypto`, `TextDecoder`, `TextEncoder`, `TransformStream`, `URL`, `URLSearchParams`, `WebAssembly`, `WritableStream`, `DOMException`.

**Node.js**: `Buffer`, `__dirname`, `__filename`, `global`, `globalThis` (aliases to `global`), `module`, `exports`, `process`, `require()`, `alert()`, `confirm()`, `prompt()` (for CLI tools).

**Bun-specific**: `Bun` global object, `BuildMessage`, `ResolveMessage`, `HTMLRewriter`.

## Migration from Node.js

### Common Patterns

Most Node.js code works without changes. Key differences to be aware of:

1. **`fetch` is global** — No need to import from `node-fetch` or use `undici`
2. **TypeScript out of the box** — No `ts-node` or `tsx` needed
3. **Web APIs native** — `WebSocket`, `ReadableStream`, `TextEncoder` available globally
4. **Faster startup** — Scripts start ~4x faster
5. **Different JS engine** — JavaScriptCore vs V8; some edge cases may differ

### Things That May Differ

- Some V8-specific globals (`v8` module) are not available
- `--experimental-*` flags from Node.js don't apply
- Native addons compiled specifically for V8 ABI may not work
- Some `node:inspector` features may differ
- Cluster mode (`node:cluster`) is not implemented — use Workers instead

### Using node_modules

Existing `node_modules` directories work with Bun. You can run `bun install` in any existing Node.js project to regenerate the lockfile and potentially speed up future installs.
