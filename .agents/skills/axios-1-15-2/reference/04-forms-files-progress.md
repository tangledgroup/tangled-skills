# Forms, Files & Progress

## multipart/form-data

### Manual FormData

Create a `FormData` object and append fields:

```js
const formData = new FormData();
formData.append("foo", "bar");
formData.append("file", fileInput.files[0]);

await axios.post("https://httpbin.org/post", formData);
```

In Node.js, use the `form-data` package (or native `FormData` in Node 18+):

```js
import fs from "fs";
import FormData from "form-data";

const form = new FormData();
form.append("my_field", "my value");
form.append("my_buffer", Buffer.alloc(10));
form.append("my_file", fs.createReadStream("/foo/bar.jpg"));

await axios.post("https://example.com", form);
```

### Automatic Serialization to FormData

Set `Content-Type: multipart/form-data` and pass a plain object — axios serializes it automatically:

```js
await axios.post("https://httpbin.org/post", { x: 1, name: "test" }, {
  headers: { "Content-Type": "multipart/form-data" },
});
```

### Shortcut Methods

Axios provides convenience methods that preset the `Content-Type` header to `multipart/form-data`:

- `axios.postForm(url, data[, config])`
- `axios.putForm(url, data[, config])`
- `axios.patchForm(url, data[, config])`

```js
await axios.postForm("https://httpbin.org/post", { x: 1 });
```

### Special Key Endings

- `{}` — serialize the value with `JSON.stringify` (e.g., `"obj{}": '{"x":1}'`)
- `[]` — unwrap array-like objects as separate fields with the same key

Arrays and FileList objects are unwrapped by default.

### Configuring the FormData Serializer

```js
axios.postForm("/api", data, {
  formSerializer: {
    visitor: (value, key, path, helpers) => {}, // custom visitor
    dots: false,           // use dot notation instead of brackets
    metaTokens: true,      // preserve special endings like {}
    indexes: false,        // null | false (default) | true
    maxDepth: 100,         // set to Infinity to disable
  },
});
```

> **Security:** The `maxDepth` default of 100 protects against DoS via deeply nested payloads. Only raise it if your schema genuinely requires it.

## x-www-form-urlencoded

### Using URLSearchParams

```js
const params = new URLSearchParams({ foo: "bar" });
params.append("extraparam", "value");
await axios.post("/foo", params);
```

### Automatic Serialization

Set `Content-Type: application/x-www-form-urlencoded` and pass a plain object:

```js
await axios.postForm("https://postman-echo.com/post", { x: 1, name: "test" }, {
  headers: { "content-type": "application/x-www-form-urlencoded" },
});
```

The object is serialized to `URLSearchParams` automatically. Nested objects use bracket notation by default (`users[0][name]=Peter`).

## File Posting

### Single File (Browser)

Pass a `File` object directly — axios detects it and sets the correct content type:

```js
await axios.postForm("https://httpbin.org/post", {
  description: "My profile photo",
  file: document.querySelector("#fileInput").files[0],
});
```

### Multiple Files (Browser)

Pass a `FileList` to upload all files under the same field name (`files[]`):

```js
await axios.postForm(
  "https://httpbin.org/post",
  document.querySelector("#fileInput").files
);
```

For distinct field names, build `FormData` manually:

```js
const formData = new FormData();
formData.append("avatar", avatarFile);
formData.append("cover", coverFile);

await axios.post("https://httpbin.org/post", formData);
```

### Files in Node.js

Use `fs.createReadStream` to stream files without loading into memory:

```js
import fs from "fs";
import FormData from "form-data";

const form = new FormData();
form.append("file", fs.createReadStream("/path/to/file.jpg"));
form.append("description", "My uploaded file");

await axios.post("https://httpbin.org/post", form);
```

### Uploading a Buffer (Node.js)

```js
const buffer = Buffer.from("Hello, world!");

const form = new FormData();
form.append("file", buffer, {
  filename: "hello.txt",
  contentType: "text/plain",
  knownLength: buffer.length,
});

await axios.post("https://httpbin.org/post", form);
```

> **Warning:** When uploading a readable stream in Node.js, set `maxRedirects: 0` to prevent `follow-redirects` from buffering the entire stream in RAM.

## Progress Capturing

Axios captures upload and download progress events at a rate limited to 3 times per second (to avoid overwhelming the browser).

### Progress Event Shape

```js
{
  loaded: number;      // bytes transferred so far
  total?: number;      // total bytes
  progress?: number;   // ratio [0..1]
  bytes: number;       // bytes since last event (delta)
  estimated?: number;  // estimated time remaining (seconds)
  rate?: number;       // transfer speed (bytes/sec)
  upload?: true;       // present on upload events
  download?: true;     // present on download events
}
```

### Usage

```js
await axios.post(url, data, {
  onUploadProgress: ({ progress }) => {
    console.log(`Upload: ${(progress * 100).toFixed(1)}%`);
  },
  onDownloadProgress: ({ progress }) => {
    console.log(`Download: ${(progress * 100).toFixed(1)}%`);
  },
});
```

### Upload Progress with File

```js
await axios.postForm("https://httpbin.org/post", {
  file: document.querySelector("#fileInput").files[0],
}, {
  onUploadProgress: (progressEvent) => {
    const percent = Math.round(
      (progressEvent.loaded * 100) / progressEvent.total
    );
    console.log(`Upload progress: ${percent}%`);
  },
});
```

### Streaming Progress (Node.js)

```js
const { data } = await axios.post(SERVER_URL, readableStream, {
  onUploadProgress: ({ progress }) => {
    console.log((progress * 100).toFixed(2));
  },
  headers: { "Content-Length": contentLength },
  maxRedirects: 0, // avoid buffering the entire stream
});
```

> **Warning:** Capturing `FormData` upload progress is not currently supported in Node.js environments.

## Rate Limiting

Bandwidth limiting is available in Node.js via the HTTP adapter using the `maxRate` option.

### Basic Usage

```js
// Limit both directions to 100 KB/s
await axios.get(URL, { maxRate: 100 * 1024 });

// Different limits for upload and download
await axios.get(URL, { maxRate: [100 * 1024, 500 * 1024] });
```

### Upload Rate Limiting with Progress

```js
const { data } = await axios.post(SERVER_URL, myBuffer, {
  onUploadProgress: ({ progress, rate }) => {
    const percent = (progress * 100).toFixed(1);
    const kbps = (rate / 1024).toFixed(1);
    console.log(`Upload [${percent}%] at ${kbps} KB/s`);
  },
  maxRate: [100 * 1024], // cap upload at 100 KB/s
});
```

### Download Rate Limiting

```js
const { data } = await axios.get(FILE_URL, {
  onDownloadProgress: ({ progress, rate }) => {
    const percent = (progress * 100).toFixed(1);
    const kbps = (rate / 1024).toFixed(1);
    console.log(`Download [${percent}%] at ${kbps} KB/s`);
  },
  maxRate: [Infinity, 200 * 1024], // no upload limit, 200 KB/s download
  responseType: "arraybuffer",
});
```

> **Note:** `maxRate` is only supported by the Node.js HTTP adapter. It has no effect in browser environments.
