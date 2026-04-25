# Stealth Mode

> **Source:** Obscura README.md (v0.1.0)
> **Loaded from:** SKILL.md (via progressive disclosure)

Stealth mode is enabled via the `--features stealth` Cargo feature flag during build, or the `--stealth` CLI flag at runtime. It activates anti-fingerprinting and tracker blocking.

## Anti-Fingerprinting

Obscura randomizes browser fingerprints per session to avoid detection:

- **GPU randomization** — Reports plausible GPU strings
- **Screen properties** — Randomized screen resolution and color depth
- **Canvas fingerprinting** — Altered canvas rendering output
- **Audio fingerprinting** — Modified audio context signatures
- **Battery API** — Realistic battery status values
- **`navigator.userAgentData`** — Reports Chrome 145 with high-entropy values
- **`event.isTrusted`** — Set to `true` for dispatched events (matches real browser behavior)
- **Hidden internal properties** — `Object.keys(window)` returns safe output without internal Obscura properties
- **Native function masking** — `Function.prototype.toString()` returns `[native code]` for wrapped functions
- **`navigator.webdriver`** — Set to `undefined` instead of `true` (matches real Chrome)

## Tracker Blocking

- **3,520 domains blocked** by default
- Blocks analytics, ads, telemetry, and fingerprinting scripts
- Prevents trackers from loading entirely (not just ignoring their output)
- Enabled automatically with `--stealth` flag

## Enabling Stealth

### Build-time

```bash
cargo build --release --features stealth
```

This pulls in `wreq` (6.0.0-rc.28) and `wreq-util` (3.0.0-rc.10) as optional dependencies in the `obscura-net` crate, which provide request-level stealth capabilities.

### Runtime

```bash
obscura serve --port 9222 --stealth
obscura fetch https://example.com --stealth
```

The `--stealth` flag propagates through the feature chain: `obscura-cli/stealth` → `obscura-browser/stealth` → `obscura-net/stealth`.
