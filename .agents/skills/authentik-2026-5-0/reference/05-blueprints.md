# Blueprints

## Contents
- Blueprint Overview
- YAML File Structure
- Custom YAML Tags
- Model References
- Storage Backends
- Applying Blueprints
- Example

## Blueprint Overview

Blueprints are YAML files that template, automate, and distribute authentik configuration. They manage default flows, system objects, and custom configurations. All entries process within a single atomic database transaction — full rollback on any error.

**Schema**: `https://goauthentik.io/blueprints/schema.json`. Per-version: `https://version-2023-4.goauthentik.io/blueprints/schema.json`.

VS Code support: add `# yaml-language-server: $schema=https://goauthentik.io/blueprints/schema.json` at the top of files. Register custom tags in `settings.json`.

## YAML File Structure

```yaml
version: 1
metadata:
  name: example-blueprint
  labels:
    foo: bar
context:
  instance_name: my-instance
entries:
  - identifiers:
      slug: my-flow
    model: authentik_flows.flow
    attrs:
      name: My Flow
      designation: authentication
```

**Required fields**: `version` (currently 1), `entries` (list of objects).

**Optional fields**: `metadata` (with `name` and `labels`), `context` (default values merged with instance context).

Each entry has:
- `identifiers`: unique lookup keys (e.g., `slug`)
- `model`: Django model path (e.g., `authentik_flows.flow`, `authentik_core.application`)
- `attrs`: field values to set. Only required fields should be specified; omit defaults to allow overriding.
- `id`: optional internal reference ID for cross-references within the blueprint

**Entry order matters** when using `!KeyOf` — tags evaluate in document order.

## Custom YAML Tags

Register these custom tags in your editor (VS Code `settings.json`):

```json
"yaml.customTags": [
  "!Condition sequence", "!Context scalar", "!Enumerate sequence",
  "!Env scalar", "!File scalar", "!File sequence", "!Find sequence",
  "!FindObject sequence", "!Format sequence", "!If sequence",
  "!Index scalar", "!KeyOf scalar", "!Value scalar", "!AtIndex scalar"
]
```

### Tag Reference

| Tag | Purpose | Example |
|---|---|---|
| `!KeyOf` | Resolve primary key of entry by internal id | `!KeyOf my-policy-id` |
| `!Context` | Lookup value from context, optional default | `!Context foo` or `!Context [foo, default]` |
| `!Env` | Read environment variable, optional default | `!Env MY_VAR` or `!Env MY_VAR, default` |
| `!File` | Read file contents, optional default | `!File /path/to/file` |
| `!Find` | Lookup model by key=value pairs, returns PK | `!Find [authentik_flows.flow, [slug, default-authentication-flow]]` |
| `!FindObject` | Lookup model, returns serialized data (2025.8.0+) | `!FindObject [authentik_flows.flow, [slug, x]]` |
| `!AtIndex` | Access attribute from object by key | `!AtIndex [!FindObject [...], designation]` |
| `!Format` | Python % string formatting | `!Format ["policy-%s", !Context name]` |
| `!If` | Conditional: `[condition, when_true, when_false]` or short `[condition]` | `required: !If [true]` |
| `!Condition` | Evaluate condition for use in `!If` | `!Condition [...]` |
| `!Enumerate` | Iterate over a list | Sequence tag |
| `!Index` | Index into a sequence | Scalar tag |
| `!Value` | Extract value from mapping | Scalar tag |

### Built-in Context Variables

- `goauthentik.io/enterprise/licensed`: Boolean — enterprise license active
- `goauthentik.io/rbac/models`: Dictionary of available RBAC models

Use in conditions: `- !Context goauthentik.io/enterprise/licensed`

## Model References

Key model paths used in blueprints:

| Model | Path |
|---|---|
| Flow | `authentik_flows.flow` |
| Stage | `authentik_stages_<type>.<type>stage` |
| Application | `authentik_core.application` |
| OAuth2 Provider | `authentik_providers_oauth2.oauth2provider` |
| SAML Provider | `authentik_providers_saml.samlprovider` |
| LDAP Provider | `authentik_providers_ldap.ldapprovider` |
| Proxy Provider | `authentik_providers_proxy.proxyprovider` |
| Policy | `authentik_policies_<type>.<type>policy` |
| User | `authentik_users.user` |
| Group | `authentik_users.group` |

Full model list available at the API schema and blueprint models documentation.

## Storage Backends

**Local file**: Mount YAML to `/blueprints/` in the container. Subdirectories: `/blueprints/default`, `/blueprints/example`, `/blueprints/system`. File modification triggers automatic re-apply. Discovery is event-driven (inotify).

**OCI registry**: Store blueprints in OCI-compliant registries (GHCR, Docker Hub). Path format: `oci://ghcr.io/<user>/blueprint/<name>:<tag>`. Push with ORAS:

```bash
oras push ghcr.io/user/blueprint/my-bp:latest blueprint.yaml:application/vnd.goauthentik.blueprint.v1+yaml
```

Private registries support embedded credentials in the URL.

**In-database**: Store blueprints internally, manageable via Terraform or API. Modifying content triggers reconciliation.

## Applying Blueprints

**Blueprint instance**: Regularly applied (every 60 minutes). Supports context key:value attributes per instance. Multiple instances per file. Auto-discovered from `/blueprints/`.

**Imported flow**: One-time import via UI (**Flows > Import** or **Blueprints > Import**). Not monitored after import. Select from local paths (bundled examples) or upload `.yaml` files.

To revert a modified default flow: delete the modified flow, then re-apply the blueprint.

## Example — Default Authentication Flow Blueprint

```yaml
version: 1
metadata:
  name: Default - Authentication flow
entries:
  - identifiers:
      slug: default-authentication-flow
    model: authentik_flows.flow
    attrs:
      designation: authentication
      name: Welcome to authentik!
      title: Welcome to authentik!
    id: flow

  - identifiers:
      slug: default-authentication-identification
    model: authentik_stages_identification.identificationstage
    attrs:
      name: default-authentication-identification
      user_fields:
        - username
        - email
    id: stage-identification

  - identifiers:
      name: default-authentication-identification
    model: authentik_flows.stagebinding
    attrs:
      flow: !KeyOf flow
      stage: !KeyOf stage-identification
      order: 1
```
