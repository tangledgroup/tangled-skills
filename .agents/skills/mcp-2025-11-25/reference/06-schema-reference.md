# Schema Reference

Complete type definitions for MCP protocol version 2025-11-25.

## JSON-RPC Types

### JSONRPCMessage

Refers to any valid JSON-RPC object that can be decoded off the wire, or encoded to be sent.

`JSONRPCMessage = JSONRPCRequest | JSONRPCNotification | JSONRPCResponse`

### JSONRPCRequest

A request that expects a response.

```typescript
interface JSONRPCRequest {
  method: string;
  params?: { [key: string]: any };
  jsonrpc: "2.0";
  id: RequestId;
}
```

### JSONRPCNotification

A notification which does not expect a response.

```typescript
interface JSONRPCNotification {
  method: string;
  params?: { [key: string]: any };
  jsonrpc: "2.0";
}
```

### JSONRPCResponse

`JSONRPCResponse = JSONRPCResultResponse | JSONRPCErrorResponse`

### JSONRPCResultResponse

A successful (non-error) response to a request.

```typescript
interface JSONRPCResultResponse {
  jsonrpc: "2.0";
  id: RequestId;
  result: Result;
}
```

### JSONRPCErrorResponse

A response to a request that indicates an error occurred.

```typescript
interface JSONRPCErrorResponse {
  jsonrpc: "2.0";
  id?: RequestId;
  error: Error;
}
```

### RequestId

A uniquely identifying ID for a JSON-RPC request. `string | number`.

### Result

```typescript
interface Result {
  _meta?: { [key: string]: any };
}
```

Carries provider-specific or middleware data (e.g. usage stats).

### Error

```typescript
interface Error {
  code: number;
  message: string;
  data?: unknown;
}
```

## Common Types

### Cursor

An opaque token used to represent a cursor for pagination. `string`.

### ProgressToken

A progress token, used to associate progress notifications with the original request. `string | number`.

### Role

The sender or recipient of messages and data in a conversation. `"user" | "assistant"`.

### LoggingLevel

Severity of a log message (RFC 5424): `"debug" | "info" | "notice" | "warning" | "error" | "critical" | "alert" | "emergency"`.

### Annotations

Optional annotations for the client.

```typescript
interface Annotations {
  audience?: Role[];
  priority?: number;  // 0.0 (least important) to 1.0 (most important)
  lastModified?: string;  // ISO 8601 timestamp
}
```

### Icon

```typescript
interface Icon {
  src: string;
  mimeType: string;
  sizes?: string[];
}
```

### Implementation

```typescript
interface Implementation {
  name: string;
  version: string;
  title?: string;
  description?: string;
  icons?: Icon[];
  websiteUrl?: string;
}
```

## Content Types

### TextContent

```typescript
interface TextContent {
  type: "text";
  text: string;
  annotations?: Annotations;
}
```

### ImageContent

```typescript
interface ImageContent {
  type: "image";
  data: string;      // base64-encoded
  mimeType: string;
  annotations?: Annotations;
}
```

### AudioContent

```typescript
interface AudioContent {
  type: "audio";
  data: string;      // base64-encoded
  mimeType: string;
  annotations?: Annotations;
}
```

### ResourceLink

A link to an MCP resource.

```typescript
interface ResourceLink {
  uri: string;
  name: string;
  description?: string;
  mimeType?: string;
  annotations?: Annotations;
  icons?: Icon[];
}
```

### EmbeddedResource

```typescript
interface EmbeddedResource {
  type: "resource";
  resource: TextResourceContents | BlobResourceContents;
}
```

### ContentBlock

`ContentBlock = TextContent | ImageContent | AudioContent | ResourceLink | EmbeddedResource`

### TextResourceContents

```typescript
interface TextResourceContents {
  uri: string;
  mimeType?: string;
  text: string;
  annotations?: Annotations;
}
```

### BlobResourceContents

```typescript
interface BlobResourceContents {
  uri: string;
  mimeType?: string;
  blob: string;     // base64-encoded
  annotations?: Annotations;
}
```

## initialize

### InitializeRequestParams

```typescript
interface InitializeRequestParams {
  protocolVersion: string;
  capabilities: ClientCapabilities;
  clientInfo: Implementation;
  _meta?: { [key: string]: any };
}
```

### InitializeResult

```typescript
interface InitializeResult {
  protocolVersion: string;
  capabilities: ServerCapabilities;
  serverInfo: Implementation;
  instructions?: string;
  _meta?: { [key: string]: any };
}
```

### ClientCapabilities

