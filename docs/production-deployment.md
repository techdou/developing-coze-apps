# Production Deployment Playbook

Use this for Coze Coding projects that move from development preview/sandbox to real users.

## 0. Evidence-first rule

Coze tooling and workspace behavior evolve. Before giving exact deployment commands, verify the current environment:

```bash
coze --version
coze code --help
coze code env --help
coze code db --help
```

Use current official documentation and current CLI help as the command contract. Treat old screenshots, uploaded reports, example repositories, and project wrappers as secondary evidence.

## 1. Freeze the release candidate

Record:

- repository + commit SHA;
- branch/tag;
- dependency lockfile state;
- migration version;
- intended production domain/project;
- expected production environment/resource IDs where visible.

Do not troubleshoot production while simultaneously changing unrelated application behavior.

## 2. Run source audits

```bash
python scripts/coze_project_audit.py . --format md --strict
python scripts/coze_env_audit.py . --format md --strict
```

Block deployment on unresolved P0 findings.

Minimum checks:

- no committed `.env.local` or real secrets;
- no service-role/private keys in client code;
- no DEV endpoint hard-coded in production code;
- no default production admin credentials;
- migrations are versioned and idempotent where practical;
- object storage persists keys, not expiring URLs;
- production does not silently downgrade privileged credentials.

## 3. Build the DEV / PROD matrix

Use `templates/environment-matrix.md`.

For each resource mark:

- actual DEV binding;
- actual PROD binding;
- ownership (`platform_injected`, `app_private`, `client_public`, `local_only`);
- whether it already exists;
- whether user action is required;
- migration/promotion strategy.

Unknown rows are deployment blockers until runtime-verified.

## 4. Decide production data policy

Default decision:

```text
schema/migrations: promote
reference seed data: promote only if explicitly production-safe
DEV business/test data: do not promote
DEV auth users/sessions: do not promote
DEV generated assets: do not promote unless allowlisted
```

If the deployment UI offers "sync development data to production", keep it disabled unless the user explicitly requests a reviewed data copy.

Document the exact tables/assets to promote if an exception is approved.

## 5. Prepare production infrastructure

Do not blindly recreate variables/resources from DEV.

### Database/Auth

1. Detect whether a production database/auth resource is already bound.
2. If missing, use the currently supported Coze UI/CLI flow to create or bind it.
3. Confirm production connection identity before migrations.
4. Back up existing production data before destructive migration.

### Object storage

1. Detect production bucket/binding.
2. Never assume DEV object keys exist in PROD.
3. Promote required curated assets through an explicit manifest.
4. Validate uploaded object key, content type, size/checksum, and read access.

### Environment variables

- Platform-injected variables: verify, do not copy DEV values manually unless current official/runtime evidence requires it.
- App-private secrets: create independent production values.
- Browser-public config: confirm production-safe values and whether they are build-time or runtime.
- Local-only values: never promote.

## 6. Run migrations

Preferred approach: migration files tracked in source control.

For every release record:

- migration IDs applied;
- execution time/result;
- target production identity;
- rollback/restore path.

Do not use ad-hoc manual schema edits as the primary deployment mechanism when a migration can express the change.

Separate migrations from seed/import operations.

## 7. Build and deploy

Use commands confirmed by current Coze CLI/UI rather than commands copied from old documents.

At deploy time verify:

- target project/environment is PROD;
- intended commit/build is used;
- required app-private secrets are configured;
- production runtime is not reading `.env.local` or DEV defaults;
- build-time browser config points to production-safe/public values.

## 8. Post-deploy smoke test

Minimum smoke suite:

1. health endpoint/page;
2. login/logout/session persistence;
3. role/RBAC enforcement;
4. create/read/update/delete one disposable record;
5. object upload -> DB key -> signed/display URL -> delete;
6. AI/model route normal request and handled failure;
7. runtime-config endpoint if used;
8. CSP/connect/frame policy in browser;
9. production logs show correct environment identity without secret leakage.

For a public API, also test auth failure, rate limit, invalid input, and idempotency where relevant.

## 9. Project-specific bootstrap / first admin

Bootstrap is application logic, not a universal Coze requirement.

If the app needs first-admin initialization:

- configure production-only bootstrap inputs;
- use high-entropy one-time protection;
- call the production bootstrap only after DB/Auth binding and migrations are verified;
- ensure it is idempotent;
- verify created admin identity;
- restrict/disable/rotate the bootstrap secret afterward where supported;
- never seed a known default production password.

See `docs/auth-bootstrap-patterns.md`.

## 10. Production handoff

Fill `templates/production-handoff.md` with:

- release commit;
- production URL/project;
- DB/Auth/Bucket identities or safe labels;
- variable ownership matrix (names only, never secret values);
- migration version;
- bootstrap status;
- smoke-test result;
- backup/rollback path;
- unresolved risks.

## Common failure patterns

### DEV admin appears in PROD

Likely causes:

- DEV data was copied;
- startup/seed created a default admin;
- `.env.local` or DEV defaults were included in deployment;
- bootstrap ran before production variables were configured.

Fix the root cause before merely changing the account.

### Browser connects to DEV DB after production deploy

Check:

- `NEXT_PUBLIC_*` or equivalent variables baked at build time;
- client bundle cache;
- runtime-config endpoint;
- CSP `connect-src`;
- server runtime vs client config mismatch.

### Terminal changes the wrong database

Do not trust shell variables after re-deploy. Re-check current project/environment identity and compare with the deployed runtime before privileged operations. Use `scripts/check_supabase_consistency.py` when the project follows the Supabase-style configuration pattern.

### Production works only with anonymous credentials

Do not accept a silent privileged->anonymous fallback. Treat missing service/admin credentials as a production configuration error.
