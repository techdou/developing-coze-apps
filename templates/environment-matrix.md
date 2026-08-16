# DEV / PROD Environment Matrix Template

Fill this before implementing persistent features or production deployment.

## Project identity

- Project/repository:
- Release commit:
- Coze project/workspace:
- Selected Coze layer:
- Last runtime verification time:
- Current `coze --version`:

## Resource matrix

| Resource | DEV identity/source | PROD identity/source | Ownership | Isolated? | Promotion / setup action | Verification |
|---|---|---|---|---|---|---|
| Runtime/project |  |  | platform_injected |  | deploy same reviewed commit |  |
| Database |  |  | platform_injected / app |  | migrations |  |
| Auth tenant |  |  | platform_injected / app |  | bootstrap/admin flow |  |
| Object storage |  |  | platform_injected / app |  | explicit asset manifest |  |
| App-private secrets |  |  | app_private | yes | configure independent values |  |
| Browser-public config |  |  | client_public |  | build/runtime allowlist |  |
| Domain/origin |  |  | platform/user |  | configure/verify |  |
| External API |  |  | app_private | recommended | independent key/quota |  |
| Logs/analytics |  |  | app/platform |  | production retention policy |  |

Ownership values:

- `platform_injected`
- `app_private`
- `client_public`
- `local_only`

Unknown facts must be marked `needs_runtime_check`.

## Variable registry

Never put secret values in this file.

| Variable name | Class | DEV source | PROD source | Browser visible | Required | Notes |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

## Database promotion decision

- [ ] Production DB binding verified.
- [ ] DEV→PROD ordinary data sync is OFF by default.
- [ ] Schema changes are represented by versioned migrations.
- [ ] Production-safe reference seed/import is explicitly listed.
- [ ] Any business-data import has table/row allowlist and backup plan.
- [ ] Auth users/sessions are not copied from DEV unless an explicit migration is approved.

### Approved production data promotion

| Dataset/table | Type: schema/reference/business | Source | Target | Reason | Approval/verification |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Object-storage promotion decision

- [ ] Production bucket/binding verified.
- [ ] Application persists object keys, not expiring signed URLs.
- [ ] DEV object keys are not assumed to exist in PROD.
- [ ] Required curated assets are listed below.

| Logical asset | DEV key/source | PROD key | Content type | Checksum/size | Verification |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Auth/bootstrap

- Does the project implement first-admin bootstrap? yes / no
- Evidence/code path:
- Project-specific variables:
- Production admin identity:
- One-time protection mechanism:
- Idempotency behavior:
- Post-bootstrap restriction/rotation:

## Build-time / runtime public config

| Config | Build-time client value? | Runtime server value? | Runtime public endpoint? | PROD verified? |
|---|---|---|---|---|
|  |  |  |  |  |

## Release blockers

| Severity | Blocker | Owner | Resolution |
|---|---|---|---|
| P0 |  |  |  |
