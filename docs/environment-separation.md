# DEV / PROD Environment Separation

This document defines the default environment model for Coze Coding projects that use persistent data, auth, object storage, secrets, external APIs, or production deployment.

## Core principle

Treat development and production as two independent runtime/resource boundaries that share application code and versioned schema—not live credentials or ordinary data.

```text
                    same application code
                           |
                   versioned migrations
                           |
             +-------------+-------------+
             |                           |
          DEV runtime                  PROD runtime
             |                           |
       DEV database                  PROD database
       DEV auth                      PROD auth
       DEV bucket                    PROD bucket
       DEV secrets                   PROD secrets
       test/demo data                real user data
```

Never infer isolation from names alone. Confirm actual Coze workspace/deploy behavior before modifying production.

## What should be shared

- Source code and dependency lockfiles.
- Database schema definitions and ordered migrations.
- Idempotent, non-sensitive reference-data seeds that are explicitly production-safe.
- Validation, RBAC policy definitions, API contracts, and infrastructure conventions.
- Object-key naming conventions and asset manifests.

## What should not be shared by default

- Database connection URLs/keys.
- Auth users and sessions.
- Service-role/admin keys.
- Object-storage buckets and generated object keys.
- Test/demo users and default passwords.
- Generated media, task history, audit logs, API keys, usage records, temporary signed URLs.
- `.env.local` values.

## Environment matrix requirement

Before persistent features are implemented, fill `templates/environment-matrix.md` with at least:

| Resource | DEV | PROD | Owner | Promotion strategy |
|---|---|---|---|---|
| Runtime |  |  | Coze/app | deploy same commit |
| Database |  |  | platform/app | migrations only |
| Auth |  |  | platform/app | bootstrap/admin workflow |
| Object storage |  |  | platform/app | explicit asset promotion |
| App-private secrets |  |  | app | configure separately |
| Browser-public config |  |  | app/platform | build/runtime allowlist |
| Domain |  |  | platform/user | runtime verify |
| External APIs |  |  | app/user | separate keys/quotas |

If any row is unknown, mark `needs_runtime_check` rather than guessing.

## Production data-sync policy

Default: **do not sync ordinary DEV data into PROD**.

Promote:

- schema/migrations;
- audited reference dictionaries;
- deliberately selected public/sample content;
- required curated assets through an explicit manifest.

Do not promote by default:

- users/auth sessions;
- default admin accounts;
- test-generated media;
- API keys/tokens;
- task/audit history;
- development-only settings;
- temporary signed URLs.

If Coze deployment UI offers a DEV→PROD data-sync switch, keep it off unless the user explicitly wants a reviewed data promotion. A platform sync feature is a transport mechanism, not a production-governance decision.

## `.env.local` policy

`.env.local` is local/development configuration only.

Required controls:

1. Ignore it in git.
2. Never use it as the production source of truth.
3. Never store production credentials in it.
4. Never place default privileged production accounts in it.
5. Prefer `.env.example` for variable names, ownership, and placeholders.
6. Audit build/start scripts for explicit dotenv loading that could re-import local files in production.

## Build-time vs runtime

Browser-public variables can be compiled into client assets. A later production runtime change may not alter an already-built bundle.

Therefore test both:

- build-time config used by frontend bundles;
- runtime config used by server code.

For platform-bound infrastructure, prefer server-side runtime variables. If the browser needs non-sensitive public configuration, expose an allowlisted runtime-config endpoint/BFF when appropriate instead of copying privileged infrastructure variables into client code.

## Failure behavior

Production must fail fast when required privileged configuration is missing or inconsistent.

Avoid patterns such as:

- service-role key missing -> silently use anonymous key;
- production DB missing -> silently use DEV DB;
- production bucket missing -> silently use DEV bucket;
- production secret missing -> silently use a hard-coded default.

Return an actionable configuration error instead.

## Agent behavior

When asked to deploy or fix a production issue, the Agent must first answer these questions from evidence:

1. Which environment is the current command/session connected to?
2. Which DB/Auth/Bucket does that environment use?
3. Which values are platform-injected vs application-owned?
4. Has the production database already been migrated?
5. Is the user asking to copy schema, reference data, or business data?
6. Could a local file or client bundle still contain DEV values?

Only then modify production.
