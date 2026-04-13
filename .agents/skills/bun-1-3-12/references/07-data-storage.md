# Bun Data & Storage APIs

Bun provides native, high-performance APIs for file I/O, SQLite, Redis, S3, and streaming without requiring external packages. These built-in APIs are significantly faster than npm alternatives.

## File I/O

### Reading Files

```typescript
// Read as string (UTF-8)
const content = await Bun.file("./path/to/file.txt").text();

// Read as JSON
const data = await Bun.file("./config.json").json();

// Read as ArrayBuffer
const bytes = await Bun.file("./binary.bin").arrayBuffer();

// Read as Blob
const blob = await Bun.file("./image.png");

// Synchronous read (use sparingly)
const syncContent = Bun.read("./file.txt", "utf-8");
```

### Writing Files

```typescript
// Write string
Bun.write("./output.txt", "Hello, world!");

// Write JSON (auto-stringifies)
Bun.write("./data.json", { key: "value" });

// Write binary data
Bun.write("./binary.bin", new Uint8Array([1, 2, 3, 4]));

// Append to file
Bun.append("./log.txt", "New log entry\n");

// Synchronous write
Bun.writeSync("./file.txt", "Content");
```

### File Operations

```typescript
// Check if file exists
if (Bun.exists("./path/to/file")) {
  console.log("File exists");
}

// Get file info
const stat = Bun.stat("./file.txt");
console.log(stat.size);      // File size in bytes
console.log(stat.mtime);     // Last modified time
console.log(stat.isFile());  // true if regular file
console.log(stat.isDirectory());  // true if directory

// Copy file
Bun.copy("./source.txt", "./destination.txt");

// Move/rename file
Bun.move("./old.txt", "./new.txt");

// Delete file
Bun.remove("./file.txt");

// Create directory
Bun.mkdir("./new-directory");
Bun.mkdir("./nested/dir", { recursive: true });

// List directory contents
const entries = Bun.glob("./directory/*");
for (const entry of entries) {
  console.log(entry.path);
}
```

### File Streams

```typescript
// Read large file as stream
const file = Bun.file("./large-file.txt");
const reader = file.stream().getReader();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  // Process chunk
  console.log(new TextDecoder().decode(value));
}

// Write as stream
const writable = Bun.writeStream("./output.txt");
const writer = writable.getWriter();

writer.write(new TextEncoder().encode("Chunk 1\n"));
writer.write(new TextEncoder().encode("Chunk 2\n"));
await writer.close();
```

## SQLite

Bun has a built-in SQLite client that's significantly faster than better-sqlite3 or sql.js.

### Basic Usage

```typescript
// Open database (creates if doesn't exist)
const db = new Bun.SQLiteDatabase("./database.sqlite");

// Execute SQL
db.query("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)").run();

// Insert data
db.query("INSERT INTO users (name, email) VALUES (?, ?)").run("Alice", "alice@example.com");
db.query("INSERT INTO users (name, email) VALUES (?, ?)").run("Bob", "bob@example.com");

// Query data
const users = db.query("SELECT * FROM users").all() as { id: number; name: string; email: string }[];
console.log(users);

// Get single row
const user = db.query("SELECT * FROM users WHERE id = ?").get(1) as { id: number; name: string };
console.log(user.name);

// Close database
db.close();
```

### Prepared Statements

```typescript
// Prepare statement for reuse
const insertUser = db.prepare("INSERT INTO users (name, email) VALUES (?, ?)");
const getUser = db.prepare("SELECT * FROM users WHERE id = ?");

// Execute multiple times
insertUser.run("Charlie", "charlie@example.com");
insertUser.run("Diana", "diana@example.com");

// Get specific user
const charlie = getUser.get(3);
console.log(charlie.name);
```

### Transactions

```typescript
// Begin transaction
const tx = db.transaction();

try {
  tx.query("INSERT INTO users (name, email) VALUES (?, ?)").run("Eve", "eve@example.com");
  tx.query("INSERT INTO users (name, email) VALUES (?, ?)").run("Frank", "frank@example.com");
  
  // Commit transaction
  tx.commit();
  console.log("Transaction committed");
} catch (error) {
  // Rollback on error
  tx.rollback();
  console.log("Transaction rolled back:", error);
}
```

### Bulk Operations

```typescript
// Insert multiple rows efficiently
const users = [
  ["Alice", "alice@example.com"],
  ["Bob", "bob@example.com"],
  ["Charlie", "charlie@example.com"],
];

const insert = db.prepare("INSERT INTO users (name, email) VALUES (?, ?)");

db.transaction(() => {
  for (const [name, email] of users) {
    insert.run(name, email);
  }
})();
```

### Raw Mode

```typescript
// Get raw SQLite data types
const result = db.query("SELECT * FROM users").raw();
console.log(result);  // Raw array format

// Use for better performance with large datasets
```

