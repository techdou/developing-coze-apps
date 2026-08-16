---
name: developing-coze-apps
description: >-
  Plan, build, review, deploy, or package Coze Coding (扣子编程) applications.
  Covers full-stack web apps, agents, workflows, RAG, media generation,
  DEV/PROD environment isolation, database/object-storage lifecycle,
  production handoff, and single-HTML/iframe packaging.
  Triggers: Coze app, architecture routing, resource plan, production deployment,
  environment variables, database/storage, single HTML, iframe embed.
---

# Developing Coze Apps

Turn a Coze requirement into a scoped architecture, correct resource-routing plan, environment-safe implementation, tested production deployment, and—when requested—a validated single-HTML package.

## Use this skill for

- Coze Coding / 扣子编程 web apps, admin systems, SaaS prototypes, teaching tools, agents, workflows, plugins, knowledge/RAG, and media-generation apps.
- Deciding whether logic belongs in Coze Coding, ordinary Coze Agent, Workflow, Plugin, Skill, backend code, database, object storage, or knowledge/RAG.
- Designing and reviewing separate DEV and PROD databases, auth, object storage, secrets, domains, migrations, seeds, and bootstrap flows.
- Reviewing an existing Coze project for resource misuse, security, quotas, deployment, environment leakage, and production readiness.
- Packaging a deployed URL or static web project as `dist/index.single.html` for iframe embedding.

## Do not use this skill for

- A short general explanation of what Coze is.
- Generic React/Next.js/Vue debugging with no Coze-specific resource, deployment, or packaging requirement.
- Pure prompt rewriting unrelated to Coze application/agent/workflow development.
- Product ideation where Coze is not the target platform.

## First decision: identify the Coze layer

Do not collapse these into one surface:

1. **Ordinary Coze / Coze Studio**: agents, workflows, plugins, knowledge bases, prompts, OpenAPI/SDK integration, publishing.
2. **Coze Coding / 扣子编程**: cloud AI programming for web apps, agents, workflows, skills, mini programs, mobile prototypes, and full-stack AI applications.
3. **Project-specific wrappers**: `coze-coding-dev-sdk`, Supabase-style helpers, S3-style helpers, runner scripts, and template commands. Treat exact APIs/model IDs as environment-specific until verified.

State the selected layer in every architecture answer.

## Mandatory environment gate

For any project that uses database, auth, object storage, secrets, deployment, or persistent user data, do this **before coding persistent features**:

1. Read `docs/environment-separation.md`, `docs/environment-variables.md`, and `templates/environment-matrix.md`.
2. Build a DEV/PROD environment matrix.
3. Classify every variable/resource as:
   - `platform_injected` — owned/injected by Coze runtime; do not ask users to recreate reserved platform variables unless current official/runtime evidence explicitly requires it.
   - `app_private` — project-owned server secret; configure separately for DEV and PROD.
   - `client_public` — intentionally browser-visible; never place service-role keys, API secrets, bootstrap tokens, or private credentials here.
   - `local_only` — developer-machine convenience such as `.env.local`; never treat it as a production source of truth.
4. Confirm whether DEV and PROD databases/storage are isolated in the current workspace. **Do not assume either automatic isolation or automatic sharing.** Verify current deployment settings/runtime.
5. Default production data policy: **schema/migrations promote; business/test data does not.** Any DEV→PROD data copy requires explicit user intent and a reviewed allowlist.

## Core routing workflow

1. Classify the deliverable: web/admin app, agent, workflow, skill, mini program, mobile app, single HTML, or hybrid.
2. Classify the workload: display, tool, business system, media generation, RAG, automation, or embed/package.
3. Route resources:
   - UI/state -> frontend.
   - Transactions, RBAC, validation, complex CRUD -> backend code + database.
   - Files/media/exports -> object storage; persist object keys, not temporary signed URLs.
   - Reasoning/generation -> LLM or specialized model.
   - Document-grounded answers -> knowledge/RAG with source metadata.
   - Reusable orchestration -> Workflow with explicit I/O contract.
4. Verify environment-specific claims before coding: package version, model list, quotas, domains, storage, auth, runtime limits, CLI commands, and deploy behavior.
5. Build in stages and validate each stage before moving on.

## Database and storage lifecycle

Read `docs/database-storage-lifecycle.md` when database/auth/storage is used.

