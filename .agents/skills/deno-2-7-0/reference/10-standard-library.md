# Standard Library (@std)

## Overview

The Deno standard library is published as modular JSR packages under the `@std` scope. Each package is independently versioned and can be imported individually.

## Core Packages

**@std/assert** — Assertion functions for testing

```typescript
import { assertEquals, assertThrows } from "jsr:@std/assert";
assertEquals(actual, expected);
```

**@std/async** — Async utilities (delay, debounce, pool)

```typescript
import { delay, withTimeout } from "jsr:@std/async";
await delay(100);
```

**@std/bytes** — Uint8Array manipulation

```typescript
import { concat, copy } from "jsr:@std/bytes";
const result = concat([new Uint8Array([1, 2]), new Uint8Array([3, 4])]);
```

**@std/collections** — Pure functions for arrays and objects

```typescript
import { groupBy, uniqueBy } from "jsr:@std/collections";
const grouped = groupBy(items, (item) => item.category);
```

**@std/crypto** — Extensions to Web Crypto API

```typescript
import { timingSafeEqual } from "jsr:@std/crypto";
```

**@std/csv** — Reading and writing CSV files

```typescript
import { parse } from "jsr:@std/csv";
const records = await parse(csvString);
```

**@std/data-structures** — Red-black trees, binary heaps

```typescript
import { BinaryHeap } from "jsr:@std/data-structures";
```

**@std/dotenv** — Load .env files (unstable)

```typescript
import { load } from "jsr:@std/dotenv";
await load();
```

**@std/encoding** — Hex, base64, varint encoding/decoding

```typescript
import { encodeBase64, decodeBase64 } from "jsr:@std/encoding";
const encoded = encodeBase64(new TextEncoder().encode("hello"));
```

**@std/expect** — Jest-compatible expect assertions

```typescript
import { expect } from "jsr:@std/expect";
expect(value).toBe(expected);
```

**@std/fmt** — Formatting utilities (colors, printf, durations)

```typescript
import { red, green } from "jsr:@std/fmt/colors";
console.log(red("Error"), green("Success"));
```

**@std/front-matter** — Extract front matter from strings

```typescript
import { parse } from "jsr:@std/front-matter/yaml";
const { attrs, body } = parse(contentWithFrontMatter);
```

**@std/fs** — File system helpers

```typescript
import { walk, copy, emptyDir, exists } from "jsr:@std/fs";
for await (const entry of walk("./src")) {
  console.log(entry.path);
}
```

**@std/html** — HTML escaping/unescaping

```typescript
import { escape } from "jsr:@std/html";
const safe = escape("<script>alert('xss')</script>");
```

**@std/http** — HTTP server utilities

```typescript
import { serveDir, status } from "jsr:@std/http";
```

**@std/json** — Streaming JSON parsing

```typescript
import { parse } from "jsr:@std/json";
```

**@std/jsonc** — JSONC (JSON with comments) parsing

```typescript
import { parse } from "jsr:@std/jsonc";
```

**@std/log** — Customizable logger framework (unstable)

```typescript
import { setupLogging, getLogger } from "jsr:@std/log";
```

**@std/media-types** — MIME type utilities

```typescript
import { contentType } from "jsr:@std/media-types";
console.log(contentType("file.html")); // "text/html"
```

**@std/msgpack** — MessagePack encoding/decoding

```typescript
import { encode, decode } from "jsr:@std/msgpack";
```

**@std/net** — Network utilities (finding available ports)

```typescript
import { getAvailablePort } from "jsr:@std/net";
const port = await getAvailablePort(8000);
```

**@std/path** — Path manipulation utilities

```typescript
import { join, extname, basename } from "jsr:@std/path";
const file = join("src", "module.ts");
```

**@std/regexp** — RegExp utilities

```typescript
import { escape } from "jsr:@std/regexp";
```

**@std/semver** — Semantic version parsing and comparison

```typescript
import { parse, greaterThan } from "jsr:@std/semver";
```

**@std/streams** — Web Streams API utilities

```typescript
import { toLines, toText } from "jsr:@std/streams";
```

**@std/testing** — Testing tools (snapshots, BDD, time mocking)

```typescript
import { assertSnapshot } from "jsr:@std/testing/snapshot";
import { describe, it } from "jsr:@std/testing/bdd";
import { FakeTime } from "jsr:@std/testing/time";
```

**@std/text** — Text processing utilities

```typescript
import { toCamelCase, toKebabCase, slugify } from "jsr:@std/text";
```

**@std/toml** — TOML parsing and serialization

```typescript
import { parse } from "jsr:@std/toml";
```

**@std/ulid** — ULID generation

```typescript
import { ulid } from "jsr:@std/ulid";
```

**@std/uuid** — UUID generation and validation

```typescript
import { generateUUID, validateUUID } from "jsr:@std/uuid";
```

**@std/yaml** — YAML parsing and serialization

```typescript
import { parse, stringify } from "jsr:@std/yaml";
```

## Import Patterns

Pin versions for reproducibility:

```typescript
import { assertEquals } from "jsr:@std/assert@1.0.8";
```

Or use caret ranges in deno.json imports:

```jsonc
{
  "imports": {
    "@std/assert": "jsr:@std/assert@^1.0.0"
  }
}
```
