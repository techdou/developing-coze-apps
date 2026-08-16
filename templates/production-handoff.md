# Production Handoff Template

Use after a successful production deploy or before transferring ownership.

## 1. Release identity

- Project:
- Repository:
- Production commit/tag:
- Deploy time:
- Production URL/domain:
- Coze project/workspace:
- CLI/runtime version verified:

## 2. Resource bindings

Use safe labels/IDs only. Do not paste secret values.

| Resource | Production identity/label | Ownership | Verified by |
|---|---|---|---|
| Database |  | platform/app |  |
| Auth |  | platform/app |  |
| Object storage |  | platform/app |  |
| Domain |  | platform/user |  |
| External API(s) |  | app |  |

## 3. Environment variables

| Variable name | Class | Configured in PROD | Rotation owner | Notes |
|---|---|---|---|---|
|  | platform_injected / app_private / client_public |  |  |  |

Never include values in this handoff.

## 4. Database state

- Migration version(s):
- Backup/export taken:
- Reference seed/import applied:
- DEV business data copied? default = no
- If yes, approved table/row scope:
- Rollback/restore procedure:

## 5. Object-storage state

- Production bucket/binding verified:
- Curated asset promotion manifest:
- Object key/checksum validation result:
- Temporary/signed URLs persisted in DB? must be no

## 6. Auth and first-admin

- Auth tenant verified:
- Bootstrap mechanism exists? yes/no
- Bootstrap completed? yes/no/not-applicable
- Admin identity verified:
- Bootstrap token/path restricted or rotated after use:
- Any DEV/default admin found in PROD? must explain if yes

## 7. Smoke-test result

| Test | Result | Evidence/notes |
|---|---|---|
| Health/app load |  |  |
| Login/logout |  |  |
| RBAC/permission denial |  |  |
| CRUD disposable record |  |  |
| Storage upload/read/delete |  |  |
| AI/model normal request |  |  |
| AI/model handled failure |  |  |
| Runtime public config |  |  |
| CSP/connect/frame policy |  |  |
| Mobile/basic browser check |  |  |

## 8. Operational ownership

- Production owner:
- Secret rotation owner:
- Database backup owner:
- Incident contact/process:
- Log/audit retention:
- Quota/cost monitoring:

## 9. Known risks / deferred work

| Severity | Risk | User impact | Mitigation/next step |
|---|---|---|---|
|  |  |  |  |

## 10. Final status

- [ ] P0 findings resolved.
- [ ] DEV/PROD resource identity verified.
- [ ] No `.env.local`/DEV defaults act as production source of truth.
- [ ] Production data-sync decision documented.
- [ ] Migrations + rollback documented.
- [ ] Bootstrap completed safely or marked not applicable.
- [ ] Smoke tests passed.
- [ ] Handoff contains no secret values.

Status: READY / READY_WITH_KNOWN_RISKS / NOT_READY
