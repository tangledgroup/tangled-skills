# Built-in APIs & Utilities

Bun provides numerous built-in utilities that eliminate the need for npm packages. This guide covers hashing, glob patterns, semver, TOML, YAML, JSON5, HTML rewriting, and more.

## Hashing & Cryptography

### Password Hashing

```typescript
// bcrypt (built-in, no npm package needed)
const { hash, verify } = await import("bcrypt");

const password = "supersecret";
const hash = await hash(password, 10);
const isValid = await verify(password, hash);

console.log(isValid);  // true
```

### Hash Functions

```typescript
// SHA-256
const encoder = new TextEncoder();
const data = encoder.encode("hello world");
const hashBuffer = await crypto.subtle.digest("SHA-256", data);
const hashArray = Array.from(new Uint8Array(hashBuffer));
const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

console.log(hashHex);  // b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
```

### Bun's Hash API

```typescript
// Faster native hashing
const sha256 = Bun.hash("hello world", "sha256");
console.log(sha256);  // Hex string

// Multiple algorithms supported
const md5 = Bun.hash("data", "md5");
const sha1 = Bun.hash("data", "sha1");
const sha512 = Bun.hash("data", "sha512");
```

### HMAC

```typescript
// HMAC-SHA256
const key = "secret-key";
const message = "data to sign";

const hmac = await crypto.subtle.importKey(
  "raw",
  new TextEncoder().encode(key),
  { name: "HMAC", hash: "SHA-256" },
  false,
  ["sign"]
);

const signature = await crypto.subtle.sign(
  "HMAC",
  hmac,
  new TextEncoder().encode(message)
);

console.log(Array.from(new Uint8Array(signature)).map(b => b.toString(16).padStart(2, '0')).join(''));
```

## Glob Patterns

### File Matching

```typescript
// Find all TypeScript files
const tsFiles = Bun.glob("./src/**/*.ts");
for (const file of tsFiles) {
  console.log(file.path);
}

// Find test files
const testFiles = Bun.glob("./tests/**/*.{test,spec}.ts");

// Exclude node_modules
const sourceFiles = Bun.glob("./src/**/*", { exclude: ["**/node_modules/**"] });
```

### Glob Options

```typescript
const files = Bun.glob("./path/*", {
  // Return absolute paths
  absolute: true,
  
  // Include directories in results
  includeDirs: false,
  
  // Follow symbolic links
  followSymlinks: true,
  
  // Patterns to exclude
  exclude: ["**/node_modules/**", "**/.git/**"],
  
  // Case insensitive matching
  caseSensitive: true,
});
```

### Common Patterns

```typescript
// All JavaScript files
Bun.glob("**/*.js");

// TypeScript files (excluding tests)
Bun.glob("**/*.ts", { exclude: ["**/*.test.ts"] });

// Images in assets folder
Bun.glob("./assets/**/*.{png,jpg,gif,svg}");

// Everything except git and node_modules
Bun.glob("**/*", { exclude: ["**/.git/**", "**/node_modules/**"] });

// Files modified in last 24 hours (custom filtering)
const recentFiles = Bun.glob("./src/**/*").filter(f => {
  const stat = Bun.stat(f.path);
  return Date.now() - stat.mtime.getTime() < 24 * 60 * 60 * 1000;
});
```

## Semver (Semantic Versioning)

### Version Parsing

```typescript
// Parse version string
const v1 = Bun.semver.parse("1.2.3");
console.log(v1.major);  // 1
console.log(v1.minor);  // 2
console.log(v1.patch);  // 3

// Parse with prerelease
const v2 = Bun.semver.parse("2.0.0-beta.1");
console.log(v2.prerelease);  // ["beta", "1"]
```

### Version Comparison

```typescript
const v1 = Bun.semver.parse("1.2.3");
const v2 = Bun.semver.parse("2.0.0");

// Compare versions
console.log(Bun.semver.compare(v1, v2));  // -1 (v1 < v2)
console.log(Bun.semver.gt(v1, v2));       // false
console.log(Bun.semver.lt(v1, v2));       // true
console.log(Bun.semver.eq(v1, v2));       // false
console.log(Bun.semver.gte(v1, v2));      // false
console.log(Bun.semver.lte(v1, v2));      // true
```

