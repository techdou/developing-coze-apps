# Architecture Blueprint Template

Use this template for Coze Coding / Coze hybrid planning.

## 1. Project summary

- Project name:
- Business/education goal:
- Primary users:
- Coze layer: Coze Coding / Agent / Workflow / Skill / Hybrid
- Confidence: confirmed_official / environment_specific / needs_runtime_check

## 2. MVP scope

| Priority | Feature | Reason | Not included yet |
|---|---|---|---|
| Must |  |  |  |
| Should |  |  |  |
| Later |  |  |  |

## 3. Roles and permissions

| Role | Can view | Can create/update | Can export/delete | Notes |
|---|---|---|---|---|

## 4. Pages/routes

| Route | Page | Core actions | Data/API |
|---|---|---|---|

## 5. Data model

| Table | Purpose | Key fields | Relationships | Risks |
|---|---|---|---|---|

Conventions:

- snake_case columns.
- `id`, `created_at`, `updated_at` by default.
- Avoid update/delete without explicit filters.
- Document dev/prod sync/migration plan.

## 6. Storage model

| Asset | Storage key format | DB reference | Access pattern |
|---|---|---|---|

Rule: store object keys, not temporary signed URLs.

## 7. AI capability map

| Feature | Model/tool | Input | Output | State/storage | Failure handling |
|---|---|---|---|---|---|

## 8. Workflow/plugin/agent assets

| Asset | Why workflow/agent/plugin | Input contract | Output contract | Test cases |
|---|---|---|---|---|

## 9. API design

| Endpoint | Method | Auth | Input | Output | Error cases |
|---|---|---|---|---|---|

## 10. Verification plan

- Build/lint/typecheck:
- CRUD smoke test:
- Auth/permission test:
- Storage persistence test:
- AI route error/quota test:
- Workflow test:
- Deployment/env test:

## 11. Single-HTML delivery (when applicable)

- Source type: deployed URL / Vite-static / native-static / full-stack / content-only
- Selected template/mode:
- Alternative options offered:
- Output path: `dist/index.single.html`
- Delivery status: self-contained / single-file-network-dependent / iframe-wrapper
- Image source: Coze built-in image integration / user-selected image skill / supplied assets
- iframe permissions required:
- Runtime checks: frame headers / cookies / HTTPS / camera-microphone / downloads
- Static-bundle limitations:
