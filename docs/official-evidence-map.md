# Official and Empirical Evidence Map

Keep official claims, current CLI behavior, uploaded test reports, and project-specific wrappers separate. Re-check current workspace availability before production commitments.

_Last reviewed: 2026-08-17._

## Evidence priority

1. Current Coze official documentation for the exact product surface.
2. Current installed `coze` CLI `--help` / official `@coze/cli` package documentation.
3. Current target-workspace runtime observation.
4. Uploaded empirical reports/scaffolds.
5. Project-specific code/wrappers.

When higher-priority evidence conflicts with lower-priority evidence, prefer the higher-priority/current target-workspace behavior and record the conflict.

## Canonical Coze Coding references

These URLs are the primary references for the resource areas this skill uses. If a page has moved, search the current official Coze documentation by the same topic before substituting third-party guidance.

| Topic | Canonical reference | Skill use |
|---|---|---|
| Vibe Coding overview | https://docs.coze.cn/guides_vibe_coding_overview | identify Coze Coding surface |
| Internal integrations | https://docs.coze.cn/guides_internal_integrations | resource routing / managed integrations |
| Database integration | https://docs.coze.cn/guides_integrate_database | DB creation/binding/deployment behavior |
| Object storage integration | https://docs.coze.cn/guides_integrate_storage | bucket/storage behavior |
| Environment variables | https://docs.coze.cn/guides_environment_variables | DEV/PROD variable management |
| Authentication integration | https://docs.coze.cn/guides_integrate_authentication | auth capabilities and boundaries |

Do not turn a URL in this table into an immutable product contract. The Agent must still check current page/CLI/workspace behavior.

## Current official CLI evidence

Official npm package:

- https://www.npmjs.com/package/@coze/cli

Behavior observed in the current package documentation as of the review date:

- project environment variables are managed with `coze code env ...` commands;
- the CLI documentation distinguishes development and production for environment-variable listing (`--env dev|prod` where supported by the documented command);
- database lifecycle commands exist under `coze code db ...` in the current CLI documentation;
- CLI command surfaces evolve, so exact deploy/db/env syntax must be verified with the installed CLI before execution.

Skill implication: never copy old `coze init/dev/build/start` examples into a production runbook without checking current `coze code ... --help`.

## Uploaded empirical reference: `coze-dev-reference.pdf`

This report describes a tested Coze Vibe Coding environment and is useful engineering evidence, but it is not a universal platform contract.

Observed report statements include:

- a Coze Coding sandbox with managed AI SDK clients;
- Supabase-style PostgreSQL/Auth and S3-compatible object storage in the tested environment;
- environment variables such as `COZE_PROJECT_ENV`, `COZE_SUPABASE_*`, and `COZE_BUCKET_*` in that environment;
- privileged SDK/database/storage usage is server-side;
- object storage should persist returned object keys rather than temporary signed URLs;
- production filesystem/runtime limits may differ from development.

Skill implication: use these observations as patterns and diagnostic hints, then verify the current workspace before treating exact names/versions/limits as guaranteed.

## Relay Studio empirical case

Repository used as a real production-hardening case study:

- https://github.com/douknowai/relay-studio

Lessons promoted into this skill:

1. `.env.local` / DEV defaults must not become production source of truth.
2. A project-specific bootstrap route/variables are not Coze platform conventions.
3. Client build-time configuration can diverge from server runtime configuration.
4. Terminal/Supabase configuration can become stale after redeploy/resource changes; verify target identity before privileged operations.
5. Production should fail fast rather than silently downgrade privileged credentials.
6. DEV/PROD database and object-storage promotion must be explicit.

These are engineering lessons from a project, not universal Coze APIs.

## Evidence status conventions

- `confirmed_official`: explicitly supported by current official documentation/official CLI documentation.
- `runtime_verified`: observed in the target workspace/runtime during the task.
- `environment_specific`: observed in an uploaded report, scaffold, SDK wrapper, or another project.
- `needs_runtime_check`: account/workspace/region/version/CLI behavior may vary.
- `unsupported_or_not_advised`: unsafe or unsupported to promise.

## Wording rules

Prefer:

> The current Coze environment exposes these managed resources/variables; verify the production binding before deployment.

Avoid:

> Every Coze project always has this exact Supabase project, bucket, variable, model ID, or CLI command.

Prefer:

> DEV→PROD business-data sync is disabled by default in this skill; promote schema through migrations and copy only reviewed data/assets when required.

Avoid:

> Because the platform provides a sync button, development data should be copied to production.

Prefer:

> `BOOTSTRAP_TOKEN` is a project-defined control in Relay Studio.

Avoid:

> Coze requires every application to configure `BOOTSTRAP_TOKEN`.

## Runtime verification commands

Before exact CLI guidance:

```bash
coze --version
coze code --help
coze code env --help
coze code db --help
```

For SDK/package-specific guidance, inspect the installed package version and local type definitions/README rather than assuming the version listed in an older PDF.