- Treat DEV DB/Auth/Bucket and PROD DB/Auth/Bucket as separate resources unless the current Coze workspace proves otherwise.
- Keep schema in version-controlled migrations.
- Keep repeatable non-sensitive reference data in explicit idempotent seed scripts.
- Keep test users, generated media, task history, audit logs, API keys, and ordinary DEV records out of production by default.
- Persist object keys/file IDs in the database; generate signed URLs at read/display time.
- Never assume a DEV object key exists in PROD storage.
- If production needs curated assets, use an explicit asset-promotion manifest and verify checksum/content type after copy.
- Destructive migrations require backup/rollback planning and explicit acknowledgement.

## Environment-variable rules

Read `docs/environment-variables.md`.

- `.env.local` is DEV/local-only. It must be ignored by git and must not be the production source of truth.
- `.env.example` may be committed only with placeholder values and classification comments.
- Reserved/platform-prefixed variables (for example observed `COZE_*` variables) must be treated as platform-owned until verified otherwise.
- `NEXT_PUBLIC_*` or equivalent client-exposed variables are build/browser-visible. Never place private secrets in them.
- Prefer runtime server configuration for platform-bound infrastructure. If the browser needs safe public config, expose only an allowlisted subset through a server/BFF runtime-config endpoint when appropriate.
- Build-time and runtime config must be tested separately; do not assume a production runtime variable can retroactively change a value already baked into a client bundle.

## Production deployment workflow

Trigger this whenever the user says deploy, publish, production, 上线, 生产环境, 生产数据库, environment variables, 数据同步, or asks why DEV works but PROD fails.

1. Read `docs/production-deployment.md`, `templates/production-handoff.md`, and `templates/production-readiness-checklist.md`.
2. Runtime-verify current Coze tooling before issuing exact commands:
   - `coze --version`
   - `coze code --help`
   - relevant `coze code env --help`, `coze code db --help`, and deploy help when available.
3. Run static audits:
   - `python scripts/coze_project_audit.py . --format md --strict`
   - `python scripts/coze_env_audit.py . --format md --strict`
4. Confirm production resource matrix and environment-variable ownership.
5. Default DEV→PROD database-data sync to **OFF** unless explicitly required. Promote schema through migrations instead.
6. Create/bind production database, auth, object storage, and project secrets only where the current workspace requires user action; do not invent platform configuration steps.
7. Run migrations against the production target exactly once per version; record migration version/result.
8. Deploy the intended commit/build.
9. Run post-deploy smoke tests: health, auth, CRUD, storage upload/read/delete, AI route, runtime config, CSP/frame policy, and permission boundaries.
10. Run any **project-specific** first-admin/bootstrap only after production infrastructure is confirmed. Bootstrap is not a universal Coze mechanism.
11. Produce a production handoff report with unresolved risks and rollback instructions.

## Bootstrap / first-admin patterns

Read `docs/auth-bootstrap-patterns.md` when the application needs a first administrator.

- `BOOTSTRAP_*`, `INIT_ADMIN_*`, or similar names are application conventions, not Coze platform standards unless official evidence says otherwise.
- Production bootstrap must be explicit, authenticated by a one-time/high-entropy secret or equivalent control, idempotent, and auditable.
- Never ship a default production admin email/password in `.env.local`, seed files, source code, or client bundles.
- Do not auto-create a privileged account from DEV defaults during production startup.
- After successful bootstrap, disable/restrict the bootstrap path where practical and rotate/remove bootstrap secrets if the design permits.

## Single-HTML / iframe workflow

Trigger this workflow when the user mentions 单 HTML, single HTML, iframe, 百宝箱, 外部应用嵌入, URL 全屏展示, 图文页, or `dist/index.single.html`.

1. Read `docs/single-html-mode-selection.md` and `templates/single-html/catalog.md`.
2. Inspect the source:
   - deployed URL -> iframe-wrapper modes;
   - native/static/Vite build -> static bundle may be possible;
   - Next.js/full-stack/auth/database/API routes -> keep the app deployed and wrap its URL; do not pretend the backend can be packed into one file;
   - content + images -> editorial templates.
3. Present the best 3 options with fit, dependency, limitation, and recommendation unless the user already specified the mode.
4. Generate images through the current Coze Coding built-in image-generation integration by default. Do not hard-code a model ID unless verified in the current environment.
5. Generate/package HTML with `scripts/single_html_tool.py`.
6. Write `dist/index.single.html` unless another path was requested.
7. Validate self-contained/network-dependent/iframe-wrapper status and iframe/security constraints.

