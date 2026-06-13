# Data & Storage

## SQLite (`bun:sqlite`)

Bun natively implements a high-performance synchronous SQLite3 driver, inspired by better-sqlite3. It is roughly 3-6x faster than better-sqlite3.

### Opening a Database

```ts
import { Database } from "bun:sqlite";

const db = new Database("mydb.sqlite");          // file-based
const db = new Database(":memory:");              // in-memory
const db = new Database();                        // also in-memory
const db = new Database("mydb.sqlite", { readonly: true });
const db = new Database("mydb.sqlite", { create: true });
```

Import syntax:

```ts
import db from "./mydb.sqlite" with { type: "sqlite" };
```

### Strict Mode

```ts
const strict = new Database(":memory:", { strict: true });
// throws on missing parameter names
strict.query("SELECT $message").all({ messag: "hello" }); // Error!
```

### Queries

```ts
const db = new Database(":memory:");

// Create table
db.run("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)");

// Insert with parameters
const insert = db.prepare("INSERT INTO users (name, email) VALUES ($name, $email)");
insert.run({ name: "Alice", email: "alice@example.com" });

// Query with positional params
const query = db.query("SELECT * FROM users WHERE name = ?");
const user = query.get("Alice");

// Get all results
const allUsers = db.query("SELECT * FROM users").all();

// Map to class
class User {
  id: number;
  name: string;
  email: string;
}
const users = db.query("SELECT * FROM users").as(User).all();
```

### Transactions

```ts
db.transaction((name, email) => {
  const insert = db.prepare("INSERT INTO users (name, email) VALUES ($name, $email)");
  insert.run({ name, email });
})("Bob", "bob@example.com");
```

### Closing

```ts
db.close(false);  // allow pending queries to finish
db.close(true);   // throw if pending queries exist

// Using statement (auto-close)
{
  using db = new Database("mydb.sqlite");
  console.log(db.query("select 'hello' as msg").get());
} // db closed automatically
```

### Features

- Transactions, named and positional parameters
- Prepared statements
- Datatype conversions (`BLOB` → `Uint8Array`, `bigint` support)
- Multi-query statements in a single `db.run()` call
- Map results to classes with `.as(MyClass)`

## Redis Client

Bun provides a native Promise-based Redis client (requires Redis 7.2+).

### Connection

```ts
import { redis, RedisClient } from "bun";

// Default client (reads REDIS_URL or VALKEY_URL env var, defaults to localhost:6379)
await redis.set("hello", "world");
const value = await redis.get("hello");

// Custom client
const client = new RedisClient("redis://username:password@localhost:6379");
await client.set("counter", "0");
```

### Connection Lifecycle

```ts
const client = new RedisClient();
// No connection until first command
await client.connect();  // explicit connect
await client.set("key", "value");
client.close();  // close when done
```

### String Operations

```ts
await redis.set("user:1:name", "Alice");
const name = await redis.get("user:1:name");
const buffer = await redis.getBuffer("user:1:name");  // Uint8Array
await redis.del("user:1:name");
const exists = await redis.exists("user:1:name");
await redis.expire("session:123", 3600);  // expire in 1 hour
const ttl = await redis.ttl("session:123");
```

### Numeric Operations

```ts
await redis.set("counter", "0");
await redis.incr("counter");
await redis.decr("counter");
```

### Hash Operations

```ts
await redis.hmset("user:123", ["name", "Alice", "email", "alice@example.com"]);
const fields = await redis.hmget("user:123", ["name", "email"]);
const name = await redis.hget("user:123", "name");
await redis.hincrby("user:123", "visits", 1);
```

### List, Set, Sorted Set Operations

```ts
// Lists
await redis.lpush("tasks", "task1");
await redis.rpush("tasks", "task2");
const task = await redis.lpop("tasks");

// Sets
await redis.sadd("tags", "javascript", "typescript");
const members = await redis.smembers("tags");

// Sorted Sets
await redis.zadd("scores", { player1: 100, player2: 200 });
const rank = await redis.zrank("scores", "player1");
```

## File I/O

Bun provides optimized file APIs that are the recommended way to perform filesystem tasks.

### Reading Files (`Bun.file()`)

```ts
const file = Bun.file("foo.txt");  // lazy — doesn't read until accessed
file.size;   // number of bytes
file.type;   // MIME type

await file.text();        // string
await file.json();        // parsed JSON
await file.stream();      // ReadableStream
await file.arrayBuffer(); // ArrayBuffer
await file.bytes();       // Uint8Array
await file.exists();      // boolean

// File descriptors and URLs
Bun.file(1234);                              // by fd
Bun.file(new URL(import.meta.url));         // current file

// Stdio
Bun.stdin;   // readonly BunFile
Bun.stdout;  // writable BunFile
Bun.stderr;  // writable BunFile

// Delete a file
await Bun.file("logs.json").delete();
```

### Writing Files (`Bun.write()`)

```ts
const bytesWritten = await Bun.write("output.txt", "Hello!");
await Bun.write("output.json", JSON.stringify({ key: "value" }));
await Bun.write("output.bin", new Uint8Array([1, 2, 3]));
await Bun.write("output.txt", Bun.file("source.txt")); // copy
```

`Bun.write()` accepts destinations as `string`, `URL`, or `BunFile`, and data as `string`, `Blob`, `ArrayBuffer`, `TypedArray`, or `Response`.

For operations not yet available with `Bun.file` (like `mkdir`, `readdir`), use Bun's implementation of `node:fs`.

## Streams

Bun implements Web-standard streams API:

```ts
const stream = Bun.file("large-file.bin").stream();
const reader = stream.getReader();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  // process chunk
}
```

## Binary Data

Bun supports efficient binary data manipulation with `ArrayBuffer`, `Uint8Array`, `Blob`, `DataView`, and `Buffer` conversions. Use built-in methods for fast transformations between formats.

## S3 Client

Bun provides native S3-compatible object storage support:

```ts
import { S3Client } from "bun";

const s3 = new S3Client({
  bucket: "my-bucket",
  region: "us-east-1",
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
});

// Put object
await s3.put("key.txt", "Hello S3!");

// Get object
const data = await s3.get("key.txt");
```
