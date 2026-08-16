# Architecture Blueprint Template

Use this template for Coze Coding / Coze hybrid planning. For any persistent project, complete the environment sections before implementation.

## 1. Project summary

- Project name:
- Business/education goal:
- Primary users:
- Coze layer: Coze Coding / Agent / Workflow / Skill / Hybrid
- Confidence: confirmed_official / runtime_verified / environment_specific / needs_runtime_check

## 2. Scope

| Priority | Feature | Reason | Not included yet |
|---|---|---|---|
| Must |  |  |  |
| Should |  |  |  |
| Later |  |  |  |

## 3. DEV / PROD environment design

Complete `templates/environment-matrix.md` and summarize here.

| Resource | DEV | PROD | Ownership | Promotion strategy | Verification |
|---|---|---|---|---|---|
| Database |  |  |  | migrations |  |
| Auth |  |  |  | bootstrap/admin flow |  |
| Object storage |  |  |  | explicit asset manifest |  |
| App-private env |  |  | app_private | independent values |  |
| Client-public env |  |  | client_public | build/runtime |  |
| Domain |  |  |  | configure/verify |  |

Default: schema promotes; ordinary DEV data does not.

## 4. Roles and permissions

| Role | Can view | Can create/update | Can export/delete | Notes |
|---|---|---|---|---|

## 5. Pages/routes

| Route | Page | Core actions | Data/API | Auth |
|---|---|---|---|---|

## 6. Data model

| Table | Purpose | Key fields | Relationships | RLS/RBAC | Risks |
|---|---|---|---|---|---|

Conventions:

- snake_case columns where consistent with project style.
- `id`, `created_at`, `updated_at` by default when appropriate.
- Avoid update/delete without explicit filters.
- Keep ordered migrations in source control.
- Classify seed data: reference / demo / privileged / migration-support / business.
- Never rely on DEV rows existing in PROD.

## 7. Database migration and seed plan

- Migration location/versioning:
- Production backup requirement:
- Reference seed data:
- DEV→PROD business-data sync decision: default `OFF`
- Approved exceptions:
- Rollback/restore path:

## 8. Storage model

| Asset | DEV key/source | PROD key/source | DB reference | Access pattern | Promotion |
|---|---|---|---|---|---|

Rules:

- store object keys/IDs, not temporary signed URLs;
- DEV key existence does not imply PROD object existence;
- promote curated assets through an explicit manifest.

## 9. Environment-variable registry

Never put values here.

| Variable | Class | DEV source | PROD source | Client-visible | Required |
|---|---|---|---|---|---|
|  | platform_injected / app_private / client_public / local_only |  |  |  |  |

## 10. Auth / first-admin initialization

- Public registration enabled? 
- First-admin bootstrap required? 
- If yes, project-specific route/mechanism:
- Secret protection:
- Idempotency:
- Post-bootstrap restriction/rotation:
- Default production credentials forbidden: yes

## 11. AI capability map

| Feature | Model/tool | Input | Output | State/storage | Failure handling |
|---|---|---|---|---|---|

Exact model/package IDs must be runtime-verified before being treated as production requirements.

## 12. Workflow/plugin/agent assets

| Asset | Why workflow/agent/plugin | Input contract | Output contract | Test cases |
|---|---|---|---|---|

## 13. API design

| Endpoint | Method | Auth | Input | Output | Error cases |
|---|---|---|---|---|---|

Private/platform credentials stay in server/BFF paths.

## 14. Build-time vs runtime configuration

- Client build-time public config:
- Server runtime config:
- Runtime public-config endpoint needed? 
- CSP/connect-src origins:
- How PROD values are verified after deploy:

## 15. Verification plan

- Current CLI/runtime version check:
- Build/lint/typecheck:
- `coze_project_audit.py`:
- `coze_env_audit.py`:
- CRUD smoke test:
- Auth/permission test:
- Storage persistence test:
- AI route error/quota test:
- Workflow test:
- Migration test:
- DEV/PROD identity check:
- Post-deploy smoke test:

## 16. Production handoff

- Release commit:
- Production URL:
- Migration version:
- Resource identities verified:
- Backup/rollback:
- Bootstrap status:
- Known risks:

Use `templates/production-handoff.md` for the final record.

## 17. Single-HTML delivery (when applicable)

- Source type: deployed URL / Vite-static / native-static / full-stack / content-only
- Selected template/mode:
- Output path: `dist/index.single.html`
- Delivery status: self-contained / single-file-network-dependent / iframe-wrapper
- Image source: Coze built-in image integration / user-selected image skill / supplied assets
- iframe permissions required:
- Runtime checks: frame headers / cookies / HTTPS / camera-microphone / downloads
- Static-bundle limitations:
