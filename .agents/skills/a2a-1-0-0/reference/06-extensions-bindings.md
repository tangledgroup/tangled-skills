# Extensions & Custom Protocol Bindings

## Extensions

Extensions allow agents to provide additional functionality or data beyond the core A2A specification while maintaining backward compatibility and interoperability.

### Purpose

Extensions enable:
- Additional capabilities such as protocol enhancements or vendor-specific features
- Backward compatibility with clients that don't support specific extensions
- Innovation through experimental or domain-specific features without modifying the core protocol
- A pathway for community-developed features to become part of the core specification

### Scope

Extensions can extend A2A in several ways:

- **Data-only Extensions:** Expose new structured information in the Agent Card without impacting request-response flow. Example: GDPR compliance data.
- **Profile Extensions:** Overlay additional structure and state change requirements on core messages. Example: requiring all messages to use DataParts adhering to a specific schema, or defining substates in metadata (e.g., 'generating-image' substate when `TaskStatus.state` is 'working').
- **Method Extensions (Extended Skills):** Add entirely new RPC methods beyond the core set. Example: a `task-history` extension adding a `tasks/search` method.
- **State Machine Extensions:** Add new states or transitions to the task state machine.

### Limitations

Extensions cannot:
- Change the definition of core data structures (adding/removing fields from protocol-defined types). Custom attributes go in the `metadata` map.
- Add new values to enum types. Use existing enum values and annotate additional meaning in metadata.

## Extension Declaration

Agents declare supported extensions in the Agent Card using `AgentExtension` objects within `capabilities.extensions`:

```json
{
  "capabilities": {
    "extensions": [
      {
        "uri": "https://standards.org/extensions/citations/v1",
        "description": "Provides citation formatting and source verification",
        "required": false
      },
      {
        "uri": "https://example.com/extensions/geolocation/v1",
        "description": "Location-based search capabilities",
        "required": false,
        "params": {
          "hints": ["Use latitude/longitude coordinates"]
        }
      }
    ]
  }
}
```

**AgentExtension fields:**
- `uri` (string, REQUIRED): Unique identifier for the extension
- `description` (string, REQUIRED): Human-readable description
- `required` (boolean): Whether client must support this extension
- `params` (object): Extension-specific parameters

### Required Extensions

When `required: true` is set, the client must support the extension. Agents should not mark data-only extensions as required. If a client does not declare support for a required extension, the agent MUST return `ExtensionSupportRequiredError`.

## Extension Activation

Extensions default to inactive. Clients and agents negotiate activation per request:

1. **Client Request:** Client includes `A2A-Extensions` header with comma-separated list of extension URIs
2. **Agent Processing:** Agent identifies supported extensions and activates them
3. **Response:** Agent SHOULD include `A2A-Extensions` header listing successfully activated extensions

**Example request with extensions:**

```http
POST /agents/eightball HTTP/1.1
Host: example.com
Content-Type: application/json
A2A-Extensions: https://example.com/ext/konami-code/v1

{
  "jsonrpc": "2.0",
  "method": "SendMessage",
  "id": "1",
  "params": {
    "message": {
      "messageId": "1",
      "role": "ROLE_USER",
      "parts": [{"text": "Oh magic 8-ball, will it rain today?"}]
    },
    "metadata": {
      "https://example.com/ext/konami-code/v1/code": "motherlode"
    }
  }
}
```

**Response echoing activated extensions:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
A2A-Extensions: https://example.com/ext/konami-code/v1

