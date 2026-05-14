# Sources

## Contents
- Source Overview
- LDAP/Active Directory Sources
- SAML Sources
- OAuth/OIDC Social Login Sources
- Kerberos Sources
- SCIM Sources
- Plex Sources
- Property Mappings
- Adding Sources to Login Page

## Source Overview

Sources connect authentik to external user directories or identity providers. They sync users and groups into authentik for use with providers. Sources are used as the RP (Relying Party) — they consume identity from external systems, whereas providers act as the OP (OpenID Provider).

**Categories**:
- **Protocols**: LDAP/AD, SAML, OAuth/OIDC, Kerberos, SCIM
- **Social logins**: Apple, Discord, GitHub, Google, Twitch, Twitter, and others
- **Directory synchronization**: Active Directory, FreeIPA

## LDAP/Active Directory Sources

Sync users and groups from OpenLDAP or Active Directory into authentik.

**Key configuration**:
- Server URL(s) with port (389 for LDAP, 636 for LDAPS)
- Base DN for search scope
- Bind DN and password for service account authentication
- Search filters for users and groups
- TLS/SSL settings with configurable ciphers (`AUTHENTIK_LDAP__TLS__CIPHERS`)
- Synchronization schedule (background task)
- Page size controlled by `AUTHENTIK_LDAP__PAGE_SIZE` (default 50)
- Task timeout via `AUTHENTIK_LDAP__TASK_TIMEOUT_HOURS` (default 2 hours)

**Directory sync**: Active Directory and FreeIPA have dedicated synchronization modes that handle schema-specific attributes and group nesting.

## SAML Sources

Authenticate users via an external SAML Identity Provider. Used for enterprise SSO where another IdP is the authority of record.

**Key configuration**:
- IdP metadata URL or XML upload
- Entity ID
- Assertion Consumer Service binding
- NameID format mapping
- Attribute mappings via property mappings

## OAuth/OIDC Social Login Sources

Connect social login providers (Google, GitHub, Apple, Discord, Twitch, Twitter, etc.) as authentication sources. authentik acts as the OAuth/RP client.

**Key configuration**:
- Client ID and Client Secret from the provider
- Redirect URI (authentik-generated)
- Scopes requested from the provider
- Property mappings to transform incoming claims into authentik user attributes

## Kerberos Sources

Sync Kerberos users into authentik. Used in enterprise environments with Active Directory Kerberos infrastructure.

**Key configuration**:
- KDC server address
- Realm
- Keytab file or service principal credentials

## SCIM Sources

Provision users from external SCIM providers into authentik. Supports SCIM 2.0 create, update, deactivate, delete operations.

## Plex Sources

Sync users from a Plex media server into authentik for home lab authentication scenarios.

## Property Mappings

Source property mappings define how data is imported from the external source into authentik user attributes. Each source type has default mappings; create custom ones to:
- Map external attributes to authentik fields
- Transform data during import (e.g., format email addresses)
- Sync group memberships
- Set custom user attributes

## Adding Sources to Login Page

To display a source on the default login screen:

1. Navigate to **Flows and Stages > Flows**
2. Open `default-authentication-flow`
3. Go to **Stage Bindings** tab
4. Edit the identification stage
5. Add sources to **Selected sources** under Source settings

Users can then select the source on the login page to authenticate via that external directory.
