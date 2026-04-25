# aiohttp 3.13 API Index

Complete index of all aiohttp components and their reference files.

## Client Components

### Core Client API
- **ClientSession** - Main client interface for HTTP requests
  - Reference: [01-client-reference.md](01-client-reference.md)
  
- **ClientResponse** - Response object from server
  - Properties: `status`, `headers`, `url`, `history`, `content`
  - Methods: `text()`, `json()`, `read()`, `raise_for_status()`
  - Reference: [01-client-reference.md](01-client-reference.md)

- **ClientRequest** - Request object (internal)
  - Reference: [01-client-reference.md](01-client-reference.md)

### Connection Management
- **BaseConnector** - Abstract connector base class
  - Reference: [07-client-api-connectors.md](07-client-api-connectors.md)

- **TCPConnector** - TCP connection pool (default)
  - Parameters: `limit`, `limit_per_host`, `keepalive_timeout`, `ssl`
  - Reference: [07-client-api-connectors.md](07-client-api-connectors.md)

- **UnixConnector** - Unix domain socket connections
  - Reference: [07-client-api-connectors.md](07-client-api-connectors.md)

- **NamedPipeConnector** - Windows named pipes
  - Reference: [07-client-api-connectors.md](07-client-api-connectors.md)

### Client Timeouts
- **ClientTimeout** - Timeout configuration
  - Parameters: `total`, `connect`, `sock_connect`, `sock_read`
  - Reference: [01-client-reference.md](01-client-reference.md)

### Client Authentication
- **BasicAuth** - HTTP Basic authentication
  - Reference: [01-client-reference.md](01-client-reference.md)

### Client Cookies
- **AbstractCookieJar** - Cookie storage interface
- **CookieJar** - Default cookie jar implementation
- **DummyCookieJar** - No-op cookie jar (disables cookies)
  - Reference: [01-client-reference.md](01-client-reference.md)

## Server Components

### Application & Routing
- **Application** - Main web application container
  - Properties: `router`, `middlewares`, `state`
  - Signals: `on_startup`, `on_shutdown`, `on_cleanup`
  - Reference: [09-server-api-application.md](09-server-api-application.md)

- **RouteTableDef** - Decorator-based route definition
  - Methods: `get()`, `post()`, `put()`, `patch()`, `delete()`, `head()`, `options()`
  - Reference: [10-server-api-routing.md](10-server-api-routing.md)

