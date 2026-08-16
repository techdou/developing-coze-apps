# Database, Auth, and Object-Storage Lifecycle

This guide covers the persistent-data boundary for Coze Coding applications.

## 1. Resource model

Think in three layers:

1. **Schema and code** — version-controlled, promoted across environments.
2. **Runtime bindings and secrets** — environment-specific.
3. **Business data/assets** — environment-specific by default.

Do not treat "same application" as "same database" or "same bucket".

## 2. Database lifecycle

### Development

Use DEV for:

- schema iteration;
- test fixtures;
- disposable users;
- synthetic/demo records;
- migration rehearsal;
- destructive testing.

### Production

PROD should receive:

- reviewed migrations;
- production-safe reference seeds;
- explicitly approved imports.

It should not receive ordinary DEV rows merely because the platform can sync them.

## 3. Migration rules

- Every schema change should have an ordered migration when practical.
- Migrations must be committed with the application code that depends on them.
- Prefer additive/backward-compatible changes before destructive changes.
- Destructive migrations require backup and rollback/restore notes.
- Record which migration version is active in production.
- Re-running an already-applied migration must not corrupt data.
- Do not mix schema migration and large business-data import in the same opaque startup step.

## 4. Seed-data classes

Classify seed data explicitly:

| Class | Example | PROD default |
|---|---|---|
| reference | status dictionary, public categories | allowed after review |
| demo | sample tasks, fake users | no |
| privileged | default admin | no |
| migration support | backfill required by schema change | explicit migration/import |
| business | real or test user records | no unless approved import |

Seed scripts should be idempotent where possible.

## 5. Authentication lifecycle

Auth state is production data.

Do not sync by default:

- DEV users;
- sessions/refresh tokens;
- test OAuth identities;
- development admin accounts.

Use a project-specific first-admin/bootstrap flow or production admin-management flow instead.

## 6. Object-storage lifecycle

Use object storage for files/media/documents/exports.

Recommended pattern:

```text
upload -> storage returns object key -> DB stores object key
                                      |
read -> generate current signed/public URL when needed
```

Do not persist expiring signed URLs as the canonical database value.

### Environment isolation

A key such as:

```text
users/123/images/abc.png
```

is only meaningful inside the bucket/resource where it exists. The same key string in DEV and PROD does not prove the same object exists.

## 7. Asset promotion

When production needs curated assets created during development, use an explicit manifest rather than copying the whole bucket.

Example manifest:

```json
{
  "assets": [
    {
      "logical_name": "welcome-cover",
      "dev_key": "seed/welcome-cover.png",
      "prod_key": "seed/welcome-cover.png",
      "content_type": "image/png",
      "sha256": "<expected checksum>"
    }
  ]
}
```

Promotion workflow:

1. verify source object;
2. copy/upload to PROD using current supported storage mechanism;
3. verify target key, size, content type, and checksum where possible;
4. update PROD database/reference data only after object verification.

## 8. Storage URL rules

- Persist key/object ID, not temporary signed URL.
- Generate signed URLs close to use time.
- Choose expiry based on task, not convenience.
- Never place privileged storage credentials in the browser.
- If long-lived public assets are required, use an explicitly supported public/CDN mechanism instead of extending a temporary signature indefinitely.

## 9. Consistency verification

Before privileged DB/Auth operations after a deploy/redeploy, confirm that your terminal/runtime and deployed application point to the same production resource.

For Supabase-style projects in this skill:

```bash
python scripts/check_supabase_consistency.py
```

Treat mismatch as P0 before password reset, quota edits, user deletion, or migration.

## 10. Backup and rollback

Before destructive production changes record:

- backup/export timestamp;
- target database identity;
- migration ID;
- rollback SQL or restore procedure;
- affected tables/objects;
- acceptable downtime/data-loss window.

For object storage, destructive cleanup should use an allowlist/prefix and preferably a dry-run report.

## 11. Agent decision rules

When a user says "把开发环境同步到生产" ask/resolve **what** is intended:

- schema only -> migrations;
- reference data -> reviewed seed/import;
- selected business data -> explicit table/row import plan;
- files -> asset manifest;
- entire DEV state -> high-risk, require explicit acknowledgement and reason.

Do not translate an ambiguous "同步" into a full database/bucket copy.
