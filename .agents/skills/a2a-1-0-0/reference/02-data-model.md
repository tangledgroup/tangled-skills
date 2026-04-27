# Protocol Data Model

The A2A protocol defines a canonical data model using Protocol Buffers (proto3). The normative definition is in `a2a.proto`. All protocol bindings must provide functionally equivalent representations. JSON serialization uses camelCase field names per ProtoJSON specification. Enum values use SCREAMING_SNAKE_CASE as defined in the proto.

## Field Presence and Optionality

- **Optional fields not explicitly set:** MUST be omitted from JSON
- **Optional fields explicitly set to defaults:** MUST be included in JSON
- **Required fields:** MUST always be present, even if matching default
- **Repeated fields with empty arrays:** Omit unless field is REQUIRED

This semantics is critical for Agent Card signing — the canonical form must accurately reflect which fields were explicitly provided versus omitted.

## Core Objects

### Task

Represents a stateful unit of work with a defined lifecycle.

Fields:
- `id` (string, REQUIRED): Server-generated unique identifier
- `contextId` (string): Groups related tasks and messages
- `status` (TaskStatus, REQUIRED): Current status including state and message
- `artifacts` (Artifact[]): Outputs generated during processing
- `history` (Message[]): Messages exchanged during task execution
- `kind` (string): Optional classification of the task

### TaskStatus

Current status of a task.

Fields:
- `state` (TaskState, REQUIRED): Current lifecycle state
- `message` (Message): Status message from the agent (progress info, input requests)
- `timestamp` (string): ISO 8601 UTC timestamp of the status change

### TaskState

Enum values:
- `TASK_STATE_SUBMITTED`
- `TASK_STATE_WORKING`
- `TASK_STATE_COMPLETED`
- `TASK_STATE_FAILED`
- `TASK_STATE_CANCELED`
- `TASK_STATE_REJECTED`
- `TASK_STATE_INPUT_REQUIRED`
- `TASK_STATE_AUTH_REQUIRED`

### Message

A communication turn between client and agent.

Fields:
- `role` (Role, REQUIRED): `ROLE_USER` or `ROLE_AGENT`
- `parts` (Part[], REQUIRED): Content parts (at least one)
- `messageId` (string): Unique identifier for the message
- `taskId` (string): Reference to an existing task
- `contextId` (string): Conversational context grouping
- `referenceTaskIds` (string[]): References to related tasks
- `metadata` (map<string, value>): Additional context
- `extensions` (string[]): Extension URIs in use

### Part

Content container using oneof structure. Must contain exactly one of:

- `text` (string): Plain textual content
- `raw` (string): Base64-encoded binary file data
- `url` (string): URI referencing external file content
- `data` (object): Structured JSON value

Optional fields on all Parts:
- `mediaType` (string): MIME type
- `filename` (string): Content name
- `metadata` (map<string, value>): Additional context

### Artifact

Tangible output generated during task processing.

Fields:
- `artifactId` (string, REQUIRED): Unique identifier
- `name` (string): Human-readable name
- `description` (string): Description of the artifact
- `parts` (Part[], REQUIRED): Content parts
- `metadata` (map<string, value>): Additional context
- `extensions` (string[]): Extension URIs in use

## Streaming Events

### StreamResponse

Wrapper allowing streaming endpoints to return different types through a single response stream. Contains exactly one of:

- `task` (Task): Current task state
- `message` (Message): Direct message response
- `statusUpdate` (TaskStatusUpdateEvent): Status change notification
- `artifactUpdate` (TaskArtifactUpdateEvent): Artifact update notification

### TaskStatusUpdateEvent

Indicates a task status change.

Fields:
- `taskId` (string, REQUIRED): Task identifier
- `contextId` (string): Context identifier
- `status` (TaskStatus, REQUIRED): Updated status
- `metadata` (map<string, value>): Additional context

### TaskArtifactUpdateEvent

Indicates artifact updates during task processing. Used to stream large files or data structures in chunks.

Fields:
- `taskId` (string, REQUIRED): Task identifier
- `contextId` (string): Context identifier
- `artifact` (Artifact, REQUIRED): Updated or new artifact
- `metadata` (map<string, value>): Additional context

