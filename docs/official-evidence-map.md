# Official and Empirical Evidence Map

Keep official claims, uploaded test reports, and project-specific wrappers separate. Re-check URLs and current workspace availability before making production commitments.

_Last reviewed: 2026-07-15._

## Skill format best practices (general design reference)

> The following design principles are derived from general AI agent skill engineering practices. They are not tied to any specific platform's documentation but reflect widely adopted conventions for progressive-disclosure skill bundles.

| Principle | Rationale | Implication |
|---|---|---|
| Skills are filesystem bundles of instructions, scripts, and resources, discovered from metadata. | Agent must efficiently match and load only what's needed. | Keep `name` and `description` in SKILL.md frontmatter precise and concise. |
| SKILL.md should stay concise and direct the Agent to detailed files only when needed (progressive disclosure). | Large skill files waste context window and reduce match accuracy. | Put detailed workflows in `docs/`, `templates/`, `scripts/`; keep SKILL.md as a router. |
| Representative evaluations reduce regressions and make behavior changes visible. | Skill updates can silently break behavior. | Maintain `evals/cases/` and deterministic script tests; update when behavior changes. |

## Official Coze / 扣子编程 capabilities

| Claim | Evidence URL | Status | Implication |
|---|---|---|---|
| Coze Coding supports AI-programming projects and integrated application development. | https://docs.coze.cn/guides_vibe_coding_overview | `confirmed_official` | It can be used as the application-development surface rather than only a Bot editor. |
| Built-in integrations include models, database, search, and managed file/object storage. | https://docs.coze.cn/guides_internal_integrations | `confirmed_official` | Route assets and AI calls to platform integrations; keep exact package APIs runtime-verified. |
| Mini-program/app projects can integrate database and storage through natural-language development instructions. | https://docs.coze.cn/guides_vibe_coding_miniapp | `confirmed_official` | Resource integration can be generated, but schema/security still require review. |
| Usage reporting includes model, image, speech, and search consumption for programming projects. | https://docs.coze.cn/coze_pro_bills_and_usage | `confirmed_official` | Quota and cost must be included in production readiness. |

## Uploaded empirical report: `coze-platform-report.pdf`

The report is an environment test record, not a universal platform contract.

| Observation | Location | Status | Skill implication |
|---|---|---|---|
| Development modes include Next.js, Vite, native minimal “single HTML + CDN”, and custom frameworks. | Page 1 | `environment_specific` | Single-HTML delivery is a valid project mode, but exact commands/templates must be verified in the current workspace. |
| The tested SDK exposes image generation with text-to-image, image-to-image, batch, and URL/Base64 output. | Page 3 | `environment_specific` | Use the current built-in image integration by default; do not hard-code model IDs globally. |
| Secrets are intended to remain server-side through a BFF/API route and environment injection. | Page 10 | `environment_specific` and sound architecture principle | Never put privileged model/storage credentials in the single HTML. |
| The report notes quota, expiring storage URLs, no-GPU sandbox, and environment-bound credentials. | Page 12 | `environment_specific` | Persist assets before packaging; disclose runtime/network dependencies and limits. |

## Evidence status conventions

- `confirmed_official`: explicitly stated in current official documentation.
- `environment_specific`: observed in an uploaded report, SDK wrapper, scaffold, or current sandbox.
- `needs_runtime_check`: account/workspace/model/region/package or browser behavior may vary.
- `unsupported_or_not_advised`: not supported or unsafe to promise.

## Wording rules

Prefer:

> The current Coze Coding environment can use its available image-generation integration; verify the active model/version at runtime.

Avoid:

> Every Coze workspace always provides this exact model ID and SDK method.

Prefer:

> A deployed full-stack app can be wrapped in one iframe HTML, while its backend remains hosted remotely.

Avoid:

> A Next.js app with API routes, database, auth, and storage can be converted into a fully offline single HTML with no loss of functionality.
