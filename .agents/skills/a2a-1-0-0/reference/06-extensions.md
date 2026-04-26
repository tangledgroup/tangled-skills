# Extensions

Extensions allow agents to provide additional functionality or data beyond the core A2A specification while maintaining backward compatibility and interoperability.

## Purpose

Extensions enable:
- Additional capabilities such as protocol enhancements or vendor-specific features
- Backward compatibility with clients that don't support specific extensions
- Innovation through experimental or domain-specific features without modifying the core protocol
- A pathway for community-developed features to become part of the core specification

## Scope

Extensions can extend A2A in several ways:

- **Data-only Extensions:** Expose new structured information in the Agent Card without impacting request-response flow. Example: GDPR compliance data.
- **Profile Extensions:** Overlay additional structure and state change requirements on core messages. Example: requiring all messages to use DataParts adhering to a specific schema, or defining substates in metadata.
- **Method Extensions (Extended Skills):** Add entirely new RPC methods beyond the core set. Example: a `task-history` extension adding a `tasks/search` method.
- **State Machine Extensions:** Add new states or transitions to the task state machine.

## Limitations

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

## Extension Activation

Extensions default to inactive. Clients and agents negotiate activation per request:

1. **Client Request:** Client includes `A2A-Extensions` header with comma-separated list of extension URIs
2. **Agent Processing:** Agent identifies supported extensions and activates them
3. **Response:** Agent SHOULD include `A2A-Extensions` header listing successfully activated extensions

**Example request with extensions:**

```http
POST /message:send HTTP/1.1
Host: agent.example.com
Content-Type: application/a2a+json
Authorization: Bearer token
A2A-Extensions: https://example.com/extensions/geolocation/v1,https://standards.org/extensions/citations/v1

{
  "message": {
    "role": "ROLE_USER",
    "parts": [{"text": "Find restaurants near me"}],
    "extensions": ["https://example.com/extensions/geolocation/v1"],
    "metadata": {
      "https://example.com/extensions/geolocation/v1": {
        "latitude": 37.7749,
        "longitude": -122.4194
      }
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

## Required Extensions

When `required: true` is set in the Agent Card, the client must support the extension. If the client does not declare support for a required extension, the agent MUST return `ExtensionSupportRequiredError`.

Agents should not mark data-only extensions as required.

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

## Governance

Official extensions use the `https://a2a-protocol.org/extensions/` URI prefix and are hosted under the `a2aproject` organization with the `ext-` repository prefix (experimental: `experimental-ext-`).

## Example Extensions

- **Secure Passport Extension:** Adds trusted contextual layer for personalization and reduced overhead
- **Timestamp Extension:** Demonstrates augmenting base A2A types by adding timestamps to Message/Artifact metadata
- **Traceability Extension:** Python implementation for tracking task provenance
- **Agent Gateway Protocol (AGP) Extension:** Introduces Autonomous Squads and routes Intent payloads based on declared capabilities