## Redis

Bun includes a native Redis client that's faster than ioredis or redis packages.

### Connection

```typescript
// Connect to Redis
const redis = new Bun.Redis("redis://localhost:6379");

// With authentication
const authRedis = new Bun.Redis("redis://:password@localhost:6379");

// To specific database
const db5 = new Bun.Redis("redis://localhost:6379/5");

// Using options object
const redisWithOptions = new Bun.Redis({
  host: "localhost",
  port: 6379,
  password: "password",
  db: 0,
});
```

### Basic Commands

```typescript
// Strings
await redis.set("key", "value");
const value = await redis.get("key");  // "value"
await redis.del("key");

// Expiration
await redis.set("temp", "value", { ex: 60 });  // Expires in 60 seconds
await redis.expire("key", 3600);  // Set expiry to 1 hour

// Hashes
await redis.hset("user:1", "name", "Alice");
await redis.hset("user:1", "email", "alice@example.com");
const name = await redis.hget("user:1", "name");  // "Alice"
const user = await redis.hgetall("user:1");  // { name: "Alice", email: "alice@example.com" }

// Lists
await redis.lpush("queue", "task1");
await redis.rpush("queue", "task2");
const item = await redis.lpop("queue");  // "task1"
const queue = await redis.lrange("queue", 0, -1);  // ["task2"]

// Sets
await redis.sadd("tags", "javascript");
await redis.sadd("tags", "typescript");
const tags = await redis.smembers("tags");  // ["javascript", "typescript"]

// Sorted sets
await redis.zadd("scores", { Alice: 100, Bob: 85, Charlie: 90 });
const rank = await redis.zrank("scores", "Alice");  // 2 (higher score = lower rank)
const top3 = await redis.zrevrange("scores", 0, 2);  // ["Alice", "Charlie", "Bob"]
```

### Pub/Sub

```typescript
// Subscribe to channel
const subscriber = await redis.subscribe("chat");

for await (const message of subscriber) {
  console.log("Received:", message.channel, message.data);
}

// Publish message
await redis.publish("chat", "Hello, everyone!");
```

### Pipelining

```typescript
// Send multiple commands at once (faster than individual calls)
const results = await redis.pipeline((pipe) => {
  pipe.set("key1", "value1");
  pipe.set("key2", "value2");
  pipe.get("key1");
  pipe.get("key2");
});

console.log(results);  // ["OK", "OK", "value1", "value2"]
```

### Transactions (MULTI/EXEC)

```typescript
// Atomic operations
const results = await redis.transaction((tx) => {
  tx.incr("counter");
  tx.get("counter");
  tx.hset("stats", "last_update", Date.now());
});

console.log(results);
```

## S3 / Object Storage

Bun provides native S3-compatible storage client.

### Configuration

```typescript
const s3 = new Bun.S3Client({
  region: "us-east-1",
  endpoint: "https://s3.amazonaws.com",  // Or custom endpoint for MinIO, etc.
  
  // Authentication (optional for public buckets)
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
});

// For MinIO or other S3-compatible services
const minio = new Bun.S3Client({
  region: "us-east-1",
  endpoint: "http://localhost:9000",
  accessKeyId: "minioadmin",
  secretAccessKey: "minioadmin",
});
```

### Bucket Operations

```typescript
// Create bucket
await s3.createBucket("my-bucket");

// Check if bucket exists
const exists = await s3.bucketExists("my-bucket");

// Delete bucket (must be empty)
await s3.deleteBucket("my-bucket");

// List buckets
const buckets = await s3.listBuckets();
```

### Object Operations

```typescript
// Upload file
await s3.putObject("my-bucket", "path/to/file.txt", "File content");

// Upload from file
await s3.putObjectFromPath("my-bucket", "remote/path.txt", "./local/file.txt");

// Upload with metadata
await s3.putObject("my-bucket", "image.png", imageBytes, {
  contentType: "image/png",
  metadata: {
    "author": "John Doe",
    "created": new Date().toISOString(),
  },
});

// Download file
const object = await s3.getObject("my-bucket", "path/to/file.txt");
const content = await object.text();

// Download to file
await s3.downloadToPath("my-bucket", "remote/path.txt", "./local/file.txt");

// Delete object
await s3.deleteObject("my-bucket", "path/to/file.txt");

// Check if object exists
const exists = await s3.objectExists("my-bucket", "path/to/file.txt");
```

### Listing Objects

```typescript
// List all objects in bucket
const objects = await s3.listObjects("my-bucket");
for (const obj of objects) {
  console.log(obj.key, obj.size, obj.lastModified);
}

// List with prefix
const images = await s3.listObjects("my-bucket", { prefix: "images/" });

// List with delimiter (group by folder)
const grouped = await s3.listObjects("my-bucket", { delimiter: "/" });
console.log(grouped.commonPrefixes);  // ["images/", "docs/"]
```

