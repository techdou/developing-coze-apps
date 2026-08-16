# Relay Studio DEV/PROD Hardening Case Study

This example captures reusable engineering lessons from production-hardening a Coze Coding full-stack project. It is not a claim that every Coze project uses the same variables/routes.

Reference project: `https://github.com/douknowai/relay-studio`

## Situation

The application used:

- a Supabase-style database/auth integration;
- S3-compatible object storage;
- browser and server configuration;
- a project-defined first-admin bootstrap route;
- development defaults for local testing.

The production deployment exposed a class of problems common to AI-generated/full-stack projects: local development configuration and initialization logic can accidentally cross the production boundary.

## Failure modes to guard against

### 1. DEV defaults reach production initialization

A local/default administrator can appear in production if startup, seed, or bootstrap logic consumes development defaults.

General fix:

- `.env.local` is DEV-only;
- no default privileged PROD credentials;
- bootstrap happens explicitly after PROD DB/Auth verification;
- ordinary seeds do not create production admins.

### 2. Client config and server config diverge

A server may use production runtime variables while browser JavaScript still contains build-time DEV/public values.

General fix:

- classify client-public vs server-private config;
- test build-time and runtime separately;
- use an allowlisted runtime public-config/BFF endpoint when appropriate;
- verify CSP/connect-src after deployment.

### 3. Terminal targets stale infrastructure

After redeploy/resource changes, local shell variables can point to a different database than the deployed application.

General fix:

- verify target resource identity immediately before privileged DB/Auth operations;
- compare deployed runtime config with shell/tool config;
- fail on mismatch.

### 4. Object key does not imply object promotion

Database references can be migrated while files remain only in the DEV bucket.

General fix:

- persist object keys;
- explicitly promote curated assets to PROD storage;
- verify object metadata/checksum/read behavior;
- then update/seed production references.

### 5. Silent credential fallback hides production misconfiguration

Using an anonymous/public key when a privileged operation expects a service/admin key can make some operations appear to work while privileged flows fail unpredictably.

General fix:

- production fail-fast for missing privileged configuration;
- no DEV/public fallback;
- return actionable diagnostics without leaking secret values.

## Reusable deployment sequence

```text
code freeze
 -> env/source audit
 -> DEV/PROD matrix
 -> verify/create PROD resources
 -> configure app-private PROD secrets
 -> run migrations
 -> deploy reviewed commit
 -> smoke test auth/CRUD/storage/AI/config
 -> project-specific first-admin bootstrap
 -> harden bootstrap
 -> handoff + rollback notes
```

## What this case does NOT mean

- `BOOTSTRAP_TOKEN` is not a universal Coze variable.
- `/api/auth/bootstrap` is not a universal Coze endpoint.
- exact `COZE_*` names/resources must still be verified in the current workspace.
- a Supabase-style integration in this project does not mean every Coze project uses the same database implementation.