### Range Matching

```typescript
// Check if version satisfies range
console.log(Bun.semver.satisfies("1.2.3", ">=1.0.0 <2.0.0"));  // true
console.log(Bun.semver.satisfies("2.0.0", "^1.2.3"));          // false
console.log(Bun.semver.satisfies("1.5.0", "^1.2.3"));          // true
console.log(Bun.semver.satisfies("1.2.5", "~1.2.3"));          // true

// Common range operators
// ^1.2.3  >=1.2.3, <2.0.0 (compatible with 1.2.3)
// ~1.2.3  >=1.2.3, <1.3.0 (approximately equivalent)
// >=1.0.0 Greater than or equal to 1.0.0
// 1.x     Any 1.x.x version
// *       Any version
```

### Version Manipulation

```typescript
const v = Bun.semver.parse("1.2.3");

// Increment version
console.log(Bun.semver.increment(v, "major"));    // 2.0.0
console.log(Bun.semver.increment(v, "minor"));    // 1.3.0
console.log(Bun.semver.increment(v, "patch"));    // 1.2.4
console.log(Bun.semver.increment(v, "prerelease"));// 1.2.4-0
```

## TOML Support

### Reading TOML

```typescript
// Import TOML file directly
import config from "config.toml";

console.log(config.database.host);  // Access properties
```

### Parse TOML String

```typescript
const tomlString = `
title = "Bun Config"

[database]
host = "localhost"
port = 5432
enabled = true

[server]
port = 3000
hosts = ["api.example.com", "www.example.com"]
`;

const config = Bun.toml.parse(tomlString);
console.log(config.title);        // "Bun Config"
console.log(config.database.port); // 5432
console.log(config.server.hosts);  // ["api.example.com", "www.example.com"]
```

### Writing TOML

```typescript
const config = {
  app: {
    name: "MyApp",
    version: "1.0.0",
  },
  database: {
    host: "localhost",
    port: 5432,
  },
};

const tomlString = Bun.toml.stringify(config);
console.log(tomlString);
// Output:
// [app]
// name = "MyApp"
// version = "1.0.0"
//
// [database]
// host = "localhost"
// port = 5432
```

## YAML Support

### Reading YAML

```typescript
// Import YAML file directly
import config from "config.yaml";

console.log(config.database.host);  // Access properties
```

### Parse YAML String

```typescript
const yamlString = `
title: Bun Config
database:
  host: localhost
  port: 5432
  enabled: true
server:
  port: 3000
  hosts:
    - api.example.com
    - www.example.com
`;

const config = Bun.yaml.parse(yamlString);
console.log(config.title);        // "Bun Config"
console.log(config.database.port); // 5432
console.log(config.server.hosts);  // ["api.example.com", "www.example.com"]
```

### Writing YAML

```typescript
const config = {
  app: {
    name: "MyApp",
    version: "1.0.0",
  },
  features: [
    "authentication",
    "authorization",
    "logging",
  ],
};

const yamlString = Bun.yaml.stringify(config);
console.log(yamlString);
// Output:
// app:
//   name: MyApp
//   version: '1.0.0'
// features:
//   - authentication
//   - authorization
//   - logging
```

## JSON5 Support

JSON5 allows comments, trailing commas, and other JavaScript-like features.

### Parse JSON5

```typescript
const json5String = `{
  // Comments are allowed
  name: "MyApp",  // Trailing commas OK
  features: [
    "auth",
    "logging",
  ],
  unquoted: true,  // Unquoted keys
  "nested-object": {
    value: 42,
  },
}`;

const data = Bun.json5.parse(json5String);
console.log(data.name);  // "MyApp"
```

### Stringify to JSON5

```typescript
const data = {
  name: "MyApp",
  version: "1.0.0",
};

const json5 = Bun.json5.stringify(data, { indent: 2 });
console.log(json5);
```

