# Providers

## Contents
- Provider Overview
- OAuth2/OIDC Provider
- SAML Provider
- LDAP Provider
- Proxy Provider
- RADIUS Provider
- SCIM Provider
- RAC (Remote Access Control) Provider
- SSF Provider
- WS-Federation Provider
- Google Workspace Provider
- Microsoft Entra ID Provider
- Property Mappings
- Single Logout

## Provider Overview

A provider is an authentication method used by authentik to authenticate users for associated applications. Providers and applications typically have a 1-to-1 relationship. Create via **Applications > Applications > New Application** (creates app + provider together) or **Applications > Providers > New Provider**.

Each provider type requires selecting flows: authorization flow (what happens when user accesses the app) and invalidation flow (logout behavior).

## OAuth2/OIDC Provider

Full OAuth 2.0 and OpenID Connect support. authentik acts as the OP (OpenID Provider/IdP). Supports all standard flows: authorization code, client_credentials, implicit, hybrid, device code. Features PKCE, automatic refresh token rotation, configurable encryption, and short expiration times.

**Creation**: Applications > Applications > New Application > select OAuth2/OIDC as provider type.

**Key configuration**:
- `client_type`: confidential, public
- `client_id` / `client_secret`
- `redirect_uris`: allowed callback URLs
- Scope mappings: define what claims are returned per scope
- `offline_access` scope mapping needed for refresh tokens

**Machine-to-machine (client_credentials)**: Create a service account user, grant it access to the OAuth2 application, use client credentials flow with that user's identity.

**Device code flow**: For devices without browsers. Users authenticate on a separate device using a code displayed on the target device.

**GitHub compatibility**: Special endpoint mode for GitHub-compatible clients that don't fully support OIDC.

**WebFinger**: Supports WebFinger discovery at `/.well-known/webfinger`.

## SAML Provider

SAML 2.0 Identity Provider. Create by specifying SP details directly or uploading SP metadata XML (contains SP certificate, entity ID, ACS URL, logout URL).

**Key configuration**:
- Entity ID
- Assertion Consumer Service URL
- NameID format
- Signing/encryption certificates
- Attribute mappings via property mappings

## LDAP Provider

Provides LDAP access to authentik users/groups via an LDAP outpost. The outpost is a separate Go application that uses the authentik server as backend.

**Key configuration**:
- Base DN (e.g., `dc=example,dc=com`)
- Bind DN for service accounts
- Property mappings control which attributes are exposed
- Listens on port 3389 (LDAP) and 6636 (LDAPS) by default

## Proxy Provider

Identity-aware reverse proxy via a Go-based outpost (forked from oauth2_proxy). Proxies HTTP requests and injects authentication headers into backend applications.

**Key configuration**:
- Authentication headers (e.g., `X-Authentik-Username`, `X-Authentik-Email`)
- Authorization header forwarding
- Cookie settings for session persistence
- Deployed as a separate outpost container

## RADIUS Provider

RADIUS authentication server via a Go-based outpost. Supports PAP, CHAP, MS-CHAPv2, and EAP methods. For applications that don't support other protocols.

**Key configuration**:
- Shared secret between NAS and RADIUS server
- Authentication flow selection
- Accounting support

## SCIM Provider

SCIM 2.0 for provisioning users and groups from authentik into other applications. Supports create, update, deactivate, delete operations via RESTful endpoints.

**Key configuration**:
- Provisioning lifecycle mapping
- Property mappings for attribute sync
- Authentication method for incoming SCIM requests

## RAC (Remote Access Control) Provider

Remote access control using a single application and provider with multiple "endpoints" (each endpoint defines a remote machine). Uses WebSocket-based tunneling.

**Key configuration**:
- Endpoint definitions per remote machine
- Authorization flow per endpoint
- Network access policies

## SSF Provider

SSF (Session Sharing Framework) provider for sharing authentication sessions across applications. Enterprise feature.

## WS-Federation Provider

WS-Federation protocol support for legacy enterprise applications, particularly Microsoft ecosystems.

## Google Workspace Provider

Specialized provider for Google Workspace integration with provisioning and synchronization capabilities.

## Microsoft Entra ID Provider

Specialized provider for Microsoft Entra ID (Azure AD) integration with provisioning and synchronization.

## Property Mappings

Control what data is exposed to applications from authentik users. Each provider type has its own property mapping schema. Default mappings are included; create custom ones to expose additional attributes or transform data.

## Single Logout

Logs users out of all active applications when they log out of authentik. Combines OAuth2/OIDC front-channel and back-channel logout with SAML Single Logout specification.

**Default behavior**: `default-provider-invalidation-flow` does not include User Logout stage — only the specific app session ends. Enable full SLO by adding a User Logout stage to the provider invalidation flow.
