# Architecture and Overview

## Model Context Protocol

Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. The specification defines authoritative protocol requirements based on the TypeScript schema in the MCP GitHub repository.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" are interpreted as described in BCP 14 (RFC2119, RFC8174) when they appear in all capitals.

## Architecture

MCP follows a **client-host-server** architecture where each host can run multiple client instances. Built on JSON-RPC, MCP provides a stateful session protocol focused on context exchange and sampling coordination.

### Core Components

#### Host

The host process acts as the container and coordinator:

- Creates and manages multiple client instances
- Controls client connection permissions and lifecycle
- Enforces security policies and consent requirements
- Handles user authorization decisions
- Coordinates AI/LLM integration and sampling
- Manages context aggregation across clients

#### Clients

Each client is created by the host and maintains an isolated server connection:

- Establishes one stateful session per server
- Handles protocol negotiation and capability exchange
- Routes protocol messages bidirectionally
- Manages subscriptions and notifications
- Maintains security boundaries between servers

A host application creates and manages multiple clients, with each client having a 1:1 relationship with a particular server.

#### Servers

Servers provide specialized context and capabilities:

- Expose resources, tools, and prompts via MCP primitives
- Operate independently with focused responsibilities
- Request sampling through client interfaces
- Must respect security constraints
- Can be local processes or remote services

## Design Principles

MCP is built on several key design principles:

- **Servers should be extremely easy to build**: Host applications handle complex orchestration. Servers focus on specific, well-defined capabilities with simple interfaces.

- **Servers should be highly composable**: Each server provides focused functionality in isolation. Multiple servers combine seamlessly through a shared protocol.

- **Servers cannot read the full conversation or see into other servers**: Servers receive only necessary contextual information. Full conversation history stays with the host. Each server connection maintains isolation.

- **Features can be added progressively**: Core protocol provides minimal required functionality. Additional capabilities are negotiated as needed, maintaining backwards compatibility.

## Capability Negotiation

MCP uses a capability-based negotiation system where clients and servers explicitly declare their supported features during initialization. Capabilities determine which protocol features and primitives are available during a session.

- Servers declare capabilities like resource subscriptions, tool support, and prompt templates
- Clients declare capabilities like sampling support and notification handling
- Both parties must respect declared capabilities throughout the session
- Additional capabilities can be negotiated through extensions

Each capability unlocks specific protocol features:

- Implemented server features must be advertised in the server's capabilities
- Emitting resource subscription notifications requires the server to declare subscription support
- Tool invocation requires the server to declare tool capabilities
- Sampling requires the client to declare support

## Key Protocol Details

### Base Protocol

- JSON-RPC message format
- Stateful connections
- Server and client capability negotiation

### Server Features (Servers offer to Clients)

- **Resources**: Context and data for the user or AI model
- **Prompts**: Templated messages and workflows for users
- **Tools**: Functions for the AI model to execute

### Client Features (Clients offer to Servers)

- **Sampling**: Server-initiated agentic behaviors and recursive LLM interactions
- **Roots**: Server-initiated inquiries into URI or filesystem boundaries
- **Elicitation**: Server-initiated requests for additional information from users

### Additional Utilities

- Configuration
- Progress tracking
- Cancellation
- Error reporting
- Logging

## Security and Trust & Safety

MCP enables powerful capabilities through arbitrary data access and code execution paths. All implementors must carefully address security considerations.

### Key Principles

- **User Consent and Control**: Users must explicitly consent to and understand all data access and operations. They must retain control over what data is shared and what actions are taken. Implementors should provide clear UIs for reviewing and authorizing activities.

- **Data Privacy**: Hosts must obtain explicit user consent before exposing user data to servers. Hosts must not transmit resource data elsewhere without user consent. User data should be protected with appropriate access controls.

- **Tool Safety**: Tools represent arbitrary code execution and must be treated with appropriate caution. Descriptions of tool behavior such as annotations should be considered untrusted unless obtained from a trusted server. Hosts must obtain explicit user consent before invoking any tool.

- **LLM Sampling Controls**: Users must explicitly approve any LLM sampling requests. Users should control whether sampling occurs, the actual prompt sent, and what results the server can see. The protocol intentionally limits server visibility into prompts.

### Implementation Guidelines

Implementors SHOULD:

- Build robust consent and authorization flows
- Provide clear documentation of security implications
- Implement appropriate access controls and data protections
- Follow security best practices in integrations
- Consider privacy implications in feature designs

## Changelog (2025-11-25)

### Major Changes

- Enhanced authorization server discovery with OpenID Connect Discovery 1.0 support
- Servers can expose icons as metadata for tools, resources, resource templates, and prompts
- Enhanced authorization flows with incremental scope consent via WWW-Authenticate
- Added guidance on tool names
- Updated ElicitResult and EnumSchema for standards-based approach with titled, untitled, single-select, and multi-select enums
- Added URL mode elicitation support
- Added tool calling support to sampling via `tools` and `toolChoice` parameters
- Added OAuth Client ID Metadata Documents as recommended client registration mechanism
- Added experimental tasks support for tracking durable requests with polling and deferred result retrieval

### Minor Changes

- Clarified that servers using stdio transport may use stderr for all types of logging
- Added optional `description` field to `Implementation` interface
