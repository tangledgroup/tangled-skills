# ⚙️ Plan: authentik-2026-5-0 skill generation

**Depends On:** NONE
**Created:** 2026-05-14T00:00:00Z
**Updated:** 2026-05-14T00:00:00Z
**Current Phase:** ⚙️ Phase 1
**Current Task:** ⚙️ Task 1.2

## ⚙️ Phase 1 Content Research

- ☑ Task 1.1 Fetch installation docs (Docker Compose, Kubernetes/Helm, AWS CloudFormation)
  - Sources: `https://next.goauthentik.io/install-config/install/docker-compose/`, `https://next.goauthentik.io/install-config/configuration/`
- ⚙️ Task 1.2 Fetch providers documentation (OAuth2/OIDC, SAML, LDAP, Proxy, RADIUS, SCIM, RAC, SSF, WS-Fed, Google Workspace, Entra ID)
  - Sources: `https://next.goauthentik.io/providers/` and linked sub-pages
- ☐ Task 1.3 Fetch flows/stages documentation (all stage types, flow designations, executors, context)
  - Sources: `https://next.goauthentik.io/add-secure-apps/flows-stages/stages/`, flow inspector, flow context
- ☐ Task 1.4 Fetch blueprints documentation (structure, YAML tags, models, examples)
  - Sources: `https://next.goauthentik.io/customize/blueprints/v1/structure/`, `https://next.goauthentik.io/customize/blueprints/v1/tags/`, `https://next.goauthentik.io/customize/blueprints/v1/models/`
- ☐ Task 1.5 Fetch sources documentation (LDAP, SAML, OAuth, Kerberos, Plex, Telegram)
  - Sources: `https://next.goauthentik.io/users-sources/` and linked sub-pages
- ☐ Task 1.6 Fetch policies documentation (expression, event_matcher, password, reputation, dummy)
  - Sources: `https://next.goauthentik.io/customize/policies/`
- ☐ Task 1.7 Fetch developer docs (full dev environment, frontend dev, debugging, releases, translations)
  - Sources: `https://next.goauthentik.io/developer-docs/setup/full-dev-environment/`, `https://next.goauthentik.io/developer-docs/setup/frontend-dev-environment/`, `https://next.goauthentik.io/developer-docs/setup/debugging/`
- ☐ Task 1.8 Fetch API schema overview from raw GitHub sources
  - Source: `https://raw.githubusercontent.com/goauthentik/authentik/version/2026.5.0-rc2/schema.yml`

## ☐ Phase 2 Structure Design (depends on: Phase 1)

- ☐ Task 2.1 Determine reference file split based on collected content
  - Target: SKILL.md as overview + navigation hub, 6-8 reference files for progressive disclosure
- ☐ Task 2.2 Draft reference file outline
  - Expected files:
    - `01-installation-configuration.md` — Docker Compose, K8s/Helm, config env vars, HA, air-gapped
    - `02-providers.md` — OAuth2/OIDC, SAML, LDAP, Proxy, RADIUS, SCIM, RAC, SSF, WS-Fed, GWS, Entra ID
    - `03-flows-stages.md` — Flow designations, stage types, executors, bindings, policies
    - `04-sources.md` — LDAP, SAML, OAuth, Kerberos, Plex, Telegram sources
    - `05-blueprints.md` — YAML structure, tags, models, OCI storage, examples
    - `06-development.md` — Dev environment setup, debugging, contributing, testing, releasing
    - `07-api.md` — API overview, schema, OpenAPI, client usage

## ☐ Phase 3 Write SKILL.md (depends on: Phase 2)

- ☐ Task 3.1 Write YAML header with validated name, description, tags, version
  - Name: `authentik-2026-5-0`, version: `0.1.0`
- ☐ Task 3.2 Write Overview section covering authentik as open-source IdP/SSO platform
- ☐ Task 3.3 Write When to Use section with specific trigger scenarios
- ☐ Task 3.4 Write Core Concepts section (Flows/Stages/Policies, Applications/Providers, Blueprints, Outposts, Sources)
- ☐ Task 3.5 Write quick-start examples (Docker Compose install, basic flow config)
- ☐ Task 3.6 Write Advanced Topics navigation hub linking to all reference files

## ☐ Phase 4 Write Reference Files (depends on: Phase 2)

- ☐ Task 4.1 Write `reference/01-installation-configuration.md`
  - Docker Compose, Kubernetes/Helm, AWS, env vars, upgrade, HA, reverse proxy, air-gapped
- ☐ Task 4.2 Write `reference/02-providers.md`
  - All provider types with configuration patterns, property mappings, SLO
- ☐ Task 4.3 Write `reference/03-flows-stages.md`
  - Flow designations, all stage types, executors, bindings, policy engine modes
- ☐ Task 4.4 Write `reference/04-sources.md`
  - LDAP source, SAML source, OAuth source, Kerberos, Plex, Telegram, SCIM provisioning
- ☐ Task 4.5 Write `reference/05-blueprints.md`
  - YAML structure, !Context tags, model references, OCI storage, examples
- ☐ Task 4.6 Write `reference/06-development.md`
  - Full dev env, frontend-only env, debugging, contributing guidelines, testing, releases
- ☐ Task 4.7 Write `reference/07-api.md`
  - API schema, OpenAPI spec, authentication, client usage patterns

## ☐ Phase 5 Validate and Finalize (depends on: Phase 3, Phase 4)

- ☐ Task 5.1 Run structural validator
  - Command: `bash scripts/validate-skill.sh .agents/skills/authentik-2026-5-0`
- ☐ Task 5.2 LLM judgment checks — content accuracy, terminology consistency, no hallucination, concise writing
- ☐ Task 5.3 Verify SKILL.md under 500 lines and all references one level deep
- ☐ Task 5.4 Run `bash scripts/gen-skills-table.sh` to regenerate README.md skills table
- ☐ Task 5.5 Final report with file tree and validation results