- **AbstractRouter** - Router interface (for custom routers)
  - Reference: [abc.html](https://docs.aiohttp.org/en/stable/abc.html)

- **Request** - Incoming HTTP request
  - Properties: `method`, `url`, `headers`, `cookies`, `match_info`
  - Methods: `json()`, `post()`, `read()`
  - Reference: [02-server-reference.md](02-server-reference.md)

- **BaseRequest** - Base request (low-level servers)
  - Reference: [02-server-reference.md](02-server-reference.md)

### Response Types
- **Response** - Basic HTTP response
  - Reference: [02-server-reference.md](02-server-reference.md)

- **StreamResponse** - Streaming response base
  - Reference: [02-server-reference.md](02-server-reference.md)

- **json_response()** - JSON response helper
  - Reference: [02-server-reference.md](02-server-reference.md)

- **FileResponse** - File serving response
  - Reference: [02-server-reference.md](02-server-reference.md)

- **WebSocketResponse** - WebSocket response
  - Reference: [03-websockets.md](03-websockets.md)

### HTTP Exceptions (Server)
- **HTTPException** - Base HTTP exception
- **HTTPError** - HTTP error (4xx/5xx)
- **HTTPBadRequest** - 400 Bad Request
- **HTTPUnauthorized** - 401 Unauthorized
- **HTTPForbidden** - 403 Forbidden
- **HTTPNotFound** - 404 Not Found
- **HTTPMethodNotAllowed** - 405 Method Not Allowed
- **HTTPInternalServerError** - 500 Internal Server Error
  - Reference: [02-server-reference.md](02-server-reference.md)

### Views
- **View** - Base class for class-based views
- **ResourceView** - Resource-oriented view
  - Reference: [10-server-api-routing.md](10-server-api-routing.md)

## Streaming API

### Readers
- **StreamReader** - Read from incoming streams
  - Methods: `read()`, `readany()`, `readexactly()`, `readline()`
  - Iterators: `iter_chunked()`, `iter_any()`, `iter_lines()`
  - Reference: [11-api-streams.md](11-api-streams.md)

### Writers
- **StreamWriter** - Write to outgoing streams
  - Methods: `write()`, `writelines()`, `drain()`, `flush()`
  - Reference: [11-api-streams.md](11-api-streams.md)

## Data Structures

### Collections
- **FrozenList** - Mutable list that can be frozen
  - Methods: `freeze()`, `frozen` property
  - Reference: [12-api-data-structures.md](12-api-data-structures.md)

- **ChainMapProxy** - Immutable chained mapping
  - Reference: [12-api-data-structures.md](12-api-data-structures.md)

- **FrozenDict** - Immutable dictionary
  - Reference: [12-api-data-structures.md](12-api-data-structures.md)

### Multi-Dictionaries (from multidict)
- **CIMultiDict** - Case-insensitive multi-dict (headers)
  - Reference: [12-api-data-structures.md](12-api-data-structures.md)

- **CIMultiDictProxy** - Read-only CIMultiDict
  - Reference: [12-api-data-structures.md](12-api-data-structures.md)

- **MultiDict** - Case-sensitive multi-dict (query params)
  - Reference: [12-api-data-structures.md](12-api-data-structures.md)

- **MultiDictProxy** - Read-only MultiDict
  - Reference: [12-api-data-structures.md](12-api-data-structures.md)

### URL Handling (from yarl)
- **URL** - URL parsing and manipulation
  - Properties: `scheme`, `host`, `port`, `path`, `query`, `fragment`
  - Methods: `with_query()`, `with_path()`, `with_host()`
  - Reference: [12-api-data-structures.md](12-api-data-structures.md)

## WebSocket API

### Client
- **ClientWebSocketResponse** - WebSocket client response
  - Methods: `send_str()`, `send_bytes()`, `send_json()`
  - Methods: `receive()`, `receive_str()`, `receive_bytes()`, `receive_json()`
  - Reference: [03-websockets.md](03-websockets.md)

### Server
- **WebSocketResponse** - WebSocket server response
  - Message types: `WSMsgType.TEXT`, `WSMsgType.BINARY`, `WSMsgType.CLOSED`
  - Reference: [03-websockets.md](03-websockets.md)

## Multipart API

### Client
- **FormData** - Multipart form data builder
  - Methods: `add_field()`
  - Reference: [04-multipart.md](04-multipart.md)

### Server
- **MultipartReader** - Parse incoming multipart data
  - Reference: [04-multipart.md](04-multipart.md)

- **BodyPartReader** - Read individual form parts
  - Properties: `name`, `filename`, `content_type`
  - Reference: [04-multipart.md](04-multipart.md)

## Tracing API

### Client Tracing
- **TraceConfig** - Client tracing configuration
  - Hooks: `on_request_start`, `on_request_end`, `on_connection_create_end`
  - Reference: [06-tracing.md](06-tracing.md)

- **TraceRequestStartParams** - Request start parameters
- **TraceRequestEndParams** - Request end parameters
  - Reference: [06-tracing.md](06-tracing.md)

## Server Runners

- **AppRunner** - Application runner (low-level)
  - Reference: [09-server-api-application.md](09-server-api-application.md)

- **Site** - Base site class
- **TCPSite** - TCP site
- **UnixSite** - Unix socket site
  - Reference: [09-server-api-application.md](09-server-api-application.md)

## Client Exceptions

### Connection Errors
- **ClientError** - Base client error
- **ClientConnectorError** - Connection failed
- **ClientConnectorCertificateError** - SSL certificate error
- **ServerDisconnectedError** - Server closed connection
  - Reference: [08-client-api-exceptions.md](08-client-api-exceptions.md)

### HTTP Errors
- **ClientResponseError** - HTTP error response
- **HTTPError** - HTTP error base
  - Reference: [08-client-api-exceptions.md](08-client-api-exceptions.md)

### Timeout Errors
- **ServerTimeoutError** - Server timeout
- **SocketTimeoutError** - Socket timeout
  - Reference: [08-client-api-exceptions.md](08-client-api-exceptions.md)

### Payload Errors
- **ClientPayloadError** - Request payload error
- **InvalidURL** - Invalid URL format
- **ContentTypeError** - Wrong content type
- **InvalidJSON** - JSON parsing failed
  - Reference: [08-client-api-exceptions.md](08-client-api-exceptions.md)

### Redirect Errors
- **TooManyRedirects** - Redirect limit exceeded
  - Reference: [08-client-api-exceptions.md](08-client-api-exceptions.md)

### WebSocket Errors
- **WSHandshakeError** - WebSocket handshake failed
- **WebSocketError** - General WebSocket error
  - Reference: [08-client-api-exceptions.md](08-client-api-exceptions.md)

## Utility Functions

### Server Utilities
- **run_app()** - Run application (convenience function)
  - Reference: [09-server-api-application.md](09-server-api-application.md)

### Response Helpers
- **json_response()** - Create JSON response
  - Reference: [02-server-reference.md](02-server-reference.md)

## Abstract Base Classes (ABC)

For custom implementations:

- **AbstractRouter** - Custom router interface
- **AbstractMatchInfo** - Route match information
- **AbstractView** - Custom view interface
- **AbstractCookieJar** - Custom cookie storage
  - Reference: [https://docs.aiohttp.org/en/stable/abc.html](https://docs.aiohttp.org/en/stable/abc.html)

## Quick Reference by Task

### Making HTTP Requests
1. Create `ClientSession` → [01-client-reference.md](01-client-reference.md)
2. Configure `TCPConnector` → [07-client-api-connectors.md](07-client-api-connectors.md)
3. Handle exceptions → [08-client-api-exceptions.md](08-client-api-exceptions.md)

### Building Web Servers
1. Create `Application` → [09-server-api-application.md](09-server-api-application.md)
2. Add routes → [10-server-api-routing.md](10-server-api-routing.md)
3. Handle requests → [02-server-reference.md](02-server-reference.md)

### Streaming Data
1. Use `StreamReader` → [11-api-streams.md](11-api-streams.md)
2. Use `StreamWriter` → [11-api-streams.md](11-api-streams.md)

### WebSockets
1. Client WebSocket → [03-websockets.md](03-websockets.md)
2. Server WebSocket → [03-websockets.md](03-websockets.md)

### File Uploads/Downloads
1. Multipart client → [04-multipart.md](04-multipart.md)
2. Multipart server → [04-multipart.md](04-multipart.md)

### Advanced Topics
1. Middleware → [05-advanced-server.md](05-advanced-server.md)
2. Tracing → [06-tracing.md](06-tracing.md)
3. Data structures → [12-api-data-structures.md](12-api-data-structures.md)