### Presigned URLs

```typescript
// Generate presigned GET URL (expires in 1 hour)
const downloadUrl = await s3.presignedGet("my-bucket", "private/file.txt", {
  expires: 3600,  // seconds
});

// Generate presigned PUT URL
const uploadUrl = await s3.presignedPut("my-bucket", "uploads/file.txt", {
  expires: 1800,
  contentType: "application/pdf",
});
```

## Streams

### Readable Streams

```typescript
// Create readable stream from generator
async function* generateNumbers() {
  for (let i = 0; i < 10; i++) {
    yield i;
    await new Promise(r => setTimeout(r, 100));
  }
}

const stream = new ReadableStream({
  start(controller) {
    generateNumbers().forEach(value => {
      controller.enqueue(value);
    });
  },
});

// Consume stream
const reader = stream.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  console.log(value);
}
```

### Transform Streams

```typescript
// Create transform stream
const upperCaseStream = new TransformStream({
  transform(chunk, controller) {
    controller.enqueue(chunk.toUpperCase());
  },
});

// Pipe through transform
const input = "hello world";
const output = await (
  new ReadableStream({
    start(controller) {
      controller.enqueue(input);
      controller.close();
    },
  })
  .pipeThrough(upperCaseStream)
  .pipeTo(new WritableStream({
    write(chunk) {
      console.log(chunk);  // "HELLO WORLD"
    },
  }))
);
```

### File Streaming

```typescript
// Stream large file without loading into memory
const file = Bun.file("./large-video.mp4");

Bun.serve({
  port: 3000,
  fetch(req) {
    const url = new URL(req.url);
    
    if (url.pathname === "/download") {
      return new Response(file.stream(), {
        headers: {
          "Content-Type": "video/mp4",
          "Content-Disposition": 'attachment; filename="video.mp4"',
        },
      });
    }
    
    return new Response("Not found", { status: 404 });
  },
});
```

## Binary Data

### Buffer Operations

```typescript
// Create buffer
const buf1 = Buffer.from("hello");
const buf2 = Buffer.alloc(10);  // Zero-filled
const buf3 = Buffer.allocUnsafe(10);  // Faster, not zeroed

// Read/write
buf2[0] = 65;  // 'A'
console.log(buf2[0]);  // 65

// Convert between formats
const bytes = new Uint8Array([72, 101, 108, 108, 111]);  // "Hello"
const str = Buffer.from(bytes).toString();  // "Hello"

// Slice buffer
const slice = buf1.slice(0, 3);  // "hel"

// Concatenate buffers
const combined = Buffer.concat([buf1, buf2]);
```

### Typed Arrays

```typescript
// Different array types
const uint8 = new Uint8Array(10);      // 8-bit unsigned integers
const int32 = new Int32Array(5);       // 32-bit signed integers
const float32 = new Float32Array(3);   // 32-bit floats
const float64 = new Float64Array(2);   // 64-bit floats

// Shared memory (for workers)
const shared = new SharedArrayBuffer(1024);
const view = new Uint8Array(shared);
```

### Text Encoding

```typescript
// Encode string to bytes
const encoder = new TextEncoder();
const bytes = encoder.encode("Hello, 世界");

// Decode bytes to string
const decoder = new TextDecoder("utf-8");
const text = decoder.decode(bytes);

// Different encodings
const utf16 = encoder.encode("Hello");
const latin1 = new TextDecoder("latin1").decode(bytes);
```

## Performance Tips

1. **Use streaming for large files**: Don't load entire file into memory
2. **Batch database operations**: Use transactions for multiple inserts
3. **Reuse prepared statements**: Prepare once, execute many times
4. **Use Redis pipelining**: Send multiple commands at once
5. **Enable connection pooling**: For database connections
6. **Use binary protocols**: Protocol buffers or MessagePack over JSON

## Error Handling

```typescript
// File operations
try {
  const content = await Bun.file("./nonexistent.txt").text();
} catch (error) {
  if (error.code === "ENOENT") {
    console.log("File not found");
  }
}

// SQLite errors
try {
  db.query("INSERT INTO users (name) VALUES (?)").run("Alice");
} catch (error) {
  console.error("SQL error:", error.message);
}

// Redis errors
try {
  await redis.connect();
} catch (error) {
  console.error("Redis connection failed:", error);
}

// S3 errors
try {
  await s3.getObject("bucket", "key");
} catch (error) {
  if (error.name === "NoSuchKey") {
    console.log("Object not found");
  }
}
```

## Related Documentation

- [Runtime Basics](references/01-runtime-basics.md) - File I/O overview
- [HTTP Server](references/06-http-server.md) - Streaming responses
- [Process & System](references/12-process-system.md) - Environment variables for connections
