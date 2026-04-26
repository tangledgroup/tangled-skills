# Request Config

The request config object controls every aspect of an axios request. The only required option is `url`. If no `method` is specified, the default is `GET`.

## URL and Method

- **`url`** — The URL for the request (string or URL instance).
- **`method`** — HTTP method. Default: `"get"`.
- **`baseURL`** — Prepended to `url` unless `url` is absolute.
- **`allowAbsoluteUrls`** — When `true` (default), absolute `url` values override `baseURL`. When `false`, `baseURL` is always prepended.

## Request Body and Transforms

- **`data`** — Request body. Applicable for `PUT`, `POST`, `DELETE`, and `PATCH`. Accepts: string, plain object, ArrayBuffer, ArrayBufferView, URLSearchParams. Browser-only: FormData, File, Blob. Node-only: Stream, Buffer.
- **`transformRequest`** — Array of functions to modify request data before sending. Each function receives `(data, headers)` and must return the transformed data. The last function must return a string, Buffer, ArrayBuffer, FormData, or Stream.
- **`transformResponse`** — Array of functions to modify response data before it reaches `.then()` / `.catch()`.

## Headers

- **`headers`** — Custom HTTP headers to send. Default `Content-Type` is `application/json`.

## Query Parameters

- **`params`** — URL query parameters as a plain object or URLSearchParams. Merged with any query string already in `url`.
- **`paramsSerializer`** — Customize how params are serialized:
  - `encode` — Custom encoder function for individual key/value pairs.
  - `serialize` — Custom serializer for the entire params object.
  - `indexes` — Array index format: `null` (no brackets), `false` (empty brackets, default), `true` (brackets with indexes).
  - `maxDepth` — Maximum nesting depth (default: 100). Set to `Infinity` to disable.

## Timeout and Credentials

- **`timeout`** — Milliseconds before the request is aborted. Default: `0` (no timeout).
- **`withCredentials