## JSONL (JSON Lines)

JSONL is a format where each line is a separate JSON object.

### Parse JSONL

```typescript
const jsonlString = `{"id": 1, "name": "Alice"}
{"id": 2, "name": "Bob"}
{"id": 3, "name": "Charlie"}`;

const objects = Bun.jsonl.parse(jsonlString);
console.log(objects);  // [{id: 1, name: "Alice"}, ...]
```

### Stringify to JSONL

```typescript
const data = [
  { id: 1, name: "Alice" },
  { id: 2, name: "Bob" },
  { id: 3, name: "Charlie" },
];

const jsonl = Bun.jsonl.stringify(data);
console.log(jsonl);
// Output:
// {"id":1,"name":"Alice"}
// {"id":2,"name":"Bob"}
// {"id":3,"name":"Charlie"}
```

## Markdown Support

### Parse Markdown

```typescript
const markdown = `# Hello World

This is a **bold** statement and this is *italic*.

- Item 1
- Item 2
- Item 3`;

const html = Bun.markdown.parse(markdown);
console.log(html);
// Output: <h1>Hello World</h1><p>...</p><ul>...</ul>
```

## HTML Rewriter

Stream-based HTML parsing and modification without loading entire document into memory.

### Basic Usage

```typescript
async function rewriteHTML(url: string) {
  const response = await fetch(url);
  const stream = response.body!
    .pipeThrough(new Bun.HTMLRewriterStream())
    .pipeThrough(new TextEncoderStream());
  
  for await (const chunk of stream) {
    process.stdout.write(chunk);
  }
}
```

### Extract Links

```typescript
async function extractLinks(url: string): Promise<string[]> {
  const links: string[] = [];
  
  const response = await fetch(url);
  const rewriter = new Bun.HTMLRewriterStream({
    visitor: {
      element(name, attributes, isClosing, isSelfClosing) {
        if (name === "a" && !isClosing) {
          const href = attributes.find(a => a.name === "href")?.value;
          if (href) {
            links.push(href);
          }
        }
      },
    },
  });
  
  await response.body!.pipeThrough(rewriter).pipeTo(new WritableStream());
  return links;
}
```

### Modify Attributes

```typescript
async function addRelNoopener(url: string) {
  const response = await fetch(url);
  
  const rewriter = new Bun.HTMLRewriterStream({
    visitor: {
      element(name, attributes, isClosing, isSelfClosing) {
        if (name === "a" && !isClosing) {
          // Add rel="noopener noreferrer" to external links
          const href = attributes.find(a => a.name === "href")?.value;
          if (href && href.startsWith("https://")) {
            return [
              ...attributes,
              { name: "rel", value: "noopener noreferrer" },
            ];
          }
        }
      },
    },
  });
  
  return new Response(response.body!.pipeThrough(rewriter), {
    headers: response.headers,
  });
}
```

### Extract Social Meta Tags

```typescript
async function extractSocialMeta(url: string) {
  const meta: Record<string, string> = {};
  
  const response = await fetch(url);
  const rewriter = new Bun.HTMLRewriterStream({
    visitor: {
      element(name, attributes, isClosing) {
        if (name === "meta" && !isClosing) {
          const property = attributes.find(a => a.name === "property")?.value;
          const name = attributes.find(a => a.name === "name")?.value;
          const content = attributes.find(a => a.name === "content")?.value;
          
          if (property && content) {
            meta[property] = content;
          }
          if (name && content) {
            meta[name] = content;
          }
        }
      },
    },
  });
  
  await response.body!.pipeThrough(rewriter).pipeTo(new WritableStream());
  return meta;
}

// Usage
const meta = await extractSocialMeta("https://example.com");
console.log(meta["og:title"]);    // Page title
console.log(meta["og:image"]);    // Open Graph image
console.log(meta["twitter:card"]);// Twitter card type
```

## Color Manipulation

### Parse Colors