## Push Notification Objects

### PushNotificationConfig

Configuration for webhook-based push notifications.

Fields:
- `id` (string): Configuration identifier (server-assigned)
- `url` (string, REQUIRED): HTTPS webhook URL
- `token` (string): Optional client-side validation token
- `authentication` (AuthenticationInfo): Credentials for the agent to authenticate to the webhook

### AuthenticationInfo

Authentication details for push notification delivery.

Fields:
- `schemes` (string[], REQUIRED): Authentication schemes (e.g., ["Bearer"])
- `credentials` (map<string, string>): Optional credential details

### Push Notification Payload

Webhook POST requests use the same StreamResponse format as streaming:

```http
POST {webhook_url}
Authorization: Bearer token
Content-Type: application/a2a+json

{
  "statusUpdate": {
    "taskId": "task-uuid",
    "contextId": "context-uuid",
    "status": {"state": "TASK_STATE_COMPLETED"}
  }
}
```

Client responsibilities:
- Respond with HTTP 2xx to acknowledge receipt
- Process notifications idempotently (duplicates may occur)
- Validate task ID matches expected tasks
- Implement security measures to verify notification source

## Agent Discovery Objects

### AgentCard

The agent's digital business card. Full specification in the Agent Discovery reference. Key structure:

```json
{
  "name": "Agent Name",
  "description": "Agent description",
  "version": "1.0.0",
  "supportedInterfaces": [
    {
      "url": "https://agent.example.com/a2a/v1",
      "protocolBinding": "HTTP+JSON",
      "protocolVersion": "1.0"
    }
  ],
  "provider": {
    "organization": "Org Name",
    "url": "https://example.com"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": false,
    "extendedAgentCard": false
  },
  "securitySchemes": { ... },
  "security": [ ... ],
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/plain", "application/json"],
  "skills": [ ... ]
}
```

### AgentSkill

Describes a specific capability of the agent.

Fields:
- `id` (string, REQUIRED): Unique skill identifier
- `name` (string, REQUIRED): Human-readable name
- `description` (string, REQUIRED): Detailed description
- `tags` (string[]): Search/discovery tags
- `examples` (string[]): Example inputs
- `inputModes` (string[]): Supported input MIME types
- `outputModes` (string[]): Supported output MIME types
- `securityRequirements` (string[]): Security schemes required for this skill

### AgentCapabilities

Declares optional features supported by the agent.

Fields:
- `streaming` (boolean): SSE streaming support
- `pushNotifications` (boolean): Webhook push notification support
- `stateTransitionHistory` (boolean): Full state transition history in Task
- `extendedAgentCard` (boolean): Authenticated extended Agent Card available
- `extensions` (AgentExtension[]): Declared protocol extensions

### AgentExtension

Declares a supported protocol extension.

Fields:
- `uri` (string, REQUIRED): Unique identifier for the extension
- `description` (string, REQUIRED): Human-readable description
- `required` (boolean): Whether client must support this extension
- `params` (object): Extension-specific parameters

### AgentCardSignature

JWS signature for Agent Card authenticity verification.

Fields:
- `protected` (string, REQUIRED): Base64url-encoded JWS Protected Header
- `signature` (string, REQUIRED): Base64url-encoded signature value
- `header` (object): Optional JWS Unprotected Header as JSON object

## Data Conventions

### Timestamps

All timestamps use ISO 8601 format in UTC:
- Pattern: `YYYY-MM-DDTHH:mm:ss.sssZ`
- Millisecond precision where available
- Must not include timezone offsets other than 'Z'

### JSON Field Naming

JSON serialization uses camelCase (not snake_case from proto definitions):
- Proto `context_id` → JSON `contextId`
- Proto `protocol_version` → JSON `protocolVersion`
- Proto `default_input_modes` → JSON `defaultInputModes`

### Enum Values

Enum values are serialized as strings matching the proto definition:
- `TASK_STATE_COMPLETED`, `ROLE_USER`, `ROLE_AGENT`

### Field Presence

Optional fields not explicitly set should be omitted from JSON. Required fields must always be present. Implementations should ignore unrecognized fields for forward compatibility.
