# Agent Discovery

To collaborate using the A2A protocol, AI agents need to first find each other and understand their capabilities. A2A standardizes agent self-descriptions through the Agent Card. However, discovery methods for these Agent Cards vary by environment and requirements.

## The Role of the Agent Card

The Agent Card is a JSON document that serves as a digital "business card" for an A2A Server (the remote agent). It is crucial for agent discovery and interaction.

Key information included:
- **Identity:** `name`, `description`, and `provider` information
- **Service Endpoint:** Specifies the URL(s) for the A2A service via `supportedInterfaces`
- **A2A Capabilities:** Lists supported features such as `streaming` or `pushNotifications`
- **Authentication:** Details the required schemes (e.g., "Bearer", "OAuth2")
- **Skills:** Describes the agent's tasks using `AgentSkill` objects, including `id`, `name`, `description`, `inputModes`, `outputModes`, and `examples`

Client agents use the Agent Card to determine an agent's suitability, structure requests, and ensure secure communication.

## Discovery Strategies

### 1. Well-Known URI

Recommended for public agents or agents intended for broad discovery within a specific domain.

- **Mechanism:** A2A Servers host their Agent Card at a standardized `well-known` URI on their domain: `https://{agent-server-domain}/.well-known/agent-card.json`, following RFC 8615.
- **Process:**
  1. Client knows or programmatically discovers the domain of a potential A2A Server (e.g., `smart-thermostat.example.com`)
  2. Client performs HTTP GET to `https://smart-thermostat.example.com/.well-known/agent-card.json`
  3. If the Agent Card exists and is accessible, the server returns it as a JSON response
- **Advantages:** Ease of implementation, adheres to standards, facilitates automated discovery
- **Considerations:** Best suited for open or domain-controlled discovery scenarios. Authentication is necessary at the endpoint if the card contains sensitive details.

### 2. Curated Registries (Catalog-Based Discovery)

Employed in enterprise environments or public marketplaces, where Agent Cards are managed by a central registry.

- **Mechanism:** An intermediary service (the registry) maintains a collection of Agent Cards. Clients query this registry to find agents based on criteria such as skills, tags, provider name, or capabilities.
- **Process:**
  1. A2A Servers publish their Agent Cards to the registry
  2. Client agents query the registry's API and search by criteria (e.g., "specific skills")
  3. Registry returns matching Agent Cards or references
- **Advantages:** Centralized management and governance, capability-based discovery, support for access controls and trust frameworks, applicable in both private and public marketplaces
- **Considerations:** Requires deployment and maintenance of a registry service. The current A2A specification does not prescribe a standard API for curated registries.

### 3. Direct Configuration / Private Discovery

Used for tightly coupled systems, private agents, or development purposes.

- **Mechanism:** Client applications utilize hardcoded details, configuration files, environment variables, or proprietary APIs for discovery.
- **Process:** Specific to the application's deployment and configuration strategy.
- **Advantages:** Straightforward for establishing connections within known, static relationships.
- **Considerations:** Inflexible for dynamic discovery. Changes to Agent Card information necessitate client reconfiguration.

## Securing Agent Cards

Agent Cards may include sensitive information, such as URLs for internal or restricted agents or descriptions of sensitive skills.

### Protection Mechanisms

- **Authenticated Agent Cards:** Use authenticated extended agent cards for sensitive information or for serving a more detailed version of the card
- **Secure Endpoints:** Implement access controls on the HTTP endpoint serving the Agent Card:
  - Mutual TLS (mTLS)
  - Network restrictions (e.g., IP ranges)
  - HTTP Authentication (e.g., OAuth 2.0)
- **Registry Selective Disclosure:** Registries return different Agent Cards based on the client's identity and permissions

Any Agent Card containing sensitive data must be protected with authentication and authorization mechanisms. The A2A specification strongly recommends the use of out-of-band dynamic credentials rather than embedding static secrets within the Agent Card.

## Caching Considerations

Agent Cards describe an agent's capabilities and typically change infrequently — for example, when skills are added or authentication requirements are updated. Applying standard HTTP caching practices to Agent Card endpoints reduces unnecessary network requests while ensuring clients eventually receive updated information.

### Server Guidance

- Agent Card HTTP endpoints SHOULD include a `Cache-Control` response header with a `max-age` directive appropriate for the agent's expected update frequency
- Agent Card HTTP endpoints SHOULD include an `ETag` response header derived from the Agent Card's `version` field or a hash of the card content
- Agent Card HTTP endpoints MAY include a `Last-Modified` response header

### Client Guidance

- Clients SHOULD honor HTTP caching semantics as defined in RFC 9111 when fetching Agent Cards
- When a cached Agent Card has expired, clients SHOULD use conditional requests (`If-None-Match` with the stored `ETag`, or `If-Modified-Since`) to avoid re-downloading unchanged cards
- When the server does not include caching headers, clients MAY apply an implementation-specific default cache duration
- For Extended Agent Cards, clients should also follow session-scoped caching guidance

## Protocol Selection from Agent Card

When an Agent Card declares multiple `supportedInterfaces`, clients MUST:

1. Parse `supportedInterfaces` if present, and select the first supported transport
2. Prefer earlier entries in the ordered list when multiple options are supported
3. Use the correct URL for the selected transport

The first entry represents the agent's preferred interface. URLs MAY be reused if multiple transports are available at the same endpoint.