{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "message": {
      "messageId": "2",
      "role": "ROLE_AGENT",
      "parts": [{"text": "That's a bingo!"}]
    }
  }
}
```

## Extension Points

### Message Extensions

Messages can include extension data for strongly typed context:

```json
{
  "role": "ROLE_USER",
  "parts": [{"text": "Find restaurants near me"}],
  "extensions": ["https://example.com/extensions/geolocation/v1"],
  "metadata": {
    "https://example.com/extensions/geolocation/v1": {
      "latitude": 37.7749,
      "longitude": -122.4194,
      "accuracy": 10.0,
      "timestamp": "2025-10-21T14:30:00Z"
    }
  }
}
```

### Artifact Extensions

Artifacts can include extension data for strongly typed context about generated content:

```json
{
  "artifactId": "research-summary-001",
  "name": "Climate Change Summary",
  "parts": [{"text": "Global temperatures have risen by 1.1°C..."}],
  "extensions": ["https://standards.org/extensions/citations/v1"],
  "metadata": {
    "https://standards.org/extensions/citations/v1": {
      "sources": [
        {
          "title": "Global Temperature Anomalies - 2023 Report",
          "url": "https://climate.gov/reports/2023-temperature"
        }
      ]
    }
  }
}
```

## Extension Versioning and Compatibility

- Extensions SHOULD include version information in their URI identifier
- A new URI MUST be created for breaking changes to an extension
- If a client requests an unsupported extension version, the agent SHOULD ignore it unless marked `required`
- Agent MUST NOT fall back to a previous version automatically

## Extension Dependencies

Extensions may depend on other extensions (required or optional). Extension specifications should document these dependencies. It is the client's responsibility to activate an extension and all its required dependencies.

## Extension Specification

An extension specification should contain:
- The specific URI(s) identifying the extension
- Schema and meaning of objects in the `params` field
- Schemas of additional data structures exchanged between client and agent
- Details of new request-response flows, endpoints, or logic

### Security Considerations for Extensions

- **Input Validation:** Any new data fields, parameters, or methods introduced by an extension MUST be rigorously validated. Treat all extension-related data from an external party as untrusted input.
- **Scope of Required Extensions:** Be mindful when marking an extension as `required: true`. This creates a hard dependency for all clients and should only be used for extensions fundamental to the agent's core function and security.
- **Authentication and Authorization:** If an extension adds new methods, the implementation MUST ensure these methods are subject to the same authentication and authorization checks as the core A2A methods. An extension MUST NOT provide a way to bypass the agent's primary security controls.

## Example Extensions

- **Secure Passport Extension:** Adds trusted contextual layer for personalization and reduced overhead
- **Timestamp Extension:** Demonstrates augmenting base A2A types by adding timestamps to Message/Artifact metadata
- **Traceability Extension:** Python implementation for tracking task provenance
- **Agent Gateway Protocol (AGP) Extension:** Introduces Autonomous Squads and routes Intent payloads based on declared capabilities

## Custom Protocol Bindings

Custom protocol bindings let implementers expose A2A operations over additional transport mechanisms not covered by the standard set (JSON-RPC, gRPC, HTTP+JSON/REST). They are a complementary but distinct concept to Extensions — extensions modify the behavior of protocol interactions on top of an existing transport; custom bindings change the transport layer itself.

### Declaration in the Agent Card

Custom protocol bindings are declared in the Agent Card's `supportedInterfaces` list. Each entry identifies the transport by URI, the endpoint URL, and the A2A protocol version it implements:

```json
{
  "supportedInterfaces": [
    {
      "url": "wss://agent.example.com/a2a/websocket",
      "protocolBinding": "https://a2a-protocol.org/bindings/websocket",
      "protocolVersion": "1.0"
    }
  ]
}
```

Agents that support multiple bindings list all of them. Clients parse `supportedInterfaces` in order and select the first transport they support, so entries should be listed in preference order.

### Requirements

Custom protocol bindings must comply with all requirements in the Protocol Binding Requirements section of the specification:

- **All core operations must be supported.** The binding must expose every operation defined in the abstract operations layer.
- **The data model must be preserved.** All data structures must be functionally equivalent to the canonical Protocol Buffer definitions.
- **Behavior must be consistent.** Semantically equivalent requests must produce semantically equivalent results regardless of which binding is used.

### Key Areas to Specify

A custom binding specification must address:

- **Data Type Mappings:** How each Protocol Buffer type is represented (binary encoding, enum representation, timestamp format)
- **Service Parameters:** Mechanism for carrying key-value context (headers, metadata fields), encoding/size constraints
- **Error Mapping:** Mapping table equivalent to the standard error code mappings
- **Streaming:** Stream mechanism, ordering guarantees, reconnection behavior, termination signaling
- **Authentication:** How credentials are transmitted over the custom transport

### Interoperability Testing

Before publishing a custom binding, verify that:
- All operations behave identically to the standard bindings for the same logical requests
- Error conditions, large payloads, and long-running tasks are handled correctly
- Any intentional deviations from standard binding behavior are clearly documented
- Sample requests and responses are included in the specification

## Governance Framework

The A2A organization uses a unified governance framework for both Extensions and Custom Protocol Bindings.

### Tiers

Both use a two-tier system within the `a2aproject` GitHub organization:

**Official:**
- Extensions: repo prefix `ext-{name}`, URI prefix `https://a2a-protocol.org/extensions/`
- Custom Bindings: repo prefix `cpb-{name}`, URI prefix `https://a2a-protocol.org/bindings/`
- MUST use RFC 2119 language, Apache 2.0 license, have at least one reference implementation
- A2A SDKs SHOULD implement official custom protocol bindings; MAY implement extensions

**Experimental:**
- Extensions: repo prefix `experimental-ext-{name}`
- Custom Bindings: repo prefix `experimental-cpb-{name}`
- Require sponsorship from an A2A Maintainer
- Breaking changes are expected; non-official status must be clearly indicated

### Lifecycle

1. **Proposal:** Open an issue in `a2aproject/A2A` with abstract, motivation, and technical approach
2. **Maintainer Sponsorship:** An A2A Maintainer sponsors and creates the experimental repository
3. **Experimental Development:** Contributors iterate on specification and reference implementations
4. **Graduation to Official:** Requires production-quality implementation, documentation, community adoption, TSC vote (50% quorum, majority approval)
5. **Official Iteration:** Repository maintainers govern day-to-day; breaking changes require new identifier and TSC review
6. **Promotion to Core:** Some extensions/bindings may transition to core protocol via the standard specification change process

### SDK Support

- **Extensions:** A2A SDKs MAY implement extensions, disabled by default, explicit opt-in required
- **Official Custom Bindings:** A2A SDKs SHOULD implement, disabled by default, explicit opt-in required
- SDK maintainers have full autonomy over support decisions; neither is required for protocol conformance
