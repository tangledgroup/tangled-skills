# Stealth Mode

## Overview

Stealth mode provides built-in anti-detection and tracker blocking capabilities. It is compiled as an optional Cargo feature (`--features stealth`) and activated at runtime with the `--stealth` flag.

## Enabling Stealth

### Build from Source

```bash
cargo build --release --features stealth
```

The `stealth` feature enables anti-detection in obscura-browser and tracker blocking in obscura-net.

### Runtime Activation

```bash
# CLI serve mode
obscura serve --stealth

# CLI fetch mode
obscura fetch https://example.com --stealth --eval "document.title"
```

## Anti-Fingerprinting

Stealth mode randomizes fingerprint vectors per session to prevent browser fingerprinting:

- **GPU spoofing** — Randomized GPU renderer string
- **Screen dimensions** — Realistic randomized screen size
- **Canvas fingerprinting** — Altered canvas rendering output
- **Audio fingerprinting** — Modified audio context data
- **Battery API** — Spoofed battery status

### Navigator Properties

- `navigator.webdriver` set to `undefined` (matches real Chrome behavior)
- Realistic `navigator.userAgentData` with Chrome 145 high-entropy values
- User agent: `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36`

### Event Trust

- `event.isTrusted = true` for dispatched events (prevents detection of automated interactions)

### Property Hiding

- Internal Obscura properties are hidden from `Object.keys(window)` enumeration
- Native function masking: `Function.prototype.toString()` returns `[native code]` for internal functions

## Tracker Blocking

When stealth mode is enabled, Obscura blocks known tracking domains using the Peter Great List (PGL) — approximately 3,520 domains covering:

- Analytics services
- Advertising networks
- Telemetry endpoints
- Fingerprinting scripts

Blocking happens at the HTTP client level — trackers are prevented from loading entirely rather than being loaded and filtered. The blocklist is embedded in the binary via `pgl_domains.txt`.

### How Blocking Works

The `is_blocked()` function checks both exact domain match and parent domain match:

```
tracker.ads.example.com → blocked if "example.com" is in list
sub.tracker.example.com → blocked if "example.com" is in list
```

## TLS Fingerprint Spoofing

With stealth mode, Obscura uses a separate `StealthHttpClient` that spoofs the TLS ClientHello fingerprint to match Chrome's JA3 signature. This prevents server-side detection based on TLS handshake characteristics.

The stealth HTTP client shares the same cookie jar as the regular client, maintaining session state across stealth and non-stealth requests within the same browser context.

## Robots.txt Compliance

Obscura includes a robots.txt parser and cache (`RobotsCache`). When `--obey-robots` is enabled, the browser checks `robots.txt` before fetching pages:

- Parses `User-agent`, `Disallow`, and `Allow` directives
- Matches against Obscura's user agent string
- Caches rules per domain
- Default behavior: allows all paths if no matching rules found
