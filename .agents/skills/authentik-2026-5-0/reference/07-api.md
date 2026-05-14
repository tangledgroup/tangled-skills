# API Reference

## Contents
- API Overview
- OpenAPI Schema
- Authentication
- Key Resource Groups
- Client Usage Patterns

## API Overview

authentik exposes a RESTful API with 1139 endpoints documented via OpenAPI 3.0.3. The schema is available at `https://api.goauthentik.io` and as raw YAML in the repository (`schema.yml`).

**Base URL**: `https://<your-authentik-instance>/api/v3/`

All API responses are JSON. Authentication via OAuth2 bearer token or session cookie.

## OpenAPI Schema

- **Schema URL**: `https://goauthentik.io/api/schema.yml`
- **Interactive docs**: `https://api.goauthentik.io`
- **Per-version**: Check the repository tag for version-specific schemas

The schema follows standard OpenAPI 3.0 conventions with:
- `operationId` for every endpoint
- Tag-based grouping (stages, sources, providers, etc.)
- Standard error responses (`ValidationErrorResponse`, `GenericErrorResponse`)
- Search, ordering, and pagination parameters on list endpoints

## Authentication

**OAuth2 Bearer Token** (recommended): Obtain a token via the OAuth2 provider's token endpoint, then include in `Authorization: Bearer <token>` header.

**Session Cookie**: Browser-based sessions work automatically when accessing the API from the same origin.

**Service Account**: Create a user, assign it to an OAuth2 application with client_credentials grant type, use the credentials to obtain tokens programmatically.

## Key Resource Groups

| Tag | Endpoint Count | Description |
|---|---|---|
| `stages` | 210 | All stage types (identification, password, email, authenticators, etc.) |
| `sources` | 173 | LDAP, SAML, OAuth, Kerberos, SCIM sources and their operations |
| `providers` | 125 | OAuth2, SAML, LDAP, Proxy, RADIUS, SCIM providers |
| `propertymappings` | 111 | Source and provider property mappings |
| `authenticators` | 83 | TOTP, WebAuthn, Duo, static key authenticator management |
| `policies` | 76 | Expression, GeoIP, password, reputation policies |
| `endpoints` | 70 | Flow endpoints, execution, context inspection |
| `core` | 69 | Users, groups, applications, brands, certificates |
| `outposts` | 34 | Outpost deployment and management |
| `events` | 33 | Event log, notifications, audit trail |
| `rbac` | 22 | Role-based access control permissions |
| `flows` | 22 | Flow definitions, bindings, planning |
| `tenants` | 14 | Multi-tenant configuration |
| `admin` | 14 | System administration (apps, files, metrics) |
| `rac` | 13 | Remote Access Control endpoints |
| `oauth2` | 12 | OAuth2-specific operations (tokens, authorization) |
| `tasks` | 10 | Background task management |
| `managed` | 10 | Managed object lifecycle |
| `lifecycle` | 10 | System lifecycle operations |
| `crypto` | 10 | Certificate and key management |
| `enterprise` | 10 | Enterprise-only features |
| `ssf` | 3 | Session Sharing Framework |
| `reports` | 3 | CSV report generation |

## Client Usage Patterns

**List with search**:
```
GET /api/v3/core/users/?search=john&ordering=username
```

**Retrieve by slug**:
```
GET /api/v3/flows/flows/?slug=default-authentication-flow
```

**Create resource**:
```
POST /api/v3/core/applications/
Content-Type: application/json

{
  "name": "My App",
  "slug": "my-app",
  "provider": "/api/v3/providers/oauth2/oauth2-provider/<uuid>/"
}
```

**Common parameters on list endpoints**:
- `search`: Full-text search across searchable fields
- `ordering`: Sort field (prefix with `-` for descending)
- `page` / `page_size`: Pagination control
- `annotation__...`: Annotate results with computed values