```typescript
// Parse various color formats
const red1 = Bun.color.parse("#ff0000");
const red2 = Bun.color.parse("rgb(255, 0, 0)");
const red3 = Bun.color.parse("red");

console.log(red1.r);  // 255
console.log(red1.g);  // 0
console.log(red1.b);  // 255
```

### Convert Colors

```typescript
const color = Bun.color.parse("#ff0000");

// Convert to different formats
console.log(color.toHex());        // "#ff0000"
console.log(color.toRGB());        // "rgb(255, 0, 0)"
console.log(color.toRGBA(1.0));    // "rgba(255, 0, 0, 1)"
console.log(color.toHSL());        // "hsl(0, 100%, 50%)"
```

### Manipulate Colors

```typescript
const color = Bun.color.parse("#ff0000");

// Lighten/darken
const lighter = color.lighten(0.2);  // 20% lighter
const darker = color.darken(0.2);    // 20% darker

// Change opacity
const transparent = color.alpha(0.5);  // 50% opacity

// Get grayscale
const gray = color.grayscale();

// Get complementary color
const complement = color.complement();
```

## Utility Functions

### Console Utilities

```typescript
// Enhanced console output
Bun.console.log("Regular log");
Bun.console.error("Error message");
Bun.console.warn("Warning");
Bun.console.info("Information");
Bun.console.debug("Debug info");

// Table output
const data = [
  { name: "Alice", age: 30, city: "NYC" },
  { name: "Bob", age: 25, city: "LA" },
  { name: "Charlie", age: 35, city: "SF" },
];

Bun.console.table(data);
```

### Sleep Utility

```typescript
// Async sleep (better than setTimeout)
await Bun.sleep(1000);  // Sleep for 1 second
await Bun.sleep(500);   // Sleep for 500 milliseconds

// Use in loops
for (let i = 0; i < 5; i++) {
  console.log(i);
  await Bun.sleep(1000);
}
```

### CSRF Token Generation

```typescript
// Generate CSRF token
const token = Bun.csrf.generate();
console.log(token);  // Random secure token

// Verify CSRF token
const isValid = Bun.csrf.verify(token, storedToken);
console.log(isValid);  // true or false
```

### Secrets Management

```typescript
// Generate secure random bytes
const secret = Bun.secrets.generate(32);  // 32 bytes
console.log(Buffer.from(secret).toString("hex"));

// Generate secure token
const token = Bun.secrets.token(64);  // 64 character token
console.log(token);
```

## Performance Tips

1. **Use native APIs** instead of npm packages when available
2. **Stream large files** with HTMLRewriter instead of loading into memory
3. **Parse formats directly** (TOML, YAML) without external dependencies
4. **Use Bun.hash** for faster hashing than crypto.subtle
5. **Batch glob operations** instead of multiple file system calls

## Comparison with npm Packages

| Task | npm Package | Bun Built-in |
|------|-------------|--------------|
| Hashing | `bcrypt`, `crypto` | `Bun.hash`, `bcrypt` |
| Glob patterns | `glob`, `fast-glob` | `Bun.glob` |
| Semver | `semver` | `Bun.semver` |
| TOML | `toml`, `@iarna/toml` | `Bun.toml` |
| YAML | `js-yaml`, `yaml` | `Bun.yaml` |
| JSON5 | `json5` | `Bun.json5` |
| JSONL | Custom implementation | `Bun.jsonl` |
| Markdown | `marked`, `remark` | `Bun.markdown` |
| HTML parsing | `cheerio`, `jsdom` | `Bun.HTMLRewriterStream` |
| Color manipulation | `color`, `tinycolor2` | `Bun.color` |
| CSRF tokens | `csurf`, `crypto` | `Bun.csrf` |

## Related Documentation

- [Runtime Basics](references/01-runtime-basics.md) - Core runtime features
- [Data Storage](references/07-data-storage.md) - File I/O and databases
- [HTTP Server](references/06-http-server.md) - Streaming with HTMLRewriter
- [Process & System](references/12-process-system.md) - Environment and utilities