## Read only what the task needs

| User task | Read these files |
|---|---|
| Platform feasibility | `docs/capability-map.md`, `docs/official-evidence-map.md`, `docs/coze-limit-boundaries.md` |
| Architecture/MVP | `templates/architecture-blueprint.md`, `templates/scope-ladder.md`, `docs/architecture-patterns.md` |
| DEV/PROD architecture | `docs/environment-separation.md`, `templates/environment-matrix.md` |
| Environment variables | `docs/environment-variables.md`, `scripts/coze_env_audit.py` |
| Database/object storage | `docs/database-storage-lifecycle.md`, `templates/environment-matrix.md` |
| Production deployment | `docs/production-deployment.md`, `templates/production-handoff.md`, `templates/production-readiness-checklist.md` |
| First admin/bootstrap | `docs/auth-bootstrap-patterns.md`, `docs/production-deployment.md` |
| Staged Coze prompts | `templates/coze-build-prompts.md` |
| Workflow design | `templates/workflow-contract.md`, `docs/agent-routing-rules.md` |
| Single HTML / iframe | `docs/single-html-mode-selection.md`, `templates/single-html/catalog.md`, `docs/single-html-security.md` |
| Static app to one HTML | `docs/static-bundling-compatibility.md`, `scripts/single_html_tool.py` |
| Project review | `templates/production-readiness-checklist.md`, `scripts/coze_project_audit.py`, `scripts/coze_env_audit.py` |
| Supabase consistency | `scripts/check_supabase_consistency.py`, `docs/database-storage-lifecycle.md` |
| Skill validation/evals | `scripts/validate_skill_package.py`, `evals/cases/` |

## Required output for planning tasks

```markdown
## 结论
<能做 / 部分能做 / 不建议这样做>

## 应采用的 Coze 层
<Coze Coding / ordinary Coze Agent / Workflow / Skill / Hybrid>

## DEV / PROD 环境矩阵
<database, auth, storage, env, domain, external APIs>

## 资源调用设计
| 模块 | 资源 | 所在层 | 环境 | 风险/验证 |

## 范围与阶段
<Must-have / Should-have / Later + phased implementation>

## 验收清单
<build, CRUD, auth, storage, AI, workflow, env isolation, migration, deployment>
```

## Required output for deployment tasks

```markdown
## Production preflight
<commit, current CLI/runtime evidence, env matrix, blockers>

## Production resources
<DB/Auth/Storage/Secrets: platform-injected vs user-created>

## Migration/data policy
<schema migration, seed, DEV→PROD sync decision>

## Deploy + smoke tests
<commands/actions actually verified in current environment>

## Bootstrap/initialization
<project-specific only; exact one-time action if required>

## Handoff
<production URL, migration version, known risks, rollback>
```

## Guardrails

- Do not claim ordinary Coze Bot alone can replace a full business system.
- Do not expose model/storage/service-role clients or private secrets in frontend code.
- Do not persist temporary signed URLs as permanent records.
- Do not promise exact CPU/RAM/disk/model/CLI behavior without checking the target workspace/current official source.
- Do not describe project-specific Supabase/S3/bootstrap wrappers as universal platform guarantees.
- Do not assume DEV and PROD share—or do not share—the same database/storage. Verify.
- Do not default to syncing DEV business/test data into PROD.
- Do not deploy `.env.local` or DEV default credentials as production configuration.
- Do not create user variables with reserved platform prefixes merely because a local example contains them.
- Do not silently fall back from privileged production credentials to weaker/public credentials. Fail fast with a clear diagnostic.
- Do not pack a server-rendered/full-stack app into one HTML and claim its backend still works.
- Do not assume a URL can be framed: verify `X-Frame-Options`, CSP `frame-ancestors`, authentication cookies, HTTPS, and required permissions.
- Do not embed secrets, service tokens, or private API endpoints in generated HTML.

## Evidence discipline

`docs/official-evidence-map.md` is the evidence index. Exact platform behavior changes quickly. Prefer current official documentation and current CLI `--help`; use uploaded/sandbox reports as empirical evidence only. When sources conflict, report the conflict and choose the behavior verified in the target workspace rather than guessing.
