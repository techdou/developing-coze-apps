# Production Readiness Checklist

Use before production deployment or handoff. This checklist is intentionally stricter than a development smoke test.

## P0 — Blockers

### Environment isolation

- [ ] DEV and PROD database/auth/storage identities are verified or explicitly marked as managed aliases that resolve to distinct intended production resources.
- [ ] `.env.local` and other local-only files are not committed/deployed as production source of truth.
- [ ] No DEV default admin credentials, DEV URLs, DEV buckets, or test tokens are used as production fallbacks.
- [ ] Platform-injected/reserved variables are not manually copied from DEV into PROD without current official/runtime evidence.
- [ ] App-private production secrets are independently configured.
- [ ] No private secret/service-role/bootstrap token is exposed through `NEXT_PUBLIC_*` or frontend code.
- [ ] Production fails fast when a required privileged credential/resource is missing; it does not silently fall back to DEV/public/anonymous credentials.

### Database/Auth

- [ ] Schema changes are represented by reviewed versioned migrations.
- [ ] Production target identity is confirmed immediately before migration.
- [ ] DEV→PROD ordinary business/test-data sync is OFF unless explicitly approved.
- [ ] Any approved production data import has an allowlist, backup, and verification plan.
- [ ] Auth users/sessions/test identities are not copied from DEV by default.
- [ ] Database update/delete operations have explicit filters and authorization.
- [ ] Auth and role checks exist for protected routes/actions.

### Object storage

- [ ] Production bucket/storage binding is verified.
- [ ] Object storage persists keys/object IDs, not temporary signed URLs.
- [ ] Code never assumes a DEV object key already exists in PROD.
- [ ] Curated DEV→PROD assets use an explicit promotion manifest/allowlist.
- [ ] Privileged storage credentials are server-only.

### Application security

- [ ] No API keys, tokens, service-role keys, model clients, or storage credentials in frontend code.
- [ ] Model/database/storage privileged clients are server-only/BFF.
- [ ] Bootstrap/first-admin logic, if present, is project-specific, protected, idempotent, and contains no default production password.
- [ ] No real secret values appear in source, docs, examples, logs, issue text, or generated HTML.

## P1 — Should fix before real users

- [ ] Current Coze CLI/runtime behavior has been re-verified (`coze --version`, relevant `coze code ... --help`).
- [ ] Build/lint/typecheck pass.
- [ ] `coze_project_audit.py` and `coze_env_audit.py` pass without unresolved P0.
- [ ] CRUD smoke tests pass against production.
- [ ] File upload/display/download/delete flow works in production storage.
- [ ] AI route handles model failure, quota, timeout, empty response, and cancellation where relevant.
- [ ] Workflow/agent/plugin calls have input/output contract and test payloads.
- [ ] Backup and rollback/restore plan is documented before destructive migration.
- [ ] Migration IDs and execution results are recorded.
- [ ] Browser build-time public config and server runtime config both point to intended production resources.
- [ ] CSP/connect-src/frame policy is verified in a real browser.
- [ ] Logs/trace retention and secret redaction are documented.
- [ ] Production handoff is completed using `templates/production-handoff.md`.

## P2 — Quality improvements

- [ ] Mobile responsive UI.
- [ ] Loading, empty, error, and success states.
- [ ] Accessibility labels for forms/buttons.
- [ ] Consistent data formatting and pagination.
- [ ] Export/import where needed.
- [ ] Basic analytics/audit log.
- [ ] Cost/quota monitoring and alert ownership.
- [ ] Secret-rotation ownership documented.

## Suggested audit commands

```bash
python scripts/coze_project_audit.py /path/to/project --format md --strict
python scripts/coze_env_audit.py /path/to/project --format md --strict
```

For Supabase-style projects after redeploy/resource changes:

```bash
python scripts/check_supabase_consistency.py
```

## Post-deploy smoke test

- [ ] Production URL loads.
- [ ] Login/logout and session persistence work.
- [ ] Unauthorized role/action is correctly denied.
- [ ] Disposable CRUD record can be created/read/updated/deleted.
- [ ] Disposable file can be uploaded/read/deleted through production storage.
- [ ] AI/model route succeeds and an induced failure is handled.
- [ ] Runtime public-config endpoint (if used) exposes only allowlisted client-safe fields.
- [ ] No production log prints secret values.
- [ ] Existing admin identity is expected; no accidental DEV/default admin exists.

## Single-HTML / iframe handoff

- [ ] Output is exactly `dist/index.single.html` unless another path was requested.
- [ ] The chosen mode matches the source: static bundle, editorial template, or deployed URL wrapper.
- [ ] No server-side capability is falsely represented as embedded in the HTML.
- [ ] No unresolved local `src`, `href`, `poster`, CSS `url(...)`, or JavaScript imports remain for self-contained mode.
- [ ] Generated images are embedded or use intentionally stable public URLs; temporary signed URLs are not used.
- [ ] iframe URL is HTTPS and contains no secret/token in query parameters.
- [ ] `X-Frame-Options`, CSP `frame-ancestors`, authentication cookies, and required feature permissions are tested.
- [ ] `sandbox` and `allow` attributes follow minimum permission.
- [ ] Mobile viewport, scrolling, full-screen sizing, fallback/open-new-window behavior, and accessibility titles/alt text are verified.

```bash
python scripts/single_html_tool.py validate dist/index.single.html --format md
```