```typescript
interface ClientCapabilities {
  experimental?: { [key: string]: any };
  roots?: { listChanged?: boolean };
  sampling?: { tools?: {}; context?: {} };
  elicitation?: { form?: {}; url?: {} };
  tasks?: {
    list?: {};
    cancel?: {};
    requests?: {
      sampling?: { createMessage?: {} };
      elicitation?: { create?: {} };
    };
  };
}
```

### ServerCapabilities

```typescript
interface ServerCapabilities {
  experimental?: { [key: string]: any };
  prompts?: { listChanged?: boolean };
  resources?: { subscribe?: boolean; listChanged?: boolean };
  tools?: { listChanged?: boolean };
  logging?: {};
  completions?: {};
  tasks?: {
    list?: {};
    cancel?: {};
    requests?: {
      tools?: { call?: {} };
    };
  };
}
```

## notifications/cancelled

```typescript
interface CancelledNotificationParams {
  requestId: RequestId;
  reason?: string;
  _meta?: { [key: string]: any };
}
```

## notifications/initialized

No parameters. Signals client is ready for normal operations.

## notifications/progress

```typescript
interface ProgressNotificationParams {
  progressToken: ProgressToken;
  progress: number;
  total?: number;
  message?: string;
  _meta?: { [key: string]: any };
}
```

## notifications/message (Logging)

```typescript
interface LoggingMessageNotificationParams {
  level: LoggingLevel;
  logger?: string;
  data: unknown;
  _meta?: { [key: string]: any };
}
```

## notifications/prompts/list_changed

No parameters. Sent when prompt list changes.

## notifications/resources/list_changed

No parameters. Sent when resource list changes.

## notifications/resources/updated

```typescript
interface ResourceUpdatedNotificationParams {
  uri: string;
  _meta?: { [key: string]: any };
}
```

## notifications/roots/list_changed

No parameters. Sent when roots list changes.

## notifications/tools/list_changed

No parameters. Sent when tools list changes.

## notifications/tasks/status

```typescript
interface TaskStatusNotificationParams {
  taskId: string;
  status: TaskStatus;
  statusMessage?: string;
  createdAt: string;
  lastUpdatedAt: string;
  ttl?: number | null;
  pollInterval?: number;
  _meta?: { [key: string]: any };
}
```

## notifications/elicitation/complete

```typescript
interface ElicitationCompleteNotificationParams {
  elicitationId: string;
}
```

## ping

No parameters. Receiver responds with empty result `{}`.

## tools/list

### ListToolsResult

```typescript
interface ListToolsResult {
  tools: Tool[];
  nextCursor?: Cursor;
  _meta?: { [key: string]: any };
}
```

### Tool

```typescript
interface Tool {
  name: string;
  title?: string;
  description?: string;
  inputSchema: object;    // JSON Schema
  outputSchema?: object;  // JSON Schema
  icons?: Icon[];
  annotations?: ToolAnnotations;
  execution?: ToolExecution;
}
```

### ToolAnnotations

```typescript
interface ToolAnnotations {
  title?: string;
  readOnlyHint?: boolean;
  destructiveHint?: boolean;
  idempotentHint?: boolean;
  openWorldHint?: boolean;
}
```

### ToolExecution

```typescript
interface ToolExecution {
  taskSupport?: "forbidden" | "optional" | "required";
}
```

## tools/call

### CallToolRequestParams

```typescript
interface CallToolRequestParams {
  name: string;
  arguments?: { [key: string]: any };
  task?: TaskMetadata;
  _meta?: { [key: string]: any };
}
```

### CallToolResult

```typescript
interface CallToolResult {
  content: ContentBlock[];
  structuredContent?: unknown;
  isError?: boolean;
  _meta?: { [key: string]: any };
}
```

## resources/list

### ListResourcesResult

```typescript
interface ListResourcesResult {
  resources: Resource[];
  nextCursor?: Cursor;
  _meta?: { [key: string]: any };
}
```

### Resource

```typescript
interface Resource {
  uri: string;
  name: string;
  title?: string;
  description?: string;
  mimeType?: string;
  size?: number;
  icons?: Icon[];
  annotations?: Annotations;
}
```

## resources/read

### ReadResourceRequestParams

```typescript
interface ReadResourceRequestParams {
  uri: string;
  _meta?: { [key: string]: any };
}
```

### ReadResourceResult

```typescript
interface ReadResourceResult {
  contents: (TextResourceContents | BlobResourceContents)[];
  _meta?: { [key: string]: any };
}
```

## resources/templates/list

### ListResourceTemplatesResult

```typescript
interface ListResourceTemplatesResult {
  resourceTemplates: ResourceTemplate[];
  nextCursor?: Cursor;
  _meta?: { [key: string]: any };
}
```

### ResourceTemplate

```typescript
interface ResourceTemplate {
  uriTemplate: string;   // RFC 6570 URI template
  name: string;
  title?: string;
  description?: string;
  mimeType?: string;
  icons?: Icon[];
  annotations?: Annotations;
}
```

## resources/subscribe

```typescript
interface SubscribeRequestParams {
  uri: string;
  _meta?: { [key: string]: any };
}
```

## resources/unsubscribe

```typescript
interface UnsubscribeRequestParams {
  uri: string;
  _meta?: { [key: string]: any };
}
```

## prompts/list

### ListPromptsResult

```typescript
interface ListPromptsResult {
  prompts: Prompt[];
  nextCursor?: Cursor;
  _meta?: { [key: string]: any };
}
```

### Prompt

```typescript
interface Prompt {
  name: string;
  title?: string;
  description?: string;
  arguments?: PromptArgument[];
  icons?: Icon[];
}
```

### PromptArgument

```typescript
interface PromptArgument {
  name: string;
  description?: string;
  required?: boolean;
}
```

## prompts/get

### GetPromptRequestParams

```typescript
interface GetPromptRequestParams {
  name: string;
  arguments?: { [key: string]: string };
  _meta?: { [key: string]: any };
}
```

### GetPromptResult

```typescript
interface GetPromptResult {
  description?: string;
  messages: PromptMessage[];
  _meta?: { [key: string]: any };
}
```

### PromptMessage

```typescript
interface PromptMessage {
  role: Role;
  content: TextContent | ImageContent | AudioContent | EmbeddedResource;
}
```

## roots/list

### ListRootsResult

```typescript
interface ListRootsResult {
  roots: Root[];
  _meta?: { [key: string]: any };
}
```

### Root

```typescript
interface Root {
  uri: string;    // file:// URI
  name?: string;
}
```

## sampling/createMessage

### CreateMessageRequestParams

```typescript
interface CreateMessageRequestParams {
  messages: SamplingMessage[];
  modelPreferences?: ModelPreferences;
  systemPrompt?: string;
  includeContext?: "none" | "thisServer" | "allServers";
  maxTokens: number;
  stopSequences?: string[];
  temperature?: number;
  tools?: Tool[];
  toolChoice?: { mode: "auto" | "required" | "none" };
  task?: TaskMetadata;
  _meta?: { [key: string]: any };
}
```

### CreateMessageResult

```typescript
interface CreateMessageResult {
  role: Role;
  content: SamplingMessageContentBlock | SamplingMessageContentBlock[];
  model: string;
  stopReason?: "endTurn" | "stopSequence" | "maxTokens" | "toolUse";
  _meta?: { [key: string]: any };
}
```

### ModelPreferences

```typescript
interface ModelPreferences {
  hints?: ModelHint[];
  costPriority?: number;
  speedPriority?: number;
  intelligencePriority?: number;
}
```

### ModelHint

```typescript
interface ModelHint {
  name: string;
}
```

### SamplingMessage

```typescript
interface SamplingMessage {
  role: Role;
  content: SamplingMessageContentBlock | SamplingMessageContentBlock[];
}
```

### SamplingMessageContentBlock

`SamplingMessageContentBlock = TextContent | ImageContent | AudioContent | ToolUseContent | ToolResultContent`

### ToolUseContent

```typescript
interface ToolUseContent {
  type: "tool_use";
  id: string;
  name: string;
  input: { [key: string]: any };
}
```

### ToolResultContent

```typescript
interface ToolResultContent {
  type: "tool_result";
  toolUseId: string;
  content: (TextContent | ImageContent | AudioContent) | (TextContent | ImageContent | AudioContent)[];
}
```

## elicitation/create

### ElicitRequestParams

`ElicitRequestParams = ElicitRequestFormParams | ElicitRequestURLParams`

### ElicitRequestFormParams

```typescript
interface ElicitRequestFormParams {
  mode?: "form";
  message: string;
  requestedSchema: object;  // Restricted JSON Schema (flat objects, primitives only)
  task?: TaskMetadata;
  _meta?: { [key: string]: any };
}
```

### ElicitRequestURLParams

```typescript
interface ElicitRequestURLParams {
  mode: "url";
  message: string;
  url: string;
  elicitationId: string;
  task?: TaskMetadata;
  _meta?: { [key: string]: any };
}
```

### ElicitResult

```typescript
interface ElicitResult {
  action: "accept" | "decline" | "cancel";
  content?: { [key: string]: any };
  _meta?: { [key: string]: any };
}
```

### Restricted JSON Schema Types (Elicitation Form Mode)

Form mode schemas are limited to flat objects with primitive properties only. Complex nested structures and arrays of objects beyond enums are not supported.

#### StringSchema

```typescript
interface StringSchema {
  type: "string";
  title?: string;
  description?: string;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  format?: "email" | "uri" | "date" | "date-time";
  default?: string;
}
```

#### NumberSchema

```typescript
interface NumberSchema {
  type: "number" | "integer";
  title?: string;
  description?: string;
  minimum?: number;
  maximum?: number;
  default?: number;
}
```

#### BooleanSchema

```typescript
interface BooleanSchema {
  type: "boolean";
  title?: string;
  description?: string;
  default?: boolean;
}
```

### Enum Schema Types

**SingleSelectEnumSchema**: `UntitledSingleSelectEnumSchema | TitledSingleSelectEnumSchema`

**MultiSelectEnumSchema**: `UntitledMultiSelectEnumSchema | TitledMultiSelectEnumSchema`

**UntitledSingleSelectEnumSchema:**

```typescript
interface UntitledSingleSelectEnumSchema {
  type: "string";
  title?: string;
  description?: string;
  enum: string[];
  default?: string;
}
```

**TitledSingleSelectEnumSchema:**

```typescript
interface TitledSingleSelectEnumSchema {
  type: "string";
  title?: string;
  description?: string;
  oneOf: { const: string; title: string }[];
  default?: string;
}
```

**UntitledMultiSelectEnumSchema:**

```typescript
interface UntitledMultiSelectEnumSchema {
  type: "array";
  title?: string;
  description?: string;
  minItems?: number;
  maxItems?: number;
  items: { type: "string"; enum: string[] };
  default?: string[];
}
```

**TitledMultiSelectEnumSchema:**

```typescript
interface TitledMultiSelectEnumSchema {
  type: "array";
  title?: string;
  description?: string;
  minItems?: number;
  maxItems?: number;
  items: { anyOf: { const: string; title: string }[] };
  default?: string[];
}
```

## completion/complete

### CompleteRequestParams

```typescript
interface CompleteRequestParams {
  ref: PromptReference | ResourceTemplateReference;
  argument: { name: string; value: string };
  context?: { arguments?: { [key: string]: string } };
  _meta?: { [key: string]: any };
}
```

### CompleteResult

```typescript
interface CompleteResult {
  completion: {
    values: string[];      // max 100
    total?: number;
    hasMore?: boolean;
  };
  _meta?: { [key: string]: any };
}
```

### PromptReference

```typescript
interface PromptReference {
  type: "ref/prompt";
  name: string;
}
```

### ResourceTemplateReference

```typescript
interface ResourceTemplateReference {
  type: "ref/resource";
  uri: string;
}
```

## logging/setLevel

```typescript
interface SetLevelRequestParams {
  level: LoggingLevel;
  _meta?: { [key: string]: any };
}
```

## tasks (Common)

### Task

```typescript
interface Task {
  taskId: string;
  status: TaskStatus;
  statusMessage?: string;
  createdAt: string;     // ISO 8601
  lastUpdatedAt: string;  // ISO 8601
  ttl?: number | null;    // milliseconds
  pollInterval?: number;  // milliseconds
}
```

### TaskStatus

`"working" | "input_required" | "completed" | "failed" | "cancelled"`

### TaskMetadata

```typescript
interface TaskMetadata {
  ttl?: number;  // requested duration in milliseconds
}
```

### RelatedTaskMetadata

```typescript
interface RelatedTaskMetadata {
  taskId: string;
}
```

## tasks/get

```typescript
interface GetTaskRequestParams {
  taskId: string;
  _meta?: { [key: string]: any };
}
```

`GetTaskResult = Result & Task`

## tasks/result

```typescript
interface GetTaskPayloadResult {
  _meta?: { [key: string]: any };
}
```

Returns the underlying request's result (e.g., `CallToolResult` for tools/call).

## tasks/list

```typescript
interface ListTasksRequestParams {
  cursor?: Cursor;
  _meta?: { [key: string]: any };
}
```

### ListTasksResult

```typescript
interface ListTasksResult {
  tasks: Task[];
  nextCursor?: Cursor;
  _meta?: { [key: string]: any };
}
```

## tasks/cancel

```typescript
interface CancelTaskRequestParams {
  taskId: string;
  _meta?: { [key: string]: any };
}
```

`CancelTaskResult = Result & Task`

## TitledMultiSelectEnumSchema

```typescript
interface TitledMultiSelectEnumSchema {
  type: "array";
  title?: string;
  description?: string;
  minItems?: number;
  maxItems?: number;
  items: { anyOf: { const: string; title: string }[] };
  default?: string[];
}
```
