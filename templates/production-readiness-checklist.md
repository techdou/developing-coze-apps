# Production Readiness Checklist

Use before deployment or handoff.

## P0 — Blockers

- [ ] No API keys, tokens, service-role keys, model clients, or storage credentials in frontend code.
- [ ] Model/database/storage clients are server-only.
- [ ] Database update/delete operations have explicit filters.
- [ ] Auth and role checks exist for protected routes/actions.
- [ ] Object storage persists keys/object IDs, not temporary signed URLs.
- [ ] AI/media long tasks have timeout, heartbeat, polling, or async state.
- [ ] Production environment variables are documented and not hard-coded.

## P1 — Should fix before real users

- [ ] Build/lint/typecheck pass.
- [ ] CRUD smoke tests pass.
- [ ] File upload/display/download flow works.
- [ ] AI route handles model failure, quota, timeout, and empty response.
- [ ] Workflow/agent/plugin calls have input/output contract and test payloads.
- [ ] Database dev/prod sync and migration behavior is documented.
- [ ] Backup and rollback plan is documented.
- [ ] Logs/Trace retention and export needs are documented.

## P2 — Quality improvements

- [ ] Mobile responsive UI.
- [ ] Loading, empty, error, and success states.
- [ ] Accessibility labels for forms/buttons.
- [ ] Consistent data formatting and pagination.
- [ ] Export/import where needed.
- [ ] Basic analytics or audit log.

## Suggested audit command

```bash
python scripts/coze_project_audit.py /path/to/project --format md --strict
```

## Single-HTML / iframe handoff

- [ ] Output is exactly `dist/index.single.html` unless another path was requested.
- [ ] The chosen mode matches the source: static bundle, editorial template, or deployed URL wrapper.
- [ ] No server-side capability is falsely represented as embedded in the HTML.
- [ ] No unresolved local `src`, `href`, `poster`, CSS `url(...)`, or JavaScript imports remain.
- [ ] Generated images are embedded or use intentionally stable public URLs; temporary signed URLs are not used.
- [ ] iframe URL is HTTPS and contains no secret/token in query parameters.
- [ ] `X-Frame-Options`, CSP `frame-ancestors`, authentication cookies, and required feature permissions are tested in the target browser/platform.
- [ ] `sandbox` and `allow` attributes follow the minimum-permission principle.
- [ ] Mobile viewport, scrolling, full-screen sizing, fallback/open-new-window behavior, and accessibility titles/alt text are verified.
- [ ] Validation passes:

```bash
python scripts/single_html_tool.py validate dist/index.single.html --format md
```
